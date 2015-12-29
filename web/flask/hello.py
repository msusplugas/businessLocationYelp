from flask import Flask
from flask import render_template, request, jsonify
from importDataFromDatabase import getCategories, getBestBusinessesOpportunities
import psycopg2
import time

listOfCities = ["Phoenix", "Las Vegas"]
dictState = {"Phoenix": "AZ", "Las Vegas": "NV"}

conn_string = "host='localhost' dbname='dbname' user='user' password='password'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

app = Flask(__name__)

@app.route('/_recommend_distance')
def recommend_distance():
    if request.args.get('keywords') and request.args.get('city'):
        print request.args.get('keywords')
        listOfKeywords = request.args.get('keywords').split("-----")
        print listOfKeywords
        state = dictState[request.args.get('city')]

        cursor.execute("SELECT SUM(matchingcategorymediandistance*matchingcategoryfrequency)/SUM(matchingcategoryfrequency) FROM matchingcategories" + state + " WHERE initialcategory = ANY(%s)", (listOfKeywords,))
        (distanceRecommended,) = cursor.fetchone()
    else:
        distanceRecommended = ''

    return jsonify(result=distanceRecommended)


@app.route('/', methods=['GET'])
def welcome():
    print "welcome"
    return render_template('welcomePage.html', categoriesAZ = getCategories(conn, cursor, "AZ"), categoriesNV = getCategories(conn, cursor, "NV"), listOfCities = listOfCities, citySelected = False)

@app.route('/results', methods=['POST'])
def results():
    t0 = time.time()

    f = request.form
    citySelected = f['city']
    state = dictState[citySelected]

    listOfCategoriesInOurMatchingCategoriesDataset = getCategories(conn, cursor, state)
    listOfCategoriesImproved = []
    for category in listOfCategoriesInOurMatchingCategoriesDataset:
        for value in f.getlist('keywords'):
            if category[0] == value:
                category = category + (True,)
        listOfCategoriesImproved.append(category)

    distance = f['distance']
    numberOfOpportunitiesFromUser = f['numberOfOpportunities']

    if (len(f.getlist('keywords')) > 0 and distance and distance > 0 and numberOfOpportunitiesFromUser and numberOfOpportunitiesFromUser > 0):
        print numberOfOpportunitiesFromUser
        businessOpportunities = getBestBusinessesOpportunities(conn, cursor, f.getlist('keywords'), distance, numberOfOpportunitiesFromUser, state)
        t1 = time.time()
        t = round((t1 - t0),2)
        return render_template('welcomePage.html',
                               listOfCategoriesImproved = listOfCategoriesImproved,
                               businessOpportunities = businessOpportunities[0],
                               matchingCategories = businessOpportunities[1],
                               numberOfOpportunities = businessOpportunities[2],
                               loadingTime = t,
                               distance = distance,
                               uniqueListOfMatchingCategories = businessOpportunities[3],
                               counterOfMatchingCategoriesNameWithoutInitialCategories = businessOpportunities[4],
                               listOfOpportunities = businessOpportunities[5],
                               listOfCities = listOfCities,
                               citySelected = citySelected,
                               categoriesAZ = getCategories(conn, cursor, "AZ"),
                               categoriesNV = getCategories(conn, cursor, "NV")
                               )
    else:
        return render_template('welcomePage.html', categoriesAZ = getCategories(conn, cursor, "AZ"), categoriesNV = getCategories(conn, cursor, "NV"), listOfCities = listOfCities, citySelected = False)



if __name__ == "__main__":
    app.run(debug=True)
