import os
import requests
from lxml import html

USERNAMES = os.environ["PA_USERNAME"].split(',')
PASSWORDS = os.environ["PA_PASSWORD"].split(',')
BASE_URL = "https://www.pythonanywhere.com"

def extend_webapps(username, password):
    client = requests.Session()

    print("GET login page...")
    login_page = client.get(BASE_URL + "/login/")
    tree = html.fromstring(login_page.text)
    
    if "csrfmiddlewaretoken" not in login_page.text:
        print("Error: Could not find CSRF token.")
        exit(1)

    csrf_token = tree.xpath('//input[@name="csrfmiddlewaretoken"]/@value')[0] 

    payload = {
        'csrfmiddlewaretoken': csrf_token,
        'auth-username': username,
        'auth-password': password,
        'login_view-current_step': 'auth'
    }
    
    print(f"Logging in as {username}...")
    headers = {'Referer': BASE_URL + "/login/"}
    response = client.post(BASE_URL + "/login/", data=payload, headers=headers)

    if "Log out" not in response.text:
        print("Login failed! Check credentials.")
        exit(1)
    
    print("Login successful.")
    
    dashboard_tree = html.fromstring(response.text)
    web_url = dashboard_tree.xpath('//a[@id="id_web_app_link"]/@href')[0]

    print(f"Visiting: {BASE_URL + web_url}")
    extend_page = client.get(BASE_URL + web_url)
    extend_tree = html.fromstring(extend_page.text)

    print("Extending web apps...")
    extend_forms = extend_tree.xpath('//form[contains(@action, "/extend")]')

    if not extend_forms:
        print("No extendable apps found (or they are already running).")
    else:
        for form in extend_forms:
            action_url = form.get("action")
            if not action_url.startswith("http"):
                action_url = BASE_URL + action_url
            csrf_token = form.xpath('.//input[@name="csrfmiddlewaretoken"]/@value')[0]
            
            print(f"Extending app at: {action_url}")
            
            response = client.post(action_url, data={
                "csrfmiddlewaretoken": csrf_token
            }, headers={"Referer": BASE_URL + web_url})

            if response.status_code != 200:
                print(f"Failed to extend app at: {action_url}")
                print(f"Response: {response.text}")
            else:
                print(f"Successfully extended app at: {action_url}")
                
if __name__ == "__main__":
    for username, password in zip(USERNAMES, PASSWORDS):
        extend_webapps(username, password)