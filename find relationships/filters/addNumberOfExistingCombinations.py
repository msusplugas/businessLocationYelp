"""
Given a csv file that contains the frequencies and median distances of a combinaison of categories, we write in a new
csv file how many business that has already this combination exist in the current dataset.
E.g. if initialCategory is A and matching Category is B then we will look in the dataset how many businesses have categoryA or categoryB or (categoryA and categoryB)
"""
import json
import csv
from collections import namedtuple

state = "NV"

dictOfBusinessesPerId = {}
dictOfCategoriesTuple = {}

Categories = namedtuple("Categories", ["categoryA","categoryB"])


jsonDatasetInputFileName = '../dataset/yelp_academic_dataset_business.json'
csvMedianDistancesAndMatchingCategoriesFrequenciesInputFileName = '../resultsFound/distances/medianDistancesAndMatchingCategoriesFrequencies' + state +'.csv'

csvMedianDistancesAndMatchingCategoriesFrequenciesWithCategoriesCountOutputFileName = '../resultsFound/filters/categoriesCountMedianDistancesAndMatchingCategoriesFrequencies' + state +'.csv'

# First we import the yelp dataset json file and we add everything in a dictionnary of categories
with open(jsonDatasetInputFileName) as fin:
    for line in fin:
        line_contents = json.loads(line)
        if line_contents['state'] == state:
            businessId = line_contents['business_id']
            categories = line_contents['categories']
            dictOfBusinessesPerId[businessId] = categories

fin.close()

i = 0
f = open(csvMedianDistancesAndMatchingCategoriesFrequenciesWithCategoriesCountOutputFileName, 'w')

with open(csvMedianDistancesAndMatchingCategoriesFrequenciesInputFileName) as csvfile:
    reader = csv.reader(csvfile,  quotechar="'")
    for row in reader: # read a row as {column1: value1, column2: value2,...}
        i+= 1
        print i
        initialCategory = row[0].replace("'","").replace("\\","'")

        rowListClean = []
        for row2 in row:
           if row2 != row[0]:
               rowListClean.append(row2.replace("'","").replace("\\","'"))

        matchingCategoriesWithFrequenciesAndDistances = rowListClean
        #print matchingCategoriesWithFrequenciesAndDistances
        dataToWrite = "'" + initialCategory.replace("'", r"\'") + "'"
        for matchingCategoryWithFrequencyAndDistance in matchingCategoriesWithFrequenciesAndDistances:
            matchingCategorySplit = matchingCategoryWithFrequencyAndDistance.split(":")
            matchingCategory = matchingCategorySplit[0]
            matchingCategorySplitAgain = matchingCategorySplit[1].split("-")
            matchingCategoryFequency = matchingCategorySplitAgain[0].strip()
            matchingCategoryDistance =  matchingCategorySplitAgain[1].strip()

            matchingCategoryAAndBCount = 0
            categoryACount = 0
            categoryBCount = 0

            for businessId in dictOfBusinessesPerId:
                if initialCategory in dictOfBusinessesPerId[businessId]:
                    if matchingCategory in dictOfBusinessesPerId[businessId]:
                        matchingCategoryAAndBCount += 1
                    categoryACount += 1
                if matchingCategory in dictOfBusinessesPerId[businessId]:
                    categoryBCount += 1

            dataToWrite += "," + "'" + matchingCategory.replace("'", r"\'") + ": " + str(matchingCategoryFequency) + " - " \
                           + str(matchingCategoryDistance) + " - " + str(matchingCategoryAAndBCount) + " / " + str(categoryACount) + " / " + str(categoryBCount) + "'"
        f.write(dataToWrite)
        f.write("\n")


f.close()
csvfile.close()