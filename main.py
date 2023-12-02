import psycopg2
import database
import time
import schedule
from config.consts import PARAMS_DEFAULT, START_X_PERIODS_AGO, START_X_UNIT, TABLE_NAME_DEFAULT


def main():
    conn = psycopg2.connect(**PARAMS_DEFAULT)
    cur = conn.cursor()
    cur.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE  table_name   = '{TABLE_NAME_DEFAULT}'
                );
            """)
    exists = cur.fetchone()[0]
    if exists:
        database.db_update()
    else:
        database.db_creation(interval=START_X_PERIODS_AGO, period=START_X_UNIT)



if __name__ == "__main__":
    for run_time in ["01:05", "07:05", "13:05", "19:05", "23:05"]:
        schedule.every().day.at(run_time).do(main)
    while True:
        schedule.run_pending()
        time.sleep(10)


