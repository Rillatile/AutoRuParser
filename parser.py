import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv

HEADERS = {
    'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        + 'AppleWebKit/537.36 (KHTML, like Gecko) '
        + 'Chrome/81.0.4044.138 Safari/537.36',
    'accept': '*/*'
}


def get_html(url, params=None):
    req = requests.get(url, headers=HEADERS, params=params)
    req.encoding = 'utf-8'

    return req


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    buttons = soup.find('span', class_='ListingPagination-module__pages')
    count = 1

    if buttons:
        last = buttons.find_all('a', class_='Button')[-1]
        count = int(last.find('span', class_='Button__text').get_text())

    return count


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='ListingItem-module__main')
    cars = []

    for item in items:
        cars.append({
            'title': item.find('h3', class_='ListingItem-module__title').get_text(),
            'link': item.find('a', class_='ListingItemTitle-module__link').get('href'),
            'price': item.find('div', class_='ListingItemPrice-module__content').get_text().replace('\xa0', ' '),
            'location': item.find('span', class_='MetroListPlace__regionName').get_text()
        })

    return cars


def save(data):
    with open(f"cars {data['datetime']}.csv", 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')

        for car in data['cars']:
            writer.writerow([car['title'], car['price'], car['location'], car['link']])


def parse():
    print('Вас приветствует парсер объявлений о продаже поддержанных автомобилей на сайте auto.ru!')
    url = input('Пожалуйста, укажите ссылку на стартовую страницу с объявлениями нужной марки: ')
    max_pages_count = int(input('Пожалуйста, укажите максимальное число страниц для парсинга: '))
    html = get_html(url)

    if html.status_code == 200:
        count = get_pages_count(html.text)

        if count > max_pages_count:
            count = max_pages_count

        data = {
            'datetime': datetime.now().strftime('%d.%m.%Y %Hh %Mm %Ss'),
            'cars': []
        }

        for page in range(1, count + 1):
            print(f'Парсинг страницы {page} из {count}.')
            current_html = get_html(url, params={
                'page': page
            })
            data['cars'].extend(get_content(current_html.text))

        print(f"Парсинг завершён. Получено автомобилей: {len(data['cars'])}.")
        print('Сохранение в файл.')
        try:
            save(data)
        except:
            print('Не удалось сохранить результат в файл.')
        else:
            print('Готово.')
    else:
        print(f'Ошибка запроса! Код статуса: {html.status_code}.')


if __name__ == '__main__':
    parse()

