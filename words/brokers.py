from brokers.rabbit_broker import SafeRabbitBroker
from faststream.rabbit import RabbitMessage
import config

broker = SafeRabbitBroker(host=config.RABBIT_HOST)

def message_decoder(msg):
    return dict(msg.body.decode())

@broker.subscriber("words_notifications", decoder=message_decoder)
async def handle_words_notification(msg: RabbitMessage):
    print(f"mesage { msg.body} type: {type(msg.body)}")

