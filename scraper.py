#                              _                      _   _  __       _                         
#                             | |                    | | (_)/ _|     | |                        
#   _____   ___ __ ___   ___  | |__   ___  __ _ _   _| |_ _| |_ _   _| |  ___  ___  _   _ _ __  
#  / __\ \ / / '_ ` _ \ / _ \ | '_ \ / _ \/ _` | | | | __| |  _| | | | | / __|/ _ \| | | | '_ \ 
# | (__ \ V /| | | | | |  __/ | |_) |  __/ (_| | |_| | |_| | | | |_| | | \__ \ (_) | |_| | |_) |
#  \___| \_/ |_| |_| |_|\___| |_.__/ \___|\__,_|\__,_|\__|_|_|  \__,_|_| |___/\___/ \__,_| .__/ 
#                         ______                                     ______              | |    
#                        |______|                                   |______|             |_|    


# Author :
# +-+-+-+-+-+-+-+-+-+
# |I|A|m|T|e|r|r|o|r|
# +-+-+-+-+-+-+-+-+-+

# Licence :
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.

# Notes :
# Python script tested on Ubuntu Linux. It can run on Windows with minor adjustements.


########################################################################################################################

########################################################################################################################

# !/usr/bin/python
# -*- coding: utf-8 -*-

import os
import csv
import requests
from bs4 import BeautifulSoup
import re
from constants import *


# FUNCTIONS ------------------------------------------------------------------------------------------------------------

# cooking of a delicious soup with Beautiful Soup
def soup_cooking(url):
    request = requests.get(url)
    page = request.content
    a_delicious_soup = BeautifulSoup(page, 'html.parser')
    return a_delicious_soup


# creation of a dictionary with file names and theirs associated fake urls
def grab_fake_links(soup):
    dictionary_of_links = {}
    for link in soup.find_all('a', href=re.compile(REGEX)):
        fake_url = link.get('href')
        file_name = link.find_previous_siblings("a")[1].h2.contents
        print(file_name)
        print(fake_url)
        print("------")
        dictionary_of_links[str(file_name)] = [fake_url]
    print(dictionary_of_links)
    return dictionary_of_links


# discovering real download links from fake urls
def reveal_true_links(dictionary_of_links):
    for key in dictionary_of_links:
        value = dictionary_of_links.get(key)
        fake_url = value[0]
        r = requests.get(fake_url)
        if r.history:
            print("Request was redirected")
            for response in r.history:
                print(response.status_code, response.url)
            print("Final destination:")
            print(r.status_code, r.url)
            if "google" in r.url:
                value.append('None')
            else:
                value.append(r.url)
            print(dictionary_of_links)
        else:
            print("Request was not redirected")
        print(r.history)
    return dictionary_of_links


# generating a csv file with all scraping datas
def write_csv_file(dictionary_of_links):
    with open(CSV_FILE_NAME, 'a', newline='') as csvfile:  # 'a' parameter allows to update an existing csv file
        list_of_existing_keys_in_csv_file = []
        reader = csv.DictReader(open(CSV_FILE_NAME))
        for raw in reader:
            file_name = raw.get('file_name')
            list_of_existing_keys_in_csv_file.append(file_name)

        fieldnames = ['file_name', 'fake_link', 'true_link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if os.stat(CSV_FILE_NAME).st_size == 0:  # allows to not writing header if a header already exists in csv file
            writer.writeheader()
        for key in dictionary_of_links:
            if key not in list_of_existing_keys_in_csv_file:
                writer.writerow({'file_name': key, 'fake_link': dictionary_of_links.get(key)[0],
                                 'true_link': dictionary_of_links.get(key)[1]})


# SCRIPT ---------------------------------------------------------------------------------------------------------------

for url in URLS:
    soup = soup_cooking(url)
    dictionary_of_links = grab_fake_links(soup)
    dictionary_of_links_v2 = reveal_true_links(dictionary_of_links)
    write_csv_file(dictionary_of_links_v2)
