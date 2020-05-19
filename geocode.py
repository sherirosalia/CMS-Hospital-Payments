# this is a clean copy of code_places_yelp_rubmaps.ipynb

import pandas as pd
import requests
import logging
import time
from os import path


logger = logging.getLogger("root")
logger.setLevel(logging.DEBUG)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

#------------------ CONFIGURATION -------------------------------

# Set your Google API key here. 
# Even if using the free 2500 queries a day, its worth getting an API key since the rate limit is 50 / second.
# With API_KEY = None, you will run into a 2 second delay every 10 requests or so.
# With a "Google Maps Geocoding API" key from https://console.developers.google.com/apis/, 
# the daily limit will be 2500, but at a much faster rate.
API_KEY = 'put key here'
# API_KEY = None
# Backoff time sets how many minutes to wait between google pings when your API limit is hit
BACKOFF_TIME = 30
# Set your output file name here.
output_filename = 'geocoded_hospitals.csv'
geo_json_filename = ""
# Set your input file here
input_filename = 'hospital_payments_geo.csv'
# Specify the column name in your input data that contains addresses here
address_column_name = "address"
# Return Full Google Results? If True, full JSON results from Google are included in output
RETURN_FULL_RESULTS = False

#------------------ DATA LOADING --------------------------------
# teaching_hospital_name,recipient_primary_business_street_address_line1,recipient_city,recipient_state,recipient_zip_code,payment
# Read the data to a Pandas Dataframe
df = pd.read_csv(input_filename, encoding='utf8', dtype=str)

df[address_column_name] = df['recipient_primary_business_street_address_line1'] + ' ' + df['recipient_city'] + ' ' + df['recipient_state'] + ' ' + df['recipient_zip_code']
print(df['address'].head(10))
# exit()

# if a partial output file already exists, read it in instead of the input file
# (this assumes that the way we are writing out the data is to update existing rows with the geocode data, 
# and then write ALL the data to the file, whether it was updated already or not)
if path.exists(output_filename):
    df = pd.read_csv(output_filename, encoding='utf8', dtype=str)

if address_column_name not in df.columns:
    raise ValueError("Missing Address column in input data")

# Form a list of addresses for geocoding:
# Make a big list of all of the addresses to be processed.
addresses = df[address_column_name].tolist()

# **** DEMO DATA / IRELAND SPECIFIC! ****
# We know that these addresses are in Ireland, and there's a column for county, so add this for accuracy. 
# (remove this line / alter for your own dataset)
# addresses = (df[address_column_name] + ',' + df['County'] + ',Ireland').tolist()


#------------------	FUNCTION DEFINITIONS ------------------------

def get_google_results(address, api_key=API_KEY, return_full_response=True):
    """
    Get geocode results from Google Maps Geocoding API.
    
    Note, that in the case of multiple google geocode reuslts, this function returns details of the FIRST result.
    
    @param address: String address as accurate as possible. For Example "18 Grafton Street, Dublin, Ireland"
    @param api_key: String API key if present from google. 
                    If supplied, requests will use your allowance from the Google API. If not, you
                    will be limited to the free usage of 2500 requests per day.
    @param return_full_response: Boolean to indicate if you'd like to return the full response from google. This
                    is useful if you'd like additional location details for storage or parsing later.
    """
    # Set up your Geocoding url
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?address={}".format(address)

    if api_key is not None:
        geocode_url = geocode_url + "&key={}".format(api_key)
    print(geocode_url)  
    # request the reuslts:
    results = requests.get(geocode_url)
    # Results will be in JSON format - convert to dict using requests functionality
    results = results.json()

    if "error_message" in results:
        print(results["error_message"])
    
    # if there's no results or an error, return empty results.
    if len(results['results']) == 0:
        output = {
            "name" : None,
            "phone" : None,
            "formatted_address" : None,
            "latitude": None,
            "longitude": None,
            "accuracy": None,
            "google_place_id": None,
            "type": None,
            "postcode": None
        }
    else:    
        answer = results['results'][0]
        output = {
            "name": answer.get('name'),
            "phone" : answer.get('phone'),
            "formatted_address" : answer.get('formatted_address'),
            "latitude": answer.get('geometry').get('location').get('lat'),
            "longitude": answer.get('geometry').get('location').get('lng'),
            "accuracy": answer.get('geometry').get('location_type'),
            "google_place_id": answer.get("place_id"),
            "type": ",".join(answer.get('types')),
            "postcode": ",".join([x['long_name'] for x in answer.get('address_components') 
                                  if 'postal_code' in x.get('types')])
        }
        
    # Append some other details: 
    output['input_string'] = address
    output['number_of_results'] = len(results['results'])
    output['status'] = results.get('status')
    if return_full_response is True:
        output['response'] = results
    
    return output

#------------------ PROCESSING LOOP -----------------------------

# Ensure, before we start, that the API key is ok/valid, and internet access is ok
test_result = get_google_results("London, England", API_KEY, RETURN_FULL_RESULTS)
if (test_result['status'] != 'OK') or (test_result['formatted_address'] != 'London, UK'):
    logger.warning("There was an error when testing the Google Geocoder.")
    print(test_result)
    raise ConnectionError('Problem with test results from Google Geocode - check your API key and internet connection.')

# Create a list to hold results
results = []
# Go through each address in turn


for index, row in df.iterrows():
    address = row[address_column_name]

    # If this is partially complete data, and this row already has been geocoded, then skip it:
    if ('google_place_id_geo' in row) and (pd.notnull( row['google_place_id_geo']) ):
        # print('skipping', address)
        continue    

    # While the address geocoding is not finished:
    geocoded = False
    while geocoded is not True:
        # Geocode the address with google
        try:
            geocode_result = get_google_results(address, API_KEY, return_full_response=RETURN_FULL_RESULTS)
        except Exception as e:
            logger.exception(e)
            logger.error("Major error with {}".format(address))
            logger.error("Skipping!")
            geocoded = True
            
        # If we're over the API limit, backoff for a while and try again later.
        if geocode_result['status'] == 'OVER_QUERY_LIMIT':
            logger.info("Hit Query Limit! Backing off for a bit.")
            time.sleep(BACKOFF_TIME * 60) # sleep for 30 minutes
            geocoded = False
        else:
            # If we're ok with API use, save the results
            # Note that the results might be empty / non-ok - log this
            if geocode_result['status'] != 'OK':
                logger.warning("Error geocoding {}: {}".format(address, geocode_result['status']))
            logger.debug("Geocoded: {}: {}".format(address, geocode_result['status']))

            for r_key in geocode_result.keys():
                df.at[index, r_key+'_geo'] = str(geocode_result[r_key])
            results.append(geocode_result)           
            geocoded = True

    # Print status every 100 addresses
    if len(results) % 100 == 0:
        logger.info("Completed {} of {} address".format(len(results), len(addresses)))
            
    # Every 500 addresses, save progress to file(in case of a failure so you have something!)
    if len(results) % 500 == 0:
        df.to_csv("{}_bak".format(output_filename))

# All done
logger.info("Finished geocoding all addresses")

# Write the full results to csv using the pandas library.
df.to_csv(output_filename, index=False, encoding='utf8')
