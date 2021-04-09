import urllib.request
import xml.dom.minidom as minidom
import sqlite3
import datetime


def get_data(xml_url):
    try:
        web_file = urllib.request.urlopen(xml_url)
        return web_file.read()
    except:
        pass


def get_currencies_dictionary(xml_content):

    dom = minidom.parseString(xml_content)
    dom.normalize()

    elements = dom.getElementsByTagName("Valute")
    currency_dict = {}

    for node in elements:
        for child in node.childNodes:
            if child.nodeType == 1:
                if child.tagName == 'Value':
                    if child.firstChild.nodeType == 3:
                        value = float(child.firstChild.data.replace(',', '.'))
                if child.tagName == 'CharCode':
                    if child.firstChild.nodeType == 3:
                        char_code = child.firstChild.data
        currency_dict[char_code] = value
    return currency_dict

def print_dict(dict):
    for key in dict.keys():
        print(key, dict[key])

def write_current_rates_to_currencies_db(cur_dict, path):

    def count_records(table, cursor):
        sql = F'SELECT COUNT(*) as count FROM {table}'
        cursor.execute(sql)
        id = cursor.fetchone()[0]+1
        return id

    table = 'currencies'

    con = sqlite3.connect(path)
    cur = con.cursor()

    query = F'CREATE TABLE IF NOT EXISTS {table} (id, usd_rate, eur_rate, data)'
    cur.execute(query)
    con.commit()

    query = F'INSERT INTO {table} VALUES ({count_records(table, cur)},{cur_dict["USD"]},{cur_dict["EUR"]},"{datetime.datetime.now()}")'
    cur.execute(query)
    con.commit()
    con.close()

def read_currencies_rates_frrom_db(path):
    table = 'currencies'

    con = sqlite3.connect(path)
    cur = con.cursor()

    query = F'SELECT * FROM {table}'
    cur.execute(query)

    data_fetched = cur.fetchall()

    currencies_list = []
    for line in data_fetched:
       currencies_list.append(list(line))

    con.close()

    return currencies_list

def print_currencies_list(cur_list):
    for line in cur_list:
        print(line)

if __name__ == '__main__':
    url = 'http://www.cbr.ru/scripts/XML_daily.asp'
    db_path = './ currencies.db'
    currency_dict = get_currencies_dictionary(get_data(url))
    print_dict(currency_dict)
    write_current_rates_to_currencies_db(currency_dict, db_path)
    print_currencies_list(read_currencies_rates_frrom_db(db_path))