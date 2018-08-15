from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
import os
from os import listdir
import sys
from datetime import datetime
import logging
import osmbundler
import osmpmvs
# import osmcmvs
import pyexiv2
from fractions import Fraction
import numpy as np
from sklearn.neighbors import KDTree
import subprocess
from flask_debugtoolbar import DebugToolbarExtension
import shutil
import trimesh

logging.basicConfig(level=logging.INFO, format="%(message)s")

app = Flask(__name__)
app.debug = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = '123456'
toolbar = DebugToolbarExtension(app)
bootstrap = Bootstrap(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/upload", methods = ['POST'])
def upload():

	modelname = request.form['modelname']
	if(modelname == ''):
		modelname = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
	print("Model name: " + modelname)

	modelFolder = os.path.join(APP_ROOT, 'static/model/')
	for f in listdir(modelFolder):
		# path = os.path.join(modelFolder, f)
		filename = f[:-4]
		if(filename == modelname):
			return redirect(url_for('error', msg="Model name already exists in server. Please choose a different name or delete the old model."))

	quality = request.form['quality']
	# print("Quality: " + quality)
	#
	# timestampfilename= (datetime.now() - datetime(1970,1,1)).total_seconds()
	# print(timestampfilename)

	sys.stdout.flush()
	target = os.path.join(APP_ROOT, 'static/images/'+str(modelname)+'/')

	if not os.path.isdir(target):
		os.mkdir(target)

	# Store quality and processing stage in .txt file (1st digit = quality, 2nd digit = stage)
	completeName = os.path.join(target, "data.txt")
	saver = open(completeName, "w+")
	saver.write(quality)
	saver.write("0")
	saver.close()
	#

	if not os.path.isdir(target):
		os.mkdir(target)
		sys.stdout.flush()

	images = 0
	for file in request.files.getlist("file"):
		images = images + 1
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

	# print("Images and relevant data saved. Total images: ", images)
	sys.stdout.flush()
	return redirect(url_for('imagesets'))


@app.route("/PrepAndMatch/<name>")
def prepandmatch(name=None):
	return render_template("prepandmatch.html", name=name)


@app.route("/PrepAndMatchprocess" , methods=['GET'])
def prepandmatchprocess():
	_time = datetime.now()
	name = request.args.get('name')
	target = os.path.join(APP_ROOT, 'static/images/' + str(name) + '/')

	# initialize OsmBundler manager class
	workaddress = str(target) + 'temp/'
	manager = osmbundler.OsmBundler(target, workaddress)

	try:
		manager.preparePhotos()
		print("Finish preparing photos, time taken ", (datetime.now() - _time).total_seconds())
		sys.stdout.flush()
		_time = datetime.now()

		manager.matchFeatures()
		print("Finish matching features, time taken ", (datetime.now() - _time).total_seconds())
		sys.stdout.flush()
		_time = datetime.now()

		# update quality and processing stage in .txt file (1st digit = quality, 2nd digit = stage)
		completeName = os.path.join(target, "data.txt")
		saver = open(completeName, "r")
		savedData = saver.read()
		saver.close()
		sys.stdout.flush()

		saver = open(completeName, "w")
		saver.write(str(savedData[0]))
		saver.write("1")
		saver.close()
		sys.stdout.flush()
	#

	except AttributeError as e:
		print("AttributeError", e.message)
		return redirect(url_for('error', msg=e.message))
	except IOError as e:
		print("IOError", e.message)
		if e.message:
			return redirect(url_for('error', msg=e.message))
		else:
			return redirect(url_for('error', msg="IOError when updating or saving quality and current stage process"))
	except ValueError as e:
		print("ValueError", e.message)
		return redirect(url_for('error', msg=e.message))
	except WindowsError as e:
		print("WindowsError", e.message)
		return redirect(url_for('error',
		                        msg="A model of the same name already exists in the server. Please rename your model or delete the model with the same name"))

	return redirect(url_for('bundleadjustment', name=name))


@app.route("/BundleAdjustment/<name>")
def bundleadjustment(name=None):
	return render_template("bundleadjustment.html", name=name)


@app.route("/BundleAdjustmentprocess" , methods=['GET'])
def bundleadjustmentprocess():
	_time = datetime.now()
	name = request.args.get('name')
	target = os.path.join(APP_ROOT, 'static/images/' + str(name) + '/')

	# initialize OsmBundler manager class
	workaddress = str(target)+'temp/'
	manager = osmbundler.OsmBundler(target,workaddress)

	try:
		manager.doBundleAdjustment()
		print("Finish bundleadjustment, time taken ",  (datetime.now() -_time).total_seconds())
		sys.stdout.flush()
		_time = datetime.now()

		# initialize OsmPMVS manager class
		pmvsmanager = osmpmvs.OsmPmvs(workaddress)
		# cmvsmanager = osmcmvs.OsmCmvs(workaddress)
		# initialize PMVS input from Bundler output
		pmvsmanager.doBundle2PMVS()
		# cmvsmanager.doBundle2PMVS()

		print("Finish bundle2PMVS, time taken ", (datetime.now() -_time).total_seconds())
		sys.stdout.flush()
		_time = datetime.now()

		# update quality and processing stage in .txt file (1st digit = quality, 2nd digit = stage)
		completeName = os.path.join(target, "data.txt")
		saver = open(completeName, "r")
		savedData = saver.read()
		saver.close()
		sys.stdout.flush()

		saver = open(completeName, "w")
		saver.write(str(savedData[0]))
		saver.write("2")
		saver.close()
		sys.stdout.flush()
		#

	except AttributeError as e:
		print("AttributeError", e.message)
		return redirect(url_for('error', msg=e.message))
	except IOError as e:
		print("IOError", e.message)
		if e.message:
			return redirect(url_for('error', msg=e.message))
		else:
			return redirect(url_for('error', msg="IOError when updating or saving quality and current stage process"))
	except ValueError as e:
		print("ValueError", e.message)
		return redirect(url_for('error', msg=e.message))
	except WindowsError as e:
		print("WindowsError", e.message)
		return redirect(url_for('error', msg="A model of the same name already exists in the server. Please rename your model or delete the model with the same name"))

	return redirect(url_for('pmvs', name=name))


@app.route("/PMVS/<name>")
def pmvs(name=None):
	return render_template("pmvs.html", name=name)


@app.route("/PMVSprocess" , methods=['GET'])
def pmvsprocess():
	_time = datetime.now()
	name = request.args.get('name')
	target = os.path.join(APP_ROOT, 'static/images/' + str(name) + '/')

	# initialize OsmBundler manager class
	workaddress = str(target)+'temp/'

	try:
		# initialize OsmPMVS manager class
		pmvsmanager = osmpmvs.OsmPmvs(workaddress)

		# call PMVS
		pmvsmanager.doPMVS()

		print("Finish doPMVS, time taken ", (datetime.now() -_time).total_seconds())
		sys.stdout.flush()

		# update quality and processing stage in .txt file (1st digit = quality, 2nd digit = stage)
		completeName = os.path.join(target, "data.txt")
		saver = open(completeName, "r")
		savedData = saver.read()
		saver.close()
		sys.stdout.flush()

		saver = open(completeName, "w")
		saver.write(str(savedData[0]))
		saver.write("3")
		saver.close()
		sys.stdout.flush()
		#

	except AttributeError as e:
		print("AttributeError", e.message)
		return redirect(url_for('error', msg=e.message))
	except IOError as e:
		print("IOError", e.message)
		if e.message:
			return redirect(url_for('error', msg=e.message))
		else:
			return redirect(url_for('error', msg="IOError when updating or saving quality and current stage process"))
	except ValueError as e:
		print("ValueError", e.message)
		return redirect(url_for('error', msg=e.message))
	except WindowsError as e:
		print("WindowsError", e.message)
		return redirect(url_for('error', msg="A model of the same name already exists in the server. Please rename your model or delete the model with the same name"))

	return redirect(url_for('denoise', name=name))


@app.route("/PointCloudDenoise/<name>")
def denoise(name=None):
	return render_template("denoise.html", name=name)


@app.route("/PointCloudDenoiseprocess" , methods=['GET'])
def denoiseprocess():
	##########################################
	_time = datetime.now()
	name = request.args.get('name')
	target = os.path.join(APP_ROOT, 'static/images/' + str(name) + '/')
	workaddress = str(target) + 'temp/'

	def isfloat(value):
		try:
			float(value)
			return True
		except:
			return False

	try:
		f = open(workaddress+"pmvs/models/pmvs_options.txt.ply","r")
		points = []

		for line in f:
			words = line.split()
			if(isfloat(words[0])):
				points.append([float(words[0]),float(words[1]),float(words[2])]) #store x y z of points
		f.close()

		points = np.array(points)
		tree = KDTree(points, leaf_size = 50)
		# find leaf with most neighbours?
		# add into leaf as long as
		distance = []
		for x in points:
			dist, ind = tree.query([x], k=200)
			# np.median(dist)
			distance.append(np.average(dist))
		distance = np.array(distance)
		upper = np.percentile(distance,70)

		indToRemove = []
		for x in range(len(distance)):
			if(distance[x]>upper):
				indToRemove.append(x)

		nf = open(workaddress+"pmvs/models/trim.ply", "w+")
		f = open(workaddress+"pmvs/models/pmvs_options.txt.ply","r")
		newLen = len(distance) - len(indToRemove)
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
					removeCount+=1 # Removed by skipping nf.write(line) below. continue to skip to next for loop
					# print("trim point")
					# TTD: COMMENTED CONTINUE TO SKIP REMOVAL OF POINTS VIA STATISTICAL APPROACH
					continue
			nf.write(line)
		nf.close()
		f.close()

		# update quality and processing stage in .txt file (1st digit = quality, 2nd digit = stage)
		completeName = os.path.join(target, "data.txt")
		saver = open(completeName, "r")
		savedData = saver.read()
		saver.close()
		sys.stdout.flush()

		saver = open(completeName, "w")
		saver.write(str(savedData[0]))
		saver.write("4")
		saver.close()
		sys.stdout.flush()
		#

		finish = datetime.now()
		print("Finish denoising, time taken ", (finish - _time).total_seconds())
		sys.stdout.flush()

	except AttributeError as e:
		print("AttributeError", e.message)
		return redirect(url_for('error', msg=e.message))
	except IOError as e:
		print("IOError", e.message)
		if e.message:
			return redirect(url_for('error', msg=e.message))
		else:
			return redirect(url_for('error', msg="IOError when updating or saving quality and current stage process"))
	except ValueError as e:
		print("ValueError", e.message)
		return redirect(url_for('error', msg=e.message + ". Perhaps images are too similar or different, and thus is unable to match features"))
	except WindowsError as e:
		print("WindowsError", e.message)
		return redirect(url_for('error', msg="A model of the same name already exists in the server. Please rename your model or delete the model with the same name"))

	return redirect(url_for('poisson', name=name))


@app.route("/PoissonReconstruction/<name>")
def poisson(name=None):
	return render_template("poisson.html", name=name)


@app.route("/PoissonReconstructionprocess" , methods=['GET'])
def poissonprocess():
	#################################################
	_time = datetime.now()
	name = request.args.get('name')
	target = os.path.join(APP_ROOT, 'static/images/' + str(name) + '/')
	workaddress = str(target) + 'temp/'

	try:
		# update quality and processing stage in .txt file (1st digit = quality, 2nd digit = stage)
		completeName = os.path.join(target, "data.txt")
		saver = open(completeName, "r")
		savedData = saver.read()
		saver.close()
		sys.stdout.flush()
		#

		# distrPath = os.path.dirname( os.path.abspath(sys.argv[0]) )
		possoinExecutable = os.path.join(APP_ROOT, "software/PoissonRecon.exe")

		# Quality settings to depth
		if savedData[0] == '2':
			depth = 12
		elif savedData[0] == '1':
			depth = 9
		else:
			depth = 8

		# depth = 8 + (int(quality) * 2)
		print("--depth: ", depth)

		currentTime = datetime.now()
		subprocess.call([possoinExecutable, "--in", workaddress + "pmvs/models/trim.ply", "--out",
		                 workaddress + "pmvs/models/mesh.ply", "--depth", str(depth), "--colors", "100", "--pointWeight", "0",
		                 "--density"])
		print("Untrimmed: ", (datetime.now() - currentTime).total_seconds())

		# # VERY LOW QUALITY
		# currentTime = datetime.now()
		# subprocess.call([possoinExecutable, "--in", workaddress+"pmvs/models/trim.ply", "--out", workaddress+"pmvs/models/mesh.ply", "--depth", "7", "--color", "100", "--pointWeight","0", "--density"])
		# print("d7 ", (datetime.now() - currentTime).total_seconds())

		saver = open(completeName, "w")
		saver.write(str(savedData[0]))
		saver.write("5")
		saver.close()
		sys.stdout.flush()
		#

		finish = datetime.now()
		print("Finish denoising, time taken ", (finish - _time).total_seconds())
		sys.stdout.flush()

	except AttributeError as e:
		print("AttributeError", e.message)
		return redirect(url_for('error', msg=e.message))
	except IOError as e:
		print("IOError", e.message)
		if e.message:
			return redirect(url_for('error', msg=e.message))
		else:
			return redirect(url_for('error', msg="IOError when updating / saving quality and current stage process"))
	except ValueError as e:
		print("ValueError", e.message)
		return redirect(url_for('error', msg=e.message))
	except WindowsError as e:
		print("WindowsError", e.message)
		return redirect(url_for('error', msg="A model of the same name already exists in the server. Please rename "
		                                     "your model or delete the model with the same name"))

	return redirect(url_for('trimmer', name=name))
	##########################################################

@app.route("/TrimAndNoiseRemoval/<name>")
def trimmer(name=None):
	return render_template("trimmer.html", name=name)

@app.route("/TrimAndNoiseRemovalprocess", methods=['GET'])
def trimmerprocess():
	#################################################
	_time = datetime.now()
	name = request.args.get('name')
	target = os.path.join(APP_ROOT, 'static/images/' + str(name) + '/')
	workaddress = str(target) + 'temp/'

	try:
		# update quality and processing stage in .txt file (1st digit = quality, 2nd digit = stage)
		completeName = os.path.join(target, "data.txt")
		saver = open(completeName, "r")
		savedData = saver.read()
		saver.close()
		sys.stdout.flush()
		#

		###################### STAGE 4 (Trims non-meaningful surfaces that may come from floors)
		surfaceTrimmer = os.path.join(APP_ROOT, "software/SurfaceTrimmer.exe")
		currentTime = datetime.now()
		subprocess.call([surfaceTrimmer, "--in", workaddress + "pmvs/models/mesh.ply", "--out",
		                 workaddress + "pmvs/models/trimmed_mesh.ply", "--trim", "6", "--smooth", "7"])
		print("Trimmed: ", (datetime.now() - _time).total_seconds())
		sys.stdout.flush()
		######################

		############################ TRIMESH
		# load a file by name or from a buffer
		_time = datetime.now()
		mesh = trimesh.load(workaddress+"pmvs/models/trimmed_mesh.ply")

		# Splits up seperated meshes from mesh in .PLY
		meshes = mesh.split(only_watertight = False)
		mesh.visual.vertex_colors = mesh.visual.vertex_colors
		currentMeshIndex = -1
		largestMeshIndex = -1
		mesharea = []
		largestMeshArea = 0

		# Find largest mesh among split meshes
		for eachmesh in meshes:
			currentMeshIndex = currentMeshIndex + 1
			mesharea.append(eachmesh.area)
			if(eachmesh.area > largestMeshArea):
				largestMeshIndex = currentMeshIndex
				largestMeshArea = eachmesh.area

		# Save largest mesh
		meshes[largestMeshIndex].visual.vertex_colors = meshes[largestMeshIndex].visual.vertex_colors
		meshes[largestMeshIndex].export(APP_ROOT+'/static/model/'+str(name)+'.ply')
		print("Trimmed: ", (datetime.now() - _time).total_seconds())
		sys.stdout.flush()
		############################ TRIMESH


		print("mesh.visual.kind = " + mesh.visual.kind)
		print("meshes[largestMeshIndex].visual.kind = " + meshes[largestMeshIndex].visual.kind)

		saver = open(completeName, "w")
		saver.write(str(savedData[0]))
		saver.write("6")
		saver.close()
		sys.stdout.flush()
		#

	except AttributeError as e:
		print("AttributeError", e.message)
		return redirect(url_for('error', msg=e.message))
	except IOError as e:
		print("IOError", e.message)
		if e.message:
			return redirect(url_for('error', msg=e.message))
		else:
			return redirect(url_for('error', msg="IOError when updating / saving quality and current stage process"))
	except ValueError as e:
		print("ValueError", e.message)
		return redirect(url_for('error', msg=e.message))
	except WindowsError as e:
		print("WindowsError", e.message)
		return redirect(url_for('error', msg="A model of the same name already exists in the server. Please rename your model or delete the model with the same name"))

	return redirect(url_for('edit', name=name))
	##########################################################


@app.route("/OSM/<name>")
def osm(name=None):
	return render_template("osmbundler.html", name=name)


@app.route("/OSMprocess" , methods=['GET'])
def osmprocess():
	_time = datetime.now()
	name = request.args.get('name')
	target = os.path.join(APP_ROOT, 'static/images/' + str(name) + '/')

	# initialize OsmBundler manager class
	workaddress = str(target)+'temp/'
	manager = osmbundler.OsmBundler(target,workaddress)

	try:
		manager.preparePhotos()
		print("Finish preparing photos, time taken ", (datetime.now() -_time).total_seconds())
		sys.stdout.flush()
		_time = datetime.now()

		manager.matchFeatures()
		print("Finish matching features, time taken ", (datetime.now() -_time).total_seconds())
		sys.stdout.flush()
		_time = datetime.now()

		manager.doBundleAdjustment()
		print("Finish bundleadjustment, time taken ",  (datetime.now() -_time).total_seconds())
		sys.stdout.flush()
		_time = datetime.now()

		# manager.openResult()

		# initialize OsmPMVS manager class
		pmvsmanager = osmpmvs.OsmPmvs(workaddress)
		# initialize PMVS input from Bundler output
		pmvsmanager.doBundle2PMVS()

		print("Finish bundle2PMVS, time taken ", (datetime.now() -_time).total_seconds())
		sys.stdout.flush()
		_time = datetime.now()

		# call PMVS
		pmvsmanager.doPMVS()

		print("Finish doPMVS, time taken ", (datetime.now() -_time).total_seconds())
		sys.stdout.flush()

		# update quality and processing stage in .txt file (1st digit = quality, 2nd digit = stage)
		completeName = os.path.join(target, "data.txt")
		saver = open(completeName, "r")
		savedData = saver.read()
		saver.close()
		sys.stdout.flush()

		saver = open(completeName, "w")
		saver.write(str(savedData[0]))
		saver.write("1")
		saver.close()
		sys.stdout.flush()
		#

	except AttributeError as e:
		print("AttributeError", e.message)
		return redirect(url_for('error', msg=e.message))
	except IOError as e:
		print("IOError", e.message)
		if e.message:
			return redirect(url_for('error', msg=e.message))
		else:
			return redirect(url_for('error', msg="IOError when updating or saving quality and current stage process"))
	except ValueError as e:
		print("ValueError", e.message)
		return redirect(url_for('error', msg=e.message))
	except WindowsError as e:
		print("WindowsError", e.message)
		return redirect(url_for('error', msg="A model of the same name already exists in the server. Please rename your model or delete the model with the same name"))

	return redirect(url_for('denoise', name=name))


@app.route("/fileUpload")
def fileUpload():
	return render_template("fileUpload.html")


@app.route("/plyUpload")
def plyUpload():
	return render_template("plyUpload.html")


@app.route("/plyUploadprocess", methods = ['POST'])
def plyUploadprocess():
	# Check if file is a .ply object
	if(request.files['file'].content_type != 'application/octet-stream'
			or request.files['file'].filename.lower().rpartition('.')[-1] != 'ply'):
			return redirect(url_for('error', msg="File is not .PLY. Please upload a an unfinished .PLY mesh model."))

	# Set default name to timestamp if not defined
	modelname = request.form['modelname']
	if(modelname == ''):
		modelname = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
	print("Model name: " + modelname)

	# Check if another file with the same name exists
	modelFolder = os.path.join(APP_ROOT, 'static/model/')
	for f in listdir(modelFolder):
		path = os.path.join(modelFolder, f)
		filename = f[:-4]
		if(filename == modelname):
			return redirect(url_for('error', msg="Model name already exists in server. Please choose a different name "
			                                     "or delete the old model."))

	quality = request.form['quality']
	print("Quality: " + quality)

	step = request.form['step']
	print("Step: " + step)

	uploadedfile = request.files['file']

	sys.stdout.flush()
	target = os.path.join(APP_ROOT, 'static/images/'+str(modelname)+'/')

	if not os.path.isdir(target):
		os.mkdir(target)

	# Store quality and processing stage in .txt file (1st digit = quality, 2nd digit = stage)
	completeName = os.path.join(target, "data.txt")
	saver = open(completeName, "w+")
	saver.write(quality)
	saver.write("0")
	saver.close()
	#

	if not os.path.isdir(target):
		os.mkdir(target)
		sys.stdout.flush()

	newDir = os.path.join(target, 'temp/pmvs/models/')
	if not os.path.isdir(newDir):
		os.mkdir(os.path.join(target, 'temp/'))
		os.mkdir(os.path.join(target, 'temp/pmvs/'))
		os.mkdir(os.path.join(target, 'temp/pmvs/models/'))

	if step == '2':
		filename = "pmvs_options.txt.ply"
	elif step == '3':
		filename = "trim.ply"
	else: # elif step == '4':
		filename = "mesh.ply"

	destination = "/".join([newDir, filename])
	uploadedfile.save(destination)
	print(".PLY saved")
	sys.stdout.flush()

	if step == '2':
		return redirect(url_for('denoise', name=modelname))
	elif step == '3':
		return redirect(url_for('poisson', name=modelname))
	elif step == '4':
		return redirect(url_for('trimmer', name=modelname))

	return redirect(url_for('error', msg="Step not chosen. Please try again"))


@app.route("/delete/<name>")
def delete(name = None):
	os.remove(APP_ROOT+"/static/model/"+name+".ply")
	return redirect(url_for('edit'))

@app.route("/deleteImages/<name>")
def deleteImages(name = None):
	shutil.rmtree(APP_ROOT+"/static/images/"+name)
	return redirect(url_for('imagesets'))

@app.route("/edit/")
@app.route("/edit/<name>")
def edit(name = None):
	modelFolder = os.path.join(APP_ROOT, 'static/model/')
	data = []

	a = [s for s in os.listdir(modelFolder)
	     if os.path.isfile(os.path.join(modelFolder, s))]
	a.sort(key=lambda s: os.path.getmtime(os.path.join(modelFolder, s)))

	for f in a:
		path = os.path.join(modelFolder, f)
		info = os.stat(path)
		filename = f[:-4]
		data.append({'filename' : filename, 'creation_time' : datetime.fromtimestamp(info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'), 'modification_time' : datetime.fromtimestamp(info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'), 'file_size' : info.st_size/1024})
	print(data)
	sys.stdout.flush()
	return render_template("edit.html", name=name, data = data)

@app.route("/imagesets/")
def imagesets():
	modelFolder = os.path.join(APP_ROOT, 'static/images/')
	data = []
	for f in listdir(modelFolder):
		try:
			path = os.path.join(modelFolder, f)
			info = os.stat(path)

			txtfile = os.path.join(path, "data.txt")
			saver = open(txtfile, "r")
			dataread = saver.read()
			saver.close()

			qualityText = "High"
			if dataread[0] == "0":
				qualityText = "Low"
			elif  dataread[0] == "1":
				qualityText = "Medium"

			data.append({'filename' : f, 'creation_time' : datetime.fromtimestamp(info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
				            , 'quality' : qualityText, 'stage' : dataread[1]})
		except IOError:
			print("IOError: ", path)
		except:
			print("Error: ", path)
	print(data)
	sys.stdout.flush()
	return render_template("imagesets.html", data = data)

@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html")

@app.route("/display/")
@app.route("/display/<name>")
def display(name = None):
	return render_template("display.html", name=name)


@app.route("/error/<msg>")
def error(msg=None):
		return render_template("error.html", msg=msg)


if __name__ == "__main__":
	app.run(host= '0.0.0.0')
	# app.run()