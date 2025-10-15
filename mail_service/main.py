from faststream import FastStream
from broker import broker
import subscribers  # noqa

app = FastStream(broker)
