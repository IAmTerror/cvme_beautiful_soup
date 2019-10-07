import os
import csv
import requests
from bs4 import BeautifulSoup
import re

# VARIABLES ------------------------------------------------------------------------------------------------------------

# TODO : creer une première etape dans la création du CSV après le grab fake links mais avant le reveal true links...
# ... afin de ne pas interroger le serveur du site scrappé si le true link existe déjà
# + interroger au contraire le site scrappé SI la key existe ET que ce lien est None
# ... *OU* si aucune entrée n'existe
# TODO : remplacer l'url unique par une liste d'url a parser
# TODO : ne pas dévoiler les variables ni le regex ni le csv généré lors du commit

url = ""
regex = ""
csv_file_name = ""


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
    for link in soup.find_all('a', href=re.compile(regex)):
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
            if "google" in r.url == False:
                value.append(r.url)
            else:
                value.append('None')
            print(dictionary_of_links)
        else:
            print("Request was not redirected")
        print(r.history)
    return dictionary_of_links


# generating a csv file with all scraping datas
def write_csv_file(dictionary_of_links):
    with open(csv_file_name, 'a', newline='') as csvfile:  # 'a' parameter allows to update an existing csv file
        list_of_existing_keys_in_csv_file = []
        reader = csv.DictReader(open(csv_file_name))
        for raw in reader:
            file_name = raw.get('file_name')
            list_of_existing_keys_in_csv_file.append(file_name)

        fieldnames = ['file_name', 'fake_link', 'true_link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if os.stat(csv_file_name).st_size == 0:  # allows to not writing header if a header already exists in csv file
            writer.writeheader()
        for key in dictionary_of_links:
            if key not in list_of_existing_keys_in_csv_file:
                writer.writerow({'file_name': key, 'fake_link': dictionary_of_links.get(key)[0],
                                'true_link': dictionary_of_links.get(key)[1]})


# SCRIPT ---------------------------------------------------------------------------------------------------------------

soup = soup_cooking(url)

dictionary_of_links = grab_fake_links(soup)

dictionary_of_links_v2 = reveal_true_links(dictionary_of_links)

write_csv_file(dictionary_of_links_v2)
