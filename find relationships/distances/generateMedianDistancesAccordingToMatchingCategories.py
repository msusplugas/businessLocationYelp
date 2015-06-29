"""
For each category (we call it "initialCategory) in the stats of matching category csv. We look at each matching category and for each matching category
we look for each business that belongs in "initialCategory", what is the closest distance to other business of other matching categories.
"""
import csv
import json
from collections import namedtuple
import computeDistances
from operator import itemgetter


state = "AZ"
Categories = namedtuple("Categories", ["categoryA","categoryB"])

csvStatMatchingCategoriesMergedInputFileName = '../resultsFound/yahooCrawler/statsMatchingCategoriesMergedAZ.csv'
jsonDatasetInputFileName = '../dataset/yelp_academic_dataset_business.json'

csvMedianDistancesAndMatchingCategoriesFrequenciesOutputFileName = '../resultsFound/distances/medianDistancesAndMatchingCategoriesFrequencies.csv'

dictOfMatchingCategories = {}
dictOfBusinesses = {}
dictOfMatchingCategoriesWithDistance = {}
dictOfCategoriesWithMedian = {}


#These values are the minimal and maximal values for the latitude/longitude
minLatitude = 180
maxLatitude = -180
minLongitude = 180
maxLongitude = -180

#We import the existing data from the csv file
with open(csvStatMatchingCategoriesMergedInputFileName) as csvfile:
    reader = csv.reader(csvfile,  quotechar="'")
    for row in reader: # read a row as {column1: value1, column2: value2,...}
        category = row[0].replace("'","").replace("\\","'")
        dictOfMatchingCategories[category] = {}
        for matchingCategory in row[1:]:
            # matchingCategory is like 'Contractors: 25' for instance
            matchingCategorySplit = matchingCategory.replace("'","").replace("\\","'").split(":")
            if len(matchingCategorySplit) > 1:
                matchingCategoryName = matchingCategorySplit[0] #return only the name. e.g. 'Contractors'
                matchingCategoryFrequency = int(matchingCategorySplit[1].strip()) #return the number. e.g. '25'
                dictOfMatchingCategories[category][matchingCategoryName] = matchingCategoryFrequency

csvfile.close()


with open(jsonDatasetInputFileName) as fin:
    for line in fin:
        line_contents = json.loads(line)
        if line_contents['state'] == state:
            businessId = line_contents['business_id']
            categories = line_contents['categories']
            longitude = line_contents['longitude']
            latitude = line_contents['latitude']
            categories = [x.encode('UTF8') for x in categories]

            if latitude < minLatitude:
                minLatitude = latitude
            if latitude > maxLatitude:
                maxLatitude = latitude
            if longitude < minLongitude:
                minLongitude = longitude
            if longitude > maxLongitude:
                maxLongitude = longitude


            dictOfBusinesses[businessId] = {"categories": categories, "longitude": longitude, "latitude": latitude}


grid = computeDistances.insertBusinessesInGrid(dictOfBusinesses, minLatitude, maxLatitude, minLongitude, maxLongitude)


f = open(csvMedianDistancesAndMatchingCategoriesFrequenciesOutputFileName, 'w')
i = 0
for initialCategory in dictOfMatchingCategories:
    i += 1
    print str(i) + "/" + str(len(dictOfMatchingCategories))
    categoryA = initialCategory
    for matchingCategory in dictOfMatchingCategories[initialCategory]:
        categoryB = matchingCategory
        categoriesNamedTuple = Categories(categoryA=categoryA,categoryB=categoryB)
        if dictOfCategoriesWithMedian.has_key(categoriesNamedTuple):
            medianDistance = dictOfCategoriesWithMedian[categoriesNamedTuple]
        else:
            medianDistance = computeDistances.computeMedianDistanceForGrid(categoryA,categoryB, grid)
            dictOfCategoriesWithMedian[categoriesNamedTuple] = medianDistance

    dataToWrite = "'" + categoryA.replace("'", r"\'") + "'"
    listOfMatchingCategories = dictOfMatchingCategories[categoryA].items()
    sortList = sorted(listOfMatchingCategories,key=itemgetter(1))
    sortList.reverse()

    for categoryBWithFrequency in sortList:
        categoryB = categoryBWithFrequency[0]
        categoryBFrequency = categoryBWithFrequency[1]
        categoriesNamedTuple = Categories(categoryA=categoryA,categoryB=categoryB)
        categoryBMedianDistance = dictOfCategoriesWithMedian[categoriesNamedTuple]

        dataToWrite +=  "," + "'" + categoryB.replace("'", r"\'") + "" + ": " + str(categoryBFrequency) + " - " + str(categoryBMedianDistance) + "'"

    f.write(dataToWrite)
    f.write("\n")


f.close()