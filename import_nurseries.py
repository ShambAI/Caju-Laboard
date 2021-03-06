import pandas as pd
import numpy as np
import re
import os, sys
import django

sys.path.append('/mnt/c/Users/Dami Olawoyin-Yussuf/Documents/Technoserve_Projects/NewRemSensing/Benin-Caju-Web-Dashboard')
os.environ['DJANGO_SETTINGS_MODULE'] = 'gettingstarted.settings'
django.setup()

from authentication import models

def nursery_row_converter(row, listy):
    #convert pandas row to a dictionary
    #requires a list of columns and a row as a tuple
    count = 1
    pictionary = {}
    pictionary['Index'] = row[0]
    for item in listy:
        if item == 'Provenance':
            word = re.sub('N°','',row[count])
            pictionary[item] = re.sub('[\W\_]','',word)
        else:
            pictionary[item] = row[count]
        count += 1
    return pictionary

def convert_to_dict_list(table):
    dict_list = []
    listy = table.columns
    for i, row in enumerate(table.itertuples()):
        dict_list.append(nursery_row_converter(row, listy))

    return dict_list

def convert_to_float(data):
    if data == "" or data == 'No data':
        return float(0)
    else:
        return float(data)

def import_dicts_to_database(dict_list):

    for i, data in enumerate(dict_list):

        if data['owner_first_name'] == "":
            first_name = str(i)
        else:
            first_name = data['owner_first_name']
        nursery_name = first_name + "'s nursery"
        owner_first_name = first_name
        owner_last_name = data['owner_last_name']
        nursery_address = data['Provenance']
        country = "Benin"
        commune = data['Commune']
        current_area = convert_to_float(data['Area (ha)'])
        latitude = convert_to_float(data['Latitude'])
        longitude = convert_to_float(data['Longitude'])
        altitude = convert_to_float(data['Altitude'])
        partner = data['Partenaire']
        number_of_plants = int(convert_to_float(data['Numebr of Plants']))

        new_nursery = models.Nursery(
            nursery_name = nursery_name,
            owner_first_name = owner_first_name,
            owner_last_name = owner_last_name,
            nursery_address = nursery_address,
            country = country,
            commune = commune,
            current_area = current_area,
            latitude = latitude,
            longitude = longitude,
            altitude = altitude,
            partner = partner,
            number_of_plants = number_of_plants,     
        )
        try:
            new_nursery.save()
        except:
            print("nursery data save error")

def clean_nursery_data():
    nur = pd.read_excel("./Data/Nurseries.xlsx",engine='openpyxl',)
    nur = nur.replace('nan', np.nan).fillna("")
    s = nur['Owner'].apply(lambda x: x.split(' '))
    nur['owner_last_name'] = s.apply(lambda x: x[0])
    nur['owner_first_name'] = s.apply(lambda x: " ".join(x[1:]) if len(x) > 0 else "" )
    import_dicts_to_database(convert_to_dict_list(nur))

if __name__ == '__main__':
    # sys.path.append('/mnt/c/Users/Dami Olawoyin-Yussuf/Documents/Technoserve_Projects/NewRemSensing/Benin-Caju-Web-Dashboard')
    # os.environ['DJANGO_SETTINGS_MODULE'] = 'gettingstarted.settings'
    # django.setup()
    clean_nursery_data()

