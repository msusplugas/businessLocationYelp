"""
Read the two matching categories file and merge them
"""
import csv

state = 'NV'

csvNewMatchingCategoriesInputFileName = '../resultsFound/yahooCrawler/newMatchingCategories' + state + '.csv'
csvMatchingCategoriesInputFileName = '../resultsFound/yahooCrawler/matchingCategories' + state + '.csv'

csvCombinedMatchingCategoriesOutputName = '../resultsFound/yahooCrawler/combinedMatchingCategories' + state + '.csv'

dictOfNewMatchingCategories = {}
dictOfMergeMatchingCategories = {}


with open(csvNewMatchingCategoriesInputFileName) as csvfile:
    reader = csv.reader(csvfile,  quotechar="'", skipinitialspace=True)
    for row in reader:
        initialCategory = row[0].replace("'","").replace("\\","'")
        rowListClean = []

        for row2 in row:
            if row2 != row[0]:
                rowListClean.append(row2.replace("'","").replace("\\","'"))

        dictOfMergeMatchingCategories[initialCategory] = rowListClean

csvfile.close()

print "first import done"

f = open(csvCombinedMatchingCategoriesOutputName, 'w')

with open(csvMatchingCategoriesInputFileName) as csvfile:
    reader = csv.reader(csvfile,  quotechar="'", skipinitialspace=True)
    for row in reader:
        initialCategory = row[0].replace("'","").replace("\\","'")
        if len(row) > 1:
            rowListClean = []

            for row2 in row:
                if row2 != row[0]:
                    rowListClean.append(row2.replace("'","").replace("\\","'"))
            categories = rowListClean
        else:
            categories = dictOfMergeMatchingCategories[initialCategory]

        data = "'" + initialCategory.replace("'", r"\'") + "'"

        for row2 in categories:
            data += "," + "'" + row2.replace("'", r"\'") + "'"

        f.write(data + "\n")


csvfile.close()
