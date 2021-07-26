import collections
import datetime
import re
import math

class LogReporter:
    
    def __init__(self, retention_time = 130) -> None:
        #deque is more optomoized for interacting with both ends of the list
        #so will be more run time effiecent that a simple list
        self._logs = collections.deque([])
        #a log with a timestamp older than now - _retention time will be purgeable
        self._retention_time = retention_time

    #adds a new log to internal log list
    #log should be in Dict object format
    #TODO: move log parsing to here
    def add_log(self, log) -> bool:
        self._logs.appendleft(log)
        return True


    #Call to prune logs past retention period
    #a call to this function could be included in the addLog or get stats function to make the model
    #self prune but i am leaving to be controlled in the higher level for more flexibility on
    #frequency of its call at this time
    def pruneLogs(self) -> bool:
        end_of_retention = datetime.datetime.now() - datetime.timedelta(seconds=self._retention_time)
        logs_to_remove = 0
        for log in reversed(self._logs):
            if log['time_received_datetimeobj'] < end_of_retention:
                logs_to_remove += 1
            else:
                break
        if logs_to_remove > 0:
            self._logs = collections.deque(list(self._logs)[:-logs_to_remove])
        return True


    #return a Dict of intersting data for the window
    #window should a int which is the number of seconds in the window
    def getStatsForWindow(self, window):
        end_of_window = datetime.datetime.now() - datetime.timedelta(seconds=window)
        stats = {}
        stats['number_of_requests'] = 0
        stats['total_response_bytes'] = 0
        stats['total_get_requests'] = 0
        stats['total_post_requests'] = 0
        sections = {}
        ip_addrs = set()

        for log in self._logs:
            if log['time_received_datetimeobj'] > end_of_window:
                #add log to stats
                stats['number_of_requests'] += 1
                stats['total_response_bytes'] += int(log['response_bytes'])
                if log['request_method'] == 'GET':
                    stats['total_get_requests'] += 1 
                if log['request_method'] == 'POST':
                    stats['total_post_requests'] += 1
                ip_addrs.add(log['remote_host'])

                #a section is defined as the text before the 2nd /
                #i have also chosen to include the text after the first / if there is no
                #second /
                # if this is undesireable, the regex would need to be changed to '^\/(.*)?\/'
                section = re.match(r'^\/(.*?)(\/|$)', log['request_url']).group(1)
                if section not in sections:
                    sections[section] = 0
                else:
                    sections[section] += 1

            else:
                break

        stats['number_of_unique_ips'] = len(ip_addrs)

        most_hit_section = ['none', -math.inf]
        for section in sections:
            if sections[section] > most_hit_section[1]:
                most_hit_section = [section, sections[section]]
        stats['most_hit_section'] = most_hit_section[0]

        return stats

    #window should be an int which is the number of seconds in the window
    def getRequestPerSecondForWindow(self, window) -> int:
        end_of_window = datetime.datetime.now() - datetime.timedelta(seconds=window)
        logs_not_counted = 0
        for log in reversed(self._logs):
            if log['time_received_datetimeobj'] < end_of_window:
                logs_not_counted += 1
            else:
                break
        total_logs_in_window = len(self._logs) - logs_not_counted
        return int(total_logs_in_window / window)

    #helper function to determin if current state should be considered an alert state
    #alert_window is time in seconds of the length of window
    #alert_threshold is requests per second that should trigger an alert
    #TODO: the return format of this function is a bit of a code smell; it is doing 2 things
    #      and functions should only do 1 thing, it works for now but is worth thinking about
    def isInAlertState(self, alert_window, alert_threshold):
        requests_per_second = self.getRequestPerSecondForWindow(alert_window)
        if requests_per_second >= alert_threshold:
            return [True, requests_per_second]
        return [False, 0]
    