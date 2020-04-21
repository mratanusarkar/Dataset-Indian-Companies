import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import timedelta


# 4,52,568 unique companies found / 30 per page = 15086 pages
total_number_of_webpages = 15086


start_time = time.time()
dataframe_final = pd.DataFrame()

for page in range(1, total_number_of_webpages+1):
    print("scraping webpage number: {page} of {total}".format(page=page, total=total_number_of_webpages))
    loop_time = time.time()
    
    # set page url and header
    url = "https://www.ambitionbox.com/list-of-companies?page={}".format(page)
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}
    
    # get page response from the website
    response = requests.get(url, headers=header)
    # time.sleep(0.1)
    
    # pass the page to BeautifulSoup
    soup = BeautifulSoup(response.text, 'lxml')
    
    # find all the company cards from the webpage
    company_cards = soup.find_all("div", class_="company-content-wrapper")
    
    # extract all the required data from each company card and store them in a list
    name = []
    rating = []
    reviews = []
    domain = []
    location = []
    years_old = []
    employee_strength = []
    tags = []
    about = []
    
    # scrap scrap scrap!
    for card in company_cards:
        # 1. name
        try:
            name.append(card.find("h2").text.strip())
        except:
            name.append(None)

        # 2. rating
        try:
            rating.append(card.find("p", class_="rating").text.strip())
        except:
            rating.append(None)

        # 3. reviews
        try:
            reviews.append(card.find("a", class_="review-count sbold-Labels").text.strip().replace(" Reviews", ""))
        except:
            reviews.append(None)

        # 4. domain, 5. location, 6. years old & 7. employee strength
        info_list = card.find_all("p", class_="infoEntity sbold-list-header")
        dom = None
        loc = None
        old = None
        emp = None
        for i in range(4):
            try:
                if info_list[i].findChildren("i")[0]["class"][0] == 'icon-domain':
                    dom = info_list[i].text.strip()

                if info_list[i].findChildren("i")[0]["class"][0] == 'icon-pin-drop':
                    loc = info_list[i].text.strip()

                if info_list[i].findChildren("i")[0]["class"][0] == 'icon-access-time':
                    old = info_list[i].text.strip()

                if info_list[i].findChildren("i")[0]["class"][0] == 'icon-supervisor-account':
                    emp = info_list[i].text.strip()
            except:
                pass

        domain.append(dom)
        location.append(loc)
        years_old.append(old)
        employee_strength.append(emp)

        # 8. tags
        t = []
        try:
            for tag in card.find_all("a", class_="ab_chip"):
                t.append(tag.text.strip())
            t = ', '.join(t)
            tags.append(t)
        except:
            tags.append(None)

        # 9. about
        try:
            about.append(card.find("p", class_="description").text.strip())
        except:
            about.append(None)
    
    # make a dictionary containing all the data extracted
    col_dic = {
        "name": name,
        "rating": rating,
        "reviews": reviews,
        "domain": domain,
        "location": location,
        "years_old": years_old,
        "employee_strength": employee_strength,
        "tags": tags,
        "about": about
    }
    
    # pass the dictionary to pandas to create a dataframe (page)
    df = pd.DataFrame(col_dic)
    
    # append the dataframe to the final dataframe (the whole website)
    dataframe_final = dataframe_final.append(df, ignore_index=True)
    
    # success
    print("success!")
    print("time taken:", round((time.time()-loop_time)*1000, 2), "ms")
    print("total time elapsed:", str(timedelta(seconds=(time.time()-start_time))))
    print()

end_time = time.time()
print("full website scraped successfully!")
print("total time taken:", str(timedelta(seconds=(end_time - start_time))))
print()


# Print some statistics about the final dataframe:
print("dataframe shape", dataframe_final.shape)
print()
print("column-wise null count")
print(dataframe_final.isna().sum())
print()


# export the data to external csv
dataframe_final.to_csv("dataset/List_of_companies_in_India.csv", encoding="utf-8")
