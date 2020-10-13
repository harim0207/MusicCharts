from bs4 import BeautifulSoup
import requests
from datetime import datetime
import datetime as DT
import sqlite3
import re


# if you need to get rid of ssl verifications, use the following code:
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context


def getDate(soup):
    date1 = soup.find('button', class_='date-selector__button button--link').get_text().strip()
    date = datetime.strptime(date1, '%B %d, %Y').date()
    return date


def create(soup):
    date1 = soup.find('button', class_='date-selector__button button--link').get_text().strip()
    f = open(str(getDate(soup)) + ".txt", "w")
    f.write('Week of ' + date1 + '\n')
    for entry in soup.find_all('li', class_='chart-list__element display--flex'):
        rank = entry.find('span', class_='chart-element__rank__number').get_text()
        title = entry.find('span', class_='chart-element__information__song text--truncate color--primary').get_text()
        artist = entry.find('span',
                            class_='chart-element__information__artist text--truncate color--secondary').get_text()
        default = entry.find('span', class_='chart-element__information__delta__text text--default').get_text()
        last = entry.find('span', class_='chart-element__information__delta__text text--last').get_text()
        peak = entry.find('span', class_='chart-element__information__delta__text text--peak').get_text()
        weeks = entry.find('span', class_='chart-element__information__delta__text text--week').get_text()
        f.write(
            rank + ': ' + title + ' by ' + artist + ' | ' + default + ' | ' + last + ' | ' + peak + ' | ' + weeks + '\n')
    f.close()


def collect(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    create(soup)
    return getDate(soup)


def dbStuff(file):
    # below is the db creation therefore use once then do not use command again
    # c.execute('''CREATE TABLE hot100 (date text, title text, artist text, rank int, points int)''')
    f = open(file, 'r')
    date = f.name.replace('.txt', '')
    lines = f.readlines()
    for i in range(1, len(lines)):
        line = lines[i].partition('|')[0]
        temp = line.partition(':')
        rank = int(temp[0])
        title = temp[2].partition('by')[0].strip()
        artist = temp[2].partition('by')[2].strip()
        pts = 101 - rank
        c.execute("INSERT INTO hot100 VALUES (?,?,?,?,?)", (date, title, artist, rank, pts))
    f.close()
    # below is used for reading db
    '''c.execute("SELECT * FROM hot100")
    rows = c.fetchall()
    for row in rows:
        print(row)'''


if __name__ == '__main__':
    # Collecting all charts since 2000:
    '''
    dates = collect('https://www.billboard.com/charts/hot-100')
    while dates >= DT.date(2000, 1, 1):
        print(dates)
        link = 'https://www.billboard.com/charts/hot-100' + '/' + str(dates)
        collect(link)
        dates = dates - DT.timedelta(days=7)
    '''
    # Adding to DB:

    conn = sqlite3.connect('hot100.db')
    c = conn.cursor()
    dates = collect('https://www.billboard.com/charts/hot-100')
    while dates >= DT.date(2000, 1, 1):
        dbStuff(str(dates) + '.txt')
        dates = dates - DT.timedelta(days=7)
    conn.commit()
    c.close()

    # For updating current to future charts:

    conn = sqlite3.connect('hot100.db')
    c = conn.cursor()
    dates = collect('https://www.billboard.com/charts/hot-100')
    while dates >= DT.date(2020, 6, 6):  # change the (YYYY, M, D) to last updated chart
        link = 'https://www.billboard.com/charts/hot-100' + '/' + str(dates)
        collect(link)
        dbStuff(str(dates) + '.txt')
        dates = dates - DT.timedelta(days=7)
    conn.commit()
    c.close()

    # For creating yearly top 20 songs chart:

    conn = sqlite3.connect('hot100.db')
    c = conn.cursor()
    for i in range(2000, 2020):
        c.execute("SELECT DISTINCT title, artist FROM hot100 WHERE date LIKE ?", (str(i) + '%',))
        rows = c.fetchall()
        allTop = {}
        calc = list(rows)
        f = open('top' + str(i) + '.txt', 'w')
        for x, y in calc:
            pts = 0
            for j in c.execute("SELECT points FROM hot100 WHERE title=? AND artist=?", (x, y)):
                pts += j[0]
            allTop[x, y] = pts
        k = 1
        ss = sorted(allTop, key=allTop.get, reverse=True)
        while k < 21:
            f.write(str(k) + ': ' + ss[k-1][0] + ' by ' + ss[k-1][1] + '\n')
            k += 1
        f.close()
    c.close()
