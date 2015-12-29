"""
Here we filter the csv file previously generated that contains the list of relationships with the median distances, frequency and numbers of businesses per category.
We filter this csv file with different parameters:
- percentile of frequencies
- percentile of median distances
- percentile of number of businesses in initialCategory
- percentile of number of businesses in matchingCategory
"""
import csv
import numpy as np

state = 'NV'

csvMatchingCategoriesInputFileName = "../resultsFound/filters/categoriesCountMedianDistancesAndMatchingCategoriesFrequencies" + state + ".csv"
csvOutputFilteredFileName = '../resultsFound/filters/filter-' + state +'.csv'
dictOfCategories = {}
listOfFrequencies = []
listOfMedianDistances = []
listOfCategoryAAndBCount = []
listOfCategoryACount = []
listOfCategoryBCount = []

with open(csvMatchingCategoriesInputFileName) as csvfile:
    reader = csv.reader(csvfile,  quotechar="'", skipinitialspace=True)
    for row in reader:
        initialCategory = row[0].replace("'","").replace("\\","'")
        dictOfCategories[initialCategory] = {}
        for row2 in row:
            if row2 != row[0]:
                categoryCleaned = (row2.replace("'","").replace("\\","'"))
                categoryCleanedSplitByColon = categoryCleaned.split(":")
                nameOfTheCategory = categoryCleanedSplitByColon[0]
                categoryCleanedSplitByDash = categoryCleanedSplitByColon[1].split("-")
                frequencyOfTheCategory = categoryCleanedSplitByDash[0].strip()
                medianDistanceOfTheCategory = categoryCleanedSplitByDash[1].strip()
                categoryCleanedSplitBySlash = categoryCleanedSplitByDash[2].split("/")
                categoryAAndBCount = categoryCleanedSplitBySlash[0].strip()
                categoryACount = categoryCleanedSplitBySlash[1].strip() #category A : initial Category
                categoryBCount = categoryCleanedSplitBySlash[2].strip() #categoryB : matching category

                dictOfCategories[initialCategory][nameOfTheCategory] = {
                    "frequency": int(frequencyOfTheCategory),
                    "medianDistance": medianDistanceOfTheCategory,
                    "categoryAAndBCount": int(categoryAAndBCount),
                    "categoryACount": int(categoryACount),
                    "categoryBCount": int(categoryBCount)
                }
                listOfFrequencies.append(int(frequencyOfTheCategory))
                if medianDistanceOfTheCategory != "None":
                    listOfMedianDistances.append(float(medianDistanceOfTheCategory))
                listOfCategoryAAndBCount.append(int(categoryAAndBCount))
                listOfCategoryACount.append(int(categoryACount))
                listOfCategoryBCount.append(int(categoryBCount))


csvfile.close()
print len(dictOfCategories)

percentileFrequencyRequired = 9 #Same as Phoenix
percentileMedianDistancesRequired = 112.25305 #Same as Phoenix
percentileCategoryACountRequired = 3 #Same as Phoenix
percentileCategoryBCountRequired = 3 #Same as Phoenix



f = open(csvOutputFilteredFileName, 'w')
i= 0
j = 0
for categoryA in dictOfCategories:
    initialCategory = categoryA
    i += 1
    dataToWrite = "'" + categoryA.replace("'", r"\'") + "'"
    for matchingCategory in dictOfCategories[initialCategory]:
        categoryB = matchingCategory
        categoryBFrequency = dictOfCategories[initialCategory][matchingCategory]["frequency"]
        categoryBMedianDistance = dictOfCategories[initialCategory][matchingCategory]["medianDistance"]
        categoryAAndBCount = dictOfCategories[initialCategory][matchingCategory]["categoryAAndBCount"]
        categoryACount = dictOfCategories[initialCategory][matchingCategory]["categoryACount"]
        categoryBCount = dictOfCategories[initialCategory][matchingCategory]["categoryBCount"]

        if int(categoryBFrequency) >=  percentileFrequencyRequired and categoryBMedianDistance != "None" \
                and float(categoryBMedianDistance) <= percentileMedianDistancesRequired and float(categoryACount) >= percentileCategoryACountRequired \
                and float(categoryBCount) >= percentileCategoryBCountRequired:
            dataToWrite += "," + "'" + categoryB.replace("'", r"\'") + ": " + str(categoryBFrequency) + " - " \
                           + str(categoryBMedianDistance) + " - " + str(categoryAAndBCount) + " / " + str(categoryACount) + " / " + str(categoryBCount) + "'"


    f.write(dataToWrite + "\n")
    j += 1

print len(dictOfCategories)
print i
print j
