channels_to_parse = [
    {"id": -1001081170974, "name": "Профунктор"},
    {"id": -1001008635019, "name": "Memes"},
    # {"id": 233835147, "name": "Таня"},
    {"id": -1001082475147, "name": "Офисная крыса"},
    #{"id": 234558922, "name": "me"},
]

hours_to_parse = 30


async def show_all_chats(client):

    async for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID', dialog.id)
