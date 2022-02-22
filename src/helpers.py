import logging
import os
from typing import Dict

import requests

logger = logging.getLogger(__name__)


def send_sms(sms_obj: Dict) -> object:
    if not sms_obj.get('username') or not sms_obj.get('message'):
        return
    body = {
        'Username': os.environ.get('SMS_GATEWAY_USERNAME'),
        'Password': os.environ.get('SMS_GATEWAY_PASSWORD'),
        'To': sms_obj['username'],
        'Message': sms_obj['message'],
        'From': os.environ.get('FROM_TEXT')
    }
    if not os.environ.get('DEBUG'):
        requests.post(os.environ.get('SMS_GATEWAY_URL'), data=body, headers={
            'Content-Type': 'application/x-www-form-urlencoded'})
    logger.info(f'sms sent to {sms_obj["username"]}')
    return
