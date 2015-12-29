"""
Functions to get the data from the database for the Flask web applications
"""
from geopy.distance import great_circle
import time
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from collections import namedtuple
from uuid import uuid1
import operator
import string
import collections

PointTuple = namedtuple("PointTuple", ["latitude", "longitude"])

"""
Compute the distance using the latitude/longitude of two points with 3 digits of precision
"""
def computeDistanceFromLatitudeLongitude(lon1, lat1, lon2, lat2):
    return round(great_circle((lon1,lat1), (lon2,lat2)).meters, 3)


def getCategories(conn, cursor, state):
    cursor.execute("SELECT DISTINCT c.name,c.numberofbusinesses FROM categories c, matchingcategories" + state + " m WHERE c.name = m.initialcategory;")
    listOfCategoriesWithNumberOfBusinesses = cursor.fetchall()
    return listOfCategoriesWithNumberOfBusinesses


def generateClustersForTheseDataFromThisDistance(listOfBusinesses, distanceCluster, category, dictionnaryOfPoints):
    listOfClusters = []

    coordinates = pd.DataFrame(listOfBusinesses).as_matrix(columns=[1,2]) #1: latitude; #2: longitude
    myEps = float(distanceCluster) / 1000 / 110.574 # convert the distance in meters to the distance that is used in by DBSCAN (in degrees)
    db = DBSCAN(eps=myEps, min_samples=2).fit(coordinates)


    colored = []
    black = []
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    distance = round(great_circle((0,0), (0,myEps)).meters, 3)
    ratio = str((float(len(db.components_))/float(len(coordinates))*100))
    """
    print('Distance used: ' + str(distance) + ' meters')

    print('Number of clusters: %d' % n_clusters_)
    print('Number of businesses: %d' % len(listOfBusinesses))
    print('Number of businesses in clusters: %d' % len(db.components_))
    print 'Ratio of businesses / businesses in clusters: ' +  ratio + " %"

    """
    ##############################################################################
    # Plot result

    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    for k in unique_labels:

        idOfThisCluster = uuid1()
        class_member_mask = (labels == k)

        xy = coordinates[class_member_mask & core_samples_mask]

        for point in xy:
            pointTuple = PointTuple(latitude = point[0], longitude = point[1])
            dictionnaryOfPoints[pointTuple] = { "categoryName": category,
                                               "id": idOfThisCluster }



        listOfClusters.append(xy)

    return [listOfClusters, dictionnaryOfPoints]

def generateClustersOfClustersForTheseDataFromThisDistance(listOfBusinesses, distanceCluster):
    dictOfClusters = {}

    coordinates = pd.DataFrame(listOfBusinesses).as_matrix(columns=[1,2]) #1: latitude; #2: longitude
    myEps = float(distanceCluster) / 1000 / 110.574 # convert the distance in meters to the distance that is used in by DBSCAN (in degrees)
    db = DBSCAN(eps=myEps, min_samples=2).fit(coordinates)


    colored = []
    black = []
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    distance = round(great_circle((0,0), (0,myEps)).meters, 3)
    ratio = str((float(len(db.components_))/float(len(coordinates))*100))
    """
    print('Distance used: ' + str(distance) + ' meters')

    print('Number of clusters: %d' % n_clusters_)
    print('Number of businesses: %d' % len(listOfBusinesses))
    print('Number of businesses in clusters: %d' % len(db.components_))
    print 'Ratio of businesses / businesses in clusters: ' +  ratio + " %"

    """
    ##############################################################################
    # Plot result

    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    for k in unique_labels:
        dictionnaryOfClusters = {}

        class_member_mask = (labels == k)

        xy = coordinates[class_member_mask & core_samples_mask]

        clusterID = uuid1()
        dictOfClusters[clusterID] = xy



    return dictOfClusters

"""
1. import the matchin categories corresponding to the variable categories
2. Create the clusters of categories with the distance "distanceCluster"
3. Create the clusters of clusters of categories with the distance "distanceCluster"
4. For each cluster of clusters, compute the ratio which is the sum of the size of the clusters of matching categories divided by the sum of the size of the clusters of the initial categories (= the keywords)
5. Take the numberOfOpportunities best ratios and return these clusters as the best opportunities
"""
def getBestBusinessesOpportunities(conn, cursor, categories, distanceCluster, numberOfOpportunities, state):
    t0 = time.time()


    cursor.execute("SELECT matchingcategoryname, matchingcategorymediandistance, matchingcategoryfrequency, initialcategory FROM matchingcategories" + state +  "  WHERE initialcategory != matchingcategoryname AND initialcategory = ANY(%s);", (categories,))
    matchingCategoryResults = cursor.fetchall()

    matchingCategoriesName = np.array(matchingCategoryResults)[:,0]
    counterOfMatchingCategoriesName = collections.Counter(matchingCategoriesName)

    counterOfMatchingCategoriesNameWithoutInitialCategories =  dict(counterOfMatchingCategoriesName)
    for category in categories:
        if counterOfMatchingCategoriesNameWithoutInitialCategories.has_key(category):
            del counterOfMatchingCategoriesNameWithoutInitialCategories[category]



    uniqueListOfMatchingCategories = set(np.array(matchingCategoryResults)[:,[0]].flat)
    uniqueListOfMatchingCategories = uniqueListOfMatchingCategories - set(categories).intersection(uniqueListOfMatchingCategories)

    listOfCategories = list(categories)
    listOfCategories.extend(matchingCategoriesName)
    listOfCategories = list(set(listOfCategories))

    dictionnaryOfBusinessesPerCategory = {}
    dictionnaryOfClustersPerCategory = {}
    for category in listOfCategories:
        dictionnaryOfBusinessesPerCategory[category] = []
        dictionnaryOfClustersPerCategory[category] = []

    cursor.execute("SELECT business_id, latitude, longitude, name, categories, stars, review_count FROM businesses" + state + " WHERE categories && ARRAY[%s] ", (listOfCategories,))
    listOfBusinesses = cursor.fetchall()

    dictionnaryOfOffsets = {} # This is use to offset a little the businesses that are in the exact same position. Otherwise they will not be shown on Google Map.
    dictionnaryOfBusinessesWithPointAsKey = {}
    for business in listOfBusinesses:
        pointTuple = PointTuple(latitude = business[1], longitude = business[2])
        newBusiness = {"business_id": business[0],
                       "latitude": business[1],
                       "longitude": business[2],
                       "name": filter(lambda x: x in string.printable, business[3]),
                       "categories": business[4],
                       "stars": business[5],
                       "review_count": business[6]
                       }
        if dictionnaryOfBusinessesWithPointAsKey.has_key(pointTuple):
            dictionnaryOfOffsets[pointTuple] += 0.00005
            newBusiness = {"business_id": business[0],
                       "latitude": (business[1])+ dictionnaryOfOffsets[pointTuple],
                       "longitude": business[2] + dictionnaryOfOffsets[pointTuple],
                       "name": filter(lambda x: x in string.printable, business[3]),
                       "categories": business[4],
                       "stars": business[5],
                       "review_count": business[6]
                       }
            dictionnaryOfBusinessesWithPointAsKey[pointTuple].append(newBusiness)
        else:
            dictionnaryOfBusinessesWithPointAsKey[pointTuple] = [newBusiness]
            dictionnaryOfOffsets[pointTuple] = 0


    for business in listOfBusinesses:
        listOfIntersection = list(set(listOfCategories).intersection(business[4]))
        for category in listOfIntersection:
            dictionnaryOfBusinessesPerCategory[category].append(business)


    dictOfClustersOfCluster = generateClustersOfClustersForTheseDataFromThisDistance(listOfBusinesses, distanceCluster)



    dictOfRatios = {}

    for clusterID in dictOfClustersOfCluster:
        goodForOpportunity = 0
        badForOpportunity = 0
        listOfBusinessForThisClusterID = []

        businessListOfThisCluster = []
        for point in dictOfClustersOfCluster[clusterID]:
            pointTuple = PointTuple(latitude = point[0], longitude = point[1])
            businessListOfThisCluster.extend(dictionnaryOfBusinessesWithPointAsKey[pointTuple])
        for business in businessListOfThisCluster:
            if bool(set(business["categories"]) & set(categories)):
                icon = 'static/img/warning.png'
                business["competitor"] = True
                numberOfCategoriesInCommon = len(set(business["categories"]).intersection(set(categories)))
                scoreOfThisBusiness =  numberOfCategoriesInCommon*(np.log(business["stars"]) + 0.1)*np.log(business["review_count"])
                if scoreOfThisBusiness < 1:
                    badForOpportunity += 1
                else:
                    badForOpportunity += scoreOfThisBusiness

            else:
                """
                strenghOfComplementorCategories represents how strong are these categories as a complementors.
                It depends of the number of times the category is a complementor of the initial categories.
                E.g.
                the initial categories of the user are: ['Restaurants', 'Italian']
                The complementors of ['Restaurants', 'Italian'] are ['Bars', 'Shopping', 'American (Traditional)', 'Chinese', 'Food', 'Nightlife', 'Burgers', 'Sandwiches', 'Fast Food', 'Mexican', 'Pizza', 'Italian', 'Pizza', 'Food', 'Fast Food', 'Shopping', 'Restaurants']
                Therefore, we can represent these complementors in the following dictionnary ('nameOfTheCategoryComplementor': numberOfTimesItIsInThisPreviousList)
                {'Shopping': 2, 'Food': 2, 'Fast Food': 2, 'Pizza': 2, 'Bars': 1, 'Chinese': 1, 'Burgers': 1, 'American (Traditional)': 1, 'Italian': 1, 'Restaurants': 1, 'Nightlife': 1, 'Mexican': 1, 'Sandwiches': 1}

                So now, if we have a business complementor which has the following categories: ['Food', 'Italian', 'Restaurants'].
                The value of strenghOfComplementorCategories is  2+1+1 = 4
                """
                strenghOfComplementorCategories = 0
                for category in business["categories"]:
                    if counterOfMatchingCategoriesName.has_key(category):
                        strenghOfComplementorCategories += counterOfMatchingCategoriesName[category]
                icon = 'static/img/star.png'
                business["competitor"] = False

                scoreOfThisBusiness = strenghOfComplementorCategories*(np.log(business["stars"]) + 0.1)*np.log(business["review_count"])
                if scoreOfThisBusiness < 1:
                    goodForOpportunity += 1
                else:
                    goodForOpportunity += scoreOfThisBusiness


            business["icon"] = icon
            listOfBusinessForThisClusterID.append(business)
        dictOfClustersOfCluster[clusterID] = listOfBusinessForThisClusterID
        if badForOpportunity != 0:
            ratio = float(goodForOpportunity) / float(badForOpportunity)
        else:
            ratio = goodForOpportunity
        dictOfRatios[clusterID] = ratio

    #listOfRatiosSorted = sorted(listOfRatios.items(), key=operator.itemgetter(1)).reverse()
    if len(dictOfRatios) < int(numberOfOpportunities):
        numberOfOpportunities = len(dictOfRatios)
    topDict = dict(sorted(dictOfRatios.iteritems(), key=operator.itemgetter(1), reverse=True)[:int(numberOfOpportunities)])

    topList = sorted(dictOfRatios.iteritems(), key=operator.itemgetter(1), reverse=True)[:int(numberOfOpportunities)]
    dictOfOpportunities = {}
    listOfOpportunities = [] # list Of opportunities contains the ratio and is ranked by ratio. It's used to show the top areas.


    topDictSet = set(topDict)
    dictOfClustersOfClusterSet = set(dictOfClustersOfCluster)

    for clustersID in topDictSet.intersection(dictOfClustersOfClusterSet):
        if dictOfRatios[clustersID] > 0: #We don't want to show the bad opportunities (more badForOpportunity than goodForOpportunity
            dictOfOpportunities[clustersID] = dictOfClustersOfCluster[clustersID]


    t2 = time.time()

    for clusterID in dictOfOpportunities:
        dictOfBusinessesForThisCluster = {}
        for business in dictOfOpportunities[clusterID]:
            dictOfBusinessesForThisCluster[business["business_id"]] = {
                "categories": (', ').join(business["categories"]),
                "name": business["name"],
                "latitude": business["latitude"],
                "longitude": business["longitude"],
                "icon": business["icon"],
                "review_count": int(business["review_count"]),
                "stars": business["stars"],
                "competitor": business["competitor"]
            }
        dictOfOpportunities[clusterID] = dictOfBusinessesForThisCluster

    for tupleClusterIDAndRatio in topList:
        clusterID = tupleClusterIDAndRatio[0]
        ratio = tupleClusterIDAndRatio[1]
        dictOfBusinessesForThisCluster = {"cluster": dictOfOpportunities[clusterID], "ratio": ratio}
        listOfOpportunities.append(dictOfBusinessesForThisCluster)

    t3 = time.time()
    print str(float(t3 - t2)) + " seconds"
    print "---"


    t1 = time.time()
    print str(float(t1 - t0)) + " seconds"
    print "---"


    return [dictOfOpportunities, matchingCategoryResults, numberOfOpportunities, uniqueListOfMatchingCategories, counterOfMatchingCategoriesNameWithoutInitialCategories, listOfOpportunities]
