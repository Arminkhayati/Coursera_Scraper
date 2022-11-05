from config import BASE_URL, SAVE_DIR, USER_AGENTS
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import re
import random
import time


def fetch_courses_by(category, csv_file_name):
    """
    Returns courses link, title, enroll_count, provider, num_ratings, and description within given category
    :param category: Category of the desired courses, e.g. /browse/data-science
    :return: Dataframe of links and titles within given category
    """
    user_agent = random.choice(USER_AGENTS)
    headers = {'User-Agent': user_agent}
    response = requests.get(BASE_URL + category, headers=headers)
    html_soup = BeautifulSoup(response.content, 'html.parser')
    html_courses = html_soup.findAll("a", "CardText-link")
    while not html_courses:
        time.sleep(2.5)
        user_agent = random.choice(USER_AGENTS)
        headers = {'User-Agent': user_agent}
        response = requests.get(BASE_URL + category, headers=headers)
        html_soup = BeautifulSoup(response.content, 'html.parser')
        html_courses = html_soup.findAll("a", "CardText-link")

    courses = {"link": [], "title": [], "enroll_count": [], "provider": [], "num_ratings": [], "description": []}
    for i, c in enumerate(html_courses):
        # print(i)
        link = BASE_URL + c["href"]
        courses["link"].append(link)
        courses["title"].append(c.getText())
        enroll_count, provider, num_ratings, description = get_course_details(link)
        courses["enroll_count"].append(enroll_count)
        courses["provider"].append(provider)
        courses["num_ratings"].append(num_ratings)
        courses["description"].append(description)

    csv_file = os.path.join(SAVE_DIR, csv_file_name)
    pd.DataFrame(courses).to_csv(csv_file, index=False)
    return csv_file


def course_category_decoder(idx):
    if idx == "1":
        return "/browse/data-science"
    elif idx == "2":
        return "/browse/business"
    elif idx == "3":
        return "/browse/computer-science"
    elif idx == "4":
        return "/browse/personal-development"
    elif idx == "5":
        return "/browse/information-technology"
    elif idx == "6":
        return "/browse/language-learning"
    elif idx == "7":
        return "/browse/health"
    elif idx == "8":
        return "/browse/math-and-logic"
    elif idx == "9":
        return "/browse/social-sciences"
    elif idx == "10":
        return "/browse/physical-science-and-engineering"
    elif idx == "11":
        return "/browse/arts-and-humanities"


def get_course_details(course_url):
    user_agent = random.choice(USER_AGENTS)
    headers = {'User-Agent': user_agent}
    response = requests.get(course_url, headers=headers)
    html_soup = BeautifulSoup(response.content, 'html.parser')
    title = html_soup.findAll("h1", "banner-title")
    if not title:
        title = html_soup.findAll("h1", {"id": "programMiniModalName"})
    skip = False
    count_try = 0
    while (response.status_code == 200) and (not title):
        if count_try > 10:
            skip = True
            break
        time.sleep(2.5)
        # print(course_url, " - code:", response.status_code)
        user_agent = random.choice(USER_AGENTS)
        headers = {'User-Agent': user_agent}
        response = requests.get(course_url, headers=headers)
        html_soup = BeautifulSoup(response.content, 'html.parser')
        title = html_soup.findAll("h1", "banner-title")
        if not title:
            title = html_soup.findAll("h1", {"id": "programMiniModalName"})
        count_try = count_try + 1


    if not skip:
        enroll_count = get_enrollment_count(html_soup)
        provider = get_provider(html_soup)
        num_ratings = get_num_ratings(html_soup)
        description = get_description(html_soup)
        # print(course_url, enroll_count, provider, num_ratings)
        return enroll_count, provider, num_ratings, description
    else:
        # print(course_url, " - code:", response.status_code)
        return "0","---","0","---"


def get_description(soup):
    # css-6ohxmr
    description = soup.findAll("div", "description")
    if description:
        description = description[0].getText()
        return description
    else:
        description = soup.findAll("div", "css-6ohxmr")
        if description:
            description = description[0].getText()
            return description
        else:
            return "---"


def get_num_ratings(soup):
    num_ratings = soup.findAll("span", {"data-test": "ratings-count-without-asterisks"})
    if num_ratings:
        num_ratings = num_ratings[0]
        num_ratings = re.sub('[^0-9,]', "", num_ratings.getText()).replace(",", "")
        return num_ratings
    else:
        return "0"


def get_provider(soup):
    #
    provider = soup.findAll("a", {"data-click-key": "xdp_v1.xdp.click.partner_name"})
    if provider:
        provider = [p.getText() for p in provider]
        provider = " & ".join(provider)
        return provider
    else:
        provider = soup.findAll("h3", {"class": "rc-Partner__title"})
        provider = [p.getText() for p in provider]
        provider = " & ".join(provider)
        return provider

def get_enrollment_count(soup):
    enroll_count = soup.findAll("div", "_1fpiay2")
    if enroll_count:
        enroll_count = enroll_count[0]
        enroll_count = re.sub('[^0-9,]', "", enroll_count.getText()).replace(",", "")
        return enroll_count
    else:
        return "0"
