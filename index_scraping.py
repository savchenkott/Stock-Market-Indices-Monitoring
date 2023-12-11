from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
import pandas as pd
import date_searching
import numpy as np



def get_index_historical_data(index, frequency, start_date):
    """
    The function returns historical data (price and volume) about a given index in a certain time period.
    The data is being web-scraped from Yahoo Finance. The time period starts with start_date and ends with today.
    :param index: str, the ticker symbol of an index.
    :param start_date: str, in YYYY-MM-DD format. The start of the period.
    :param frequency: str, either "d", "wk", or "mo".
    :return: pandas DataFrame with open, high, low, close, adjusted close prices, and volume.
    """

    end_date = datetime.now()
    periods = []
    for date in [start_date, end_date]:
        if type(date) != datetime:
            date = pd.to_datetime(date)
        period = int(time.mktime(date.timetuple()))
        periods.append(period)
    period1, period2 = periods

    index_name = index.upper()

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    url = f'https://finance.yahoo.com/quote/%5E{index_name}/history?period1={period1}&period2={period2}&interval=1{frequency}&filter=history&frequency=1{frequency}&includeAdjustedClose=true'

    result = requests.get(url, headers=headers)
    soup = BeautifulSoup(result.text, "html.parser")
    index_full_name = soup.find('h1', class_='D(ib) Fz(18px)').text.strip()
    rows = soup.find_all('tr', class_='BdT Bdc($seperatorColor) Ta(end) Fz(s) Whs(nw)')

    data = []
    for row in rows:
        date = row.find('td', class_='Py(10px) Ta(start) Pend(10px)').text.strip()
        open_price = (row.find_all('td', class_='Py(10px) Pstart(10px)')[0].text.strip().replace(',', ''))
        high_price = (row.find_all('td', class_='Py(10px) Pstart(10px)')[1].text.strip().replace(',', ''))
        low_price = (row.find_all('td', class_='Py(10px) Pstart(10px)')[2].text.strip().replace(',', ''))
        close_price = (row.find_all('td', class_='Py(10px) Pstart(10px)')[3].text.strip().replace(',', ''))
        adjusted_close_price = (row.find_all('td', class_='P'
                                                         'y(10px) Pstart(10px)')[4].text.strip().replace(',', ''))
        volume_i = (row.find_all('td', class_='Py(10px) Pstart(10px)')[5].text.strip().replace(',', ''))
        data.append({'date': date, 'index_full_name': index_full_name, 'index_name': (f"{index.lower()}"), 'open_price': open_price, 'high_price': high_price, 'low_price': low_price, 'close_price': close_price, 'adjusted_close_price': adjusted_close_price, 'volume_i': volume_i})

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'], format='%b %d, %Y').dt.date
    columns = ['open_price', 'high_price', 'low_price', 'close_price', 'adjusted_close_price', 'volume_i']
    for col in columns:
        df[col] = df[col].replace('-', np.nan).astype(float)
    return df


def get_index_historical_data_to_database(connection, engine, indexes, frequency, suffix, start_date, end_date = datetime.now()):
    """
    Web-scrapes historical data (prices and volume) of specific indexes in a given time period. Then puts each index
    data as a table in a database.
    :param connection: connection to the desired database
    :param engine: engine to the desired database
    :param indexes: list with strs, ticker symbols of wanted indexes.
    :param frequency: str, either "d", "wk", or "mo".
    :param suffix: str, the suffix of tables' names (prefix is index name "dji", suffix is "index_prices", the full name "dji_index_prices).
    :param start_date: str, in YYYY-MM-DD format. The start of the period.
    :param end_date: str, in YYYY-MM-DD format. The end of the period. Default = today.
    """

    for index in indexes:
        index_prices = get_index_historical_data(index=index, start_date=start_date,
                                                 frequency=frequency)
        index_name = index.lower()
        table_name = (index_name + '_' + str(suffix))

        index_prices.to_sql(table_name, engine, index=False, if_exists='replace')
        connection.commit()


def union_all_tables_to_one(connection, cursor, table_name, order_column = None):
    """
    Creates a new table in database which is the union of all tables.
    :param connection: Connection object, connected to the needed database.
    :param cursor: Cursor object, created for the same database.
    :param table_name: str, name of a table to be created.
    :param order_column: str, name of a column the table should be sorted by. Default = None.
    """

    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    connection.commit()
    cursor.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';")
    table_names = cursor.fetchall()
    table_names = [table[0] for table in table_names]

    union_query = " UNION ALL ".join(f"SELECT * FROM {table}" for table in table_names)
    if order_column == None:
        main_query = (f"CREATE TABLE {table_name} AS {union_query};")
    else:
        main_query = (f"CREATE TABLE {table_name} AS {union_query} ORDER BY {order_column};")

    cursor.execute(main_query)
    connection.commit()



def update_indexes_prices_table(connection, engine, cursor, table_name, frequency):
    """
    The function is intended to daily update the database, created by db_creation function. It updates the table with
    current dates and data (on prices and volume of the indexes in the table).
    :param connection: Connection object, connected to the needed database.
    :param cursor: Cursor object, created for the same database.
    :param table_name: str, name
    :param frequency: str, either "d", "wk", or "mo". The same frequency as in the current dataset
    """

    start_date = date_searching.get_date_x_periods_from_today(delta=3, period=frequency)
    suffix = f"updated_by_last_3_{frequency}"

    selecting_all_index_names = f"SELECT DISTINCT(index_name) FROM {table_name}"
    cursor.execute(selecting_all_index_names)
    indexes = cursor.fetchall()
    index_names = [i[0] for i in indexes]

    get_index_historical_data_to_database(connection=connection, engine=engine, indexes=index_names, start_date=start_date,
                                          frequency=frequency, suffix=suffix)

    selecting_columns_query = f"""SELECT column_name
                                    FROM information_schema.columns
                                    WHERE table_name = '{table_name}'"""
    cursor.execute(selecting_columns_query)
    columns = cursor.fetchall()
    columns_names = [i[0] for i in columns]
    columns_names_to_update = columns_names[3:]

    for i in index_names:

        for column in columns_names_to_update:

            updating_last_3_periods_query = f"""
                        UPDATE {table_name}
                        SET {column} = (
                            SELECT new.{column}
                            FROM {i}_{suffix} AS new
                            WHERE {table_name}.date = new.date AND {table_name}.index_name = new.index_name
                        )
                        WHERE EXISTS (
                            SELECT 1
                            FROM {i}_{suffix} AS new
                            WHERE {table_name}.date = new.date AND {table_name}.index_name = new.index_name)"""
            cursor.execute(updating_last_3_periods_query)
            connection.commit()

        delete_yesterdays_query = f"""
                            DELETE FROM {table_name}
                            WHERE date IN (SELECT date 
                            FROM {table_name} 
                            WHERE (date >= '{start_date}' 
                            AND (date NOT IN (SELECT date FROM {i}_{suffix})))) 
                            AND index_name = '{i}' """
        cursor.execute(delete_yesterdays_query)
        connection.commit()

        add_today_query = f"""
                        INSERT INTO {table_name} SELECT * FROM {i}_{suffix} WHERE (date = (SELECT date
                        FROM {i}_{suffix} 
                        WHERE (date >= '{start_date}'
                        AND (date NOT IN (SELECT date FROM {table_name} WHERE index_name = '{i}'))))
                        AND index_name = '{i}') """
        cursor.execute(add_today_query)
        connection.commit()

    for i in index_names:
        cursor.execute(f"DROP TABLE IF EXISTS {i}_{suffix};")
        connection.commit()
