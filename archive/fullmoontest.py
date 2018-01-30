from flask import Flask, render_template, request, redirect, url_for, jsonify
import sys

app = Flask(__name__)

phase = 0
countdown = 25

@app.route("/getCountDown")
def getCountDown():
	return jsonify(countdown);

@app.route("/getPhase")
def getPhase():
	return jsonify(phase);

@app.route("/movePhase", methods = ['POST'])
def movePhase():
	global phase
	identity = request.form['identity']
	print(identity)
	sys.stdout.flush()
	if(identity == "detective"):
		phase += 1
	return jsonify("success");

@app.route("/reset", methods = ['POST'])
def resetGame():
	global phase
	identity = request.form['identity']
	print(identity)
	sys.stdout.flush()
	if(identity == "detective"):
		phase = 0
	return jsonify("success");


if __name__ == "__main__":
	# app.run(host= '0.0.0.0')
	app.run(debug=True)