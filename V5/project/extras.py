#!/usr/bin/env python
# -*- coding: utf-8 -*-import json

import yaml
import os
import sys
import json
import boto3


def get_config():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_directory)
    with open(f'{current_directory}/config.yaml', 'r') as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)

    return config


def response(status_code=200, body={}):
    return {
        "statusCode": status_code,
        "body": json.dumps(body, ensure_ascii=False),
        "headers": {
            "Content-Type": "application/json",
        }
    }


def download_model(path_parent, name_file):
    temp_dir = '/tmp'
    if os.path.exists(f'{temp_dir}/{name_file}'):
        return True
    bucket_name = os.environ['MyBucket']
    s3 = boto3.client('s3')
    path_file = f'{path_parent}/{name_file}'
    response = s3.list_objects(Bucket=bucket_name, Prefix=path_file)

    if not 'Contents' in response:
        return False
    with open(f'{temp_dir}/{name_file}', 'wb') as f:
        s3.download_fileobj(bucket_name, path_file, f)

    return True
