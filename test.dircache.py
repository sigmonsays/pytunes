#!/usr/bin/python

from lib import pymplayerd

mp = pymplayerd.mplayerd()

mp.connect()

print mp.pwd()


for f in mp.dirdump('/mnt/media/slange/mp3'):
	print f
mp.disconnect()
