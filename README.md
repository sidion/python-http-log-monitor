Take home project for Datadog

Initial Requirements statement:

> Consume an actively written-to w3c-formatted HTTP access log (https://www.w3.org/Daemon/User/Config/Logging.html). It should default to reading /tmp/access.log and be overrideable

- Display stats every 10s about the traffic during those 10s: the sections of the web site with the most hits, as well as interesting summary statistics on the traffic as a whole. A section is defined as being what's before the second '/' in the resource section of the log line. For example, the section for "/pages/create" is "/pages"
- Make sure a user can keep the app running and monitor the log file continuously
- Whenever total traffic for the past 2 minutes exceeds a certain number on average, print or display a message saying that “High traffic generated an alert - hits = {value}, triggered at {time}”. The default threshold should be 10 requests per second, and should be overridable
- Whenever the total traffic drops again below that value on average for the past 2 minutes, print or display another message detailing when the alert recovered
- Write a test for the alerting logic
- Explain how you’d improve on this application design


https://github.com/kiritbasu/Fake-Apache-Log-Generator was a useful tool in generating test data though note its python 2.7 requirement



improvements
- dynamic terminal window resizing
- abstract reporter, log parser and subprocess in c_main  as a parameter for better SOLID alignment
- create a more robust log parser that can handle multiple files or a queue service like aws SQS or RabitMQ
- allow for logs to be passed in via stdin vs a file read
- apachy log parser does not parse timezone offset correctly, open bug: https://github.com/amandasaurus/apache-log-parser/issues/19
- ensure type definition on all paramters and function return values
- take better advantage of horizontal space in the stats section