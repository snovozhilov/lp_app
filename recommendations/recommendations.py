# import pandas as pd
import numpy as np
import datetime as dt
import recommendations.sql_templates as sql
from scipy.sparse import lil_matrix
from sklearn.preprocessing import normalize
from scipy.sparse import spdiags, vstack
from sql_stuff.model import db, Recommendations



def get_users(cursor):
    """забираем ид юзеров, которые оценили более I картинок. присваиваем им порядковое номера"""
    users_sql = sql.users_sql
    cursor.execute(users_sql)
    user_to_col = {}
    for col_id, (user_id,) in enumerate(cursor):
        user_to_col[user_id] = col_id

    return user_to_col


def get_images(cursor):
    """забираем ид картинок, которые оценили более U юзеров из словаря user_to_col. присваиваем им порядковое номера"""
    image_sql = sql.image_sql
    cursor.execute(image_sql)
    obj_to_row = {}
    for row_id, (image_id,) in enumerate(cursor):
        obj_to_row[image_id] = row_id

    return obj_to_row


def make_matrix(user_to_col, obj_to_row, cursor):
    """заполяет матрицу [Юзер-Объект] = Оценка"""
    rate_matrix = sql.rate_matrix
    cursor.execute(rate_matrix)

    matrix = lil_matrix((len(obj_to_row), len(user_to_col)))  # создаем матрицу нужных размеров
    # заполняем матрицу
    for obj_id, user_id, rate in cursor:
        row_id = obj_to_row.get(obj_id)
        col_id = user_to_col.get(user_id)
        if row_id is not None and col_id is not None:
            matrix[row_id, col_id] = min(rate, 10)
    return matrix


def cosine_matrix(matrix):
    """заполняем матрицу item-item, где в полях косинусная мера. зануляем диагональ."""
    normalized_matrix = normalize(matrix.tocsr()).tocsr()
    cosine_sim_matrix = normalized_matrix.dot(normalized_matrix.T)
    diag = spdiags(-cosine_sim_matrix.diagonal(), [0], *cosine_sim_matrix.shape, format='csr')
    cosine_sim_matrix = cosine_sim_matrix + diag
    return cosine_sim_matrix


def neigbohood(cosine_sim_matrix, m):
    """Оставляем в матрице ТОП m ближайших соседей для каждого объекта (item)"""
    cosine_sim_matrix = cosine_sim_matrix.tocsr()

    rows = []
    for row_id in np.unique(cosine_sim_matrix.nonzero()[0]):
        row = cosine_sim_matrix[row_id]  # исходная строка матрицы
        if row.nnz > m:
            work_row = row.tolil()
            work_row[0, row.nonzero()[1][np.argsort(row.data)[-m:]]] = 0
            row = row - work_row.tocsr()
        rows.append(row)
    top_neighbor_matrix = vstack(rows)
    # нормализуем матрицу-результат
    top_neighbor_matrix = normalize(top_neighbor_matrix)
    return top_neighbor_matrix


def row_to_obj(obj_to_row):
    """сделать обратные сооттветствия порядковый_номер<->image_id"""
    row_to_object = {row_id: obj_id for obj_id, row_id in obj_to_row.items()}
    return row_to_object


def get_recommendation(top_neighbor_matrix, matrix, row_to_object, user_to_col, app):
    """для каждого юзера умножаем его вектор оценок на матрицу item-item с косинусными расстояниями"""
    top_n = 10  # ТОП сколько рекомендаций мы хотим получить
    dadd = dt.datetime.utcnow().strftime("%Y-%m-%d")
    result = []
    for user_id, col_id in user_to_col.items():
        user_vector = matrix.getcol(col_id)  # получить вектор для номера юзера в колонке (внутренний ид)
        user_vector = user_vector.tocsr()  # сделать вектором
        x = top_neighbor_matrix.dot(user_vector).tolil()  # умножаем матрицу item-item на вектор оценок пользователя
        for i, j in zip(*user_vector.nonzero()):  # занулить то что он уже оценил
            x[i, j] = 0
        x = x.T.tocsr()  # сделать результаты вектором

        data_ids = np.argsort(x.data)[-top_n:][::-1]

        for arg_id in data_ids:
            row_id, p = x.indices[arg_id], x.data[arg_id]
            image_id = row_to_object[row_id]
            expected_rate = round(p, 2)
            result.append({"user_id": user_id, "image_id": image_id, "expected_rate": expected_rate})
            save_recommendation_to_db(app=app, user_id=user_id, image_id=image_id, expected_rate=expected_rate, dadd=dadd)
    print(result)
    return result


def save_recommendation_to_db(app, user_id, image_id, expected_rate, dadd):
    with app.app_context():
        new_recommendation = Recommendations(user_id=user_id, image_id=image_id, expected_rate=expected_rate, dadd=dadd)
        db.session.add(new_recommendation)
        db.session.commit()

def main(cursor, app):
    m = 5  # сколько ближайших соседей рассматриваем
    user_to_col = get_users(cursor)
    obj_to_row = get_images(cursor)
    matrix = make_matrix(user_to_col, obj_to_row, cursor)
    cosine_sim_matrix = cosine_matrix(matrix)
    top_neighbor_matrix = neigbohood(cosine_sim_matrix, m)
    row_to_object = row_to_obj(obj_to_row)
    get_recommendation(top_neighbor_matrix, matrix, row_to_object, user_to_col, app)


if __name__ == "__main__":
    main()
