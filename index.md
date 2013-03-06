---
layout: page
title: "Kurt's GameDev Excuses"
tagline: "Or, Why NotOrion Remains Unfinished"
---
{% include JB/setup %}

# What the heck is NotOrion?
NotOrion is (going to be) a galactic conquest game based on the 1996 game ["Master of Orion 2: Battle for Antares"](http://en.wikipedia.org/wiki/Master_of_Orion_II:_Battle_at_Antares). Tell me [more]({{ BASE_PATH }}/more.html)!

{% for site_post in site.posts %}{% if site_post.categories contains 'galleries' and newest_gallery == nil %}{% assign newest_gallery = site_post %}{% endif %}{% endfor %}
{% if newest_gallery %}
# <a href="{{ BASE_PATH }}{{ newest_gallery.url }}" title="{{ newest_gallery.title }}">Game Pics</a>
<p>
{% for post in site.posts reversed %}
  {% if post.categories contains 'screenshots' %}
    {% if post.tags contains newest_gallery.tags[0] %}

{% capture img_src %}{{ BASE_PATH }}/img/screenshots/{{ post.date | date: "%Y-%m-%d" }}/{{ post.tags }}/{{ post.slug }}_thumb.gif{% endcapture %}
<a href="{{ BASE_PATH }}{{ post.url }}" title="{{ post.description }}"><img alt='{{ post.description }}' src='{{ img_src }}' height='50' /></a>

    {% endif %}
  {% endif %}
{% endfor %}
</p>

* [All galleries]({{ BASE_PATH }}/categories.html#galleries-ref)
{% endif %}

# [Installation]({{ BASE_PATH }}/installation.html)
* See [installation instructions]({{ BASE_PATH }}/installation.html)

# Meta/News
<ul class="posts">
{% for post in site.posts %}
  {% unless post.categories contains 'screenshots' or post.categories contains 'galleries' %}
  <li><span>{{ post.date | date_to_string }}</span> &raquo; <a href="{{ BASE_PATH }}{{ post.url }}">{{ post.title }}</a></li>
  {% endunless %}
{% endfor %}
</ul>

# Links
<ul class="posts">
  <li><a href="http://github.com/greenmoss/NotOrion">Source code</a></li>
  <li><a href="https://github.com/greenmoss/NotOrion/issues">Report an issue</a></li>
</ul>
