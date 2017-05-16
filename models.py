from orator import DatabaseManager, Model
from orator.orm import belongs_to_many

config = {
    'mysql': {
        'driver': 'mysql',
        'host': 'localhost',
        'database': 'green_case',
        'user': 'root',
        'password': 'root',
        'prefix': ''
    }
}

db = DatabaseManager(config)
Model.set_connection_resolver(db)

class ContaminationType(Model):
    pass

class Citizen(Model):
    __guarded__ = []

    @belongs_to_many
    def channels(self):
        return CommunicationType

    def createFromMessenger(self, chat_id, user_data):
        # Create the citizen and
        # assign messenger as communication channel

class CommunicationType(Model):

    @belongs_to_many
    def citizens(self):
        return Citizen
