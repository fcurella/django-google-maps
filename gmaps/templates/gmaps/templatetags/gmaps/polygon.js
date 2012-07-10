new google.maps.Polygon({
    paths: [
    {% for point in coords %}
        new google.maps.LatLng({{ point.1 }}, {{ point.0 }}){% if not forloop.last %},{% endif %}
    {% endfor %}
    ]
    {% include "quakeparser/templatetags/gmaps/kwargs.js" %}
  });