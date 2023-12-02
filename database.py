import index_scraping
import date_searching
from config.consts import *
import psycopg2
from sqlalchemy import create_engine


def get_connection(params, link):
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()
    engine = create_engine(link)
    return [connection, cursor, engine]


def db_creation(interval, period):
    connection, cursor, engine = get_connection(params=PARAMS_DEFAULT, link=LINK_DEFAULT)

    start_date = date_searching.get_date_x_periods_from_today(delta=interval, period=period)
    # end_date = functions_date_searching.get_date_x_periods_from_today(delta = 2, period = "wk")
    # end_date = end_date

    index_scraping.get_index_historical_data_to_database(connection=connection, engine=engine, indexes=INDEXES_DEFAULT,
                                                         start_date=start_date, frequency=FREQUENCY_DEFAULT,
                                                         suffix=SUFFIX_DEFAULT)
    index_scraping.union_all_tables_to_one(connection=connection, cursor=cursor, table_name=TABLE_NAME_DEFAULT,
                                           order_column=ORDER_COLUMN_DEFAULT)

    for table in INDEXES_DEFAULT:
        cursor.execute(f"DROP TABLE IF EXISTS {table}_{SUFFIX_DEFAULT};")
        connection.commit()

    connection.close()


def db_update():
    connection, cursor, engine = get_connection(params=PARAMS_DEFAULT, link = LINK_DEFAULT)
    index_scraping.update_indexes_prices_table(connection=connection, engine=engine, cursor=cursor, table_name=TABLE_NAME_DEFAULT,
                                                        frequency=FREQUENCY_DEFAULT)
    connection.close()