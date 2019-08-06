from functions import *
from config import *

import vk_api
import requests


def write_msg(user_id, message):
    VK_BOT.method('messages.send', {'user_id': user_id, 'message': message})


def get_new_lp():
    return VK_BOT.method('messages.getLongPollServer', {'need_pts': 1, 'lp_version': 3})


VK_BOT = vk_api.VkApi(token=BOT_TOKEN)
VK_USER = vk_api.VkApi(token=USER_TOKEN)

lp_server = get_new_lp()

write_msg(MASTER_ID, 'Бот включен')

while True:
    try:
        response = requests.get(
            'https://{server}?act=a_check&key={key}&ts={ts}&wait=20ms&mode=2&version=2'.format(
                server=lp_server['server'],
                key=lp_server['key'],
                ts=lp_server['ts'])).json()
    except KeyError:
        lp_server = get_new_lp()
        response = requests.get(
            'https://{server}?act=a_check&key={key}&ts={ts}&wait=20ms&mode=2&version=2'.format(
                server=lp_server['server'],
                key=lp_server['key'],
                ts=lp_server['ts'])).json()

    updates = response['updates']
    if updates:
        if updates[0][0] == 4 and (
                updates[0][2] == 17 or updates[0][2] == 1):  # 4 - новое сообщение, 17 - сообщение мне, с телефона 1 -
            text = updates[0][5].lower()
            print('new massage')
            mess_id = updates[0][3]

            owner_id = textInterp(text, txtToDict('dic-1.txt'), txtToDict('groups.txt'))

            if 'привет' in text:  # далее всякие команды можно добавлять, чтобы управлять им из чата
                topics = ''
                for key in txtToDict('groups.txt').keys():
                    topics += ', ' + str(key)
                write_msg(mess_id, 'Привет, я Marvin. Я могу тебе прислать лучшие посты групп по темам:' + topics[
                                                                                                           1:] + '. Просто попроси, например, так: "скинь мне научный пост"')
            elif text == 'stop':
                write_msg(mess_id, 'Окей, выключаюсь')
                break
            elif owner_id == 'interp error':
                write_msg(mess_id, 'такого я не знаю(')
            else:
                postID = bestPost(owner_id, mess_id)
                if postID == 'thats all':
                    VK_BOT.method('messages.send',
                                  {'user_id': mess_id, 'message': 'по этому запросу пока все', 'attachment': wallpost})
                else:
                    wallpost = 'wall' + str(owner_id) + '_' + str(postID)
                    VK_BOT.method('messages.send', {'user_id': mess_id, 'message': 'вот', 'attachment': wallpost})
    lp_server['ts'] = response['ts']
write_msg(MASTER_ID, 'Бот выключен')  # это работает только, если выключение по команде stop
