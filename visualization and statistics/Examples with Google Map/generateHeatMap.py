"""
Import the datas from the json dataset file and return the big array that contains it
"""
import simplejson as json
datasetPath = '../../find\ relationships/dataset/yelp_academic_dataset_business.json'

heatMapData= open("heatMapData.html", "w")

with open(datasetPath) as fin:
    for business in fin:
        line_contents = json.loads(business)
        if line_contents["state"] == "AZ":
            latitude = str(line_contents['latitude'])
            longitude = str(line_contents['longitude'])
            data = 'new google.maps.LatLng(' + latitude + ', ' + longitude + '), \n'
            heatMapData.write(data)

heatMapData.close()