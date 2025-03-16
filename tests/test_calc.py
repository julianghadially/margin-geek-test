'''
Provides Unit Tests for fees, volume, and profitability calculations

Dependencies:
- requires importing functions from Amati Agents package, including secret keys

'''
import math
import pytest
import sys
import os
import importlib
import copy
import time
from test_context.architecture import amati_agents_path
sys.path.append(amati_agents_path)

from product_management.scan_settings import ScanSettings
import product_management.product_schema
product_management.product_schema = importlib.reload(product_management.product_schema)
from product_management.product_schema import Prodpair
from integrations.keepa_api.keepa_api import get_keepa_time, ratings_from_keepa_ratings_csv

#import test_context.keepa_test_responses
#test_context.keepa_test_responses = importlib.reload(test_context.keepa_test_responses)
from test_context.keepa_test_responses import keepa_test_response_with_no_offers_no_ratings1, offers_good, ratings_good, ratings_good_variant_has_half, variant_ratings_small_sample, ratings_small_sample
from test_context.architecture import dev_api_host

def print_test_outcome(d):
    for key, value in d.items():
        print(f'{key}: {value}')
customer_id = "cus_QcwLkv0EVqYtYs" #prod 9002, which is used for e2e1 auto
client_id = '1007'
settings = {'Batch Name': 'MG', 'Client ID': client_id,'Email':'julian.a.ghadially@gmail.com', 'Pricing Units': 'Unit of Measure', 'rerank_algorithm':'single','Settings': {'AI Search': "Yes", 'Exclusions': {'Amazon in buybox': 'Include', 'Single-seller listings': 'Exclude'}, 'Human Quality Check': 'No', 'Priority': 'Standard', 'ROI Cutoff': 0, 'Revenue Cutoff': 50, 'Sales Volume': 'n/a', 'Check Match History':'No','Check Requests':'No','Seller Costs': {'FBM': 1, 'Price Discounts': 1, 'Shipping to Amazon': 'None','Peak Volume':"Auto",'Inbound Locations':'4+', 'Low Inventory Percentage':0}}, 'Type': 'Wholesale', 'Stripe ID': customer_id}
settings = ScanSettings(settings)

keepa_categories = {'133140011': 'Kindle Store', '9013971011': 'Video Shorts', '2350149011': 'Apps & Games', '165796011': 'Baby Products', '163856011': 'Digital Music', '13727921011': 'Alexa Skills', '165793011': 'Toys & Games', '2972638011': 'Patio, Lawn & Garden', '283155': 'Books', '2617941011': 'Arts, Crafts & Sewing', '229534': 'Software', '3375251': 'Sports & Outdoors', '2238192011': 'Gift Cards', '468642': 'Video Games', '11260432011': 'Handmade Products', '7141123011': 'Clothing, Shoes & Jewelry', '1064954': 'Office Products', '16310101': 'Grocery & Gourmet Food', '228013': 'Tools & Home Improvement', '2625373011': 'Movies & TV', '11091801': 'Musical Instruments', '4991425011': 'Collectibles & Fine Art', '2619525011': 'Appliances', '2619533011': 'Pet Supplies', '2335752011': 'Cell Phones & Accessories', '16310091': 'Industrial & Scientific', '10272111': 'Everything Else', '5174': 'CDs & Vinyl', '3760911': 'Beauty & Personal Care', '1055398': 'Home & Kitchen', '265523': 'Stores', '172282': 'Electronics', '15684181': 'Automotive', '599858': 'Magazine Subscriptions', '3760901': 'Health & Household', '18145289011': 'Audible Books & Originals','284507':'Kitchen & Dining',"541966":"Computers & Accessories","9000000000000002":"Amazon Renewed"}


#=====================
#helper functions
#=====================

def apply_fee_scenario_inputs(test_response, pp, scenario):
    price = scenario['price']
    test_response['categories'] = [scenario['category']]
    #if str(test_response['categories']) == '7141123011':
    #    test_response['categories'] = [fake_cateogry['Beauty & Personal Care']]
    test_response['stats']['current'][1] = price * 100
    test_response['stats']['buyBoxPrice'] = price * 100
    test_response['stats']['avg30'][1] = price * 100
    test_response['stats']['avg90'][1] = price * 100
    
    # Add package dimensions if present in scenario
    if 'package_weight' in scenario:
        test_response['packageWeight'] = scenario['package_weight']
        test_response['packageHeight'] = scenario['package_height']
        test_response['packageLength'] = scenario['package_length']
        test_response['packageWidth'] = scenario['package_width']
    return test_response, pp

def apply_volume_scenario_inputs(test_response, pp, price=50, bsr=0, bsr_category=None, spv=0, reviews=None,offers=None, all_variant_ratings = None, variant_ratings = None,number_of_variants = 1, oos_amz = 1, total_offer_ct=None, fba_sellers=None, nonfba_sellers = None):
    end_t = get_keepa_time(time.time())
    test_response['stats']['current'][1] = price * 100
    test_response['stats']['buyBoxPrice'] = price * 100
    test_response['stats']['avg30'][1] = price * 100
    test_response['stats']['avg90'][1] = price * 100
    test_response['stats']['current'][3] = bsr
    test_response['stats']['avg30'][3] = bsr
    test_response['salesRankReference'] = bsr_category
    test_response['monthlySold'] = spv
    pp['Social Proof Volume'] = 0  # get it from monthlySold
    if 'Reviews Volume' in pp.keys():
        del pp['Reviews Volume']
    if reviews is not None:
        #this assumes we got reviews from db.requests
        pp['Reviews'] = reviews   
    test_response['stats']['outOfStockCountAmazon30'] = oos_amz * 100  # amazon oos. keepa requires value from 0-100
    test_response['stats']['outOfStockPercentage30'][0] = oos_amz * 100  # amazon oos
    test_response['stats']['outOfStockPercentage30'][1] = 0  # new oos
    #test_response['stats']['buyBoxIsFBA']
    if number_of_variants == 1:
        test_response['variationCSV'] = []
    elif number_of_variants > 1:
        variations = ['B005CPZFWQ','B00JKQE8JO','B09NFBKPRZ','B0BVV2ZRWY']
        test_response['variationCSV'] = variations[0:number_of_variants-1]
    elif number_of_variants > 5:
        raise Exception('please build out more variants')
    else:
        raise Exception('please supply number of variants 1 or more')
    
    print(f"inside apply_volume_scenario_inputs. will we add csv?: {'csv' not in test_response and all_variant_ratings is not None or offers is not None}")
    if 'csv' not in test_response and (all_variant_ratings is not None or offers is not None):
        test_response['csv'] = [[]]*18
        test_response['csv'][1] = [end_t, price]
        test_response['csv'][3] = [end_t,bsr]
    if offers is not None:
        test_response['offersSuccessful'] = True
        test_response['offers'] = offers
    if all_variant_ratings is not None:
        print('adding all variant ratings')
        test_response['csv'][17] = all_variant_ratings
    if variant_ratings is not None:
        print('adding variant ratings')
        if 'reviews' not in test_response.keys():
            test_response['reviews'] = {'ratingCount':variant_ratings}
        else:
            test_response['reviews']['ratingCount'] = variant_ratings
    
    #sellers
    if fba_sellers is not None:
        test_response['buyBoxEligibleOfferCounts'][0] = fba_sellers
    if nonfba_sellers is not None:
        test_response['buyBoxEligibleOfferCounts'][1] = nonfba_sellers
    if total_offer_ct is not None:
        if 'stats' not in test_response.keys():
            test_response['stats'] = {'totalOferCount': total_offer_ct}
        test_response['stats']['totalOfferCount'] = total_offer_ct
        test_response['csv_count_new'] = [end_t - 60*24*1, total_offer_ct, end_t, total_offer_ct]
    return test_response, pp


class TestCalculations:
    '''
    Test suite for Margin Geek calculations and related unit tests
    '''
    fake_category = {
        'Beauty & Personal Care':3760911, #8% up to $10 | 15%
        'Home & Kitchen': 1055398, # 15%
        'Electronics': 172282 # 8%
    }
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment before each test"""
        self.app_mode = os.environ.get('TEST_APP_MODE','prod')
        if self.app_mode == 'prod':
            print('Running tests in prod')
            self.is_dev = False
            self.api_host = 'https://api.margingeek.com'
            self.headers = {"Origin": "https://app.margingeek.com"}
            self.customer_id = customer_id  # Use a test customer ID
            self.client_id = "1007"
        else:
            print('Running tests in dev')
            self.is_dev = True
            self.api_host = dev_api_host # 'https://dev-api.margingeek.com:444' #'http://127.0.0.1:5000'  # Change to https://dev-api.margingeek.com:444 for dev testing
            self.headers = {"Origin": "https://margin-geek-portal.vercel.app"}
            self.customer_id = customer_id  # Use a test customer ID
            self.client_id = "1007"
        
        self.supply_row_basic = {'MG Idx': '101300004342','Identifier': '100800000888-B01IA9BEQG','Code': '70501013007','Brand': 'Neutrogena','Product Description': 'Neutrogena Fragrance Free Norwegian Formula Hand Cream','Source': '','Source Url': 'file://1013/e2e1 copy.csv','Purchase Price':'1.00','Date Updated': '20250201'}
        self.row_basic = {'Index-ASIN': '101300004342-B00JKQE8JO','MG Idx':'101300004342','_Margin': '0.16','Summary': 'Yes','Listing Notes': 'Only 2 seller(s)','Identifier': '100800000888-B01IA9BEQG','Code': '70501013007','Brand': 'Neutrogena','Product Description': 'Neutrogena Fragrance Free Norwegian Formula Hand Cream','Listing ID': 'B00JKQE8JO','Listing Link': 'https://www.amazon.com/dp/B00JKQE8JO','Listing Description': 'Neutrogena Norwegian Formula Moisturizing Hand Cream Formulated with Glycerin for Dry, Rough Hands, Fragrance-Free Intensive Hand Lotion, 2 Oz, Pack of 6','_': '','AI Match': 'Match','QA Match': '','Conversion Factor': '0.17','Purchase Price Units': 'Each','Purchase Price': '4.9','__': '','Price': '49.27','Unit COGS': '29.4','Unit Costs': '41.52','Unit Profit': '7.75','ROI': '0.26','Margin': '0.16','_______': '','Monthly Volume': '18.48','Monthly Revenue': '910.51','Monthly Profit': '143.29','________': '','BSR': '66191','BSR 30': '69091','Social Proof Volume': '0','Reviews Volume': '80','Volume, All Sellers': '110.9','Number of Sellers': '2','Number of Sellers, Adjusted (Incl. 1 New Seller)': '2','Number of Variants': '2','Out of Stock Percentage - New': '21','Out of Stock Percentage - Amazon': '100','Buy Box Suppressed': 'TRUE','Referral Fee': '7.05','FBA Fulfillment Fee': '4.99','Storage Fees': '0.07','Shipping Cost': '0','Fee Comments': 'Base Fulfillment Fee (FBA Non-Peak): $4.99 Low Inventory Fee: $0.0 Inbound Fulfillment Fee: $0 FBM Multiplier: 100%','Fees and Fulfillment': '12.12','Market Price': '47.02','Price 30 Day': '49.27','Weight (lb)': '1.12','Dimension 1 - Longest (in)': '14.84','Dimension 2 (in)': '5.55','Dimension 3 - Shortest (in)': '1.97','Main Category': 'Beauty & Personal Care','Enough Data?': 'TRUE','_________': '','Source': '','Source Url': 'file://1013/e2e1 copy.csv','Latest Scan - Demand': '20250201','Latest Scan - Source': '20250131','Date Updated': '20250201','Listing Flags': 'Only 2 seller(s).','Analysis Flags': '120'}
        #settings1: 
        adjust_for_variants = 'Yes'
        self.settings1 = {'Batch Name': 'MG', 'Client ID': self.client_id, 'Email': 'julian.a.ghadially@gmail.com', 'Pricing Units': 'Unit of Measure', 'rerank_algorithm': 'single', 'Settings': {'AI Search': 'Yes', 'Exclusions': {'Amazon in buybox': 'Include', 'Single-seller listings': 'Exclude'}, 'Human Quality Check': 'No', 'Priority': 'Standard', 'ROI Cutoff': 0, 'Revenue Cutoff': 50, 'Sales Volume': 'n/a', 'Check Match History': 'No', 'Check Requests': 'No', 'Seller Costs': {'FBM': 1, 'Price Discounts': 1, 'Shipping to Amazon': 'None', 'Peak Volume': 'No', 'Inbound Locations': '4+', 'Low Inventory Percentage': 0, 'Low Inventory History': '14-21'}, 'Adjust for Variants': adjust_for_variants, 'Seller Count Replacement': 6, 'FBA Seller Count Replacement': 2, 'Other FBA Seller Weight': 0.5, 'FBM-Competitive Seller Weight': 0.5, 'Other FBM Seller Weight': 0.05}, 'Type': 'Wholesale', 'Stripe ID': self.customer_id}
        #settings2: 
        adjust_for_variants = 'No'
        self.settings2 = {'Batch Name': 'MG', 'Client ID': self.client_id, 'Email': 'julian.a.ghadially@gmail.com', 'Pricing Units': 'Unit of Measure', 'rerank_algorithm': 'single', 'Settings': {'AI Search': 'Yes', 'Exclusions': {'Amazon in buybox': 'Include', 'Single-seller listings': 'Exclude'}, 'Human Quality Check': 'No', 'Priority': 'Standard', 'ROI Cutoff': 0, 'Revenue Cutoff': 50, 'Sales Volume': 'n/a', 'Check Match History': 'No', 'Check Requests': 'No', 'Seller Costs': {'FBM': 1, 'Price Discounts': 1, 'Shipping to Amazon': 'None', 'Peak Volume': 'No', 'Inbound Locations': '4+', 'Low Inventory Percentage': 0, 'Low Inventory History': '14-21'}, 'Adjust for Variants': adjust_for_variants, 'Seller Count Replacement': 6, 'FBA Seller Count Replacement': 2, 'Other FBA Seller Weight': 0.5, 'FBM-Competitive Seller Weight': 0.5, 'Other FBM Seller Weight': 0.05}, 'Type': 'Wholesale', 'Stripe ID': self.customer_id}

    def test_fee_calculations(self):
        """Test various Amazon fee calculations including referral fees and fulfillment fees"""
        import copy
    
        # Define test scenarios
        test_scenarios = [
            {
                "name": "Referral fee: Beauty under $10",
                "price": 9.00,
                "category": TestCalculations.fake_category['Beauty & Personal Care'],
                "expected_value": max(9.00 * .08, 0.3),
                "expected_value_column": 'Referral Fee',
                "description": "Beauty & Personal Care under $10 should have 8% referral fee"
            },
            {
                "name": "Referral fee: Beauty over $10",
                "price": 50.00,
                "category": TestCalculations.fake_category['Beauty & Personal Care'],
                "expected_value": max(50.00 * .15, 0.3),
                "expected_value_column": 'Referral Fee',
                "description": "Beauty & Personal Care over $10 should have 15% referral fee"
            },
            {
                "name": "Referral fee: Electronics",
                "price": 50.00,
                "category": TestCalculations.fake_category['Electronics'],
                "expected_value": max(50.00 * .08, 0.3),
                "expected_value_column": 'Referral Fee',
                "description": "Electronics should have 8% referral fee"
            },
            # TODO: Add Electronics Accessories test
            # Electronics Accessories, assert 15% referral fee under $100
            {
                "name": "Fulfillment fee: Small standard non-peak",
                "price": 50.00,
                "category": TestCalculations.fake_category['Beauty & Personal Care'],
                "package_weight": 0.12 * 453.59237,  # lb to gram
                "package_height": 1 * 25.4,  # in to mm
                "package_length": 1 * 25.4,  # in to mm
                "package_width": 0.5 * 25.4,  # in to mm
                "peak_volume": "No",
                "expected_value": 3.06,
                "expected_value_column": 'FBA Fulfillment Fee',
                "description": "< 0.125 lb & Small standard = $3.06 non-peak; $3.25 peak" 
            },
            {
                "name": "Fulfillment fee: Small standard Peak",
                "price": 50.00,
                "category": TestCalculations.fake_category['Beauty & Personal Care'],
                "package_weight": 0.12 * 453.59237,  # lb to gram
                "package_height": 1 * 25.4,  # in to mm
                "package_length": 1 * 25.4,  # in to mm
                "package_width": 0.5 * 25.4,  # in to mm
                "peak_volume": "Yes",
                "expected_value": 3.25,
                "expected_value_column": 'FBA Fulfillment Fee',
                "description": "< 0.125 lb & Small standard = $3.06 non-peak; $3.25 peak" 
            },
            {
                "name": "Fulfillment fee: Large standard peak",
                "price": 50.00,
                "category": TestCalculations.fake_category['Beauty & Personal Care'],
                "package_weight": 2.1 * 453.59237,  # lb to gram
                "package_height": 4 * 25.4,  # in to mm
                "package_length": 16 * 25.4,  # in to mm
                "package_width": 4 * 25.4,  # in to mm
                "peak_volume": "No",
                "expected_value": 5.87,
                "expected_value_column": 'FBA Fulfillment Fee',
                "description": " 2.1 lb & large standard = $5.87 non-peak; $6.24 peak"
            },
            {
                "name": "Fulfillment fee: Large standard Non-Peak",
                "price": 50.00,
                "category": TestCalculations.fake_category['Beauty & Personal Care'],
                "package_weight": 2.1 * 453.59237,  # lb to gram
                "package_height": 4 * 25.4,  # in to mm
                "package_length": 16 * 25.4,  # in to mm
                "package_width": 4 * 25.4,  # in to mm
                "peak_volume": "Yes",
                "expected_value": 6.24,
                "expected_value_column": 'FBA Fulfillment Fee',
                "description": " 2.1 lb & large standard = $5.87 non-peak; $6.24 peak"
            },
            # Add more scenarios for large standard and apparel items
        ]
        # Run each test scenario
        for scenario in test_scenarios:
            print(f"\nRunning: {scenario['name']}")
            
            # Setup test
            keepa_test_responses1 = [copy.deepcopy(keepa_test_response_with_no_offers_no_ratings1)]
            test_response = copy.deepcopy(keepa_test_responses1[0])
            test_row = copy.deepcopy(self.row_basic)
            pp = Prodpair(test_row)
            
            # Configure test response based on scenario
            test_response, pp = apply_fee_scenario_inputs(test_response, pp, scenario)
            
            # Configure settings
            test_settings = copy.deepcopy(self.settings1)
            if 'peak_volume' in scenario:
                test_settings['Settings']['Seller Costs']['Peak Volume'] = scenario['peak_volume']
            
            # Run test
            pp.fake_keepa([test_response])
            pp.assess_fees(test_settings)
            
            # Check results
            
            expected_value = scenario['expected_value']
            expected_value_column = scenario['expected_value_column']
            actual_value = pp[expected_value_column]
                
            calculation_accuracy = actual_value == expected_value
            
            test_outcome = {
                "Test Completion": True,
                "Calculation accuracy": calculation_accuracy,
            }
            
            if not calculation_accuracy:
                test_outcome['Comments'] = f"Actual {expected_value_column}: {actual_value} vs expected {expected_value_column}: {expected_value}"
            
            print_test_outcome(test_outcome)
            
            # Assert for pytest to catch failures
            assert calculation_accuracy, f"{scenario['name']} failed. Expected {expected_value}, got {actual_value} for {expected_value_column}"
    
    def test_volume_calculations(self):
        variant_share_ratings_good_half_three_variants = (((20/190*30)+1)  /   (( (14+math.ceil(53/2))  /190*30)+3))
        variant_share_small_sample = ((0 / 150 * 30) + 1) / ((4 / 150 * 30) + 3)
        test_scenarios = [
            {
                "name": "Volume scenario 1: BSR-based volume",
                "bsr": 10000,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": 0,
                "reviews": 0,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "expected_value": 1515,
                "expected_value_column": 'Volume, All Sellers',
                "settings":self.settings1,
                "scenario description": "bsr driven volume"
            },
            {
                "name": "Volume scenario 2: Social proof volume",
                "bsr": 10000,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": 2000,
                "reviews": 99999,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "expected_value": 2000,
                "expected_value_column": 'Volume, All Sellers',
                "settings":self.settings1,
                "scenario description": "1) bsr vs spv. spv should win. 2) volume"
            }, 
            {
                "name": "Market Volume scenario 3: reviews market volume",
                "bsr": -1,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": -1,
                "reviews": ratings_good[-1],
                "all_variants_ratings_csv": ratings_good,
                "variant_ratings_csv": ratings_good,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "expected_value": (14+(53/2))/(190/30) * (1 / 0.05 / 2), #in ratings_good, there were 14 reviews over 6 months (190 days). but there were also 44 removed reviews which count as half, up to 15... The rest of the formula is assuming 5% leave reviews, plus conservating adjustment by half
                "expected_value_column": 'Volume, All Sellers',
                "settings": self.settings1,
                "scenario description": "reviews with reviews csv"
            }, 
            {
                "name": "Market Volume scenario 4: reviews market volume without reviews csv",
                "bsr": -1,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": -1,
                "reviews": 2000,
                "all_variants_ratings_csv": [],
                "variant_ratings_csv": [],
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "expected_value": 2000 * (1/0.05)/12/5/2,
                "expected_value_column": 'Volume, All Sellers',
                "settings": self.settings1,
                "scenario description": "reviews without reviews csv"
            },
            {
                "name": "Volume Seller Adjustments 1",
                "bsr": 10000,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": -1,
                "reviews": 2000,
                "offers_csv": offers_good,
                "all_variants_ratings_csv": None,
                "variant_ratings_csv": None,
                "variants": 1,
                "fba_sellers": 3,    #Make sure this aligns with offers_csv. (aligns with offers_good)
                "nonfba_sellers": 2, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "total_offer_ct": 5, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "oos_amz": 1,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "settings": self.settings1,
                "expected_value": (1515 * 1) / ((1*1 + 1 * self.settings1['Settings']['FBM-Competitive Seller Weight'] + 2 * self.settings1['Settings']['Other FBA Seller Weight'] + 1 * self.settings1['Settings']['Other FBM Seller Weight'])+ 1),
                "expected_value_column": 'Monthly Volume',
                "settings":self.settings1,
                "scenario description": "Incorporate Seller adjustments via populated offers csv"
            },
            {
                "name": "Volume Seller Adjustments 2 - missing offers",
                "bsr": 10000,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": -1,
                "reviews": 2000,
                "offers_csv": None,
                "all_variants_ratings_csv": None,
                "variant_ratings_csv": None,
                "variants": 1,
                "fba_sellers": 3,  #Make sure this aligns with offers_csv. (aligns with offers_good)
                "nonfba_sellers": 2, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "total_offer_ct": 5, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "oos_amz": 1,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "settings": self.settings1,
                "expected_value": (1515 * 1) / ((3*1 + 2 * self.settings1['Settings']['FBM-Competitive Seller Weight'] + 0* self.settings1['Settings']['Other FBA Seller Weight'] + 0 * self.settings1['Settings']['Other FBM Seller Weight'])+ 1),
                "expected_value_column": 'Monthly Volume',
                "scenario description": "Incorporate Seller adjustments with missing offers csv. FBA seller and FBM sellers should replace FBM-Competitive",
            },
            {
                "name": "Volume Seller Adjustments 3 - missing data",
                "bsr": 10000,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": -1,
                "reviews": 2000,
                "offers_csv": None,
                "all_variants_ratings_csv": None,
                "variant_ratings_csv": None,
                "variants": 1,
                "fba_sellers": -1,
                "nonfba_sellers": -1,
                "total_offer_ct": -1,
                "oos_amz": 1,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "settings": self.settings1,
                "expected_value": (1515 * 1) / (self.settings1['Settings']['FBA Seller Count Replacement'] * 1 + (self.settings1['Settings']['Seller Count Replacement'] - self.settings1['Settings']['FBA Seller Count Replacement'] )* self.settings1['Settings']['FBM-Competitive Seller Weight'] + 1),
                "expected_value_column": 'Monthly Volume',
                "scenario description": "Incorporate Seller adjustments with missing offers csv and missing seller counts. Should not return a volume",
            },
            {
                "name": "Volume Adjustment: Variant share",
                "bsr": 10000,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": -1,
                "reviews": 2000,
                "offers_csv": offers_good,
                "all_variants_ratings_csv": ratings_good,
                "variant_ratings_csv": ratings_good_variant_has_half,
                "variants": 3,
                "fba_sellers": 3, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "nonfba_sellers":2, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "total_offer_ct": 5, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "oos_amz": 1,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "settings": self.settings1,
                "expected_value": (1515 * variant_share_ratings_good_half_three_variants) / ((1*1 + 1 * self.settings1['Settings']['FBM-Competitive Seller Weight'] + 2 * self.settings1['Settings']['Other FBA Seller Weight'] + 1 * self.settings1['Settings']['Other FBM Seller Weight'])+ 1),
                "expected_value_column": 'Monthly Volume',
                "scenario description": "Incorporate variant share (and good offers) using good variants data"
            },
            {
                "name": "Volume Adjustment: Variant share small sample",
                "bsr": 10000,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": -1,
                "reviews": 2000,
                "offers_csv": offers_good,
                "all_variants_ratings_csv": ratings_small_sample,
                "variant_ratings_csv": variant_ratings_small_sample,
                "variants": 3,
                "fba_sellers": 3, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "nonfba_sellers":2, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "total_offer_ct": 5, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "oos_amz": 1,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "settings": self.settings1,
                "expected_value": (1515 * variant_share_small_sample) / ((1*1 + 1 * self.settings1['Settings']['FBM-Competitive Seller Weight'] + 2 * self.settings1['Settings']['Other FBA Seller Weight'] + 1 * self.settings1['Settings']['Other FBM Seller Weight'])+ 1),
                "expected_value_column": 'Monthly Volume',
                "scenario description": "Incorporate variant share (and good offers) using good variants data"
            },
            {
                "name": "Volume Adjustment: Variant share No Adjust",
                "bsr": 10000,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": -1,
                "reviews": 2000,
                "offers_csv": offers_good,
                "all_variants_ratings_csv": ratings_good,
                "variant_ratings_csv": ratings_good_variant_has_half,
                "variants": 3,
                "fba_sellers": 3, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "nonfba_sellers":2, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "total_offer_ct": 5, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "oos_amz": 1,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "settings": self.settings2,
                "expected_value": (1515) / ((1*1 + 1 * self.settings1['Settings']['FBM-Competitive Seller Weight'] + 2 * self.settings1['Settings']['Other FBA Seller Weight'] + 1 * self.settings1['Settings']['Other FBM Seller Weight'])+ 1),
                "expected_value_column": 'Monthly Volume',
                "scenario description": "Incorporate variant share (and good offers) using good variants data"
            },
            {
                "name": "Volume Adjustment: Variant share with social proof",
                "bsr": 10000,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": 500,
                "reviews": 2000,
                "offers_csv": offers_good,
                "all_variants_ratings_csv": ratings_good,
                "variant_ratings_csv": ratings_good_variant_has_half,
                "variants": 3,
                "fba_sellers": 3, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "nonfba_sellers":2, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "total_offer_ct": 5, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "oos_amz": 1,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "settings": self.settings1,
                "expected_value": (500) / ((1*1 + 1 * self.settings1['Settings']['FBM-Competitive Seller Weight'] + 2 * self.settings1['Settings']['Other FBA Seller Weight'] + 1 * self.settings1['Settings']['Other FBM Seller Weight'])+ 1),
                "expected_value_column": 'Monthly Volume',
                "scenario description": "Incorporate variant share (and good offers) using good variants data"
            },
            {
                "name": "Volume Adjustment: Variant share with no data",
                "bsr": 10000,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": -1,
                "reviews": 2000,
                "offers_csv": offers_good,
                "all_variants_ratings_csv": [],
                "variant_ratings_csv": [],
                "variants": 3,
                "fba_sellers": 3, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "nonfba_sellers":2, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "total_offer_ct": 5, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "oos_amz": 1,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "settings": self.settings1,
                "expected_value": (1515 / 3) / ((1*1 + 1 * self.settings1['Settings']['FBM-Competitive Seller Weight'] + 2 * self.settings1['Settings']['Other FBA Seller Weight'] + 1 * self.settings1['Settings']['Other FBM Seller Weight'])+ 1),
                "expected_value_column": 'Monthly Volume',
                "scenario description": "Incorporate variant share (and good offers) with no variants data"
            },
            {
                "name": "Volume Adjustment: Amazon OOS",
                "bsr": 10000,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": -1,
                "reviews": 2000,
                "offers_csv": offers_good,
                "all_variants_ratings_csv": ratings_good,
                "variant_ratings_csv": ratings_good_variant_has_half,
                "variants": 3,
                "fba_sellers": 3, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "nonfba_sellers":2, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "total_offer_ct": 5, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "oos_amz": .10,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "settings": self.settings1,
                "expected_value": ((1515 * variant_share_ratings_good_half_three_variants) * (1/4)) / ((1*1 + 1 * self.settings1['Settings']['FBM-Competitive Seller Weight'] + 2 * self.settings1['Settings']['Other FBA Seller Weight'] + 1 * self.settings1['Settings']['Other FBM Seller Weight'])+ 1),
                "expected_value_column": 'Monthly Volume',
                "scenario description": "Incorporate amazon oos (and good offers and good variants) with no variants data"
            },
            {
                "name": "Volume Adjustment: Amazon OOS 40%",
                "bsr": 10000,
                "bsr_category": TestCalculations.fake_category['Beauty & Personal Care'],
                "spv": -1,
                "reviews": 2000,
                "offers_csv": offers_good,
                "all_variants_ratings_csv": ratings_good,
                "variant_ratings_csv": ratings_good_variant_has_half,
                "variants": 3,
                "fba_sellers": 3, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "nonfba_sellers":2, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "total_offer_ct": 5, #Make sure this aligns with offers_csv. (aligns with offers_good)
                "oos_amz": .40,
                "keepa_response": keepa_test_response_with_no_offers_no_ratings1,
                "settings": self.settings1,
                "expected_value": ((1515 * variant_share_ratings_good_half_three_variants) * .4) / ((1*1 + 1 * self.settings1['Settings']['FBM-Competitive Seller Weight'] + 2 * self.settings1['Settings']['Other FBA Seller Weight'] + 1 * self.settings1['Settings']['Other FBM Seller Weight'])+ 1),
                "expected_value_column": 'Monthly Volume',
                "scenario description": "Incorporate amazon oos (and good offers and good variants) with no variants data"
            }
        ]
        for scenario in test_scenarios:
            print(f"\nRunning: {scenario['name']}")
            
            test_response = copy.deepcopy(scenario['keepa_response'])
            test_row = copy.deepcopy(self.row_basic)
            settings = scenario['settings']
            pp = Prodpair(test_row)
            price = 46.10
            
            # Apply the scenario inputs
            test_response, pp = apply_volume_scenario_inputs(
                test_response, 
                pp, 
                price=price,
                bsr=scenario['bsr'], 
                bsr_category=scenario['bsr_category'], 
                spv = scenario['spv'], 
                reviews = scenario['reviews'],
                offers = scenario.get('offers_csv', None),
                all_variant_ratings = scenario.get('all_variants_ratings_csv',None),
                variant_ratings = scenario.get('variant_ratings_csv',None),
                number_of_variants=scenario.get('variants',1),
                fba_sellers=scenario.get('fba_sellers', None),
                nonfba_sellers=scenario.get('nonfba_sellers', None),
                total_offer_ct=scenario.get('total_offer_ct', None),
                oos_amz= scenario.get('oos_amz',1)
            )
            print(f"offers before: {test_response.get('offers','')}")
            
            pp.fake_keepa([test_response])

            
            test_settings = copy.deepcopy(settings)
            pp.assess_fees(test_settings)
            pp.forecast_volume(test_settings)
            pp.forecast_profitability(test_settings)
            
            value_key = scenario['expected_value_column']
            actual_value = pp[value_key]
            expected_value = scenario['expected_value']
            calculation_accuracy = abs(actual_value - expected_value) < 3
            
            test_outcome = {
                "Test Completion": True,
                "Calculation accuracy": calculation_accuracy,
            }
            
            if not calculation_accuracy:
                test_outcome['Comments'] = f"Actual value: {actual_value} vs expected value: {expected_value} for {value_key}"
            
            print_test_outcome(test_outcome)
            
                
            
            #for troubleshooting:
            volume_build_cols = ['BSR 30','Social Proof Volume','Reviews','Reviews Volume', 'Volume, All Sellers','Number of Sellers','Number of Sellers, Adjusted (Incl. 1 New Seller)','Number of Variants','Variant Share','Out of Stock Percentage - New','Out of Stock Percentage - Amazon','Buy Box Suppressed', 'Monthly Volume']
            volume_build_statement = ''
            for key in volume_build_cols:
                if key in pp.keys():
                    volume_build_statement  = volume_build_statement + f" {key} : {pp[key]} | "
            
            if not calculation_accuracy:
                print("\n".join(volume_build_statement.split("|"))) 
            # Assert for pytest to catch failures
            assert calculation_accuracy, f'''Volume calculation failed for {scenario['name']}. Expected {expected_value}, got {actual_value} for {value_key}

            Volume Build:
            {volume_build_statement}'''

if __name__ == '__main__':
    pytest.main([__file__])


if False:
    self = TestCalculations()
    self.setup()

    

    # fulfillment fee scenario 1:  < 0.125 lb & Small standard = $3.06 non-peak; $3.25 peak
    test_response = copy.deepcopy(keepa_test_responses1[0])
    test_row = copy.deepcopy(row)
    pp = Prodpair(test_row)
    price = 50.00
    if str(test_response['categories']) == '7141123011': #if apparel, change
        test_response['categories'] = [fake_category['Beauty & Personal Care']]
    test_response['stats']['current'][1] = price * 100
    test_response['stats']['buyBoxPrice'] = price * 100
    test_response['stats']['avg30'][1] = price * 100
    test_response['stats']['avg90'][1] = price * 100
    test_response['packageWeight'] = 0.12 / 0.06102 #in to gram
    test_response['packageHeight'] = 1 * 25.4 #in to mm
    test_response['packageLength'] = 1 * 25.4 #in to mm
    test_response['packageWidth'] = 0.5 * 25.4 #in to mm
    test_settings = copy.deepcopy(settings)
    test_settings['Settings']['Seller Costs']['Peak Volume'] = 'No'
    pp.fake_keepa([test_response])

    #non-Peak
    pp.assess_fees(test_settings)
    expected_value = 3.06
    actual_value = pp['FBA Fulfillment Fee']
    calculation_accuracy = actual_value == expected_value

    #Peak
    test_settings['Settings']['Seller Costs']['Peak Volume'] = 'Yes'
    pp.assess_fees(test_settings)
    expected_value_peak = 3.25
    actual_value_peak = pp['FBA Fulfillment Fee']
    calculation_accuracy_peak = actual_value == expected_value

    test_outcome = {
        "Test Completion": True,
        "Calculation accuracy": calculation_accuracy and calculation_accuracy_peak,
    }
    if not calculation_accuracy:
        test_outcome['Comments'] = f"Actual value (Non-Peak): {actual_value} vs expected value (Non-Peak): {expected_value}. Peak value: {actual_value_peak} vs expected value (Peak): {expected_value_peak}"
    print_test_outcome(test_outcome)

    # fulfillment fee scenario 2:  2.1 lb & large standard = $5.87 non-peak; $6.24 peak
    test_response = copy.deepcopy(keepa_test_responses1[0])
    test_row = copy.deepcopy(row)
    pp = Prodpair(test_row)
    price = 50.00
    if str(test_response['categories']) == '7141123011': #if apparel, change
        test_response['categories'] = [fake_category['Beauty & Personal Care']]
    test_response['stats']['current'][1] = price * 100
    test_response['stats']['buyBoxPrice'] = price * 100
    test_response['stats']['avg30'][1] = price * 100
    test_response['stats']['avg90'][1] = price * 100
    test_response['packageWeight'] = 2.1 * 453.59237 #lb to gram
    test_response['packageHeight'] = 4 * 25.4 #in to mm
    test_response['packageLength'] = 16 * 25.4 #in to mm
    test_response['packageWidth'] = 4 * 25.4 #in to mm

    test_settings = copy.deepcopy(settings)
    test_settings['Settings']['Seller Costs']['Peak Volume'] = 'No'
    pp.fake_keepa([test_response])

    #non-Peak
    pp.assess_fees(test_settings)
    expected_value = 5.87
    actual_value = pp['FBA Fulfillment Fee']
    calculation_accuracy = actual_value == expected_value

    #Peak
    test_settings['Settings']['Seller Costs']['Peak Volume'] = 'Yes'
    pp.assess_fees(test_settings)
    expected_value_peak = 6.24
    actual_value_peak = pp['FBA Fulfillment Fee']
    calculation_accuracy_peak = actual_value == expected_value

    test_outcome = {
        "Test Completion": True,
        "Calculation accuracy": calculation_accuracy and calculation_accuracy_peak,
    }
    if not calculation_accuracy:
        test_outcome['Comments'] = f"Actual value (Non-Peak): {actual_value} vs expected value (Non-Peak): {expected_value}. Peak value: {actual_value_peak} vs expected value (Peak): {expected_value_peak}"
    print_test_outcome(test_outcome)

    # fulfillment fee scenario 3:  Apparel & 2.1 lb = $6.83 non-peak; $7.04 peak
    test_response = copy.deepcopy(keepa_test_responses1[0])
    test_row = copy.deepcopy(row)
    pp = Prodpair(test_row)
    price = 50.00
    test_response['categories'] = [7141123011] #apparel
    test_response['stats']['current'][1] = price * 100
    test_response['stats']['buyBoxPrice'] = price * 100
    test_response['stats']['avg30'][1] = price * 100
    test_response['stats']['avg90'][1] = price * 100
    test_response['packageWeight'] = 2.1 * 453.59237 #lb to gram
    test_response['packageHeight'] = 4 * 25.4 #in to mm
    test_response['packageLength'] = 16 * 25.4 #in to mm
    test_response['packageWidth'] = 4 * 25.4 #in to mm

    test_settings = copy.deepcopy(settings)
    test_settings['Settings']['Seller Costs']['Peak Volume'] = 'No'
    pp.fake_keepa([test_response])

    #non-Peak
    pp.assess_fees(test_settings)
    expected_value = 6.83
    actual_value = pp['FBA Fulfillment Fee']
    calculation_accuracy = actual_value == expected_value

    #Peak
    test_settings['Settings']['Seller Costs']['Peak Volume'] = 'Yes'
    pp.assess_fees(test_settings)
    expected_value_peak = 7.04
    actual_value_peak = pp['FBA Fulfillment Fee']
    calculation_accuracy_peak = actual_value == expected_value

    test_outcome = {
        "Test Completion": True,
        "Calculation accuracy": calculation_accuracy and calculation_accuracy_peak,
    }
    if not calculation_accuracy:
        test_outcome['Comments'] = f"Actual value (Non-Peak): {actual_value} vs expected value (Non-Peak): {expected_value}. Peak value: {actual_value_peak} vs expected value (Peak): {expected_value_peak}"
    print_test_outcome(test_outcome)

    # fulfillment fee scenario 4:  Dangerouse & 2.1 lb = $6.56 non-peak; $7.30 peak

    #Peak
    calculation_accuracy = False
    calculation_accuracy_peak = False

    test_outcome = {
        "Test Completion": True,
        "Calculation accuracy": calculation_accuracy and calculation_accuracy_peak,
    }
    #if not calculation_accuracy:
    #    test_outcome['Comments'] = f"Actual value (Non-Peak): {actual_value} vs expected value (Non-Peak): {expected_value}. Peak value: {actual_value_peak} vs expected value (Peak): {expected_value_peak}"
    print_test_outcome(test_outcome)


    #test profitability

    # Unit COGS scenario 1:  Conversion factor: 2 & Purchase price = $10, assert Unit COGS = $5
    #inputs
    cf = 2
    purchase_price = 10
    price_discount = 0
    expected_value = 5.0
    #run
    test_response = copy.deepcopy(keepa_test_responses1[0])
    test_row = copy.deepcopy(row)
    pp = Prodpair(test_row)
    price = 50
    test_response['stats']['current'][1] = price * 100
    test_response['stats']['buyBoxPrice'] = price * 100
    test_response['stats']['avg30'][1] = price * 100
    test_response['stats']['avg90'][1] = price * 100
    pp['Purchase Price'] = purchase_price
    pp['Conversion Factor'] = cf
    if 'Conversion Factor_user' in pp.keys():
        pp.user_set({'Conversion Factor', 2})
    pp.fake_keepa([test_response])

    test_settings = copy.deepcopy(settings)
    test_settings['Settings']['Seller Costs']['Price Discounts'] = price_discount
    pp.assess_fees(test_settings)
    pp.forecast_volume(test_settings)
    pp.forecast_profitability(test_settings)

    actual_value = pp['Unit COGS']
    calculation_accuracy = actual_value == expected_value
    test_outcome = {
        "Test Completion": True,
        "Calculation accuracy": calculation_accuracy,
    }
    if not calculation_accuracy:
        test_outcome['Comments'] = f"Actual value: {actual_value} vs expected value: {expected_value}"
    print_test_outcome(test_outcome)



    # Unit COGS scenario 2:  Conversion factor: .5 & Purchase price = $10, assert Unit COGS = $18
    #inputs
    cf = 0.5
    purchase_price = 10
    price_discount = .1
    expected_value = 18
    #run
    test_response = copy.deepcopy(keepa_test_responses1[0])
    test_row = copy.deepcopy(row)
    pp = Prodpair(test_row)
    price = 50
    test_response['stats']['current'][1] = price * 100
    test_response['stats']['buyBoxPrice'] = price * 100
    test_response['stats']['avg30'][1] = price * 100
    test_response['stats']['avg90'][1] = price * 100
    pp['Purchase Price'] = purchase_price
    pp['Conversion Factor'] = cf
    if 'Conversion Factor_user' in pp.keys():
        pp.user_set({'Conversion Factor', 2})
    pp.fake_keepa([test_response])

    test_settings = copy.deepcopy(settings)
    test_settings['Settings']['Seller Costs']['Price Discounts'] = price_discount
    pp.assess_fees(test_settings)
    pp.forecast_volume(test_settings)
    pp.forecast_profitability(test_settings)


    actual_value = pp['Unit COGS']
    calculation_accuracy = actual_value == expected_value
    test_outcome = {
        "Test Completion": True,
        "Calculation accuracy": calculation_accuracy,
    }
    if not calculation_accuracy:
        test_outcome['Comments'] = f"Actual value: {actual_value} vs expected value: {expected_value}"
    print_test_outcome(test_outcome)







    # Test volume:
    #volume scenario 1:
    #inputs

    
    # Volume, seller adjustments
    bsr = 10000
    bsr_category = fake_category['Beauty & Personal Care']
    spv = 1000
    reviews = 2000
    fba_sellers = 3
    nonfba_sellers = 2
    new_sellers_ct = 5
    total_offer_ct = 5
    amz_oos = 100
    expected_market = 1515
    expected_volume = 1515 / (3 + 2*.5 + 1)
    adjust_for_variants = 'No'

    test_response = copy.deepcopy(keepa_test_responses1[0])
    test_row = copy.deepcopy(row)
    pp = Prodpair(test_row)
    price = 50

    test_response, pp = apply_volume_scenario_inputs(test_response, pp, bsr= bsr, bsr_category= bsr_category, spv = spv, reviews = reviews)
    test_response['stats']['outOfStockCountAmazon30'] = amz_oos #amazon oos
    test_response['stats']['outOfStockPercentage30'][0] = amz_oos #amazon oos
    test_response['stats']['outOfStockPercentage30'][1] = 1 #new oos
    test_response['stats']['buyBoxIsAmazon'] = amz_oos < 100
    test_response['csv_count_new'][-1] = new_sellers_ct
    test_response['stats']['totalOfferCount'] = total_offer_ct
    test_response['buyBoxEligibleOfferCounts'] = [fba_sellers, nonfba_sellers, 0, 0, 0, 0, 0, 0]


    pp.fake_keepa([test_response])

    test_settings = copy.deepcopy(settings)
    test_settings['Settings']['Adjust for Variants'] = adjust_for_variants
    pp.assess_fees(test_settings)
    pp.forecast_volume(test_settings)
    pp.forecast_profitability(test_settings)


    actual_market_value = pp['Volume, All Sellers']
    expected_market_value = expected_market
    actual_value = pp['Monthly Volume']
    expected_value = expected_volume

    calculation_market_accuracy = abs(actual_market_value - expected_market_value) < 3
    calculation_accuracy = abs(actual_value - expected_value) < 3
    test_outcome = {
        "Test Completion": True,
        "Calculation accuracy, Market": calculation_market_accuracy,
        "Calculation accuracy, Volume": calculation_accuracy
    }
    if not calculation_accuracy or not calculation_market_accuracy:
        test_outcome['Comments'] = f"Actual volume: {actual_value} vs expected volume: {expected_value}"
    print_test_outcome(test_outcome)

    # Volume, adjustments - amazon and variants
    bsr = 10000
    bsr_category = fake_category['Beauty & Personal Care']
    spv = 0
    reviews = 0
    fba_sellers = 3
    nonfba_sellers = 2
    new_sellers_ct = 5
    total_offer_ct = 5
    amz_oos = 50
    variants = 'B005CPZFWQ,B00JKQE8JO' # 2 + 1 variants
    expected_market = 1515
    expected_volume = 1515 / (3 + 2*.5 + 1) / 2 / 3
    adjust_for_variants = 'Yes'

    test_response = copy.deepcopy(keepa_test_responses1[0])
    test_row = copy.deepcopy(row)
    pp = Prodpair(test_row)
    price = 50

    test_response, pp = apply_volume_scenario_inputs(test_response, pp, bsr= bsr, bsr_category= bsr_category, spv = spv, reviews = reviews)
    test_response['stats']['outOfStockCountAmazon30'] = amz_oos #amazon oos
    test_response['stats']['outOfStockPercentage30'][0] = amz_oos #amazon oos
    test_response['stats']['outOfStockPercentage30'][1] = 1 #new oos
    test_response['stats']['buyBoxIsAmazon'] = amz_oos < 100
    test_response['csv_count_new'][-1] = new_sellers_ct
    test_response['stats']['totalOfferCount'] = total_offer_ct
    test_response['buyBoxEligibleOfferCounts'] = [fba_sellers, nonfba_sellers, 0, 0, 0, 0, 0, 0]
    test_response['variationCSV'] = variants


    pp.fake_keepa([test_response])

    test_settings = copy.deepcopy(settings)
    test_settings['Settings']['Adjust for Variants'] = adjust_for_variants
    pp.assess_fees(test_settings)
    pp.forecast_volume(test_settings)
    pp.forecast_profitability(test_settings)


    actual_market_value = pp['Volume, All Sellers']
    expected_market_value = expected_market
    actual_value = pp['Monthly Volume']
    expected_value = expected_volume

    calculation_market_accuracy = abs(actual_market_value - expected_market_value) < 3
    calculation_accuracy = abs(actual_value - expected_value) < 3
    test_outcome = {
        "Test Completion": True,
        "Calculation accuracy, Market": calculation_market_accuracy,
        "Calculation accuracy, Volume": calculation_accuracy
    }
    if not calculation_accuracy or not calculation_market_accuracy:
        test_outcome['Comments'] = f"Actual volume: {actual_value} vs expected volume: {expected_value}"
    print_test_outcome(test_outcome)









    #full calculation scenario 
    # - Beauty, over $10, assert 15% referral fee = 7.5
    # - 2.1 lb & large standard = $5.87 non-peak
    # - Unit COGS = ($10 * .1) * (1/2) = $18
    # = Unit profit = 50 - 18 - 5.87 - 7.5 - storage - low inventory - inbound placement
    # - Storage: 0.11555 Didnt actually calculate
    # - Low Inventory Fee

    price = 50.00
    cf = 0.5
    purchase_price = 10
    price_discount = .1
    expected_cogs = 18
    peak_volume = "No"
    expected_unit_profit = 50 - 18 - 5.87 - 7.5 - 0.11555
    expected_margin = expected_unit_profit / 50
    expected_roi = expected_unit_profit / 18
    inbound_locs = '4+'
    low_inventory_percent = 0
    #volume inputs
    bsr = 10000
    bsr_category = fake_category['Beauty & Personal Care']
    spv = 0
    reviews = 0
    fba_sellers = 3
    nonfba_sellers = 2
    new_sellers_ct = 5
    total_offer_ct = 5
    amz_oos = 50
    variants = 'B005CPZFWQ,B00JKQE8JO' # 2 + 1 variants
    expected_market = 1515
    expected_volume = 1515 / (3 + 2*.5 + 1) / 2 / 3
    adjust_for_variants = 'Yes'

    #run
    test_response = copy.deepcopy(keepa_test_responses1[0])
    test_row = copy.deepcopy(row)
    pp = Prodpair(test_row)

    test_response, pp = apply_volume_scenario_inputs(test_response, pp, bsr= bsr, bsr_category= bsr_category, spv = spv, reviews = reviews)
    test_response['categories'] = [fake_category['Beauty & Personal Care']]
    test_response['stats']['current'][1] = price * 100
    test_response['stats']['buyBoxPrice'] = price * 100
    test_response['stats']['avg30'][1] = price * 100
    test_response['stats']['avg90'][1] = price * 100
    test_response['packageWeight'] = 2.1 * 453.59237 #lb to gram
    test_response['packageHeight'] = 4 * 25.4 #in to mm
    test_response['packageLength'] = 16 * 25.4 #in to mm
    test_response['packageWidth'] = 4 * 25.4 #in to mm
    test_response['stats']['outOfStockCountAmazon30'] = amz_oos #amazon oos
    test_response['stats']['outOfStockPercentage30'][0] = amz_oos #amazon oos
    test_response['stats']['outOfStockPercentage30'][1] = 1 #new oos
    test_response['stats']['buyBoxIsAmazon'] = amz_oos < 100
    test_response['csv_count_new'][-1] = new_sellers_ct
    test_response['stats']['totalOfferCount'] = total_offer_ct
    test_response['buyBoxEligibleOfferCounts'] = [fba_sellers, nonfba_sellers, 0, 0, 0, 0, 0, 0]
    test_response['variationCSV'] = variants

    pp['Purchase Price'] = purchase_price
    pp['Conversion Factor'] = cf
    if 'Conversion Factor_user' in pp.keys():
        pp.user_set({'Conversion Factor', 2})

    test_settings = copy.deepcopy(settings)
    test_settings['Settings']['Seller Costs']['Price Discounts'] = price_discount
    test_settings['Settings']['Seller Costs']['Peak Volume'] = peak_volume
    test_settings['Settings']['Seller Costs']['Low Inventory Percentage'] = low_inventory_percent
    test_settings['Settings']['Seller Costs']['Inbound Locations'] = inbound_locs
    test_settings['Settings']['Adjust for Variants'] = adjust_for_variants

    pp.fake_keepa([test_response])
    pp.assess_fees(test_settings)
    pp.forecast_volume(test_settings)
    pp.forecast_profitability(test_settings)

    #calc - unit profit
    actual_unit_profit = pp['Unit Profit']
    actual_margin = pp['Margin']
    actual_roi = pp['ROI']
    calc_acc_unit_profit = abs(actual_unit_profit - expected_unit_profit) < expected_unit_profit * 0.01
    calc_acc_margin = abs(actual_margin - expected_margin) < expected_margin * 0.01
    calc_acc_roi = abs(actual_roi - expected_roi) < expected_roi * 0.01
    #calc - volume
    actual_volume = pp['Monthly Volume']
    actual_revenue = pp['Monthly Revenue']
    actual_m_profit = pp['Monthly Profit']
    calc_acc_volume = abs(actual_volume - expected_volume) < 1
    calc_acc_revenue = abs(actual_revenue - (price * expected_volume)) < 1
    calc_acc_m_profit = abs(actual_m_profit - (actual_unit_profit * expected_volume)) < 1

    test_outcome = {
        "Test Completion": True,
        "Accuracy - Unit Profit": calc_acc_unit_profit,
        "Accuracy - Margin": calc_acc_margin,
        "Accuracy - ROI": calc_acc_roi,
        "Accuracy - Volume": calc_acc_volume,
        "Accuracy - Revenue": calc_acc_revenue,
        "Accuracy - Monthly Profit": calc_acc_m_profit

    }
    if not calc_acc_unit_profit or not calc_acc_margin or not calc_acc_unit_profit:
        test_outcome['Comments'] = f"Actual profit, margin, roi: {round(actual_unit_profit,2)}, {round(actual_margin,3)}, {round(actual_roi,3)} vs expected profit, margin, roi: {round(expected_unit_profit,2)}, {round(expected_margin,3)}, {round(expected_roi,3)}"

    print_test_outcome(test_outcome)


    #Scenario: Edit without keepa 
    #test_row = copy.deepcopy(row)
    test_row = {'Brand': 'Neutrogena', 'Code': '70501013007', 'Conversion Factor': None, 'Identifier': '100800000888-B01IA9BEQG', 'Listing ID': 'B00JKQE8JO', 'Listing Notes': '', 'MG Idx': '101300004342', 'Match': 'Match', 'Match_user': 'Match', 'Product Description': 'Neutrogena Fragrance Free Norwegian Formula Hand Cream', 'Purchase Price': '1.00', 'Summary': 'pending', 'change_log': [], 'Listing Description': 'Neutrogena Norwegian Formula Moisturizing Hand Cream Formulated with Glycerin for Dry, Rough Hands, Fragrance-Free Intensive Hand Lotion, 2 Oz, Pack of 6', 'Market Price': 46.1, 'Price 30 Day': 47.21, 'BSR': 74006.0, 'BSR 30': 64689.0, 'BSR Category': 'Beauty & Personal Care', 'Number of Sellers': 3.0, 'Number of FBA Sellers': 0, 'Volume, All Sellers': 83.64417789501792, 'Dimension 1 - Longest (in)': 14.8425277, 'Dimension 2 (in)': 5.5511840999999995, 'Dimension 3 - Shortest (in)': 1.968505, 'Weight (lb)': 1.11994696, 'Warnings': '', 'Number of Variants': 2, 'Buy Box Is Amazon': False, 'Buy Box Suppressed': 'True', 'Out of Stock Percentage - New': 0.0, 'Out of Stock Percentage - Amazon': 100.0, 'Main Category': 'Beauty & Personal Care', 'Referral Fee': 6.915, 'FBA Fulfillment Fee': 4.99, 'Storage Fees': 0.07321176642058609, 'Shipping Cost': 0.0, 'Unit COGS': 0.0, 'Unit Costs': 11.978211766420586, 'Unit Profit': 35.231788233579415, 'Monthly Profit': 35.231 * (83.6441 / (3/2 + 1)), 'Margin': 0.7462780816263379, 'Price': 47.21, 'Monthly Volume': 83.6441 / (3/2 + 1), 'Monthly Revenue': 47.21 * (83.6441 / (3/2 + 1)), 'Fees and Fulfillment': 11.978211766420586, 'ROI': 99.99}
    pp = Prodpair(test_row)

    expected_unit_profit = float(pp['Unit Profit'])
    expected_margin = float(pp['Margin'])
    expected_roi = float(pp['ROI'])
    expected_volume = float(pp['Monthly Volume'])
    expected_revenue = float(pp['Monthly Revenue'])
    expected_m_profit = float(pp['Monthly Profit'])

    test_settings = copy.deepcopy(settings)
    pp.recalculate_without_keepa(test_settings)

    actual_unit_profit = float(pp['Unit Profit'])
    actual_margin = float(pp['Margin'])
    actual_roi = float(pp['ROI'])
    actual_volume = float(pp['Monthly Volume'])
    actual_revenue = float(pp['Monthly Revenue'])
    actual_m_profit = float(pp['Monthly Profit'])

    test_outcome = {
        "Test Completion": True,
        "Accuracy - Unit Profit": abs(expected_unit_profit - actual_unit_profit) < (expected_unit_profit * 0.01),
        "Accuracy - Margin": abs(expected_margin - actual_margin) < (0.004),
        "Accuracy - ROI": abs(expected_roi - actual_roi) < (0.004),
        "Accuracy - Volume": abs(expected_volume - actual_volume) < (expected_volume * 0.01),
        "Accuracy - Revenue": abs(expected_revenue - actual_revenue) < (expected_revenue * 0.01),
        "Accuracy - Monthly Profit": abs(expected_m_profit - actual_m_profit) < (expected_m_profit * 0.01)
    }
    if True:
        test_outcome['Comments'] = f"Actual profit, margin, roi: {round(actual_unit_profit,2)} vs {round(expected_unit_profit,2)}, margin:  {round(actual_margin,3)} vs {round(expected_margin,3)}, {round(actual_roi,3)} vs {round(expected_roi,3)}" + f'''
        Actual vs expected volume, revenue, monthly profit: {actual_volume} vs {expected_volume}, revenue: {actual_revenue} vs {expected_revenue}, monthly profit: {actual_m_profit} vs {expected_m_profit}'''
    print_test_outcome(test_outcome)

    #Scenario: Edit without keepa. edit price; see how pick_price logic executes, and see how volume changes


    #pp.recalculate_without_keepa(test_settings)


    # weird scenarios: Beauty, $1, assert at least 0.3 referral fee



