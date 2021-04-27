import time
import nltk
import os
import re
from selenium import webdriver
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# The url of the researcher's homepage on Google Scholar
url = 'https://scholar.google.com/citations?user=37jEMC0AAAAJ&hl=en'
# The most frequent one token or two used in the titles of the scholar's works to display
most_fre = 20
# Put the root where you want to get the file saved on your computer
root = '/Users/wzx/Library/Mobile Documents/com~apple~CloudDocs/Documents/Web Scraping/Google Scholar Profile/'
# Change the equation if you do not have NLTK data installed. Use the alternative as in the Manual
stop_words = stopwords.words('english')


# This function will come in handy when extracting texts of extracted tags
def texts_extractor(xpath):
    targets = wd.find_elements_by_xpath(xpath)
    texts = [target.text for target in targets]
    return texts


# Used to lemmatize tokens into their stems
lemmatizer = WordNetLemmatizer()


# Program begins
wd = webdriver.Chrome()
# Get the Google Scholar homepage of the interested researcher
wd.get(url)

# This will locate the SHOW MORE button at the bottom of the webpage
# We do this in the very beginning because the website is dynamic
# and we have to fully load the webpage before extracting any information
show_more = wd.find_element_by_xpath('//*[@id="gsc_bpf_more"]/span/span[2]')
more_to_show = True
click_times = 0
while more_to_show:
    cur_page_trs = wd.find_elements_by_class_name('gsc_a_tr')
    show_more.click()
    click_times += 1
    # Pause for 1 sec to get the renewed webpage loaded
    time.sleep(1)
    renewed_page_trs = wd.find_elements_by_class_name('gsc_a_tr')
    # Current page and renewed page have same amount of listed articles, that means there is no more page to load
    # The reasons to limit the click times up to 5 (which equals up to 500 articles on display are twofold:
    # first, to reduce irrelevant articles that might have no direct connection with the interested scholar;
    # second, to have the running of the program complete in a relatively bearable time span (within 2 minutes)
    if cur_page_trs == renewed_page_trs or click_times == 5:
        more_to_show = False

# Get basic information of the interested scholar
name = wd.find_element_by_xpath('//*[@id="gsc_prf_in"]').text
name_final = name.split(' ')[-1].lower()
name_initial = name.split(' ')[0].lower()
# The formatting of the organisation section on the webpage changes according to whether there is a link to it
# By using the following methods, only the name of the organisation the scholar is affiliated with will be extracted
org = wd.find_elements_by_xpath('//*[@id="gsc_prf_i"]/div[2]/a')
if org:
    org = org[0].text
else:
    org = wd.find_element_by_xpath('//*[@id="gsc_prf_i"]/div[2]').text
org = org.split(',')[-1] if 'Professor' in org or 'professor' in org else org
# Get the link of the homepage of the scholar if provided, otherwise "not available"
homepage = wd.find_elements_by_xpath('//*[@id="gsc_prf_ivh"]/a')
if homepage:
    homepage = homepage[0].get_attribute('href')
else:
    homepage = 'Not available'
# Get the basic citation info of the scholar as shown on the right side of the Google Scholar
citation_all = wd.find_element_by_xpath('//*[@id="gsc_rsb_st"]/tbody/tr[1]/td[2]').text
since_year = wd.find_element_by_xpath('//*[@id="gsc_rsb_st"]/thead/tr/th[3]').text
citation_since = wd.find_element_by_xpath('//*[@id="gsc_rsb_st"]/tbody/tr[1]/td[3]').text
# Get a list of specialized areas as listed on Google Scholar
specialized_areas = texts_extractor('//*[@id="gsc_prf_int"]/a')

# Get the breakdown information of the articles listed on Google Scholar, including
# title, author(s), citation, year of publication, places of publication
titles = texts_extractor('//*[@id="gsc_a_b"]/tr/td[1]/a')
authors = texts_extractor('//*[@id="gsc_a_b"]/tr/td[1]/div[1]')
citations = texts_extractor('//*[@id="gsc_a_b"]/tr/td[2]')
years = texts_extractor('//*[@id="gsc_a_b"]/tr/td[3]')
years_filtered = [y for y in years if y.isdigit()]
places_of_pub = texts_extractor('//*[@id="gsc_a_b"]/tr/td[1]/div[2]')

# Quit the browser
wd.quit()


# Further processing of raw data obtained above
# Most used one token or two used in titles
lexicons = []
tokenizer = nltk.tokenize.RegexpTokenizer(r'[\'\w-]+')
for title in titles:
    tokenized_title = tokenizer.tokenize(title)
    words = [w.lower() for w in tokenized_title]
    lexicons.extend(words)
lexicons_filtered = [w for w in lexicons if w not in stop_words]
lexicons_filtered = [lemmatizer.lemmatize(w) for w in lexicons_filtered]
lexicons_fd = nltk.FreqDist(lexicons_filtered).most_common(most_fre)
lexicons_bi_gm = [*map(' '.join, nltk.bigrams(lexicons_filtered))]
lexicons_bi_gm_fd = nltk.FreqDist(lexicons_bi_gm).most_common(most_fre)

# Calculate the average number of author(s) and the distribution of author positions for the interested scholar
authors_num = sum(len(a.split(',')) for a in authors)
which_author_list = []
for author in authors:
    author_list = author.split(',')
    which_author_list.extend([author_list.index(i) + 1 for i in author_list if name_final in i.lower() or name_initial in i.lower()])
which_author_list_fd = nltk.FreqDist(which_author_list).most_common()
which_author_list = [('#_' + str(i[0]), i[1]) for i in which_author_list_fd]
which_author_dict = dict(which_author_list)

# Reduce extracted extra line because of the use of '*' in Google Scholar citation
citations = [re.sub(r'\n', ' ', i) for i in citations]

# Start saving all the data you have retrieved into your computer
sub_root = root + org.upper() + '/'
try:
    if not os.path.exists(sub_root):
        os.mkdir(sub_root)
    path = f'{sub_root}{name}.txt'
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(f'Name: {name}\nOrganization: {org}\nHomepage: {homepage}\nGoogle Scholar: {url}'
                    f'\nBiggest Citation: {citations[0]}  Citation ({min(years_filtered)} ~ {max(years_filtered)}): {citation_all}   Citation {since_year}: {citation_since}')
            f.write(f'\nAverage authors: {authors_num / len(authors)}')
            f.write(f'\nWhich author: {which_author_dict}')
            f.write('\nSpecialized areas: ')

            template_1 = "{0:^20}\t{1:^10}\t{2:^30}\t{3:^10}"
            for sa in specialized_areas:
                f.write(sa + '; ')
            f.write(f'\n\n\n{most_fre} MOST USED words and bigrams\n\n' +
                    template_1.format('Word', 'Frequency', 'Bigram', 'Frequency'))
            for i in range(most_fre):
                f.write('\n' + template_1.format(lexicons_fd[i][0], lexicons_fd[i][1],
                                                 lexicons_bi_gm_fd[i][0], lexicons_bi_gm_fd[i][1]))
            if len(titles) < 500:
                f.write(f'\n\n\nFull WORKS({len(titles)}) by citation\n')
            else:
                f.write('\n\n\nSelected 500 WORKS by citation\n')
            for n in range(0, len(titles)):
                f.write(f'\nTitle: {titles[n]}\nAuthor(s): {authors[n]}\nPublication: {places_of_pub[n]}'
                        f'\nCitation: {citations[n]}\nYear: {years[n]}\n')
            f.close()
            print('File Saved!')
    else:
        print('File already exists!')
except:
    print('Oop! File not saved!')
