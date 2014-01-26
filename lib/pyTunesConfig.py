import ConfigParser
import os

class pyTunesConfig:
	def __init__(self):
		self.cfg = ConfigParser.SafeConfigParser()

		home = os.getenv('HOME')
		if home is None:
			return

		self.path = '%s/%s' % (home, '/.pyTunes')

		if not os.path.exists(self.path):
			os.makedirs(self.path)

		if not os.path.exists('%s/pyTunes.ini' % (self.path)):
			open('%s/pyTunes.ini' % (self.path), 'w' ).close()

		self.cfg.read('%s/pyTunes.ini' % (self.path))

		if not self.cfg.has_section("pyTunes"):
			self.cfg.add_section("pyTunes")

		self.set("pyTunes", "dude", 1)

	def save(self):
		self.write()

	def write(self):
		fp = open('%s/pyTunes.ini' % (self.path), 'w' )
		self.cfg.write(fp)

	def get(self, section, variable, default = None):

		if not self.cfg.has_section(section):
			return default

		if not self.cfg.has_option(section, variable):
			return default

		return self.cfg.get(section, variable)

	def set(self, section, variable, value):
	
		if not self.cfg.has_section(section):
			self.cfg.add_section(section)

		self.cfg.set(section, variable, value)


	def items(self, section, default = None):
		if not self.cfg.has_section(section):
			return default
		return self.cfg.items(section)

