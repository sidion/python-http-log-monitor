import sys
import argparse
import configparser
import curses

from src import httplogparser

def main() -> int:
    '''Main function, a wrapper to handle program inputs and pass them to the internal program'''
    config = configparser.ConfigParser()
    config.read('config.ini')
    default_config = config['default']

    file_location = default_config.get('FILE_LOCATION', 'tmp/access.log')
    alert_window_length = default_config.getint('ALERT_WINDOW_LENGTH', 120)
    alert_threshold = default_config.getint('ALERT_THRESHOLD', 10)
    stat_window_length = default_config.getint('STAT_WINDOW_LENGTH', 10)

    if len(sys.argv) > 1:
        #user submitted command line args parsing
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--file", help = "specify log file location", required = False)
        parser.add_argument("-a", "--alertwindow", help = "length in seconds of the alert window", required = False)
        parser.add_argument("-t", "--alertthreshold", help = "number of requests per second that will trigger an alert", required = False)
        parser.add_argument("-w", "--statwindow", help = "length in seconds of the window for stats. min=0, max=59", required = False)
        arguments = parser.parse_args()

        if arguments.file:
            file_location = arguments.file
        if arguments.alertwindow:
            alert_window_length = int(arguments.alertwindow)
        if arguments.alertthreshold:
            alert_threshold = int(arguments.alertthreshold)
        if arguments.statwindow:
            stat_window_length =int(arguments.statwindow)

    # this wrapper handles returning the terminal window to its previous state on appliation exit
    return curses.wrapper(httplogparser.
                            HttpLogParser.c_main,
                            file_location,
                            alert_window_length,
                            alert_threshold,
                            stat_window_length)


if __name__ == '__main__':
    sys.exit(main())
      