import os
PASSWORD = os.getenv('PASSWORD')

PARAMS_DEFAULT = {
    "host": "ep-fragrant-pond-03700094.ap-southeast-1.aws.neon.fl0.io",
    "database": "sp500-nasdaq-dow-russell",
    "user": "fl0user",
    "password": f"{PASSWORD}",
    "port": 5432,
    "sslmode": "require"
}
LINK_DEFAULT = "postgresql://fl0user:ur3xF5qjeQhp@ep-fragrant-pond-03700094.ap-southeast-1.aws.neon.fl0.io:5432/sp500-nasdaq-dow-russell?sslmode=require"
FREQUENCY_DEFAULT = 'mo'
SUFFIX_DEFAULT = "index_prices"
INDEXES_DEFAULT = ["GSPC", "DJI", "IXIC", "RUT", "NYA"]
TABLE_NAME_DEFAULT = "all_indexes_prices"
ORDER_COLUMN_DEFAULT = "date"
START_X_PERIODS_AGO = 10
START_X_UNIT = "yr"
