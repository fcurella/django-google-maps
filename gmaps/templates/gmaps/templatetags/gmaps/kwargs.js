{% if map_var %}{% if not is_map %},
map: {{ map_var }}
{% endif %}{% endif %}
{% if kwargs %},{% endif %}
{% for k,v in kwargs.items %}{{ k|safe }}: {{ v|safe }}{% if not forloop.last%}, 
{% endif %}{% endfor %}
