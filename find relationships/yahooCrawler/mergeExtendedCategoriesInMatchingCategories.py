"""
Import the two csv files that contain the matching categories and the extedended categories
Then in the matching categories file we will agglomerate every extended categories
"""
import operator
from collections import Counter
import csv

def convertAnExtendedCategoryToListOfCategories(extendedCategory, dictOfExtendedCategories):
    contained = []
    for category in dictOfExtendedCategories:
        if extendedCategory in dictOfExtendedCategories[category] or extendedCategory == category.lower():
            contained.append(category)
    return contained


csvMatchingCategorieslInputFileName = '../resultsFound/yahooCrawler/matchingCategoriesAZ.csv'
csvExtendedCategoriesInputFileName = '../resultsFound/yahooCrawler/categoriesAZExtendedCategoriesWith025Improved2.csv'

csvStatMatchingCategoriesMergedOutputFileName = '../resultsFound/yahooCrawler/statsMatchingCategoriesMergedAZImproved.csv'

dictOfOldMatchingCategories = {}
dictOfExtendedCategories = {}
dictOfNewMatchingCategories = {} #The new dict where we have replaced the extended categories

with open(csvMatchingCategorieslInputFileName) as csvfile:
    reader = csv.reader(csvfile,  quotechar="'")
    for row in reader: # read a row as {column1: value1, column2: value2,...}
        category = row[0].replace("'","").replace("\\","'")

        rowListClean = []
        for row2 in row:
           if row2 != row[0]:
               rowListClean.append(row2.replace("'","").replace("\\","'"))


        dictOfOldMatchingCategories[category] = rowListClean
csvfile.close()

with open(csvExtendedCategoriesInputFileName) as csvfile:
    reader = csv.reader(csvfile,  quotechar="'")
    for row in reader: # read a row as {column1: value1, column2: value2,...}
        category = row[0].replace("'","").replace("\\","'")
        dictOfExtendedCategories[category] = [x.replace("'","").replace("\\","'").lower() for x in row[1:]] #We lower case every extended category
csvfile.close()


"""
Category1 is the category that has the matching categories (first element of a row of matchingCategories)
Category2 is a category that have been extended (other elements of a row in matchingCategories)
"""
i = 0
lengthOfDict = str(len(dictOfOldMatchingCategories))
for category1 in dictOfOldMatchingCategories:
    i += 1
    print str(i) + "/" + lengthOfDict
    dictOfNewMatchingCategories[category1] = {}
    for row in dictOfOldMatchingCategories[category1]:
        listOfCategoriesThatHaveThisExtendedCategory = convertAnExtendedCategoryToListOfCategories(row, dictOfExtendedCategories)
        if listOfCategoriesThatHaveThisExtendedCategory:
            for category2 in listOfCategoriesThatHaveThisExtendedCategory:
                if dictOfNewMatchingCategories[category1].has_key(category2):
                    dictOfNewMatchingCategories[category1][category2] += 1
                else:
                    dictOfNewMatchingCategories[category1][category2] = 1



f = open(csvStatMatchingCategoriesMergedOutputFileName, 'w')
for category in dictOfNewMatchingCategories:
    data = "'" + category.replace("'", r"\'") + "'"
    counts = Counter(dictOfNewMatchingCategories[category])
    orderedDict = sorted(counts.items(), key=operator.itemgetter(1))
    orderedDict.reverse()
    for row in orderedDict:
        data += "," + "'" + row[0].replace("'", r"\'") + ": " + str(row[1]) +"'"
        # row[0] is the name and row[1] is the number of times this name was present in this category

    f.write(data + "\n")