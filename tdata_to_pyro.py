from TGConvertor.manager.manager import SessionManager
from pathlib import Path

from opentele.api import API

api = API.TelegramAndroid.Generate()
API_ID = api.api_id
API_HASH = api.api_hash


def main():
    session = SessionManager.from_tdata_folder(Path("sessions/6283140335980/tdata"))
    print(session)
    res = session.pyrogram_client()
    print(res)


if __name__ == "__main__":
    main()