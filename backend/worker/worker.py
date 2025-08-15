# TODO: implement RQ worker entrypoint

from rq import Worker, Queue, Connection

from ..app.config import settings

listen = ["default"]


if __name__ == "__main__":
    with Connection():
        worker = Worker(list(map(Queue, listen)))
        worker.work()
