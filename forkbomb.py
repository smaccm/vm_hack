#!/usr/bin/env python

import curses
from random import choice, shuffle
from time import sleep
from collections import namedtuple

Program = namedtuple('Program',
                   ['x', 'y', 'x_min', 'x_max', 'y_min', 'y_max', 'next_split'])

def sign(x):
  if x < 0:
    return -1
  elif x == 0:
    return 0
  else:
    return 1

def addchr(window, y, x, c, attr):
  try:
    window.addstr(y, x, c, attr)
  except:
    pass

def draw_program(window, y, x):
  addchr(window, y, x, '#', curses.color_pair(1) | curses.A_BOLD)
  addchr(window, y - 1, x, '#', curses.color_pair(1) | curses.A_NORMAL)
  addchr(window, y + 1, x, '#', curses.color_pair(1) | curses.A_NORMAL)
  addchr(window, y, x - 1, '#', curses.color_pair(1) | curses.A_NORMAL)
  addchr(window, y, x + 1, '#', curses.color_pair(1) | curses.A_NORMAL)
  addchr(window, y - 1, x - 1, '#', curses.color_pair(1) | curses.A_DIM)
  addchr(window, y + 1, x + 1, '#', curses.color_pair(1) | curses.A_DIM)
  addchr(window, y + 1, x - 1, '#', curses.color_pair(1) | curses.A_DIM)
  addchr(window, y - 1, x + 1, '#', curses.color_pair(1) | curses.A_DIM)

def draw_programs(window, programs):
  window.erase()

  shuffle(programs)
  for p in programs:
    try:
      draw_program(window, p.y, p.x)
    except:
      pass
  window.refresh()

def advance_program(p):
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

def move_programs(programs):
  result = []
  for p in programs:
    result.extend(advance_program(p))
  return result

def splitting_animation(window):
  my, mx = window.getmaxyx()
  programs = [Program(mx/2, 0, 0, mx, 0, my, 'x')]
  while len(programs) < my * mx:
    draw_programs(window, programs)
    programs = move_programs(programs)
    sleep(0.04)

def sparkle_animation(window):
  my, mx = window.getmaxyx()
  contrasts = [curses.A_DIM] * 4 + [curses.A_NORMAL] * 4 + [curses.A_BOLD]
  while True:
    for y in range(my):
      for x in range(mx):
        addchr(window, y, x, '#', curses.color_pair(1) | choice(contrasts))
    sleep(0.1)
    window.refresh()

def main(stdscr):
  curses.curs_set(False)
  curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

  splitting_animation(stdscr)
  sparkle_animation(stdscr)
  sleep(1000)

curses.wrapper(main)
