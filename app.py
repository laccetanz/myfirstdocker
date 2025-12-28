#!/usr/bin/env python3.7

import threading
import requests
from bs4 import BeautifulSoup, Tag
import json
import os
import platform
import requests
import re
import time as t
from datetime import datetime, time


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
queries = dict()
apiCredentials = dict()
dbFile = "searches.tracked"
telegramApiFile = "telegram_api_credentials"


#-------------------------------------
# load queries from file
def load_queries():
    '''A function to load the queries from the json file'''
    global queries
    global dbFile
    if not os.path.isfile(dbFile):
        return
    with open(dbFile) as file:
        queries = json.load(file)


#-------------------------------------
#load telegram api from file
def load_api_credentials():
    '''A function to load the telegram api credentials from the json file'''
    global apiCredentials
    global telegramApiFile
    if not os.path.isfile(telegramApiFile):
        return
    with open(telegramApiFile) as file:
        apiCredentials = json.load(file)


#-------------------------------------
#print queries
def print_queries():
    '''A function to print the queries'''
    global queries
    output = []
    for search in queries.items():
        output.append("search: "+ str(search[0]))
        for query_url in search[1]:
            output.append("query url:" + str(query_url))
            for url in search[1].items():
                for minP in url[1].items():
                    for maxP in minP[1].items():
                        for result in maxP[1].items():
                            output.append("\n" + str(result[1].get('title').encode("utf-8", errors="ignore")))
                            output.append("Price: " + str(result[1].get('price')))
                            output.append("Location :" + str(result[1].get('location')))
                            output.append("Link: " + str(result[0]))
    return "\n".join(output)


#-------------------------------------
# printing a compact list of trackings
def print_sitrep():
    '''A function to print a compact list of trackings'''
    global queries
    output = []
    i = 1
    for search in queries.items():
        output.append("\n" + str(i) + " search: "+ str(search[0]))
        for query_url in search[1].items():
            for minP in query_url[1].items():
                for maxP in minP[1].items():
                    output.append("query url: "+str(query_url[0]))
                    if minP[0] !="null":
                        output.append(str(minP[0])+"<")
                    if minP[0] !="null" or maxP[0] !="null":
                        output.append(" price ")
                    if maxP[0] !="null":
                        output.append("<" + str(maxP[0]))
        i+=1
    return "\n".join(output)


#-------------------------------------
#refresh list
def refresh(notify):
    '''A function to refresh the queries

    Arguments
    ---------
    notify: bool
        whether to send notifications or not

    Example usage
    -------------
    >>> refresh(True)   # Refresh queries and send notifications
    >>> refresh(False)  # Refresh queries and don't send notifications
    '''
    global queries
    output = []
    try:
        for search in queries.items():
            for url in search[1].items():
                for minP in url[1].items():
                    for maxP in minP[1].items():
                         output.append(run_query(url[0], search[0], notify, minP[0], maxP[0]))
    except requests.exceptions.ConnectionError:
        output.append(datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + " ***Connection error***")
    except requests.exceptions.Timeout:
        output.append(datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + " ***Server timeout error***")
    except requests.exceptions.HTTPError:
        output.append(datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + " ***HTTP error***")
    except Exception as e:
        output.append(datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + " " + e)
    return "\n".join(output)


#-------------------------------------
#delete queries
def delete(toDelete):
    '''A function to delete a query

    Arguments
    ---------
    toDelete: str
        the query to delete

    Example usage
    -------------
    >>> delete("query")
    '''
    global queries
    output = []
    try:
        queries.pop(toDelete)
        output.append(str(toDelete) + " Deleted")
    except:
        output.append(str(toDelete) + " Not Found")
    return "\n".join(output)

#-------------------------------------
#add queries
def add(url, name, minPrice, maxPrice):
    ''' A function to add a new query

    Arguments
    ---------
    url: str
        the url to run the query on
    name: str
        the name of the query
    minPrice: str
        the minimum price to search for
    maxPrice: str
        the maximum price to search for

    Example usage
    -------------
    >>> add("https://www.subito.it/annunci-italia/vendita/usato/?q=auto", "auto", 100, "null")
    '''
    global queries
    # If the query has already been added previously, delete it
    if queries.get(name):
        delete(name)
    queries[name] = {url:{minPrice: {maxPrice:{}}}}


#-------------------------------------
#run single querie
def run_query(url, name, notify, minPrice, maxPrice):
    '''A function to run a query

    Arguments
    ---------
    url: str
        the url to run the query on
    name: str
        the name of the query
    notify: bool
        whether to send notifications or not
    minPrice: str
        the minimum price to search for
    maxPrice: str
        the maximum price to search for

    Returns
    -------
    output: str
        report on the entry added

    Example usage
    -------------
    >>> run_query("https://www.subito.it/annunci-italia/vendita/usato/?q=auto", "query", True, 100, "null")
    '''
    global queries
    output = []

    page = requests.get(url,headers=headers)
    page.raise_for_status()
    
    # print(page)
    if page.status_code == 200:
        output.append(str(datetime.now().strftime("%Y-%m-%d, %H:%M:%S")) + " running query ( " + str(name) +" - "+ str(url) +" ) ")
        products_deleted = False
        soup = BeautifulSoup(page.text, 'html.parser')
        # print(soup)

        #-----------------------------
        # product_list_items = soup.find_all('div', class_=re.compile(r'item-card'))
        script_tag = soup.find('script', id='__NEXT_DATA__')
        if not script_tag:
            output.append("Error: Could not find JSON data on page (Next.js data not found).")
            return

        json_data = json.loads(script_tag.string)

        try:
            items_list = json_data['props']['pageProps']['initialState']['items']['list']
        except KeyError:
            items_list = []
        #-----------------------------

        
        msg = []
    
        #-----------------------------
        # for product in product_list_items:
        #     title = product.find('h2').string
        for item_wrapper in items_list:
            product = item_wrapper.get('item')
            if not product:
                continue
        #-----------------------------

            try:
            #-----------------------------
            #    price=product.find('p',class_=re.compile(r'price')).contents[0]
            #    # check if the span tag exists
            #    price_soup = BeautifulSoup(price, 'html.parser')
            #    if type(price_soup) == Tag:
            #       continue
            #    #at the moment (20.5.2021) the price is under the 'p' tag with 'span' inside if shipping available
            #    price = int(price.replace('.','')[:-2])
            # except:
                item_key = product.get('urn')
                if not item_key: continue

                title = product.get('subject', 'No Title')
                link = product.get('urls', {}).get('default', '')
                location = product.get('geo', {}).get('town', {}).get('value', 'Unknown location')

                # Price extraction
                raw_price = None
            #-----------------------------

                price = "Unknown price"

            #-----------------------------    
            # link = product.find('a').get('href')
                features = product.get('features', {})
                price_feature = features.get('/price')
                if price_feature and 'values' in price_feature:
                    raw_price = price_feature['values'][0].get('key')

                if raw_price:
                    try:
                        price = int(raw_price)
                    except ValueError:
                        pass

                is_sold = product.get('sold', False)
            #-----------------------------    

            #-----------------------------    
            # sold = product.find('span',re.compile(r'item-sold-badge'))
            except Exception as e:
                continue
            #-----------------------------  

    
            # check if the product has already been sold
            #-----------------------------  
            # if sold != None:
            if is_sold:
            #-----------------------------              
                # if the product has previously been saved remove it from the file
                if queries.get(name).get(url).get(minPrice).get(maxPrice).get(link):
                    del queries[name][url][minPrice][maxPrice][link]
                    products_deleted = True
                continue
    
            #-----------------------------  
            #try:
            #    location = product.find('span',re.compile(r'town')).string + product.find('span',re.compile(r'city')).string
            #except:
            #    output.append(str(datetime.now().strftime("%Y-%m-%d, %H:%M:%S")) + " Unknown location for item " + str(title))
            #    location = "Unknown location"
            #-----------------------------  


            if minPrice == "null" or price == "Unknown price" or price>=int(minPrice):
                if maxPrice == "null" or price == "Unknown price" or price<=int(maxPrice):
                    if not queries.get(name).get(url).get(minPrice).get(maxPrice).get(link):   # found a new element
                        queries[name][url][minPrice][maxPrice][link] ={'title': title, 'price': price, 'location': location}
                        output.append(" Adding result: "+ str(price) + "€ - " + str(title) + " - " + str(location))
                        tmp = (str(price) + "€ - " + str(title) + " - " + str(location) + " - " + str(link) + '\n' ) # compose telegram msg
                        msg.append(tmp)



        # recap of query run                
        if len(msg) > 0:
            if notify:
                if is_telegram_active():
                    send_telegram_messages(msg)
                output.append(str(len(msg)) + " new elements have been found.\n")
            save_queries()
        else:
            output.append("All lists are already up to date.\n")
            # if at least one search was deleted, update the search file
            if products_deleted:
                save_queries()
    else:
        output.append(str(datetime.now().strftime("%Y-%m-%d, %H:%M:%S")) + " Failed to fetch " + str(url) + ": status code " + str(page.status_code))
        # send_telegram_messages(["Failed to fetch"])
    
    t.sleep(5)

    return "\n".join(output)
#-------------------------------------
#save queries to json file    
def save_queries():
    '''A function to save the queries
    '''
    with open(dbFile, 'w') as file:
        file.write(json.dumps(queries))


#-------------------------------------
#save telegram api to file
def save_api_credentials():
    '''A function to save the telegram api credentials into the telegramApiFile'''
    with open(telegramApiFile, 'w') as file:
        file.write(json.dumps(apiCredentials))


#-------------------------------------
#check if telegram is active
def is_telegram_active():
    '''A function to check if telegram is active, i.e. if the api credentials are present

    Returns
    -------
    bool
        True if telegram is active, False otherwise
    '''
    return "chatid" in apiCredentials and "token" in apiCredentials


#-------------------------------------
#send telegram notify
def send_telegram_messages(messages):
    '''A function to send messages to telegram

    Arguments
    ---------
    messages: list
        the list of messages to send

    Example usage
    -------------
    >>> send_telegram_messages(["message1", "message2"])
    '''
    for msg in messages:
        request_url = "https://api.telegram.org/bot" + apiCredentials["token"] + "/sendMessage?chat_id=" + apiCredentials["chatid"] + "&text=" + msg
        requests.get(request_url)


#-------------------------------------
#check if time is in between two items
def in_between(now, start, end):
    '''A function to check if a time is in between two other times

    Arguments
    ---------
    now: datetime
        the time to check
    start: datetime
        the start time
    end: datetime
        the end time

    Example usage
    -------------
    >>> in_between(datetime.now(), datetime(2021, 5, 20, 0, 0, 0), datetime(2021, 5, 20, 23, 59, 59))
    '''

    if start < end:
        return start <= now < end
    elif start == end:
	    return True
    else: # over midnight e.g., 23:30-04:15
        return start <= now or now < end




        

#-------------------------------------
#-------------------------------------
#-------------------------------------
if __name__ == '__main__':

    #-------------------------------------
    ### Setup commands ###
    #load files
    print(datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + "STARTING")
    load_queries()
    load_api_credentials()
    
    print("\n")
    
    print(print_sitrep())
    
    print("\n")
    
    daemon_DELAY = "600"
    
    notify = True
    
    while True:
        # if in_between(datetime.now().time(), time(int(daemon_ACTIVE)), time(int(daemon_PAUSE))):
        print(refresh(notify))
        notify = True
        print("\n")
        print(str(daemon_DELAY) + " seconds to next poll.")
        save_queries()
        t.sleep(int(daemon_DELAY))
                
    #-------------------------------------
    save_queries()



