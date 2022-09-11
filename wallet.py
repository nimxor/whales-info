from db import _MongoDBService

client = _MongoDBService()


def get_policy(collection_name: str) -> dict:
    exp = client.getCollection().find_one({"collection_name": collection_name})
    return exp["policy_id"] if exp is not None else None


def get_matching_collections(collection_name: str) -> dict:
    return client.getCollection().find({"collection_name": {"$regex": collection_name}})[:5]


def get_collection(policy_id: str) -> dict:
    exp = client.getCollection().find_one({"policy_id": policy_id})
    return exp["collection_name"] if exp is not None else None


def remove_collection(collection_name: str) -> dict:
    return client.getCollection().delete_one({"collection_name": collection_name})


def init_collection(collection_name: str, policy_id: str) -> dict:
    return client.getCollection().insert_one({"collection_name": collection_name, "policy_id": policy_id})
