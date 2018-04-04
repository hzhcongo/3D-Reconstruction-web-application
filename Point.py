import math

class Point:

    def __init__(self, x, y, z, nx, ny, nz, red, green, blue):
        self.x = x
        self.y = y
        self.z = z
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.red = red
        self.green = green
        self.blue = blue
        self.printData()

    def printData(self):
        print("Point values: " + str(self.x) + " " + str(self.y) + " " + str(self.z) + " " + str(self.nx) + " " + str(self.ny) + " " + str(self.nz) + " " + str(self.red) + " " + str(self.green) + " " + str(self.blue))

    @classmethod
    def calcEuclideanDist(cls, a, b):
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)