from models import Citizen

citizen = Citizen.where_has('channels', lambda ch: ch.where('account_id', 1379137542147034)).first()

print citizen.to_json()