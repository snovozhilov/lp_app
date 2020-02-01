import psycopg2
from sql_stuff import create_app
from recommendations.recommendations import main


def run_recommendations():
    app = create_app()

    # make a cursor (change to sqlalchemy)
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='localhost')
    cursor = conn.cursor()
    main(cursor, app)


if __name__ == "__main__":
    run_recommendations()
