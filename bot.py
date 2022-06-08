from vk_api import *
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import * # Create this file before start

import requests
import urllib.request
import os
import time
import glob
import random
import re

class bcolors:
    WARNING = '\033[93m'
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'

# Auth group bot
vk_group = VkApi(token=group_token)
vk_api_group = vk_group.get_api()
longpoll = VkBotLongPoll(vk_group, group_id=group_id)

# Auth user bot
vk_session_user = vk_api.VkApi(user_login, user_password)
vk_session_user.auth(token_only=True)
vk_api_user = vk_session_user.get_api()

print("Bot ready")

images_folder = os.path.join(os.path.dirname(__file__), 'images')



def post_image(from_id, filename):
    # # Getting upload server
    print(bcolors.WARNING + "[2/6] Getting upload server..." + bcolors.ENDC)
    upload_server = vk_api_user.photos.getWallUploadServer(group_id=group_id)
    upload_url = upload_server['upload_url']

    # # Post image to server
    print(bcolors.WARNING + "[3/6] Post image to server..." + bcolors.ENDC)
    file = open(filename, 'rb')
    files = { 'photo': file }
    response = requests.post(upload_url, files=files)
    response_json = response.json()
    file.close()
    os.remove(filename)

    # # Saving a photo
    print(bcolors.WARNING + "[4/6] Saving a photo..." + bcolors.ENDC)
    server = response_json['server']
    photo = response_json['photo']
    hash = response_json['hash']
    save_photo = vk_api_user.photos.saveWallPhoto(group_id=group_id, server=server, photo=photo, hash=hash)
    photo_id = save_photo[0]['id']
    owner_id = save_photo[0]['owner_id']

    # # Posting on the wall
    print(bcolors.WARNING + "[5/6] Posting on the wall..." + bcolors.ENDC)
    attachment = f"photo{owner_id}_{photo_id}"
    wall_post = vk_api_user.wall.post(owner_id=f"-{group_id}", attachments=attachment)
    #
    # # Send message
    print(bcolors.WARNING + "[6/6] Send message..." + bcolors.ENDC)
    wall_post_id = wall_post['post_id']
    link = f"https://vk.com/public{group_id}?w=wall-{group_id}_{wall_post_id}"
    vk_api_group.messages.send(user_id=from_id, random_id=get_random_id(), message=f"Картиночка загружена!\n {link}")
    #
    print()
    print(link)
    print(bcolors.OKGREEN + "Done!" + bcolors.ENDC)
    print()



def say(text):
    vk_api_group.messages.send(user_id=from_id, random_id=get_random_id(), message=text)



def load():
    if( len(glob.glob(images_folder + "/*.*")) > 0 ):
        list = glob.glob(images_folder + "/*.*")
        filename = random.choice(list)
        post_image(from_id, filename)
    else:
        say("В базе сейчас нет картинок")



def autoload(delta, type, limit):
    delta = int(delta)
    if len(glob.glob(images_folder + "/*.*")) == 0:
        say("В базе сейчас нет картинок")
        return
    if type == 'm':
        delta = delta * 60
    elif type == 'h':
        delta = delta * 3600

    if limit is None:
        say("Установлена автоматическая загрузка с интервалом %s секунд" % str(delta))
        limit = len(glob.glob(images_folder + "/*.*"))
    elif limit is not None:
        say("Установлена загрузка %s картинок с интервалом %s секунд" % (str(limit), str(delta)))
        limit = int(limit)

    while limit > 0:
        say("Осталось картиночек: %s" % str(limit))
        time.sleep(delta)
        list = glob.glob(images_folder + "/*.*")
        filename = random.choice(list)
        post_image(from_id, filename)
        limit -= 1



for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        from_id = event.obj['message']['from_id']
        if from_id == int(user_id):
            attachments = event.object.message['attachments']
            if not attachments:
                message = event.obj['message']['text']
                if re.match(r'end', message, re.IGNORECASE):
                    say("Бот отключён")
                    longpoll.end()
                elif re.match(r'test', message, re.IGNORECASE):
                    say("Привет! Я работаю " + where)
                elif re.match(r'ls', message, re.IGNORECASE):
                    list = glob.glob(images_folder + "/*.*")
                    say("В базе целых %s картиночек" % str(len(list)))
                elif re.match(r'post', message, re.IGNORECASE):
                    load()
                elif re.match(r'timer\s\d+[s|m|h]$', message, re.IGNORECASE):
                    (delta, type) = re.findall(r'timer\s(\d+)([s|m|h])', message)[0]
                    autoload(delta, type, limit=None)
                elif re.match(r'timer\s\d+[s|m|h]\s\d+', message, re.IGNORECASE):
                    (delta, type, limit) = re.findall(r'timer\s(\d+)([s|m|h])\s(\d+)', message)[0]
                    autoload(delta, type, limit)
                else:
                    say('Такой команды нет :С')
            else:
                # Saving image to /images
                print(bcolors.WARNING + "[1/6] Saving images from attachments..." + bcolors.ENDC)
                if not os.path.isdir(images_folder):
                    os.mkdir(images_folder)
                for i, attachment in enumerate(attachments):
                    max_size = 0
                    max_size_index = 0
                    for j, size in enumerate(attachment['photo']['sizes']):
                        if size['height'] > max_size:
                            max_size = size['height']
                            max_size_index = j

                    image_url = attachment['photo']['sizes'][max_size_index]['url']
                    ext = image_url.split('.')[-1]
                    filename = str(time.time()) + '-' + str(i)
                    new_file_name = "%s.%s" % (filename, ext.split('?')[0])
                    target = os.path.join(images_folder, new_file_name)
                    urllib.request.urlretrieve(image_url, target)
                    say("Картинка %s.%s загружена на сервер" % (filename, ext))
