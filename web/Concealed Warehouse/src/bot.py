from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from os import environ

import time

SLEEP_TIME = 2

def admin_check_url(url):
	options = Options()
	options.add_argument("--headless=new")
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")
	driver = webdriver.Chrome(options=options)
	driver.get(f'http://{environ.get("ANSIBLE_DEPLOY_DOMAIN_NAME", "127.0.0.1:5000")}/')
	driver.add_cookie({"name": "flag", "value": environ.get("FLAG", "")})
	driver.get(url)
	time.sleep(SLEEP_TIME)
	driver.quit()
