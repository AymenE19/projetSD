from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, BulkWriteError

from course_extractor.app.utils.logging import log_message


class AtlasClient:
    def __init__(self,  db_uri: str, db_name: str):
        self.mongodb_client = MongoClient(db_uri)
        self.db = self.mongodb_client[db_name]

    def ping(self):
        return self.mongodb_client.admin.command('ping')

    def insert_one(self, collection_name: str, item: dict, ignore_duplicates: bool = False):
        try:
            return self.db[collection_name].insert_one(item).inserted_id
        except DuplicateKeyError as e:
            if ignore_duplicates:
                log_message(f"Caught the following error while inserting data to the database {e}")
            else:
                raise e

    def get_one(self, collection_name: str, _filter: dict = None) -> dict:
        return self.db[collection_name].find_one(filter=_filter)

    def insert_many(self, collection_name: str, items: list[dict], ignore_duplicates: bool = False):
        try:
            return self.db[collection_name].insert_many(items, ordered=False).inserted_ids
        except BulkWriteError as e:
            if ignore_duplicates:
                log_message(f"Caught the following error while inserting data to the database {e}")
            else:
                raise e

    def get_many(self, collection_name: str, _filter: dict = None, limit: int = 0) -> list[dict]:
        return list(self.db[collection_name].find(filter=_filter, limit=limit))

    def update_one(self, collection_name: str, item_id: int, new_data: dict):
        result = self.db[collection_name].update_one({'_id': item_id}, {'$set': new_data}, True)

        if result.modified_count > 0:
            log_message(f"Document {item_id} updated successfully.")
        else:
            log_message(f"No changes made or document {item_id} was not found.")
