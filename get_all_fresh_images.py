from tg_parser import create_app
from tg_parser.telegram_parser_2 import get_fresh_images, client

app = create_app()
with app.app_context():
    with client:
        client.loop.run_until_complete(get_fresh_images())
