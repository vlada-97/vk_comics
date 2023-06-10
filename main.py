import argparse
import json
import logging
import os
import pathlib
import random
import re

import requests
from dotenv import load_dotenv


class VKapiError(BaseException):
    def __init__(self, response, message='VK Api error!'):
        self.response = response['error']['error_msg']
        self.message = message
        super().__init__(f'{self.message}: {self.response}')


def choose_random_comics_num():
    xkcd_last_url = 'https://xkcd.com/info.0.json'
    response = requests.get(xkcd_last_url)
    response.raise_for_status()
    response = response.json()

    last_comics_num = response['num']
    return random.randint(2, last_comics_num)


def get_image(img):
    response = requests.get(img)
    response.raise_for_status()
    with open(os.path.join(path, rf'{title}.png'), 'wb') as file:
        file.write(response.content)


def get_upload_url(access_token, group_id, vk_version):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    uploading_address = requests.post(url, params={
        'access_token': access_token,
        'group_id': group_id,
        'v': vk_version
    })
    uploading_address.raise_for_status()
    uploading_address = uploading_address.json()
    return uploading_address


def save_server_photo(upload_url, title, access_token, group_id, vk_version):
    with open(os.path.join(path, rf'{title}.png'), 'rb') as file:
        photo = {
            'photo': file
        }
        response = requests.post(upload_url, params={
            'access_token': access_token,
            'group_id': group_id,
            'v': vk_version
        }, files=photo)
    response.raise_for_status()
    if response['error']['error_msg']:
        raise VKapiError(response)
    response = response.json()
    return response['photo'], response['server'], response['hash']


def save_wall_photo(photo, server, photo_hash, access_token, group_id, vk_version, comment):
    save_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'access_token': access_token,
        'group_id': group_id,
        'v': vk_version,
        "photo": photo,
        'server': server,
        'hash': photo_hash,
        'caption': comment
    }
    response = requests.post(save_url, params=params)
    response.raise_for_status()
    if response['error']['error_msg']:
        raise VKapiError(response)
    response = response.json()
    return response['response'][0]['owner_id'], response['response'][0]['id']


def post_wall_photo(owner_id, photo_id, access_token, group_id, vk_version, comment):
    post_url = 'https://api.vk.com/method//wall.post'
    attachment = f'photo{owner_id}_{photo_id}'
    params = {
        'access_token': access_token,
        'group_id': group_id,
        'v': vk_version,
        'owner_id': f'-{vk_group_id}',
        'from_group': 1,
        'attachments': attachment,
        'message': comment
    }
    response = requests.post(post_url, params=params)
    response = response.json()
    if response['error']['error_msg']:
        raise VKapiError(response)
    response.raise_for_status()


if __name__ == '__main__':
    load_dotenv()
    vk_group_id = os.environ["VK_GROUP_ID"]
    vk_access_token = os.environ["VK_ACCESS_TOKEN"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default='comics',
                        help="Comics path name")
    args = parser.parse_args()
    path = args.path
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    params = {
        'access_token': vk_access_token,
        'group_id': vk_group_id,
        'v': 5.131
    }
    try:
        random_num = choose_random_comics_num()
        url = f'https://xkcd.com/{random_num}/info.0.json'
        response = requests.get(url)
        response.raise_for_status()
        response = response.json()

        img = response.get('img')
        comment = response.get("alt")
        title = response.get('title')
        title = re.sub(r'\W', ' ', title)
        get_image(img)

        upload_url = get_upload_url(
            params['access_token'], params['group_id'], params['v'])
        if upload_url['error']['error_msg']:
            raise VKapiError(upload_url)
        else:
            upload_url = upload_url['response']['upload_url']
            photo, server, photo_hash = save_server_photo(
                upload_url, title, params['access_token'], params['group_id'], params['v'])
            owner_id, photo_id = save_wall_photo(
                photo, server, photo_hash, params['access_token'], params['group_id'], params['v'], comment)
            post_wall_photo(
                owner_id, photo_id, params['access_token'], params['group_id'], params['v'], comment)
    except VKapiError as ex:
        logging.error(ex)
    except (OSError, FileNotFoundError) as ex:
        logging.error(ex)
    except (ConnectionError, RuntimeError) as ex:
        logging.error(ex)
    finally:
        os.remove(os.path.join(path, rf'{title}.png'))
