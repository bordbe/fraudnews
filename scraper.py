from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from retry import retry
import pandas as pd
from datetime import datetime, timedelta
import os
from datetime import datetime


def set_driver():
    """set up selenium webdriver

    Args:
        path (string): path to chromedriver

    Returns:
        webdriver: selenium webdriver with options
    """
    options = Options()
    os.environ['WDM_LOG'] = "false"
    options.add_argument("--headless")  # Runs Chrome in headless mode.
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("disable-infobars")
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(ChromeDriverManager(log_level=0).install(), options=options, service_log_path=os.devnull)


@retry(IndexError, delay=5, tries=2)
def parse_news(driver):
    today = datetime.today()
    last_close = datetime.strftime(
        today - timedelta(days=1), "%Y-%m-%d") + " " + "17:30"
    last_close = datetime.strptime(last_close, "%Y-%m-%d %H:%M")
    find_elem = False
    scroll_from = 0
    days_to_subtract = 0
    scroll_limit = 3000
    morning = True if datetime.now().hour < 12 else False
    while not find_elem:
        news_list = driver.find_element(By.CLASS_NAME, "news-list")
        news = news_list.find_elements(By.TAG_NAME, 'a')
        last_news_date = news[-1].text.split('\n')[0]
        driver.execute_script("window.scrollTo(%d, %d);" %
                              (scroll_from, scroll_from+scroll_limit))
        scroll_from += scroll_limit
        try:
            if morning and "PM" in last_news_date:
                days_to_subtract += 1
            morning = True if "AM" in last_news_date else False
            last_news_date = datetime.strptime(last_news_date, '%I:%M %p')
            day = today - timedelta(days=days_to_subtract)
            last_news_date = datetime.strftime(day, "%Y-%m-%d") + " " + str(
                last_news_date.hour) + ":" + str(last_news_date.minute).zfill(2)
            last_news_date = datetime.strptime(
                last_news_date, "%Y-%m-%d %H:%M")
            if last_news_date < last_close:
                find_elem = True
        except:
            pass
    return news


def get_overnight_news():
    driver = set_driver()
    driver.get("https://stocklabs.com/news")
    news = parse_news(driver)
    news = [title.text for title in news]
    news_splitted = []
    for title in news:
        try:
            # remove timeline from each news
            news_splitted.append(title.split('\n')[1])
        except:
            continue
    driver.quit()
    #save in df
    return pd.DataFrame(news_splitted, columns=["text"])
