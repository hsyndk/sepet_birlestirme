
import requests


class GeocodeLocationConverter:
    
    def __init__(self):
        print("hüseyin_dik hehehe")
        
    
    def get_location_from_geocode(self, lat, lon):
        url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=en&zoom=18&addressdetails=1'
        try:
            result = requests.get(url=url)
            result_json = result.json()
            return result_json
        except:
            return {}

    def get_geocode_from_location(self, location):
        return None