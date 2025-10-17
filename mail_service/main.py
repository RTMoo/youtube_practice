from faststream import FastStream
from src.broker import broker
from src import subscribers  # noqa


app = FastStream(broker)
