import json
import os

import requests
from datetime import datetime
from dotenv import load_dotenv

path = os.path.join(os.getcwd(), 'temp_photos')
upload_report = []

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
        if not os.path.exists('temp_photos'):
            os.mkdir('temp_photos')

        """
        Если внимательно изучить ответ API метода photos.get, то можно увидеть, что
        самое большое фото хранится в поле orig_photo. Это поле содержит
        ссылку на оригинальное фото. Если мы будем скачивать оригинальное
        фото, то мы можем использовать ссылку из этого поля и не нужно перебирать фотографии поля sizes для определения наибольшего размера. Однако, в задании указан формат выходных данных который подразумевает получение максимального размера фотографии именно из sizes. В таком случае более просто код с загрузкой оригинала я закомментировал, оставлю код для скачивания максимального размера путем вычисления из поля sizes.
        """

        # for photo in data['response']['items']:
        #     photo_url = photo['orig_photo']['url']
        #     photo_name = photo['likes']['count']
        #     if not os.path.exists(f'{path}/{photo_name}.jpg'):
        #         with open(f'{path}/{photo_name}.jpg', 'wb') as file:
        #             file.write(requests.get(photo_url).content)
        #     else:
        #         current_date = datetime.now().date().strftime('%d-%m-%Y')
        #         with open(f'{path}/{photo_name}_{current_date}.jpg', 'wb') as file:
        #             file.write(requests.get(photo_url).content)

        for photo in data['response']['items']:
            max_size = max(photo['sizes'], key=lambda x: x['width'] + x['height'])
            photo_url = max_size['url']
            photo_name = photo['likes']['count']
            if not os.path.exists(f'{path}/{photo_name}.jpg'):
                with open(f'{path}/{photo_name}.jpg', 'wb') as file:
                    file.write(requests.get(photo_url).content)
                    upload_report.append(dict(file_name=file.name.split('/')[-1], size=max_size['type']))
            else:
                current_date = datetime.now().date().strftime('%d-%m-%Y')
                with open(f'{path}/{photo_name}_{current_date}.jpg', 'wb') as file:
                    file.write(requests.get(photo_url).content)
                    upload_report.append(dict(file_name=file.name.split('/')[-1], size=max_size['type']))

        return f'Фотографии: {', '.join(os.listdir(path))}\nсохранены в папке {path}'


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

    def make_upload_url(self, file_path, overwrite=False):
        params = {
            'path': file_path,
            'overwrite': overwrite
        }
        response = requests.get(self._make_request_url('resources/upload'),
                                params=params,
                                headers=self.headers)
        return response.json()['href']

    def upload_files(self, folder_name):
        self.make_folder(folder_name)
        for file in os.listdir(path):
            url = self.make_upload_url(f'{folder_name}/{file}')
            with open(os.path.join(path, file), 'rb') as f:
                uploader = requests.put(url, files={'file': f})
                if 200 <= uploader.status_code < 300:
                    print(f'Файл #{os.listdir(path).index(file) + 1} из '
                          f'{len(os.listdir(path))} загружен в облачную папку "{folder_name}"')
        make_upload_report()
        print('*' * 50)
        return print('Загрузка завершена')


if __name__ == "__main__":
    load_dotenv('config.env')
    vk = VKApp(os.getenv('VK_TOKEN'))
    download_photos = vk.download_profile_photos('125401800')
    yad = YandexDisk(os.getenv('YANDEX_TOKEN'))
    yad.upload_files('vk_photos')