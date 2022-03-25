import time
import logging
from datetime import datetime, timedelta
from math import trunc

from decouple import config

import player_functions
import query_functions
import etl
import report_generator
import report_viewer

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("dataofempires.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def main():
    placeholder_option = 4
    if placeholder_option == 1:
        now = datetime.now()
        specific_timestamp = datetime(2022, 3, 7, 0, 0)  # Year, month, day, hour, minutes
        # now_less_1_hour = now - timedelta(weeks=0, days=0, hours=12, minutes=0)
        timestamp = trunc(time.mktime(specific_timestamp.timetuple()))
        etl.etl_matches(timestamp)
    elif placeholder_option == 2:
        steam_id = config('STEAM_ID_CAPOCH')
        player_functions.extract_player_matches(steam_id)
    elif placeholder_option == 3:
        report_generator.civ_winrate()
    elif placeholder_option == 4:
        for report in report_viewer.show_all_reports():
            report.show()
    elif placeholder_option == 5:
        etl.update_db()
    elif placeholder_option == 6:
        etl.batch_update(1)

if __name__ == "__main__":
    main()
