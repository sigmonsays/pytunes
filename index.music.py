#!/usr/bin/python
import os
from lib import ID3
import sqlite
import md5
import string

def del_nonprintables(s, Ac_s = string.maketrans("",""), ab_printables = string.maketrans("","").translate(string.maketrans("",""), string.printable)): 
	return s.translate(Ac_s, ab_printables)

def escape(s):
	new =  del_nonprintables(str(s).replace("'", "''"))
	new.replace("\000", "")
	return new

create_sql = """
create table music (id varchar(255), path varchar(255), filename varchar(255), artist varchar(255), album varchar(255), 
title varchar(255), track varchar(255), year varchar(255), genre varchar(255), comment varchar(255))
"""



dir = "/mnt/media/"

db = sqlite.connect('music.db')
cursor = db.cursor()

for dirpath, dirnames, filenames in os.walk(dir):

	for filename in [f for f in filenames if f.rfind('.mp3', -4) > 0]:

		id3 = ID3.ID3('%s/%s' % (dirpath, filename) )

		id = md5.new('%s/%s' % (dirpath, filename) ).hexdigest()

		album = id3.album
		artist = id3.artist
		title = id3.title
		track = id3.track
		year = id3.year
		genre = id3.genre
		comment = id3.comment

		qry = "INSERT INTO music ( id, path, filename, artist, album, title, track, year, genre, comment ) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (id, escape(dirpath) , escape(filename), escape(artist), escape(album), escape(title), escape(track), escape(year), escape(genre), escape(comment))

		print "QUERY:",qry	
		cursor.execute(qry)

		db.commit()
		

