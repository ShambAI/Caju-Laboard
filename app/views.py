# -*- encoding: utf-8 -*-

import folium
from django import template
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
import locale
from django.utils.translation import gettext
from django.utils.translation import activate, get_language
from app.nursery_information import Nursery_LAYER
from app.benin_republic import add_benin_republic
from app.benin_department import add_benin_department
from app.benin_commune import add_benin_commune
from app.benin_plantations import add_benin_plantation


from folium import plugins
import pandas as pd
from folium.plugins import MarkerCluster
import ee

#Google service account for the GEE geotiff
service_account = 'cajulab@benin-cajulab-web-application.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'privatekey.json')
ee.Initialize(credentials)
locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
alldept = ee.Image('users/ashamba/allDepartments_v0')

class my_home():
    

    def __init__(self):

        self.figure = folium.Figure()

    def get_context_data(self, path_link, **kwargs):

        
        # Basemap dictionary
        basemaps = {
                    'Google Maps': folium.TileLayer(
                        tiles = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                        attr = gettext('Google'),
                        name = 'Maps',
                        max_zoom =25,
                        overlay = True,
                        control = False
                    ),
                    'Google Satellite': folium.TileLayer(
                        tiles = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                        attr = 'Google',
                        name = gettext('Google Satellite'),
                        max_zoom = 25,
                        overlay = True,
                        show=False,
                        control = True
                    ),
                    'Mapbox Satellite': folium.TileLayer(
                        tiles='https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoic2hha2F6IiwiYSI6ImNrczMzNTl3ejB6eTYydnBlNzR0dHUwcnUifQ.vHqPio3Pe0PehWpIuf5QUg',
                        attr = 'Mapbox',
                        name = gettext('Mapbox Satellite'),
                        max_zoom = 25,
                        overlay = True,
                        show=False,
                        control = True
                    )
                }
        
        #Initialize map object

        m = folium.Map(
            location=[9.0, 2.4],
            zoom_start=8,
            prefer_canvas=True,
            tiles = None
        )

        m.add_child(basemaps['Google Maps'])
        m.add_child(basemaps['Google Satellite'])
        m.add_child(basemaps['Mapbox Satellite'])

        plugins.Fullscreen(position='topright', title='Full Screen', title_cancel='Exit Full Screen', force_separate_button=False).add_to(m)



       #Adding the nursery layer from the class Nursery_LAYER
        marker_cluster = MarkerCluster(name=gettext("Nursery Information"))
        Nursery_layer = Nursery_LAYER(marker_cluster).add_nursery()
        Nursery_layer.add_to(m)

        # Define a method for displaying Earth Engine image tiles on a folium map.
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
        m.add_ee_layer(zones, {'palette': "red"}, gettext('Satellite Prediction'))


        # The no boundary layer to remove shapefiles on the Benin region
        No_Boundary_layer = folium.FeatureGroup(name=gettext('No Boundary'), show=False, overlay = False)
        No_Boundary_layer.add_to(m)
        
        # Adding the shapefiles with popups for the Benin Republic region
        Benin_layer = add_benin_republic()
        Benin_layer.add_to(m)

        # Adding the shapefiles with popups for the Benin departments region
        Benin_dept_layer, dept_yieldHa = add_benin_department()
        Benin_dept_layer.add_to(m)

        # Adding the shapefiles with popups for the Benin commune region
        Benin_commune_layer = add_benin_commune()
        Benin_commune_layer.add_to(m)

        # Adding the shapefiles with popups for the Benin plantations
        Benin_plantation_layer = add_benin_plantation(path_link, dept_yieldHa)
        Benin_plantation_layer.add_to(m)
        
        #adding folium layer control for the previously added shapefiles
        m.add_child(folium.LayerControl())
        m=m._repr_html_()
        context = {'my_map': m}

        return context


@login_required(login_url="/login/")
def index(request):
   
    path_link = request.path
    home_obj = my_home()
    context = home_obj.get_context_data(path_link)
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
