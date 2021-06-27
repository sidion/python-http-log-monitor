import pytest
import apache_log_parser
import datetime
import time
from src import logreporter

class TestLogReporter:

    def addLogsToReporter(self, reporter, number_of_logs):
        log_parser = apache_log_parser.make_parser('%h %u %l %t "%r" %s %B')
        for idx in range(number_of_logs):
            now = datetime.datetime.now(datetime.timezone.utc).astimezone().strftime('%d/%b/%Y:%H:%M:%S %z')
            reporter.addLog( log_parser(f"127.0.0.1 - james [{now}] \"GET /report/idx HTTP/1.0\" 200 123"))
        

    def test_file_is_fuctional(self):
        assert True

    @pytest.fixture
    def base_reporter(self):
        return logreporter.LogReporter()

    @pytest.fixture
    def reporter_without_retention(self):
        return logreporter.LogReporter(0) #create reporter with no retention

    @pytest.fixture
    def reporter_with_10_logs(self, base_reporter):
        self.addLogsToReporter(base_reporter, 10)
        return base_reporter

    def test_init(base_reporter):
        assert base_reporter

    def test_init_with_param(self):
        my_log_reporter = logreporter.LogReporter(300)
        assert my_log_reporter._retention_time == 300


    def test_addLog(self, base_reporter):
        #note this is a very bad test as we should not be parsing a string here but providing the test
        #a mocked object log generate via a factory
        log_parser = apache_log_parser.make_parser('%h %u %l %t "%r" %s %B')
        log = log_parser('127.0.0.1 - james [09/May/2018:16:00:39 +0000] "GET /report HTTP/1.0" 200 123')
        assert base_reporter.addLog(log)

    def test_getRequestPerSecondForWindow(self, reporter_with_10_logs):
        assert reporter_with_10_logs.getRequestPerSecondForWindow(10) == 1

    def test_isInAlertState(self, reporter_with_10_logs):
        assert reporter_with_10_logs.isInAlertState(10, 1) == [True, 1]
        
    def test_getStatsForWindow(self, reporter_with_10_logs):
        #not an ideal test, unit tests should only test 1 thing and we are making many assertions
        #getting closer to a functional test which might be better to move into a different file/suite
        stats = reporter_with_10_logs.getStatsForWindow(10)
        assert stats['number_of_requests'] == 10
        assert stats['total_get_requests'] == 10
        assert stats['total_post_requests'] == 0
        assert stats['number_of_unique_ips'] == 1
        assert stats['most_hit_section'] == 'report'

    def test_pruneLog(self, reporter_without_retention):
        self.addLogsToReporter(reporter_without_retention, 10)
        time.sleep(1)  #TODO mock time change instead of sleep for faster test run
        reporter_without_retention.pruneLogs()
        assert len(reporter_without_retention._logs) == 0

    def test_transition_to_alert(self, base_reporter):
        assert base_reporter.isInAlertState(10,1) == [False, 0]
        self.addLogsToReporter(base_reporter, 10)
        assert base_reporter.isInAlertState(10,1) == [True, 1]

    def test_transition_out_of_alert(self, reporter_without_retention):
        self.addLogsToReporter(reporter_without_retention, 10)
        assert reporter_without_retention.isInAlertState(10,1) == [True, 1]
        reporter_without_retention.pruneLogs()
        assert reporter_without_retention.isInAlertState(10,1) == [False, 0]