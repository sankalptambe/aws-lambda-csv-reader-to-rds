import json
# import boto3
# import os
import logging
import traceback

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    logger.info(event)

    message = event['Records'][0]['Sns']['Message']

    logger.info("From SNS: " + message)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Inside success handler"
        }),
    }