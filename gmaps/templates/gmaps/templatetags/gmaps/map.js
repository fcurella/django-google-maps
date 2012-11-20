var {{ map_var }} = new google.maps.Map(document.getElementById('{{ element_id }}'), {
    center: new google.maps.LatLng({{ latitude }}, {{ longitude }}),
    mapTypeId: {{ map_type|safe }},
    zoom: {{ zoom }}{% if map_type == '"OSM"' %},
        mapTypeControlOptions: {
        mapTypeIds: ["OSM"]
    }{% endif %}
    {% include "gmaps/templatetags/gmaps/kwargs.js" %}
});
{% if map_type == '"OSM"' %}
    {{ map_var }}.mapTypes.set("OSM", osmMapType);
{% endif %}
