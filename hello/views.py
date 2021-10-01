from django.shortcuts import render
from branca.element import MacroElement
from jinja2 import Template

# generic base view
from django.views.generic import TemplateView 




#folium
import folium
import geojson
from folium import plugins
import pandas as pd
from folium.plugins import MarkerCluster



# import ee
# from geemap import geojson_to_ee, ee_to_geojson
# from ipyleaflet import GeoJSON, Marker, MarkerCluster

# ee.Authenticate()

# ee.Initialize()


#forntend
#home
# import ee

service_account = 'cajulab@benin-cajulab-web-application.iam.gserviceaccount.com'
# credentials = ee.ServiceAccountCredentials(service_account, 'privatekey.json')
# ee.Initialize(credentials)

class FloatImage(MacroElement):
    """Adds a floating image in HTML canvas on top of the map."""
    _template = Template("""
            {% macro header(this,kwargs) %}
                <style>
                    #{{this.get_name()}} {
                        position:absolute;
                        bottom:{{this.bottom}}%;
                        left:{{this.left}}%;
                        }
                </style>
            {% endmacro %}
            {% macro html(this,kwargs) %}
            <img id="{{this.get_name()}}" alt="float_image"
                 src="{{ this.image }}"
                 style="z-index: 999999"
                 width="200" height="85">
            </img>
            {% endmacro %}
            """)

    def __init__(self, image, bottom=75, left=75):
        super(FloatImage, self).__init__()
        self._name = 'FloatImage'
        self.image = image
        self.bottom = bottom
        self.left = left


class home(TemplateView):
    template_name = 'index.html'
    # Define a method for displaying Earth Engine image tiles on a folium map.
    

    def get_context_data(self, **kwargs):

        figure = folium.Figure()

        m = folium.Map(
            location=[9.0, 2.4],
            zoom_start=7,
        )
        m.add_to(figure)

        plugins.Fullscreen(position='topright', title='Full Screen', title_cancel='Exit Full Screen', force_separate_button=False).add_to(m)
        
        # alldept = ee.Image('users/ashamba/allDepartments_v0')
        ben_nursery = pd.read_excel("./Data/Nurseries.xlsx",engine='openpyxl',)

        ben_nursery['Commune'] = ben_nursery['Commune'].str.title()
        ben_nursery['Owner'] = ben_nursery['Owner'].str.title()

        #Drop nan columns
        ben_nursery.drop(["Date","Provenance","Regarnissage", "Altitude", "Partenaire"], axis = 1, inplace = True)
        ben_nursery.dropna(inplace=True)

        marker_cluster = MarkerCluster(name="Benin-Nursery Information").add_to(m)
        
        for i in range(len(ben_nursery)):
           folium.Marker(location= [ben_nursery[i:i+1]['Latitude'].values[0], ben_nursery[i:i+1]['Longitude'].values[0]],
                        rise_on_hover=True,
                        rise_offset = 250,
                        icon = folium.Icon(color="red", icon="leaf"),
                        popup='''
                        <h4 style="font-family: 'Trebuchet MS', sans-serif">Commune Name: <b>{}</b></h4>
                        <h5 style="font-family: 'Trebuchet MS', sans-serif">Nursery Owner: <i>{}</i></h5>
                        <h5 style="font-family: 'Trebuchet MS', sans-serif">Nursery Area (ha): <b>{}</b></h5>
                        <h5 style="font-family: 'Trebuchet MS', sans-serif">Number of Plants: <b>{}</b></h5>
                        <a href="https://www.technoserve.org/our-work/agriculture/cashew/?_ga=2.159985149.1109250972.1626437600-1387218312.1616379774"target="_blank">click link to website</a>
                        <img src="https://gumlet.assettype.com/deshdoot/import/2019/12/tripXOXO-e1558439144643.jpg?w=1200&h=750&auto=format%2Ccompress&fit=max" width="200" height="70">
                        '''.format(ben_nursery[i:i+1].Commune.values[0], ben_nursery[i:i+1].Owner.values[0], ben_nursery[i:i+1]['Area (ha)'].values[0], ben_nursery[i:i+1]['Numebr of Plants'].values[0])).add_to(marker_cluster)

        # alldept = ee.Image('srtm90_v4')

        # benin_adm1 = ee.FeatureCollection("users/ashamba/BEN_adm1")
        # benin_adm1_json = ee_to_geojson(benin_adm1)

        with open("ben_adm1.json") as f:
            benin_adm1_json = geojson.load(f)

        with open("ben_adm2.json") as f:
            benin_adm2_json = geojson.load(f)
        
        
        # benin_adm2 = ee.FeatureCollection("users/ashamba/BEN_adm2")
        # benin_adm2_json = ee_to_geojson(benin_adm2)

        



        # dataset = ee.ImageCollection('MODIS/006/MOD13Q1').filter(ee.Filter.date('2019-07-01', '2019-11-30')).first()
        # modisndvi = dataset.select('NDVI')
        # visParams = {'min':0, 'max':3000, 'palette':['225ea8','41b6c4','a1dab4','034B48']}
        # vis_paramsNDVI = {
        #     'min': 0,
        #     'max': 9000,
        #     'palette': [ 'FE8374', 'C0E5DE', '3A837C','034B48',]}

        # map_id_dict = ee.Image(modisndvi).getMapId(vis_paramsNDVI)
        # folium.raster_layers.TileLayer(
        #             tiles = map_id_dict['tile_fetcher'].url_format,
        #             attr = 'Google Earth Engine',
        #             name = 'NDVI',
        #             overlay = True,
        #             control = True
        #             ).add_to(m)

        # def add_ee_layer(self, ee_image_object, vis_params, name):
        #     map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
        #     folium.raster_layers.TileLayer(
        #         tiles=map_id_dict['tile_fetcher'].url_format,
        #         attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
        #         name=name,
        #         overlay=True,
        #         control=True
        #     ).add_to(self)

        # folium.Map.add_ee_layer = add_ee_layer   
        # m.add_ee_layer(alldept, {'min':0, 'max': 4, 'palette': "black, green, white, gray"}, 'Benin-Caju Prediction')

        # json_layer_ben = folium.GeoJson(data=benin_adm1_json, name='Benin States JSON')

        def highlight_function(feature):
            return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "1, 1"}

        g = folium.GeoJson(data=benin_adm1_json,
           name='Benin-Adm1 Department',
           highlight_function = highlight_function)

        g1 = folium.GeoJson(data=benin_adm2_json,
           name='Benin-Adm2 Communes',
           highlight_function = highlight_function)

    
        
        # m.add_child(json_layer_ben)

        folium.GeoJsonTooltip(fields=["NAME_1"],
            aliases = ["Dep't name:"],
            labels = False,
            sticky = False,
            style=("background-color: white; color: black; font-family: sans-serif; font-size: 12px; padding: 4px;")
            ).add_to(g)

        folium.GeoJsonTooltip(fields=["NAME_2"],
            aliases = ["Commune name:"],
            labels = False,
            sticky = False,
            style=("background-color: white; color: black; font-family: sans-serif; font-size: 12px; padding: 4px;")
            ).add_to(g1)

        g.add_to(m)

        g1.add_to(m)

        value1="https://www.diversityjobs.com/wp-content/uploads/2020/12/technoserve-logo.png"
        value2 = "http://www.tnsbenin.org/uploads/1/0/9/8/109816790/logo-cajulab-jpg_orig.jpg"

        FloatImage(value1, bottom=78, left=2).add_to(m)
        FloatImage(value2, bottom=87, left=2).add_to(m)

        m.add_child(folium.LayerControl())


        figure.render()

        # print('test')
        return {"map": figure}