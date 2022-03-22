import time
import logging
from datetime import datetime, timedelta
from math import trunc

from decouple import config

import cargarJSON

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("log_app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def main():
    now = datetime.now()
    now_less_1_hour = now - timedelta(hours=1, minutes=0)
    timestamp = trunc(time.mktime(now_less_1_hour.timetuple()))
    # cargarJSON.extract_matches(timestamp)
    steam_id = config('STEAM_ID_CAPOCH')
    cargarJSON.extract_player_matches(steam_id)

if __name__ == "__main__":
    main()
