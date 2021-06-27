import curses
import sys
import time
import subprocess
import select

import apache_log_parser
from apache_log_parser import LineDoesntMatchException

import collections
from collections import deque

import datetime

from src import logreporter

class HttpLogParser:

    def c_main(stdscr: 'curses._CursesWindow', log_file, alert_window, alert_threshold, stat_window):
        #tail subprocess and log parser setup
        #the use of sh.tail will limit this appliation to only working on *nix systems with the tail command
        f = subprocess.Popen(['tail','-F', log_file], stdout=subprocess.PIPE )
        p = select.poll()
        p.register(f.stdout)
        log_parser = apache_log_parser.make_parser('%h %u %l %t "%r" %s %B')
        
        #reporter internal data structure setup
        #set log retention length to alter_window + stat_window to ensure we always have the data we need
        #but don't introduce any memory leaks
        reporter = logreporter.LogReporter(alert_window + stat_window)
        stats = {} #initialize stats reporting object

        #curses display setup
        #-1 required to keep the bottom line of the terminal for the curses and prevent curses exception
        size_of_top_data = 8
        number_of_logs_to_show = curses.LINES - size_of_top_data -1
        display_log_queue = collections.deque([],number_of_logs_to_show)
        current_state = 'Nominal'
        alert_string = ''
        current_window = ''
        stdscr.nodelay(True) #prevent blocking input

        #main process loop
        while True:
            now = datetime.datetime.now()
            if now.second % stat_window == 0: # only prcoess new stats per time window
                current_window = now.strftime("%H:%M:%S") + ' - ' + ( now - datetime.timedelta(seconds=stat_window) ).strftime('%H:%M:%S')
                stats = reporter.getStatsForWindow(stat_window)

                #TODO explore option of alert reporting in every loop for faster notification of alert
                alertstate = reporter.isInAlertState(alert_window, alert_threshold)
                if alertstate[0]:
                    current_state = 'ALERT'
                    alert_string = f" High traffic generated an alert - hits = {alertstate[1]}, triggered at {now.strftime('%H:%M:%S')}"                
                elif current_state == 'ALERT':
                    current_state = "RECOVERED"
                    alert_string = ''
                else:
                    current_state = 'Nominal'

                reporter.pruneLogs()

            #render data
            stdscr.clear()
            title = f"HTTP Log monitor - press any key to exit"
            title_location = int((curses.COLS / 2) - ( len(title) /2 ))
            stdscr.addstr(0,title_location, title)
            stdscr.addstr(1,0, f"Stats for window: {current_window}")
            stdscr.addstr(2,0, f"STATUS: {current_state}")
            if current_state == 'ALERT':
                stdscr.addstr(2, 14, alert_string)
            line_index = 3
            
            for key in stats:
                name = key.replace("_", " ")
                display_string = f"{name}: {stats[key]}"
                stdscr.addstr(line_index, 0, display_string[:curses.COLS])
                line_index += 1
            
            for idx, log in enumerate(display_log_queue):
                stdscr.addstr(idx + size_of_top_data, 0, log[:curses.COLS])

            stdscr.refresh()

            # injest new data
            while p.poll(1): 
                try:
                    log_line = f.stdout.readline()
                    display_log_queue.append(log_line)
                    reporter.addLog( log_parser(str(log_line)) )
                except LineDoesntMatchException:
                    print(f"log found that did not match parsing: {log_line}", file=sys.stderr)
                    pass

            time.sleep(1)    
            if stdscr.getch() != curses.ERR:
                #user input detected exit
                break