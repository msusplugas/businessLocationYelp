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
--> [addNumberOfExistingCombinations.py](find%20relationships/filters/addNumberOfExistingCombinations.py) is the method that computes the number of time a business is in each categor. It is used to filter the files so that it removes the relationships that contains only a few businesses (in the case of this study: at least 3 businesses are required per category of a relationships)
--> [filterMatchingCategories.py](find%20relationships/filters/filterMatchingCategories.py) is the file that has been used to filter the relationships. It uses the parameters "median distances", "frequency" and the number of businesses required to filter the list of results. The filtering is done by indicating the percentiles required for each parameter.
* 

