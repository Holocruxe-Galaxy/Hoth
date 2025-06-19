import json
import boto3
import os
from botocore.exceptions import ClientError


# def get_encryption_key():
#     secret_name = "encryption_secrets"
#     region_name = os.getenv('REGION', 'us-east-1')

#     session = boto3.session.Session()
#     client = session.client(
#         service_name='secretsmanager',
#         region_name=region_name
#     )

#     try:
#         get_secret_value_response = client.get_secret_value(
#             SecretId=secret_name
#         )
#     except ClientError as e:
#         raise e

#     secret = get_secret_value_response['SecretString']
#     return json.loads(secret)


def get_mongo_db_secrets(secret_name:str)-> dict:
    #secret_name = f"mongo_db_secret_{os.getenv('STAGE')}"
    region_name = os.getenv('REGION', 'us-east-1')

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    secrets = get_secret_value_response['SecretString']
    #print(secrets)

    return json.loads(secrets)
