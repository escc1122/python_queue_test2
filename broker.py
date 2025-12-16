import dramatiq
from dramatiq.brokers.redis import RedisBroker

broker = RedisBroker(host="localhost", port=6379)
dramatiq.set_broker(broker)
