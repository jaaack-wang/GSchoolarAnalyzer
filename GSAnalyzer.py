import requests
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
import pandas as pd
import os


def gshp_link_by_query(query):
    # Find a researcher's Google Scholar homepage link by a query
    kw = '+'.join(query.split())
    search_link = 'https://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors=' + kw
    r = requests.get(search_link)
    if r.status_code == 200:
        soup = bs(r.content, 'html.parser')
        if len(soup.select('.gsc_1usr')) == 1:
            return 'https://scholar.google.com' + soup.select('.gsc_1usr')[0].find('a')['href']
        elif len(soup.select('.gsc_1usr')) == 0:
            print(f'No scholar was found given the input {query}')
            return None
        # If multiple scholars are found given the query, a manual inspection is required
        elif len(soup.select('.gsc_1usr')) > 1:
            print(f'More than two scholars were found given the input {query}.'
                  f'\nSee: {search_link}')
            return None
    else:
        print(f"A bad request. {r.status_code} Client Error.")
        return None


def spw_filter(string):
    """Filter stopwords in a given string --> Titles of researchers' publications"""
    stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
                 "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
                 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
                 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these',
                 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do',
                 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
                 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before',
                 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
                 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
                 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
                 'same', 'so', 'than', 'too', 'very', 'can', 'cannot', 'will', 'just', "don't", 'should', "should've",
                 'now', "aren't", "couldn't", "didn't", "doesn't", "hadn't", "hasn't", "haven't", "isn't", "mightn't",
                 "mustn't", "needn't", "shan't", "shouldn't", "wasn't", "weren't", "won't", "wouldn't"]

    return [tk.strip() for tk in string.lower().split() if tk not in stopwords]


def ngram(tokens, n):
    start = 0
    end = len(tokens) - n + 1
    res = []
    for i in range(start, end):
        res.append(' '.join(tokens[i:i+n]))
    return res


def filtered_ngram(list_of_str, n):
    ngram_res = []
    if n == 1:
        for st in list_of_str:
            ngram_res.extend(spw_filter(st))
    else:
        tks = [spw_filter(st) for st in list_of_str]
        # To avoid creating a unwanted ngram based on mixed titles
        for tk in tks:
            if len(tk) >= n:
                ngram_res.extend(ngram(tk, n))
    return ngram_res


def counter(alist, most_common=None):
    if not type(alist) is list:
        alist = list(alist)
    else:
        pass
    counts = dict()
    for i in alist:
        counts[i] = counts.get(i, 0) + 1

    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:most_common]


class GSAnalyzer:

    def __init__(self, wd, res_dir):
        self.wd = wd
        self.res_dir = res_dir if res_dir.endswith('/') else res_dir + '/'

    def loading_gs_homepage(self, url, loading_sp=1, pages_to_load=5):
        # loading a researcher's GS homepage to the fullest or to a given page
        self.wd.get(url)
        self.url = url
        # the publication list in the previous page before loading
        pre_page_plist = self.wd.find_elements_by_class_name('gsc_a_tr')
        # keep loading the webpage
        show_more = self.wd.find_element_by_xpath('//*[@id="gsc_bpf_more"]/span/span[2]')
        loading_sp = loading_sp
        pages_to_load = pages_to_load
        click_times = 0
        while click_times < pages_to_load:
            show_more.click()
            click_times += 1
            time.sleep(loading_sp)
            cur_page_plist = self.wd.find_elements_by_class_name('gsc_a_tr')
            if len(pre_page_plist) == len(cur_page_plist):
                self.plist = cur_page_plist
                break
            else:
                pre_page_plist = cur_page_plist

    def list_of_texts_by_xpath(self, xpath):
        targets = self.wd.find_elements_by_xpath(xpath)
        return [target.text for target in targets]

    def gs_basic_info(self):
        # basic info: name, affiliation, homepage (if any), gs_url, specialization,
        # all-time citation, past 5 year citation, date recorded

        self.gs_name = wd.find_element_by_xpath('//*[@id="gsc_prf_in"]').text
        try:
            affiliation = wd.find_element_by_xpath('//*[@id="gsc_prf_i"]/div[2]/a').text
        except:
            affiliation = 'Unknown'
        try:
            homepage = wd.find_element_by_xpath('//*[@id="gsc_prf_ivh"]/a').get_attribute('href')
        except:
            homepage = 'Not available'
        specialization = '; '.join(self.list_of_texts_by_xpath('//*[@id="gsc_prf_int"]/a'))
        all_citation = wd.find_element_by_xpath('//*[@id="gsc_rsb_st"]/tbody/tr[1]/td[2]').text
        past5y_citation = wd.find_element_by_xpath('//*[@id="gsc_rsb_st"]/tbody/tr[1]/td[3]').text

        self.date = datetime.now().strftime('%Y-%m-%d')
        return [self.gs_name, affiliation, homepage, self.url, specialization, all_citation, past5y_citation, self.date]

    def citation_by_year(self):
        # Return the citation number over the years
        r = requests.get(self.url)
        soup = bs(r.content, 'html.parser')
        years = [int(y.text) for y in soup.select('#gsc_rsb_cit > div > div.gsc_md_hist_w > div > span')]
        citations = [int(c.text) for c in soup.select('#gsc_rsb_cit > div > div.gsc_md_hist_w > div > a > span')]
        return zip(years, citations)

    def gs_publication_info(self):
        # Publication info: title, author, link (for more details),
        # author(s), citation, year, source (place of publication)
        titles_links = self.wd.find_elements_by_xpath('//*[@id="gsc_a_b"]/tr/td[1]/a')
        self.titles = [title.text for title in titles_links]
        self.links = ['https://scholar.google.com' + link.get_attribute('data-href') for link in titles_links]
        self.authors = self.list_of_texts_by_xpath('//*[@id="gsc_a_b"]/tr/td[1]/div[1]')
        self.citations = self.list_of_texts_by_xpath('//*[@id="gsc_a_b"]/tr/td[2]')
        self.years = self.list_of_texts_by_xpath('//*[@id="gsc_a_b"]/tr/td[3]')
        self.source = self.list_of_texts_by_xpath('//*[@id="gsc_a_b"]/tr/td[1]/div[2]')
        return zip(self.titles, self.links, self.authors, self.citations, self.years, self.source)

    def titles_ngram_analysis(self, n_gram=2, most_used=20):
        # Return unigram and specified ngram analysis of the titles
        if not self.titles:
            self.titles = self.list_of_texts_by_xpath('//*[@id="gsc_a_b"]/tr/td[1]/a')
        unigram = filtered_ngram(self.titles, 1)
        ngram_ = filtered_ngram(self.titles, n_gram)
        fdist_ug = counter(unigram)
        fdist_ug = fdist_ug[:most_used] if len(fdist_ug) >= most_used else fdist_ug
        fdist_ng = counter(ngram_)
        fdist_ng = fdist_ng[:most_used] if len(fdist_ng) >= most_used else fdist_ng
        if len(fdist_ng) < len(fdist_ug):
            for i in range(len(fdist_ug) - len(fdist_ng)):
                fdist_ng.append(('', ''))
        splitter = [''] * len(fdist_ug)

        return zip(fdist_ug, splitter, fdist_ng)

    def num_of_pub_by_year(self):
        # Return the number of publication each year
        if not self.years:
            self.years = self.list_of_texts_by_xpath('//*[@id="gsc_a_b"]/tr/td[3]')
        years = [str(y) for y in self.years]
        return counter(years)

    def authors_analysis(self):
        # 1. The contribution of the researcher of interest to the publications that he/she authored.
        # The contribution is intuitively displayed as the frequency of the author ranks the researcher was in.
        # 2. The list of co-author, including the researcher him/herself.
        if not self.authors:
            self.authors = self.list_of_texts_by_xpath('//*[@id="gsc_a_b"]/tr/td[1]/div[1]')

        auth_list = []
        last_name = self.gs_name.split()[-1].strip()
        contribution_index = []

        for au in self.authors:
            l = [a.strip() for a in au.split(',')]
            auth_list.extend(l)
            if last_name in au:
                contribution_index.extend([l.index(i) + 1 for i in l if last_name in i])
            else:
                contribution_index.append('N/A')

        ctr_fdist = counter(contribution_index)
        ctr_fdist = [('Which author', 'Count')] + [('#_' + str(i), j) for i, j in ctr_fdist]
        ctr_fdist += [('# of Pubs', len(self.authors)), ('', ''), ('Author', 'Count')]
        auth_fdist = counter(auth_list)

        return ctr_fdist + auth_fdist

    def gs_profile_database(self, info):
        # The basic info of the scholar searched will be aggregated into an excel file
        path = self.res_dir + 'Aggregated GS Database.xlsx'
        if os.path.exists(path):
            df = pd.read_excel(path)
            df.loc[df.shape[0]] = info
            print(f'File {path} created!')
        else:
            df = pd.DataFrame(columns=[
                'Name', 'Affiliation', 'Homepage', 'GScholarUrl', 'Specialization',
                'Citation(All)', 'Citation(Past 5 Year)', 'Date Recorded'
            ])
            df.loc[0] = info
            print(f'File {path} updated!')
        df.to_excel(path, index=False)

    def gs_profile_generator(self, n_gram=2, most_used=20, add2database=True):
        """
        :param n_gram: for the analysis of the publication titles
        :param most_used: for the analysis of the publication titles
        :param add2database: whether the researcher's basic info is saved in the aggregated database
        :return: The researcher's GS profile and by default the Aggregated GS Database (basic info)
        """
        info = self.gs_basic_info()
        basic_info = pd.Series(info, index=[
            'Name', 'Affiliation', 'Homepage', 'GScholarUrl', 'Specialization',
            'Citation(All)', 'Citation(Past 5 Year)', 'Date Recorded'
        ])
        citation_by_y = pd.DataFrame(self.citation_by_year(), columns=['Year', 'Citation'])
        publication_info = pd.DataFrame(self.gs_publication_info(), columns=[
            'Title', 'Link', 'Author', 'Citation', 'Year', 'Source'
        ])
        titles_ngram = pd.DataFrame(self.titles_ngram_analysis(n_gram, most_used), columns=[
            'Unigram', '', f'{n_gram}-gram'
        ])
        pub_years = pd.DataFrame(self.num_of_pub_by_year(), columns=['Year', 'Count'])
        authors = pd.DataFrame(self.authors_analysis())

        if add2database:
            self.gs_profile_database(info)

        writer = pd.ExcelWriter(f'{self.res_dir}{self.gs_name} GSProfile_{self.date}.xlsx')
        basic_info.to_excel(writer, sheet_name='Basic Info', header=False)
        citation_by_y.to_excel(writer, sheet_name='Citation by Year', index=False)
        publication_info.to_excel(writer, sheet_name='Publication Info', index=False)
        titles_ngram.to_excel(writer, sheet_name='Titles Ngram', index=False)
        pub_years.to_excel(writer, sheet_name='Pub Num by Year', index=False)
        authors.to_excel(writer, sheet_name='Authors Analysis', header=False, index=False)
        writer.save()
        print(f'File {self.res_dir}{self.gs_name} GSProfile_{self.date}.xlsx saved!')

    def gs_profiles_generators_by_urls(self, urls, n_gram=2, most_used=20, add2database=True):
        if not type(urls) is list:
            print('Please enter a list of urls!')
            try:
                self.loading_gs_homepage(urls)
                self.gs_profile_generator(n_gram=n_gram, most_used=most_used, add2database=add2database)
            except:
                self.close()
        else:
            for url in urls:
                try:
                    self.loading_gs_homepage(url)
                    self.gs_profile_generator(n_gram=n_gram, most_used=most_used, add2database=add2database)
                except:
                    print(f'Nothing found in {url}')
        self.close()

    def gs_profiles_generators_by_queries(self, queries, n_gram=2, most_used=20, add2database=True):
        if not type(queries) is list:
            url = gshp_link_by_query(queries)
            if url is not None:
                self.loading_gs_homepage(url)
                self.gs_profile_generator(n_gram=n_gram, most_used=most_used, add2database=add2database)
        else:
            urls = []
            for query in queries:
                url = gshp_link_by_query(query)
                if url is not None:
                    urls.append(url)
            self.gs_profiles_generators_by_urls(urls, n_gram=n_gram, most_used=most_used, add2database=add2database)

    def close(self):
        self.wd.quit()
