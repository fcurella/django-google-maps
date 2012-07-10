{% if map_var %},
map: {{ map_var }}
{% endif %}
{% if kwargs %},{% endif %}
{% for k,v in kwargs.items %}{{k}}: {{v}}{% if not forloop.last%},{% endif %}{% endfor %}
