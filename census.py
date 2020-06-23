import pickle
from math import sin, cos, sqrt, atan2, radians
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from fastapi import HTTPException
from pydantic import BaseModel

pkl_file = open('Pickle/census.pkl', 'rb')
census = pickle.load(pkl_file)
pkl_file.close()

pkl_file = open('Pickle/cities_dict.pkl', 'rb')
cities_dict = pickle.load(pkl_file)
pkl_file.close()


class Census(BaseModel):
    location: list
    user_id: int

    class Config:
        schema_extra = {
            "example": {
                "location": [
                    "Sea Girt", "NJ"
                ],
                "user_id": 1
            }
        }

    def census_totals(self, user_dict: dict):
        """
        Function to create the categorized census average expenditures of a user's area, according to a user's categorical preferences
        Inputs: user_dict - a user's categorization preferences
        Outputs: final_request - a JSON/dictionary that contains the closest city (or region if >=50 miles from a city) and totals of
                 personally categorized census expenditure averages for their area
        """
        location = self.location
        # Find coordinates of user city
        geolocator = Nominatim(user_agent="aklefebvere@gmail.com")

        limit_geo = RateLimiter(geolocator.geocode, min_delay_seconds=1)

        city = location[0]
        state = location[1]
        country = "US"

        try:
            loc = limit_geo(city + ',' + state + ',' + country)
        except GeocoderUnavailable as e:
            raise HTTPException(status_code=500, detail=f"Geopy: {e.message}")

        lat_lon = [loc.latitude, loc.longitude]

        # Find distances between all cities in census data, and user's city
        cities = list(cities_dict.keys())
        min_distance = 100000
        closest_city = ''
        for city in cities:
            # approximate radius of earth in km
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

            # Save the shortest distance to min_distance and the corresponding
            # city to closest_city
            if distance < min_distance:
                min_distance = distance
                closest_city = city

        # Print the miles to the closest city
        # print((min_distance*.621))

        # List of all PLAID categories in census data
        plaid_cats = list(census.keys())

        # List of all budget blocks cats
        bb_cats = list(user_dict.keys())

        personalized_census = {}
        # Add the closest city to the personalized census dict
        personalized_census['City'] = closest_city
        # Save the region instead of closest_city if it's over 50 miles away
        # Save the first index of census.keys to a variable because we only
        # need to look at one
        temp = list(census.keys())[0]
        if (min_distance * .621) >= 50:
            for region in list(census[temp].keys()):
                if closest_city in list(census[temp][region].keys()):
                    personalized_census['City'] = region
                    closest_city = region

        # Make sure that there is a key for every category and they all start
        # with a value of 0
        for cat in bb_cats:
            if cat not in personalized_census:
                personalized_census[cat] = 0

        for key in plaid_cats:
            # Need to split the plaid_cats because they aren't formatted like
            # they should be to compare
            new_key = key.split(', ', 1)

            for i in bb_cats:
                for v in user_dict[i]:
                    if new_key == v:
                        # Add the average expenditure of the corresponding city to the correct user BB cat value
                        # Divide by 12 to go from annual to monthly
                        for region in list(census[key].keys()):
                            if closest_city in list(
                                    census[key][region].keys()):
                                personalized_census[i] += (census[key]
                                                           [region][closest_city] / 12)

        # Make savings equal to the income minus all of the spending
        total_spending = 0
        for key in list(personalized_census.keys()):
            if (key != "Income") & (key != "Savings") & (key != "City"):
                total_spending += personalized_census[key]

        personalized_census["Savings"] = abs(personalized_census["Income"]) - total_spending

        return personalized_census
