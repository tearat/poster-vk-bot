from vk_api import *
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import requests
import urllib.request
import os
from config import *

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

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        from_id = event.obj['message']['from_id']
        if from_id == int(user_id):
            attachments = event.object.message['attachments']
            if not attachments:
                vk_api_group.messages.send(user_id=from_id, random_id=get_random_id(), message="Привет! Я работаю!")
            else:
                # Saving image from url
                print(bcolors.WARNING + "[1/6] Saving image from url..." + bcolors.ENDC)
                image_url = attachments[0]['photo']['sizes'][6]['url']
                if not os.path.isdir('./images'):
                    os.mkdir('./images')
                urllib.request.urlretrieve(image_url, "images/local.jpg")

                # Getting upload server
                print(bcolors.WARNING + "[2/6] Getting upload server..." + bcolors.ENDC)
                upload_server = vk_api_user.photos.getWallUploadServer(group_id=group_id)
                upload_url = upload_server['upload_url']

                # Post image to server
                print(bcolors.WARNING + "[3/6] Post image to server..." + bcolors.ENDC)
                files = { 'photo': open('images/local.jpg', 'rb') }
                response = requests.post(upload_url, files=files )
                response_json = response.json()

                # Saving a photo
                print(bcolors.WARNING + "[4/6] Saving a photo..." + bcolors.ENDC)
                server = response_json['server']
                photo = response_json['photo']
                hash = response_json['hash']
                save_photo = vk_api_user.photos.saveWallPhoto(group_id=group_id, server=server, photo=photo, hash=hash)
                photo_id = save_photo[0]['id']
                owner_id = save_photo[0]['owner_id']

                # Posting on the wall
                print(bcolors.WARNING + "[5/6] Posting on the wall..." + bcolors.ENDC)
                message = event.obj['message']['text']
                attachment = f"photo{owner_id}_{photo_id}"
                wall_post = vk_api_user.wall.post(owner_id=f"-{group_id}", message=message, attachments=attachment)

                # Send message
                print(bcolors.WARNING + "[6/6] Send message..." + bcolors.ENDC)
                wall_post_id = wall_post['post_id']
                link = f"https://vk.com/public{group_id}?w=wall-{group_id}_{wall_post_id}"
                vk_api_group.messages.send(user_id=from_id, random_id=get_random_id(), message=f"Картиночка загружена!\n {link}")

                print()
                print(link)
                print(bcolors.OKGREEN + "Done!" + bcolors.ENDC)
                print()
