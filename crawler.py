from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import sqlite3
import json
import sys
UT_SCHOOL_ID = "13814"
LINKEDIN_BASE_URL = 'https://linkedin.com/'
LINKEDIN_MY_EMAIL = 'alitoumob@gmail.com'
LINKEDIN_MY_PASSWORD = 'aliali'

db = sqlite3.connect('database.db', check_same_thread=False, isolation_level=None)
dbcursor = db.cursor()

dbcursor.execute('''CREATE TABLE IF NOT EXISTS Data
                  (
                  name text,
                  experiences text,
                  educations text,
                  people_also_viewed text,
                  location text,
                  skills text,
                  interests text,
                  accomplishments text
                  )''')

fp = webdriver.FirefoxProfile()
fp.set_preference("browser.tabs.remote.autostart", False)
fp.set_preference("browser.tabs.remote.autostart.1", False)
fp.set_preference("browser.tabs.remote.autostart.2", False)

driver = webdriver.Firefox(fp)


def login():
    """
    Goes to LinkedIn main page
    Finds username and password fields
    Fills them with default values
    Logs In
    """
    driver.get(LINKEDIN_BASE_URL)
    user_field = driver.find_element_by_xpath("""/html/body\
    /div[@id="application-body"]/main[@id="layout-main"]/div[@class="global-wrapper artdeco-a"]\
    /div[@class="header"]/div[@class="wrapper"]/form[@class="login-form"]/input[@class="login-email"]""")

    password_field = driver.find_element_by_xpath("""/html/body\
    /div[@id="application-body"]/main[@id="layout-main"]/div[@class="global-wrapper artdeco-a"]\
    /div[@class="header"]/div[@class="wrapper"]/form[@class="login-form"]/input[@class="login-password"]""")

    # Login
    user_field.send_keys(LINKEDIN_MY_EMAIL)
    password_field.send_keys(LINKEDIN_MY_PASSWORD)
    password_field.send_keys(Keys.ENTER)


def get_items(elements):
    r = []
    for item in elements:
        interest = item.text
        r.append(interest)
    return r


def click_on_show_more_button():
    try:
        skill_show_more_button = driver\
            .find_element_by_xpath("""//button[contains(@data-control-name, "skill_details")]""")
        skill_show_more_button.click()
        sleep(0.2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.2)
    except Exception as e:
        print(e, file=sys.stderr)


def get_experiences(experiences_elem):
    r = []
    try:
        for experience_elem in experiences_elem:
            title = experience_elem \
                .find_element_by_xpath("""//a[contains(@data-control-name, "background_details_company")]//h3""") \
                .text

            at = experience_elem \
                .find_element_by_xpath("""//span[contains(@class, "pv-entity__secondary-title")]""") \
                .text

            dates = str(
                experience_elem
                .find_element_by_xpath("""//h4[contains(@class, "pv-entity__date-range")]""")
                .find_elements_by_tag_name("span")[1]
                .text
                        )
            dates = dates.replace('\u2013', '-')
            new_exp = {
                'title': title,
                'at': at,
                'dates': dates
            }
            r.append(new_exp)
    except Exception as e:
        print(e, file=sys.stderr)
    finally:
        return r


def get_accomplishments(accomplishments_elem):
    r = {}
    try:
        for accomplishment_category in accomplishments_elem:
            category = accomplishment_category \
                .find_element_by_xpath("""//h3[contains(@class, "pv-accomplishments-block__title")]""").text
            accs_elem = accomplishment_category \
                .find_elements_by_xpath("""//ul[contains(@class, "pv-accomplishments-block__summary-list")]\
                //li[contains(@class, "pv-accomplishments-block__summary-list-item")]""")

            accs = get_items(accs_elem)

            r[category] = accs
    except Exception as e:
        print(e, file=sys.stderr)
    finally:
        return r


def get_also_viewed(also_viewed_elem):
    r = []
    try:
        for item in also_viewed_elem:
            link = item.get_attribute("href")
            r.append(link)
    except Exception as e:
        print(e, file=sys.stderr)
    finally:
        return r


def get_educations(educations_elem):
    r = []
    try:
        for education_elem in educations_elem:
            at = education_elem\
                .find_element_by_xpath("""//h3[contains(@class, "pv-entity__school-name")]""")\
                .text
            description = education_elem\
                .find_element_by_xpath("""//p[contains(@class, "pv-entity__secondary-title")]""")\
                .text\
                .split('\n')[1]
            dates = str(
                education_elem
                .find_element_by_xpath("""//p[contains(@class, "pv-entity__dates")]""")
                .text
                .split('\n')[1]
            )
            dates = dates.replace('\u2013', '-')
            new_edu = {
                'at': at,
                'description': description,
                'dates': dates,
            }
            r.append(new_edu)
    except Exception as e:
        print(e, file=sys.stderr)
    finally:
        return r


def store_data(link):
    """
    Opens a new tab,
    Goes to following link
    Gathers data
    Saves them in database
    Closes the tab
    """
    driver.get(link)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(0.2)
    name = driver.find_element_by_xpath("""//h1[contains(@class, "pv-top-card-section__name")]""").text

    location = driver.find_element_by_xpath("""//h3[contains(@class, "pv-top-card-section__location")]""").text

    sleep(0.2)

    experiences_elem = driver.find_elements_by_xpath("""//ul[contains(@class, "pv-profile-section__section-info")]\
//a[contains(@data-control-name, "background_details_company")]\
/div[contains(@class, "pv-entity__summary-info ")]""")

    experiences = get_experiences(experiences_elem)

    sleep(0.2)

    educations_elem = driver.find_elements_by_xpath("""//li[contains(@class, "pv-education-entity")]\
/a[contains(@data-control-name, "background_details_school")]\
/div[contains(@class, "pv-entity__summary-info")]""")

    educations = get_educations(educations_elem)

    sleep(0.2)

    also_viewed_elem = driver.find_elements_by_xpath("""//a[contains(@data-control-name, "browsemap_profile")]""")

    also_viewed = get_also_viewed(also_viewed_elem)

    sleep(0.2)

    interests_elem = driver.find_elements_by_xpath("""//li[contains(@class, "pv-interest-entity")]\
    //span[contains(@class, "pv-entity__summary-title-text")]""")

    interests = get_items(interests_elem)

    click_on_show_more_button()

    skills_elem = driver.find_elements_by_xpath("""//p[contains(@class, "pv-skill-category-entity__name")]""")

    skills = get_items(skills_elem)

    sleep(0.2)

    accomplishments_elem = driver\
        .find_elements_by_xpath("""//section[contains(@class, "pv-accomplishments-block")]""")

    accomplishments = get_accomplishments(accomplishments_elem)

    educations = json.dumps(educations)
    experiences = json.dumps(experiences)
    interests = json.dumps(interests)
    accomplishments = json.dumps(accomplishments)
    skills = json.dumps(skills)
    also_viewed = json.dumps(also_viewed)
    data = (name, experiences, educations, also_viewed, location, skills, interests, accomplishments)
    print(data)
    dbcursor.execute("""INSERT INTO Data VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", data)


login()

WebDriverWait(driver, 10).until(ec.title_is("LinkedIn"))

page_number = int(sys.argv[1]) if len(sys.argv) == 2 else 1

until_page = int(sys.argv[2]) if len(sys.argv) == 3 else page_number + 10

while page_number <= until_page:
    # print(page_number)
    url = """https://www.linkedin.com/search/results/people/?\
company=&facetSchool=%5B%22{school_id}%22%5D&firstName=&lastName=&\
origin=FACETED_SEARCH&school=&title=&page={page_number}""" \
        .format(school_id=UT_SCHOOL_ID, page_number=str(page_number))
    # print(url)
    print(driver.session_id)

    sleep(0.2)
    if page_number > 1:
        driver.switch_to.window(main_window)
        sleep(0.1)
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
        sleep(0.2)
        driver.switch_to.window(driver.window_handles[0])  # Assume new tab is in index 1
        sleep(0.2)
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
        sleep(0.2)



    driver.get(url)  # Search for UT students

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down
    sleep(0.2)

    search_results = driver.find_elements_by_xpath("""//ul[contains(@class, "results-list")]//\
    a[contains(@class, "search-result__result-link")]""")

    search_results = search_results[0::2]  # Omitting duplicate values
    links = []

    main_window = driver.current_window_handle

    for item in search_results:
        link = item.get_attribute("href")
        links.append(link)

    #  `people_also_viewed` is a list of profile URLs, in JSON formatted text.
    #  `experiences`, `educations`, `skills`, `interests`, `accomplishments`, are a list in JSON formatted text.

    # Experience Example:
    # {
    #     'title': 'Back-End Developer',
    #     'at': 'Avaanegar',
    #     'dates': 'Aug 2016-Oct 2016',
    # }

    # Education Example:
    # {
    #     'at': 'University of Tehran',
    #     'description' : 'Bsc, Computer Engineering',
    #     'dates': '2016-2020',
    # }

    for link in links:
        driver.switch_to.window(main_window)

        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
        sleep(0.2)
        driver.switch_to.window(driver.window_handles[1])  # Assume new tab is in index 1

        store_data(link)

        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')

        sleep(0.2)

        if links.index(link) > 3:
            break

    page_number += 1

driver.close()
