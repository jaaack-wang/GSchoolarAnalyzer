# GSchoolarAnalyzer (GSA)
This is a simple Python program than can be used to scrape information from researchers' Google Scholar homepages. 

The script was first causally written in August, 2020, in an attempt to help myself get to know "who a researcher is" in a minute. People who want to seek a future supervisor or research collaborator may find the program useful because it will generate an academic profile of a searched scholar based on information available on Google Scholar and save the scraped data on your computer. The source code as well as manual for the early version GSA can be found inside the [2020-08Version](https://github.com/jaaack-wang/GSchoolarAnalyzer/tree/main/2020-08Version) folder. The early version saves the scraped data in a txt file and the output looks like [this](https://github.com/jaaack-wang/GSchoolarAnalyzer/blob/main/2020-08Version/GSA_output.png).

The current version, however, saves the results in an excel file with 6 different sheets displaying 6 aspects of information: the basic info, the citation number over year, publication info and more nuanced analyses of the titles, years and authors of the available publications. The [sample output](https://github.com/jaaack-wang/GSchoolarAnalyzer/blob/main/【Sample_Output】Ronald%20A.%20Fisher%20GSProfile_2021-04-27.xlsx) is just located on this main page. 

Obviously, both versions are fine for personal use, but the current version makes post hoc quantitative analysis, if any, much easier since the scraped data is stored structurally. 

## Prerequisites
To use the program, you have to install Python Version 3.5 or later. 

You also need to install the following packages: [pandas](https://pandas.pydata.org), [requests](https://pypi.org/project/requests/), [BeautifulSoup](https://pypi.org/project/beautifulsoup4/), [selenium](https://github.com/SeleniumHQ/selenium/tree/trunk/py) and a [driver](https://github.com/SeleniumHQ/selenium/tree/trunk/py#drivers) that matches your browser that you want to remotely control with selenium.

## Usage
With [GSAnalyzer.py](https://github.com/jaaack-wang/GSchoolarAnalyzer/blob/main/GSAnalyzer.py) downloaded, you can either work directly on it or import it from outside. Suppose you choose to import it.

```python
from GSAnalyzer import GSAnalyzer
from selenium import webdriver


# Choose a driver. I used Chromedriver
wd = webdriver.Chrome('/usr/local/bin/chromedriver')
# load the driver into the GSAnalyzer class and specify the output directory
g = GSAnalyzer(wd, '/Users/wzx/Downloads/')

# Scraping one scholar's GS info by url
url = 'https://scholar.google.com/citations?user=2M6S-aAAAAAJ&hl=en'
# Loading the Google Scholar webpage up to 5 pages (by default). 
# The loading speed for the next page should be around 1 second to allow it to be fully loaded. 
g.loading_gs_homepage(url,loading_sp=1, pages_to_load=5)
# Generate the output and close the browser.
# You can specify the ngram model for the publciation titles along with a default unigram.
# Most_used is for the top ngram that you want to display.
# If add2database=True allows to add the basic info of the searched researcher(s) into a excel file 
# as the GS scholars' database for future reference. 
g.gs_profile_generator(n_gram=2, most_used=20, add2database=True)
g.close()


# Scraping multiple scholars' GS info by urls
urls = ['https://scholar.google.com/citations?user=2M6S-aAAAAAJ&hl=en',
        'https://scholar.google.com/citations?user=66ioxOQAAAAJ&hl=en']
# You do not have to do anything other than the following code
g.gs_profiles_generators_by_urls(urls, loading_sp=loading_sp, pages_to_load=pages_to_load, n_gram=2, most_used=20, add2database=True))

# You can pass a link in a list or as stirng to g.gs_profiles_generators_by_urls() as well and it works same way. 

```

The current program also allows you to scrape researchers' academic information available on Google Scholar by queries. 
```python
from GSAnalyzer import GSAnalyzer
from selenium import webdriver

queries = ['Claude E Shannon', 'Ronald A. Fisher', 'Max Karl Ernst Ludwig Planck']
wd = webdriver.Chrome('/usr/local/bin/chromedriver')
g = GSAnalyzer(wd, '/Users/wzx/Downloads/')
g.gs_profiles_generators_by_queries(queries, loading_sp=loading_sp, pages_to_load=pages_to_load, n_gram=2, most_used=20, add2database=True)

# If you only have one query, it is still ok to use the above function directly.
# You can either put the query in a list or as a string.
```

Please note that, if a query results in multiple scholars identified, the program will print "More than two scholars were found given the input query" along with a related link, which means that you need to manually identify your desired scholar and save his/her GS homepage link to use the program. Similarly, if no scholar is found given the query, the program will print "No scholar was found given the input query".

A better way to use the query is to add the research affiliation of the researcher with his/her name, which will increase the success rate.
