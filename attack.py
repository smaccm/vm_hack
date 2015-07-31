#!/usr/bin/env python

import sys
import curses
import re
import os
from time import sleep
from mmap import mmap
from subprocess import call

WIDTH = 120
UPPER_HEIGHT = 10
LOWER_HEIGHT = 35
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

DEV_NULL = open(os.devnull, 'w')

def flush():
    # Recompiling seems to be enough to flush out the VM cache
    call(["make", "clean"], stdout=DEV_NULL)
    call(["make"], stdout=DEV_NULL)

flush()
dev_mem_fd = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)
mem = mmap(dev_mem_fd, 2 * PAGE_SIZE, offset=BASE_ADDR)

def main(stdscr):
  curses.curs_set(False)
  curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)
  GREEN = curses.color_pair(1)
  curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
  RED = curses.color_pair(2)

  upper_box = curses.newwin(UPPER_HEIGHT, WIDTH, 0, 0)
  upper_box.border(0)
  upper_box.addstr(0, 1, "Status")
  upper = curses.newwin(UPPER_HEIGHT - 2, WIDTH - 2, 1, 1)
  upper.scrollok(True)

  lower_box = curses.newwin(LOWER_HEIGHT, WIDTH, UPPER_HEIGHT, 0)
  lower_box.border(0)
  lower_box.addstr(0, 1, "Memory")
  lower = curses.newwin(LOWER_HEIGHT - 2, WIDTH - 2, UPPER_HEIGHT + 1, 1)
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

  for row in range(0, 2 * PAGE_SIZE / BYTES_PER_ROW):
    row_addr = BASE_ADDR + BYTES_PER_ROW * row
    lower.addstr("0x%08x: " % row_addr)

    for col in range(0, BYTES_PER_ROW):
      addr = row_addr + col;
      lower.addstr("0x%02x " % ord(mem[addr - BASE_ADDR]))

    lower.refresh()
    sleep(0.02)

    middle = (LOWER_HEIGHT - 3) / 2
    middle_addr = row_addr - (LOWER_HEIGHT - 3 - middle) * BYTES_PER_ROW
    middle_addrs = range_length(middle_addr, BYTES_PER_ROW)
    
    def highlight_and_modify(block, text, modify):
      if block[0] in middle_addrs:
        py, px = lower.getyx()
        upper.addstr("Found encryption " + text + ": ")
        upper.refresh()

        lower.addstr(middle, 12 + 5 * BYTES_PER_ROW + 2, text + " detected", curses.A_BOLD)
        
        # Highlight block
        for block_addr in block:
          offset = block_addr - middle_addr
          hy = middle
          while (offset >= BYTES_PER_ROW):
            offset -= BYTES_PER_ROW
            hy += 1
          hx = 12 + 5 * offset

          upper.addstr("0x%02x " % ord(mem[block_addr - BASE_ADDR]))
          upper.refresh()
          length = 5
          if (offset == BYTES_PER_ROW - 1 or block_addr == block[-1]):
            length = 4
          lower.chgat(hy, hx, length, GREEN)
          lower.refresh()
          sleep(0.1)

        upper.addstr("\n")
        upper.refresh()
        stdscr.getch()

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
            hx = 12 + 5 * offset
            mod_text = "0x00 "
            if (offset == BYTES_PER_ROW - 1 or block_addr == block[-1]):
              mod_text = "0x00"

            lower.addstr(hy, hx, mod_text, RED)
            lower.refresh()
            sleep(0.25)

          lower.addstr(middle, 12 + 5 * BYTES_PER_ROW + 2, text + " modified", curses.A_BOLD)
          lower.refresh()
          # Python can't seem to modify /dev/mem through the mmap, so use rw_mem
          call(["./rw_mem", "-a", "0x%08x" % block[0], "-s", str(len(block)), "-w", "-h", "0x00"])
          flush()
          stdscr.getch()

        lower.move(py, px)

    highlight_and_modify(KEY1, "key", False)
    highlight_and_modify(KEY2, "key", False)
    highlight_and_modify(SALT1, "salt", True)
    highlight_and_modify(SALT2, "salt", True)
    highlight_and_modify(NONCE1, "nonce", True)
    highlight_and_modify(NONCE2, "nonce", True)

    lower.addstr("\n")

  upper.addstr("Finished (press q to quit)")
  upper.refresh()
  flush()
  while (stdscr.getch() != ord('q')):
    pass

curses.wrapper(main)
