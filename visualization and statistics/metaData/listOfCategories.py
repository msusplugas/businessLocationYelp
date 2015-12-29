
import simplejson as json

maxCat = 0
dictOfCategories = {}

datasetPath = '../../find relationships/dataset/yelp_academic_dataset_business.json'
i = 0
with open(datasetPath) as fin:
    for line in fin:
        line_contents = json.loads(line)
        if line_contents['state'] == "NV":
            i += 1

            categories = line_contents["categories"]
            for category in categories:
                if category not in dictOfCategories:
                    dictOfCategories[category] = 1
                else:
                    dictOfCategories[category] += 1


print "Categories:"
for key, value in sorted(dictOfCategories.items()): # Note the () after items!
    print(key, value)

print len(dictOfCategories)
print "Number of businesses: "  + str(i)
#print "list of categories:" + str(listOfCategories)