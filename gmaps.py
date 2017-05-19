# -*- coding: utf-8 -*-
import requests
import config

class LimaException(Exception):
    message = 'Ubicación fuera de Lima'

class GMaps(object):
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'

    @staticmethod
    def get_district_name(lat, _long):
        data = requests.get('{}?latlng={},{}&location_type=APPROXIMATE&result_type=locality&key={}'.format(
            GMaps.base_url, lat, _long, config.GOOGLE_MAPS_KEY)).json()
        print data
        address_components = data['results'][0]['address_components']

        # departments have types colloquial_area, locality, political
        dep_types = ['colloquial_area', 'locality', 'political']
        in_lima = False
        for results in data['results']:
            for item in results['address_components']:
                if item['types'] == dep_types and item['long_name'] == 'Lima':
                    in_lima = True

        if in_lima:
            for results in data['results']:
                for item in results['address_components']:
                    # districts have types locality and political
                    if item['types'] == ['locality', 'political']:
                        return item['long_name']

            return None
        else:
            raise LimaException
