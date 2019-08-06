import csv
import time

start = time.time()
def csv_reader(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as file_obj:
        reader = csv.reader(file_obj)
        dic = {}
        for row in reader:
            key, val = row[0].split(';')
            dic[key] = val.lower()
        return dic

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