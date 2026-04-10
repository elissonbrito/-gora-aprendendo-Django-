import os
from datetime import datetime
from pymongo import MongoClient
import redis

class MongoAuditService:
    def __init__(self):
        self.client = None
        self.db = None
        try:
            self.client = MongoClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017/'), serverSelectionTimeoutMS=1000)
            self.client.admin.command('ping')
            self.db = self.client[os.getenv('MONGO_DB', 'agora')]
        except Exception:
            self.client = None
            self.db = None

    def log(self, collection, payload):
        if self.db is None:
            return
        payload['timestamp'] = datetime.utcnow()
        self.db[collection].insert_one(payload)

mongo_audit = MongoAuditService()

class RedisCacheService:
    def __init__(self):
        self.client = None
        try:
            self.client = redis.from_url(os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'), socket_connect_timeout=1)
            self.client.ping()
        except Exception:
            self.client = None

    def get(self, key):
        if not self.client:
            return None
        value = self.client.get(key)
        return value.decode('utf-8') if value else None

    def set(self, key, value, ex=60):
        if self.client:
            self.client.set(key, value, ex=ex)

    def delete(self, key):
        if self.client:
            self.client.delete(key)

cache_service = RedisCacheService()
