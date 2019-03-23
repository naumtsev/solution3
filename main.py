import requests
from requests import get, post, put
import sys
import os
import pygame

def size(response_my):
    resp = response_my['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['boundedBy']['Envelope']
    lx, ly = map(float, resp['lowerCorner'].split())
    rx, ry = map(float, resp['upperCorner'].split())
    w = abs(rx - lx)
    h = abs(ry - ly)
    return (w, h)

def scope(response_my):
    w, h = size(response_my)
    return w / 3 , h / 3

def position(response_my):
    return response_my['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']


def search(place):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode={}&format=json".format(place)
    response = get(geocoder_request)
    json_response = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    x, y = json_response.split()
    return (str(x) + ',' + str(y), (float(x), float(y)))



me = 'Новосондецкий бульвар, 5 , п. 4'




search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
address_ll = search(me)[0]
my_adress = search(me)[0]
search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params).json()
apteki = []
string = []
for i in range(min(10, len(response['features']))):
    data = response['features'][i]['properties']
    name = data['name'].replace(' ', '_')
    x, y = data['boundedBy'][0]
    buffer = data['CompanyMetaData']['Hours']['Availabilities'][0]
    print(data['CompanyMetaData']['Hours'])
    if 'TwentyFourHours' in buffer and buffer['TwentyFourHours']: # Зелёная
        apteki.append(str(x) + ',' + str(y) +  ',pm2gnl'+ str(i + 1))
    else:
        if 'text' not in buffer: # Серая
            apteki.append(str(x) + ',' + str(y) + ',pm2bll'+ str(i + 1))
        else: # Синяя
            apteki.append(str(x) + ',' + str(y) + ',pm2grl' + str(i + 1))
    string.append(str(x) + ',' + str(y))
    #print(data['CompanyMetaData'])


print('~'.join(apteki))
response = None
map_request = "http://static-maps.yandex.ru/1.x/?l=map&pt={}~{},home".format('~'.join(apteki), my_adress)
response = requests.get(map_request)

# Запишем полученное изображение в файл.
map_file = "map.png"
try:
    with open(map_file, "wb") as file:
        file.write(response.content)
except IOError as ex:
    print("Ошибка записи временного файла:", ex)
    sys.exit(2)

# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))
# Рисуем картинку, загружаемую из только что созданного файла.
screen.blit(pygame.image.load(map_file), (0, 0))

# Переключаем экран и ждем закрытия окна.
pygame.display.flip()
while pygame.event.wait().type != pygame.QUIT:
    pass
pygame.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)
