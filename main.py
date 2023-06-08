import argparse
import json
import logging
import os
import pathlib
import random
import re
import time

import requests
from dotenv import load_dotenv


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
    if response.ok:
        with open(os.path.join(path, rf'{title}.png'), 'wb') as file:
            file.write(response.content)


def get_upload_url(params):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    uploading_address = requests.post(url, params=params)
    uploading_address = uploading_address.json()
    print(uploading_address)
    if uploading_address:
        return uploading_address['response']['upload_url']


def save_server_photo(upload_url, title, params):
    with open(os.path.join(path, rf'{title}.png'), 'rb') as file:
        photo = {
            'photo': file
        }
        response = requests.post(upload_url, params=params, files=photo)
        response.raise_for_status()
        response = response.json()
    return response['photo'], response['server'], response['hash']


def save_wall_photo(photo, server, hash, params, comment):
    save_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params.update({
        "photo": photo,
        'server': server,
        'hash': hash,
        'caption': comment
    })
    response = requests.post(save_url, params=params)
    response.raise_for_status()
    response = response.json()
    return response['response'][0]['owner_id'], response['response'][0]['id']


def post_wall_photo(owner_id, id, params, comment):
    post_url = 'https://api.vk.com/method//wall.post'
    attachment = 'photo{0}_{1}'.format(
        owner_id, id)
    params.update({
        'owner_id': f'-{vk_group_id}',
        'from_group': 1,
        'attachments': attachment,
        'message': comment
    })
    response = requests.post(post_url, params=params)
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

        upload_url = get_upload_url(params)
        photo, server, hash = save_server_photo(upload_url, title, params)
        owner_id, id = save_wall_photo(
            photo, server, hash, params, comment)
        post_wall_photo(owner_id, id, params, comment)
    except (OSError, FileNotFoundError) as ex:
        logging.error(ex)
    except (ConnectionError, RuntimeError) as ex:
        time.sleep(60)
        logging.error(ex)
    finally:
        os.remove(f"{path}/{title}.png")
