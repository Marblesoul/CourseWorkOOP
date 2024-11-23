import json
import os

import requests
from dotenv import load_dotenv

upload_report = {}

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
        for photo in response.json()['response']['items']:
            max_size = max(photo['sizes'], key=lambda x: x['width'] + x['height'])
            created_date = photo['date']
            photo_url = max_size['url']
            photo_name = str(photo['likes']['count'])
            if photo_name not in upload_report:
                upload_report[photo_name] = dict(size=max_size['type'], url=photo_url)
            else:
                photo_name = f'{photo_name}_{created_date}'
                upload_report[photo_name] = dict(size=max_size['type'], url=photo_url)
        return response.status_code


def make_upload_report():
    with open(os.path.join(os.getcwd(), 'report.json'), 'w') as f:
        f.write(json.dumps(upload_report, indent=4, ensure_ascii=False))
        print('Отчет о загрузке сохранен в report.json')


class YandexDisk:
    def __init__(self, token):
        self.token = token
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/'
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def _make_request_url(self, method):
        return self.base_url + method

    def make_folder(self, folder_name):
        params = {
            'path': folder_name
        }

        response = requests.put(self._make_request_url('resources'),
                                params=params,
                                headers=self.headers)
        return print(f'Папка "{folder_name}" успешно создана в облаке'
                     if 200 <= response.status_code < 300
                     else f'Ошибка при создании папки "{folder_name}" код ошибки: {response.status_code}')


    def upload_files(self, folder_name):
        self.make_folder(folder_name)
        counter = 1
        for photo_name, data in upload_report.items():
            params = {
                'path': f'{folder_name}/{photo_name}.jpg',
                'url': data['url'],
            }
            upload_response = requests.post(self._make_request_url('resources/upload'), params=params, headers=self.headers)
            if 200 <= upload_response.status_code < 300:
                print(f'Файл "{photo_name}.jpg" {counter} из {len(upload_report)} успешно загружен в облачную папку "{folder_name}"')
                counter += 1
            else:
                print(f'Ошибка при загрузке файла "{photo_name}.jpg" код ошибки: {upload_response.status_code}')
        make_upload_report()
        print('*' * 50)
        return print('Загрузка завершена')


if __name__ == "__main__":
    load_dotenv('config.env')
    vk = VKApp(os.getenv('VK_TOKEN'))
    get_photo = vk.get_profile_photos('ENTER VK ID HERE')
    yad = YandexDisk(os.getenv('YANDEX_TOKEN'))
    yad.upload_files('vk_photos')