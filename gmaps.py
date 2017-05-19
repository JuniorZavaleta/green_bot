import requests
import config

class GMaps(object):
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'

    @staticmethod
    def get_district_name(lat, _long):
        data = requests.get('{}?latlng={},{}&location_type=ROOFTOP&result_type=street_address&key={}'.format(
            GMaps.base_url, lat, _long, config.GOOGLE_MAPS_KEY)).json()

        address_components = data['results'][0]['address_components']

        for item in address_components:
            if 'locality' in item['types'] and 'political' in item['types'] and len(item['types']) == 2:
                return item['long_name']

        return None
