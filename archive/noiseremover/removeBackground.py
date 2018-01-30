
import numpy as np

def isfloat(value):
	try:
		float(value)
		return True
	except:
		return False

f = open("trim1.ply","r")
a1 = []
a2 = []
a3 = []

for line in f:
	words = line.split()
	if(isfloat(words[0])):
		print(str(words[0]))
		a1.append(float(words[0]))
		a2.append(float(words[1]))
		a3.append(float(words[2]))

f.close()

a1 = np.array(a1)
a2 = np.array(a2)
a3 = np.array(a3)

# print("median for a1 is", np.percentile(a1,50))
# print("median for a2 is", np.percentile(a2,50))
# print("median for a3 is", np.percentile(a3,50))

a1upper = np.percentile(a1,80)
print("98 percentile for a1 is", a1upper)
a2upper = np.percentile(a2,80)
print("98 percentile for a2 is", a2upper)
a3upper = np.percentile(a3,80)
print("98 percentile for a3 is", a3upper)

a1lower = np.percentile(a1,20)
print("2 percentile for a1 is", a1lower)
a2lower = np.percentile(a2,20)
print("2 percentile for a2 is", a2lower)
a3lower = np.percentile(a3,20)
print("2 percentile for a3 is", a3lower)

nf = open("trim2.ply", "w+")
f = open("trim1.ply","r")
for line in f:
	words = line.split()
	if(isfloat(words[0])):
		if(float(words[0]) < a1lower or float(words[0]) > a1upper or float(words[1]) < a2lower or float(words[1]) > a2upper or float(words[2]) < a3lower or float(words[2]) > a3upper):
			if(float(words[6])>180 and float(words[7])>180 and float(words[8])>180):
				print("trim point")
				continue
	print words[0]
	nf.write(line)

nf.close()
f.close()