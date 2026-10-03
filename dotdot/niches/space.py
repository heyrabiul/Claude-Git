"""Outer Space niche."""
import math

from ._kit import *  # noqa: F401,F403  (shared drawing kit)

T = "space"


@design("saturn", T)
def saturn(rng):
    planet = circle(0, 0, 1.6, 140)
    ring_outer = ellipse(0, 0, 2.9, 0.75, 120, rot=-0.2)
    ring_inner = ellipse(0, 0, 2.2, 0.5, 100, rot=-0.2)
    bands = [arc(0, 2.4, 2.6, math.radians(240), math.radians(300), 30), arc(0, -2.4, 2.6, math.radians(60), math.radians(120), 30)]
    stars_ = [star(x, y, 0.25) for x, y in [(-2.6, 2.0), (2.4, 2.2), (-2.2, -2.2)]]
    return Design("Ringed Planet", [planet, ring_outer, ring_inner] + bands + stars_, [], T)


@design("astronaut", T)
def astronaut(rng):
    helmet = circle(0, 1.8, 1.1, 100)
    visor = rrect(-0.75, 1.25, 0.75, 2.35, 0.4)
    body = rrect(-1.0, -1.4, 1.0, 0.75, 0.4)
    pack = rect(-0.5, -0.5, 0.5, 0.3)
    arms = [tube([(-1.0, 0.4), (-1.9, -0.4), (-1.7, -1.2)], 0.5), tube([(1.0, 0.4), (1.9, 1.0), (2.3, 1.8)], 0.5)]
    legs = [rect(-0.9, -2.8, -0.15, -1.4), rect(0.15, -2.8, 0.9, -1.4)]
    flag = [[(2.4, 1.8), (2.4, 3.4)], rect(2.4, 2.6, 3.4, 3.4)]
    return Design("Astronaut", [helmet, visor, body, pack] + arms + legs + flag, [], T)


@design("crescent_moon", T)
def crescent_moon(rng):
    outer = arc(0, 0, 2.2, math.radians(70), math.radians(290), 120)
    inner = arc(0.9, 0.0, 1.85, math.radians(115), math.radians(245), 100)
    moon = chain(outer, inner[::-1])
    craters = [circle(-1.3, 0.6, 0.3, 24), circle(-1.6, -0.5, 0.2, 18), circle(-0.9, -1.4, 0.25, 20)]
    stars_ = [star(x, y, r) for x, y, r in [(1.6, 1.4, 0.4), (2.4, -0.4, 0.3), (1.2, -1.8, 0.25)]]
    face = [arc(-1.1, 0.0, 0.25, math.radians(200), math.radians(340), 10)]
    return Design("Crescent Moon", [moon] + craters + stars_ + face, [], T)


@design("ufo", T)
def ufo(rng):
    dome = chain(arc(0, 0.5, 1.0, 0, math.pi, 40), [(1.0, 0.5)])
    saucer = ellipse(0, 0.3, 2.6, 0.6, 140)
    lights = [circle(x, 0.15, 0.15, 14) for x in (-1.6, -0.8, 0.0, 0.8, 1.6)]
    beam = poly((-0.8, -0.3), (-1.8, -3.0), (1.8, -3.0), (0.8, -0.3), closed=False)
    cow = [ellipse(0, -2.2, 0.5, 0.3, 30), [(-0.3, -2.45), (-0.3, -2.7)], [(0.3, -2.45), (0.3, -2.7)]]
    alien = [circle(0, 0.95, 0.3, 24)]
    return Design("Flying Saucer", [dome, saucer, beam] + lights + cow + alien, [], T)


@design("satellite", T)
def satellite(rng):
    body = rect(-0.6, -0.6, 0.6, 0.6)
    panels = [rect(-3.2, -0.5, -1.0, 0.5), rect(1.0, -0.5, 3.2, 0.5)]
    grid = [[(x, -0.5), (x, 0.5)] for x in (-2.65, -2.1, -1.55, 1.55, 2.1, 2.65)]
    arms = [[(-1.0, 0), (-0.6, 0)], [(0.6, 0), (1.0, 0)]]
    dish = [arc(0, 1.5, 0.7, math.radians(200), math.radians(340), 20), [(0, 0.6), (0, 1.1)]]
    signal = [arc(0, 1.0, r, math.radians(60), math.radians(120), 12) for r in (1.3, 1.7, 2.1)]
    return Design("Satellite", [body] + panels + grid + arms + dish + signal, [], T)


@design("comet", T)
def comet(rng):
    head = circle(1.8, 1.2, 0.7, 60)
    tails = [quad((1.3, 1.6), (-0.5, 1.2), (-3.0, 2.4)), quad((1.2, 1.2), (-0.6, 0.4), (-3.2, 0.6)),
             quad((1.4, 0.7), (-0.2, -0.4), (-2.6, -1.2))]
    stars_ = [star(x, y, r) for x, y, r in [(-1.0, -2.0, 0.35), (2.6, -1.6, 0.3), (-2.6, 2.9, 0.2), (0.4, 2.8, 0.25)]]
    planet = circle(2.4, -2.6, 0.5, 40)
    return Design("Shooting Comet", [head, planet] + tails + stars_, [], T)


@design("telescope", T)
def telescope(rng):
    tube_ = poly((-2.2, 0.0), (1.8, 1.6), (2.2, 0.8), (-1.9, -0.6))
    lens_ = ellipse(2.0, 1.2, 0.22, 0.45, 30, rot=0.38)
    eyepiece = rect(-2.6, -0.4, -2.1, 0.0)
    tripod = [[(0, 0.5), (-1.2, -2.8)], [(0, 0.5), (1.2, -2.8)], [(0, 0.5), (0.1, -2.8)]]
    stars_ = [star(x, y, r) for x, y, r in [(2.6, 2.8, 0.35), (1.0, 3.0, 0.25), (-1.4, 2.4, 0.3)]]
    return Design("Telescope", [tube_, lens_, eyepiece] + tripod + stars_, [], T)


@design("alien", T)
def alien(rng):
    head = chain(cubic((0, -0.6), (-2.0, 0.0), (-1.8, 2.8), (0, 2.8), 50), cubic((0, 2.8), (1.8, 2.8), (2.0, 0.0), (0, -0.6), 50))
    eyes_ = [ellipse(-0.6, 1.2, 0.45, 0.6, 40, rot=0.4), ellipse(0.6, 1.2, 0.45, 0.6, 40, rot=-0.4)]
    mouth = arc(0, 0.3, 0.4, math.radians(210), math.radians(330), 14)
    ants = [quad((-0.6, 2.6), (-1.0, 3.4), (-1.4, 3.6)), quad((0.6, 2.6), (1.0, 3.4), (1.4, 3.6))]
    tips = [circle(-1.5, 3.65, 0.15, 14), circle(1.5, 3.65, 0.15, 14)]
    body = chain(quad((-0.5, -0.5), (-0.9, -2.0), (-0.6, -2.6)), [(0.6, -2.6)], quad((0.9, -2.0), (0.5, -0.5), (0.5, -0.5)))
    return Design("Friendly Alien", [head, mouth, body] + eyes_ + ants + tips, [eye(-0.55, 1.25, 0.15), eye(0.55, 1.25, 0.15)], T)


@design("earth", T)
def earth(rng):
    globe = circle(0, 0, 2.2, 160)
    lands = [chain(cubic((-1.4, 1.2), (-0.6, 1.8), (0.2, 1.2), (-0.2, 0.4), 20), cubic((-0.2, 0.4), (-0.6, -0.2), (-1.6, 0.0), (-1.4, 1.2), 20)),
             chain(cubic((0.6, 0.0), (1.6, 0.4), (1.8, -0.8), (1.0, -1.4), 20), cubic((1.0, -1.4), (0.4, -1.2), (0.2, -0.4), (0.6, 0.0), 20)),
             chain(cubic((-1.2, -1.0), (-0.6, -0.8), (-0.4, -1.6), (-0.9, -1.8), 15), quad((-0.9, -1.8), (-1.4, -1.6), (-1.2, -1.0), 10))]
    orbit = ellipse(0, 0, 3.2, 0.9, 140, rot=0.35)
    moon_ = circle(2.9, 1.6, 0.35, 30)
    return Design("Planet Earth", [globe, orbit, moon_] + lands, [], T)
