import reverse_geocoder as rg
import csv
import multiprocessing as mp
import glob
import re

# coordinates = (30.5029812,-84.2449241)
#
# results = rg.search(coordinates) # default mode = 2
#
# print(results)

NUM_OF_PROCESSES = 1

def ensure_output_paths_exist():
    """Maybe we will not use this since we will be editing the files directly"""
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

    file_paths = glob.glob(path+"/*.csv")
    # Based on the current tweet storage mechanism (from Todd's code)
    # ensure_output_paths_exist()

    # If NUM_OF_PROCESSES is False, use mp.cpu_count
    pool = mp.Pool(NUM_OF_PROCESSES or mp.cpu_count())

    pool.map(gzworker, file_paths, chunksize=1)

    pool.close()

##############################################################################
###################### Worker Function #######################################
##############################################################################

# def gzworker(fullpath):
#     """Worker opens one .gz file"""
#     print('Processing {}'.format(fullpath))
#     tweet_buffer = []
#     try:
#         with open(fullpath, 'r+') as f:
#             reader = csv.reader(f)
#             #TODO: location = ???
#             location = blob
#             out_lines = [row + [lstName[i]] for i, row in enumerate(reader)]
#             # f.seek(0)    # set file position to the beginning of the file
#             csv.writer(f, delimiter=',').writerows(out_lines)
#
#
#         with csv.open(str(fullpath), 'rb') as infile:
#             decoded = io.TextIOWrapper(infile, encoding='utf8')
#             for _line in decoded:
#                 if _line.strip() != "":
#                     json_data = _line.split('|', 1)[1][:-1]
#
#                     result = tweet_select(json.loads(json_data))
#                     if result:
#                         tweet_buffer.append(result)
#
#     except:
#         print("Error in {}".format(fullpath))
#         pass
#
#     #Write to OUTPUT_DIRECTORY (if _buffer has contents)
#     if tweet_buffer != None:
#         print("going to save")
#         OUTPUT_PATH = "%s/%s.csv" % (OUTPUT_DIRECTORY, fullpath[5:-3])
#
#         with open(OUTPUT_PATH, "w", errors='ignore') as csvfile:
#            writer = csv.writer(csvfile)
#            for row in tweet_buffer:
#                writer.writerow(row)
#
#     print('Finished {}'.format(fullpath))

def gzworker(fullpath):
    """Worker will open the .csv file and process the information inside"""
    print('Processing {}'.format(fullpath))
    # try:
    with open(fullpath, 'r+') as f:
        reader = csv.reader(f)
        for row in reader:
            geoloc = row[3]
            geoloc = geoloc.split(',')
            lon = geoloc[0].replace('[', '')
            lat = geoloc[1].replace(']', '').replace(' ', '')
            # print('Longitude: {} \nLatitude: {}'.format(lon, lat))
            # m_obj = re.search(r"(\d+)", geoloc)
            # print(m_obj)
            coordinates = (lat,lon)
            results = rg.search(coordinates) # default mode = 2
            print(results)

    # except:
    #     print("Error in {}".format(fullpath))
    #     pass

    print('Finished {}'.format(fullpath))
#TODO: Get .csv file loaded
#TODO: extract long-lat from tweet
#TODO: invert long-lat
#TODO: use reverse_geocoder to get the information
#TODO: save the information on the same line in the same .csv file
