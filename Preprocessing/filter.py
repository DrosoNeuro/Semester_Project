from collections import namedtuple
from itertools import repeat

import gzip
import os
import io
import json
import re
import string
import sys
import multiprocessing as mp
import glob
import uuid
import configparser
import csv

##############################################################################
################### Configurable Params ######################################
##############################################################################
#See config.ini
Config = configparser.ConfigParser()
Config.read("config.ini")

NUM_OF_PROCESSES = 30
OUTPUT_DIRECTORY = "Dump"
STRIP = True


def ensure_output_paths_exist():
    # ensure OUTPUT_DIRECTORY exists
    try:
        os.mkdir(OUTPUT_DIRECTORY)
    except:
        #TODO: Use the correct exception here
        pass


##############################################################################
############### Run through all folders ######################################
##############################################################################

def run_all(path):
    """This will allow to run all the directories from a path"""

    file_paths = glob.glob(path+"/*.gz")
    # Based on the current tweet storage mechanism (from Todd's code)
    ensure_output_paths_exist()

    # If NUM_OF_PROCESSES is False, use mp.cpu_count
    pool = mp.Pool(NUM_OF_PROCESSES or mp.cpu_count())

    pool.starmap(gzworker, zip(file_paths, repeat(STRIP)), chunksize=1)

    pool.close()



##############################################################################
###################### Worker Function #######################################
##############################################################################

def gzworker(fullpath, strip="True"):
    """Worker opens one .gz file"""
    print('Processing {}'.format(fullpath))
    tweet_buffer = []
    try:
        with gzip.open(str(fullpath), 'rb') as infile:
            decoded = io.TextIOWrapper(infile, encoding='utf8')
            for _line in decoded:
                if _line.strip() != "":
                    json_data = _line.split('|', 1)[1][:-1]

                    result = tweet_select(json.loads(json_data))
                    if result:
                        tweet_buffer.append(result)

    except:
        print("Error in {}".format(fullpath))
        pass

    #Write to OUTPUT_DIRECTORY (if _buffer has contents)
    if tweet_buffer != None:
        print("going to save")
        OUTPUT_PATH = "%s/%s.csv" % (OUTPUT_DIRECTORY, fullpath[5:-3])

        with open(OUTPUT_PATH, "w", errors='ignore') as csvfile:
           writer = csv.writer(csvfile)
           for row in tweet_buffer:
               writer.writerow(row)

    print('Finished {}'.format(fullpath))


##############################################################################
###################### Select Function #######################################
##############################################################################
def tweet_select(tweet_obj):
    if tweet_obj["coordinates"] is not None:
        tweet_id = tweet_obj["id"]
        tweet_date = tweet_obj["created_at"]
        tweet_text = tweet_obj["text"]
        tweet_coordinates = tweet_obj["coordinates"]["coordinates"]
        tweet_type = "coordinates"

    elif tweet_obj["geo"] is not None:
        tweet_id = tweet_obj["id"]
        tweet_date = tweet_obj["created_at"]
        tweet_text = tweet_obj["text"]
        tweet_coordinates = tweet_obj["geo"]["coordinates"]
        tweet_type = "geo"

    elif "place" in tweet_obj:
        tweet_id = tweet_obj["id"]
        tweet_date = tweet_obj['created_at']
        tweet_text = tweet_obj["text"]
        tweet_coordinates = tweet_obj["place"]['bounding_box']['coordinates']
        tweet_type = "place"


    big_block = []
    big_block.append(tweet_id)
    big_block.append(tweet_date)
    big_block.append(tweet_text)
    big_block.append(tweet_coordinates)
    big_block.append(tweet_type)
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
