import sys, os

# pytest -m test was alternative solution
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import unittest
from DB.userDB import *
from DB.masterDB import *
from transactionhist import *
from census import *


class TestTransactions(unittest.TestCase):
    def test_check_keys(self):
        # Using the example values
        trans = TransactionHistory.Config.schema_extra['example']['transactions']

        user_id = 42
        trans_object = TransactionHistory(transactions = trans, user_id = user_id)

        recats = trans_object.getCats(cats_dict=masterPull())

        expected_totals = {
                "Personal": 0,
                "Food": 0,
                "Debt": 25,
                "Income": 0,
                "Giving": 0,
                "Housing": 0,
                "Transportation": 0,
                "Transfer": 0,
                "Savings": 0
            }

        self.assertEqual(recats['totals'], expected_totals)
        self.assertEqual(recats['user_id'], user_id)
        self.assertEqual(recats["transactions"][0]['plaid_category'],  ["Payment","Credit Card"])
        self.assertEqual(recats["transactions"][0]['budget_blocks_category'], ["Debt"])        

class TestCensus(unittest.TestCase):
    def test_census(self):
        user_id = 42
        census = Census(location = ['Sea Girt', 'NJ'], user_id = user_id)
        census_totals = census.census_totals(user_dict=masterPull())

        # If master is in factory default
        expected_census = {
            "City": "New York",
            "Personal": 2304.0833333333335,
            "Food": 725.5,
            "Debt": 0,
            "Income": 8409.25,
            "Giving": 125.66666666666667,
            "Housing": 1950.5833333333335,
            "Transportation": 707.75,
            "Transfer": 0,
            "Savings": 0
            }

        self.assertEqual(census_totals, expected_census)

if __name__ == '__main__':
    unittest.main()