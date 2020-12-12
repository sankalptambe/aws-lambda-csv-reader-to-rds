import json
import urllib.parse
import boto3
import os
import csv
import logging
import traceback
import pyodbc
import time

if os.getenv('AWS_SAM_LOCAL'):
    s3_resource = boto3.resource('s3', endpoint_url='http://localhost:4566')  # http://docker.for.mac.localhost:4566
else:
    s3_resource = boto3.resource('s3')

sql_driver = 'ODBC Driver 17 for SQL Server'
sql_host = f"{os.getenv('SQL_HOST')},{os.getenv('SQL_PORT')}"
sql_user = os.getenv('SQL_USER')
sql_password = os.getenv('SQL_PASSWORD')
sql_db = os.getenv('SQL_DB')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn_string: str = f"DRIVER={sql_driver};SERVER={sql_host};UID={sql_user};PWD={sql_password};timeout=1"
    logger.info(conn_string)
    cnx = pyodbc.connect(conn_string)
except Exception as e:
    logger.error(f"ERROR: Cannot connect to database.\n{traceback.format_exc()}")
    raise e


def log_err(err) -> object:
    """
    :param err: string
    :return:
    :rtype: object
    """
    logger.error(err)
    return {"body": err, "headers": {}, "statusCode": 400,
            "isBase64Encoded": "false"}


logger.info("Cold start complete.")


def lambda_handler(event, context):

    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

        s3_object = s3_resource.Object(bucket, key)
        data = s3_object.get()['Body'].read().decode('utf-8').splitlines()

    except:
        return log_err(
            "Error getting object {} from bucket {}. "
            "Make sure they exist and your bucket is in the same region as this function.".format(key, bucket))

    else:

        lines = csv.reader(data)
        headers = next(lines, None)
        print('headers: %s' % [header.strip().replace('"', '') for header in headers])

        data = [[x.strip().replace('"', '') for x in line] for line in lines if line != []]

        chunksize = 10
        chunks = [data[i:i + chunksize] for i in range(0, len(data), chunksize)]

        cursor = cnx.cursor()

        try:

            cursor.execute(f'Use {sql_db}')

            cursor.fast_executemany = True  # new in pyodbc 4.0.19

            sql = "INSERT INTO cities (LatD, LatM, LatS, NS, LonD, LonM, LonS, EW, City, State) " \
                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

            t0 = time.time()

            for chunk in chunks:
                cursor.executemany(sql, chunk)

            logger.info(f' Time taken to bulk insert: {time.time() - t0:.1f} seconds')

            cursor.commit()

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Success"
                }),
            }

        except Exception as e:
            logger.error(e)
            return log_err('Database connection error. Please check the DB or the table name.')
