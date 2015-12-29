"""
Find the categories used in the Yelp dataset and write them in a csv file
"""
import simplejson as json

listOfCategories = []
state = "NV"


datasetPath = '../dataset/yelp_academic_dataset_business.json'
csvOutputFileName = '../resultsFound/yahooCrawler/categories' + state + '.csv'

with open(datasetPath) as fin:
    for line in fin:
        line_contents = json.loads(line)
        if line_contents['state'] == state:
            categories = line_contents["categories"]
            for category in categories:
                categoryReplaced = category.replace("'", r"\'")  # escape the quotes by a \
                if categoryReplaced not in listOfCategories:
                    listOfCategories.append(categoryReplaced)

listOfCategories.sort()


f = open(csvOutputFileName, 'w')
for category in listOfCategories:
    f.write("'" + category + "'" + "\n")
