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
import Point
from sklearn.neighbors import KDTree
import subprocess
from flask_debugtoolbar import DebugToolbarExtension

class Group:

    def __init__(self, name):
        self.name = name
        self.points = []
        self.points = np.array(self.points)

    def addPoint(self, point):
        try:
            self.points = np.append(self.points, point)
            print("Point added to Group" + self.name)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except ValueError:
            print "Could not convert data to point."
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getName(self):
		return self.name