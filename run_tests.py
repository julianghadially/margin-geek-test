import pymongo
from pymongo.server_api import ServerApi
from datetime import datetime
from time import time
import subprocess
import os
import pytest
from typing import List, Dict


mongo_key = os.environ.get('MONGODB_KEY')
mongo = 'mongodb+srv://julianghadially:'+mongo_key+'@amati0.xwuxtdi.mongodb.net/?retryWrites=true&w=majority&authSource=admin'
mongo_c = pymongo.MongoClient(mongo,server_api=ServerApi('1'))
db_logs = mongo_c.get_database('logs') 

app_mode = os.environ.get('TEST_APP_MODE')

class TestResultCollector:
    def __init__(self):
        self.results = {
            'success': True,
            'total': 0,
            'passed': 0,
            'failed': 0,
            'failed_tests': [],
            'failed_test_details': []
        }

    def _extract_test_name(self, nodeid: str) -> str:
        # Extract just the test name from nodeid
        # Convert 'tests/test_api.py::TestMarginGeekAPI::test_validate_scan'
        # to 'test_validate_scan'
        return nodeid.split('::')[-1]

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        
        if report.when == "call":
            self.results['total'] += 1
            if report.failed:
                self.results['failed'] += 1
                self.results['success'] = False
                self.results['failed_tests'].append(self._extract_test_name(report.nodeid))
                self.results['failed_test_details'].append(f'In {self._extract_test_name(report.nodeid)}: Error: {str(report.longrepr)}')
            elif report.passed:
                self.results['passed'] += 1


def log_test_results(results):
    """Store test results in MongoDB"""
    failed_tests = ", ".join(results['failed_tests'])
    failed_test_details = "  |||  ".join(results['failed_test_details'])
    

    log_record = {
        'timestamp': int(time()),
        'datetime': datetime.now().isoformat(),
        'success': results['success'],
        'total_tests': results['total'],
        'passed_tests': results['passed'],
        'failed_tests': failed_tests,
        'failed_test_details': failed_test_details,
        'environment': os.environ.get('TEST_APP_MODE', 'prod')
    }
    
    db_logs.test_results.insert_one(log_record)
    return log_record

def run_tests():
    try:
        collector = TestResultCollector()
        env = os.environ.copy()
        pytest.main(['tests/test_api.py','-v'],plugins=[collector])
        #run_seq = ["pytest", "tests/test_api.py", "-v"]
        #result = subprocess.run(run_seq, capture_output=True, text=True,env=env) #f"TEST_APP_MODE={app_mode}",
        results = collector.results
        print('---------------')
        print("\nTest Results Summary:")
        print(f"Total: {results['total']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        if results['failed'] > 0:
            print("\nFailed Tests:")
            for item in results['failed_test_details']:
                print(f"\n\n{item}")

                
        log_results = log_test_results(results)
        
        print('---------------')
        print('Result:')
        print(log_results)
        print('---------------')

        return results
        # Parse pytest output
        a = '''results = {
            'success': result.returncode == 0,
            'total': 0,
            'passed': 0,
            'failed': 0,
            'failed_tests': "",
            'failed_tests_details': "",
            'details': result.stdout if result.returncode == 0 else result.stderr
        }

        failed_tests = []
        failed_test_details = []

        for line in result.stdout.split('\n'):
            if line.strip().endswith('FAILED'):
                test_name = line.split('::')[1].split()[0]
                error_start = result.stdout.find(line)
                error_end = result.stdout.find('=', error_start)
                if error_end == -1:  # If no more '=' found, take until the end
                    error_end = len(result.stdout)
                error_details = result.stdout[error_start:error_end].strip()
                failed_tests.append(test_name)
                failed_test_details.append(error_details)
        results['failed_tests'] = ", ".join(failed_tests)
        results['failed_test_details'] = ", ".join(failed_test_details)
        
        # Parse test counts from output
        if "failed" in result.stdout:
            results['failed'] = int(result.stdout.split(" failed")[0].split()[-1])
        if "passed" in result.stdout:
            results['passed'] = int(result.stdout.split(" passed")[0].split()[-1])
        results['total'] = results['passed'] + results['failed']
        
        print(results)'''
        log_test_results(results)
        
    except Exception as e:
        error_results = {
            'success': False,
            'total': 0,
            'passed': 0,
            'failed': 1,
            'failed_tests': ['test_execution_error'],
            'failed_test_details': [{
                'test': 'test_execution',
                'error': str(e)
            }]
        }
        log_results = log_test_results(error_results)
        print('Error results:')
        print(log_results)
        return error_results

if __name__ == "__main__":
    run_tests()