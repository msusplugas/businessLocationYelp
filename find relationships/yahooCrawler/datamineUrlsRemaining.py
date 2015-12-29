"""
We complete the matching categories that have failed (timeout in datamineUrls.py)
It fails if the matching category has no other category in it.
"""

import csv
import signal
import requests
from bs4 import BeautifulSoup
import time


"""
Timeout functions for websites which doesn't answer
"""

class TimeoutException(Exception):   # Custom exception class
    pass

def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException

# Change the behavior of SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)

state = 'NV'

csvWithUrlInputFileName = '../resultsFound/yahooCrawler/categories' + state +  'WithUrl.csv'
csvExtendedCategoriesInputFileName = '../resultsFound/yahooCrawler/categories' + state + 'ExtendedCategories.csv'
csvMatchingCategoriesInputFileName = '../resultsFound/yahooCrawler/matchingCategories' + state + '.csv'

csvNewMatchingCategoriesOutputFileName = '../resultsFound/yahooCrawler/newMatchingCategories' + state + '.csv'


dictOfCategoriesWithUrl = {}
dictOfExtendedCategories = {}
dictOfCategoriesWithMatchingCategories = {}


with open(csvExtendedCategoriesInputFileName) as csvfile:
    reader = csv.reader(csvfile,  quotechar="'", skipinitialspace=True)
    for row in reader:
        initialCategory = row[0].replace("'","").replace("\\","'")
        rowListClean = []

        for row2 in row:
            if row2:
                rowListClean.append(row2.replace("'","").replace("\\","'"))

        dictOfExtendedCategories[initialCategory] = rowListClean

csvfile.close()

with open(csvWithUrlInputFileName) as csvfile:
    reader = csv.DictReader(csvfile,  quotechar="'", skipinitialspace=True)
    for row in reader: # read a row as {column1: value1, column2: value2,...}
        category = row["category"].replace("'","").replace("\\","'")
         #We skip the first value which is the category, here we want only the links. The category is the key of the dict
        # and is in the position 2 of rowList
        rowList = row.values()
        rowListClean = []
        for row in rowList:
            if row and row.replace("'","").replace("\\","'") != category:
                rowListClean.append(row.replace("'","").replace("\\","'"))

        dictOfCategoriesWithUrl[category] = rowListClean
csvfile.close()

print "start to work on the bugged categories"

with open(csvMatchingCategoriesInputFileName) as csvfile:
    reader = csv.reader(csvfile,  quotechar="'", skipinitialspace=True)
    for row in reader: # read a row as {column1: value1, column2: value2,...}
        category = row[0].replace("'","").replace("\\","'")

        if len(row) > 1: #If we have the initialCategory and the other categories.
            dictOfCategoriesWithMatchingCategories[category] = row[1:]

        else: #If we have only the initialCategory:
            t0 = time.time()

            print category

            dictOfOtherCategoriesExtended = dict(dictOfExtendedCategories)
            if dictOfOtherCategoriesExtended.has_key(category):
                dictOfOtherCategoriesExtended.pop(category)
            else:
                print "CATEGORY NOT FOUND: " + category

            listOfUrls = dictOfCategoriesWithUrl[category]

            for url in listOfUrls:
                try:
                    signal.alarm(15) #After 15s for a single url, we reset
                    requestedUrl = requests.get(url)
                    if requestedUrl.ok:
                        #remove html from the raw content:
                        content = BeautifulSoup(requestedUrl.content).get_text().lower()

                        """
                        contained is the list of other categories that contains the response
                         e.g. if the current category is "a" and other categories are "b","c","d".
                         Then if response contains "b", "a" and "d", finally contained will have the value: ["b","d"]

                         We also lowercase everything so that we will not have to care about sensistive case

                        """
                        contained = [x.lower() for x in dictOfOtherCategoriesExtended if x.lower() in content]


                        if contained:
                            if category in dictOfCategoriesWithMatchingCategories:
                                dictOfCategoriesWithMatchingCategories[category].extend(contained)
                                #print dictOfCategoriesWithMatchingCategories[category]
                            else:
                                dictOfCategoriesWithMatchingCategories[category] = contained
                                #print dictOfCategoriesWithMatchingCategories[category]

                        contained = []

                except Exception as e:
                    print str(category) + ": " + url + " not working: " + str(e)
                    continue

                finally:
                    signal.alarm(0)
                    
            t1 = time.time()
            print str(t1 - t0) + " s"

csvfile.close()

print "We write the new file"

f = open(csvNewMatchingCategoriesOutputFileName, 'w')
for category in dictOfCategoriesWithMatchingCategories:
    data = "'" + category.replace("'", r"\'") + "'"

    for row in dictOfCategoriesWithMatchingCategories[category]:
        data += "," + "'" + row.replace("'", r"\'") + "'"

    f.write(data + "\n")

f.close()