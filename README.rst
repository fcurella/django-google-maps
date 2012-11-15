Django Google Maps
======================================

This app provides template tags for easily creating Google Maps from GeoDjango models.

Installation
~~~~~~~~~~~~

1. Add ``GOOGLE_API_KEY`` to your settings.
2. Add ``'gmaps'`` to your ``INSTALLED_APPS``.


Usage
~~~~~

::

    {% load gmaps %}
    <div id="mymap"></div>

    {% gmap_js %} {# prints out the <script> tag calling the Google Maps API #}

    {% map "mymap" object.location %}
        {% marker someobj.location %}
        {# all tags accept optional parameters that will be passed to the js constructor #}
        {% marker someobj.location "title" "'Hello, World!'" %}
        {% polygon someobj.mpoly %}
        {% polyline someobj.mpoly %}
    {% endmap %}
