import collections
import sys
import argparse

import curses

import time
import subprocess
import select

import apache_log_parser
from apache_log_parser import LineDoesntMatchException

from collections import deque

def c_main(stdscr: 'curses._CursesWindow', log_file) -> int:
    #the use of sh.tail will limit this appliation to only working on *nix systems with the tail command
    f = subprocess.Popen(['tail','-F', log_file], stdout=subprocess.PIPE )
    p = select.poll()
    p.register(f.stdout)

    log_parser = apache_log_parser.make_parser('%h %u %l %t "%r" %s %B')

    size_of_top_data = 7

    #-1 required to keep the bottom line of the terminal for the curses and prevent curses exception
    number_of_logs_to_show = curses.LINES - size_of_top_data -1
    
    display_log_queue = collections.deque([],number_of_logs_to_show)

    stdscr.nodelay(True) #prevent blocking input

    #main process loop
    while True:
        #render data
        stdscr.clear()
        stdscr.addstr(0,0, "HTTP Log monitor - press any key to exit")
        stdscr.addstr(1,0, "STATUS: Nominal")
        for idx, log in enumerate(display_log_queue):
            stdscr.addstr(idx + size_of_top_data, 0, log[:curses.COLS])

        stdscr.refresh()

        # injest new data
        if p.poll(1): 
            try:
                log_line = f.stdout.readline()
                display_log_queue.append(log_line)
                parts = log_parser(str(log_line))
            except LineDoesntMatchException:
                print(f"log found that did not match parsing: {log_line}", file=sys.stderr)
                pass

        time.sleep(1)    
        if stdscr.getch() != curses.ERR:
            #user input detected exit
            break
    
 
def main() -> int:
    #Default values
    #TODO: move to config file
    FILE_LOCATION = '/tmp/access.log'

    if len(sys.argv) > 1:
        #user submitted command line args parsing
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--file", help = "specify log file location", required = False)
        arguments = parser.parse_args()

        if arguments.file:
            FILE_LOCATION = arguments.file


    return curses.wrapper(c_main, FILE_LOCATION)


if __name__ == '__main__':
    exit(main())
      