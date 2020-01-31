import socks
import os
import datetime as dt
import imagehash
from tg_parser import tg_config
from tg_parser import channels_to_parse as ctp
from PIL import Image
from telethon import TelegramClient, events
from telethon.tl.types import InputMessagesFilterPhotos, MessageMediaPhoto
from model import db, ParsedImages

client = TelegramClient('session_name', tg_config.API_ID, tg_config.API_HASH, proxy=(
    socks.SOCKS5, tg_config.PROXY_IP, tg_config.PORT, True, tg_config.PROXYUSERNAME, tg_config.PROXYUSERNAMEPASS))

# set time
now = dt.datetime.now()
utcnow = dt.datetime.utcnow()

#замени принты на логирование

def get_phash(filename):
    try:
        phash = str(imagehash.phash(Image.open(filename)))
    except (NameError, IOError, TypeError, ValueError):
        print("get phash error, file deleted")
        os.remove(filename)
        phash = False
    return phash


def is_uniq_phash(phash, filename):
    phash_exists = ParsedImages.query.filter(ParsedImages.phash == phash).count()
    if not phash_exists:
        return True
    else:
        try:
            os.remove(filename)
        except(NameError, OSError):
            print('can not delete phash double')
        return False


def save_parsed_image_to_db(phash, chat_id, chat_name, full_filename, filename, published_ts, parsed_ts, dadd):
    if is_uniq_phash(phash, filename=full_filename):
        new_parsed_image = ParsedImages(phash=phash, chat_id=chat_id, chat_name=chat_name, full_filename=full_filename,
                                        filename=filename, published_ts=published_ts, parsed_ts=parsed_ts, dadd=dadd)
        db.session.add(new_parsed_image)
        db.session.commit()
        print(f"{chat_name}: download one more pic ")
    else:
        print(f"{chat_name}: already have same pic, not to save")


async def parse_chat(chat_id, chat_name, offset_date, chat_path):
    async for message in client.iter_messages(chat_id, offset_date=offset_date, filter=InputMessagesFilterPhotos,
                                              reverse=True):
        try:
            fname = f'{message.date.strftime("%y%m%d%H%M%S")}{message.media.photo.id}.jpg'  # дата + telegram id photo
        except (ValueError, TypeError, KeyError):
            fname = f'{message.date.strftime("%y%m%d%H%M%S")}{"0" * 9}.jpg'  # имя файла = цифры даты + нули
        filename = os.path.join(chat_path, fname)

        await message.download_media(filename, thumb=-1)  # скачать изображение в наибольшем разрешении

        phash = get_phash(filename)
        if phash:
            try:
                published_ts = message.date.isoformat()
            except (ValueError, TypeError, KeyError):
                published_ts = dt.datetime.utcnow().isoformat()
            parsed_ts = dt.datetime.utcnow().isoformat()
            dadd = dt.datetime.utcnow().strftime("%Y-%m-%d")

            save_parsed_image_to_db(phash=phash, chat_id=chat_id, chat_name=chat_name, full_filename=filename,
                                    filename=fname, published_ts=published_ts, parsed_ts=parsed_ts, dadd=dadd)


async def get_fresh_images():
    """настраивае пути для сохр. картинок, для каждого чата запускает функцию parse_chat(), передавая в нее нужные
    пути для сохранения """
    offset_date = dt.datetime.utcnow() - dt.timedelta(hours=ctp.hours_to_parse)
    basedir = os.path.abspath(os.path.dirname(__file__))
    images_storage_path = os.path.join(basedir, "..", "images_storage")
    os.makedirs(images_storage_path, exist_ok=True)

    for chat in ctp.channels_to_parse:
        chat_name = chat["name"]
        chat_id = chat["id"]
        chat_path = os.path.join(images_storage_path, chat_name)
        os.makedirs(chat_path, exist_ok=True)
        await parse_chat(chat_id, chat_name, offset_date, chat_path)


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(get_fresh_images())
