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

    @belongs_to_many('citizen_communication')
    def channels(self):
        return CommunicationType

    @staticmethod
    def createForMessenger(chat_id, user_data):
        # Create the citizen and
        citizen = Citizen.create(name=user_data['first_name'])

        # Assign Messenger as communication channel
        citizen.channels().attach(
            CommunicationType.find(CommunicationType.MESSENGER), {
                'account_id': chat_id})

class CommunicationType(Model):
    MESSENGER = 1

    @belongs_to_many('citizen_communication')
    def citizens(self):
        return Citizen

class Complaint(Model):
    __guarded__ = []

    __timestamps__ = False

class ComplaintState(Model):
    INCOMPLETE = 1
