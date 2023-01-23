from opentele.api import API
from pyrogram import Client
api = API.TelegramDesktop.Generate('my_account')
app = Client("session_files/my_account", api_id=api.api_id, api_hash=api.api_hash)


async def main():
    await app.start()
    ...  # Invoke API methods
    await app.stop()


app.run(main())