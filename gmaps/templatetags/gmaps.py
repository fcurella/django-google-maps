"""
{% load gmaps %}

{% gmap_js [<sensor>] %}

{% map <element_id> <center_location> [zoom <zoom>] [map_type <type>] %}
    {% marker <location> [title <title>] %}
    {% marker <location> [title <title>] %}
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
from django.core.exceptions import ImproperlyConfigured


register = template.Library()
TEMPLATE_ROOT = 'gmaps/templatetags/gmaps/'


def list_to_dict(x):
    return dict(x[i:i + 2] for i in range(0, len(x), 2))


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

    def __init__(self, nodelist, element_id, location, map_type='"roadmap"', zoom="13", **kwargs):
        self.nodelist = nodelist
        self.element_id = template.Variable(element_id)
        self.location = template.Variable(location)
        self.map_type = template.Variable(map_type)
        self.zoom = template.Variable(zoom)

        for k, v in kwargs.items():
            kwargs[k] = template.Variable(v)
        self.kwargs = kwargs

    def render(self, context):
        location = self.location.resolve(context)
        lon = location.x
        lat = location.y

        element_id = self.element_id.resolve(context)
        map_var = "%s_map" % element_id

        for k, v in self.kwargs.items():
            self.kwargs[k] = v.resolve(context)

        ctx = {
            'map_var': map_var,
            'element_id': element_id,
            'latitude': lat,
            'longitude': lon,
            'map_type': MAP_TYPES[self.map_type.resolve(context)],
            'zoom': self.zoom.resolve(context),
            'kwargs': self.kwargs
        }
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
    kwargs = list_to_dict(args)

    lon = location.x
    lat = location.y

    context.update({
        'latitude': lat,
        'longitude': lon,
        'kwargs': kwargs
    })

    return context


@register.inclusion_tag(TEMPLATE_ROOT + 'polygon.js', takes_context=True)
def polygon(context, mpoly, *args):
    """
    Given a GeoDjango mpoly fields, outputs the necessary code to generate a Polygon.
    """
    kwargs = list_to_dict(args)
    coords = mpoly.coords[0]

    context.update({
        'coords': coords,
        'kwargs': kwargs
    })
    return context


@register.inclusion_tag(TEMPLATE_ROOT + 'polyline.js', takes_context=True)
def polyline(context, mpoly, *args):
    """
    Given a GeoDjango mpoly fields, outputs the necessary code to generate a Polyline.
    """
    kwargs = list_to_dict(args)
    coords = mpoly.coords[0]

    context.update({
        'coords': coords,
        'kwargs': kwargs
    })

    return context
