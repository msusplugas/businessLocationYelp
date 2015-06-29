"""
Read the list of categories and urls from the csv file
Then for each category we look for each url if in the content of the webpage there is another category, if yes then we
add it to our list and then we write our list in a new csv file
"""
import requests
import csv
import time
import grequests
from bs4 import BeautifulSoup
import os
import signal


"""
Timeout functions for websites which doesn't answer
"""
class TimeoutException(Exception):   # Custom exception class
    pass

def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException

# Change the behavior of SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)




csvWithUrlInputFileName = '../resultsFound/yahooCrawler/categoriesAZWithUrl.csv'
csvExtendedCategoriesInputFileName = '../resultsFound/yahooCrawler/categoriesAZExtendedCategoriesWith025Improved2.csv'

csvMatchingCategoriesOutputFileName = '../resultsFound/yahooCrawler/matchingCategoriesAZImproved.csv'

dictOfCategoriesWithUrl = {}
listOfCategories = []
dictOfCategoriesWithMatchingCategories = {}
listOfAlreadyComputedCategories = []

dictOfExtendedCategories = {}

if os.path.isfile(csvMatchingCategoriesOutputFileName):
    #First we see what has been already written in the output file
    with open(csvMatchingCategoriesOutputFileName) as csvfile:
        reader = csv.reader(csvfile,  quotechar="'", skipinitialspace=True)
        for row in reader: # read a row as {column1: value1, column2: value2,...}
            category = row[0]
            listOfAlreadyComputedCategories.append(category)
    csvfile.close()

with open(csvWithUrlInputFileName) as csvfile:
    reader = csv.DictReader(csvfile,  quotechar="'", skipinitialspace=True)
    for row in reader: # read a row as {column1: value1, column2: value2,...}
        category = row["category"].replace("'","").replace("\\","'")
        #We want to compute only the categories that were not computed here
        if category not in listOfAlreadyComputedCategories:
            listOfCategories.append(category)
             #We skip the first value which is the category, here we want only the links. The category is the key of the dict
            # and is in the position 2 of rowList
            rowList = row.values()
            rowListClean = []
            for row in rowList:
                if row and row.replace("'","").replace("\\","'") != category:
                    rowListClean.append(row.replace("'","").replace("\\","'"))


            dictOfCategoriesWithUrl[category] = rowListClean
csvfile.close()

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

if listOfAlreadyComputedCategories:
    print "old csv file"
    f = open(csvMatchingCategoriesOutputFileName, 'a')
else:
    print "new csv file"
    f = open(csvMatchingCategoriesOutputFileName, 'w')
i= 0
for category in dictOfCategoriesWithUrl:

    signal.alarm(300) #After 300s, we reset
    try:

        i += 1
        t0 = time.time()
        print "Currently working on: " + category
        rs = (grequests.get(u) for u in dictOfCategoriesWithUrl[category])

        for response in grequests.map(rs):
            try:
                if response:
                    content = response.content

            except Exception as e:
                print str(response) + " not working: " + str(e)


            dictOfOtherCategoriesExtended = dict(dictOfExtendedCategories)
            if dictOfOtherCategoriesExtended.has_key(category):
                dictOfOtherCategoriesExtended.pop(category)
            else:
                print "CATEGORY NOT FOUND: " + category
            #remove html from the raw content:
            content = BeautifulSoup(content).get_text().lower()

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
                else:
                    dictOfCategoriesWithMatchingCategories[category] = contained

            contained = []


    except Exception as e:
        print str(category) + " not working: " + str(e)
        print "do it manually"

        signal.alarm(0)
        listOfUrls = dictOfCategoriesWithUrl[category]

        for url in listOfUrls:
            try:
                signal.alarm(120) #After 120s for a single url, we reset
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
                        else:
                            dictOfCategoriesWithMatchingCategories[category] = contained

                    contained = []

            except Exception as e:
                print str(category) + ": " + url + " not working: " + str(e)
                continue

            finally:
                signal.alarm(0)

    finally:
        signal.alarm(0)


        t1 = time.time()
        tdiff = t1-t0
        print "current time to go through this category: " + str(tdiff) + " s"
        numberOfCategoriesRemaining = len(dictOfCategoriesWithUrl) - i
        print "There are " + str(numberOfCategoriesRemaining) + " remaining categories"
        ttotal= numberOfCategoriesRemaining * tdiff
        print "So we will need: " + str(ttotal) + " more seconds"

        data = "'" + category.replace("'", r"\'") + "'"

        if dictOfCategoriesWithMatchingCategories.has_key(category): #In case it didn't work, we skip this row and write only the initial category
            for row in dictOfCategoriesWithMatchingCategories[category]:
                data += "," + "'" + row.replace("'", r"\'") + "'"
        f.write(data + "\n")


"""
Now we write in a csv file our results like this:
CategoryA, matchingCategory1, matchingCategory2, ...
where Category is the category where we looked at the 50 different urls, and the matching categories
represent the "keywords" that we found on these urls
"""


f.close()