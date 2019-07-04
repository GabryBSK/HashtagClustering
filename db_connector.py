from pymongo import MongoClient


# # # CONNECTOR # # #
class Connector():
    """
    Crea un connettore per svolgere operazioni sul database Atlas.
    """

    def __init__(self, name, psw):
        self.name = name
        self.psw = psw

    # Apre la connessione col database
    def open_connection(self):
        client = MongoClient("mongodb+srv://{}:{}*************.mongodb.net/test?retryWrites=true"
                             .format(self.name, self.psw))
        return client

    # Carica un record
    def upload_record(self, client, db_name, collection_name, record_to_insert):
        db = client.get_database(db_name)
        records = db.get_collection(collection_name)
        records.insert_one(record_to_insert)

    # Prende e stampa le occorrenze degli hashtag
    def get_hashtag_occurrences(self, client, db_name, collection_name):
        db = client.get_database(db_name)
        records = db.get_collection(collection_name)
        for result in records.aggregate([
            {"$unwind": "$hashtags"},
            {"$group": {
                "_id": "$hashtags",
                "count": {"$sum": 1}
                }
            }
        ]):
            print("{}: {}".format(result["_id"], result["count"]))

    # Esegue le query per il calcolo della distanza tra hashtag
    def get_distance(self, client, db_name, collection_name, query):
        result = []
        db = client.get_database(db_name)
        records = db.get_collection(collection_name)
        for element in records.find(query):
            result.append(element)
        print(len(result))
        return len(result)
