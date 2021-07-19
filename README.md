# HTTP log monitor
A live http log monitor application inspired by Top

Initial Requirements statement:

> Consume an actively written-to w3c-formatted HTTP access log (https://www.w3.org/Daemon/User/Config/Logging.html). It should default to reading /tmp/access.log and be overridable

- Display stats every 10s about the traffic during those 10s: the sections of the web site with the most hits, as well as interesting summary statistics on the traffic as a whole. A section is defined as being what's before the second '/' in the resource section of the log line. For example, the section for "/pages/create" is "/pages"
- Make sure a user can keep the app running and monitor the log file continuously
- Whenever total traffic for the past 2 minutes exceeds a certain number on average, print or display a message saying that “High traffic generated an alert - hits = {value}, triggered at {time}”. The default threshold should be 10 requests per second, and should be overridable
- Whenever the total traffic drops again below that value on average for the past 2 minutes, print or display another message detailing when the alert recovered
- Write a test for the alerting logic
- Explain how you’d improve on this application design
---

## Requirements:
base computer system requires:
- python 3 (3.8.6 was used to develop the application)
- Tail (tail 8.3 was used to develop the application)

Optional:
- python 2.7 was used for a helper test application

---

## Installation:
I highly recommend using a venv to run or work on this application
see https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/ for basic information on venvs

once your venv is setup install requirements with:


`pip install -r requirements.txt`

---

## Running Application:
after installing requirements you can run the application with:

`python main.py`

or

`python3 main.py`

depending on your executable name for python3

---

## Configuration:
custom configuration can be done via the config file for a more permanent alteration or via command line arg
help info can be found in terminal with

`python3 main.py -h`

but is as follows:
```
usage: main.py [-h] [-f FILE] [-a ALERTWINDOW] [-t ALERTTHRESHOLD] [-w STATWINDOW]

optional arguments:
-h, --help show this help message and exit
-f FILE, --file FILE specify log file location
-a ALERTWINDOW, --alertwindow ALERTWINDOW length in seconds of the alert window
-t ALERTTHRESHOLD, --alertthreshold ALERTTHRESHOLD number of requests per second that will trigger an alert
-w STATWINDOW, --statwindow STATWINDOW length in seconds of the window for stats. min=0, max=59
```

---

## Runnin Tests:
after installing requirements you can run all tests with:

`pytest`

---

## Known Issues:
- log parser does not take timezone into account; known issue in library: https://github.com/amandasaurus/apache-log-parser/issues/19
  - please ensure timestamps in log are in the same timezone format as the system time
- application will not handle window resizing
- alter state will only be triggered during a stat update window which could be problematic for large stat update windows
---

## Suggestions for Manual QA test cases:
### setup:
1. install application
2. install https://github.com/kiritbasu/Fake-Apache-Log-Generator in a seperate venv, it will be used to generate live test data (note it requires python 2.7)

### Test Cases:
- Happy path, application runs as expected
   1. start generating logs into `tmp/access.log` with the Fake Apache Log Generator via: `python apache-fake-log-gen.py --sleep 1 -n 0 -o CONSOLE > /tmp/access.log`
   2. run the Http Log Monitor via: `python3 main.py`
   3. Verify logs are appearing on screen
   4. Verify stats are being updated every 10s 
   5. Verify pressing a key will exit the application
   6. kill the fake log generator with `ctrl-c`
   7. (optional) delete the log file to save space
- Alerting
   1. start generating logs into `tmp/access.log` with the Fake Apache Log Generator via: `python apache-fake-log-gen.py --sleep 0.3 -n 0 -o CONSOLE > /tmp/access.log`
   2. run the Http Log Monitor via: `python3 main.py -a 10 -t 2`
   3. wait until the displayed requests per second reach 20 or above
   4. verify Alert state is triggered
   5. kill the fake log generator with `ctrl-c` to stop additional logs from being generated
   6. wait until the displayed requests per second fall below 20
   7. verify Alert state is ended and Recovery State entered
   8. verify Recovery State returns to Nominal state in the reporting window after the Recovery state was reached
   9. (optional) delete the log file to save space
 
---

## Forward looking improvements for the project:
- dynamic terminal window resizing
- adding colour to output for better readability
- take better advantage of horizontal space in the stats section
- abstract reporter, log parser and subprocess in c_main  as a parameter for better SOLID alignment
  - moving the log parser and log display deque into the LogReporter class would be a better encapsulation of application state
  - this would also facilitate better unit testing as the test coverage for the project is far too low for a production system
- create a more robust log parser that can handle multiple files or a queue service like aws SQS or RabitMQ
- allow for logs to be passed in via stdin vs a file read
- apachy log parser does not parse timezone offset correctly: possible solutions:
  - create PR to update apachy log parser project to fix issue
  - investigate alternative log parsers to migrate to
- ensure type definition on all parameters and function return values
- rewrite to conform to all pep8 style guidelines
- dockerize the application for easier containerization
---


## Personal notes / reflections:
- I should have taken a more TDD approach with the LogReporter instead of writing automated tests late in the project it would have highlighting the timezone parsing issue sooner and I may have had time to find a new parser




