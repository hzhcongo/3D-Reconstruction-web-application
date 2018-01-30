import trimesh
import sys
import math
import networkx as nx
import numpy as np

for i in range(0,5):
	# Load mesh
	mesh = trimesh.load_mesh('trimmed_mesh.ply')
	print("1"+mesh.visual.kind)
	meshes = mesh.split(only_watertight=False)
	largestFaceCount = 0
	for m in meshes:
		faceCount = len(m.faces)
		if(faceCount>largestFaceCount):
			largestFaceCount = faceCount
			mesh = m
	print("2"+mesh.visual.kind)
	mesh.process()
	print("3"+mesh.visual.kind)
	# mesh = trimesh.primitives.Sphere()
	# mesh.export("sphere.ply")

	def distance(edge):
		vertices = mesh.vertices
		u=vertices[edge[0]]
		v=vertices[edge[1]]
		return math.sqrt((u[0]-v[0])**2 + (u[1]-v[1])**2 + (u[2]-v[2])**2)

	edges = mesh.edges_unique
	print("First 10 elements in edges")
	for i in range(0,8):
		print(edges[i])	
	sys.stdout.flush()

	edge_d = []
	for idx,val in enumerate(edges):
		edge_d.append([idx, distance(val)])
	print("First 10 elements in the edge_d")
	for i in range(0,8):
		print(edge_d[i])	
	sys.stdout.flush()

	edge_d.sort(key=lambda element:element[1])
	print("First 10 elements in the sorted edge_d")
	for i in range(0,8):
		print(edge_d[i])	
	sys.stdout.flush()

	edges = edges[[(int)(element[0]) for element in edge_d]]
	print("First 10 elements in the sorted edges")
	for i in range(0,8):
		print(edges[i])	
	sys.stdout.flush()

	#get the unique index of elements in 1-D version of edges
	temp,keep = np.unique(edges, return_index=True)
	keep.sort()
	#get the duplicate index of elements in 1-D version of edges
	keep = np.delete(np.arange(len(edges)*2),keep)
	#get the duplicate index of elements in 2-D version of edges
	keep = np.unique(keep/2)
	#get the unique index of elements in 2-D version of edges
	keep = np.delete(np.arange(len(edges)), keep)
	edges = edges[keep]
	vertices = mesh.vertices
	new_pos = [(vertices[element[0]] + vertices[element[1]])/2 for element in edges]

	target = len(edges)
	# print("Before process, first element is {}, second element is {}".format(mesh.vertices[14034], mesh.vertices[14079]))
	# mesh.vertices[[element[0] for element in edges]] = mesh.vertices[[element[1] for element in edges]]
	mesh.vertices[[element[0] for element in edges]] = new_pos
	mesh.vertices[[element[1] for element in edges]] = new_pos	
	# print("After process, first element is {}, second element is {}".format(mesh.vertices[14034], mesh.vertices[14079]))


	mesh.process()
	sys.stdout.flush()
	mesh.export('trimmed_mesh.ply')



# oldVertices = []
# oldFaces = []
# newVertices = []
# newFaces = []
# verticesToRemove = []
# facesToRemove = []

class Vertex:
	pass

class Triangle:
	pass


def removeVertex():
	print("vertices to romove count is ", len(verticesToRemove))
	sys.stdout.flush()
	verticesToRemove.sort(reverse=True)
	for v in verticesToRemove:
		del mesh.vertices[v]

def removeFace():
	print("faces to romove count is ", len(facesToRemove))
	sys.stdout.flush()
	facesToRemove.sort(reverse=True)
	for f in facesToRemove:
		del mesh.faces[f]

def replaceVertex(faceind, vertex):
	for f in mesh.faces[faceind]:
		if(f == vertex.index):
			f = vertex.collapseNeighbor

def distance(u,v):
	return math.sqrt((u[0]-v[0])**2 + (u[1]-v[1])**2 + (u[2]-v[2])**2)
	
def calcEdgeCollapseCost(u,v):
	return distance(mesh.vertices[u], mesh.vertices[v])

def collapse(vertex):
	collapseNeighbor = vertex.collapseNeighbor
	faceList = vertex.faceList
	faces = mesh.faces
	if(not collapseNeighbor):
		verticesToRemove.append(vertex.index)
		# removeVertex(vertex)
		return
	if collapseNeighbor in verticesToRemove:
		return

	for fIndex in faceList:
		# print("face list count is ", len(vertex.faceList))
		if collapseNeighbor in faces[fIndex]:
			# removeFace(f)
			facesToRemove.append(fIndex)
		else:
			replaceVertex(fIndex, vertex)
	# removeVertex(vertex)
	verticesToRemove.append(vertex.index)


def simplifyMesh(mesh, targetVerticeCount):
	if(targetVerticeCount>=len(mesh.vertices)):
		return

	for index, v in enumerate(mesh.vertices):
		vertex = Vertex()
		vertex.index = index
		vertex.v = v
		vertex.faceList = []
		newVertices.append(vertex)

	# print("after enumerate, oldvertices count is "+str(len(oldVertices)))


	for index, f in enumerate(mesh.faces):
		newVertices[f[0]].faceList.append(index)
		newVertices[f[1]].faceList.append(index)
		newVertices[f[2]].faceList.append(index)
		triangle = Triangle()
		triangle.f = f
		triangle.index = index
		newFaces.append(triangle)

	for vertex in newVertices:
		neighbors = graph.neighbors(vertex.index)
		if(len(neighbors) == 0):
			vertex.collapseNeighbor = None
			vertex.collapseCost = - 0.01
			return
		vertex.collapseNeighbor = None
		vertex.collapseCost = 10000
		for n in neighbors:
			cost = calcEdgeCollapseCost(vertex.index, n)
			if(not vertex.collapseNeighbor):
				vertex.collapseNeighbor = n
				vertex.collapseCost = cost
				vertex.minCost = cost
				vertex.totalCost = 0
				vertex.costCount = 0
			vertex.totalCost += vertex.collapseCost
			vertex.costCount += 1
			if(cost < vertex.minCost):
				vertex.minCost = cost
				vertex.collapseNeighbor = n
		vertex.collapseCost = vertex.totalCost/vertex.costCount

	sorted(newVertices, key = lambda vertex: vertex.collapseCost)
	count = 0
	print("Start to do collapsing, target count is ", targetVerticeCount)
	sys.stdout.flush()
	while(count<targetVerticeCount):
		collapse(newVertices[count])
		count+=1
		if(count%1000 == 0):
			print(count)
			sys.stdout.flush()
	removeVertex()
	removeFace()

# simplifyMesh(mesh, len(mesh.vertices)/2)
# mesh.export('simplified.ply')

