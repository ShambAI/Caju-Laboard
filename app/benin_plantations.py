from authentication.models import BeninYield
from authentication.models import AlteiaData
from authentication.models import SpecialTuple
import folium
from django.utils.translation import gettext
import geojson
from area import area
from math import log10, floor
from folium.plugins import MarkerCluster
import pandas as pd
from shapely.geometry import shape

with open("Data/CajuLab_Plantations.geojson", errors="ignore") as f:
    alteia_json = geojson.load(f)

def highlight_function(feature):
            return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}

class Benin_plantation_LAYER:
    def __init__(self, benin_plantation_layer, dept_yieldHa):
        self.benin_plantation_layer = benin_plantation_layer
        self.dept_yieldHa = dept_yieldHa
    def add_benin_plantation(self):
        
        #Plantation translation variables
        Plantation_Owner = gettext("Plantation Owner")
        Plantation_ID = gettext("Plantation ID")
        Village = gettext("Village")
        Satellite_Estimate = gettext("Satellite Estimate")
        Yield_Survey = gettext("2020 Yield Survey")
        Cashew_Yield = gettext("Cashew Yield (kg)")
        Plantation_Size = gettext("Plantation Size (ha)")
        Cashew_Surface_Area = gettext("Cashew Surface Area (ha)")
        Yield_Per_Hectare = gettext("Yield Per Hectare (kg/ha)")
        Number_of_TreesP = gettext("Number of Trees")
        Yield_per_TreeP = gettext("Yield per Tree (kg/tree)")
        Average_Surface_AreaP = gettext("Average Surface Area and Cashew Yield Information for Plantations in Benin Republic")

        Number_of_Farms = gettext("Number of Farms")
        Total_Plantation_Yield = gettext("Total Plantation Yield (kg)")
        Total_Plantation_Area = gettext("Total Plantation Area (ha)")
        Cashew_Surface_Area = gettext("Cashew Surface Area (ha)")
        Average_Yield_Per = gettext("Average Yield Per Hectare (kg/ha)")
        Total_Number_of = gettext("Total Number of Trees")
        Average_Yield_per = gettext("Average Yield per Tree (kg/tree)")
        Source_TNS = gettext("Source: TNS/BeninCaju Yield Surveys 2020")
        
        #Adding Benin Plantation to the map
        plantation_cluster = MarkerCluster(name=gettext("Benin Plantations"))
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
            items = len(SpecialTuple.objects.filter(alteia_id=code_sum))
            if items != 0:
                counter += 1
                code_2_sum = SpecialTuple.objects.filter(alteia_id=code_sum)[0].plantation_id


                grand_pred_surface += round(AlteiaData.objects.filter(plantation_code=code_sum)[0].cashew_tree_cover/10000,2)
                grand_ground_surface += BeninYield.objects.filter(plantation_code=code_2_sum)[0].surface_area
                grand_total_yield += BeninYield.objects.filter(plantation_code=code_2_sum)[0].total_yield_kg
                grand_plantation_size += area(feature['geometry'])/10000
                grand_num_tree += BeninYield.objects.filter(plantation_code=code_2_sum)[0].total_number_trees

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
            
            items = len(SpecialTuple.objects.filter(alteia_id=code))
            if items != 0:
                plantation_size = area(feature['geometry'])/10000
                plantation_size = round(plantation_size,1)
                code_2 = SpecialTuple.objects.filter(alteia_id=code)[0].plantation_id  
                temp_layer_a = folium.GeoJson(feature, zoom_on_click = True)
                department_name = BeninYield.objects.filter(plantation_code=code_2)[0].department
                tree_ha_pred_plant = round(round(AlteiaData.objects.filter(plantation_code=code)[0].cashew_tree_cover/10000,2),1)
                yield_pred_plant = int(tree_ha_pred_plant*self.dept_yieldHa[department_name])
                surface_areaP =  round(BeninYield.objects.filter(plantation_code=code_2)[0].surface_area,1)
                total_yieldP =  int(round(BeninYield.objects.filter(plantation_code=code_2)[0].total_yield_kg))
                yield_haP =  int(total_yieldP/surface_areaP)
                num_treeP = int(BeninYield.objects.filter(plantation_code=code_2)[0].total_number_trees)
                yield_treeP = int(round(total_yieldP/num_treeP))
                nameP = BeninYield.objects.filter(plantation_code=code_2)[0].owner_first_name+' '+BeninYield.objects.filter(plantation_code=code_2)[0].owner_last_name
                village = BeninYield.objects.filter(plantation_code=code_2)[0].village

                try:
                    r_total_yieldP = round(total_yieldP, 1-int(floor(log10(abs(total_yieldP))))) if total_yieldP < 90000 else round(total_yieldP, 2-int(floor(log10(abs(total_yieldP)))))
                except:
                    r_total_yieldP = total_yieldP
                try:
                    r_yield_pred_plant = round(yield_pred_plant, 1-int(floor(log10(abs(yield_pred_plant))))) if yield_pred_plant < 90000 else round(yield_pred_plant, 2-int(floor(log10(abs(yield_pred_plant)))))
                except:
                    r_yield_pred_plant = yield_pred_plant


                
                    
                html_a = f'''
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
                        

                            <h3>{Plantation_Owner}: {nameP}</h3>
                            <h4>{Plantation_ID}: {code}</h4>
                            <h4>{Village}: {village}</h4>
                            <table>
                            <tr>
                                <th></th>
                                <th>{Satellite_Estimate}</th>
                                <th>{Yield_Survey}</th>
                            </tr>
                            <tr>
                                <td>{Cashew_Yield}</td>
                                <td>{r_yield_pred_plant/1000:n}K</td>
                                <td>{r_total_yieldP/1000:n}K</td>       
                            </tr>
                            <tr>
                                <td>{Plantation_Size}</td>
                                <td>{plantation_size}</td>
                                <td>{surface_areaP}</td>
                            </tr>
                            <tr>
                                <td>{Cashew_Surface_Area}</td>
                                <td>{tree_ha_pred_plant}</td>
                                <td>NA</td>
                            </tr>
                            <tr>
                                <td>{Yield_Per_Hectare}</td>
                                <td>{self.dept_yieldHa[department_name]}</td>
                                <td>{yield_haP}</td>  
                            </tr>
                            <tr>
                                <td>{Number_of_TreesP}</td>
                                <td>NA</td>
                                <td>{num_treeP}</td>
                            </tr>
                            <tr>
                                <td>{Yield_per_TreeP}</td>
                                <td>NA</td>
                                <td>{yield_treeP}</td>
                            </tr>
                            
                            </table>
                            
                            <h4>
                            {Average_Surface_AreaP}
                            </h4>
                            <table>
                            <tr>
                                <th></th>
                                <th>{Satellite_Estimate}</th>
                                <th>{Yield_Survey}</th>
                            </tr>
                            <tr>
                                <td>{Number_of_Farms}</td>
                                <td>{counter}</td>
                                 <td>{counter}</td>
                            
                            </tr>
                            <tr>
                                <td>{Total_Plantation_Yield}</td>
                                <td>{r_total_grand_pred_yield/1000:n}K</td>
                                <td>{r_total_grand_ground_yield/1000:n}K</td>
                                
                            </tr>
                            <tr>
                                <td>{Total_Plantation_Area}</td>
                                <td>{grand_plantation_size}</td>
                                <td>{total_grand_ground_surface}</td>
                            
                            </tr>
                            <tr>
                                <td>{Cashew_Surface_Area}</td>
                                <td>{total_grand_pred_surface}</td>
                                <td>NA</td>
                            
                            </tr>
                            
                            <tr>
                                <td>{Average_Yield_Per}</td>
                                <td>{average_pred_yield_ha}</td>
                                <td>{average_ground_yield_ha}</td>
                                
                            </tr>
                            <tr>
                                <td>{Total_Number_of}</td>
                                <td>NA</td>
                                <td>{r_total_grand_num_tree/1000:n}K</td>
                            </tr>
                            <tr>
                                <td>{Average_Yield_per}</td>
                                <td>NA</td>
                                <td>{total_grand_yield_tree}</td>
                            </tr>
                            
                            </table>
                            <table>
                                <td><div style= "text-align: center"><h6>{Source_TNS}</h6></div>
                            </table> 
                        </body>
                        </html>
                    '''
                    
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

                temp_layer_a.add_to(self.benin_plantation_layer)

        plantation_cluster.add_to(self.benin_plantation_layer)
        return self.benin_plantation_layer

        