import APIs
import requests
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
import csv
import json
import datetime

YOUR_API_KEY = APIs.MapsKey


class Location:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return f"({self.latitude}, {self.longitude})"


def get_distance(location1: Location, location2: Location) -> float:
    """
        Calculates the Haversine distance between two locations on Earth.

        :param: location1: The first location object containing latitude and longitude in decimal degrees.
        :type: location1: Location
        :param: location2: The second location object containing latitude and longitude in decimal degrees.
        :type: location2: Location
        :return: The distance between the two locations in kilometers.
        :rtype: float
        """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [location1.latitude, location1.longitude, location2.latitude,
                                           location2.longitude])

    # Calculate the Haversine distance
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c  # Earth radius in km

    return distance


def get_address(location: Location) -> str | None:
    """
    Retrieves the formatted address of a location using its latitude and longitude coordinates via the Google
    Maps Geocoding API.

    :param: location: The location object containing latitude and longitude in decimal degrees.
    :type: location: Location
    :return: The formatted address of the location, or None if an error occurs or no address is found.
    :rtype: str or None
    """
    # Define the API endpoint and parameters
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"latlng": f"{location.latitude},{location.longitude}", "key": YOUR_API_KEY }

    # Send a GET request to the API endpoint
    response = requests.get(endpoint, params=params)

    # Parse the response JSON and extract the formatted address
    data = response.json()
    if data["status"] == "OK":
        return data["results"][0]["formatted_address"]
    else:
        return None


def get_lat_long(location: str) -> tuple | None:
    """
    Given a location address, returns its latitude and longitude using Google Maps Geocoding API.
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location,
        "key": YOUR_API_KEY
    }

    # Send GET request to the API endpoint with the parameters
    response = requests.get(url, params=params)

    # Check if the API request was successful
    if response.status_code == 200:
        data = response.json()

        # Check if the response contains any results
        if len(data["results"]) > 0:
            # Get the latitude and longitude from the first result
            lat = data["results"][0]["geometry"]["location"]["lat"]
            lng = data["results"][0]["geometry"]["location"]["lng"]
            return lat, lng

    # If the API request was not successful, return None
    return None


def get_travel_time(origin: str, destination: str) -> float:
    """
        Retrieves the estimated travel time between an origin and a destination address using the Google Maps Directions
        API in minutes.

        :param: origin: The origin address for the travel time calculation.
        :type: origin: str
        :param: destination: The destination address for the travel time calculation.
        :type: destination: str
        :return: The estimated travel time between the origin and destination in minutes, or -1 if an error occurs.
        :rtype: float
        """
    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": origin,
        "destination": destination,
        "key": YOUR_API_KEY
    }

    # Send GET request to the API endpoint with the parameters
    response = requests.get(url, params=params)

    # Check if the API request was successful
    if response.status_code == 200:
        data = response.json()

        # Check if the response contains any routes
        if len(data["routes"]) > 0:
            # Get the travel time from the first route
            duration = data['routes'][0]['legs'][0]['duration']['value']
            travel_time = duration / 60  # convert seconds to minutes

            return travel_time

    # If the API request was not successful, print an error message
    else:
        return -1


def values_from_ds(target_latitude: float, target_longitude: float) -> float | int:
    """
    Retrieves values from a CSV data source for a target latitude and longitude.

    :param: target_latitude: The target latitude for filtering the data.
    :type: target_latitude: float
    :param: target_longitude: The target longitude for filtering the data.
    :type: target_longitude: float
    :return: The filtered results from the CSV data source as a float value for 'AvgTimeToPark', and the result of
             calling 'get_searching_by_hour' function on 'AvgTimeToPark' index as an integer value.
    :rtype: float | int
    """
    # Load the CSV data into a pandas DataFrame
    df = pd.read_csv('Searching_for_parking.csv')

    # Use boolean indexing to filter rows that match the target latitude and longitude
    filtered_df = df[(df['Latitude_SW'] == target_latitude) & (df['Longitude_SW'] == target_longitude)]
    # return the filtered results
    return float(filtered_df['AvgTimeToPark']), get_searching_by_hour(int(filtered_df['AvgTimeToPark'].index.to_numpy()))


def get_searching_by_hour_test(hour: int, row_num: int) -> int | None:
    """
    Retrieves the value of 'SearchingByHour' for a specific hour from a CSV data source for a given row number.

    :param: hour: The hour for which the 'SearchingByHour' value is retrieved.
    :type: hour: int
    :param: row_num: The row number of the CSV data source to retrieve the value from.
    :type: row_num: int
    :return: The value of 'SearchingByHour' for the specified hour, or None if the hour is not found.
    :rtype: Any
    """
    with open('Searching_for_parking.csv', 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for i, row in enumerate(reader):
            if i == row_num:
                searching_by_hour = json.loads(row[header.index('SearchingByHour')])
                if hour in searching_by_hour:
                    return searching_by_hour[hour]
                else:
                    return None
        return None


def get_searching_by_hour(row_num: int) -> float | None:
    """
    Retrieves the value of 'SearchingByHour' for the current hour from a CSV data source for a given row number.

    :param: row_num: The row number of the CSV data source to retrieve the value from.
    :type: row_num: int
    :return: The value of 'SearchingByHour' for the current hour, or None if the hour is not found.
    :rtype: float or None
    """
    current_hour = str(datetime.datetime.now().hour)
    with open('Searching_for_parking.csv', 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for i, row in enumerate(reader):
            if i == row_num:
                searching_by_hour = json.loads(row[header.index('SearchingByHour')])
                if current_hour in searching_by_hour:
                    return searching_by_hour[current_hour]
                else:
                    return None
        return None
