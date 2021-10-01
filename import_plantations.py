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

        
        MALE = 'male'
        FEMALE = 'female'
        
        plantation_name = data['ID_Plantation']
        plantation_code = data['Code']
        owner_first_name = data['Given Name']
        owner_last_name = data['Surname']
        owner_gender = FEMALE if data['Sex'] == 'Femme' else MALE
        total_trees = convert_to_float(data['Number of trees'])
        country = 'Benin'
        department = data['Departement']
        commune = data['Commune']
        arrondissement = data['Arrondissement']
        village = data['Village']
        current_area = data['2020 estimated surface (ha)']
        latitude = convert_to_float(data['GPS__Latitude'])
        longitude = convert_to_float(data['GPS__Longitude'])
        altitude = convert_to_float(data['GPS__Altitude'])
        

        new_plantation = models.Plantation(
            plantation_name = plantation_name,
            plantation_code = plantation_code,
            owner_first_name = owner_first_name,
            owner_last_name = owner_last_name,
            owner_gender = owner_gender,
            total_trees = total_trees,
            country = country,
            department = department,
            commune = commune,
            arrondissement = arrondissement,
            village = village,
            current_area = current_area,
            latitude = latitude,
            longitude = longitude,
            altitude = altitude,     
        )
        try:
            new_plantation.save()
        except:
            print("plantation data save error")

def import_dicts_to_yields(dict_list):

    for i, data in enumerate(dict_list):
        
        plantation_id = models.Plantation.objects.get(plantation_name = data['ID_Plantation'])
        product_id = data['ID_product']
        year = '2020'
        total_plants = convert_to_float(data['Number of trees'])
        total_yield_kg = convert_to_float(data['2020 total yield (kg)'])
        total_yield_per_ha_kg = convert_to_float(data['2020 yield per ha (kg)'])
        total_yield_per_tree_kg = convert_to_float(data['2020 yield per tree (kg)'])
        total_sick_trees = convert_to_float(data['Number of sick trees'])
        total_dead_trees = convert_to_float(data['Number of dead trees'])
        total_trees_out_of_prod = convert_to_float(data['Number of trees out of production'])
        
        new_yield = models.YieldHistory(
            plantation_id = plantation_id,
            product_id = product_id,
            year = year,
            total_plants = total_plants,
            total_yield_kg = total_yield_kg,
            total_yield_per_ha_kg = total_yield_per_ha_kg,
            total_yield_per_tree_kg = total_yield_per_tree_kg,
            total_sick_trees = total_sick_trees,
            total_dead_trees = total_dead_trees,
            total_trees_out_of_prod = total_trees_out_of_prod,  
        )
        try:
            new_yield.save()
        except Exception as e:
            print(e)


def clean_yield_data():
    yie = pd.read_excel("./Data/Yield data_YEARS_master.xlsx", skiprows = 1,engine='openpyxl',)
    colls = list(yie.columns)
    needed_colls = colls[:19] + colls[-9:]
    yield_data = yie[needed_colls]
    yield_data = yield_data.replace('nan', np.nan).fillna("")
    dict_list = convert_to_dict_list(yield_data)
    import_dicts_to_database(dict_list)
    import_dicts_to_yields(dict_list)

if __name__ == '__main__':
    # sys.path.append('/mnt/c/Users/Dami Olawoyin-Yussuf/Documents/Technoserve_Projects/NewRemSensing/Benin-Caju-Web-Dashboard')
    # os.environ['DJANGO_SETTINGS_MODULE'] = 'gettingstarted.settings'
    # django.setup()
    clean_yield_data()

