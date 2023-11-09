# 2023-11-09

*** 

I'm trying to collapse all my little experiments and "software/programming studies" under a single repository and document my thought process as well as the things that have prompted me in this direction. Most of the things here will likely be dead ends, but some may end up being somewhat useful to me (this is all personal computing softare).

Doing all these in python just because it's what I have handy and it's fresher in my head, though to be honest a lot of these ideas are better implemente in other languages/tech stacks. I could potentially split this off into languages if I ever feel that way.

Today I just renamed and restructured the package and moved a couple of things from older packages. Also created some empty modules for older experiments I have to refactor and shape up a little to make useful.

*** 

`hasty` wraps multiple ideas of how I'd like objects in an application to behave by default. I'd like to be able to get a lot of default conveniences out of an object as I start a project and then - if needed - customize them or turn them off as things move along; if nothing else a lot of the ideas in `hasty` are useful for some degree of rapid prototyping.

What are these conveniences? I'm thinking of things like:
- graphical representation based on its context.
- some degree of direct manipulation (I don't have a good idea about how to accomplish this exactly right now).
- persistence not as in an ORM, but more in the transparent persistence sense.

I should elaborate more on this, but short on time right now so I'll just list a few sources of inspiration and references.

- rails/django
- smalltalk
- lisp machines
- Charles Chamberlain's [Redpear and Walnut](https://inclouds.space/blog/redpear/) (which - btw - illustrates how much easier this is to do in `ruby`.

So far I've only moved some of the display/render/presentation based bit of hasty and added a test to make sure it works on its own.
