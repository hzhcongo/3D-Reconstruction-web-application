from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
import os
from os import listdir
import sys
from datetime import datetime
import logging
import osmbundler
import osmpmvs
import osmcmvs
import pyexiv2
from fractions import Fraction
import numpy as np
from sklearn.neighbors import KDTree
import subprocess
from flask_debugtoolbar import DebugToolbarExtension

logging.basicConfig(level=logging.INFO, format="%(message)s")


app = Flask(__name__)
app.debug = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = '123456'
toolbar = DebugToolbarExtension(app)
bootstrap = Bootstrap(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/upload", methods = ['POST'])
def upload():
	timestampfilename= (datetime.utcnow() - datetime(1970,1,1)).total_seconds()
	print(timestampfilename)
	beginTime = datetime.utcnow()
	sys.stdout.flush()
	target = os.path.join(APP_ROOT, 'images/'+str(timestampfilename)+'/')

	if not os.path.isdir(target):
		os.mkdir(target)

	for file in request.files.getlist("file"):
		filename = file.filename
		destination = "/".join([target, filename])
		file.save(destination)
		#prepare meta data for each picture as OsmBundler requires it
		metadata = pyexiv2.ImageMetadata(destination)
		metadata.read()
		metadata['Exif.Image.FocalLength'] = Fraction(4150,1000)
		metadata['Exif.Image.Make'] = 'Iphone'
		metadata['Exif.Image.Model'] = 'Iphone 6'
		metadata.write()

	# initialize OsmBundler manager class
	workaddress = str(target)+'temp/'
	manager = osmbundler.OsmBundler(target,workaddress)

	_time = datetime.utcnow()
	manager.preparePhotos()
	print("Finish preparing photos, time taken ", (datetime.utcnow() -_time).total_seconds())
	sys.stdout.flush()
	_time = datetime.utcnow()

	manager.matchFeatures()
	print("Finish matching features, time taken ", (datetime.utcnow() -_time).total_seconds())
	sys.stdout.flush()
	_time = datetime.utcnow()

	manager.doBundleAdjustment()
	print("Finish bundleadjustment, time taken ",  (datetime.utcnow() -_time).total_seconds())
	sys.stdout.flush()
	_time = datetime.utcnow()


	# manager.openResult()

	# initialize OsmPMVS manager class
	pmvsmanager = osmpmvs.OsmPmvs(workaddress)
	# cmvsmanager = osmcmvs.OsmCmvs(workaddress)
	# initialize PMVS input from Bundler output
	pmvsmanager.doBundle2PMVS()
	# cmvsmanager.doBundle2PMVS()
	
	print("Finish bundle2PMVS, time taken ", (datetime.utcnow() -_time).total_seconds())
	sys.stdout.flush()
	_time = datetime.utcnow()


	# call CMVS
	# cmvsmanager.doCMVS()
	# call PMVS
	pmvsmanager.doPMVS()
	print("Finish doPMVS, time taken ", (datetime.utcnow() -_time).total_seconds())
	sys.stdout.flush()
	_time = datetime.utcnow()

	# do noise removal by KNN

	def isfloat(value):
		try:
			float(value)
			return True
		except:
			return False

	f = open(workaddress+"pmvs/models/pmvs_options.txt.ply","r")
	points = []
	# a1 = []
	# a2 = []
	# a3 = []
	
	for line in f:
		words = line.split()
		if(isfloat(words[0])):
			points.append([float(words[0]),float(words[1]),float(words[2])])
			# a1.append(float(words[0]))
			# a2.append(float(words[1]))
			# a3.append(float(words[2]))

	f.close()

	points = np.array(points)
	# a1 = np.array(a1)
	# a2 = np.array(a2)
	# a3 = np.array(a3)
	# x_center = (np.amax(points, axis=0) - np.amin(points, axis=0))/2
	# y_center = (np.amax(points, axis=1) - np.amin(points, axis=1))/2
	# z_center = (np.amax(points, axis=2) - np.amin(points, axis=2))/2
	# a1upper = np.percentile(a1,98)
	# print("98 percentile for a1 is", a1upper)
	# a2upper = np.percentile(a2,98)
	# print("98 percentile for a2 is", a2upper)
	# a3upper = np.percentile(a3,98)
	# print("98 percentile for a3 is", a3upper)

	# a1lower = np.percentile(a1,2)
	# print("2 percentile for a1 is", a1lower)
	# a2lower = np.percentile(a2,2)
	# print("2 percentile for a2 is", a2lower)
	# a3lower = np.percentile(a3,2)
	# print("2 percentile for a3 is", a3lower)

	tree = KDTree(points, leaf_size = 50)

	distance = []
	for x in points:
		dist, ind = tree.query([x], k=200)
		distance.append(np.average(dist))
	distance = np.array(distance)
	upper = np.percentile(distance,80)

	indToRemove = []
	for x in range(len(distance)):
		if(distance[x]>upper):
			indToRemove.append(x)

	nf = open(workaddress+"pmvs/models/trim.ply", "w+")
	f = open(workaddress+"pmvs/models/pmvs_options.txt.ply","r")
	newLen = len(distance) -len(indToRemove)
	removeCount = 0
	lineCount = -1
	for line in f:
		words = line.split()
		if(words[0] == "element"):
			nf.write(words[0]+" "+words[1]+" "+str(newLen)+"\n")
			continue
		if(words[0] == "property" and words[1] == "uchar" and words[2] == "diffuse_red"):
			nf.write(words[0]+" "+words[1]+" "+"red\n")
			continue
		if(words[0] == "property" and words[1] == "uchar" and words[2] == "diffuse_green"):
			nf.write(words[0]+" "+words[1]+" "+"green\n")
			continue
		if(words[0] == "property" and words[1] == "uchar" and words[2] == "diffuse_blue"):
			nf.write(words[0]+" "+words[1]+" "+"blue\n")
			continue
		if(isfloat(words[0])):
			lineCount+=1
			if(removeCount < len(indToRemove) and lineCount == indToRemove[removeCount]):
				removeCount+=1
				# print("trim point")
				continue
		nf.write(line)
	nf.close()
	f.close()

	print("Finish noiseRemoval, time taken ", (datetime.utcnow() -_time).total_seconds())
	sys.stdout.flush()
	_time = datetime.utcnow()

	# distrPath = os.path.dirname( os.path.abspath(sys.argv[0]) )
	possoinExecutable = os.path.join(APP_ROOT, "software/PoissonRecon.exe")
	surfaceTrimmer = os.path.join(APP_ROOT, "software/SurfaceTrimmer.exe")
	subprocess.call([possoinExecutable, "--in", workaddress+"pmvs/models/trim.ply", "--out", workaddress+"pmvs/models/mesh.ply", "--depth", "12", "--color", "100", "--pointWeight","0", "--density"])
	subprocess.call([surfaceTrimmer, "--in", workaddress+"pmvs/models/mesh.ply", "--out", workaddress+"pmvs/models/trimmed_mesh.ply", "--trim", "7", "--smooth", "5"])

	print("Finish mesh construction, time taken ", (datetime.utcnow() -_time).total_seconds())
	print("Total time taken ",  (datetime.utcnow() -beginTime).total_seconds())
	sys.stdout.flush()

	return redirect(url_for('fileUpload'))

@app.route("/fileUpload")
def fileUpload():
	return render_template("fileUpload.html")

@app.route("/edit/")
@app.route("/edit/<name>")
def edit(name = None):
	modelFolder = os.path.join(APP_ROOT, 'static/model/')
	# meshFiles = [f for f in listdir(modelFolder)]
	data = []
	for f in listdir(modelFolder):
		# print(f, jsonify({'filename' : f}))
		# sys.stdout.flush()
		path = os.path.join(modelFolder, f)
		info = os.stat(path)
		filename = f[:-4]
		data.append({'filename' : filename, 'creation_time' : datetime.fromtimestamp(info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'), 'modification_time' : datetime.fromtimestamp(info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'), 'file_size' : info.st_size/1024})
	print(data)
	sys.stdout.flush()
	return render_template("edit.html", name=name, data = data)

@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html")

@app.route("/display/")
@app.route("/display/<name>")
def display(name = None):
	return render_template("display.html", name=name)

# @app.route("/fullmoontest/")
# def fullmoontest():
# 	return render_template("fullmoontest.html");

if __name__ == "__main__":
	app.run(host= '0.0.0.0')
	# app.run()