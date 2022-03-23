import time
import logging
from datetime import datetime, timedelta
from math import trunc

from decouple import config

import player_functions
import query_functions
import etl

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("dataofempires.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def main():
    now = datetime.now()
    specific_timestamp = datetime(2022, 3, 1, 0, 0)  # Year, month, day, hour, minutes
    now_less_1_hour = now - timedelta(weeks=0, days=0, hours=12, minutes=0)
    timestamp = trunc(time.mktime(specific_timestamp.timetuple()))
    etl.etl_matches(timestamp)
    # steam_id = config('STEAM_ID_CAPOCH')
    # player_functions.extract_player_matches(steam_id)

if __name__ == "__main__":
    main()
