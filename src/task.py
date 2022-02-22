import json
import os
import pprint

from celery import Celery, bootsteps
from celery.utils.log import get_task_logger
from kombu import Consumer, Exchange, Queue

from helpers import send_sms

logger = get_task_logger(__name__)

AUTH_SMS_QUEUE = 'auth.events.send.sms'
AUTH_POC_QUEUE = 'auth.events.fanout.poc'

exchange = Exchange('auth.event.exchange', type='direct')
fanout_exchange = Exchange('auth.fanout.exchange', type='fanout')

sms_queue = Queue(name=AUTH_SMS_QUEUE,
                  exchange=exchange, routing_key=AUTH_SMS_QUEUE)
poc_queue = Queue(name=AUTH_POC_QUEUE, exchange=fanout_exchange,
                  routing_key=AUTH_POC_QUEUE)


celery_app = Celery(
    'consumer',
    broker=os.environ.get('CELERY_BROKER_URL'),
    backend=os.environ.get('REDIS')
)


class SMSServiceConsumer(bootsteps.ConsumerStep):
    def get_consumers(self, channel):
        return [Consumer(channel,
                         queues=[sms_queue],
                         callbacks=[self.handle_message],
                         accept=['json'])]

    @staticmethod
    @celery_app.task(name=AUTH_SMS_QUEUE)
    def handle_message(body, message):
        logger.info('sms send task intiated')
        send_sms(body)
        message.ack()


class POCConsumer(bootsteps.ConsumerStep):
    def get_consumers(self, channel):
        return [Consumer(channel,
                         queues=[poc_queue],
                         callbacks=[self.handle_message],
                         accept=['json'])]

    @staticmethod
    @celery_app.task(name=AUTH_POC_QUEUE)
    def handle_message(body, message):
        logger.info('auth user sync poc task intiated')
        logger.info(
            f'request to sync received for user {body["user"]}')
        message.ack()


celery_app.steps['consumer'].add(SMSServiceConsumer)
celery_app.steps['consumer'].update([POCConsumer])


if __name__ == '__main__':
    celery_app.start()
