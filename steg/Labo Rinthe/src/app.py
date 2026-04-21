from flask import Flask, redirect, render_template

import json

app = Flask(__name__)

@app.route('/')
def home():
	return render_template("index.html")

@app.route('/begin')
def begin():
	return redirect_wrap("/a6a44570-df8d-45fd-978d-81ae1cea605d", data="Let's go !")

#### BEGIN ####


@app.route('/a6a44570-df8d-45fd-978d-81ae1cea605d')
def func_13():
	return redirect_wrap("/7c8b9421-380a-4a8c-972b-d69bf51bb9eb", data=json.dumps({13:"3"}))

@app.route('/7c8b9421-380a-4a8c-972b-d69bf51bb9eb')
def func_10():
	return redirect_wrap("/872e36ad-a700-4591-a680-93506b0501cd", data=json.dumps({10:"m"}))

@app.route('/872e36ad-a700-4591-a680-93506b0501cd')
def func_12():
	return redirect_wrap("/e20ce22f-2b63-42be-884e-30453507ede8", data=json.dumps({12:"z"}))

@app.route('/e20ce22f-2b63-42be-884e-30453507ede8')
def func_17():
	return redirect_wrap("/101d4100-2366-4e1e-9ee0-338766ef6d68", data=json.dumps({17:"g"}))

@app.route('/101d4100-2366-4e1e-9ee0-338766ef6d68')
def func_7():
	return redirect_wrap("/49b9ef6b-9816-4d5a-aa68-f63ef8857b03", data=json.dumps({7:"t"}))

@app.route('/49b9ef6b-9816-4d5a-aa68-f63ef8857b03')
def func_9():
	return redirect_wrap("/21f4d0f5-ec67-474f-abb5-1db171799136", data=json.dumps({9:"_"}))

@app.route('/21f4d0f5-ec67-474f-abb5-1db171799136')
def func_6():
	return redirect_wrap("/dc606269-e9c0-4cae-ad1e-b19a2e0cf8c0", data=json.dumps({6:"c"}))

@app.route('/dc606269-e9c0-4cae-ad1e-b19a2e0cf8c0')
def func_8():
	return redirect_wrap("/8f90b753-e608-4d90-89de-b3ae0912334a", data=json.dumps({8:"s"}))

@app.route('/8f90b753-e608-4d90-89de-b3ae0912334a')
def func_2():
	return redirect_wrap("/1c62ed26-a2ff-4204-a84b-33675cd109c9", data=json.dumps({2:"d"}))

@app.route('/1c62ed26-a2ff-4204-a84b-33675cd109c9')
def func_4():
	return redirect_wrap("/37c020cb-64e2-470f-a384-e590c677490e", data=json.dumps({4:"r"}))

@app.route('/37c020cb-64e2-470f-a384-e590c677490e')
def func_11():
	return redirect_wrap("/24d192c4-21cb-4466-b148-5c241acf1533", data=json.dumps({11:"4"}))

@app.route('/24d192c4-21cb-4466-b148-5c241acf1533')
def func_1():
	return redirect_wrap("/839af201-d548-4c8c-b235-7f10a3b9a0d3", data=json.dumps({1:"3"}))

@app.route('/839af201-d548-4c8c-b235-7f10a3b9a0d3')
def func_16():
	return redirect_wrap("/53750ccc-4cb5-45a5-bbae-657c24117b92", data=json.dumps({16:"u"}))

@app.route('/53750ccc-4cb5-45a5-bbae-657c24117b92')
def func_3():
	return redirect_wrap("/8b47a1d1-8267-4bd5-a5e4-1e29510cbacc", data=json.dumps({3:"1"}))

@app.route('/8b47a1d1-8267-4bd5-a5e4-1e29510cbacc')
def func_14():
	return redirect_wrap("/95c16fb7-33e0-4741-ba67-dc28181b7828", data=json.dumps({14:"-"}))

@app.route('/95c16fb7-33e0-4741-ba67-dc28181b7828')
def func_0():
	return redirect_wrap("/f75be05d-f652-46f0-97b4-5a4985a40b1b", data=json.dumps({0:"r"}))

@app.route('/f75be05d-f652-46f0-97b4-5a4985a40b1b')
def func_5():
	return redirect_wrap("/d7052761-5de5-42ae-84d1-e3a20aa255bd", data=json.dumps({5:"3"}))

@app.route('/d7052761-5de5-42ae-84d1-e3a20aa255bd')
def func_15():
	return redirect_wrap("/", data=json.dumps({15:"9"}))


#### END ####

def redirect_wrap(location: str, code: int = 302, data: str|bytes = None):
	response = redirect(location, code)
	if data:
		response.set_data(data)
	return response


if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000)
