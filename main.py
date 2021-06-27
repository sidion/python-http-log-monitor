import sys
import argparse
import configparser
import curses

from src import httplogparser
 
def main() -> int:
    config = configparser.ConfigParser()
    config.read('config.ini')
    default_config = config['default']

    FILE_LOCATION = default_config.get('FILE_LOCATION', 'tmp/access.log')
    ALERT_WINDOW_LENGTH = default_config.getint('ALERT_WINDOW_LENGTH', 120)
    ALERT_THRESHOLD = default_config.getint('ALERT_THRESHOLD', 10)
    STAT_WINDOW_LENGTH = default_config.getint('STAT_WINDOW_LENGTH', 10)

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
            ALERT_WINDOW_LENGTH = int(arguments.alertwindow)
        if arguments.alertthreshold:
            ALERT_THRESHOLD = int(arguments.alertthreshold)
        if arguments.statwindow:
            STAT_WINDOW_LENGTH =int(arguments.statwindow)

    # this wrapper handles returning the terminal window to its previous state on appliation exit
    return curses.wrapper(httplogparser.HttpLogParser.c_main, FILE_LOCATION, ALERT_WINDOW_LENGTH, ALERT_THRESHOLD, STAT_WINDOW_LENGTH)


if __name__ == '__main__':
    exit(main())
      