'''
Collection of test responses from keepa

This guarantees stable input data to test calculations for fees, volume, and profitability

There are multiple different configurations of responses
1. Request includes offers, ratings, stats, and buybox etc
2. Request includes stats and buybox, but NO offers and NO ratings
3. Preliminary search request (basic product request costing 1 token)

'''
from integrations.keepa_api.keepa_api import get_keepa_time
import time
import random

#This response has ample data for the request
keepa_test_response_with_no_offers_no_ratings1 = {
    'categories': [11062261, 8797459011, 10052289011], 'imagesCSV': '619hFZPlaPL.jpg,81ji71QHkmL.jpg,71f7+dmZdAL.jpg,71W4CtW4VeL.jpg,716KAySebcL.jpg,81g8kW1+ncL.jpg,810KYg+hYML.jpg,71Xpa1C5YPL.jpg,61tVqCUvRfL.jpg,41LVG-THEIL.jpg,41iYCLY-bnL.jpg,31mXx2qQdhL.jpg,41xvrNNEuxL.jpg,41Zm21mNppL.jpg,41P4vne8FgL.jpg,41xuaJI4AvL.jpg,31kMJuk0uKL.jpg,31TPDN4kXQL.jpg,41ooryVJ+fL.jpg,41HC-UzVjOL.jpg,41j--WUiVxL.jpg,41f60rnqrZL.jpg,41Gjql+uWgL.jpg', 
    'manufacturer': 'Kenvue', 
    'title': 'Neutrogena Norwegian Formula Moisturizing Hand Cream Formulated with Glycerin for Dry, Rough Hands, Fragrance-Free Intensive Hand Lotion, 2 Oz, Pack of 6', 
    'lastUpdate': 7432972, 'lastPriceChange': 7421944, 'rootCategory': 3760911, 'productType': 0, 
    'parentAsin': 'B01I9TL7SM', 'variationCSV': 'B005CPZFWQ,B00JKQE8JO', 
    'asin': 'B00JKQE8JO', 'domainId': 1, 
    'type': 'SKIN_MOISTURIZER', 'hasReviews': True, 'trackingSince': 1840620, 
    'brand': 'Neutrogena', 'productGroup': 'Beauty', 'partNumber': '680130000', 
    'model': '070501013007', 'color': 'White', 'size': '2 Ounce (Pack of 6)', 'edition': None, 'format': None, 
    'packageHeight': 50, 'packageLength': 377, 'packageWidth': 141, 'packageWeight': 508, 'packageQuantity': 6, 
    'isAdultProduct': False, 'isEligibleForTradeIn': False, 'isEligibleForSuperSaverShipping': False, 'offers': None, 'isRedirectASIN': False, 'isSNS': False, 'author': None, 'binding': None, 'numberOfItems': 6, 'numberOfPages': -1, 'publicationDate': -1, 'releaseDate': 20140427, 'languages': None, 'lastRatingUpdate': 7432896, 'ebayListingIds': None, 'lastEbayUpdate': -1, 
    'eanList': None, 'upcList': None, 'liveOffersOrder': None, 'frequentlyBoughtTogether': ['B00GMP5OYO', 'B00GHNYKM8'], 
    'description': 'Product Description\n\nRelieve dry skin effectively with Neutrogena Norwegian Formula Hand Cream. Featuring a highly concentrated Norwegian formula, this moisturizing hand cream has been clinically proven to provide immediate and lasting relief for dry, rough hands. Rich in glycerin, this intensive hand cream is long-lasting and helps improve the look and feel of dry skin, leaving it noticeably softer and smoother. This hand moisturizing cream is fragrance-free and is so concentrated that only a small amount is needed, with over 200 applications contained in this 2-ounce tube.\n\nFrom the Manufacturer\n\nNeutrogena Norwegian formula hand cream delivers effective relief for dry, chapped hands. It is so concentrated that only a small amount instantly leaves even dry, cracked hands noticeably softer and smoother after just one application. Used daily, it moisturizes dry, chapped skin; used overnight, it heals dry skin-even under the harshest of conditions. It started with Norwegian fishermen. Faced with some of the harshest, coldest weather on earth, they used a formula that delivers concentrated levels of glycerin to dry, chapped skin providing immediate and lasting relief. Five years of independent clinical testing confirmed what the fishermen knew all along-Norwegian formula hand cream consistently outperformed other products. Today, the Norwegian formula product line includes a variety of body, hand and foot moisturizers to meet your individual dry skin needs. Just a little goes a long way. One 2 oz tube contains over 200 applications.', 
    'promotions': None, 'newPriceIsMAP': False, 'coupon': None, 'availabilityAmazon': -1, 'listedSince': 856696, 
    'fbaFees': {'lastUpdate': 7432308, 'pickAndPackFee': 499}, 
    'variations': 
        [
            {'asin': 'B005CPZFWQ', 'attributes': [{'dimension': 'Size', 'value': '2 Ounce (Pack of 2)'}]}, 
            {'asin': 'B00JKQE8JO', 'attributes': [{'dimension': 'Size', 'value': '2 Ounce (Pack of 6)'}]}
        ], 
    'itemHeight': 25, 'itemLength': 152, 'itemWidth': 152, 'itemWeight': 340, 
    'salesRankReference': 3760911, 
    'salesRankReferenceHistory': [7195262, 3760911, 7345466, -1, 7345960, 3760911, 7347198, -1, 7347326, 3760911, 7348868, -1, 7349326, 3760911, 7350084, -1, 7350276, 3760911, 7351522, -1, 7351690, 3760911, 7352960, -1, 7353560, 3760911, 7354846, -1, 7355720, 3760911, 7355840, -1, 7356576, 3760911, 7357948, -1, 7358968, 3760911, 7360634, -1, 7361600, 3760911, 7368798, -1, 7370634, 3760911, 7374348, -1, 7374948, 3760911, 7375868, -1, 7376752, 3760911, 7381768, -1, 7382182, 3760911, 7382996, -1, 7383684, 3760911], 
    'launchpad': False, 'isB2B': False, 'lastSoldUpdate': 6949200, 
    'monthlySoldHistory': [6691364, 50, 6791228, 100, 6814824, 200, 6815052, 100, 6815280, 200, 6830678, 300, 6834706, 200, 6834880, 300, 6834952, 200, 6857434, 300, 6857604, 200, 6857630, 300, 6857688, 200, 6858270, 300, 6859028, 200, 6860004, 300, 6860008, 200, 6860072, 300, 6860480, 200, 6860536, 300, 6860572, 200, 6860934, 300, 6862324, 200, 6862676, 300, 6863312, 200, 6863850, 300, 6866234, 200, 6866588, 300, 6883096, 400, 6891232, 300, 6891452, 400, 6912396, 300, 6924126, 200, 6936946, 100, 6944548, 50, 6948784, 100, 6949200, 50, 6993924, -1], 
    'buyBoxEligibleOfferCounts': [0, 3, 0, 0, 0, 0, 0, 0], 
    'competitivePriceThreshold': 3144, 
    'suggestedLowerPrice': 3843, 
    'parentAsinHistory': ['7065360', 'B01I9TL7SM', '7084044', 'B0D6G8GZPH'], 'isHeatSensitive': False, 
    'urlSlug': 'Neutrogena-Norwegian-Moisturizing-Formulated-Fragrance-Free', 
    'ingredients': 'Water, Glycerin, Cetearyl Alcohol, Stearic Acid, Sodium Cetearyl Sulfate, Methylparaben, Propylparaben, Dilauryl Thiodipropionate, Sodium Sulfate', 
    'unitCount': {'unitValue': 12.0, 'unitType': 'Ounce'}, 'activeIngredients': 'glycerin', 
    'itemForm': 'Cream', 'itemTypeKeyword': 'body-gels-and-creams', 
    'recommendedUsesForProduct': 'Moisturizing', 
    'specificUsesForProduct': ['Dryness'], 
    'productBenefit': 'Benefits: Neutrogena Hand Cream delivers effective relief for dry, chapped hands with a classic, light fragrance.This clinically proven, highly concentrated formula rapidly heals dry hands. It noticeably improves the look and feel of your skin.Hands feel soft and smooth after just one application.', 
    'style': 'Pack of 6 (Old)', 'scent': 'Fragrance Free', 'brandStoreName': 'Neutrogena', 'brandStoreUrl': '/stores/Neutrogena/page/3BC8CF14-3F35-41A4-9BF3-705A7FB2B6B6', 
    'stats': 
        {
            'current': [-1, 4610, -1, 101176, 4068, -1, -1, -1, -1, -1, -1, 3, -1, -1, -1, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'avg': [-1, 4610, -1, 62512, 4068, -1, -1, -1, -1, -1, -1, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'avg30': [-1, 4610, -1, 64026, 4068, -1, -1, -1, -1, -1, -1, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'avg90': [-1, 4610, -1, 82762, 4048, -1, -1, -1, -1, -1, -1, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'avg180': [3143, 4343, -1, 110128, 4059, -1, -1, -1, -1, -1, -1, 8, -1, -1, -1, -1, -1, -1, 3143, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'avg365': [3002, 3976, -1, 115408, 4063, -1, -1, -1, -1, -1, -1, 10, -1, -1, -1, -1, -1, -1, 3002, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'atIntervalStart': [-1, 4890, -1, 59750, 4068, -1, -1, -1, -1, -1, -1, 1, -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'min': [[3107376, 1362], [3042012, 531], [5178514, 883], [2967600, 163], [3112572, 1602], None, None, None, None, None, None, [3915320, 1], [2283870, 1], None, None, None, None, None, [3992300, 1590], None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
            'max': [[6365144, 4074], [7362344, 7000], [2999700, 2952], [7124012, 207633], [2283870, 4076], None, None, None, None, None, None, [3782990, 25], [2283870, 1], None, None, None, None, None, [6365144, 4074], None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], 
            'minInInterval': [[-1, -1], [7421612, 4610], [-1, -1], [7404796, 45881], [7384320, 4068], None, None, None, None, None, None, [7384320, 1], [-1, -1], None, None, None, None, None, [-1, -1], None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], 
            'maxInInterval': [[-1, -1], [7384320, 4890], [-1, -1], [7388958, 89113], [7384320, 4068], None, None, None, None, None, None, [7416880, 3], [-1, -1], None, None, None, None, None, [-1, -1], None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], 
            'isLowest': [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False], 
            'isLowest90': [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False], 
            'outOfStockPercentageInInterval': [100, 0, 100, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 100, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'outOfStockPercentage365': [99, 5, 100, -1, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 99, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'outOfStockPercentage180': [100, 10, 100, -1, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 100, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'outOfStockPercentage90': [100, 19, 100, -1, 14, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 100, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'outOfStockPercentage30': [100, 0, 100, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 100, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'outOfStockCountAmazon30': 1, 'outOfStockCountAmazon90': 1, 
            'deltaPercent90_monthlySold': 0, 'retrievedOfferCount': -2, 
            'totalOfferCount': 3, 'tradeInPrice': -2, 'lastOffersUpdate': 7432896, 'isAddonItem': None, 'lightningDealInfo': None, 
            'sellerIdsLowestFBA': None, 'sellerIdsLowestFBM': None, 'offerCountFBA': -2, 'offerCountFBM': -2, 
            'salesRankDrops30': 44, 'salesRankDrops90': 117, 'salesRankDrops180': 217, 'salesRankDrops365': 587, 
            'buyBoxPrice': -1, 'buyBoxShipping': -1, 'buyBoxIsUnqualified': True, 'buyBoxIsShippable': False, 
            'buyBoxIsPreorder': False, 
            'buyBoxIsFBA': False, 
            'buyBoxIsAmazon': False, 
            'buyBoxIsMAP': False, 
            'buyBoxIsUsed': False, 'buyBoxIsBackorder': None, 'buyBoxIsPrimeExclusive': None, 'buyBoxIsFreeShippingEligible': None, 
            'buyBoxIsPrimePantry': None, 
            'buyBoxIsPrimeEligible': None, 
            'buyBoxMinOrderQuantity': None, 'buyBoxMaxOrderQuantity': None, 'buyBoxCondition': None, 'lastBuyBoxUpdate': 7432972, 'buyBoxAvailabilityMessage': None, 'buyBoxShippingCountry': None, 
            'buyBoxSellerId': None, 'buyBoxIsWarehouseDeal': None
        }, 
    'offersSuccessful': False, 
    'g': 62617, 
    'categoryTree': 
        [
            {'catId': 3760911, 'name': 'Beauty & Personal Care'}, 
            {'catId': 17242866011, 'name': 'Foot, Hand & Nail Care'}, 
            {'catId': 11062211, 'name': 'Foot & Hand Care'}, 
            {'catId': 11062261, 'name': 'Hand Creams & Lotions'}
        ], 
    'parentTitle': 'Neutrogena Norwegian Formula Hand Cream Fragrance-Free 2 oz', 
    'brandStoreUrlName': 'Neutrogena', 'referralFeePercent': 15, 
    'referralFeePercentage': 15.01, 
    'csv_count_new': [7287140, 9, 7289354, 10, 7304826, 11, 7320570, 10, 7341960, 8, 7342544, 7, 7343396, 3, 7343920, 2, 7345092, 1, 7345466, -1, 7346278, 2, 7347198, -1, 7362344, 1, 7368414, -1, 7370634, 1, 7371550, -1, 7376752, 1, 7381758, -1, 7382996, 1, 7386084, 2, 7398368, 1, 7398824, 2, 7403356, 1, 7403932, 2, 7404600, 1, 7404796, 2, 7408824, 1, 7409116, 2, 7416880, 3], 
        'asin0': 'B00JKQE8JO'
}


#This response has very limited data
keepa_test_response_with_no_offers_no_ratings2 = {
    'categories': [11062261], 
    'imagesCSV': '61EyGI7WGJL.jpg,61-kdIOnYzL.jpg,71nQKiiAt5L.jpg,71EugSdY5LL.jpg', 
    'manufacturer': 'Neutrogena', 
    'title': 'Neutrogena Norwegian Formula Hand Cream, Fragrance-Free, 2 Ounce', 
    'lastUpdate': 7432972, 
    'lastPriceChange': 6018906, 
    'rootCategory': 3760911, 
    'productType': 0, 
    'parentAsin': None, 
    'variationCSV': None, 
    'asin': 'B005M339RQ', 
    'domainId': 1, 
    'type': 'BEAUTY', 
    'hasReviews': True, 
    'trackingSince': 3567610, 
    'brand': 'Neutrogena', 'productGroup': 'Beauty', 
    'partNumber': '070501013007', 
    'model': '070501013007', 
    'color': None, 'size': 'oz', 'edition': None, 'format': None, 
    'packageHeight': 0, 'packageLength': 0, 'packageWidth': 0, 'packageWeight': 0, 'packageQuantity': 1, 'isAdultProduct': False, 'isEligibleForTradeIn': False, 'isEligibleForSuperSaverShipping': False, 
    'offers': None, 
    'isRedirectASIN': False, 'isSNS': False, 'author': None, 'binding': None, 
    'numberOfItems': 1, 'numberOfPages': -1, 'publicationDate': -1, 'releaseDate': -1, 'languages': None, 'lastRatingUpdate': 7409238, 'ebayListingIds': None, 'lastEbayUpdate': 0, 'eanList': ['0070501013007'], 
    'upcList': ['070501013007'], 'liveOffersOrder': None, 'frequentlyBoughtTogether': None, 'description': None, 'promotions': None, 'newPriceIsMAP': False, 'coupon': None, 'availabilityAmazon': -1, 'listedSince': 362516, 'fbaFees': None, 'variations': None, 'itemHeight': 0, 'itemLength': 0, 'itemWidth': 0, 'itemWeight': 0, 'salesRankReference': -1, 'salesRankReferenceHistory': None, 'launchpad': False, 'isB2B': False, 'isHeatSensitive': False, 'urlSlug': 'Neutrogena-Norwegian-Formula-Cream-Fragrance-Free', 
    'unitCount': {'unitValue': 2.0, 'unitType': 'Ounce'}, 'itemForm': 'Cream', 'itemTypeKeyword': 'hand-creams', 'brandStoreName': 'Neutrogena', 'brandStoreUrl': '/stores/Neutrogena/page/3BC8CF14-3F35-41A4-9BF3-705A7FB2B6B6', 
    'stats': 
        {
            'current': [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'avg': [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'avg30': [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'avg90': [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'avg180': [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'avg365': [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 'atIntervalStart': [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 'min': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], 'max': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], 'minInInterval': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], 'maxInInterval': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], 'isLowest': [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False], 
            'isLowest90': [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False], 
            'outOfStockPercentageInInterval': [100, 100, 100, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 'outOfStockPercentage365': [100, 100, 100, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'outOfStockPercentage180': [100, 100, 100, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'outOfStockPercentage90': [100, 100, 100, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'outOfStockPercentage30': [100, 100, 100, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
            'outOfStockCountAmazon30': 1, 'outOfStockCountAmazon90': 1, 'deltaPercent90_monthlySold': None, 'retrievedOfferCount': -2, 'totalOfferCount': 0, 'tradeInPrice': -2, 'lastOffersUpdate': 7409238, 'isAddonItem': None, 'lightningDealInfo': None, 'sellerIdsLowestFBA': None, 'sellerIdsLowestFBM': None, 
            'offerCountFBA': -2, 'offerCountFBM': -2, 'salesRankDrops30': 0, 'salesRankDrops90': 0, 'salesRankDrops180': 0, 'salesRankDrops365': 0, 
            'buyBoxPrice': -1, 'buyBoxShipping': -1, 'buyBoxIsUnqualified': False, 'buyBoxIsShippable': False, 'buyBoxIsPreorder': False, 'buyBoxIsFBA': False, 'buyBoxIsAmazon': False, 'buyBoxIsMAP': False, 'buyBoxIsUsed': False, 'buyBoxIsBackorder': None, 'buyBoxIsPrimeExclusive': None, 'buyBoxIsFreeShippingEligible': None, 'buyBoxIsPrimePantry': None, 'buyBoxIsPrimeEligible': None, 'buyBoxMinOrderQuantity': None, 'buyBoxMaxOrderQuantity': None, 'buyBoxCondition': None, 'lastBuyBoxUpdate': 7409238, 'buyBoxAvailabilityMessage': None, 'buyBoxShippingCountry': None, 'buyBoxSellerId': None, 
            'buyBoxIsWarehouseDeal': None
        }, 'offersSuccessful': False, 'g': 2298, 
    'categoryTree': 
        [
            {'catId': 3760911, 'name': 'Beauty & Personal Care'}, 
            {'catId': 17242866011, 'name': 'Foot, Hand & Nail Care'}, 
            {'catId': 11062211, 'name': 'Foot & Hand Care'}, 
            {'catId': 11062261, 'name': 'Hand Creams & Lotions'}
        ], 
    'brandStoreUrlName': 'Neutrogena', 'csv_count_new': None, 
    'asin0': 'B005M339RQ'
}

end_t = get_keepa_time(time.time())
#offers with good quality. Has 5 sellers: 1 FBA-competitive seller (price of 46.10), 1 other FBA, 1 FBM competitive, and 2 other FBM. 
#    -  all conditions = 1 (New)
offers_good = [
    {
        'lastSeen': end_t, 
        'sellerId': 'A3S588S5LPPRZZ', 
        'offerCSV': [7310960, 4395, 0, 7341754, 4395, 0, end_t - 40000, 4395, 0, end_t - 38000, 4799, 0, end_t - 26000, 4799, 0, end_t - 25000, 4799, 0, end_t - 24000, 4799, 0, end_t - 22000, 4799, 0, end_t - 20000, 4610, 0, end_t - 200, 4610, 0, end_t, 4610, 0], 
        'condition': 1, 
        'conditionComment': None, 
        'isPrime': True, 
        'isMAP': False, 
        'isShippable': True, 
        'isAddonItem': False, 
        'isPreorder': False, 
        'isWarehouseDeal': False, 
        'isScam': False, 
        'isAmazon': False, 
        'isPrimeExcl': False, 
        'offerId': 10, 
        'isFBA': True, 
        'shipsFromChina': False, 
        'minOrderQty': 1, 
        'couponHistory': [6932180, 0]
    },  #FBA competitive
    {'lastSeen': end_t, 'sellerId': 'ASEVS99O6FS73', 'offerCSV': [7318126, 4688, 0, 7322660, 4890, 0, 7398824, 4798, 0, 7399038, 4702, 0, 7400476, 4798, 0, 7403932, 4702, 0, 7404844, 4798, 0, 7406376, 4702, 0, 7406572, 4798, 0, 7408196, 4702, 0, 7409904, 4798, 0, 7410052, 4702, 0, 7410556, 4798, 0, 7411996, 4702, 0, 7412200, 4798, 0, 7413296, 4702, 0, 7413436, 4798, 0, 7414694, 4702, 0, 7414876, 4798, 0, 7416316, 4702, 0, end_t - 1000, 4610, 0, end_t - random.randint(0,60*1), 4610 - random.randint(-int(0.04*4610),int(.01*4610)), 0], 'condition': 1, 'conditionComment': None, 'isPrime': True, 'isMAP': False, 'isShippable': True, 'isAddonItem': False, 'isPreorder': False, 'isWarehouseDeal': False, 'isScam': False, 'isAmazon': False, 'isPrimeExcl': False, 'offerId': 2, 'isFBA': False, 'shipsFromChina': False, 'minOrderQty': 1, 'couponHistory': [7214396, 0]}, #FBM competitive
    {'lastSeen': end_t, 'sellerId': 'A3FT2NUVSQ8ZHD', 'offerCSV': [7453684, 5000, 0, 7458736, 5000, 0, 7461452, 5000, 0, 7463676, 5000, 0, 7464296, 5000, 0, 7466088, 5000, 0, end_t - random.randint(0,60), 4610+460+5, 0], 'condition': 1, 'conditionComment': None, 'isPrime': True, 'isMAP': False, 'isShippable': True, 'isAddonItem': False, 'isPreorder': False, 'isWarehouseDeal': False, 'isScam': False, 'isAmazon': False, 'isPrimeExcl': False, 'offerId': 134, 'isFBA': True, 'shipsFromChina': False, 'minOrderQty': 1, 'couponHistory': [7133828, 0]}, #FBA non-competitive
    {'lastSeen': end_t, 'sellerId': 'A3KGCU4HM6EAVD', 'offerCSV': [7310960, 4839, 0, 7341754, 4839, 834, end_t - random.randint(0,60), 4610+460+1, 0], 'condition': 1, 'conditionComment': None, 'isPrime': False, 'isMAP': False, 'isShippable': True, 'isAddonItem': False, 'isPreorder': False, 'isWarehouseDeal': False, 'isScam': False, 'isAmazon': False, 'isPrimeExcl': False, 'offerId': 98, 'isFBA': True, 'shipsFromChina': False, 'minOrderQty': 1, 'couponHistory': [6850926, 0]}, #FBA non-competitive
    #{'lastSeen': end_t, 'sellerId': 'A1AT90P5YN70N6', 'offerCSV': [7310960, 4716, 0, 7341754, 4716, 559, end_t - random.randint(0,60), 4610+460+1, 0], 'condition': 1, 'conditionComment': None, 'isPrime': False, 'isMAP': False, 'isShippable': True, 'isAddonItem': False, 'isPreorder': False, 'isWarehouseDeal': False, 'isScam': False, 'isAmazon': False, 'isPrimeExcl': False, 'offerId': 122, 'isFBA': True, 'shipsFromChina': False, 'minOrderQty': 1, 'couponHistory': [6850926, 0]}, #FBA non-competitive
    {'lastSeen': end_t, 'sellerId': 'A2D90AT56DGLZQ', 'offerCSV': [end_t - random.randint(0,60), 4600+460+1, 0], 'condition': 1, 'conditionComment': None, 'isPrime': False, 'isMAP': False, 'isShippable': True, 'isAddonItem': False, 'isPreorder': False, 'isWarehouseDeal': False, 'isScam': False, 'isAmazon': False, 'isPrimeExcl': False, 'offerId': 138, 'isFBA': False, 'shipsFromChina': False, 'minOrderQty': 1, 'couponHistory': [7362344, 0]} #FBM non-competitive
]

#ratings csv with 180 days back data and increase in 13 reviews
ratings_good = [
    end_t - 60*24*200, 2476,
    end_t - 60*24*190, 2475, 
    end_t - 60*24*170, 2476, 
    end_t - 60*24*150, 2477, 
    end_t - 60*24*120, 2478, 
    end_t - 60*24*110, 2479, 
    end_t - 60*24*90, 2435, #there is a big removal on this day of 44, which impacts the calculation
    end_t - 60*24*80, 2426, #there is a big removal on this day of 9, which impacts the calculation  
    end_t - 60*24*70, 2427, 
    end_t - 60*24*60, 2481, 
    end_t - 60*24*30, 2482, 
    end_t - 60*24*5, 2484, 
    end_t - 60*24*4, 2485, 
    end_t - 60*24*3, 2486, 
    end_t - 60*24*2, 2487, 
    end_t - 60*24*1, 2488, 
    end_t, 2489
]

ratings_good_variant_has_half = [-1]* len(ratings_good)
for i in range(1,len(ratings_good),2):
    ratings_good_variant_has_half[i-1] = ratings_good[i-1]
    ratings_good_variant_has_half[i] = round(ratings_good[i]/2)


ratings_good_variant_has_half[-1] - ratings_good_variant_has_half[3]

#from integrations.keepa_api.keepa_api import ratings_from_keepa_ratings_csv
#ratings_from_keepa_ratings_csv(ratings_good_variant_has_half)



ratings_small_sample = [ 
    end_t - 60*24*150, 9, 
    end_t - 60*24*120, 10, 
    end_t - 60*24*110, 10, 
    end_t - 60*24*90, 10, 
    end_t - 60*24*4, 11, 
    end_t - 60*24*3, 12,  
    end_t - 60*24*1, 13, 
    end_t, 13
] #delta: 3 period: 90

variant_ratings_small_sample = [ 
    end_t - 60*24*150, 3, 
    end_t - 60*24*120, 3, 
    end_t - 60*24*110, 3, 
    end_t - 60*24*90, 3, 
    end_t - 60*24*4, 3, 
    end_t - 60*24*3, 3,  
    end_t - 60*24*1, 3, 
    end_t, 3
] #delta 0, period: 90