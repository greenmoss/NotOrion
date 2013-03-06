---
layout: post
title: "Modelling the Star System View"
description: ""
category: galleries
tags: [modelling-the-star-system-view]
---
{% include JB/setup %}

This is a gallery of screenshots showing me [modelling the star system view]({{ BASE_PATH }}/2013/03/02/star-system-scenery/). Each of the images below is a thumbnail preview. Click on the preview image or description to see the full-sized image.
{% for post in site.posts reversed %}
  {% if post.categories contains 'screenshots' %}
    {% if post.tags contains 'modelling-the-star-system-view' %}

{% capture img_src %}{{ BASE_PATH }}/img/screenshots/{{ post.date | date: "%Y-%m-%d" }}/{{ post.tags }}/{{ post.slug }}_thumb.gif{% endcapture %}

<h3 id='{{ post.slug }}'><a href='{{ BASE_PATH }}{{ post.url }}'>{{ post.description }}</a></h3>

<p><a href='{{ BASE_PATH }}{{ post.url }}'><img height='{{ post.thumb_height }}' width='{{ post.thumb_width }}' alt='{{ post.description }}' src='{{ img_src }}' /></a></p>

    {% endif %}
  {% endif %}
{% endfor %}
