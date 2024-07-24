import pandas as pd
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import datetime
import logging
import re
import json
import urllib
logging.basicConfig(filename="search.log", level=logging.INFO)
pd.options.mode.chained_assignment = None  # default='warn'

# predefined declarations
search_sites = ["site:greenhouse.io", "site:lever.co", "site:dover.com", "site:jobs.* ", "site:careers.*", "site:oraclecloud.com",
                "site:myworkdayjobs.com", "site:icims.com", "site:notion.site"]
clearance = ["Top Secret",
             "Top Secret/Sensitive Compartmented Information", "TS/SCI", "Polygraph", "US Secret security clearance"]
sponsorship = ["not offering new sponsorships", "no sponsorship",
               "not offering sponsorships", "do not sponsor", "No visa sponsorship"]
time = {"Past hour": "qdr:h",	"Past day": "qdr:d",
        "Past week": "qdr:w", "Past month": "qdr:m", "Past year": "qdr:y"}

us_location = ["usa", "us", "america",
               "united states of america", "united states"]
default = {
    "role": "Software engineer",
    "location": "USA",
    "keywords": "",
    "exclusion": "",
    "no_of_hits": 10,
    "time_filter": "Past day",
    "clearance": "True",
    "sponsorship": "True",
    "filtering": "True"
}


def initializations(data):
    logging.info(
        f'{datetime.datetime.now()} Entered the Initialization module')
    if data['location'] == "":
        data['location'] = default['location']
    if data['no_of_hits'] == "":
        data['no_of_hits'] = default['no_of_hits']
    if data['time_filter'] == "":
        data['time_filter'] = default['time_filter']
    if data['location'].lower() in us_location:
        data['location'] = "united states"
    considerations = [i for i in data if data[i]
                      == "True" and i != "filtering"]
    if data['location']:
        considerations.append('location')
    if len(data['search_sites']) == 0:
        data['search_sites'] = search_sites
    logging.info(
        f'{datetime.datetime.now()} Existing the Initialization module')
    return data, considerations


def url_lang_coun_update(url):
    pattern = r"/[a-z]{2}-[A-Z]{2}/"
    match = re.search(pattern, url)

    if match and "en-US" not in url:
        new_url = re.sub(pattern, "/en-US/", url)
        return new_url
    else:
        return url


def language_adjustments(url_list):
    logging.info(
        f'{datetime.datetime.now()} Entered the language_adjustments module')
    for url in url_list:
        if "myworkdayjobs" in url:
            uin = url_list.index(url)
            new_url = url_lang_coun_update(url)
            url_list[uin] = new_url
    logging.info(
        f'{datetime.datetime.now()} Existing the language_adjustments module')
    return url_list


def is_valid_json(string):
    try:
        json.loads(string, strict=False)
    except ValueError:
        return False
    return True


def string_search(response, constraint):
    logging.info(
        f'{datetime.datetime.now()} Entered the String Search Module for {constraint}')
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    text_content = soup.get_text()
    for const in constraint:
        if const in text_content:
            logging.info(
                f'{datetime.datetime.now()} Search for {constraint} is found')
            return True
    logging.info(
        f'{datetime.datetime.now()} Search for {constraint} is not found')
    return False


def extract_location(json_data):
    logging.info(
        f'{datetime.datetime.now()} Entered the location extract for other urls Module')
    jstring = json.dumps(json_data['jobLocation'])
    if 'name' in jstring:
        val = 'name'
    elif 'addressLocality' in jstring:
        val = 'addressLocality'
    if 'val' in locals():
        if isinstance(json_data['jobLocation'], list):
            if isinstance(json_data['jobLocation'][0]['address'], list):
                al = json_data['jobLocation'][0]['address'][0][val] or ""
                ac = json_data['jobLocation'][0]['address'][0]['addressCountry'] or ""
            else:
                al = json_data['jobLocation'][0]['address'][val] or ""
                ac = json_data['jobLocation'][0]['address']['addressCountry'] or ""
        elif isinstance(json_data['jobLocation'], dict):
            if isinstance(json_data['jobLocation']['address'], list):
                al = json_data['jobLocation']['address'][0][val] or ""
                ac = json_data['jobLocation']['address'][0]['addressCountry'] or ""
            if isinstance(json_data['jobLocation']['address'], dict):
                al = json_data['jobLocation']['address'][val] or ""
                ac = json_data['jobLocation']['address']['addressCountry'] or ""
        logging.info(
            f'{datetime.datetime.now()} Existing the location extract for other urls Module')
        return al + ", "+ac
    else:
        return False


def url_extract(response, considerations):
    logging.info(
        f'{datetime.datetime.now()} Entered the url extract for other urls Module')
    con = {}
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    main_content = soup.find("div", class_="location")
    content = soup.find("script", type="application/ld+json")
    cont = soup.find("div", id="content")
    cons = soup.find("script", id="data-job")
    co = soup.find("span", class_="js-primary-location")
    location = None
    if main_content is not None:
        location = main_content.text
    if content is not None and location is None:
        json_data = json.loads(content.text, strict=False)
        if "jobLocation" in json_data:
            location = extract_location(json_data)
            if location is False:
                location_div = soup.find(
                    'div', {'class': 'fields-data_value', 'itemprop': 'jobLocation'})
                location = location_div.get_text(
                    strip=True) if location_div else 'Location not found'
    if cons is not None and location is None:
        json_data = json.loads(cons.text, strict=False)
        if "location" in json_data:
            location = json_data['location']['name']
    if co is not None and location is None:
        location = co.text
    if cont is not None and len(cont.text) <= 1 and location is None:
        location = "Posting Closed"
    if location is None:
        location = "Posting Site"
    for i in considerations:
        if i == 'location':
            con[i] = location
        else:
            con[i] = string_search(response, globals()[i])
    logging.info(
        f'{datetime.datetime.now()} Existing the location extract for other urls Module with considerations {con}')
    return con


def redirect_url_extract(url):
    logging.info(
        f'{datetime.datetime.now()} Entered the redirect url extract Module with url {url}')
    matchjid = url.split('/')
    jid = matchjid[-1]
    parsed_url = urllib.parse.urlparse(url)
    matchcn = parsed_url.path.split('/')
    cn = matchcn[1]
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    encoded_url = urllib.parse.quote(base_url, safe='')
    path = f"embed/job_app?for={cn}&token={jid}&b={encoded_url}"
    parsed_url = parsed_url._replace(path=path)
    res = requests.get(parsed_url.geturl())
    if res.ok:
        logging.info(
            f'{datetime.datetime.now()} Existing the redirect url extract Module with url {parsed_url.geturl()}')
        return parsed_url.geturl()
    else:
        logging.info(
            f'{datetime.datetime.now()} Existing the redirect url extract Module with url {url}')
        return url


def oracle_extract(url, considerations):
    logging.info(
        f'{datetime.datetime.now()} Entering the oracle extract Module with url {url}')
    con = {}
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    content = soup.find("script").text
    patternsn = r"siteNumber:\s*'([^']+)'"
    matchsn = re.search(patternsn, content)
    if matchsn:
        site_number = matchsn.group(1)
    patternjid = r"/job/(\d+)"
    matchjid = re.search(patternjid, url)

    if matchjid:
        jid = matchjid.group(1)
        end_position = url.find('.com') + 4  # +4 to include '.com'
        base_url = url[:end_position]

        req_url = base_url+"/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&onlyData=true&finder=ById;Id=%22" + \
            jid+"%22,siteNumber="+site_number
        response = requests.get(req_url)
        html_content = response.text
        jresp = json.loads(html_content, strict=False)
    for i in considerations:
        if i == "location":
            if is_valid_json(html_content):
                if jresp["items"]:
                    con[i] = jresp["items"][0]["PrimaryLocation"]
                else:
                    con[i] = "Posting Closed"
            else:
                con[i] = "Posting Site"
        else:
            con[i] = string_search(response, globals()[i])
    logging.info(
        f'{datetime.datetime.now()} Existing the oracle extract Module with considerations {con}')
    return con


def workday_extract(response, considerations):
    logging.info(
        f'{datetime.datetime.now()} Entering the workday extract Module')
    con = {}
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    content = soup.find("script").text
    meta_tag = soup.find('meta', attrs={'name': 'title'})
    if meta_tag is not None:
        cont = meta_tag.get('content')
    else:
        for i in considerations:
            if i == "location":
                con[i] = "Posting Site"
            else:
                con[i] = False
        logging.info(
            f'{datetime.datetime.now()} Existing the workday extract Module with consideration {con}')
        return con
    for i in considerations:
        if i == "location":
            if is_valid_json(content):
                jresp = json.loads(content, strict=False)
                if 'jobLocation' in jresp:
                    con[i] = jresp['jobLocation']['address']['addressLocality'] + \
                        ", "+jresp['jobLocation']['address']['addressCountry']
                else:
                    con[i] = "Posting Closed"
            elif cont is None:
                con[i] = "Posting Closed"
            else:
                con[i] = "Posting Site"
        else:
            con[i] = string_search(response, globals()[i])
    logging.info(
        f'{datetime.datetime.now()} Existing the workday extract Module with considerations {con}')
    return con


def microsoft_extract(url, considerations):
    logging.info(
        f'{datetime.datetime.now()} Entering the microsoft extract Module with url {url}')
    con = {}
    response = requests.get(url)
    if response.ok:
        mir_url = "https://gcsservices.careers.microsoft.com/search/api/v1/job/"
        patternjid = r"/job/(\d+)"
        matchjid = re.search(patternjid, url)
        if matchjid:
            jid = matchjid.group(1)
            req_url = mir_url+jid
            respo = requests.get(req_url)
            cont = respo.text
            jsresp = json.loads(cont, strict=False)
            if jsresp['operationResult']['result']['posted'] is not None:
                for i in considerations:
                    if i == "location":
                        con[i] = jsresp['operationResult']['result']['primaryWorkLocation']['city']+", " + \
                            jsresp['operationResult']['result']['primaryWorkLocation']['state']+", " + \
                            jsresp['operationResult']['result']['primaryWorkLocation']['country']
                    else:
                        con[i] = string_search(response, globals()[i])
                logging.info(
                    f'{datetime.datetime.now()} Existing the oracle extract Module with considerations {con}')
                return con
            else:
                for i in considerations:
                    if i == "location":
                        con[i] = "Posting Closed"
                    else:
                        con[i] = False
                logging.info(
                    f'{datetime.datetime.now()} Existing the oracle extract Module with considerations {con}')
                return con
        else:
            for i in considerations:
                if i == "location":
                    con[i] = "Posting Site"
                else:
                    con[i] = False
            logging.info(
                f'{datetime.datetime.now()} Existing the oracle extract Module with considerations {con}')
            return con


def normalize_string(input_string):
    return input_string.strip().lower()


def get_country_from_place_nominatim(place_string):
    """
    Geocode the place string using Nominatim to get the country name.
    """
    logging.info(
        f'{datetime.datetime.now()} Entered the get country Module with place {place_string}')
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place_string,
        "format": "json",
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "YourAppName/1.0"
    }
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            max_dict = max(data, key=lambda x: x.get('importance'))
            address = max_dict.get('address', {})
            logging.info(
                f'{datetime.datetime.now()} Existing the get country Module with country {address}')
            return address.get('country')
    logging.info(
        f'{datetime.datetime.now()} Existing the get country Module with no country found')
    return None


def is_place_in_country(place_string, country_string):
    logging.info(
        f'{datetime.datetime.now()} Entering the country check Module')
    normalized_place = normalize_string(place_string)
    normalized_country = normalize_string(country_string)
    norm_country = normalize_string(place_string.split(',')[-1])
    place_country = get_country_from_place_nominatim(normalized_place)
    pl_country = get_country_from_place_nominatim(norm_country)
    if "remote" in normalized_place:
        if normalized_country in normalized_place:
            logging.info(
                f'{datetime.datetime.now()} Existing the country check Module with country found and valid')
            return True
        else:
            logging.info(
                f'{datetime.datetime.now()} Existing the country check Module with country not found but remote place')
            return "Remote but location not found"
    elif "posting site" in normalized_place:
        logging.info(
            f'{datetime.datetime.now()} Existing the country check Module with a posting website')
        return "Posting Website"
    elif place_country:
        normalized_place_country = normalize_string(place_country)
        logging.info(
            f'{datetime.datetime.now()} Existing the country check Module with country found and valid')
        return normalized_place_country == normalized_country
    elif pl_country:
        normalized_place_country = normalize_string(pl_country)
        logging.info(
            f'{datetime.datetime.now()} Existing the country check Module with country found and valid')
        return normalized_place_country == normalized_country
    elif normalized_country in normalized_place:
        logging.info(
            f'{datetime.datetime.now()} Existing the country check Module with country found and valid')
        return True
    else:
        logging.info(
            f'{datetime.datetime.now()} Existing the country check Module with country not found')
        return False


def xlsx_gen(df):
    date = datetime.date.today()
    today = date.strftime("%d%b%y")
    datatoexcel = pd.ExcelWriter(f'Job_Hunt.xlsx')
    df.to_excel(datatoexcel, index=False)
    datatoexcel.close()
    return True


def compute(url_list, considerations):
    logging.info(f'{datetime.datetime.now()} Entered the Compute Module')
    final_df = pd.DataFrame()
    for url in url_list:
        logging.info(
            f'{datetime.datetime.now()} Entered the Url List loop for url {url}')
        response = requests.get(url)
        redirect_url = response.url
        original_url = url
        if redirect_url != url:
            url = redirect_url_extract(url)
        response = requests.get(url)
        if response.ok:
            ul = {}
            ul['URL'] = original_url
            if "oraclecloud" in url:
                # print("oracle", url)
                con = oracle_extract(url, considerations)
            elif "myworkday" in url:
                # print("myworkday", url)
                con = workday_extract(response, considerations)
            elif "microsoft" in url:
                # print("microsoft", url)
                con = microsoft_extract(url, considerations)
            else:
                # print("other", url)
                con = url_extract(response, considerations)
            for i in considerations:
                ul[i] = con[i]
            df = pd.DataFrame([ul])
            final_df = pd.concat([final_df, df], ignore_index=True)
    logging.info(f'{datetime.datetime.now()} Existing the compute Module')
    return final_df


def filterings(final_df, considerations, location, filtering):
    logging.info(f'{datetime.datetime.now()} Entered the filtering Module')
    filtered_df = final_df.copy()
    if filtering:
        for j in considerations:
            if j == 'location':
                filtered_df['location_match'] = filtered_df['location'].apply(
                    lambda x: is_place_in_country(x, location))
                filtered_df = filtered_df.query(
                    'location_match != False')
            else:
                filtered_df = filtered_df.query(f'{j} == False')
        # removing not required columns
        filtered_df.rename({'location_match': 'comments'},
                           axis=1, inplace=True)
        filtered_df.loc[filtered_df['comments'] ==
                        True, 'comments'] = "location matched"
        for j in considerations:
            filtered_df = filtered_df.drop(columns=[f'{j}'])
    filtered_df['Role'] = " "
    filtered_df['Status'] = " "
    filtered_df['username/email'] = " "
    filtered_df['Password'] = " "
    filtered_df['Applied Date'] = " "
    filtered_df
    logging.info(f'{datetime.datetime.now()} Existing the filtering Module')
    return filtered_df


def url_generator(data):
    logging.info(f'{datetime.datetime.now()} Entered the url_generator module')
    url_list = []
    if data['exclusion'] != "":
        exclue = ["-"+i for i in data['exclusion'].split(' ')]
        excluded = " ".join(exclue)
    else:
        excluded = data['exclusion']
    for i in data['search_sites']:
        query = data['keywords']+" "+excluded+" '"+data['role']+"' "+i
        logging.info(f'{datetime.datetime.now()} executing the query {query}')
        for j in search(query, tld="co.in", num=10, stop=data['no_of_hits'], pause=2, tbs=time[data['time_filter']]):
            url_list.append(j)
    url_list = language_adjustments(url_list)
    logging.info(
        f'{datetime.datetime.now()} Leaving the url_generator module with urls {url_list}')
    return url_list


def logfile_empty():
    open('search.log', 'w').close()


def process_data(data):
    try:
        logfile_empty()
        data, considerations = initializations(data)
        url_list = url_generator(data)
        if not url_list:
            return "No search results were found and please change the parameters to generate output"
        else:
            final_df = compute(url_list, considerations)
            filtered_df = filterings(
                final_df, considerations, data['location'], data['filtering'])
            if filtered_df.empty:
                return "No data found after filtering please change the parameters to generate output"
            else:
                file_generated = xlsx_gen(filtered_df)
                if file_generated:
                    print("file generated")
                return True
    except Exception as e:
        logging.error(f"{datetime.datetime.now()} Error in main: {e}")
        return "Error while processing will be fixed soon!!"
