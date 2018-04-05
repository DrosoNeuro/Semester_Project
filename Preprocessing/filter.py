from collections import namedtuple
from itertools import repeat

import reverse_geocoder as rg
import gzip
import os
import io
import json
import re
import string
import sys
import multiprocessing as mp
import multiprocessing.pool
import glob
import uuid
import csv

mx_ca_us_state_abbrev = {
    'Alabama': '1',
    'Alaska': '2',
    'Arizona': '3',
    'Arkansas': '4',
    'California': '5',
    'Colorado': '6',
    'Connecticut': '7',
    'Delaware': '8',
    'Florida': '9',
    'Georgia': '10',
    'Hawaii': '11',
    'Idaho': '12',
    'Illinois': '13',
    'Indiana': '14',
    'Iowa': '15',
    'Kansas': '16',
    'Kentucky': '17',
    'Louisiana': '18',
    'Maine': '19',
    'Maryland': '20',
    'Massachusetts': '21',
    'Michigan': '22',
    'Minnesota': '23',
    'Mississippi': '24',
    'Missouri': '25',
    'Montana': '26',
    'Nebraska': '27',
    'Nevada': '28',
    'New Hampshire': '29',
    'New Jersey': '30',
    'New Mexico': '31',
    'New York': '32',
    'North Carolina': '33',
    'North Dakota': '34',
    'Ohio': '35',
    'Oklahoma': '36',
    'Oregon': '37',
    'Pennsylvania': '38',
    'Rhode Island': '39',
    'South Carolina': '40',
    'South Dakota': '41',
    'Tennessee': '42',
    'Texas': '43',
    'Utah': '44',
    'Vermont': '45',
    'Virginia': '46',
    'Washington': '47',
    'West Virginia': '48',
    'Wisconsin': '49',
    'Wyoming': '50',
    'Ontario': '51',
    'Quebec': '52',
    'Nova Scotia': '53',
    'New Brunswick': '54',
    'Manitoba': '55',
    'British Columbia': '56',
    'Prince Edward': '57',
    'Saskatchewan': '58',
    'Alberta': '59',
    'Newfoundland and Labrador': '60',
    'Washington, D.C.': '61',
    'Chihuahua': '62',
    'Baja California': '63',
    'Freeport': '64',
    'Nuevo Leon': '65',
}

##############################################################################
################### Configurable Params ######################################
##############################################################################

NUM_OF_PROCESSES = False
# NUM_OF_PROCESSES = 2
#OUTPUT_DIRECTORY = "../../mount/SDF/Dump"
#OUTPUT_DIRECTORY = "Dump"
OUTPUT_DIRECTORY = "../../../../mount/SDF/TweetDumpInclUser"


def ensure_output_paths_exist():
    # ensure OUTPUT_DIRECTORY exists
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)


##############################################################################
############### Run through all folders ######################################
##############################################################################

def run_all(path):
    """This will allow to run all the directories from a path"""
    #file_paths = glob.glob(path+"/*/*.gz")
    file_paths = glob.glob(path+"/*.gz")
    # Based on the current tweet storage mechanism (from Todd's code)
    ensure_output_paths_exist()

    # If NUM_OF_PROCESSES is False, use mp.cpu_count
    pool = multiprocessing.pool.ThreadPool(NUM_OF_PROCESSES or mp.cpu_count()-2)

    pool.map(gzworker, file_paths, chunksize=1)

    pool.close()




##############################################################################
###################### Worker Function #######################################
##############################################################################

def gzworker(fullpath):
    """Worker opens one .gz file"""
    print('Processing {}'.format(fullpath))
    tweet_buffer = []
    save_name = re.findall('(tweets.*\d{4}-\d{2}-\d{2}_\d{2})',fullpath)
    save_name = save_name[0]
    try:
        with gzip.open(str(fullpath), 'rb') as infile:
            decoded = io.TextIOWrapper(infile, encoding='utf8')
            for _line in decoded:
                if _line.strip() != "":
                    json_data = _line.split('|', 1)[1][:-1]
                    result = tweet_select(json.loads(json_data))
                    if result:
                        tweet_buffer.append(result)

        #Write to OUTPUT_DIRECTORY (if _buffer has contents)
        if tweet_buffer != None:
            print("going to save")
            #OUTPUT_PATH = "%s/%s.csv" % (OUTPUT_DIRECTORY, fullpath[50:-3])
            OUTPUT_PATH = "%s/%s.csv" % (OUTPUT_DIRECTORY, save_name)
            print(OUTPUT_PATH)
            # OUTPUT_PATH = "%s/%s.csv" % (OUTPUT_DIRECTORY, fullpath[5:-3])

            with open(OUTPUT_PATH, "w", errors='ignore') as csvfile:
               writer = csv.writer(csvfile)
               for row in tweet_buffer:
                   writer.writerow(row)
    except:
        print("Error in {}".format(fullpath))
        pass

    print('Finished {}'.format(fullpath))


##############################################################################
###################### Select Function #######################################
##############################################################################
def tweet_select(tweet_obj):
    if tweet_obj["coordinates"] is not None:
        tweet_id = tweet_obj["id"]
        user_id = tweet_obj["user"]["id_str"]
        tweet_date = tweet_obj["created_at"]
        tweet_text = tweet_obj["text"]
        tweet_coordinates = tweet_obj["coordinates"]["coordinates"]
        tweet_type = "coordinates"

    elif tweet_obj["geo"] is not None:
        tweet_id = tweet_obj["id"]
        user_id = tweet_obj["user"]["id_str"]
        tweet_date = tweet_obj["created_at"]
        tweet_text = tweet_obj["text"]["user"]["id_str"]
        tweet_coordinates = tweet_obj["geo"]["coordinates"]
        tweet_type = "geo"

    elif "place" in tweet_obj:
        tweet_id = tweet_obj["id"]
        user_id = tweet_obj["user"]["id_str"]
        tweet_date = tweet_obj['created_at']
        tweet_text = tweet_obj["text"]
        tweet_coordinates = tweet_obj["place"]['bounding_box']['coordinates']
        tweet_type = "place"

    #geoloc = str(tweet_coordinates).split(',')
    #lon = geoloc[0].replace('[', '')
    #lat = geoloc[1].replace(']', '').replace(' ', '')
    #coordinates = (lat,lon)
    #results = rg.search(coordinates) # default mode = 2
    #state_num = mx_ca_us_state_abbrev.get(results[0].get('admin1'))

    big_block = []
    big_block.append(tweet_id)
    big_block.append(user_id)
    big_block.append(tweet_date)
    big_block.append(tweet_text)
    big_block.append(tweet_coordinates)
    big_block.append(tweet_type)
    #big_block.append(state_num)

    return big_block


##############################################################################
###################### Filter Function #######################################
##############################################################################

def tweet_filter(tweet_obj, condition, key="text", strip="True"):
    """Will return the tweet object if the conditions are met in the specific tweet_obj"""

    if key in tweet_obj:
        if strip:
            text = strip_all_entities(strip_links(tweet_obj[key]))
        else:
            text = tweet_obj[key]
    else:
        print("Not a valid key (" + key + ")")
        sys.exit(1)

    if evaluate_condition(text, parse_condition(tokenize_condition(condition))):
        return tweet_obj
    else:
        return None

##############################################################################
############### Function to remove url/#/@ from text for filter ##############
##############################################################################

def strip_links(text):
    """Will remove the links from the text"""
    link_regex = re.compile('((https?):((//)|(\\\\))+([\w\d:#@%/;'
                            '$()~_?\+-=\\\.&](#!)?)*)', re.DOTALL)
    links = re.findall(link_regex, text)
    for link in links:
        text = text.replace(link[0], ', ')
    return text

def strip_all_entities(text):
    """Will remove the tags and hashtags from the text"""
    entity_prefixes = ['@', '#']
    for separator in string.punctuation:
        if separator not in entity_prefixes:
            text = text.replace(separator, ' ')
    words = []
    for word in text.split():
        word = word.strip()
        if word:
            if word[0] not in entity_prefixes:
                words.append(word)
    return ' '.join(words)
