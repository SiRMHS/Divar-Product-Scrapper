import os
import time
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import progressbar

def save_urls(scroll_times=100):
    with open(url_file, 'w', newline='', encoding='utf-8') as write_obj:
        write_obj.writelines('')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(search_url)
    time.sleep(2)  
    scroll_pause_time = 7  
    screen_height = driver.execute_script("return window.screen.height;")
    
    link_batch = []
    link_counter = 0

    bar = progressbar.ProgressBar(maxval=scroll_times, \
        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

    print('Finding links progress:')
    bar.start()

    for i in range(scroll_times):
        bar.update(i + 1)

        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
        time.sleep(scroll_pause_time)  

        soup = BeautifulSoup(driver.page_source, "html.parser")

        for a_tag in soup.find_all("a", class_="kt-post-card__action"):
            if a_tag is not None and a_tag.has_attr('href'):
                url = urljoin(home_url, a_tag['href'])  
                link_batch.append(url)
                link_counter += 1

                print(f"Link {link_counter}")
            
            if link_counter >= 20:
                print("Saving 20 links to file.")
                with open(url_file, 'a+', newline='', encoding='utf-8') as write_obj:
                    write_obj.writelines([link + '\n' for link in link_batch])

                link_batch = []
                link_counter = 0

    if link_batch:
        print(f"Saving {len(link_batch)} remaining links to file.")
        with open(url_file, 'a+', newline='', encoding='utf-8') as write_obj:
            write_obj.writelines([link + '\n' for link in link_batch])

    bar.finish()

def scrap_links():
    with open(url_file, 'r', newline='', encoding='utf-8') as read_obj:
        links = read_obj.readlines()

    print('------------------------------')
    print('Total link counts:', len(links))

    links = list(set(links))
    print('Unique link counts:', len(links))
    print('------------------------------')

    with open(data_file, mode='w', newline='', encoding='utf-8') as csv_file:
        handle = csv.writer(csv_file)
        handle.writerow(['id', 'name', 'neighborhood', 'area', 'year', 'room', 'deposit', 'rent', 'floor', 
                         'elevator', 'parking', 'warehouse', 'description', 'images', 'link'])

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    link_batch = []
    index_counter = 0

    bar1 = progressbar.ProgressBar(maxval=len(links), \
        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    
    print('Scraping links progress:')
    bar1.start()

    for each_link in links:
        bar1.update(index_counter + 1)
        index_counter += 1 

        name = neighborhood = area = year = room = deposit = rent = floor = ''
        elevator = parking = warehouse = description = ''
        images = 'بدون تصویر'

        each_link = each_link.strip()

        driver.get(each_link)
        time.sleep(5) 

        soup = BeautifulSoup(driver.page_source, "html.parser")

        name_tag = soup.find('h1', class_='kt-page-title__title')
        name = name_tag.get_text() if name_tag else 'ناموجود'

        neighborhood_tag = soup.find('div', class_='kt-page-title__subtitle')
        neighborhood = neighborhood_tag.get_text().split('،')[1] if neighborhood_tag else 'ناموجود'

        data_rows = soup.find_all('tr', class_='kt-group-row__data-row')

        if len(data_rows) == 3:
            data_row_1 = data_rows[0]
            tds = data_row_1.find_all('td')
            area = tds[0].get_text() if len(tds) > 0 else 'ناموجود'
            year = tds[1].get_text() if len(tds) > 1 else 'ناموجود'
            room = tds[2].get_text() if len(tds) > 2 else 'ناموجود'

            data_row_2 = data_rows[1]
            tds = data_row_2.find_all('td')
            deposit = tds[0].get_text() if len(tds) > 0 else 'ناموجود'
            rent = tds[1].get_text() if len(tds) > 1 else 'ناموجود'

            data_row_3 = data_rows[2]
            tds = data_row_3.find_all('td')
            elevator = f"{tds[0].get_text()} دارد" if len(tds) > 0 else 'ناموجود'
            parking = f"{tds[1].get_text()} دارد" if len(tds) > 0 else 'ناموجود'
            warehouse = f"{tds[2].get_text()} دارد" if len(tds) > 0 else 'ناموجود'

            floor_tag = soup.find('p', class_='kt-unexpandable-row__value')
            floor = floor_tag.get_text() if floor_tag else 'ناموجود'

        elif len(data_rows) == 2:
            data_row_1 = data_rows[0]
            tds = data_row_1.find_all('td')
            area = tds[0].get_text() if len(tds) > 0 else 'ناموجود'
            year = tds[1].get_text() if len(tds) > 1 else 'ناموجود'
            room = tds[2].get_text() if len(tds) > 2 else 'ناموجود'
            flor_box = soup.find_all('div', class_='kt-unexpandable-row__value-box')[3]
            if flor_box:
                floor_tag = flor_box.find('p', class_='kt-unexpandable-row__value')
                floor = floor_tag.get_text() if floor_tag else 'ناموجود'
            else:
                floor = 'ناموجود'

            deposit_box = soup.find('div', class_='kt-unexpandable-row__value-box')
            if deposit_box:
                deposit_tag = deposit_box.find('p', class_='kt-unexpandable-row__value')
                deposit = deposit_tag.get_text() if deposit_tag else 'ناموجود'
            else:
                deposit = 'ناموجود'

            rent_box = soup.find_all('div', class_='kt-unexpandable-row__value-box')[1]
            if rent_box:
                rent_tag = rent_box.find('p', class_='kt-unexpandable-row__value')
                rent = rent_tag.get_text() if rent_tag else 'ناموجود'
            else:
                rent = 'ناموجود'

            data_row_2 = data_rows[1]
            tds = data_row_2.find_all('td')
            elevator = f"{tds[0].get_text()} دارد" if len(tds) > 0 else 'ناموجود'
            parking = f"{tds[1].get_text()} دارد" if len(tds) > 0 else 'ناموجود'
            warehouse = f"{tds[2].get_text()} دارد" if len(tds) > 0 else 'ناموجود'
        else:
            area = year = room = deposit = rent = elevator = parking = warehouse = 'ناموجود'


        description_tag = soup.find('p', class_='kt-description-row__text--primary')
        description = description_tag.get_text() if description_tag else 'ناموجود'

        image_tags = soup.find_all('img', class_='kt-image-block__image')
        image_sources = [img['src'] for img in image_tags if 'src' in img.attrs]

        images = ', '.join(image_sources) if image_sources else 'بدون تصویر'

        new_row = [index_counter, name, neighborhood, area, year, room, deposit, rent, floor, 
                   elevator, parking, warehouse, description, images, each_link]
        
        link_batch.append(new_row)

        if len(link_batch) >= 5:
            print(f"Saving {len(link_batch)} links to file.")
            with open(data_file, 'a+', newline='', encoding='utf-8') as write_obj:
                csv_writer = csv.writer(write_obj)
                csv_writer.writerows(link_batch)
            link_batch = [] 

    if link_batch:
        print(f"Saving {len(link_batch)} remaining links to file.")
        with open(data_file, 'a+', newline='', encoding='utf-8') as write_obj:
            csv_writer = csv.writer(write_obj)
            csv_writer.writerows(link_batch)

    bar1.finish()

def save_to_excel(data_file, output_excel_file):
    data = pd.read_csv(data_file, encoding='utf-8')

    data.to_excel(output_excel_file, index=False, engine='openpyxl')

    print(f"Data saved to {output_excel_file}")

if __name__ == "__main__":
    city = int(input("Shahr ra Vared Konid (exmp = tehran) : "))
    if not os.path.exists('Urls'):
        os.makedirs('Urls')
    if not os.path.exists('Data'):
        os.makedirs('Data')
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    url_file = './Urls/' + 'AdsUrls_' + city + '_'  +  timestamp + '.txt'
    data_file = './Data/' + 'Data_' +  city + '_' + timestamp  + '.csv'
    output_excel_file = './Data/' + 'Data_' +  city + '_' + timestamp + '.xlsx'
    home_url = 'https://divar.ir'
    search_url = "https://divar.ir/s/" + city  + "/rent-apartment"

    numbs = int(input("Tedad Page ra Vared Konid (1page = 20Case) : "))
    save_urls(numbs)
    scrap_links()
    
    save_to_excel(data_file, output_excel_file)
