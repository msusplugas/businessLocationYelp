"""
Import the datas from the json dataset file and return the big array that contains it
"""
import simplejson as json
import unicodedata

def strip_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    only_ascii = only_ascii.replace(',', ' ')
    only_ascii = only_ascii.replace("'", " ")
    return only_ascii

datasetPath = '../../find\ relationships/dataset/yelp_academic_dataset_business.json'

heatMapData= open("markerMapData.html", "w")

i = 1
with open(datasetPath) as fin:
    for business in fin:
        line_contents = json.loads(business)
        if line_contents["state"] == "AZ":
            if line_contents["city"] == "Tucson":
                print str(line_contents)
            name = line_contents['name']
            safeName = '<strong>' + strip_accents(unicode(name)) + '</strong>'
            categories = '-'.join(line_contents['categories'])
            safeCategories = strip_accents(unicode(categories))
            #print categories
            latitude = str(line_contents['latitude'])
            longitude = str(line_contents['longitude'])

            data = "['"+ safeName +": "+ safeCategories +"', "+latitude+", "+ longitude +", "+ str(i) +"], \n"
            #print data
            heatMapData.write(data)

            i += 1

heatMapData.close()
