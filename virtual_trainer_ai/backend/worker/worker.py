"""RQ worker entrypoint."""

from rq import Connection, Queue, Worker
import redis

from ..app.config import settings

listen = ["default"]


if __name__ == "__main__":
    conn = redis.from_url(settings.redis_url)
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
