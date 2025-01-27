'''
Documentation:
Test Margin Geek API

Tests a live api based on the app_mode (dev or prod). 

Dev endpoint: https://dev-api.margingeek.com (Not always running)
prod endpoint: https://api.margingeek.com

Cron will run on prod hourly
'''
#To Run:
#   pytest tests/test_api.py -v


import pytest
#from flask_testing import TestCase
import json
import os
import sys
#from margingeek_api.app import app
import requests
import pymongo
from pymongo.server_api import ServerApi
from time import time, sleep

#os.environ['TEST_APP_MODE'] = 'dev'
mongo_key = os.environ.get('MONGODBTESTER_KEY')
if mongo_key is None:
    with open("env/bin/secrets.json", 'r') as file:
        secrets = json.load(file)
    mongo_key = secrets['MONGODBTESTER_KEY']

mongo = 'mongodb+srv://tester:'+mongo_key+'@amati0.xwuxtdi.mongodb.net/?retryWrites=true&w=majority&authSource=admin'
mongo_c = pymongo.MongoClient(mongo,server_api=ServerApi('1'))
db_customers = mongo_c.get_database('customers') 

#=====================================
# Variables
#=====================================
latest_base_cost = 0.01
latest_ai_cost = 0.003
latest_qa_cost = 0.01
latest_expedited_cost = 0.005

# It is okay to update the balance / rows for these customers, but only these customers:
from context.globals import premium_customer_id_dev, free_customer_id_dev, premium_customer_id_prod, free_customer_id_prod      


#=====================================
#Functions used
#=====================================

def update_balance(customer_id, balance = None, rows = None):
    '''Update balance for test accounts'''
    try:
        record = db_customers.customers.find_one({'customer_id':customer_id})
        if record == None:
            print('No rows updated')
            return None
        else:
            update_dict = {}
            if balance is not None:
                update_dict['balance'] = balance
            if rows is not None:
                update_dict['included_rows'] = rows
            if len(update_dict.keys()) > 0:
                record = db_customers.customers.update_one({'customer_id':customer_id},{'$set':{'balance':balance,'included_rows':rows,'datetime_updated':int(time())}})
                return record
            else:
                print('No update specified.')
    except Exception as e:
        print("Failed to update customer record: " +str(e))




#================================
# Test Class
#================================
class TestMarginGeekAPI:
    """Test suite for MarginGeek API endpoints"""
    
    #def create_app(self):
    #    """Create test Flask application"""
    #    app.config['TESTING'] = True
    #    return app
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment before each test"""
        self.app_mode = os.environ.get('TEST_APP_MODE','prod')
        if self.app_mode == 'prod':
            print('Running tests in prod')
            self.is_dev = False
            self.api_host = 'https://api.margingeek.com'
            self.headers = {"Origin": "https://app.margingeek.com"}
            self.test_customer_id = premium_customer_id_prod  # Use a test customer ID
            self.test_client_id = "9002"
            self.premium_customer_id = premium_customer_id_prod  # Use a test customer ID
            self.premium_client_id = "9002"
            self.free_customer_id = free_customer_id_prod  # Use a test customer ID
        else:
            print('Running tests in dev')
            self.is_dev = True
            self.api_host = 'https://dev-api.margingeek.com:444' #'http://127.0.0.1:5000'  # Change to https://dev-api.margingeek.com:444 for dev testing
            self.headers = {"Origin": "https://margin-geek-portal.vercel.app"}
            self.test_customer_id = premium_customer_id_dev # Use a test customer ID
            self.test_client_id = "9002"
            self.premium_customer_id = premium_customer_id_dev # Use a test customer ID
            self.premium_client_id = "9002"
            self.free_customer_id = free_customer_id_dev  # Use a test customer ID
        

    def test_health_check(self):
        """Test basic health check endpoint"""
        response = requests.get(f"{self.api_host}", headers=self.headers)
        assert response.status_code == 200
        assert response.text == "OK"

    def test_get_settings(self):
        """Test retrieving settings"""
        params = {
            "client_id": self.test_client_id,
            "filename": "settings.json"
        }
        response = requests.get(
            f"{self.api_host}/get-settings",
            params=params,
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert 'settings' in data
        assert 'exists' in data

    def test_save_settings(self):
        """Test saving settings"""
        
        test_settings = {
            "Settings": {
                "Human Quality Check": "no",
                "AI Search": "no",
                "Priority": "no",
                "Seller Costs": {}
            },
            "Client ID": self.test_client_id,
            "Stripe ID": self.test_customer_id
        }
        
        # Then try to save them back
        data = {
            "client_id": self.test_client_id,
            "filename": "settings unittest.json",
            "settings": test_settings,
            "section":"settings"
        }
        response = requests.post(
            f"{self.api_host}/save-settings",
            json=data,
            headers=self.headers
        )
        assert response.status_code == 200
        assert response.json()['status'] == 'Settings saved successfully'

    def test_validate_scan(self):
        """Test scan validation"""
        data = {
            "client_id": self.test_client_id,
        }
        files = {'file': open('Input/Folgerstest - highlights.csv', 'rb')}
        
        response = requests.post(
            f'{self.api_host}/validate-scan',
            data=data,
            files=files,
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert 'task_id' in data

    def test_check_validate_scan(self):
        """Test checking scan validation status"""
        # First submit a validation
        data = {"client_id": self.test_client_id}
        files = {'file': open('Input/Folgerstest - highlights.csv', 'rb')}
        
        submit_response = requests.post(
            f'{self.api_host}/validate-scan',
            data=data,
            files=files,
            headers=self.headers
        )
        task_id = submit_response.json()['task_id']
        
        # Then check its status
        response = requests.get(
            f'{self.api_host}/check-validate-scan',
            params={"task_id": task_id},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data

    def test_get_plan_meta(self):
        """Test retrieving plan metadata"""
        response = requests.get(
            f'{self.api_host}/get-plan-meta',
            params={'customer_id': self.test_customer_id},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert 'customer_id' in data
        assert 'customer_mgid' in data
        assert 'plan' in data
        assert 'status' in data

    def test_compute_cost(self):
        """Test cost computation for different settings combinations"""
        record = update_balance(self.premium_customer_id, balance = 50, rows = 10000)
        record = update_balance(self.free_customer_id, balance = 50)
        test_cases = [
            {
                "name": "Basic Premium - No Add-ons",
                "customer_id":self.premium_customer_id,
                "settings": {
                    "Settings": {
                        "AI Search": "No",
                        "Human Quality Check": "No",
                        "Priority": "Standard",
                        "Seller Costs": {}
                    }
                },
                "rows": 15,
                "expected": {
                    "rows_used": 0,
                    "balance_used": 0,
                    "balance_required": 0
                }
            },
            {
                "name": "Premium with AI Standard",
                "customer_id":self.premium_customer_id,
                "settings": {
                    "Settings": {
                        "AI Search": "Yes",
                        "Human Quality Check": "No",
                        "Priority": "Standard",
                        "Seller Costs": {}
                    }
                },
                "rows": 15,
                "expected": {
                    "rows_used": 15,  # All rows count because AI is enabled
                    "balance_used": 0,
                    "balance_required": 0
                }
            },
            {
                "name": "Premium with AI Standard",
                "customer_id":self.premium_customer_id,
                "settings": {
                    "Settings": {
                        "AI Search": "Yes",
                        "Human Quality Check": "No",
                        "Priority": "Standard",
                        "Seller Costs": {}
                    }
                },
                "rows": 10050,
                "expected": {
                    "rows_used": 10000,  # All rows count because AI is enabled
                    "balance_used": 50 * latest_ai_cost,
                    "balance_required": 0
                }
            },
            {
                "name": "Premium All Features",
                "customer_id":self.premium_customer_id,
                "settings": {
                    "Settings": {
                        "AI Search": "Yes",
                        "Human Quality Check": "Yes",
                        "Priority": "Expedited",
                        "Seller Costs": {}
                    }
                },
                "rows": 15,
                "expected": {
                    "rows_used": 15,
                    "balance_used": 0 * (latest_ai_cost) + 15 * (latest_expedited_cost + latest_qa_cost),
                    "balance_required": 0
                }
            },
            {
                "name": "Free Base Only",
                "customer_id":self.free_customer_id,
                "settings": {
                    "Settings": {
                        "AI Search": "No",
                        "Human Quality Check": "No",
                        "Priority": "Standard",
                        "Seller Costs": {}
                    }
                },
                "rows": 15,
                "expected": {
                    "rows_used": 0,
                    "balance_used": 15 * latest_base_cost,
                    "balance_required": 0
                }
            },
            {
                "name": "Free AI only",
                "customer_id":self.free_customer_id,
                "settings": {
                    "Settings": {
                        "AI Search": "Yes",
                        "Human Quality Check": "No",
                        "Priority": "Standard",
                        "Seller Costs": {}
                    }
                },
                "rows": 15,
                "expected": {
                    "rows_used": 0,
                    "balance_used": 15 * (latest_base_cost + latest_ai_cost),
                    "balance_required": 0
                }
            },
            {
                "name": "Free Not Enough",
                "customer_id":self.free_customer_id,
                "settings": {
                    "Settings": {
                        "AI Search": "No",
                        "Human Quality Check": "No",
                        "Priority": "Standard",
                        "Seller Costs": {}
                    }
                },
                "rows": 50 / latest_base_cost + 1,
                "expected": {
                    "rows_used": 0,
                    "balance_used": 0,
                    "balance_required": ((50 / latest_base_cost) +1) * (latest_base_cost)
                }
            },
            {
                "name": "Free All Features",
                "customer_id":self.free_customer_id,
                "settings": {
                    "Settings": {
                        "AI Search": "Yes",
                        "Human Quality Check": "Yes",
                        "Priority": "Expedited",
                        "Seller Costs": {}
                    }
                },
                "rows": 15,
                "expected": {
                    "rows_used": 0,
                    "balance_used": 15 * (latest_base_cost + latest_ai_cost + latest_expedited_cost + latest_qa_cost),
                    "balance_required": 0
                }
            }
        ]

        for test_case in test_cases:
            sleep(.1)
            # Add common settings fields
            test_case["settings"].update({
                "Batch Name": "MG",
                "Client ID": "9002",
                "Type": "Wholesale",
                "Stripe ID": test_case['customer_id'],
                "rerank_algorithm": "single"
            })

            data = {
                "customer_id": test_case['customer_id'],
                "rows": test_case["rows"],
                "settings": test_case["settings"]
            }

            response = requests.post(
                f'{self.api_host}/compute-cost',
                json=data,
                headers=self.headers
            )

            assert response.status_code == 200, f"Failed on test case: {test_case['name']}"
            result = response.json()

            # Check response structure
            assert 'rows_used' in result, f"Missing rows_used in {test_case['name']}"
            assert 'balance_used' in result, f"Missing balance_used in {test_case['name']}"
            assert 'balance_required' in result, f"Missing balance_required in {test_case['name']}"

            # Check expected values
            assert result['rows_used'] == test_case['expected']['rows_used'], \
                f"Wrong rows_used in {test_case['name']}. Expected {test_case['expected']['rows_used']}, got {result['rows_used']}"
            
            assert abs(result['balance_used'] - test_case['expected']['balance_used']) < 0.001, \
                f"Wrong balance_used in {test_case['name']}. Expected {test_case['expected']['balance_used']}, got {result['balance_used']}"
            
            assert result['balance_required'] == test_case['expected']['balance_required'], \
                f"Wrong balance_required in {test_case['name']}. Expected {test_case['expected']['balance_required']}, got {result['balance_required']}"
            
            print(f"✓ {test_case['name']} passed")

    def test_get_scans(self):
        """Test retrieving scan history"""
        response = requests.get(
            f'{self.api_host}/get-scans',
            params={"customer_id": self.test_customer_id},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'scans' in data

#def pytest_addoption(parser):
#    parser.addoption("--app_mode", default="dev", help="app mode: dev or prod")

#@pytest.fixture
#def app_mode(request):
#    return request.config.getoption("--app_mode")

if __name__ == '__main__':
    pytest.main([__file__])
