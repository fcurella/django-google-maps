new google.maps.Polygon({
    paths: [
    {% for line in coords %}
    {% for point in line %}
        new google.maps.LatLng({{ point.1 }}, {{ point.0 }}){% if not forloop.last %},{% endif %}
    {% endfor %}
    {% endfor %}
    ]
    {% include "gmaps/templatetags/gmaps/kwargs.js" %}
  });