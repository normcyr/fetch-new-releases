#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
import re
import json

def get_releases_week(base_url):
    homepage = requests.get(base_url).text
    home_soup = BeautifulSoup(homepage, 'html.parser')
    menu = home_soup.find('ul', {'id': 'menu2'})
    week = menu.find_all('li')[2].find('a', href=True).attrs['href']

    return(week)

def get_releases_page(base_url, week, payload):
    full_url = base_url + week
    releases_page = requests.get(full_url, params = payload).text

    return(releases_page)

def make_soup(page):
    soup = BeautifulSoup(page, 'html.parser')
    results_disp = soup.find(text = re.compile('Results Displayed: 1 -'))
    nb_results = re.findall(r'\d+', results_disp)

    return(nb_results, soup)

def retreive_data(soup, i):
    data = soup.find('tr', {'id': 'BaseList_TR_ResultLine_' + str(i)})
    td_class = data.find('td', {'class': 'udf_format'})

    if td_class.text == 'Vinyl':
        return(data)

def parse_data(data):
    artist = data.find('td', {'class': 'UDF_product'}).text
    title = data.find('td', {'class': 'UDF_title'}).text
    label = data.find('td', {'class': 'udf_label'}).text
    cat_no = data.find('td', {'class': 'udf_cat'}).text
    price = float(data.find('span', {'class': 'ItemSearchResults_Price'}).text[1:-3])
    record = {'artist': artist, 'title': title, 'label': label, 'cat_no': cat_no, 'price': price}

    return(record)

def save_data(new_releases, json_filename):
    with open(json_filename, 'w') as f:
        f.write(json.dumps(new_releases))

def main():

    base_url = 'http://www.rpmdistribution.ca'
    payload = {'DropDownPageSize': '1000', 'forcePrice': 'True'}

    week = get_releases_week(base_url)

    new_releases = []
    date_release = re.findall('\w+', week)[1]
    json_filename = 'new_releases' + date_release + '.json'



    releases_page = get_releases_page(base_url, week, payload)
    nb_results, soup = make_soup(releases_page)

    for i in range(int(nb_results[0]) - 1, int(nb_results[1])):
        data = retreive_data(soup, i)
        if data:
            record = parse_data(data)
            new_releases.append(record)

    save_data(new_releases, json_filename)

if __name__ == '__main__':
    main()
