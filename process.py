import urllib.request as web
from operator import itemgetter
import re
from flask import Flask, render_template, request
from bs4 import BeautifulSoup


app = Flask(__name__) # defining a flask application


@app.route('/', methods=['GET', 'POST']) #auto run the following method
def index(): # 0
    return render_template('index.html') # return the rendered html file


def findUrlsInWebPage(page): # 5
    link_start = page.find('<a href=') #find the anchor tag in the html file fo the specified url
    if link_start == -1:
        return None, 0
    else:
        link_initial = page.find('"', link_start) # to find the initial offset value of the link
        link_end = page.find('"', link_initial + 1) # to find the end offset value of the link
        url = page[link_initial + 1: link_end] # slicing the url
        return url, link_end


def listingUrls(page): # 4
    links = list()
    links_list = list()
    while True:
        url, end_pos = findUrlsInWebPage(page) #invoking the findUrlsInWebPage()
        if url:
            links.append(url) #appending the urls to the list
            page = page[end_pos:]
        else:
            break
    for link in links: #searching for more urls in the links list
        pattern = re.compile("(https|http)(://)((www)|.*)(\.?)(.+)(\.)((\w\w\w)|(\w+\.\w\w))(/.*)", re.IGNORECASE) # Matching the provided urls
        match_object = pattern.match(link)
        if match_object: # if links matched specified pattern
            links_list.append(link) # append all the urls to the new list
    return links_list


def contentExtract(page): # 3
    source = web.urlopen(page).read().decode('utf-8') # reading the html page and decoding into utf-8 format
    links = listingUrls(source) # passing the content of the url to the listingUrls()
    return links


def urlOpenFunction(urls): # 6
    try:
        pages = web.urlopen(urls).read().decode('utf-8') # reading the html page and decoding into utf-8 format
        return pages
    except Exception:
        pass


def sortingLinks(url_list, count_list): #7
    keys, values = url_list, count_list
    url_dict = dict(zip(keys, values))
    link_list = list()
    for key, value in sorted(url_dict.items(), key=itemgetter(1), reverse=True): # sorting the urls based on key values
       if value > 0:
           link_list.append(key) # appending the key values to a new list
       else:
           continue
    return link_list


def titleDescription(links):
    title_list = list()
    desc_list = list()
    for link in links:
        try:
            page = web.urlopen(link).read()
            soup = BeautifulSoup(page, 'html.parser')
            title_list.append(soup.title.string)
            try:
                desc_list.append(soup.find("meta", {'name': 'description'})['content'])
            except:
                desc_list.append(soup.find('p').string)
        except:
            pass
    return title_list, desc_list

@app.route('/searchWordInWebPage', methods=['POST'])
def searchWordInWebPage(): # 2
    max_value = 1000
    count = 0
    if request.method == 'POST':
        words = request.form['search_box'].strip().lower() #strip the search term and convert to lowercase
        word_list = words.split()
        word_list.append(words)
        word_list.reverse()
        counter = 0
        count_list = list()
        url_list = ['https://www.python.org', 'https://www.twitter.com', 'https://www.youtube.com',
                    'https://www.wikipedia.org', 'https://www.facebook.com', 'https://www.udacity.com',
                    'https://www.plus.google.com']
        link_list = list()
        link_urls = list()
        for urls in url_list:
            link_list.append(contentExtract(urls))
        for url_ in link_list:
            if url_ != "":
                for urls_ in url_:
                    link_urls.append(urls_)
        for link in link_urls:
            url_list.append(link)
        for word in word_list:
            for url in url_list:
                try:
                    extract_text = urlOpenFunction(url)
                    extract_text = str(extract_text).lower()  # converting the content to string in lower case
                    count = extract_text.count(word)
                    counter = counter + count
                    count_list.append(count)
                except Exception:
                    continue
        links = sortingLinks(url_list, count_list) #the url list and count list are passed for sorting
        titles, descs = titleDescription(links)
        return render_template('Result.html', links=links, counter=len(links), titles=titles, descs=descs) # rendering the html page for the output


# to run the program automatically when the local url is given

if __name__ == "__main__": # 1
    app.run(debug=True, threaded=True)
