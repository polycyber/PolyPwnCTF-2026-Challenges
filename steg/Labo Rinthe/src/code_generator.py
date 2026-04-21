import uuid
import random

MAX_REDIRECTS = 20

flag = "r3d1r3cts_m4z3-9ug"

assert len(flag) + 2 <= MAX_REDIRECTS # 2 = ( / -> /begin ) + ( /<last> -> / )

CODE_PART_1 = """from flask import Flask, redirect, render_template

import json

app = Flask(__name__)

@app.route('/')
def home():
	return render_template("index.html")

"""




CODE_PART_2 = """
#### END ####

def redirect_wrap(location: str, code: int = 302, data: str|bytes = None):
	response = redirect(location, code)
	if data:
		response.set_data(data)
	return response


if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)
"""

def main():
	global CODE_PART_1, CODE_PART_1
	uuids = []
	for index, char in enumerate(flag):
		my_uuid = uuid.uuid4()
		uuids.append((index, char, str(my_uuid)))

	random.shuffle(uuids)

	for list_index, (flag_index, char, page_uuid) in enumerate(uuids):
		if list_index+1 < len(uuids):
			next_page_uuid = uuids[list_index+1][2]
		else:
			next_page_uuid = ""
		template = f"""@app.route('/{page_uuid}')
def func_{flag_index}():
	return redirect_wrap("/{next_page_uuid}", data=json.dumps({{{flag_index}:"{char}"}}))
"""
		if list_index == 0:
			CODE_PART_1 += f"""@app.route('/begin')
def begin():
	return redirect_wrap("/{page_uuid}", data="Let's go !")

#### BEGIN ####


"""
		CODE_PART_1 += template + "\n"

	return CODE_PART_1 + CODE_PART_2

if __name__ == '__main__':
	code = main()
	with open("app.py", "w") as f:
		f.write(code)
