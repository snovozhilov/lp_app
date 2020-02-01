from sql_stuff import db, create_app


def create_db():
    """создать все таблицы из model.py, если не сущесвуют"""
    db.create_all(app=create_app())


if __name__ == "__main__":
    create_db()
