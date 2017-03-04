#!/usr/bin/env python

import curses
from random import choice
from time import sleep
from collections import namedtuple

Point = namedtuple('Point',
                   ['x', 'y', 'x_min', 'x_max', 'y_min', 'y_max', 'next_split'])

def sign(x):
  if x < 0:
    return -1
  elif x == 0:
    return 0
  else:
    return 1

def draw_points(window, points):
  window.erase()
  my, mx = window.getmaxyx()

  contrasts = [curses.A_BOLD]
  if len(points) > 40:
    contrasts = [curses.A_DIM, curses.A_NORMAL, curses.A_BOLD]

  for p in points:
    if 0 <= p.x < mx and 0 <= p.y < my:
      try:
        window.addstr(p.y, p.x, '#',
                      curses.color_pair(1) | choice(contrasts))
      except:
        pass
  window.refresh()

def advance_point(p):
  # Try to move towards center
  x_center = (p.x_min + p.x_max) / 2
  y_center = (p.y_min + p.y_max) / 2
  x_update = p.x + sign(x_center - p.x)
  y_update = p.y + sign(y_center - p.y)
  if p.x != x_update or p.y != y_update:
    return [p._replace(x=x_update, y=y_update)]

  # Destination reached, perform split
  if p.next_split == 'x':
    q1 = p._replace(x_max=x_center, next_split='y')
    q2 = p._replace(x_min=x_center, next_split='y')
  else:
    q1 = p._replace(y_max=y_center, next_split='x')
    q2 = p._replace(y_min=y_center, next_split='x')
  if q1 != q2:
    return [q1, q2]
  else:
    return []


def move_points(points):
  result = []
  for p in points:
    result.extend(advance_point(p))
  return result

def main(stdscr):
  curses.curs_set(False)
  my, mx = stdscr.getmaxyx()
  curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

  points = [Point(mx/2, 0, 0, mx, 0, my, 'x')]
  for _ in range(140):
    draw_points(stdscr, points)
    points = move_points(points)
    sleep(0.04)
  sleep(1000)

curses.wrapper(main)
