#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


def get_body():
    """read event.json and return body"""
    with open('events/event.json') as file:
        event = json.load(file)
    return event["body"]


def get_environments():
    """read environments.json and return dict"""
    with open(f'environments.json') as file:
        environments = json.load(file)

    return environments["SuggestedV5Function"]
