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
