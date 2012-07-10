new google.maps.Marker({
      position: new google.maps.LatLng({{ latitude }}, {{ longitude }})
      {% include "quakeparser/templatetags/gmaps/kwargs.js" %}
  });