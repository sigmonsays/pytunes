#!/usr/bin/python

from lib import pyTunes
import sys

def main(argv):
	app = pyTunes.pyTunesMain()
	app.run(argv)

main(sys.argv)

