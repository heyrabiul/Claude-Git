"""Airplanes & Flight niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "aviation"


@design("jet_plane", T)
def jet_plane(rng):
    body = chain(quad((-3.2, 0.2), (-3.4, 0.0), (-3.2, -0.2), 6), [(2.4, -0.3)], quad((2.4, -0.3), (3.4, -0.2), (3.4, 0.0), 8),
                 quad((3.4, 0.0), (3.4, 0.2), (2.4, 0.4), 8), [(-3.2, 0.2)])
    wing = poly((0.4, 0.0), (-1.0, -2.2), (-0.2, -2.2), (1.6, -0.2), closed=False)
    wing2 = poly((0.4, 0.3), (-0.6, 1.6), (0.0, 1.6), (1.4, 0.35), closed=False)
    tail = poly((-2.6, 0.2), (-3.2, 1.4), (-2.7, 1.4), (-2.0, 0.25), closed=False)
    windows = [circle(-1.6 + 0.5 * k, 0.05, 0.08, 10) for k in range(7)]
    engine = rrect(-0.6, -1.4, 0.4, -1.0, 0.2)
    clouds = [chain(arc(-2.4, -2.4, 0.4, math.pi, 0, 12), arc(-1.8, -2.2, 0.5, math.pi, 0, 12), [(-2.8, -2.4)])]
    return Design("Jet Airliner", [body, wing, wing2, tail, engine] + windows + clouds, [], T)


@design("biplane", T)
def biplane(rng):
    body = chain(quad((-3.0, 0.2), (0, 0.6), (2.0, 0.4), 20), [(2.4, 0.0)], quad((2.0, -0.4), (0, -0.4), (-3.0, 0.0), 20), [(-3.0, 0.2)])
    wings = [rrect(-0.6, 1.4, 1.4, 1.7, 0.1), rrect(-0.6, -0.8, 1.4, -0.5, 0.1)]
    struts = [[(-0.3, -0.5), (-0.3, 1.4)], [(1.1, -0.5), (1.1, 1.4)], [(-0.3, -0.5), (1.1, 1.4)]]
    prop = [lens((2.5, 0.0), (2.5, 1.0), 0.3), lens((2.5, 0.0), (2.5, -1.0), 0.3)]
    tail = poly((-2.6, 0.2), (-3.0, 1.0), (-2.4, 1.0), (-2.0, 0.3), closed=False)
    pilot = arc(0.6, 0.55, 0.3, 0, math.pi, 12)
    wheels = [circle(0.6, -1.5, 0.3, 20), [(0.4, -0.4), (0.6, -1.2)]]
    return Design("Biplane", [body, tail, pilot] + wings + struts + prop + wheels, [], T)


@design("helicopter", T)
def helicopter(rng):
    cabin = chain(cubic((-1.2, -1.0), (-1.4, 1.2), (1.4, 1.4), (1.8, 0.0), 40), quad((1.8, 0.0), (1.6, -1.0), (-1.2, -1.0), 20))
    window = chain(quad((0.2, 0.2), (0.4, 1.0), (1.2, 0.8)), quad((1.2, 0.8), (1.6, 0.1), (0.2, 0.2)))
    tail = poly((-1.2, 0.0), (-3.4, 0.4), (-3.4, 0.1), (-1.2, -0.4), closed=False)
    tail_rotor = circle(-3.4, 0.25, 0.45, 30)
    mast = [(0.2, 1.1), (0.2, 1.6)]
    rotor = [(-2.6, 1.6), (3.0, 1.6)]
    skids = [[(-1.0, -1.6), (2.0, -1.6)], [(-0.4, -1.0), (-0.6, -1.6)], [(1.0, -1.0), (1.2, -1.6)]]
    return Design("Helicopter", [cabin, window, tail, tail_rotor, mast, rotor] + skids, [], T)


@design("parachute", T)
def parachute(rng):
    canopy = chain(arc(0, 0.6, 2.6, math.radians(10), math.radians(170), 80), *[arc(x, 1.05, 0.51, math.pi, 2 * math.pi, 12) for x in (-2.04, -1.02, 0.0, 1.02, 2.04)])
    panels = [quad((0, 3.2), (x * 0.5, 2.2), (x, 1.05)) for x in (-1.53, -0.51, 0.51, 1.53)]
    lines_ = [[(x, 1.05), (0, -1.6)] for x in (-2.55, -1.02, 1.02, 2.55)]
    person = [circle(0, -1.9, 0.3, 20), [(0, -2.2), (0, -3.0)], [(-0.5, -2.4), (0.5, -2.4)], [(0, -3.0), (-0.3, -3.4)], [(0, -3.0), (0.3, -3.4)]]
    return Design("Parachute", [canopy] + panels + lines_ + person, [], T)


@design("paper_plane", T)
def paper_plane(rng):
    plane = poly((2.8, 1.6), (-2.8, 0.2), (-0.6, -0.4))
    fold = [(2.8, 1.6), (-0.6, -0.4), (-0.4, -1.4), (0.6, -0.1)]
    trail = [(-3.2 + 0.1 * k, -1.2 - 0.6 * math.sin(k / 30 * 2 * math.pi)) for k in range(31)]
    loop = spiral(-1.6, -2.0, 0.1, 0.6, 1.0, 40)
    return Design("Paper Plane", [plane, fold, trail, loop], [], T)


@design("control_tower", T)
def control_tower(rng):
    shaft = poly((-0.6, -3.0), (-0.4, 1.0), (0.4, 1.0), (0.6, -3.0), closed=False)
    cab = poly((-1.4, 1.0), (-1.8, 2.2), (1.8, 2.2), (1.4, 1.0))
    roof = rect(-1.6, 2.2, 1.6, 2.5)
    windows = [[(x, 1.15), (x * 1.25, 2.05)] for x in (-0.7, 0.0, 0.7)]
    antenna = [[(0, 2.5), (0, 3.4)], circle(0, 3.5, 0.12, 10)]
    door = rect(-0.25, -3.0, 0.25, -2.4)
    beacon = [arc(0, 3.5, r, math.radians(-30), math.radians(30), 10) for r in (0.5, 0.8)]
    return Design("Control Tower", [shaft, cab, roof, door] + windows + antenna + beacon, [], T)


@design("blimp", T)
def blimp(rng):
    envelope = ellipse(0, 0.6, 3.0, 1.2, 160)
    fins = [poly((-2.6, 1.0), (-3.4, 1.8), (-3.0, 0.6), closed=False), poly((-2.6, 0.2), (-3.4, -0.6), (-3.0, 0.6), closed=False)]
    gondola = rrect(-0.8, -1.1, 0.8, -0.5, 0.15)
    hangers = [[(-0.6, -0.5), (-0.6, -0.4)], [(0.6, -0.5), (0.6, -0.4)]]
    stripes = [quad((-2.2, 1.4), (0, 1.8), (2.2, 1.4)), quad((-2.6, 0.4), (0, 0.2), (2.6, 0.4))]
    return Design("Airship", [envelope, gondola] + fins + hangers + stripes, [], T)


@design("seaplane", T)
def seaplane(rng):
    body = chain(quad((-2.6, 0.6), (0, 1.1), (2.2, 0.6), 20), quad((2.2, 0.6), (2.6, 0.3), (2.2, 0.1), 8), quad((2.2, 0.1), (0, 0.0), (-2.6, 0.4), 20))
    wing = rrect(-0.8, 1.2, 1.4, 1.45, 0.1)
    struts = [[(-0.4, 1.2), (-0.4, 0.7)], [(1.0, 1.2), (1.0, 0.7)]]
    floats = [rrect(-1.6, -0.9, 1.8, -0.6, 0.15), [(-0.6, -0.6), (-0.4, 0.05)], [(1.0, -0.6), (1.0, 0.05)]]
    tail = poly((-2.2, 0.55), (-2.8, 1.4), (-2.3, 1.4), (-1.8, 0.7), closed=False)
    prop = [[(2.6, -0.3), (2.6, 0.9)]]
    water = [wave(-3.2, 3.2, -1.2, 0.1, 6, 100)]
    return Design("Seaplane", [body, wing, tail] + struts + floats + prop + water, [], T)
