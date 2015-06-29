from flask import Flask
from flask import render_template, request, jsonify
from importDataFromDatabase import getCategories, getBestBusinessesOpportunities
import psycopg2
import time

conn_string = "host='localhost' dbname='mydb' user='postgres' password='YourPassword'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

app = Flask(__name__)

@app.route('/_recommend_distance')
def recommend_distance():
    if request.args.get('keywords'):
        print request.args.get('keywords')
        listOfKeywords = request.args.get('keywords').split("-----")
        print listOfKeywords

        cursor.execute("SELECT SUM(matchingcategorymediandistance*matchingcategoryfrequency)/SUM(matchingcategoryfrequency) FROM matchingcategories WHERE initialcategory = ANY(%s)", (listOfKeywords,))
        (distanceRecommended,) = cursor.fetchone()
    else:
        distanceRecommended = ''

    return jsonify(result=distanceRecommended)


@app.route('/', methods=['GET'])
def welcome():
    print "welcome"
    return render_template('welcomePage.html', categories = getCategories(conn, cursor))

#@TODO: we can recommend the distance as the average with the weights (frequency) of the matchingCategories from the initialBusinesses provided by the user
@app.route('/results', methods=['POST'])
def results():
    t0 = time.time()

    cursor.execute("SELECT initialcategory, matchingcategoryname, matchingcategorymediandistance, matchingcategoryfrequency  FROM matchingcategories", )
    fullListOfMatchingCategories = cursor.fetchall()

    listOfCategoriesInOurMatchingCategoriesDataset = getCategories(conn, cursor)
    listOfCategoriesImproved = []
    f = request.form
    for category in listOfCategoriesInOurMatchingCategoriesDataset:
        for value in f.getlist('keywords'):
            if category[0] == value:
                category = category + (True,)
        listOfCategoriesImproved.append(category)
    distance = f['distance']
    numberOfOpportunitiesFromUser = f['numberOfOpportunities']
    print "--"
    print distance
    print numberOfOpportunitiesFromUser

    if (len(f.getlist('keywords')) > 0 and distance > 0 and numberOfOpportunitiesFromUser > 0):
        businessOpportunities = getBestBusinessesOpportunities(conn, cursor, f.getlist('keywords'), distance, numberOfOpportunitiesFromUser)
        t1 = time.time()
        t = round((t1 - t0),3)
        return render_template('welcomePage.html', categories = listOfCategoriesImproved,
                               businessOpportunities = businessOpportunities[0],
                               matchingCategories = businessOpportunities[1],
                               numberOfOpportunities = businessOpportunities[2],
                               loadingTime = t,
                               distance = distance,
                               fullListOfMatchingCategories = fullListOfMatchingCategories,
                               uniqueListOfMatchingCategories = businessOpportunities[3]
                               )
    else:
        return render_template('welcomePage.html', categories = getCategories(conn, cursor))



if __name__ == "__main__":
    app.run(debug=True)
