import pickle
from math import sin, cos, sqrt, atan2, radians
from geopy.geocoders import Nominatim

pkl_file = open('census.pkl', 'rb')
census = pickle.load(pkl_file)
pkl_file.close()

pkl_file = open('cities_dict.pkl', 'rb')
cities_dict = pickle.load(pkl_file)
pkl_file.close()

def census_totals(transactions, location, user_dict):
    """
    Function to create the categorized census average expenditures of a user's area, according to a user's categorical preferences, then append it onto and return their transactions dictionary
    Inputs: transactions - dictionary of a user's categorized (BB) transactions
            location - a user's location (list: city, state)
            user_dict - a user's categorization preferences
    Outputs: final_request - a JSON/dictionary that contains a user's transactions, location, user ID, and totals of personally categorized census expenditure averages for their area
    """
    # Find coordinates of user city
    geolocator = Nominatim()
    city = location[0]
    state = location[1]
    country = "US"
    loc = geolocator.geocode(city + ',' + state + ',' + country)
    lat_lon = [loc.latitude,loc.longitude]

    # Find distances between all cities in census data, and user's city
    # approximate radius of earth in km
    distances = []
    cities = list(cities_dict.keys())
    min_distance = 100000
    closest_city = ''
    for city in cities:
        R = 6373.0

        lat1 = radians(lat_lon[0])
        lon1 = radians(lat_lon[1])
        lat2 = radians(cities_dict[city][0])
        lon2 = radians(cities_dict[city][1])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        
        distances.append(distance)
        
        if distance < min_distance:
            min_distance = distance
            closest_city = city

    # List of all PLAID categories in census data
    plaid_cats = list(census.keys())
    
    # List of all budget blocks cats
    bb_cats = list(user_dict.keys())

    personalized_census = {}


    # pc_formatted = []
    for key in plaid_cats:
        new_key = key.split(', ', 1)
        # pc_formatted.append(new_key)

        for i in bb_cats:
            for v in user_dict[i]:
                if key == v:
                    personalized_census[i] += census[key][closest_city]
        

