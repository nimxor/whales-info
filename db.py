from typing import Collection, Mapping, Any, final

from pymongo import MongoClient
import os


@final
class _MongoDBService:
    _inst = None
    _inited = False
    _mongo_client = None

    def __new__(cls) -> '_MongoDBService':
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst

    def __init__(self) -> None:
        if type(self)._inited:
            return
        username = os.environ['MONGODB_USERNAME']
        password = os.environ['MONGODB_PASSWORD']
        # CONNECTION_STRING = "mongodb://{0}:{1}@tipping-bot-db:27017".format(username, password)
        CONNECTION_STRING = "mongodb+srv://{0}:{1}@cluster0.mtyoupg.mongodb.net/?retryWrites=true&w=majority".format(
            username, password)
        self._mongo_client = MongoClient(CONNECTION_STRING)
        print(self._mongo_client)
        type(self)._inited = True

    def getClient(self) -> MongoClient[Mapping[str, Any]]:
        return self._mongo_client

    def getCollection(self) -> Collection[Mapping[str, Any]]:
        return self._mongo_client['jpg']["whales-info"]
