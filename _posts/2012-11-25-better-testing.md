---
layout: post
title: "Better Testing"
description: ""
category: 
tags: [updates]
---
{% include JB/setup %}
I have taken a stab at resurrecting automated unit testing for NotOrion. This is in the "tests" directory, currently on branch "milestone_3", which I pushed to github.

In MVC terms, the tests only cover the "model" code. As far as I know, OpenGL output is pretty much impossible to test algorithmically. I still aim to "exercise" my state/"Controller" and view code by writing tests to open windows and trigger various GUI events. That way I can at least detect fatal errors.

I also started using coverage testing with some nice html output. This was invaluable in tightening up my test code and finding unused corner cases. So I'm glad I've made the investment in figuring out how to make it work. I also enabled branch testing, though it seems to be a bit quirky about reporting some branch conditions. Maybe I'm doing it wrong...

To test, change to NotOrion directory:
* To run all tests: `nosetests`
* To get a coverage report: `shovel test_coverage`
* Use a web browser to view the html report, which is in `cover/index.html`
* To clean out all test artifacts: `shovel clean`
