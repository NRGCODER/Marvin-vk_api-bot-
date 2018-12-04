import vk_api
import json
import requests
import ast
import time
# comment just for test
master_id = 2299551 #этому пользователю бот сообщает свое состояние

def txtToDict(name): #открывает подготовленный txt и преобразует его в dict
	dic = {}
	file = open(name, 'r')
	while True:
		try:
			key, val = file.readline().split(':')
			dic[key] = val
		except ValueError:
			file.close()
			return dic
			break

def textInterp(text, InterpDic, GroupDic): #нужна для того, чтобы распознавать слова по корням (пример: скинь котейку. видит, находит "кот" в InterpDic и его значение находит в GroupsDic, где получает id нужной группы)
	text = text.lower()
	for key in InterpDic.keys():
		if key in text:
			groupKey = (InterpDic[key])[:-1] #почему-то разрыв строки выдает 
			return int(GroupDic[groupKey])
			break
	return 'interp error'

IDHistory = {} #история того, какие посты показаны кокретному пользователю

def Uchet(udic, n, m): #ведение любого учета, например постов показанных пользователю (lists in dicts)
	if n in udic.keys():
		udic[n].append(m)
	else:
		udic[n] = []
		udic[n].append(m)
	return udic

def bestPost(owner_id, user): #поиск лучшего поста в заданной группе за последние сутки. сохраняет id поста в IDHistory для данного пользователя, чтобы потом не скидывать тот же пост при таком же запросе.
	posts = vk.method('wall.get', {'owner_id': owner_id, 'count': 40, 'filter': 'all'})
	likesIds = {}
	for post in posts['items']:
		ID = post['id']
		COUNT = post['likes']['count']
		try:
			if (time.time() - post['date']) < 86400 and ID not in IDHistory[user]:
				likesIds[COUNT] = ID
		except KeyError:
			likesIds[COUNT] = ID
	if len(likesIds) == 0:
		return 'thats all'
	else:
		best = likesIds[max(likesIds.keys())]
		Uchet(IDHistory, user, best)
		return best

def write_msg(user_id, s):
    vkg.method('messages.send', {'user_id':user_id,'message':s})


vk_auth = txtToDict('auth.txt') #сделал чтобы потом, в демонстарациях для учеником, не писать в открытую свои данные
vk = vk_api.VkApi(login = vk_auth['login'][:-1], password = vk_auth['pass'][:-1]) #почему-то из словаря у меня появился пробел в конце. пока не разобрался
vk.auth()

vkg = vk_api.VkApi(token = vk_auth['token']) #Авторизоваться как сообщество
LPServer = vkg.method('messages.getLongPollServer', {'need_pts' : 1, 'lp_version' : 3}) #проверка последних сообщений (замена message.get)
write_msg(master_id, 'Бот включен')
while True:
	response = requests.get('https://{server}?act=a_check&key={key}&ts={ts}&wait=20ms&mode=2&version=2'.format(server = LPServer['server'], key = LPServer['key'], ts = LPServer['ts'])).json()
	updates = response['updates']
	if updates:
		if updates[0][0] == 4 and (updates[0][2] == 17 or updates[0][2] == 1): #4 - новое сообщение, 17 - сообщение мне, с телефона 1 - 
			text = updates[0][5].lower()
			print('new massage')
			mess_id = updates[0][3]
			
			owner_id = textInterp(text, txtToDict('dic-1.txt'), txtToDict('groups.txt'))
			

			if 'привет' in text: #далее всякие команды можно добавлять, чтобы управлять им из чата
				topics = ''
				for key in txtToDict('groups.txt').keys():
					topics += ', ' + str(key)
				write_msg(mess_id, 'Привет, я Marvin. Я могу тебе прислать лучшие посты групп по темам:' + topics[1:] + '. Просто попроси, например, так: "скинь мне научный пост"')
			elif text == 'stop':
				write_msg(mess_id, 'Окей, выключаюсь')
				break
			elif owner_id == 'interp error':
				write_msg(mess_id, 'такого я не знаю(')
			else:
				postID = bestPost(owner_id, mess_id)
				if postID == 'thats all':
					vkg.method('messages.send', {'user_id':mess_id,'message': 'по этому запросу пока все', 'attachment': wallpost})
				else:
					wallpost = 'wall' + str(owner_id) + '_' + str(postID)
					vkg.method('messages.send', {'user_id':mess_id,'message': 'вот', 'attachment': wallpost})
	LPServer['ts'] = response['ts']
write_msg(master_id, 'Бот выключен') #это работает только, если выключение по команде stop