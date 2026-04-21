from flask import Flask, request, render_template, send_file
from bot import admin_check_url

import threading
import csv
import os
import re


app = Flask(__name__)

WAREHOUSE_DIR = "db"
HOST = os.environ.get("ANSIBLE_DEPLOY_DOMAIN_NAME", "127.0.0.1:5000")
GOOD_URL_PATTERN = re.compile(fr"^https?://{HOST}/.*$")
FORBIDDEN_CHARS = {"<",">"}

@app.route('/')
def home():
	return render_template("index.html")

@app.route("/inventory")
def inventory():
	warehouse = request.args.get("warehouse")
	if warehouse:
		if not FORBIDDEN_CHARS.isdisjoint(warehouse):
			return render_template("inventory.html", message="Unauthorized characters !")
		inventory = get_inventory(warehouse)
		return render_template("inventory.html", warehouse=warehouse, inventory=inventory)
	else:
		return render_template("inventory.html")

@app.route("/inventory/export", methods=["POST"])
def export():
	warehouse = request.form.get("warehouse")
	if warehouse:
		inventory = get_inventory(warehouse)
		if inventory is not None:
			return send_file(f"{WAREHOUSE_DIR}/{warehouse}.csv", as_attachment=True, download_name=f"{warehouse}.csv")
	return render_template("inventory.html")

@app.route("/report", methods=["GET","POST"])
def report():
	message = ""
	if request.method == 'POST':
		url = request.form.get("url")
		if is_ok_url(url):
			t = threading.Thread(target=admin_check_url, args=(url,))
			t.daemon = True
			t.start()
			message = "Thanks for your feedback !"
		else:
			message = "This isn't my website !"
	return render_template('report.html', message=message)

def get_inventory(warehouse):
	filename = f"{warehouse}.csv"
	if filename in os.listdir(WAREHOUSE_DIR):
		with open(f"{WAREHOUSE_DIR}/{filename}") as f:
			csv_reader = csv.DictReader(f)
			inventory = []
			for row in csv_reader:
				inventory.append(row)
		return inventory
	else:
		return None

def is_ok_url(url):
	return re.search(GOOD_URL_PATTERN, url)


if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000)