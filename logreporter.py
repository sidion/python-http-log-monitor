import collections
from collections import deque
import datetime
import re
import math

class LogReporter:
    
    def __init__(self, retention_time = 130) -> None:
        #deque is more optomoized for interacting with both ends of the list
        #so will be more run time effiecent that a simple list
        self._logs = collections.deque([])
        #a log with a timestamp older than now - _retention time should be removed
        self._retention_time = retention_time 

    #adds a new log to internal log list
    #log should be in Dict object format
    def addLog(self, log) -> bool:
        self._logs.appendleft(log)
        return True

    #return a Dict of intersting data for the window
    #window should a int which is the number of seconds in the window
    def getStatsForWindow(self, window):
        end_of_window = datetime.datetime.now() - datetime.timedelta(seconds=window)
        stats = {}
        stats['number_of_requests'] = 0
        sections = {}

        for log in self._logs:
            if log['time_received_datetimeobj'] > end_of_window:
                #add log to stats
                stats['number_of_requests'] += 1
                section = re.match(r'^\/(.*?)(\/|$)', log['request_url']).group(1)
                if section not in sections:
                    sections[section] = 0
                else:
                    sections[section] += 1
            else:
                break
        
        most_hit_section = ['none', -math.inf]
        for section in sections:
            if sections[section] > most_hit_section[1]:
                most_hit_section = [section, sections[section]]
        stats['most_hit_section'] = most_hit_section[0]
                
        return stats

    