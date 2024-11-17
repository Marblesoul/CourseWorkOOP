import os
import requests
from datetime import datetime
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

    def get_profile_photos(self, owner_id: str, count: int = 5):
        params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'count': count,
            'extended': 1
        }
        response = requests.get(self._make_request_url('photos.get'), params={**self.params, **params})
        return response.json()

    def download_profile_photos(self, owner_id: str, count: int = 5):
        data = self.get_profile_photos(owner_id, count)
        temp_path = os.path.join(os.getcwd(), 'temp_photos')
        if not os.path.exists('temp_photos'):
            os.mkdir('temp_photos')
        for photo in data['response']['items']:
            photo_url = photo['orig_photo']['url']
            photo_name = photo['likes']['count']
            if not os.path.exists(f'{temp_path}/{photo_name}.jpg'):
                with open(f'{temp_path}/{photo_name}.jpg', 'wb') as file:
                    file.write(requests.get(photo_url).content)
            else:
                current_date = datetime.now().date().strftime('%d-%m-%Y')
                with open(f'{temp_path}/{photo_name}_{current_date}.jpg', 'wb') as file:
                    file.write(requests.get(photo_url).content)

        return f'Фотографии: {', '.join(os.listdir(temp_path))}\nсохранены в папке {temp_path}'



if __name__ == "__main__":
    load_dotenv('config.env')

    vk = VKApp(os.getenv('VK_TOKEN'))
    photos = vk.get_profile_photos('125401800')
    pprint(photos['response']['items'])

    download_photos = vk.download_profile_photos('125401800')
    print(download_photos)