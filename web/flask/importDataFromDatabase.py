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

PointTuple = namedtuple("PointTuple", ["latitude", "longitude"])

"""
Compute the distance using the latitude/longitude of two points with 3 digits of precision
"""
def computeDistanceFromLatitudeLongitude(lon1, lat1, lon2, lat2):
    return round(great_circle((lon1,lat1), (lon2,lat2)).meters, 3)


def getCategories(conn, cursor):
    cursor.execute("SELECT DISTINCT c.name,c.numberofbusinesses FROM categories c, matchingcategories m WHERE c.name = m.initialcategory;")
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

        """
        for point in xy:
            print point
            print "--"
            print xy
            pointTuple = PointTuple(latitude = point[0], longitude = point[1])
            if dictionnaryOfPoints.has_key(pointTuple):
                categoryName = dictionnaryOfPoints[pointTuple]["categoryName"]
                #print categoryName
                id = dictionnaryOfPoints[pointTuple]["id"]
                if not dictionnaryOfClusters.has_key(categoryName):
                    dictionnaryOfClusters[categoryName] = {}
                if dictionnaryOfClusters[categoryName].has_key(id):
                    dictionnaryOfClusters[categoryName][id].append(point)
                else:
                    dictionnaryOfClusters[categoryName][id] = [point]
                print dictionnaryOfClusters[categoryName][id]
                die
        clustersID = uuid1()
        """
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
def getBestBusinessesOpportunities(conn, cursor, categories, distanceCluster, numberOfOpportunities):
    t0 = time.time()


    cursor.execute("SELECT matchingcategoryname, matchingcategorymediandistance, matchingcategoryfrequency, initialcategory FROM matchingcategories WHERE initialcategory = ANY(%s);", (categories,))
    matchingCategoryResults = cursor.fetchall()

    matchingCategoriesName = np.array(matchingCategoryResults)[:,0]


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

    cursor.execute("SELECT business_id, latitude, longitude, name, categories, stars, review_count FROM businesses WHERE categories && ARRAY[%s] ", (listOfCategories,))
    listOfBusinesses = cursor.fetchall()

    dictionnaryOfBusinessesWithPointAsKey = {  PointTuple(latitude = x[1], longitude = x[2]):
                                                   {"business_id": x[0],
                                                    "name": filter(lambda x: x in string.printable, x[3]),
                                                    "categories": x[4],
                                                    "stars": x[5],
                                                    "review_count": x[6]
                                                    } for x in listOfBusinesses}


    for business in listOfBusinesses:
        listOfIntersection = list(set(listOfCategories).intersection(business[4]))
        for category in listOfIntersection:
            dictionnaryOfBusinessesPerCategory[category].append(business)

    """
    dictionnaryOfPoints = {}

    for category in listOfCategories:
        listOfBusinessesOfThisCategory = dictionnaryOfBusinessesPerCategory[category]
        print "generate cluster"
        cluster = generateClustersForTheseDataFromThisDistance(listOfBusinessesOfThisCategory, distanceCluster, category, dictionnaryOfPoints)
        dictionnaryOfClustersPerCategory[category] = cluster[0]
        dictionnaryOfPoints = cluster[1]
    """

    dictOfClustersOfCluster = generateClustersOfClustersForTheseDataFromThisDistance(listOfBusinesses, distanceCluster)



    dictOfRatios = {}

    for clusterID in dictOfClustersOfCluster:
        goodForOpportunity = 0
        badForOpportunity = 0
        newDictForThisClusterID = {}
        for point in dictOfClustersOfCluster[clusterID]:
            pointTuple = PointTuple(latitude = point[0], longitude = point[1])
            business = dictionnaryOfBusinessesWithPointAsKey[pointTuple]
            if bool(set(business["categories"]) & set(categories)):
                icon = 'static/img/warning.png'
                badForOpportunity += (np.log(business["stars"]) + 0.1)*np.log(business["review_count"])
            else:
                icon = 'static/img/star.png'
                goodForOpportunity += (np.log(business["stars"]) + 0.1)*np.log(business["review_count"])
            business["icon"] = icon
            newDictForThisClusterID[pointTuple] = business
        dictOfClustersOfCluster[clusterID] = newDictForThisClusterID
        if badForOpportunity != 0:
            ratio = float(goodForOpportunity) / float(badForOpportunity)
        else:
            ratio = goodForOpportunity

        dictOfRatios[clusterID] = ratio
        print ratio, goodForOpportunity, badForOpportunity, len(dictOfClustersOfCluster[clusterID])

    #listOfRatiosSorted = sorted(listOfRatios.items(), key=operator.itemgetter(1)).reverse()
    if len(dictOfRatios) < int(numberOfOpportunities):
        numberOfOpportunities = len(dictOfRatios)
    topDict = dict(sorted(dictOfRatios.iteritems(), key=operator.itemgetter(1), reverse=True)[:int(numberOfOpportunities)])

    dictOfOpportunities = {}

    topDictSet = set(topDict)
    dictOfClustersOfClusterSet = set(dictOfClustersOfCluster)

    for clustersID in topDictSet.intersection(dictOfClustersOfClusterSet):
        if dictOfRatios[clustersID] > 0: #We don't want to show the bad opportunities (more badForOpportunity than goodForOpportunity
            dictOfOpportunities[clustersID] = dictOfClustersOfCluster[clustersID]

    print len(dictOfOpportunities)
    t2 = time.time()

    print "--------"
    for clusterID in dictOfOpportunities:
        dictOfBusinessesForThisCluster = {}
        for point in dictOfOpportunities[clusterID]:
            business =  dictOfOpportunities[clusterID][point]
            """
            pointLatitude = point[0]
            pointLongitude = point[1]
            business = listOfBusinesses[[(x[1],x[2]) for x in listOfBusinesses].index((pointLatitude, pointLongitude))]
            businessID = business[0]
            businessName =  filter(lambda x: x in string.printable, business[3])
            businessCategories = business[4]
            if bool(set(businessCategories) & set(categories)) : #If they share a category in common then it will not be an opportunity but a warning
                icon = 'static/img/warning.png'
            else:
                icon = 'static/img/star.png'
            """
            dictOfBusinessesForThisCluster[business["business_id"]] = {
                "categories": (', ').join(business["categories"]),
                "name": business["name"],
                "latitude": point[0],
                "longitude": point[1],
                "icon": business["icon"],
                "review_count": int(business["review_count"]),
                "stars": business["stars"]
            }
        dictOfOpportunities[clusterID] = dictOfBusinessesForThisCluster

    t3 = time.time()
    print t3 - t2
    print "---"


    t1 = time.time()
    print t1 - t0


    return [dictOfOpportunities, matchingCategoryResults, numberOfOpportunities, uniqueListOfMatchingCategories]
