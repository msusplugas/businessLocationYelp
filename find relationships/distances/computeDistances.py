"""
We use a grid here to compute faster the distances, indeed we need only the shortest distance, therefore it's useless
to compute the distance between two business that are really far away because in this case they will not be the shortest
distance of the two categories
"""
from geopy.distance import great_circle
import numpy

"""
Insert the businesses in a grid of a size lengthOfTheGrid x lengthOfTheGrid
"""
lengthOfTheGrid = 100

"""
Insert all the businesses of dictOfBusinesses into a grid of length: lengthOfTheGrid
Then we return this grid
"""
def insertBusinessesInGrid(dictOfBusinesses, minLatitude, maxLatitude, minLongitude, maxLongitude):

    #We want a scale from 0 to n
    maxPositiveLatitude = maxLatitude - minLatitude
    maxPositiveLongitude = maxLongitude - minLongitude

    sizeOfACellLatitude = float(maxPositiveLatitude)/float(lengthOfTheGrid-1)
    sizeOfACellLongitude = float(maxPositiveLongitude)/float(lengthOfTheGrid-1)

    #We create a grid  full of empty list
    #grid[Latitude][Longitude]
    grid = [[ [] for x in range(lengthOfTheGrid)] for y in range(lengthOfTheGrid)]


    for businessId in dictOfBusinesses: #We insert the datas in the grid
        latitude = dictOfBusinesses[businessId]['latitude']
        longitude = dictOfBusinesses[businessId]['longitude']

        relativeLatitude = latitude - minLatitude
        relativeLongitude = longitude - minLongitude

        #We remove 1 because the lists start at 0
        latitudeCellNumber = int(round(relativeLatitude/(sizeOfACellLatitude)))
        longitudeCellNumber = int(round(relativeLongitude/(sizeOfACellLongitude)))

        grid[latitudeCellNumber][longitudeCellNumber].append(dictOfBusinesses[businessId])

    return grid

"""
Given a grid and two categories it will compute the median distance between the categories.
For each cell of the grid we compute the median distance between every business of categoryA to another business
 of categoryB
"""
def computeMedianDistanceForGrid(categoryA, categoryB, grid):
    latitudeIndexList = range(len(grid))
    longitudeIndexList = range(len(grid))
    listOfMedianDistance = []
    for latitudeIndex in latitudeIndexList:
        for longitudeIndex in longitudeIndexList:
            for business in grid[latitudeIndex][longitudeIndex]:
                if categoryA in business['categories']:
                    medianDistance = computeMedianDistanceForThisBusiness(business, categoryB, grid, latitudeIndex, longitudeIndex)
                    if medianDistance:
                        listOfMedianDistance.append(medianDistance)

    return median(listOfMedianDistance)

"""
Find the shortest distance between the business and any other business of categoryB
"""
def computeMedianDistanceForThisBusiness(business, categoryB, grid, latitude, longitude):
    minDistance = None

    """
    We want to compute the distance between our business and all the businesses that are in the same cell of the grid or
    in a close cell. Latitude + or -1 and longitude + or -1
    """
    lenGrid = len(grid) - 1
    listOfBusinessesInGrid = []

    listOfBusinessesInGrid.extend(grid[latitude][longitude])

    if longitude > 0:
        listOfBusinessesInGrid.extend(grid[latitude][longitude-1])
    if longitude < lenGrid:
        listOfBusinessesInGrid.extend(grid[latitude][longitude+1])
    if latitude > 0 and longitude > 0:
        listOfBusinessesInGrid.extend(grid[latitude-1][longitude-1])
    if latitude > 0:
        listOfBusinessesInGrid.extend(grid[latitude-1][longitude])
    if latitude > 0 and longitude < lenGrid:
        listOfBusinessesInGrid.extend(grid[latitude-1][longitude+1])
    if latitude < lenGrid and longitude > 0:
        listOfBusinessesInGrid.extend(grid[latitude+1][longitude-1])
    if latitude < lenGrid:
        listOfBusinessesInGrid.extend(grid[latitude+1][longitude])
    if latitude < lenGrid and longitude < lenGrid:
        listOfBusinessesInGrid.extend(grid[latitude+1][longitude+1])

    for businessOfGrid in grid[latitude][longitude]:
        if businessOfGrid != business and categoryB in businessOfGrid['categories']:
            distance = computeDistanceFromLatitudeLongitude(businessOfGrid['longitude'], businessOfGrid['latitude'],
                                                    business['longitude'], business['latitude'])
            if  distance < minDistance or minDistance == None:
                minDistance = distance

    return minDistance


"""
Compute the distance using the latitude/longitude of two points with 3 digits of precision
"""
def computeDistanceFromLatitudeLongitude(lon1, lat1, lon2, lat2):
    return round(great_circle((lon1,lat1), (lon2,lat2)).meters, 3)


"""
Compute the median of a list
"""
def median(list):
    if list:
        return numpy.median(numpy.array(list))
    else:
        return None
