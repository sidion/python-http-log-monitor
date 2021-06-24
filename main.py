import sys
import argparse

import time
import subprocess
import select

import apache_log_parser
from apache_log_parser import LineDoesntMatchException

if __name__ == '__main__':
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

    #the use of sh.tail will limit this appliation to only working on *nix systems with the tail command
    f = subprocess.Popen(['tail','-F', FILE_LOCATION], stdout=subprocess.PIPE )
    p = select.poll()
    p.register(f.stdout)

    log_parser = apache_log_parser.make_parser('%h %u %l %t "%r" %s %B')


    while True:
        if p.poll(1):
            try:
                log_line = f.stdout.readline()
                parts = log_parser(str(log_line))
                print(parts)
            except LineDoesntMatchException:
                print(f"log found that did not match parsing: {log_line}", file=sys.stderr)
                pass
        time.sleep(1)    
    
        