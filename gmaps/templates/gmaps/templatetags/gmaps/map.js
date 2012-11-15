var {{ map_var }} = new google.maps.Map(document.getElementById('{{ element_id }}'), {
    center: new google.maps.LatLng({{ latitude }}, {{ longitude }}),
    mapTypeId: {{ map_type }},
    zoom: {{ zoom }}
    {% include "gmaps/templatetags/gmaps/kwargs.js" %}
});
