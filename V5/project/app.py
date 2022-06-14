#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

from extras import response
from prediction import prediction


def lambda_handler(event, context):
    """handle request http POST"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    try:
        payload_data = json.loads(event['body'])
        predict_response = prediction(payload_data)
        if not predict_response:
            logger.warning(f"no suggested-price for: {json.dumps(payload_data)}")
            return response(404, {})
        payload_data['response'] = predict_response
        logger.info(f'suggested-price for: {json.dumps(payload_data)}')

        return response(200, predict_response)

    except Exception as error:
        logger.error(f'Error in suggested-price V5: {error}')

        return response(400, {'error': str(error)})
