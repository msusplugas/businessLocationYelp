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

csvMatchingCategoriesInputFileName = "../resultsFound/filters/categoriesCountMedianDistancesAndMatchingCategoriesFrequencies.csv"
csvOutputFilteredFileName = '../resultsFound/filters/filter-90-10-10-10.csv'
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

percentileFrequencyRequired = np.percentile(listOfFrequencies,90)
percentileMedianDistancesRequired = np.percentile(listOfMedianDistances,10)
percentileCategoryACountRequired = np.percentile(listOfCategoryACount,10)
percentileCategoryBCountRequired = np.percentile(listOfCategoryBCount,10)



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


"""
Statistics about the results from the filter
x = []
x2 = []
for i in range(50,99):
    x.append(np.percentile(listOfFrequencies,i))
    x2.append(i)
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}
plt.rc('font', **font)
plt.plot(x2,x,linewidth=2.5)

plt.ylabel("Frequency")
plt.xlabel("Percentile")
plt.show()


print "Show stats"
print "ListOfFrequencies 10: " + str(np.percentile(listOfFrequencies,10))
print "ListOfFrequencies 25: " + str(np.percentile(listOfFrequencies,25))
print "ListOfFrequencies 50: " + str(np.percentile(listOfFrequencies,50))
print "ListOfFrequencies 75: " + str(np.percentile(listOfFrequencies,75))
print "ListOfFrequencies 80: " + str(np.percentile(listOfFrequencies,80))
print "ListOfFrequencies 85: " + str(np.percentile(listOfFrequencies,85))
print "ListOfFrequencies 90: " + str(np.percentile(listOfFrequencies,90))
print "ListOfFrequencies 95: " + str(np.percentile(listOfFrequencies,95))
print "ListOfFrequencies 100: " + str(np.percentile(listOfFrequencies,100))
print "--"
print "listOfMedianDistances 1: " + str(np.percentile(listOfMedianDistances,1))
print "listOfMedianDistances 2: " + str(np.percentile(listOfMedianDistances,2))
print "listOfMedianDistances 3: " + str(np.percentile(listOfMedianDistances,3))
print "listOfMedianDistances 4: " + str(np.percentile(listOfMedianDistances,4))
print "listOfMedianDistances 5: " + str(np.percentile(listOfMedianDistances,5))
print "listOfMedianDistances 6: " + str(np.percentile(listOfMedianDistances,6))
print "listOfMedianDistances 7: " + str(np.percentile(listOfMedianDistances,7))
print "listOfMedianDistances 8: " + str(np.percentile(listOfMedianDistances,8))
print "listOfMedianDistances 9: " + str(np.percentile(listOfMedianDistances,9))
print "listOfMedianDistances 10: " + str(np.percentile(listOfMedianDistances,10))
print "listOfMedianDistances 25: " + str(np.percentile(listOfMedianDistances,25))
print "listOfMedianDistances 50: " + str(np.percentile(listOfMedianDistances,50))
print "listOfMedianDistances 75: " + str(np.percentile(listOfMedianDistances,75))
print "listOfMedianDistances 80: " + str(np.percentile(listOfMedianDistances,80))
print "listOfMedianDistances 85: " + str(np.percentile(listOfMedianDistances,85))
print "listOfMedianDistances 90: " + str(np.percentile(listOfMedianDistances,90))
print "listOfMedianDistances 95: " + str(np.percentile(listOfMedianDistances,95))
print "listOfMedianDistances 100: " + str(np.percentile(listOfMedianDistances,100))
print "--"
print "listOfCategoryAAndBCount 10: " + str(np.percentile(listOfCategoryAAndBCount,10))
print "listOfCategoryAAndBCount 25: " + str(np.percentile(listOfCategoryAAndBCount,25))
print "listOfCategoryAAndBCount 50: " + str(np.percentile(listOfCategoryAAndBCount,50))
print "listOfCategoryAAndBCount 75: " + str(np.percentile(listOfCategoryAAndBCount,75))
print "listOfCategoryAAndBCount 80: " + str(np.percentile(listOfCategoryAAndBCount,80))
print "listOfCategoryAAndBCount 85: " + str(np.percentile(listOfCategoryAAndBCount,85))
print "listOfCategoryAAndBCount 90: " + str(np.percentile(listOfCategoryAAndBCount,90))
print "listOfCategoryAAndBCount 95: " + str(np.percentile(listOfCategoryAAndBCount,95))
print "listOfCategoryAAndBCount 96: " + str(np.percentile(listOfCategoryAAndBCount,96))
print "listOfCategoryAAndBCount 97: " + str(np.percentile(listOfCategoryAAndBCount,97))
print "listOfCategoryAAndBCount 98: " + str(np.percentile(listOfCategoryAAndBCount,98))
print "listOfCategoryAAndBCount 99: " + str(np.percentile(listOfCategoryAAndBCount,99))
print "listOfCategoryAAndBCount 100: " + str(np.percentile(listOfFrequencies,100))
print "--"
print "listOfCategoryACount 10: " + str(np.percentile(listOfCategoryACount,10))
print "listOfCategoryACount 25: " + str(np.percentile(listOfCategoryACount,25))
print "listOfCategoryACount 50: " + str(np.percentile(listOfCategoryACount,50))
print "listOfCategoryACount 75: " + str(np.percentile(listOfCategoryACount,75))
print "listOfCategoryACount 80: " + str(np.percentile(listOfCategoryACount,80))
print "listOfCategoryACount 85: " + str(np.percentile(listOfCategoryACount,85))
print "listOfCategoryACount 90: " + str(np.percentile(listOfCategoryACount,90))
print "listOfCategoryACount 95: " + str(np.percentile(listOfCategoryACount,95))
print "listOfCategoryACount 100: " + str(np.percentile(listOfCategoryACount,100))
print "--"
print "listOfCategoryBCount 10: " + str(np.percentile(listOfCategoryBCount,10))
print "listOfCategoryBCount 25: " + str(np.percentile(listOfCategoryBCount,25))
print "listOfCategoryBCount 50: " + str(np.percentile(listOfCategoryBCount,50))
print "listOfCategoryBCount 75: " + str(np.percentile(listOfCategoryBCount,75))
print "listOfCategoryBCount 80: " + str(np.percentile(listOfCategoryBCount,80))
print "listOfCategoryBCount 85: " + str(np.percentile(listOfCategoryBCount,85))
print "listOfCategoryBCount 90: " + str(np.percentile(listOfCategoryBCount,90))
print "listOfCategoryBCount 95: " + str(np.percentile(listOfCategoryBCount,95))
print "listOfCategoryBCount 100: " + str(np.percentile(listOfCategoryBCount,100))
print "--"
"""
