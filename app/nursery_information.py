from authentication.models import Nursery
import folium
from django.utils.translation import gettext


class Nursery_LAYER:
    def __init__(self, marker_cluster):
        self.marker_cluster = marker_cluster
    def add_nursery(self):
        # variables for translation
        Commune_Name = gettext('Commune Name')
        Nursery_Owner = gettext("Nursery Owner")
        Nursery_Area = gettext("Nursery Area (ha)")
        Number_of_Plants = gettext("Number of Plants")

        # Loop through every nursery owner and add to the nursery marker popups
        for i in range(len(Nursery.objects.all())):
                    folium.Marker(location= [Nursery.objects.all()[i].latitude, Nursery.objects.all()[i].longitude],
                                rise_on_hover=True,
                                rise_offset = 250,
                                icon = folium.Icon(color="red", icon="leaf"),
                                popup=f'''
                                <div style="border: 3px solid #808080">
                                <h4 style="font-family: 'Trebuchet MS', sans-serif">{Commune_Name}: <b>{Nursery.objects.all()[i].commune}</b></h4>
                                <h5 style="font-family: 'Trebuchet MS', sans-serif">{Nursery_Owner}: <i>{Nursery.objects.all()[i].nursery_name}</i></h5>
                                <h5 style="font-family: 'Trebuchet MS', sans-serif">{Nursery_Area}: <b>{Nursery.objects.all()[i].current_area}</b></h5>
                                <h5 style="font-family: 'Trebuchet MS', sans-serif">{Number_of_Plants}: <b>{Nursery.objects.all()[i].number_of_plants}</b></h5>
                                <a href="https://www.technoserve.org/our-work/agriculture/cashew/?_ga=2.159985149.1109250972.1626437600-1387218312.1616379774"target="_blank">click link to website</a>
                                <img src="https://gumlet.assettype.com/deshdoot/import/2019/12/tripXOXO-e1558439144643.jpg?w=1200&h=750&auto=format%2Ccompress&fit=max" width="200" height="70">
                                </div>''').add_to(self.marker_cluster)

        return self.marker_cluster