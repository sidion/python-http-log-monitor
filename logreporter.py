import collections
from collections import deque
import datetime

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
        for log in self._logs:
            if log['time_received_datetimeobj'] > end_of_window:
                #add log to stats
                stats['number_of_requests'] += 1
            else:
                break
        return stats

    