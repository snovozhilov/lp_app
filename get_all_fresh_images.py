from sql_stuff import create_app
from tg_parser.telegram_parser_2 import get_fresh_images, client


def run_parser():
    app = create_app()
    with app.app_context():
        with client:
            client.loop.run_until_complete(get_fresh_images())


if __name__ == "__main__":
    run_parser()
