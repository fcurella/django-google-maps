"""
{% load gmaps %}

{% gmap_js [<sensor>] %}

{% map <element_id> <center_location> ["zoom" <zoom>] ["map_type" <type>] %}
    {% marker <location> ["title" <title>] %}
    {% marker <location> ["title" <title>] %}
    {% polygon <mpoly> %}
{% endmap %}
"""

"""
function initialize() {
  var map = new google.maps.Map(document.getElementById('map-canvas'), {
    center: new google.maps.LatLng(37.4419, -122.1419),
    zoom: 13,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  });

  var marker = new google.maps.Marker({
      position: new google.maps.LatLng(37.4440, -122.1419),
      map: map,
      title:"Hello World!"
  });
  var marker2 = new google.maps.Marker({
      position: new google.maps.LatLng(37.4460, -122.1300),
      map: map,
      title:"Hello World!2"
  });
  var marker3 = new google.maps.Marker({
      position: new google.maps.LatLng(37.4500, -122.1500),
      map: map,
      title:"Hello World!3"
  });

  var triangleCoords = [
    new google.maps.LatLng(37.4440, -122.1419),
    new google.maps.LatLng(37.4460, -122.1300),
    new google.maps.LatLng(37.4500, -122.1500),
    new google.maps.LatLng(37.4440, -122.1419)
  ];

  var triangle = new google.maps.Polygon({
    paths: triangleCoords,
    strokeColor: "#FF0000",
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: "#FF0000",
    fillOpacity: 0.35,
    map: map
  });

}

"""

from django import template
from django.conf import settings
from django.contrib.gis.geos import fromstr
from django.core.exceptions import ImproperlyConfigured

from django.template.defaultfilters import slugify
from copy import copy


register = template.Library()
TEMPLATE_ROOT = 'gmaps/templatetags/gmaps/'


def list_to_dict(x):
    return dict([x[i:i + 2] for i in range(0, len(x), 2)])


def ensure_geometry(geomtry_or_wkt):
    if hasattr(geomtry_or_wkt, 'x') and hasattr(geomtry_or_wkt, 'y'):
        return geomtry_or_wkt
    return fromstr(geomtry_or_wkt)


@register.inclusion_tag(TEMPLATE_ROOT + 'gmap_js.html')
def gmap_js(sensor=False):
    api_key = getattr(settings, 'GOOGLE_API_KEY', None)
    if api_key is None:
        raise ImproperlyConfigured(u'You must define GOOGLE_API_KEY in your settings.')

    return {
        'sensor': sensor,
        'GMAPS_API_KEY': api_key,
    }


MAP_TYPES = {
    'hybrid': 'google.maps.MapTypeId.HYBRID',
    'roadmap': 'google.maps.MapTypeId.ROADMAP',
    'satellite': 'google.maps.MapTypeId.SATELLITE',
    'terrain': 'google.maps.MapTypeId.TERRAIN',
}


class MapNode(template.Node):
    template_name = TEMPLATE_ROOT + 'map.js'
    template_name_handler = TEMPLATE_ROOT + 'load_handler.js'

    def __init__(self, nodelist, element_id, location, map_type='roadmap', zoom=13, **kwargs):
        self.nodelist = nodelist
        self.element_id = template.Variable(element_id)
        self.location = template.Variable(location)
        self.map_type = template.Variable(map_type)
        if 'zoom' in kwargs:
            self.zoom = template.Variable(kwargs.pop('zoom'))
        else:
            self.zoom = zoom

        if 'map_type' in kwargs:
            self.map_type = template.Variable(kwargs.pop('map_type'))
        else:
            self.map_type = map_type

        if 'map_var' in kwargs:
            self.map_var = template.Variable(kwargs.pop('map_var'))
        else:
            self.map_var = None

        self.kwargs = dict([(template.Variable(k), template.Variable(v)) for k, v in kwargs.items()])

    def render(self, context):
        location = ensure_geometry(self.location.resolve(context))
        lon = location.x
        lat = location.y

        element_id = self.element_id.resolve(context)
        if self.map_var is not None:
            map_var = self.map_var.resolve(context)
        else:
            map_var = slugify(element_id).replace('-', '_')

        if isinstance(self.zoom, template.Variable):
            zoom = self.zoom.resolve(context)
        else:
            zoom = self.zoom

        if isinstance(self.map_type, template.Variable):
            map_type = self.map_type.resolve(context)
        else:
            map_type = self.map_type

        _kwargs = {}
        for k, v in self.kwargs.items():
            _kwargs[k.resolve(context)] = v.resolve(context)

        ctx = copy(context)
        ctx.update({
            'is_map': True,
            'map_var': map_var,
            'element_id': element_id,
            'latitude': lat,
            'longitude': lon,
            'map_type': MAP_TYPES[map_type],
            'zoom': zoom,
            'kwargs': _kwargs
        })
        output = template.loader.render_to_string(self.template_name, ctx)
        context['map_var'] = map_var
        output += self.nodelist.render(context)

        return template.loader.render_to_string(self.template_name_handler, {'output': output})


@register.tag
def map(parser, token):
    bits = token.split_contents()[1:]
    args = bits[:2]
    kwargs = list_to_dict(bits[2:])
    nodelist = parser.parse(('endmap',))
    parser.delete_first_token()
    return MapNode(nodelist, *args, **kwargs)


@register.inclusion_tag(TEMPLATE_ROOT + 'marker.js', takes_context=True)
def marker(context, location, *args):
    """
    Outputs the necessary code to put a marker on the map.

    {% marker <location> [options] %}


    """
    _kwargs = list_to_dict(args)

    location = ensure_geometry(location)
    lon = location.x
    lat = location.y

    context.update({
        'latitude': lat,
        'longitude': lon,
        'kwargs': _kwargs
    })
    return context


@register.inclusion_tag(TEMPLATE_ROOT + 'polygon.js', takes_context=True)
def polygon(context, mpoly, *args):
    """
    Given a GeoDjango mpoly fields, outputs the necessary code to generate a Polygon.
    """
    _kwargs = list_to_dict(args)
    mpoly = ensure_geometry(mpoly)
    coords = mpoly.coords

    context.update({
        'coords': coords,
        'kwargs': _kwargs
    })
    return context


@register.inclusion_tag(TEMPLATE_ROOT + 'polyline.js', takes_context=True)
def polyline(context, mpoly, *args):
    """
    Given a GeoDjango mpoly fields, outputs the necessary code to generate a Polyline.
    """
    _kwargs = list_to_dict(args)
    mpoly = ensure_geometry(mpoly)
    coords = mpoly.coords

    context.update({
        'coords': coords,
        'kwargs': _kwargs
    })

    return context
