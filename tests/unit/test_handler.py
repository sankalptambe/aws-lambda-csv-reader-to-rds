import json
import pytest
from src.csv_reader import app


# pip install pytest py-mock


@pytest.fixture()
def s3_event():
    """ Generates API GW Event"""

    return {
          "Records": [
            {
              "eventVersion": "2.0",
              "eventSource": "aws:s3",
              "awsRegion": "ap-south-1",
              "eventTime": "1970-01-01T00:00:00.000Z",
              "eventName": "ObjectCreated:Put",
              "userIdentity": {
                "principalId": "EXAMPLE"
              },
              "requestParameters": {
                "sourceIPAddress": "127.0.0.1"
              },
              "responseElements": {
                "x-amz-request-id": "EXAMPLE123456789",
                "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
              },
              "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "testConfigRule",
                "bucket": {
                  "name": "csv-reader-localstack",
                  "ownerIdentity": {
                    "principalId": "EXAMPLE"
                  },
                  "arn": "arn:aws:s3:::csv-reader-localstack"
                },
                "object": {
                  "key": "cities.csv",
                  "size": 1024,
                  "eTag": "0123456789abcdef0123456789abcdef",
                  "sequencer": "0A1B2C3D4E5F678901"
                }
              }
            }
          ]
        }


def test_lambda_handler(s3_event, mocker):

    ret = app.lambda_handler(s3_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "Success"
    # assert "location" in data.dict_keys()
