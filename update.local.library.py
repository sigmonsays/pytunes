#!/usr/bin/python

from lib import Library

lib = Library.LocalMusicLibrary('/home/exonic/.pyTunes/testmusiclibrary')

for info in lib.iterateFolder('/mnt/media'):

	lib.addRecord(info)

lib.commit()
