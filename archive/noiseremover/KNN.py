
import numpy as np
from sklearn.neighbors import KDTree

def isfloat(value):
	try:
		float(value)
		return True
	except:
		return False

f = open("test.ply","r")
points = []

for line in f:
	words = line.split()
	if(isfloat(words[0])):
		# print(str(words[0]))
		points.append([float(words[0]),float(words[1]),float(words[2])])

f.close()

points = np.array(points)
tree = KDTree(points, leaf_size = 50)

distance = []
for x in points:
	# print x[0]	
	dist, ind = tree.query([x], k=50)
	distance.append(np.average(dist))
	# print 'the average distance for the first point is', np.average(dist)
distance = np.array(distance)
upper = np.percentile(distance,80)

indToRemove = []
for x in range(len(distance)):
	if(distance[x]>upper):
		indToRemove.append(x)
# print indToRemove

nf = open("trim.ply", "w+")
f = open("test.ply","r")
newLen = len(distance) -len(indToRemove)
removeCount = 0
lineCount = -1
for line in f:
	words = line.split()
	if(words[0] == "element"):
		nf.write(words[0]+" "+words[1]+" "+str(newLen)+"\n")
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

# print ind
# print dist