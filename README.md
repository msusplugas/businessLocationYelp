# Recommending Ideal Location for Business based on Yelp Dataset

Welcome to the "Recommending Ideal Location for Business based on Yelp Dataset" repository. This repository contains the code that has been used to identify the relationships between the categories in Yelp and to show the results directtly to the users through our website.

The paper that describe this project in details can be found here: http://www.michaelsusplugas.com/yelp/results/paper.pdf

The website to see directly the results can be found here:
http://www.michaelsusplugas.com/yelp

This project has been made for the Yelp Dataset Challenge (round five): http://www.yelp.com/dataset_challenge/

This repository contains three folders:
* [find relationships](find%20relationships): It contains the methods used to determine the relationships between the different categories:
* [visualization and statistics](visualization%20and%20statistics): contains diverse files that show with some examples the dataset of Yelp. For instance [visualization and statistics / Examples with Google Map](visualization%20and%20statistics/Examples%20with%20Google%20Map)have different HTML files that show the positions of two categories on Google Map (for Phoenix only). This is useful to understand how the dataset is build on Yelp and what they mean concretely
* [web](web): Is the directory that contains the files used for the web server. The generation of the database is done with the methods in [web/Insert data in the database](web/Insert%20data%20in%20the%20database).

Folders in details
------------------

[find relationships](find%20relationships):
* [distances](find%20relationships/distances): It contains the method used to generate the "median distances" for each category. [generateMedianDistancesAccordingToMatchingCategories.py](find%20relationships/distances/generateMedianDistancesAccordingToMatchingCategories.py) is the file to run and it executes [computeDistances.py](find%20relationships/distances/computeDistances.py) to insert the businesses in a grid so that it speeds up the process
* [filters](find%20relationships/filters): It contains two methods.   
  + [addNumberOfExistingCombinations.py](find%20relationships/filters/addNumberOfExistingCombinations.py) is the method that computes the number of time a business is in each categor. It is used to filter the files so that it removes the relationships that contains only a few businesses (in the case of this study: at least 3 businesses are required per category of a relationships)
  + [filterMatchingCategories.py](find%20relationships/filters/filterMatchingCategories.py) is the file that has been used to filter the relationships. It uses the parameters "median distances", "frequency" and the number of businesses required to filter the list of results. The filtering is done by indicating the percentiles required for each parameter.
* [resultsFound](find%20relationships/resultsFound): It contains all the csv files results found during this study.
* [yahooCrawler](find%20relationships/yahooCrawler): It contains the files that were used to find the relationships between the categories (before filtering).
  + [exportCategoriesCSV.py](find%20relationships/yahooCrawler/exportCategoriesCSV.py) is the file that read the Yelp's business dataset to extract all the categories and store them in a CSV file.
  + [extendCategoriesWIthNLTK.py](find%20relationships/yahooCrawler/extendCategoriesWIthNLTK.py) is used to find synonyms and other related words for each category. It extend the list of keywords associated to the categories.
  + [yahoo.php](find%20relationships/yahooCrawler/yahoo.php) is the file used to get the 50 links per category.
  + [OAtuh.php](find%20relationships/yahooCrawler/OAuth.php) is the library used by Yahoo to connect to their servers.
  + [datamineUrls.py](find%20relationships/yahooCrawler/datamineUrls.py): this file uses the 50 links per category provided by the [yahoo.php](find%20relationships/yahooCrawler/yahoo.php) to find the matching categories by analyzing the keywords in the websites' links.
  + [datamineUrlsRemaining.py](find%20relationships/yahooCrawler/datamineUrlsRemaining.py): this file is used in the case of links that were not datamined by [datamineUrls.py](find%20relationships/yahooCrawler/datamineUrls.py). It will read each link and give them more time to get the results.
  + [mergeExtendedCategoriesInMatchingCategories.py](find%20relationships/yahooCrawler/mergeExtendedCategoriesInMatchingCategories.py) is the opposite of [extendCategoriesWIthNLTK.py](find%20relationships/yahooCrawler/extendCategoriesWIthNLTK.py). Given a list of keywords it will find for each keyword what is the original category. The goal is to use the keywords found on the websites to understand what are the matching categories.
  + [combinedMatchingCategoriesFile.py](find%20relationships/yahooCrawler/combinedMatchingCategoriesFile.py) is the file that is used to merge the two matching categories filed (in the case they are two). There can be two matching categories files if the process of finding these matching categories was interrupted.

[web](web):
* [Insert data in the database](web/Insert%20data%20in%20the%20database)/ [insertCSVConfigInDatabase.py](web/Insert%20data%20in%20the%20database/insertCSVConfigInDatabase.py) : Contains the methods to import in the database the data required to run the webserver. It inserts the businesses, matching categories (the list of relationships) and the list of categories (categories used in the Yelp dataset)
* [flask](web/flask) : the framework used to run this server. It contains:
  + [static](web/flask/static) is the folder that contains all the files used to improve the user experiance: css, images and javascript.
  + [template/welcomePage.html](flask/templates/welcomePage.html) is the folder (file) that handle the front end for Flask. It uses jinja2 for the templating.
  + [hello.py](web/flask/hello.py) is the core of the server application. It contains the main methods and routes used to show the results to the users.
  + [importDataFromDatabase.py](web/flask/importDataFromDatabase.py) contains all the methods used by the server to find the data and get the results from the database. It contains also the algorithm DBSCAN used to clusterize the businesses.
  
Generate the relationships
------------------
The relationships can be generated by running the scripts in the folder [find relationships](find%20relationships). The python files that are inside will do the different processes so that all the relationships between the initial categories and the matching categories can be discovered. The final result is a CSV file that contains the relationships and some details (frequency, median distances, number of businesses). This final file is generated by [filterMatchingCategories.py](find%20relationships/filters/filterMatchingCategories.py).

Therefore, the scripts to run to generate the relationships are the following:
1. [exportCategoriesCSV.py](find%20relationships/yahooCrawler/exportCategoriesCSV.py): Generate a csv file that contains the categories. Input: {dataset/yelp_academic_dataset_business.json}; Output: {resultsFound/yahooCrawler/categories' + state + '.csv'} where state is the parameter that represent which state is being evaluated.

2. [yahoo.php](find%20relationships/yahooCrawler/yahoo.php): Generate a csv file that contains the 50 links per category. It uses the results from [exportCategoriesCSV.py](find%20relationships/yahooCrawler/exportCategoriesCSV.py). Input: {resultsFound/yahooCrawler/categories' . $state . '.csv'}; Output {resultsFound/yahooCrawler/categories' . $state . 'WithUrl.csv} where $state is a parameter that represent which state is being evaluated.
3. [extendCategoriesWIthNLTK.py](find%20relationships/yahooCrawler/extendCategoriesWIthNLTK.py): Extend the categories previously found with [yahoo.php](find%20relationships/yahooCrawler/yahoo.php). Input {resultsFound/yahooCrawler/categories' + state + 'WithUrl.csv}; Output {resultsFound/yahooCrawler/categories' + state + 'ExtendedCategoriesWith025Improved2.csv}
4. [datamineUrls.py](find%20relationships/yahooCrawler/datamineUrls.py): read the contents of the links and find the keywords (matching categories). It uses the results from [extendCategoriesWIthNLTK.py](find%20relationships/yahooCrawler/extendCategoriesWIthNLTK.py). Input: {resultsFound/yahooCrawler/categories' + state + 'WithUrl.csv} and {resultsFound/yahooCrawler/categories' + state + 'ExtendedCategoriesWith025Improved2.csv}; Output {resultsFound/yahooCrawler/matchingCategories' + state + '.csv}
5. [mergeExtendedCategoriesInMatchingCategories.py](find%20relationships/yahooCrawler/mergeExtendedCategoriesInMatchingCategories.py): replace the keywords found by [datamineUrls.py](find%20relationships/yahooCrawler/datamineUrls.py) to the original category name. It uses the results of [datamineUrls.py](find%20relationships/yahooCrawler/datamineUrls.py). Input {resultsFound/yahooCrawler/matchingCategories' + state +  '.csv} and {resultsFound/yahooCrawler/categories' + state +  'ExtendedCategoriesWith025Improved2.csv}; Output: {resultsFound/yahooCrawler/statsMatchingCategoriesMerged' + state +  '.csv}.
6. [generateMedianDistancesAccordingToMatchingCategories.py](find%20relationships/distances/generateMedianDistancesAccordingToMatchingCategories.py): compute the distances between the businesses of the differents relationships. It uses the results of  [mergeExtendedCategoriesInMatchingCategories.py](find%20relationships/yahooCrawler/mergeExtendedCategoriesInMatchingCategories.py). Input {resultsFound/yahooCrawler/statsMatchingCategoriesMerged' + state +'.csv} and {dataset/yelp_academic_dataset_business.json}; Output {resultsFound/distances/medianDistancesAndMatchingCategoriesFrequencies' + state +'.csv}.
7. [addNumberOfExistingCombinations.py](find%20relationships/filters/addNumberOfExistingCombinations.py): add the number of existing businesses of the different categories of the relationship. It uses the result of [mergeExtendedCategoriesInMatchingCategories.py](find%20relationships/yahooCrawler/mergeExtendedCategoriesInMatchingCategories.py). Input {dataset/yelp_academic_dataset_business.json} and {resultsFound/distances/medianDistancesAndMatchingCategoriesFrequencies' + state +'.csv}; Output {resultsFound/filters/categoriesCountMedianDistancesAndMatchingCategoriesFrequencies' + state +'.csv}.
8. [filterMatchingCategories.py](find%20relationships/filters/filterMatchingCategories.py): Filter the results previously found to keep only the best. It uses the results from [addNumberOfExistingCombinations.py](find%20relationships/filters/addNumberOfExistingCombinations.py). Input {resultsFound/filters/categoriesCountMedianDistancesAndMatchingCategoriesFrequencies" + state + ".csv}; Output {resultsFound/filters/filter-' + state +'.csv}
