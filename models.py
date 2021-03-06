from orator import DatabaseManager, Model
from orator.orm import belongs_to_many, has_many, scope, belongs_to
import config

db = DatabaseManager(config.DATABASE)
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

    @staticmethod
    def createForTelegram(chat_id, name):
        # Create the citizen and
        citizen = Citizen.create(name=name)

        # Assign Telegram as communication channel
        citizen.channels().attach(
            CommunicationType.find(CommunicationType.TELEGRAM), {
                'account_id': chat_id})

    @has_many
    def complaints(self):
        return Complaint

class CommunicationType(Model):
    MESSENGER = 1
    TELEGRAM = 2

    @belongs_to_many('citizen_communication')
    def citizens(self):
        return Citizen

class Complaint(Model):
    __guarded__ = []

    __timestamps__ = False

    @has_many
    def images(self):
        return ComplaintImage

    @scope
    def incomplete(self, query):
        return query.where('complaint_status_id', ComplaintState.INCOMPLETE)\
                    .order_by('id', 'DESC')

    @belongs_to
    def citizen(self):
        return Citizen

class ComplaintState(Model):
    __table__ = 'complaint_status'

    INCOMPLETE = 1
    COMPLETE = 2

class ComplaintImage(Model):
    __fillable__ = ['img']

    __table__ = 'img_complaint'

    @belongs_to
    def complaint(self):
        return Complaint

class District(Model):
    pass

class Authority(Model):
    pass
