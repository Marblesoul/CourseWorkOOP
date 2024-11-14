import os
import requests
from pprint import pprint
from dotenv import load_dotenv

class VKApp:
    def __init__(self, token, version='5.199'):
        self.token = token
        self.v = version
        self.base_url = 'https://api.vk.com/method/'
        self.params = {
            'access_token': self.token,
            'v': self.v
        }

    def _make_request_url(self, method):
        return self.base_url + method

    def get_profile_photos(self, owner_id: str):
        params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'extended': 1
        }
        response = requests.get(self._make_request_url('photos.get'), params={**self.params, **params})
        return response.json()


if __name__ == "__main__":
    load_dotenv('config.env')

    vk = VKApp(os.getenv('VK_TOKEN'))
    photos = vk.get_profile_photos('123456789')
    pprint(photos['response']['items'])