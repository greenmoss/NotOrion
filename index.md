---
layout: page
title: "Kurt's GameDev Excuses"
tagline: "Or, Why NotOrion Remains Unfinished"
---
{% include JB/setup %}

# What the heck is NotOrion?

NotOrion is (going to be) a galactic conquest game based on the 1996 game ["Master of Orion 2: Battle for Antares"](http://en.wikipedia.org/wiki/Master_of_Orion_II:_Battle_at_Antares). Tell me [more]({{ BASE_PATH }}/more.html)!

# Links

<ul class="posts">
{% for site_post in site.posts %} 
  {% if site_post.categories contains 'galleries' and newest_gallery == nil %}
    {% assign newest_gallery = site_post %}
  {% endif %} 
{% endfor %}
{% if newest_gallery %}
  <li><a href="{{ BASE_PATH }}{{ newest_gallery.url }}">Most recent screen shots ({{ newest_gallery.date | date_to_string }})</a></li>
{% endif %}
  <li><a href="http://github.com/greenmoss/NotOrion">NotOrion on GitHub</a></li>
</ul>

# Meta/News

<ul class="posts">
  {% for post in site.posts %}
    {% unless post.categories contains 'screenshots' or post.categories contains 'galleries' %}
    <li><span>{{ post.date | date_to_string }}</span> &raquo; <a href="{{ BASE_PATH }}{{ post.url }}">{{ post.title }}</a></li>
    {% endunless %}
  {% endfor %}
</ul>
