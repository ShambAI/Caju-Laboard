# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import numpy as np
import os
import geojson
import folium
from django import template
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from branca.element import MacroElement
from jinja2 import Template
from shapely.geometry import shape
from shapely import geometry
from area import area
import locale
from math import log10, floor

# generic base view
from django.views.generic import TemplateView

# folium
from folium import plugins
import pandas as pd
from folium.plugins import MarkerCluster
import ee

service_account = 'cajulab@benin-cajulab-web-application.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'privatekey.json')
ee.Initialize(credentials)
locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
heroku = True

alldept = ee.Image('users/ashamba/allDepartments_v0')
dtstats_df = pd.read_excel("./new_data/dtstats_df.xlsx", engine='openpyxl')
dtstats_df1 = pd.read_excel("./new_data/dtstats_df1.xlsx", engine='openpyxl')
alteia_df = pd.read_excel("./new_data/alteia_df.xlsx", engine='openpyxl')
ben_yield = pd.read_excel("./new_data/ben_yield.xlsx", engine='openpyxl')
ben_nursery = pd.read_excel("./new_data/ben_nursery.xlsx", engine='openpyxl')
ben_yield_GEO = pd.read_excel("./new_data/ben_yield_GEO.xlsx", engine='openpyxl')
drone_df = pd.read_excel("./plant_drone_data/drone_dataframe_reviewed.xlsx", engine='openpyxl')
drone_directory = "./plant_drone_data/Images"

with open("Data/CajuLab_Plantations.geojson", errors="ignore") as f:
        alteia_json = geojson.load(f)

with open("ben_adm0.json", errors="ignore") as f:
    benin_adm0_json = geojson.load(f)

with open("ben_adm1.json", errors="ignore") as f:
    benin_adm1_json = geojson.load(f)

with open("ben_adm2.json", errors="ignore") as f:
    benin_adm2_json = geojson.load(f)


    
list_global = []
for item in list(ben_yield_GEO['Code']):
    if item in list(ben_yield['Code']):
        list_global.append(item)
        
GEO_id_tuple = []
for unique_id in list_global:
    GEO_id_tuple.append((list(ben_yield_GEO[ben_yield_GEO['Code']==unique_id]['Local shape ID or coordinates'])[0], unique_id))
    
special_id_tuple = []
special_id = []
for (id_u, code_u) in GEO_id_tuple:
    if id_u in list(alteia_df['Code']):
        special_id_tuple.append((id_u, code_u))
        special_id.append(id_u)


basemaps = {
            'Google Maps': folium.TileLayer(
                tiles = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                attr = 'Google',
                name = 'Maps',
                max_zoom =18,
                overlay = True,
                control = False
            ),
            'Google Satellite': folium.TileLayer(
                tiles = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                attr = 'Google',
                name = 'Satellite View',
                max_zoom = 18,
                overlay = True,
                show=False,
                control = True
            ),
            'Google Terrain': folium.TileLayer(
                tiles = 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
                attr = 'Google',
                name = 'Google Terrain',
                overlay = True,
                control = True
            ),
            'Google Satellite Hybrid': folium.TileLayer(
                tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                attr = 'Google',
                name = 'Google Satellite',
                overlay = True,
                control = True
            ),
            'Esri Satellite': folium.TileLayer(
                tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr = 'Esri',
                name = 'Esri Satellite',
                overlay = True,
                control = True
            )
        }



feature_group_drone = folium.map.FeatureGroup(name='TNS Drone Images')
for root, subdirectories, files in os.walk(drone_directory):
    for file in files:
        image_path = os.path.join(root, file)
        if not os.path.isfile(image_path):
            continue
        else:
            drone_code = file.split('.')[0]
            upper_lat = list(drone_df[drone_df['plantation_id']==drone_code]['upper_lat'])[0]
            upper_lon = list(drone_df[drone_df['plantation_id']==drone_code]['upper_lon'])[0]
            lower_lat = list(drone_df[drone_df['plantation_id']==drone_code]['lower_lat'])[0]
            lower_lon = list(drone_df[drone_df['plantation_id']==drone_code]['lower_lon'])[0]
            
            img = folium.raster_layers.ImageOverlay(
                name="Dronez",
                image=image_path,
                bounds=[[upper_lat, upper_lon], [lower_lat, lower_lon]],
                opacity=1.0,
                interactive=True,
                cross_origin=False,
                zindex=1,
            )
            feature_group_drone.add_child(img)

class my_home():
    # Define a method for displaying Earth Engine image tiles on a folium map.

    def __init__(self):
        self.figure = folium.Figure()
        self.m = ""
        self.value2 = ""
        self.name = ""

    def get_context_data(self, **kwargs):

                # figure = folium.Figure()

        m = folium.Map(
            location=[9.0, 2.4],
            zoom_start=8,
            tiles = None
        )

        m.add_child(basemaps['Google Maps'])
        m.add_child(basemaps['Google Satellite'])

        plugins.Fullscreen(position='topright', title='Full Screen', title_cancel='Exit Full Screen', force_separate_button=False).add_to(m)

        def highlight_function(feature):
            return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}

        marker_cluster = MarkerCluster(name="Nursery Information").add_to(m)
        for i in range(len(ben_nursery)):
            folium.Marker(location= [ben_nursery[i:i+1]['Latitude'].values[0], ben_nursery[i:i+1]['Longitude'].values[0]],
                        rise_on_hover=True,
                        rise_offset = 250,
                        icon = folium.Icon(color="red", icon="leaf"),
                        popup='''
                        <div style="border: 3px solid #808080">
                        <h4 style="font-family: 'Trebuchet MS', sans-serif">Commune Name: <b>{}</b></h4>
                        <h5 style="font-family: 'Trebuchet MS', sans-serif">Nursery Owner: <i>{}</i></h5>
                        <h5 style="font-family: 'Trebuchet MS', sans-serif">Nursery Area (ha): <b>{}</b></h5>
                        <h5 style="font-family: 'Trebuchet MS', sans-serif">Number of Plants: <b>{}</b></h5>
                        <a href="https://www.technoserve.org/our-work/agriculture/cashew/?_ga=2.159985149.1109250972.1626437600-1387218312.1616379774"target="_blank">click link to website</a>
                        <img src="https://gumlet.assettype.com/deshdoot/import/2019/12/tripXOXO-e1558439144643.jpg?w=1200&h=750&auto=format%2Ccompress&fit=max" width="200" height="70">
                        </div>'''.format(ben_nursery[i:i+1].Commune.values[0], ben_nursery[i:i+1].Owner.values[0], ben_nursery[i:i+1]['Area (ha)'].values[0], ben_nursery[i:i+1]['Numebr of Plants'].values[0])).add_to(marker_cluster)

        def add_ee_layer(self, ee_image_object, vis_params, name):
            map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
            folium.raster_layers.TileLayer(
                tiles=map_id_dict['tile_fetcher'].url_format,
                attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
                name=name,
                overlay=True,
                control=True
            ).add_to(self)

        folium.Map.add_ee_layer = add_ee_layer
        folium.map.FeatureGroup.add_ee_layer = add_ee_layer

        zones = alldept.eq(1)
        zones = zones.updateMask(zones.neq(0));

        m.add_ee_layer(zones, {'palette': "red"}, 'Satellite Prediction')

        layer3 = folium.FeatureGroup(name='No Boundary', show=False, overlay = False)
        layer3.add_to(m)

        layer0 = folium.FeatureGroup(name='Benin Republic', show=False, overlay = False)
        temp_geojson0  = folium.GeoJson(data=benin_adm0_json,
            name='Benin-Adm0 Department',
            highlight_function = highlight_function)


        for feature in temp_geojson0.data['features']:
            # GEOJSON layer consisting of a single feature

            y0 = dtstats_df1[dtstats_df1['Country']=='Benin']['Districts']
            # getting values against each value of y

            pred_ben_data = []
            pred_ground_ben_data = [['Departments', 'Satellite Prediction', 'Ground Data Estimate']]
            for y in y0:
                x_new = round(sum(ben_yield[ben_yield['Departement']==y]['2020 estimated surface (ha)'].dropna()),2)
                x = round(sum(dtstats_df[dtstats_df['Districts']==y].Cashew_Yield)/10000,2)
                pred_ben_data.append([y, x])
                pred_ground_ben_data.append([y, x, x_new])

            temp_layer0 = folium.GeoJson(feature,  zoom_on_click = True, highlight_function = highlight_function)

            name = 'Benin Republic'
            surface_area = int(round(sum(ben_yield['2020 estimated surface (ha)'].dropna()),2))
            total_yield = int(round(sum(ben_yield['2020 total yield (kg)'].dropna()),2))
            yield_ha = int(round(np.mean(ben_yield['2020 yield per ha (kg)'].dropna()),2))
            # yield_tree = int(round(np.mean(ben_yield['2020 yield per tree (kg)'].dropna()),2))
            num_tree = int(sum(ben_yield['Number of trees'].dropna()))
            sick_tree = int(sum(ben_yield['Number of sick trees'].dropna()))
            out_prod_tree = int(sum(ben_yield['Number of trees out of production'].dropna()))
            dead_tree = int(sum(ben_yield['Number of dead trees'].dropna()))
            tree_ha_pred = int(round(sum(dtstats_df[dtstats_df['Country']=='Benin'].Cashew_Yield)/10000,2))
            yield_pred = 390*tree_ha_pred
            region_size = area(feature['geometry'])/10000
            active_trees = num_tree- sick_tree- out_prod_tree- dead_tree
            
            r_surface_area = round(surface_area, 1-int(floor(log10(abs(surface_area))))) if surface_area < 90000 else round(surface_area, 2-int(floor(log10(abs(surface_area)))))
            r_total_yield = round(total_yield, 1-int(floor(log10(abs(total_yield))))) if total_yield < 90000 else round(total_yield, 2-int(floor(log10(abs(total_yield)))))
            r_yield_ha = round(yield_ha, 1-int(floor(log10(abs(yield_ha))))) if yield_ha < 90000 else round(yield_ha, 2-int(floor(log10(abs(yield_ha)))))
            # r_yield_tree = round(yield_tree, 1-int(floor(log10(abs(yield_tree))))) if yield_tree < 90000 else round(yield_tree, 2-int(floor(log10(abs(yield_tree)))))
            r_tree_ha_pred = round(tree_ha_pred, 1-int(floor(log10(abs(tree_ha_pred))))) if tree_ha_pred < 90000 else round(tree_ha_pred, 2-int(floor(log10(abs(tree_ha_pred)))))
            r_yield_pred = round(yield_pred, 1-int(floor(log10(abs(yield_pred))))) if yield_pred < 90000 else round(yield_pred, 2-int(floor(log10(abs(yield_pred)))))
            r_num_tree = round(num_tree, 1-int(floor(log10(abs(num_tree))))) if num_tree < 90000 else round(num_tree, 2-int(floor(log10(abs(num_tree)))))
            r_region_size = round(region_size, 1-int(floor(log10(abs(region_size))))) if region_size < 90000 else round(region_size, 2-int(floor(log10(abs(region_size)))))
            
            r_yield_tree = round(r_total_yield/active_trees)

            html4 = '''
                    <html>
                        <head>
                            <style>
                            table {{
                            border-collapse: collapse;
                            width: 100%;
                            }}


                            table th {{
                            background-color: #004b55;
                            text-align: left;
                            color: #FFF;
                            padding: 4px 30px 4px 8px;
                            }}


                            table td {{
                            border: 1px solid #e3e3e3;
                            padding: 4px 8px;
                            }}


                            table tr:nth-child(odd) td{{
                            background-color: #e7edf0;
                            }}
                            </style>
                            <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                            <script type="text/javascript">
                            // Load Charts and the corechart and barchart packages.
                            google.charts.load('current', {{'packages':['corechart']}});
                            google.charts.load('current', {{'packages':['bar']}});

                            // Draw the pie chart and bar chart when Charts is loaded.
                            google.charts.setOnLoadCallback(drawChart);

                            function drawChart() {{

                                var pie_data = new google.visualization.DataTable();
                                pie_data.addColumn('string', 'Commune');
                                pie_data.addColumn('number', 'Cashew Tree Cover (ha)');
                                pie_data.addRows({1});

                                var piechart_options = {{title:'Departments Cashew Tree Cover Statistics In {0}',
                                                            is3D: true,
                                                        }};
                                var piechart = new google.visualization.PieChart(document.getElementById('piechart_div'));
                                piechart.draw(pie_data, piechart_options);

                                


                                var data_donut = google.visualization.arrayToDataTable([
                                ['Tree Type', 'Number of Trees'],
                                ['Active Trees',      {14}],
                                ['Sick Trees',      {11}],
                                ['Dead Trees',     {13}],
                                ['Out of Production Trees',      {12}],
                                ]);

                                var options_donut = {{
                               
                                title: 'Cashew Trees Status in {0}',
                                pieHole: 0.5,
                                colors: ['007f00', '#02a8b1', '9e1a1a', '#242526'],
                                }};

                                var chart_donut = new google.visualization.PieChart(document.getElementById('donutchart'));
                                chart_donut.draw(data_donut, options_donut);

                                }};
                            </script>
                        </head>
                        <body>
                            <h2>{0}</h2>
                            <h4>{0} is ranked <b>{7}</b> in the world in terms of total cashew yield.</h4>
                            <table>
                            <tr>
                                <th></th>
                                <th>Satellite Est</th>
                                <th>TNS Survey</th>
                            </tr>
                            <tr>
                                <td>Total Cashew Yield (kg)</td>
                                <td>{15:n}M</td>
                                <td>{3:n}M</td>
                                
                            </tr>
                            <tr>
                                <td>Total Area (ha)</td>
                                <td>{16:n}M</td>
                                <td>{5:n}K</td>
                            </tr>
                            <tr>
                                <td>Cashew Tree Cover (ha)</td>
                                <td>{4:n}K</td>
                                <td>NA</td>
                                
                            </tr>
                            <tr>
                                <td>Yield/Hectare (kg/ha)</td>
                                <td>390</td>
                                <td>{8}</td>
                                
                            </tr>
                            <tr>
                                <td>Yield per Tree (kg/tree)</td>
                                <td>NA</td>
                                <td>{9}</td>
                                
                            </tr>
                            <tr>
                                <td>Number of Trees</td>
                                <td>NA</td>
                                <td>{10:n}K</td>
                                
                            </tr>
                            </table>
                            
                            <table>
                                <td><div id="piechart_div" style="width: 400; height: 350;border: 3px solid #00a5a7"></div></td>
                            </table>
                            <table>
                                <td><div id="donutchart" style="width: 400; height: 350;border: 3px solid #00a5a7"></div></td>
                            </table>
                            <table>
                                <td><div style= "text-align: center"><h5>Source: TNS/BeninCaju Yield Surveys 2020</h5></div>
                            </table>    

                        </body>
                        </html>'''.format(name, pred_ben_data, pred_ground_ben_data, r_total_yield/1000000, r_tree_ha_pred/1000, r_surface_area/1000, abs(round(surface_area - tree_ha_pred,2)), '9th',
                            r_yield_ha, r_yield_tree, r_num_tree/1000, sick_tree, out_prod_tree, dead_tree, active_trees, r_yield_pred/1000000, r_region_size/1000000)



            iframe = folium.IFrame(html=html4, width=450, height=380)

            folium.Popup(iframe, max_width=2000).add_to(temp_layer0)

            # consolidate individual features back into the main layer


        # m.add_child(json_layer_ben)

            temp_layer0.add_to(layer0)

        layer0.add_to(m)

        layer = folium.FeatureGroup(name='Benin Departments', show=False, overlay = False)


        temp_geojson  = folium.GeoJson(data=benin_adm1_json,
            name='Benin-Adm1 Department',
            highlight_function = highlight_function)


        dept_yieldHa = {}
        for feature in temp_geojson.data['features']:
            # GEOJSON layer consisting of a single feature
            name = feature["properties"]["NAME_1"]

            y1 = dtstats_df[dtstats_df['Districts']==name]['Communes']

            # getting values against each value of y

            x1 = dtstats_df[dtstats_df['Districts']==name]['Cashew_Yield']/10000

            z1 = zip(y1,x1)

            c_y1 = dtstats_df1[dtstats_df1['Country']=='Benin']['Districts']
            z_list = []
            for c_y in c_y1:
                c_x = round(sum(ben_yield[ben_yield['Departement']==c_y]['2020 total yield (kg)'].dropna()),2)
                z_list.append((c_y, c_x))

            sorted_by_second = sorted(z_list, reverse = True, key=lambda tup: tup[1])
            list1, _ = zip(*sorted_by_second)

            if heroku:
                position = list1.index(name)
            else:
                position = 1
            my_dict = {'0': "highest", '1': "2nd", '2': "3rd", '3': "4th", '4': "5th", '5': "6th", '6': "7th", '7': "8th", '8': "9th", '9': "10th", '10': "11th", '11':"lowest"}

            pred_dept_data = []
            pred_ground_dept_data = [['Communes', 'Satellite Prediction', 'Ground Data Estimate']]
            for (y,x) in z1:
                x_new = round(sum(ben_yield[ben_yield['Commune']==y]['2020 estimated surface (ha)'].dropna()),2)    
                pred_dept_data.append([y, x])
                pred_ground_dept_data.append([y, x, x_new*100])

            temp_layer1 = folium.GeoJson(feature, zoom_on_click = True, highlight_function = highlight_function)

            tree_ha_pred_dept = int(round(sum(dtstats_df[dtstats_df['Districts']==name].Cashew_Yield)/10000,2))
            yield_pred_dept = int(390*tree_ha_pred_dept)
            surface_areaD = int(round(sum(ben_yield[ben_yield['Departement']==name]['2020 estimated surface (ha)'].dropna()),2))
            total_yieldD = int(round(sum(ben_yield[ben_yield['Departement']==name]['2020 total yield (kg)'].dropna()),2))
            try:
                yield_haD = int(round(np.mean(ben_yield[ben_yield['Departement']==name]['2020 yield per ha (kg)'].dropna()),2))
            except:
                yield_haD = round(np.mean(ben_yield[ben_yield['Departement']==name]['2020 yield per ha (kg)'].dropna()),2)

            #Used only in case of error in the try and except catch    
            try:
                yield_treeD = int(round(np.mean(ben_yield[ben_yield['Departement']==name]['2020 yield per tree (kg)'].dropna()),2))
            except:
                yield_treeD = round(np.mean(ben_yield[ben_yield['Departement']==name]['2020 yield per tree (kg)'].dropna()),2)
                
            num_treeD = int(sum(ben_yield[ben_yield['Departement']==name]['Number of trees'].dropna()))
            sick_treeD = int(sum(ben_yield[ben_yield['Departement']==name]['Number of sick trees'].dropna()))
            out_prod_treeD = int(sum(ben_yield[ben_yield['Departement']==name]['Number of trees out of production'].dropna()))
            dead_treeD = int(sum(ben_yield[ben_yield['Departement']==name]['Number of dead trees'].dropna()))
            region_sizeD = area(feature['geometry'])/10000

            active_treesD = num_treeD- sick_treeD- out_prod_treeD- dead_treeD
            

            try:
                r_tree_ha_pred_dept = round(tree_ha_pred_dept, 1-int(floor(log10(abs(tree_ha_pred_dept))))) if tree_ha_pred_dept < 90000 else round(tree_ha_pred_dept, 2-int(floor(log10(abs(tree_ha_pred_dept)))))
            except:
                r_tree_ha_pred_dept = tree_ha_pred_dept
            try:
                r_yield_pred_dept = round(yield_pred_dept, 1-int(floor(log10(abs(yield_pred_dept))))) if yield_pred_dept < 90000 else round(yield_pred_dept, 2-int(floor(log10(abs(yield_pred_dept)))))
            except:
                r_yield_pred_dept = yield_pred_dept
            try:
                r_surface_areaD = round(surface_areaD, 1-int(floor(log10(abs(surface_areaD))))) if surface_areaD < 90000 else round(surface_areaD, 2-int(floor(log10(abs(surface_areaD)))))
            except:
                r_surface_areaD = surface_areaD
            try:
                r_total_yieldD = round(total_yieldD, 1-int(floor(log10(abs(total_yieldD))))) if total_yieldD < 90000 else round(total_yieldD, 2-int(floor(log10(abs(total_yieldD)))))
            except:
                r_total_yieldD = total_yieldD
            try:
                r_yield_haD = round(yield_haD, 1-int(floor(log10(abs(yield_haD))))) if yield_haD < 90000 else round(yield_haD, 2-int(floor(log10(abs(yield_haD)))))
            except:
                r_yield_haD = yield_haD
            # try:
            #     r_yield_treeD = round(yield_treeD, 1-int(floor(log10(abs(yield_treeD))))) if yield_treeD < 90000 else round(yield_treeD, 2-int(floor(log10(abs(yield_treeD)))))
            # except:
            #     r_yield_treeD = yield_treeD
            try:
                r_yield_treeD = round(r_total_yieldD/active_treesD)
            except:
                r_yield_treeD = yield_treeD
            try:
                r_num_treeD = round(num_treeD, 1-int(floor(log10(abs(num_treeD))))) if num_treeD < 90000 else round(num_treeD, 2-int(floor(log10(abs(num_treeD)))))
            except:
                r_num_treeD = num_treeD
            
            try:
                r_region_sizeD = round(region_sizeD, 1-int(floor(log10(abs(region_sizeD))))) if region_sizeD < 90000 else round(region_sizeD, 2-int(floor(log10(abs(region_sizeD)))))
            except:
                r_region_sizeD = region_sizeD
                
            
            dept_yieldHa[name] = yield_haD
            html3 = '''
                    <html>
                        <head>
                        <style>
                            table {{
                            font-family: arial, sans-serif;
                            border-collapse: collapse;
                            width: 100%;
                            }}


                            table th {{
                            background-color: #004b55;
                            text-align: left;
                            color: #FFF;
                            padding: 4px 30px 4px 8px;
                            }}


                            table td {{
                            border: 1px solid #e3e3e3;
                            padding: 4px 8px;
                            }}


                            table tr:nth-child(odd) td{{
                            background-color: #e7edf0;
                            }}
                            </style>
                            <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                            <script type="text/javascript">
                            // Load Charts and the corechart and barchart packages.
                            google.charts.load('current', {{'packages':['corechart']}});
                            google.charts.load('current', {{'packages':['bar']}});

                            // Draw the pie chart and bar chart when Charts is loaded.
                            google.charts.setOnLoadCallback(drawChart);

                            function drawChart() {{

                                var pie_data = new google.visualization.DataTable();
                                pie_data.addColumn('string', 'Commune');
                                pie_data.addColumn('number', 'Cashew Tree Cover');
                                pie_data.addRows({1});

                                var piechart_options = {{title:'Predicted Cashew Tree Cover: Communes Statistics In {0}',
                                            width:400,
                                            height:350,
                                            is3D: true}};
                                var piechart = new google.visualization.PieChart(document.getElementById('piechart_div'));
                                piechart.draw(pie_data, piechart_options);

                                

                                var data_donut = google.visualization.arrayToDataTable([
                                ['Tree Type', 'Number of Trees'],
                                ['Active Trees',      {14}],
                                ['Sick Trees',      {11}],
                                ['Dead Trees',     {13}],
                                ['Out of Production Trees',      {12}],
                                ]);

                                var options_donut = {{
                                title: 'Cashew Trees Status in {0}',
                                pieHole: 0.5,
                                colors: ['007f00', '#02a8b1', '9e1a1a', '#242526'],
                                }};

                                var chart_donut = new google.visualization.PieChart(document.getElementById('donutchart'));
                                chart_donut.draw(data_donut, options_donut);

                                }};
                            </script>
                        </head>
                        <body>
                            <h2>{0}</h2>
                            <h4>In 2020, {0} was ranked <b>{7}</b> among Benin departments in terms of total cashew yield according to the TNS Yield Survey.</h4>
                            <table>
                            <tr>
                                <th></th>
                                <th>Satellite Est</th>
                                <th>TNS Survey</th>
                                
                            </tr>
                            <tr>
                                <td>Total Cashew Yield (kg)</td>
                                <td>{15:n}M</td>
                                <td>{3:n}M</td>
                                
                            </tr>
                            <tr>
                                <td>Total Area (ha)</td>
                                <td>{16:n}M</td>
                                <td>{5:n}K</td>
                            </tr>
                            <tr>
                                <td>Cashew Tree Cover (ha)</td>
                                <td>{4:n}K</td>
                                <td>NA</td>
                                
                            </tr>
                            <tr>
                                <td>Yield/Hectare (kg/ha)</td>
                                <td>390</td>
                                <td>{8}</td>
                                
                            </tr>
                            <tr>
                                <td>Yield per Tree (kg/tree)</td>
                                <td>NA</td>
                                <td>{9}</td>
                                
                            </tr>
                            <tr>
                                <td>Number of Trees</td>
                                <td>NA</td>
                                <td>{10:n}K</td>
                            
                            </tr>
                            </table>
                            
                            <table>
                                <td><div id="piechart_div" style="border: 3px solid #00a5a7"></div></td>
                            </table>                           
                            <table>
                                <td><div id="donutchart" style="width: 400; height: 350;border: 3px solid #00a5a7"></div></td>
                            </table>
                            <table>
                                <td><div style= "text-align: center"><h5>Source: TNS/BeninCaju Yield Surveys 2020</h5></div>
                            </table> 
                        </body>
                        </html>
                    '''.format(name, pred_dept_data, pred_ground_dept_data, r_total_yieldD/1000000, r_tree_ha_pred_dept/1000, r_surface_areaD/1000, abs(round(surface_areaD - tree_ha_pred_dept,2)), my_dict[str(position)],
                            r_yield_haD, r_yield_treeD, r_num_treeD/1000, sick_treeD, out_prod_treeD, dead_treeD, num_treeD-sick_treeD-out_prod_treeD-dead_treeD, r_yield_pred_dept/1000000, r_region_sizeD/1000000)

            iframe = folium.IFrame(html=html3, width=450, height=380)

            folium.Popup(iframe, max_width=2000).add_to(temp_layer1)

            # consolidate individual features back into the main layer



            folium.GeoJsonTooltip(fields=["NAME_1"],
                aliases = ["Department:"],
                labels = True,
                sticky = False,
                style=("background-color: white; color: black; font-family: sans-serif; font-size: 12px; padding: 4px;")
                ).add_to(temp_layer1)

            temp_layer1.add_to(layer)

        layer.add_to(m)

        # Communes section

        layer2 = folium.FeatureGroup(name='Benin Communes', show=False, overlay = False)


        temp_geojson2 = folium.GeoJson(data = benin_adm2_json,
            name = 'Benin-Adm2 Communes',
            highlight_function = highlight_function)


        for feature in temp_geojson2.data['features']:
            # GEOJSON layer consisting of a single feature
            name = feature["properties"]["NAME_2"]

            c_y2 = dtstats_df['Communes']

            z_list_2 = []
            for c_y in c_y2:
                c_x = round(sum(ben_yield[ben_yield['Commune']==c_y]['2020 estimated surface (ha)'].dropna()),2)
                z_list_2.append((c_y, c_x))

            sorted_by_second2 = sorted(z_list_2, reverse = True, key=lambda tup: tup[1])
            list2, _ = zip(*sorted_by_second2)

            if heroku:
                position2 = list2.index(name) 
            else:
                position2 = 1
                               
            my_dict_communes = {'1': 'highest',
                    '2': '2nd',
                    '3': '3rd',
                    '4': '4th',
                    '5': '5th',
                    '6': '6th',
                    '7': '7th',
                    '8': '8th',
                    '9': '9th',
                    '10': '10th',
                    '11': '11th',
                    '12': '12th',
                    '13': '13th',
                    '14': '14th',
                    '15': '15th',
                    '16': '16th',
                    '17': '17th',
                    '18': '18th',
                    '19': '19th',
                    '20': '20th',
                    '21': '21st',
                    '22': '22nd',
                    '23': '23rd',
                    '24': '24th',
                    '25': '25th',
                    '26': '26th',
                    '27': '27th',
                    '28': '28th',
                    '29': '29th',
                    '30': '30th',
                    '31': '31st',
                    '32': '32nd',
                    '33': '33rd',
                    '34': '34th',
                    '35': '35th',
                    '36': '36th',
                    '37': '37th',
                    '38': '38th',
                    '39': '39th',
                    '40': '40th',
                    '41': '41st',
                    '42': '42nd',
                    '43': '43rd',
                    '44': '44th',
                    '45': '45th',
                    '46': '46th',
                    '47': '47th',
                    '48': '48th',
                    '49': '49th',
                    '50': '50th',
                    '51': '51st',
                    '52': '52nd',
                    '53': '53rd',
                    '54': '54th',
                    '55': '55th',
                    '56': '56th',
                    '57': '57th',
                    '58': '58th',
                    '59': '59th',
                    '60': '60th',
                    '61': '61st',
                    '62': '62nd',
                    '63': '63rd',
                    '64': '64th',
                    '65': '65th',
                    '66': '66th',
                    '67': '67th',
                    '68': '68th',
                    '69': '69th',
                    '70': '70th',
                    '71': '71st',
                    '72': '72nd',
                    '73': '73rd',
                    '74': '74th',
                    '75': '75th',
                    '76': 'lowest'}

            temp_layer2 = folium.GeoJson(feature,  zoom_on_click = True, highlight_function = highlight_function)

            name = feature['properties']['NAME_2']
            tree_ha_pred_comm = int(round(sum(dtstats_df[dtstats_df['Communes']==name].Cashew_Yield)/10000,2))
            yield_pred_comm = int(390*tree_ha_pred_comm)
            
            surface_areaC = int(round(sum(ben_yield[ben_yield['Commune']==name]['2020 estimated surface (ha)'].dropna()),2))
            total_yieldC = int(round(sum(ben_yield[ben_yield['Commune']==name]['2020 total yield (kg)'].dropna()),2))
            try:
                yield_haC = int(round(np.mean(ben_yield[ben_yield['Commune']==name]['2020 yield per ha (kg)'].dropna()),2))
            except:
                yield_haC = round(np.mean(ben_yield[ben_yield['Commune']==name]['2020 yield per ha (kg)'].dropna()),2)
                
            try:
                yield_treeC = int(round(np.mean(ben_yield[ben_yield['Commune']==name]['2020 yield per tree (kg)'].dropna()),2))
            except:
                yield_treeC = round(np.mean(ben_yield[ben_yield['Commune']==name]['2020 yield per tree (kg)'].dropna()),2)
                
            num_treeC = int(sum(ben_yield[ben_yield['Commune']==name]['Number of trees'].dropna()))
            sick_treeC = int(sum(ben_yield[ben_yield['Commune']==name]['Number of sick trees'].dropna()))
            out_prod_treeC = int(sum(ben_yield[ben_yield['Commune']==name]['Number of trees out of production'].dropna()))
            dead_treeC = int(sum(ben_yield[ben_yield['Commune']==name]['Number of dead trees'].dropna()))
            region_sizeC = area(feature['geometry'])/10000

            active_treesC = num_treeC- sick_treeC- out_prod_treeC- dead_treeC
            
            try:
                r_region_sizeC = round(region_sizeC, 1-int(floor(log10(abs(region_sizeC))))) if region_sizeC < 90000 else round(region_sizeC, 2-int(floor(log10(abs(region_sizeC)))))
            except:
                r_region_sizeC = region_sizeC
            
            try:
                r_tree_ha_pred_comm = round(tree_ha_pred_comm, 1-int(floor(log10(abs(tree_ha_pred_comm))))) if tree_ha_pred_comm < 90000 else round(tree_ha_pred_comm, 2-int(floor(log10(abs(tree_ha_pred_comm)))))
            except:
                r_tree_ha_pred_comm = tree_ha_pred_comm
            try:
                r_yield_pred_comm = round(yield_pred_comm, 1-int(floor(log10(abs(yield_pred_comm))))) if yield_pred_comm < 90000 else round(yield_pred_comm, 2-int(floor(log10(abs(yield_pred_comm)))))
            except:
                r_yield_pred_comm = yield_pred_comm
            try:
                r_surface_areaC = round(surface_areaC, 1-int(floor(log10(abs(surface_areaC))))) if surface_areaC < 90000 else round(surface_areaC, 2-int(floor(log10(abs(surface_areaC)))))
            except:
                r_surface_areaC = surface_areaC
            try:
                r_total_yieldC = round(total_yieldC, 1-int(floor(log10(abs(total_yieldC))))) if total_yieldC < 90000 else round(total_yieldC, 2-int(floor(log10(abs(total_yieldC)))))
            except:
                r_total_yieldC = total_yieldC
            try:
                r_yield_haC = round(yield_haC, 1-int(floor(log10(abs(yield_haC))))) if yield_haC < 90000 else round(yield_haC, 2-int(floor(log10(abs(yield_haC)))))
            except:
                r_yield_haC = yield_haC
            # try:
            #     r_yield_treeC = round(yield_treeC, 1-int(floor(log10(abs(yield_treeC))))) if yield_treeC < 90000 else round(yield_treeC, 2-int(floor(log10(abs(yield_treeC)))))
            # except:
            #     r_yield_treeC = yield_treeC

            try:
                r_yield_treeC = round(r_total_yieldC/active_treesC)
            except:
                r_yield_treeC = yield_treeC

            try:
                r_num_treeC = round(num_treeC, 1-int(floor(log10(abs(num_treeC))))) if num_treeC < 90000 else round(num_treeC, 2-int(floor(log10(abs(num_treeC)))))
            except:
                r_num_treeC = num_treeC


            html3 = '''
                    <html>
                    <head>
                        <style>
                            table {{
                            font-family: arial, sans-serif;
                            border-collapse: collapse;
                            width: 100%;
                            }}


                            table th {{
                            background-color: #004b55;
                            text-align: left;
                            color: #FFF;
                            padding: 4px 30px 4px 8px;
                            }}


                            table td {{
                            border: 1px solid #e3e3e3;
                            padding: 4px 8px;
                            }}


                            table tr:nth-child(odd) td{{
                            background-color: #e7edf0;
                            }}
                            </style>
                            <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                            <script type="text/javascript">
                            // Load Charts and the corechart and barchart packages.
                            google.charts.load('current', {{'packages':['corechart']}});
                            google.charts.load('current', {{'packages':['bar']}});

                            // Draw the pie chart and bar chart when Charts is loaded.
                            google.charts.setOnLoadCallback(drawChart);

                            function drawChart() {{

                                var data_donut = google.visualization.arrayToDataTable([
                                ['Tree Type', 'Number of Trees'],
                                ['Active Trees',      {12}],
                                ['Sick Trees',      {9}],
                                ['Dead Trees',     {11}],
                                ['Out of Production Trees',      {10}],
                                ]);

                                var options_donut = {{
                                title: 'Cashew Trees Status in {0}',
                                pieHole: 0.5,
                                colors: ['007f00', '#02a8b1', '9e1a1a', '#242526'],
                                }};

                                var chart_donut = new google.visualization.PieChart(document.getElementById('donutchart'));
                                chart_donut.draw(data_donut, options_donut);

                                }};
                            </script>
                        </head>
                        <body>

                            <h2>{0}</h2>
                            <h4>In 2020, {0} was ranked <b>{5}</b> among Benin communes in terms of total cashew yield according to the TNS Yield Survey.</h4>
                            <table>
                            <tr>
                                <th></th>
                                <th>Satellite Est</th>
                                <th>TNS Survey</th>
                                
                            </tr>
                            <tr>
                                <td>Total Cashew Yield (kg)</td>
                                <td>{13:n}M</td>
                                <td>{1:n}M</td>
                                
                            </tr>
                            <tr>
                                <td>Total Area (ha)</td>
                                <td>{14:n}K</td>
                                <td>{3:n}K</td>
                            </tr>
                            <tr>
                                <td>Cashew Tree Cover (ha)</td>
                                <td>{2:n}K</td>
                                <td>NA</td>
                                
                            </tr>
                            <tr>
                                <td>Yield/Hectare (kg/ha)</td>
                                <td>390</td>
                                <td>{6}</td>
                            
                            </tr>
                            <tr>
                                <td>Yield per Tree (kg/tree)</td>
                                <td>NA</td>
                                <td>{7}</td>
                            
                            </tr>
                            <tr>
                                <td>Number of Trees</td>
                                <td>NA</td>
                                <td>{8:n}K</td>
                                
                            </tr>
                            </table>
                            
                            <table>
                                <td><div id="donutchart" style="width: 400; height: 350;border: 3px solid #00a5a7"></div></td>
                            </table>
                            <table>
                                <td><div style= "text-align: center"><h5>Source: TNS/BeninCaju Yield Surveys 2020</h5></div>
                            </table> 
                        </body>
                        </html>
                    '''.format(name, r_total_yieldC/1000000, r_tree_ha_pred_comm/1000, r_surface_areaC/1000, abs(round(surface_areaC - tree_ha_pred_comm,2)), my_dict_communes[str(position2+1)],
                            r_yield_haC, r_yield_treeC, r_num_treeC/1000, sick_treeC, out_prod_treeC, dead_treeC, active_treesC, r_yield_pred_comm/1000000, r_region_sizeC/1000)

            iframe = folium.IFrame(html=html3, width=450, height=380)

            folium.Popup(iframe, max_width=2000).add_to(temp_layer2)

            # consolidate individual features back into the main layer

            folium.GeoJsonTooltip(fields=["NAME_2"],
                aliases = ["Commune:"],
                labels = True,
                sticky = False,
                style=("background-color: white; color: black; font-family: sans-serif; font-size: 12px; padding: 4px;")
                ).add_to(temp_layer2)

            temp_layer2.add_to(layer2)

        layer2.add_to(m)

        #Adding Benin Plantation to the map
        #Adding Benin Plantation to the map
        layer_alt = folium.FeatureGroup(name='Plantation Locations', show=True, overlay = True)
        plantation_cluster = MarkerCluster(name="Benin Plantations")

        temp_geojson_a  = folium.GeoJson(data=alteia_json,
            name='Alteia Plantation Data 2',
            highlight_function = highlight_function)

        grand_pred_surface = 0
        grand_ground_surface = 0
        grand_total_yield = 0
        grand_plantation_size = 0
        counter = 0
        grand_num_tree = 0
        for feature in temp_geojson_a.data['features']:
            # GEOJSON layer consisting of a single feature
            code_sum = feature["properties"]["Plantation code"]
            if code_sum in special_id:
                counter += 1
                indx = special_id.index(code_sum)
                code_2_sum = special_id_tuple[indx][1]
                grand_pred_surface += sum(round(alteia_df[alteia_df['Code']==code_sum].Cashew_Tree/10000,2))
                grand_ground_surface += sum(ben_yield[ben_yield['Code']==code_2_sum]['2020 estimated surface (ha)'])
                grand_total_yield += sum(ben_yield[ben_yield['Code']==code_2_sum]['2020 total yield (kg)'])
                grand_plantation_size += area(feature['geometry'])/10000
                
                grand_num_tree += sum(ben_yield[ben_yield['Code']==code_2_sum]['Number of trees'])

        average_pred_yield_ha = 390
        total_grand_pred_surface = int(round(grand_pred_surface))
        total_grand_ground_surface = int(round(grand_ground_surface))
        total_grand_pred_yield = int(round(390*grand_pred_surface))
        total_grand_ground_yield = int(round(grand_total_yield))
        grand_plantation_size = int(round(grand_plantation_size))
        average_ground_yield_ha = int(total_grand_ground_yield/total_grand_ground_surface)
        total_grand_num_tree = int(round(grand_num_tree))
        total_grand_yield_tree = int(round(total_grand_ground_yield/total_grand_num_tree))

        r_total_grand_num_tree = round(total_grand_num_tree, 1-int(floor(log10(abs(total_grand_num_tree))))) if total_grand_num_tree < 90000 else round(total_grand_num_tree, 2-int(floor(log10(abs(total_grand_num_tree)))))
        r_total_grand_pred_yield = round(total_grand_pred_yield, 1-int(floor(log10(abs(total_grand_pred_yield))))) if total_grand_pred_yield < 90000 else round(total_grand_pred_yield, 2-int(floor(log10(abs(total_grand_pred_yield)))))
        r_total_grand_ground_yield = round(total_grand_ground_yield, 1-int(floor(log10(abs(total_grand_ground_yield))))) if total_grand_ground_yield < 90000 else round(total_grand_ground_yield, 2-int(floor(log10(abs(total_grand_ground_yield)))))

        for feature in temp_geojson_a.data['features']:
            
            code = feature["properties"]["Plantation code"]
            
            if code in special_id:
                
                plantation_size = area(feature['geometry'])/10000
                plantation_size = round(plantation_size,1)
                indx = special_id.index(code)
                code_2 = special_id_tuple[indx][1]
                
                
                temp_layer_a = folium.GeoJson(feature, zoom_on_click = True)
                department_name = list(ben_yield[ben_yield['Code']==code_2]['Departement'])[0]
                length2 = len(ben_yield[ben_yield['Code']==code_2]['2020 estimated surface (ha)'])
                tree_ha_pred_plant = round(sum(round(alteia_df[alteia_df['Code']==code].Cashew_Tree/10000,2)),1)
                yield_pred_plant = int(tree_ha_pred_plant*dept_yieldHa[department_name])
                surface_areaP =  round(sum(ben_yield[ben_yield['Code']==code_2]['2020 estimated surface (ha)'])/length2,1)
                total_yieldP =  int(round(sum(ben_yield[ben_yield['Code']==code_2]['2020 total yield (kg)'])/length2))
                yield_haP =  int(total_yieldP/surface_areaP)
                num_treeP = int(sum(ben_yield[ben_yield['Code']==code_2]['Number of trees']))
                yield_treeP = int(round(total_yieldP/num_treeP))
                
                nameP = list(ben_yield[ben_yield['Code']==code_2]['Surname'])[0]+' '+list(ben_yield[ben_yield['Code']==code_2]['Given Name'])[0]
                village = list(ben_yield[ben_yield['Code']==code_2]['Village'])[0]

                try:
                    r_total_yieldP = round(total_yieldP, 1-int(floor(log10(abs(total_yieldP))))) if total_yieldP < 90000 else round(total_yieldP, 2-int(floor(log10(abs(total_yieldP)))))
                except:
                    r_total_yieldP = total_yieldP
                try:
                    r_yield_pred_plant = round(yield_pred_plant, 1-int(floor(log10(abs(yield_pred_plant))))) if yield_pred_plant < 90000 else round(yield_pred_plant, 2-int(floor(log10(abs(yield_pred_plant)))))
                except:
                    r_yield_pred_plant = yield_pred_plant
                    
                html_a = '''
                    <html>
                    <head>
                        <style>
                            table {{
                            font-family: arial, sans-serif;
                            border-collapse: collapse;
                            width: 100%;
                            }}


                            table th {{
                            background-color: #004b55;
                            text-align: left;
                            color: #FFF;
                            padding: 4px 30px 4px 8px;
                            }}


                            table td {{
                            border: 1px solid #e3e3e3;
                            padding: 4px 8px;
                            }}


                            table tr:nth-child(odd) td{{
                            background-color: #e7edf0;
                            }}
                            </style>
                        </head>
                        <body>

                            <h3>Plantation Owner: {0}</h3>
                            <h4>Plantation ID: {1}</h4>
                            <h4>Village: {2}</h4>
                            <table>
                            <tr>
                                <th></th>
                                <th>Satellite Estimate</th>
                                <th>2020 Yield Survey</th>
                            </tr>
                            <tr>
                                <td>Cashew Yield (kg)</td>
                                <td>{6:n}K</td>
                                <td>{7:n}K</td>       
                            </tr>
                            <tr>
                                <td>Plantation Size (ha)</td>
                                <td>{3}</td>
                                <td>{4}</td>
                            </tr>
                            <tr>
                                <td>Cashew Surface Area (ha)</td>
                                <td>{5}</td>
                                <td>NA</td>
                            </tr>
                            <tr>
                                <td>Yield Per Hectare (kg/ha)</td>
                                <td>{8}</td>
                                <td>{9}</td>  
                            </tr>
                            <tr>
                                <td>Number of Trees</td>
                                <td>NA</td>
                                <td>{20}</td>
                            </tr>
                            <tr>
                                <td>Yield per Tree (kg/tree)</td>
                                <td>NA</td>
                                <td>{21}</td>
                            </tr>
                            
                            </table>
                            
                            <h4>
                            Average Surface Area and Cashew Yield Information for Plantations in Benin Republic
                            </h4>
                            <table>
                            <tr>
                                <th></th>
                                <th>Satellite Estimate</th>
                                <th>2020 Yield Survey</th>
                            </tr>
                            <tr>
                                <td>Number of Farms</td>
                                <td>{17}</td>
                                <td>{17}</td>
                            
                            </tr>
                            <tr>
                                <td>Total Plantation Yield (kg)</td>
                                <td>{13:n}K</td>
                                <td>{14:n}K</td>
                                
                            </tr>
                            <tr>
                                <td>Total Plantation Area (ha)</td>
                                <td>{10}</td>
                                <td>{11}</td>
                            
                            </tr>
                            <tr>
                                <td>Cashew Surface Area (ha)</td>
                                <td>{12}</td>
                                <td>NA</td>
                            
                            </tr>
                            
                            <tr>
                                <td>Average Yield Per Hectare (kg/ha)</td>
                                <td>{15}</td>
                                <td>{16}</td>
                                
                            </tr>
                            <tr>
                                <td>Total Number of Trees</td>
                                <td>NA</td>
                                <td>{18:n}K</td>
                            </tr>
                            <tr>
                                <td>Average Yield per Tree (kg/tree)</td>
                                <td>NA</td>
                                <td>{19}</td>
                            </tr>
                            
                            </table>
                            <table>
                                <td><div style= "text-align: center"><h6>Source: TNS/BeninCaju Yield Surveys 2020</h6></div>
                            </table> 
                        </body>
                        </html>
                    '''.format(nameP, code, village, plantation_size, surface_areaP, tree_ha_pred_plant, r_yield_pred_plant/1000,
                            r_total_yieldP/1000, dept_yieldHa[department_name], yield_haP, grand_plantation_size, total_grand_ground_surface, total_grand_pred_surface,
                            r_total_grand_pred_yield/1000, r_total_grand_ground_yield/1000, average_pred_yield_ha, average_ground_yield_ha, counter, r_total_grand_num_tree/1000, total_grand_yield_tree, num_treeP, yield_treeP)

                iframe = folium.IFrame(html=html_a, width=370, height=380)

                folium.Popup(iframe, max_width=1000).add_to(temp_layer_a)

                # consolidate individual features back into the main layer
                
                s = shape(feature["geometry"])
                centre = s.centroid
                folium.Marker(location= [centre.y, centre.x],
                            rise_on_hover=True,
                            rise_offset = 250,
                            icon = folium.Icon(color="green", icon="globe"),
                            popup=None).add_to(plantation_cluster)

                temp_layer_a.add_to(layer_alt)
        plantation_cluster.add_to(layer_alt)

        layer_alt.add_to(m)
        feature_group_drone.add_to(m)
        m.add_child(folium.LayerControl())

        m=m._repr_html_()
        context = {'my_map': m}

        ## rendering
        return context


@login_required(login_url="/login/")
def index(request):

    home_obj = my_home()
    context = home_obj.get_context_data()
    context['segment'] = 'index'

    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        context['segment'] = load_template

        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))
