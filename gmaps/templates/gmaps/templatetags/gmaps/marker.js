new google.maps.Marker({
      position: new google.maps.LatLng({{ latitude }}, {{ longitude }})
      {% include "gmaps/templatetags/gmaps/kwargs.js" %}
  });