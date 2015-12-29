"""
Read the csv config file and insert the data in the database
"""
import psycopg2
import simplejson as json
import csv

datasetPath = '../../find relationships/dataset/yelp_academic_dataset_business.json'

conn_string = "host='localhost' dbname='dbname' user='user' password='password'"
tableBusinessesName = ''

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

def createBusinessesTable(state):
    query = ("CREATE TABLE businesses" + state + " "
        "( "
          "business_id text, "
          "id serial NOT NULL, "
          "categories text[], "
          "latitude real, "
          "longitude real, "
          "stars real, "
          "review_count real, "
          "name text, "
          "CONSTRAINT businesses" + state + "_pkey PRIMARY KEY (id), "
          "CONSTRAINT businesses" + state + "_business_id_key UNIQUE (business_id) "
        ") "
        "WITH ( "
          "OIDS=FALSE "
        "); "
        "ALTER TABLE businesses" + state + " "
          "OWNER TO postgres; ")

    cursor.execute(query)
    conn.commit()

def createMatchingCategoriesTable(state):
    query = ("CREATE TABLE matchingcategories" + state + " "
        "("
          "id serial NOT NULL, "
          "initialcategory text, "
          "matchingcategoryname text, "
          "matchingcategoryfrequency integer, "
          "matchingcategorymediandistance real, "
          "initialcategoryandmatchingcategorycount integer, "
          "initialcategorycount integer, "
          "matchingcategorycount integer, "
          "CONSTRAINT matchingcategories" + state + "_pkey PRIMARY KEY (id) "
        ") "
        "WITH ( "
          "OIDS=FALSE "
        "); "
        "ALTER TABLE matchingcategories" + state + " "
          "OWNER TO postgres; ")

    cursor.execute(query)

    conn.commit()

def insertBusinesses(state):
    j = 0
    with open(datasetPath) as fin:
        for line in fin:
            line_contents = json.loads(line)
            stateBusiness = line_contents["state"]
            if stateBusiness == state:
                j += 1
                print j
                categories = line_contents["categories"]
                business_id = line_contents['business_id']
                latitude = line_contents['latitude']
                longitude = line_contents['longitude']
                stars = line_contents['stars']
                review_count = line_contents['review_count']
                name = line_contents['name']


                cursor.execute("INSERT INTO businesses" + state + " (business_id, categories, latitude, longitude,stars, review_count, name) VALUES (%s, %s, %s, %s, %s, %s, %s)",
              (business_id,categories, latitude,longitude,stars, review_count, name,))


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


def insertMatchingCategories(state):
    csvMatchingCategoriesInputFileName = "../../find relationships/resultsFound/filters/filter-" + state + ".csv"
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

            cursor.execute("INSERT INTO matchingcategories" + state + " (initialcategory, matchingcategoryname, matchingcategoryfrequency, "
                           "matchingcategorymediandistance, initialcategoryandmatchingcategorycount, initialcategorycount,"
                           "matchingcategorycount) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (initialCategory, matchingCategory, frequency, medianDistance, categoryAAndBCount, categoryACount, categoryBCount))
    print "commit"
    conn.commit()
