# app/modules/users/models.py

class User:
    def __init__(self, db):
        self.collection = db.users

    def find_user(self, username, password):
        return self.collection.find_one({"username": username, "password": password})

    def find_user_by_username(self, username):
        return self.collection.find_one({"username": username})

    def insert_user(self, username, password):
        self.collection.insert_one({"username": username, "password": password})
