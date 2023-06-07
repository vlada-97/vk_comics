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


def generate_random_comics():
    xkcd_last_url = 'https://xkcd.com/info.0.json'
    response = requests.get(xkcd_last_url)
    response.raise_for_status()
    response = response.json()

    last_comics = response['num']
    random_comics = random.randint(2, last_comics)
    return random_comics


def get_image(response):
    img = response.get('img')
    comment = response.get("alt")
    title = response.get('title')
    title = re.sub(r'\W', ' ', title)

    response = requests.get(img)
    with open(os.path.join(path, rf'{title}.png'), 'wb') as file:
        file.write(response.content)
    return response, title, comment


def get_token():
    autorize_url = 'https://oauth.vk.com/authorize'
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'display': 'popup',
        'response_type': 'token',
        'scope': 'scope=photos,groups,wall',
        'v': 5.131
    }
    response = requests.post(autorize_url, params=params)
    token_link = response.url  # follow the link


def saveServerPhoto(title, params):
    photo = {
        'photo': open(os.path.join(path, rf'{title}.png'), 'rb')
    }
    response = requests.post(upload_url, params=params, files=photo)
    response.raise_for_status()
    response = response.json()
    return response


def saveWallPhoto(response, params, comment):
    save_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params.update({
        "photo": response['photo'],
        'server': response['server'],
        'hash': response['hash'],
        'caption': comment
    })
    response_save = requests.post(save_url, params=params)
    response_save.raise_for_status()
    response_save = response_save.json()
    return response_save


def post_wall_photo(response, params, comment):
    post_url = 'https://api.vk.com/method//wall.post'
    response = response['response']
    attachment = 'photo{0}_{1}'.format(
        response[0]['owner_id'], response[0]['id'])
    params.update({
        'owner_id': f'-{group_id}',
        'from_group': 1,
        'attachments': attachment,
        'message': comment
    })
    response_save = requests.post(post_url, params=params)
    response_save.raise_for_status()


if __name__ == '__main__':
    load_dotenv()
    group_id = os.environ["group_id"]
    client_id = os.environ["client_id"]
    upload_url = os.environ["upload_url"]
    access_token = os.environ["access_token"]
    redirect_uri = os.environ["redirect_uri"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default='comics',
                        help="Comics path name")
    args = parser.parse_args()
    path = args.path
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    params = {
        'access_token': access_token,
        'group_id': group_id,
        'v': 5.131
    }
    try:
        random_num = generate_random_comics()
        url = f'https://xkcd.com/{random_num}/info.0.json'
        response = requests.get(url)
        response.raise_for_status()
        response = response.json()

        response_img, title_img, comment_img = get_image(response)
        response_saveServer = saveServerPhoto(title_img, params)
        response_saveWall = saveWallPhoto(
            response_saveServer, params, comment_img)
        post_wall_photo(response_saveWall, params, comment_img)
        os.remove(f"{path}/{title_img}.png")
    except (OSError, FileNotFoundError) as ex:
        logging.error(ex)
    except (ConnectionError, RuntimeError) as ex:
        time.sleep(60)
        logging.error(ex)
