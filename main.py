from logreporter import LogReporter
import sys
import argparse

import curses

import time
import subprocess
import select

import apache_log_parser
from apache_log_parser import LineDoesntMatchException

import collections
from collections import deque

import datetime


def c_main(stdscr: 'curses._CursesWindow', log_file, alert_window, alert_threshold, stat_window) -> int:
    #the use of sh.tail will limit this appliation to only working on *nix systems with the tail command
    f = subprocess.Popen(['tail','-F', log_file], stdout=subprocess.PIPE )
    p = select.poll()
    p.register(f.stdout)

    log_parser = apache_log_parser.make_parser('%h %u %l %t "%r" %s %B')

    size_of_top_data = 7

    #-1 required to keep the bottom line of the terminal for the curses and prevent curses exception
    number_of_logs_to_show = curses.LINES - size_of_top_data -1
    
    display_log_queue = collections.deque([],number_of_logs_to_show)
    
    #set log retention length to alter window + stat window to ensure we always have the data we need
    #but don't introduce any memory leaks
    reporter = LogReporter(alert_window + stat_window)
    stats = {}

    stdscr.nodelay(True) #prevent blocking input

    
    current_state = 'Nominal'
    alert_string = ''
    current_window = ''
    requests_per_sec_in_alert_window = 0
    #main process loop
    while True:
        now = datetime.datetime.now()
        if now.second % stat_window == 0:
            current_window = now.strftime("%H:%M:%S") + ' - ' + ( now - datetime.timedelta(seconds=stat_window) ).strftime('%H:%M:%S')
            stats = reporter.getStatsForWindow(stat_window)

            requests_per_sec_in_alert_window = reporter.getRequestPerSecondForWindow(alert_window)
            if requests_per_sec_in_alert_window >= alert_threshold:
                current_state = 'ALERT'
                alert_string = f" - hits = {requests_per_sec_in_alert_window}, triggered at {now.strftime('%H:%M:%S')}"                
            elif current_state == 'ALERT':
                current_state = "RECOVERED"
                alert_string = ''
            else:
                current_state = 'Nominal'

            reporter.pruneLogs()

        #render data
        stdscr.clear()
        title = "HTTP Log monitor - press any key to exit"
        title_location = int((curses.COLS / 2) - ( len(title) /2 ))
        stdscr.addstr(0,title_location, title)
        stdscr.addstr(1,0, f"Stats for window: {current_window}")
        stdscr.addstr(2,0, f"STATUS: {current_state}")
        if current_state == 'ALERT':
            stdscr.addstr(2, 14, alert_string)
        line_index = 3
        
        for key in stats:
            display_string = f"{key}: {stats[key]}"
            stdscr.addstr(line_index, 0, display_string[:curses.COLS])
            line_index += 1
        
        for idx, log in enumerate(display_log_queue):
            stdscr.addstr(idx + size_of_top_data, 0, log[:curses.COLS])

        stdscr.refresh()

        # injest new data
        if p.poll(1): 
            try:
                log_line = f.stdout.readline()
                display_log_queue.append(log_line)
                reporter.addLog( log_parser(str(log_line)) )
            except LineDoesntMatchException:
                print(f"log found that did not match parsing: {log_line}", file=sys.stderr)
                pass

        time.sleep(0.3)    
        if stdscr.getch() != curses.ERR:
            #user input detected exit
            break
    
 
def main() -> int:
    #Default values
    #TODO: move to config file
    FILE_LOCATION = '/tmp/access.log'
    ALERT_WINDOW_LENGTH = 120
    ALERT_THRESHOLD = 10
    STAT_WINDOW_LENGTH = 10

    if len(sys.argv) > 1:
        #user submitted command line args parsing
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--file", help = "specify log file location", required = False)
        parser.add_argument("-a", "--alertwindow", help = "length in seconds of the alert window", required = False)
        parser.add_argument("-t", "--alertthreshold", help = "number of requests per second that will trigger an alert", required = False)
        parser.add_argument("-w", "--statwindow", help = "length in seconds of the window for stats. min=0, max=59", required = False)
        arguments = parser.parse_args()

        if arguments.file:
            FILE_LOCATION = arguments.file
        if arguments.alertwindow:
            ALERT_WINDOW_LENGTH = arguments.alertwinow
        if arguments.alertthreshold:
            ALERT_THRESHOLD = arguments.alertthreshold
        if arguments.statwindow:
            STAT_WINDOW_LENGTH = arguments.statwindow

    return curses.wrapper(c_main, FILE_LOCATION, ALERT_WINDOW_LENGTH, ALERT_THRESHOLD, STAT_WINDOW_LENGTH)


if __name__ == '__main__':
    exit(main())
      