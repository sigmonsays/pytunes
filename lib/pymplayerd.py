import socket
import string

class mplayerd:

	"""
	Python interface to control an mplayerd server
	"""

	def __init__(self):

		"""
		Constructor, no arguments needed.
		"""
		self.sock = None
		# 0 stopped, 1 playing, 2 paused
		self.host = 'localhost'
		self.port = 7400
		self.eof = chr(160)

		self.error = None

	def connect(self, host = 'localhost', port = 7400):
		"""
		create a connection 
		returns True on connect, Otherwise False
		"""
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			sock.connect( (host, port) )
		except:
			return False

		self.host = host
		self.port = port

		self.sock = sock
		self.read()
		
		return True

	def isConnected(self):
		"""
		Returns True if there is a connection, Otherwise False
		"""

		if self.sock is None:
			return False
		return True

	def disconnect(self):
		"""
		Disconnect the connection. Returns True on disconnect, if no connection Returns False.
		"""

		if not self.sock: return False
		self.sock.close()
		self.sock = None
		return True

	def read(self):
		"""
		Read data from socket until self.eof char is read()
		"""

		if not self.sock: return False

		buf = ''
		while True:
			tmp = self.sock.recv(4096)
			buf += tmp
			if (buf.find(self.eof) >= 0): break

		return buf

	def write(self, buf):
		"""
		write data to socket
		"""

		self.sock.send(buf)

	def command(self, cmd):

		"""
		sends a command to the socket, buf will have a newline automatically appended, reads response and returns
		the raw result buffer.
		"""

		self.write(cmd + "\r\n")
		return self.read()


	def responseOK(self, buf):

		"""
		Parse a response from a standard mplayerd response, and return True
		if the command was successfull, otherwise False
		"""

		[resp] = buf.split("\r\n")[1:2]
		tmp = resp.split(" ") 

		code = int(tmp[0])
		response = tmp[1:]
		self.error = None
		self.response = response
		if code: return True
		self.error = response
		return False


	def status(self, instance = 1):
		"""
		Returns a dict containing the response from the mplayerd status command.
		"""

		buf = self.command("status")

		rv = {}

		for f in buf.split("\r\n"):
			
			i = f.find(":")

			if (i == -1): continue

			rv[ f[0:i] ] = f[i+1:].strip()

		return rv

	def cd(self, directory):
		"""
		Change directory 
		"""

		buf = self.command('cd 1 "%s"' % (directory) )
		lines = buf.split("\r\n")

		if lines[1] == 'No such file or directory':
			return False

		return True

	def load(self, file, instance = 1):

		"""
		Open file into mplayerd. Optionally specify an instance.
		"""

		buf = self.command('load %d "%s"' % (instance, file))
		return self.responseOK(buf)


	def stop(self, instance = 1):
		"""
		Stop the file from playing and unload it
		"""

		buf = self.command("stop %d" % (instance))
		return self.responseOK(buf)

	def pause(self, instance = 1):
		"""
		Pause the file. Optionally specify an instance.
		"""

		buf = self.command("pause %d" % (instance))
		return self.responseOK(buf)
	
	def fullscreen(self, instance = 1):

		"""
		Fullscreen the file (if supported). Optionally specify an instance.
		"""
		buf = self.command("fullscreen %d" % (instance))
		return self.responseOK(buf)

	def osd(self, level = 1, instance = 1):

		"""
		Change the osd level int value 1 to 3. Optionally specify an instance.
		"""
		buf = self.command('osd %d %d' % (instance, level) )
		return self.responseOK(buf)	

	def volume(self, direction, instance = 1):
		"""
		Change the volume in one up or down. 1 for up, 0 for down.
		Optionally specify an instance.
		"""

		buf = self.command('volume %d %s' % (instance, direction) )
		return self.responseOK(buf)


	def mute(self, instance = 1):
		"""
		Mute the audio. Optionally specify an instance.
		"""

		buf = self.command('mute %d' % (instance) )
		return self.responseOK(buf)

	def version(self):
		"""
		Return the version of mplayerd 
		"""

		buf = self.command('version')
		resp = buf.split("\r\n")[1]
		return resp


	def shutdown(self):
		"""
		Shutdown the mplayerd server. This will cause the server to exit and all connections closed.
		"""

		buf = self.command('shutdown now')
		return self.responseOK(buf)

	def pwd(self):
		"""
		Return the current working directory.
		"""

		buf = self.command('pwd')
		resp = buf.split("\r\n")[1:-1][0]
		return resp


	def line_read(self):

		if not self.sock: yield None
		
		get_out_the_choppa = False

		while True and not get_out_the_choppa:

			buf = self.sock.recv(4096)

			if buf == '':
				break

			for line in buf.split("\r\n"):

				if line.strip() == '': continue

				if line.find(self.eof) >= 0: 
					get_out_the_choppa = True
					break

				yield line

	def dirdump(self, path = '/'):
		"""
		I am a generator
		Dump a directory structure and information recurively 
		"""
		self.write( 'dirdump "%s"\r\n' % (path) )

		self.sock.recv(512)

		for f in self.line_read():
			p = f.find(" ")

			if p == -1:
				break

			entry = ( f[:p], f[p:].strip() )

			yield entry
			
	def filedump(self, path = '/'):
		"""
		I am a generator
		Dump a file list and information of a directory structure 
		"""
		return None

	def ls(self, path = None):

		"""
		I am a generator. I return a tuple (id, type, name), 
		where id is a unique number, type is either 'f' for file or 'd' for directory, and name
		is the name of the file.
		"""

		cmd = 'ls 1'
		if not path is None:
			cmd += ' "%s"' % (path)
		buf = self.command(cmd)
		lines = buf.split("\r\n")

		for f in lines[1:-1]:
			i = f.find(" ")
			if f[-1] == '/':
				type = 'd'
				name = f[i:-1].strip()
			else:
				type = 'f'
				name = f[i:].strip()

			id = int(f[:i])

			yield (id, type, name)
		

	def who(self):

		"""
		Who else is connected?
		"""

		buf = self.command('who')
		lines = buf.split("\r\n")
		l = len(lines)
		who = lines[2:l - 2]
		resp = []
		for w in who:
			[ID,IP,CWD] = w.split("\t\t")
			resp.append( (ID, IP, CWD) ) 

		return resp

	def kill(self, session):
		"""
		Disconnect a client by session id
		Returns the raw response from the server. This will change in the future.
		"""

		buf = self.command('kill 1 %d' % (session) )
		return buf

	def instances(self):

		"""
		Returns a list of instances, each entry contains a tuple (id, status, info),
		where id is a unique instance id, current status, and other info.
		"""

		buf = self.command('instances')
		lines = buf.split("\r\n")
		l = len(lines)
		instances = []
		for inst in lines[2:l - 1]:
			tmp = inst.split(" ")
			[id, status] = tmp[0:2]
			info = tmp[2:]
			instances.append( (id, status, info) )	
		return instances

	def new(self):
		"""
		Create a new instance and return it's ID
		Otherwise returns False if instance failed.
		"""

		buf = self.command('new')
		if not self.responseOK(buf): return False

		[new] = buf.split("\r\n")[3]
		return new

	def length(self):
		"""
		I tell mplayerd to get the length of the loaded song
		The length is then available in the status command.
		"""

		resp = self.command('length')

		if self.responseOK(resp):
			return True

		return False

	def seek_percent(self, percentage, instance = 1):
		"""
		Seeks by percent
		"""

		resp = self.command('seek_percent %d %d' % (instance, percentage) )

		if self.responseOK(resp):
			return True

		return False

	def seek_absolute(self, seconds, instance = 1):
		"""
		Seek by seconds to an absolute position
		"""

		resp = self.command('seek_absolute %d %d' % (instance, percentage) )

		if self.responseOK(resp):
			return True

		return False

	def seek_relative(self, seconds, instance = 1):
		"""
		Seek relative to current position by seconds
		"""

		resp = self.command('seek_relative %d %d' % (instance, percentage) )

		if self.responseOK(resp):
			return True

		return False


	def id3(self, filename, instance = 1):

		"""
		Read id3 info
		Returns a dict containing read id3v1 tags
		"""

		buf = self.command('id3 %d "%s"' % (instance, filename))
		id3 = {}

		for line in buf.split("\r\n")[2:-1]:

			p = line.find(":")
			if p == -1:
				continue

			var = line[:p]
			val = line[p + 1:].strip()

			if val == '':
				val = 'none'

			id3[var] = val

		return id3
