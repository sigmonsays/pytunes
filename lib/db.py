import sys
import MySQLdb

class musicdb:

	def __init__(self, db_path, host = 'localhost', username = 'root', password = ''):

		self.db = MySQLdb.connect( host, username, password )
		self.cur = self.db.cursor()

	def query(self, qry):
		self.cur.execute(qry)
		result = self.cur.fetchall()
		return result

