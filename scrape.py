import urllib3
from lxml import etree
import csv

list_page = 'https://en.wikipedia.org/wiki/The_World%27s_Billionaires'

user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) ..'}
http = urllib3.PoolManager(10, headers=user_agent)

curr_page = http.request('GET', list_page)

htmlparser = etree.HTMLParser()

tree = etree.HTML(curr_page.data, htmlparser)

table = []

for x in range(2, 21):
    for y in range(2, 12):
        number = tree.xpath('//*[@id="mw-content-text"]/div/table[%s]/tr[%s]/td[1]/text()' % (str(x), str(y)))
        print(number)
        num = number[0].strip()

        name = tree.xpath('//*[@id="mw-content-text"]/div/table[%s]/tr[%s]/td[2]/span/span/span/a/text()' % (str(x), str(y)))
        if name == []:
            name = tree.xpath('//*[@id="mw-content-text"]/div/table[%s]/tr[%s]/td[2]/a/text()' % (str(x), str(y)))
            if len(name) == 2:
                person = name[0] + ' and ' + name[1]
            else:
                person = name[0]
        else:
            person = name[0]

        money = tree.xpath('//*[@id="mw-content-text"]/div/table[%s]/tr[%s]/td[3]/text()' % (str(x), str(y)))
        worth = money[0].strip()
        # print(worth)

        age = tree.xpath('//*[@id="mw-content-text"]/div/table[%s]/tr[%s]/td[4]/text()' % (str(x), str(y)))
        old = age[0]

        origin = tree.xpath('//*[@id="mw-content-text"]/div/table[%s]/tr[%s]/td[5]/a/text()' % (str(x), str(y)))
        locale = origin[0]

        source = tree.xpath('//*[@id="mw-content-text"]/div/table[%s]/tr[%s]/td[6]/a/text()' % (str(x), str(y)))
        if source == []:
            source = tree.xpath('//*[@id="mw-content-text"]/div/table[%s]/tr[%s]/td[2]/span/span/span/a/text()' % (str(x), str(y)))
        money_maker = source[0]

        year = tree.xpath('//*[@id="mw-content-text"]/div/h3[%s]/span/text()' % (str(x-1)))[0]
        table.append((year, num, person, worth, old, locale, money_maker))


with open('output.csv', 'w') as csvfile:
    w = csv.writer(csvfile)
    for x in table:
        print(list(x))
        w.writerow(list(x))
