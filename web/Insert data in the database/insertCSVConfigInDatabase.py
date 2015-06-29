"""
Read the csv config file and insert the data in the database
"""
import psycopg2
import simplejson as json
import sys
import csv

datasetPath = '../dataset/yelp_academic_dataset_business.json'

conn_string = "host='localhost' dbname='mydb' user='postgres' password='YourPassword'"
tableBusinessesName = ''

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

def insertBusinesses(conn, cursor):
    j = 0
    with open(datasetPath) as fin:
        for line in fin:
            line_contents = json.loads(line)
            state = line_contents["state"]
            if state == "AZ":
                j += 1
                print j
                categories = line_contents["categories"]
                business_id = line_contents['business_id']
                latitude = line_contents['latitude']
                longitude = line_contents['longitude']
                stars = line_contents['stars']
                review_count = line_contents['review_count']
                name = line_contents['name']

                #die()

                cursor.execute("INSERT INTO businesses (business_id, categories, latitude, longitude,stars, review_count, name) VALUES (%s, %s, %s, %s, %s, %s, %s)",
              (business_id,categories, latitude,longitude,stars, review_count, name,))

                #cursor.execute("INSERT INTO businesses (business_id, categories, latitude, longitude, stars, review_count, name) VALUES (%s, %f, %f, %f, %f, %f, %s)",
                #(business_id, latitude, longitude, stars, review_count, name,))



    conn.commit()

def insertCategories():
    dictOfCategories = {}
    i = 0
    with open(datasetPath) as fin:
        for line in fin:
            i += 1
            line_contents = json.loads(line)
            categories = line_contents["categories"]
            for category in categories:
                if category not in dictOfCategories:
                    dictOfCategories[category] = 1
                else:
                    dictOfCategories[category] += 1

    for category in dictOfCategories:
        cursor.execute("INSERT INTO categories (name, numberofbusinesses) VALUES (%s, %s)",
    (category, dictOfCategories[category]))

    conn.commit()


def insertMatchingCategories():
    csvMatchingCategoriesInputFileName = "../filters/filter-90-10-10-10.csv"
    dictOfCategories = {}

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

    print "import done"
    for initialCategory in dictOfCategories:
        for matchingCategory in dictOfCategories[initialCategory]:
            print dictOfCategories[initialCategory][matchingCategory]
            frequency = dictOfCategories[initialCategory][matchingCategory]["frequency"]
            medianDistance = dictOfCategories[initialCategory][matchingCategory]["medianDistance"]
            categoryAAndBCount = dictOfCategories[initialCategory][matchingCategory]["categoryAAndBCount"]
            categoryACount = dictOfCategories[initialCategory][matchingCategory]["categoryACount"]
            categoryBCount = dictOfCategories[initialCategory][matchingCategory]["categoryBCount"]
            print initialCategory, frequency, medianDistance, categoryAAndBCount, categoryACount, categoryBCount

            cursor.execute("INSERT INTO matchingcategories (initialcategory, matchingcategoryname, matchingcategoryfrequency, "
                           "matchingcategorymediandistance, initialcategoryandmatchingcategorycount, initialcategorycount,"
                           "matchingcategorycount) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (initialCategory, matchingCategory, frequency, medianDistance, categoryAAndBCount, categoryACount, categoryBCount))
    print "commit"
    conn.commit()
