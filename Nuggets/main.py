from flask import Flask, request, render_template, redirect, session, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

# libraries for automated checks
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

app.secret_key = "thisismysecretkey"

# setup secure sockets layer
'''
from OpenSSL import SSL
context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
context.use_privatekey_file('server.key')
context.use_certificate_file('server.crt')
'''

# Initialize global status variables
nuggets = False
french_toast = False

def get_food_for_url(url):
    menu_html = requests.get(url)
    # print(cc.status_code) this should be 200
    menu_parse = BeautifulSoup(menu_html.content, "html.parser")
    all_food_divs = menu_parse.findAll("span", {"class": "item__name"})
    food_divs = []
    # do not include the hidden addons that are generic whole foods
    for div in all_food_divs:
        div_string = str(div.parent.parent.parent)[0:50]
        if "menu__addOns" not in div_string:
            food_divs.append(div)
    # get the divs inside of the food name divs to get their names
    food_name_divs = []
    for div in food_divs:
        for child in div.findChildren("a", recursive=False):
            food_name_divs.append(child)
    food_names = []
    for f in food_name_divs:
        food_names.append(str(f.decode_contents()).lower())
    # return a list of strings
    return food_names

def update_status():
    cc = get_food_for_url("https://uc.campusdish.com/LocationsAndMenus/CenterCourt")
    print(cc)
    otg = get_food_for_url("https://uc.campusdish.com/LocationsAndMenus/OnTheGreen")
    global nuggets
    global french_toast
    nuggets = False
    french_toast = False
    for food in cc:
        if "nuggets" in food:
            nuggets = True
        if "french toast" in food:
            french_toast = True
    print("Status updated")

# FLASK STUFF
@app.route('/', methods=["GET"])
def hello():
    # write their ip to a file
    visitor_file = open("Visitors.txt", "a+")
    print(request.remote_addr)
    visitor_file.write(request.remote_addr + '\n')
    nug_msg = "There are not nuggets"
    frch_toast_msg = "There is not French toast"
    if nuggets:
        nug_msg = "There are nuggets"
    if french_toast:
        frch_toast_msg = "There is French toast"
    return render_template('index.html', nug_msg=nug_msg, frch_toast_msg=frch_toast_msg)

# UPDATE STATUS EVERY 30 MINUTES
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_status, trigger="interval", minutes=3)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
    update_status()