import os
import json
import time
from time import sleep
import datetime

import pytest

import boto3
import pymongo
import pandas as pd
import requests
from pymongo.server_api import ServerApi
import argparse

from tools import read_csv_from_server, convert_to_number, yyyymmdd_date
from tests.test_api import update_balance
#premium_customer_id = "cus_QcwLkv0EVqYtYs"      # It is okay to update the balance / rows for these customers, but only these customers
#free_customer_id = "cus_QziFoGqYoOjJKb"         # It is okay to update the balance / rows for these customers, but only these customers
#premium_customer_id_prod = "cus_QdBn80R17gnunh" # It is okay to update the balance / rows for these customers, but only these customers
#free_customer_id_prod = "cus_QzjqmsH9lWZ5Zn"    # It is okay to update the balance / rows for these customers, but only these customers
from context.globals import free_customer_id_prod, premium_customer_id_prod, premium_client_id_prod, free_client_id_prod
from context.globals import free_customer_id_dev, premium_customer_id_dev, premium_client_id_dev, free_client_id_dev


def delete_pg(asin,db,display_deleted_count = True):
    link = 'https://www.amazon.com/dp/'+str(asin)
    result = db.requests.delete_many({'asin':asin})
    deleted_count = result.deleted_count
    result2 = db.requests.delete_many({'url':link})
    deleted_count = deleted_count + result2.deleted_count
    if display_deleted_count:
        print(f"Deleted {deleted_count} records for {asin}")
    
class TestMarginGeekScanner:
    """Test suite for MarginGeek scanner, end to end"""
    
    @pytest.fixture(autouse=True)
    def setup(self,command_line_args):
        """Setup test environment before each test"""
        self.app_mode = os.environ.get('TEST_APP_MODE','prod')
        location = os.environ.get('LOCATION','server') #really just a backup
        #get args and potentially change prior settings
        mini = None
        try:
            print(command_line_args)
            print(type(command_line_args))
            if 'mode' in command_line_args.keys():
                mode = command_line_args["mode"]
                if str(mode).lower() in ['prod','dev']:
                    print(f"setting app_mode to {str(mode).lower()}")
                    self.app_mode = str(mode).lower()
            if 'mini' in command_line_args.keys():
                mini = command_line_args["mini"]
            if 'location' in command_line_args.keys():
                location = command_line_args["location"] #local or nothing
                print(f"setting location to {location}")
        except Exception as error:
            print(f"WARNING: not using passed arguments {error}")
        self.local = str(location).lower() == 'local'
        if self.app_mode == 'prod':
            print('Running tests in prod')
            self.is_dev = False
            self.api_host = 'https://api.margingeek.com'
            self.headers = {"Origin": "https://app.margingeek.com"}
            #self.test_customer_id = premium_customer_id_prod
            self.premium_customer_id = premium_customer_id_prod
            self.premium_client_id = premium_client_id_prod
            self.free_customer_id = free_customer_id_prod
            self.free_client_id = free_client_id_prod
            self.main_customer = premium_customer_id_prod
            self.main_client = premium_client_id_prod
        else:
            print('Running tests in dev')
            self.is_dev = True
            if 'true' in str(self.local).lower():
                self.api_host = 'http://127.0.0.1:5000'
                self.headers = {"Origin": "https://margin-geek-portal.vercel.app"}
            else:
                self.api_host = 'https://dev-api.margingeek.com:444'
                self.headers = {"Origin": "https://margin-geek-portal.vercel.app"}
            
            self.premium_customer_id = premium_customer_id_dev
            self.premium_client_id = premium_client_id_dev
            self.free_customer_id = free_customer_id_dev
            self.free_client_id = free_client_id_dev
            self.main_customer = premium_customer_id_dev
            self.main_client = premium_client_id_dev
        self.file1 = 'e2e1.csv'
        if mini is not None:
            print('Using mini file for e2e1')
            self.file1 = 'e2e1 mini.csv'
        

    def test_e2e_completion(self):
        """
        Example of running multiple test cases in an End-to-End style
        """
        print('starting end 2 end completion test')
        # Grab secrets for DigitalOcean and Mongo
        dospaces_key = os.environ.get('DIGITAL_OCEAN_SPACES')
        mongo_key = os.environ.get('MONGODBTESTER_KEY')
        if mongo_key is None:
            with open("env/bin/secrets.json", 'r') as file:
                secrets = json.load(file)
            mongo_key = secrets['MONGODBTESTER_KEY']
            dospaces_key = secrets['DIGITAL_OCEAN_SPACES']

        s3_client = boto3.client(
            's3',
            region_name='sfo2',  # DigitalOcean region (e.g., sfo2, nyc3)
            endpoint_url='https://margingeek.sfo2.digitaloceanspaces.com',
            aws_access_key_id='DO0037EZYUND6J8C8YGW',
            aws_secret_access_key=dospaces_key
        )
        mongo = 'mongodb+srv://tester:' + mongo_key + '@amati0.xwuxtdi.mongodb.net/?retryWrites=true&w=majority&authSource=admin'
        mongo_c = pymongo.MongoClient(mongo, server_api=ServerApi('1'))
        db = mongo_c.get_database('celery')
        db_customers = mongo_c.get_database('customers')

        date = yyyymmdd_date(datetime.date.today())
        # ------------------------------------------------------------------
        # You can define multiple test_cases here:
        # Each test_case dict can override scan_name, filename, rerank_algorithm, etc.
        # ------------------------------------------------------------------
        test_cases = [
            {
                "scan_name": f"e2e1 auto {date}",
                "sku_file": self.file1,
                "rr_algo": "single",
                "customer_id": self.premium_customer_id,  # or some other customer that you want to test with
                "column_mappings": {
                    'Identifier': 'MG Index',
                    'Brand': 'Brand_left',
                    'Code': 'Code_left',
                    'Product Description': 'Title_left',
                    'Additional Product Text': 'Description_left',
                    'Purchase Price': 'Purchase Price',
                    'Unit of Measure': "Purchase Price Units"
                },
                "checkpoint": 0,
                "settings": {
                    'Batch Name': 'MG',
                    'Client ID': self.premium_client_id,
                    'Email': 'julian.a.ghadially@gmail.com',
                    'Pricing Units': 'Unit of Measure',
                    'rerank_algorithm': 'single',
                    'Settings': {
                        'AI Search': "Yes",
                        'Exclusions': {
                            'Amazon in buybox': 'Include',
                            'Single-seller listings': 'Exclude'
                        },
                        'Human Quality Check': 'No',
                        'Priority': 'Standard',
                        'ROI Cutoff': 0,
                        'Revenue Cutoff': 50,
                        'Sales Volume': 'n/a',
                        'Check Match History': 'No',
                        'Check Requests': 'No',
                        'Seller Costs': {
                            'FBM': 1,
                            'Price Discounts': 0.90,
                            'Shipping to Amazon': 'None',
                            'Peak Volume': "Auto",
                            'Inbound Locations': '4+',
                            'Low Inventory Percentage': 0
                        }
                    },
                    'Type': 'Wholesale',
                    'Stripe ID': self.premium_customer_id
                },
                "test_pt3": False
            },
            {
                "scan_name": f"e2e2 auto {date}", #test each with price discount = 100%, and various seler cost settings, also evaluate every product.  
                "sku_file": "e2e2.csv",
                "rr_algo": "single",
                "customer_id": self.free_customer_id,  # or some other customer that you want to test with
                "column_mappings": {
                    'Identifier': 'MG Index',
                    'Brand': 'Brand_left',
                    'Code': 'Code_left',
                    'Product Description': 'Title_left',
                    'Additional Product Text': 'Description_left',
                    'Purchase Price': 'Purchase Price',
                    'Unit of Measure': "Purchase Price Units"
                },
                "checkpoint": 0,
                "settings": {
                    'Batch Name': 'MG',
                    'Client ID': self.free_client_id,
                    'Email': 'julian.a.ghadially@gmail.com',
                    'Pricing Units': 'Each',
                    'rerank_algorithm': 'single',
                    'Settings': {
                        'AI Search': "Yes",
                        'Exclusions': {
                            'Amazon in buybox': 'Include',
                            'Single-seller listings': 'Exclude'
                        },
                        'Human Quality Check': 'No',
                        'Priority': 'Standard',
                        'ROI Cutoff': 0,
                        'Revenue Cutoff': 50,
                        'Sales Volume': 'n/a',
                        'Check Match History': 'No',
                        'Check Requests': 'No',
                        'Evaluate Every Product':"Yes",
                        'Seller Costs': {
                            'FBM': 1.1,
                            'Price Discounts': 100,
                            'Shipping to Amazon': .5,
                            'Peak Volume': "No",
                            'Inbound Locations': '2-3',
                            'Low Inventory Percentage': .5
                        }
                    },
                    'Type': 'Wholesale',
                    'Stripe ID': self.free_customer_id
                },
                "test_pt3": False
            }
        ]
        test_cases.reverse()
        #Precursor: make sure customers have appropriate balances
        record = update_balance(self.premium_customer_id, balance = 50, rows = 10000)
        sleep(.05)
        record = update_balance(self.free_customer_id, balance = 50)
        
        #Start by submit all test cases and collect their responses
        submitted_cases = []
        for tcase in test_cases:
            scan_name = tcase["scan_name"]
            filename = tcase["sku_file"]
            rr_algo = tcase["rr_algo"]
            customer_id = tcase["customer_id"]
            column_mappings = tcase["column_mappings"]
            checkpoint = tcase["checkpoint"]
            settings = tcase["settings"]
            test_pt3 = tcase["test_pt3"]

            
            # Overwrite the Stripe ID inside settings if you want to unify with main_customer
            # or let it remain from the test case.
            # settings['Stripe ID'] = self.main_customer
            # or keep tcase's definition:
            # settings['Stripe ID'] = customer_id

            filepath = f'Input/{filename}'
            skus = pd.read_csv(filepath, skiprows=3)
            asins = skus['ASIN Cheat Sheet'].values

            # OPTIONALLY test part 3 by removing old entries of these asins from the DB
            if test_pt3:
                # If you have a helper function like delete_pg(asin, db), call it here
                # for asin in asins:
                #     delete_pg(asin, db)
                pass

            # Submit the scan
            url = f'{self.api_host}/submit-scan'
            data = {
                "client_id": settings['Client ID'],
                'settings': json.dumps(settings),
                'mappings': json.dumps(column_mappings),
                'scan_name': scan_name,
                'checkpoint': checkpoint
            }
            files = {'file': open(filepath, 'rb')}
            response = requests.post(url, data=data, files=files, headers=self.headers)
            print(f"Submitted {scan_name}: {response.text}")
            
            submitted_cases.append({
                "case": tcase,
                "response": response,
                "submit_time": time.time()
            })

        # Track all test failures
        test_failures = []
        
        # Now process all submitted cases
        timeout = 60 * 60 * 2     # 2 hours
        for submission in submitted_cases:
            tcase = submission["case"]
            response = submission["response"]
            start_t = submission["submit_time"]
            
            scan_name = tcase["scan_name"]
            filename = tcase["sku_file"]
            rr_algo = tcase["rr_algo"]
            customer_id = tcase["customer_id"]
            settings = tcase["settings"]
            test_pt3 = tcase["test_pt3"]

            print(f"\nProcessing results for {scan_name}")
            
            try:
                # test metrics
                completion_pass = False
                completion_comment = ''
                pass_cf_accuracy = 0
                pass_cf_completion = 0
                search_p2recall = 0
                rerank_p2recall = 0
                code_p2recall = 0
                total_p2recall = 0

                result = {}
                status = 'pending'
                try:
                    if json.loads(response.text)['status'] == 'success':
                        usage_record = json.loads(response.text)['usage_record']
                        scan_name = usage_record['scan_name']
                        file_name = usage_record['file_name']
                        while str(status).lower() in ['pending'] and (time.time() - start_t) < timeout:
                            print(f'checking status. {status}')
                            try:
                                result = db_customers.usage.find_one({'customer_id': customer_id, 'scan_name': scan_name})
                            except Exception as error:
                                raise Exception(f'Error connecting to mongodb. Likely authentication issue. {error}')
                            if result and 'status' in result.keys():
                                status = str(result['status']).lower()
                                sleep(.1)
                                if status == 'pending':
                                    if (time.time() - start_t) < 300:
                                        sleep(20)
                                    else:
                                        sleep(180)
                        if status == 'complete':
                            completion_pass = True
                        else:
                            completion_pass = False
                            errors = result['errors'] if 'errors' in result.keys() else ''
                            message = result['message'] if 'message' in result.keys() else ''
                            completion_comment = f"{status}: {message}. {errors}"
                    else:
                        raise Exception('Scan Submission Failed')
                except Exception as ex:
                    print(f'Scan submission error: {ex}')
                    completion_pass = False
                    completion_comment = f"Exception on submission or tracking: {str(ex)}"
                print(f'status passed. {status}')
                if completion_pass:
                    # Part 2 recall checks
                    batch_path = "tasks/Product Scanner/Store/History/"
                    batch_file = f"{settings['Client ID']} {scan_name} pt2 ranked.csv"
                    # read the batch and input
                    batch = read_csv_from_server(
                        batch_path + batch_file, 
                        s3_client=s3_client, 
                        cloud=True, 
                        dtype={"Code": str},
                        index_col=(0,1)
                    )
                    skus_input = read_csv_from_server(
                        batch_path + batch_file.replace("pt2 ranked", "Input"),
                        s3_client=s3_client, 
                        cloud=True, 
                        dtype={"Code": str},
                        index_col=(0,1)
                    )
                    pt2_search_found = 0
                    pt2_rerank_found = 0
                    pt2_code_found = 0
                    pt2_total_rows = 0
                    pt2_total_found = []
                    for idx in batch.index:
                        secret_idx = batch.loc[idx, 'Identifier']
                        try:
                            secret_asin = secret_idx.split('-')[1]
                        except:
                            continue
                        asin = batch.loc[idx, '_Product ID']
                        search_type = batch.loc[idx, '_Match Certainty']
                        prod_i = idx[1]

                        if prod_i == 0:
                            pt2_total_rows += 1
                            if secret_asin in str(batch.loc[idx,'Search Results - Links']):
                                pt2_search_found +=1
                            if secret_asin in str(batch.loc[idx,'Matches - Link']):
                                pt2_rerank_found +=1
                                pt2_total_found.append(secret_idx)
                        if prod_i > 0 and 'code' in str(search_type).lower():
                            if secret_asin == asin:
                                pt2_code_found += 1
                                pt2_total_found.append(secret_idx)

                    pt2_total_found = len(list(set(pt2_total_found)))
                    if pt2_total_rows > 0:
                        search_p2recall = round(pt2_search_found / pt2_total_rows,3)
                        rerank_p2recall = round(pt2_rerank_found / pt2_total_rows, 3)
                        code_p2recall   = round(pt2_code_found / pt2_total_rows, 3)
                        total_p2recall  = round(pt2_total_found / pt2_total_rows, 3)

                    search_p2_threshold = 0.65 if pt2_total_rows > 20 else 0.6 if pt2_total_rows > 10 else .5
                    rerank_p2_threshold = 0.45 if pt2_total_rows > 20 else 0.4 if pt2_total_rows > 10 else .3
                    code_p2_threshold = 0.45 if pt2_total_rows > 20 else 0.4 if pt2_total_rows > 10 else .3
                    total_p2_threshold = 0.65 if pt2_total_rows > 20 else 0.6 if pt2_total_rows > 10 else .5
                    pass_p2_search = search_p2recall > search_p2_threshold
                    pass_p2_rerank = rerank_p2recall > rerank_p2_threshold
                    pass_p2_code   = code_p2recall > code_p2_threshold
                    pass_p2_total  = total_p2recall > total_p2_threshold
                    p2recall_comments = (
                        f"Total P2 Recall: {round(total_p2recall*100,2)}%, which is {pt2_total_found} out "
                        f"of {pt2_total_rows} rows. Search recall: {round(search_p2recall*100,2)}%. "
                        f"Rerank recall: {round(rerank_p2recall*100,2)}%. Code recall: {round(code_p2recall*100,2)}%"
                    ) #not used anymore

                    # match accuracy checks
                    total_matches = 0
                    ct_codesearch = 0
                    accurate_ct_codesearch = 0
                    ct_aisearch = 0
                    accurate_ct_aisearch = 0
                    batch_file_pt4 = f"{settings['Client ID']} {scan_name} pt4ii scored.csv"
                    batch_pt4 = read_csv_from_server(
                        batch_path + batch_file_pt4, 
                        s3_client=s3_client, 
                        cloud=True, 
                        dtype={"Code": str},
                        index_col=(0,1)
                    )
                    for idx in batch_pt4.index:
                        secret_idx = batch_pt4.loc[idx,'Identifier']
                        try:
                            secret_asin = secret_idx.split('-')[1]
                        except:
                            continue
                        asin = batch_pt4.loc[idx,'_Product ID']
                        if asin == secret_asin:
                            match_class = batch_pt4.loc[idx, '_Match Class']
                            # unify "match" or "match cant confirm" under 'match'
                            if str(match_class).replace("\'","") in ['match', 'match cant confirm']:
                                match_class = 'match'
                            else:
                                match_class = 'not a match'
                            match_type = batch_pt4.loc[idx,'_Match Certainty']

                            if match_class == 'match':
                                if 'ai' in str(match_type).lower():
                                    accurate_ct_aisearch +=1
                                elif 'code' in str(match_type).lower():
                                    accurate_ct_codesearch +=1
                                else:
                                    print(f'WARNING: unexpected match type: {match_type}')
                                    continue
                            if 'ai' in str(match_type).lower():
                                ct_aisearch +=1
                            if 'code' in str(match_type).lower():
                                ct_codesearch +=1

                    match_completion = 0
                    match_ai_recall = 0 
                    match_code_recall = 0
                    pass_match_completion = False
                    pass_match_ai_recall = True 
                    pass_match_code_recall = True

                    if (ct_aisearch + ct_codesearch) > 0:
                        match_completion = round((accurate_ct_aisearch + accurate_ct_codesearch) / (ct_aisearch + ct_codesearch),3)
                        pass_match_completion = True
                    if ct_aisearch > 0:
                        match_ai_recall = round(accurate_ct_aisearch / ct_aisearch,3)
                    if ct_codesearch > 0:
                        match_code_recall = round(accurate_ct_codesearch / ct_codesearch,3)

                    match_comments = (
                        f"Code match recall of {match_code_recall} with n = {ct_codesearch}. "
                        f"AI Match recall of {match_ai_recall} with n = {ct_aisearch}"
                    )
                    match_code_threshold = .9 if ct_codesearch > 20 else .85 if ct_codesearch > 10 else .75
                    match_ai_threshold = .8 if ct_aisearch > 20 else .6 if ct_codesearch > 10 else .5
                    pass_match_code_recall = match_code_recall > match_code_threshold
                    pass_match_ai_recall = match_ai_recall > match_ai_threshold

                    # known conversion factor accuracy
                    total_matches = 0
                    cf_counter = 0
                    cf_counter_accurate = 0
                    batch_file_matches = f"{settings['Client ID']} {scan_name} matches tab.csv"
                    matches_tab = read_csv_from_server(
                        batch_path + batch_file_matches, 
                        s3_client=s3_client, 
                        cloud=True, 
                        dtype={"Code": str},
                        index_col=(0,1)
                    )
                    problem_asins = []
                    for idx in matches_tab.index:
                        summary = matches_tab.loc[idx,'Summary']
                        secret_idx = matches_tab.loc[idx,'Identifier']
                        row_filtered = skus_input[skus_input['Identifier'] == secret_idx]
                        if row_filtered.empty:
                            continue
                        sku = row_filtered.iloc[0]
                        try:
                            secret_asin = secret_idx.split("-")[1]
                        except:
                            continue
                        secret_cf = sku['Cf Cheat Sheet']
                        cf_val = convert_to_number(matches_tab.loc[idx, 'Conversion Factor'], replace_na=-1)
                        asin = matches_tab.loc[idx,'Listing ID']
                        if asin == secret_asin:
                            if 'match' in str(summary).lower():
                                total_matches += 1
                                if cf_val > 0:
                                    cf_counter += 1
                                    # check relative difference
                                    if abs(secret_cf - cf_val) / secret_cf < .01:
                                        cf_counter_accurate += 1
                                else:
                                    problem_asins.append(secret_idx)

                    if len(problem_asins) > 10:
                        problem_asins = problem_asins[0:10]

                    completion_threshold = .95 if total_matches > 20 else .85
                    cf_accuracy_thresh = .85 if total_matches > 20 else .75 if total_matches > 10 else .55 if total_matches > 5 else .45

                    if cf_counter > 0 and total_matches > 0:
                        pass_cf_completion = cf_counter / total_matches > completion_threshold
                        pass_cf_accuracy = cf_counter_accurate / cf_counter > cf_accuracy_thresh
                        cf_comments = (
                            f'CF Accuracy is {round((cf_counter_accurate / cf_counter)*100,2)}%. '
                            f'Completed {cf_counter} CFs out of {total_matches} matches, '
                            f'of which {cf_counter_accurate} CFs were accurate. '
                        )
                        if len(problem_asins) > 0:
                            cf_comments += f"Problem Matches: {', '.join(problem_asins)}"
                    else:
                        pass_cf_completion = False
                        pass_cf_accuracy = False
                        cf_comments = f'No conversion factors available'

                    test_outcome = {
                        "Batch Completion": completion_pass,
                        "Completion Comments": completion_comment,
                        "Part 2 Recall Test": pass_p2_total,
                        "Part 2 Search Recall": f"{pass_p2_search}: {search_p2recall} vs. threshold: {search_p2_threshold}. n = {pt2_total_rows}",
                        "Part 2 Rerank Recall": f"{pass_p2_rerank}: {rerank_p2recall} vs. threshold: {rerank_p2_threshold}. n = {pt2_total_rows}",
                        "Part 2 Code Recall": f"{pass_p2_code}: {code_p2recall} vs. threshold: {code_p2_threshold}. n = {pt2_total_rows}",
                        "Part 2 Total Recall": f"{pass_p2_total}: {total_p2recall} vs. threshold: {total_p2_threshold}. n = {pt2_total_rows}",
                        "Match Completion": pass_match_completion,
                        "Match Recall": pass_match_code_recall and pass_match_ai_recall,
                        "Match Recall - Codes": f"{pass_match_code_recall}: {match_code_recall} vs threshold {match_code_threshold}. n = {ct_codesearch}",
                        "Match Recall - AI": f"{pass_match_ai_recall}: {match_ai_recall} vs threshold {match_ai_threshold}. n = {ct_aisearch}",
                        "Match Comments": match_comments,
                        "CF Completed": pass_cf_completion,
                        "CF Accuracy": pass_cf_accuracy,
                        "CF Comments": f"CF Comments: {cf_comments}.  n = {total_matches}"
                    }

                    final_outcome = True
                    for key, value in test_outcome.items():
                        if isinstance(value, bool) and not value:
                            final_outcome = False
                        print(f"{key}: {value}")
                    print('==========================')
                    print(f'  Tests Passed: {final_outcome}')
                    print('==========================')

                    # Update assertion messages with more detail
                    try:
                        assert completion_pass, f"Batch failed to complete: {completion_comment}"
                        assert pass_p2_total, f"Part 2 total recall failed: {total_p2recall} vs. threshold: {total_p2_threshold}. n = {pt2_total_rows}"
                        assert pass_match_completion, f"Match completion failed: {match_completion}"
                        assert pass_match_code_recall, f"Match code recall failed: {match_code_recall} vs threshold {match_code_threshold}. n = {ct_codesearch}"
                        assert pass_match_ai_recall, f"Match AI recall failed: {match_ai_recall} vs. threshold: {match_ai_threshold}. n = {ct_aisearch}"
                        assert pass_cf_completion, f"CF completion failed: {pass_cf_completion}. n = {total_matches}"
                        assert pass_cf_accuracy, f"CF accuracy failed: {pass_cf_accuracy}. CF Comments: {cf_comments}.  n = {total_matches}"
                    except AssertionError as e:
                        failure_msg = (
                            f"\nTest case '{scan_name}' failed:"
                            f"\n  Customer ID: {customer_id}"
                            f"\n  Settings: {settings}"
                            f"\n  Error: {str(e)}"
                        )
                        test_failures.append(failure_msg)
                        print(failure_msg)
                else:
                    try:
                        assert completion_pass, f"Batch failed to complete: {completion_comment}" 
                    except AssertionError as e:
                        test_failures.append(f'Test case {scan_name} failed: \n Customer ID: {customer_id} \n Settings: {settings} \n Error: {str(e)}')
            except Exception as e:
                test_failures.append(f"Test case '{scan_name}' failed with exception: {str(e)}")
                print(f"Error processing test case {scan_name}: {str(e)}")
                continue

        # After all test cases are processed, fail if there were any failures
        if test_failures:
            failure_message = "\n".join(test_failures)
            raise AssertionError(f"One or more test cases failed:\n{failure_message}")

if __name__ == '__main__':
    pytest.main([__file__])
