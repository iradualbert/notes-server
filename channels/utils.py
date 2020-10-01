import json
from django.db.models import Q
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Channel, Product

def parse_geom(lat, lng):
   geom = Point([float(x) for x in (lng, lat)], srid=4326)
   return geom

def get_lat_lng(geom):
    location = json.loads(geom.geojson)
    lng = location.get('coordinates')[0]
    lat = location.get('coordinates')[1]
    return {
        "lat": lat,
        "lng": lng
    }

def get_ip_address(request):
    ip = str()
    try:
        x_forward = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forward:
            ip = x_forward.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
    except:
        pass
    return ip

# nearby and popular 
def recommend_channels(user, offset=0, limit=9, location=None, ):
    to_fetch = limit + 1
    channels = []
    more_available = False
    if user.is_authenticated:
        profile = user.profile
        geom = profile.geom
        if geom:
            channels = Channel.objects.filter(Q(geom__distance_lt=(geom, D(m=2500)))
            ).annotate(
                distance=Distance('geom', geom)[offset:offset+to_fetch]
            )
        else:
            country = profile.country
            channels = Channel.objects.filter(country=country)[offset:offset+to_fetch]
        more_available = len(channels) == to_fetch
        return channels[0:limit], more_available
        
    
    else:
        return [], False

## recommend popular and nearby products
def popular_products(request, offset=0, limit=5):
    to_fetch = limit + 1
    products = []
    more_available = False
    products = Product.objects.filter(
        link__isnull=False
        ).order_by('views', 'totat_reviews', 'average_rate')[offset:offset+to_fetch]
    return products, more_available

    