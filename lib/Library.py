import os
from lib import ID3
from lib import db
import sha
from lib import pymplayerd
from lib import exceptions


class baseLibrary:

	"""
	I am the base library. I shouldn't be created directly. I manage the DB API, hold file types possibly more
	"""

	def __init__(self, path):

		self.database = db.musicdb(path)
		self.file_types = { 
			'.mp3' : "MP3 Audio" ,
			'.mp4' : "MP4 Audio" ,
			'.ogg' : "Ogg Vorbis Audio" ,

		}

	def addRecord(self, rec):

		rec_escaped = {}
		for tmp in rec:
			val = rec[tmp].replace("'", "''")
			val = val.replace("\0", "")
			rec_escaped[tmp] = val

		qry = "INSERT INTO music ( ID, directory, filename, artist, album, title  ) "\
			"VALUES ('%(id)s', '%(directory)s', '%(filename)s', '%(artist)s', '%(album)s', '%(title)s' )" % rec_escaped

		self.database.query(qry)

	def commit(self):
		self.database.commit()


class RemoteMusicLibrary(baseLibrary):

	"""
	I am a music library class implementing a library interface to mplayerd
	"""

	def __init__(self, path, host = 'localhost', port = 7400 ):
		baseLibrary.__init__(self, path)

		self.mp = pymplayerd.mplayerd()

		self.host = host
		self.port = port

		self.mp.connect(host, port)


	def iterateFolder(self, path):

		""" 
		I am a generator
		I recursively iterate a "folder"
		"""

		if not self.mp.isConnected():
			raise exceptions.NoConnection()

		print "Entering '%s'" % (path)

		for id, file_type, filename in self.mp.ls(path):
		
			print "%s %s %s" % (id, file_type, filename)

			if file_type == 'd':
				for x in self.iterateFolder('%s/%s' % (path, filename) ):
					yield x

			elif file_type == 'f':

				if not self.file_types.has_key( filename[-4:] ):
					print "Skipping '%s'" % (filename)
					continue

				id3 = self.mp.id3( '%s/%s' % (path, filename)  )

				dirpath = '%s://%s' % (self.mp.host, path)

				info = {'directory' : dirpath, 'filename' : filename } 
				info.update(id3)

				yield info




class LocalMusicLibrary(baseLibrary):

	"""
	I am a generator
	I represent a local library
	"""

	def __init__(self, path):
		baseLibrary.__init__(self, path)

	def iterateFolder(self, path):

		for dirpath, dirnames, filenames in os.walk(path):

			filenames = [f for f in filenames if self.file_types.has_key( f[-4:] )]
			for filename in filenames:

				info = {'directory' : dirpath, 'filename' : filename }

				full_path = '%s/%s' % (dirpath, filename)
				id3 = ID3.ID3( full_path )

				info['id'] = sha.new(full_path).hexdigest()

				info['artist'] = id3.get('ARTIST', 'none')
				info['album'] = id3.get('ALBUM', 'none')
				info['title'] = id3.get('TITLE', 'none')

				yield info

