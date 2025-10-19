from faststream import FastStream

from src import subscribers  # noqa
from src.broker import broker

app = FastStream(broker)
