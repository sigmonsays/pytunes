import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject
from lib import pymplayerd
import pyTunesConfig

import time

from lib import Library

class commonDialog:

	"""
	I am a class that creates a simple common dialog with an OK and Cancel button
	All options configurable...
	There could be a better way but I like this method. 'Twas a Good Learning process.
	"""

	def __init__(self, widgets, title, message):

		"""
		I am the Constructor, 
		
		Create a window with widgets placed into the window, having a message
		title and display message.
		"""

		self.title = title
		self.message = message
		self.widgets = widgets
		self.resp = None

		self.window_name = 'dialog_box'
		self.cancel_button_name = 'dialogBtnBoxCancel'
		self.ok_button_name = 'dialogBtnBoxOK'

		self.win = self.widgets[self.window_name]


		self.setup()

	def show(self):

		
		"""
		Call me to display the dialog
		"""

		dialogBox = self.widgets[self.window_name]
		if dialogBox is None:
			print "Couldn't find dialog box named '%s'" % (dialog_name)
			return

		dialogBox.show()

	def setup(self):

		"""
			Sets up the command dialog
			Create the window, setup events, etc
		"""
		win = self.win

		if win is None:
			print "Couldn't find window!"
			return False

		win.connect('delete-event', self.window_delete_event)

		cancelButton = self.widgets[self.cancel_button_name]
		if cancelButton is None:
			print "Couldn't find cancel button"
			return False
		cancelButton.connect('clicked', self.cancel_button_clicked)

		okButton = self.widgets[self.ok_button_name]
		if cancelButton is None:
			print "Couldn't find OK button"
			return False
		okButton.connect('clicked', self.ok_button_clicked)

		return True

	def response(self):
		""" 
		Returns button response, True for OK, False for Cancel, None if nothing clicked
		"""
		return self.resp

	def window_delete_event(self, win, gdkEvent):
		"""
		I am fired to destroy the window, I actually only hide it
		"""

		self.win.hide()
		return True

	def cancel_button_clicked(self, button):
		"""
		I am fired when the cancel button is clicked. I also hide the window.
		"""
		self.win.hide()
		self.resp = False

	def ok_button_clicked(self, button):
		"""
		I am called when the OK button is clicked, I also hide the window.
		"""
		self.win.hide()
		resp.resp = True


class pyTunesMain:

	"""
	I represent the pyTunes GUI events and handle setting up and managing the display.
	"""

	def __init__(self):

		"""
		Constructor. No arguments passed
		I load up various support classes
		"""
		self.Browser = BasicObject()


		self.initGUI()

		self.config = pyTunesConfig.pyTunesConfig()


		self.mp = pymplayerd.mplayerd()

		self.cwd = None
		self.status = None

		self.playerProgress = self.widgets.get_widget("hscrollbarProgress")

		self.configUpdateGUI()


	def initGUI(self):

		"""
		I initialize the GUI, setup all GUI related stuff here
		"""

		self.widgets = gtk.glade.XML('pytunes.glade')
		self.widgets.signal_autoconnect(self)

		self.timeout = 1000;


		progressBarMain = gtk.ProgressBar()
		self.progressBar = progressBarMain

		hbox = self.widgets.get_widget("hboxStatus")
		hbox.pack_start(progressBarMain)

		# hide the tabs on the notebook
		notebook = self.widgets.get_widget("notebookMain")
		notebook.set_show_tabs(False)
		
		# setup treeArtist  headings and listStore
		cell = gtk.CellRendererText()
		listStore = gtk.ListStore(gobject.TYPE_STRING)

		col = gtk.TreeViewColumn("Artist", cell, text=0)
		tree = self.widgets.get_widget("treeArtist")
		tree.append_column(col)
		tree.set_model(listStore)


		# setup treeAlbum headings and listStore
		cell = gtk.CellRendererText()
		listStore = gtk.ListStore(gobject.TYPE_STRING)

		col = gtk.TreeViewColumn("Album", cell, text=0)
		tree = self.widgets.get_widget("treeAlbum")
		tree.append_column(col)
		tree.set_model(listStore)


		# setup treeBrowse headings and listStore
		cell = gtk.CellRendererText()
		listStore = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING)


		listStore.set_sort_column_id(2, gtk.SORT_ASCENDING)

		tree = self.widgets.get_widget("treeBrowse")


		col = gtk.TreeViewColumn("ID", cell, text=0)
		col.set_visible(False)
		tree.append_column(col)

		col = gtk.TreeViewColumn("Type", cell, text=1)
		col.set_visible(False)
		tree.append_column(col)

		col = gtk.TreeViewColumn("Filename", cell, text=2)
		tree.append_column(col)

		tree.set_model(listStore)



		# Set the "Sources" TreeView
		cell = gtk.CellRendererText()
		tree = self.widgets.get_widget("treeSources")
		
		col = gtk.TreeViewColumn("pyTunes", cell, text=0)
		tree.append_column(col)

		# 									name, tab position
		cell = gtk.CellRendererText()
		treeStore = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT)
		tree.set_model(treeStore)

		iter = treeStore.append(None)
		treeStore.set( iter, 0,  "Music", 1, 0 )

		iter = treeStore.append(None)
		treeStore.set( iter, 0,  "Console", 1, 1 )

		iter = treeStore.append(None)
		treeStore.set( iter, 0,  "Library", 1, 2 )
			
		iter = treeStore.append(None)
		treeStore.set( iter, 0,  "Browser", 1, 3 )

		iter = treeStore.append(None)
		treeStore.set( iter, 0,  "Playlists", 1, 4 )

		# setup the Library TreeView
		cell = gtk.CellRendererText()
		listStore = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING)
		tree = self.widgets.get_widget("treeLibrary")
		tree.set_model(listStore)
		
		col = gtk.TreeViewColumn("Folder Name", cell, text=0)
		tree.append_column(col)

		col = gtk.TreeViewColumn("File Count", cell, text=1)
		tree.append_column(col)


		ConsoleWindow = self.widgets.get_widget("txtViewConsole")
		textbuffer = ConsoleWindow.get_buffer()

		textbuffer.create_mark('scrollmark', textbuffer.get_end_iter())


		# setup the addSource TreeView
		cell = gtk.CellRendererText()
		listStore = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING)

		tree = self.widgets.get_widget("treeViewAddSource")
		tree.set_model(listStore)

		col = gtk.TreeViewColumn("Name", cell, text=0)
		tree.append_column(col)

		# browse menu

		self.menus = {}
		menu = gtk.Menu()

		item = gtk.MenuItem("Add to Playlist")
		item.connect('activate', self.on_browse_add_to_playlist1_activate)
		item.show()
		menu.append(item)

		item = gtk.CheckMenuItem("Show All")
		item.connect('toggled', self.on_browse_tog_show_all)
		item.show()
		self.Browser.Show_All_CheckMenuItem = item
		menu.append(item)
		
		# item.connect('')

		self.menus['browse_menu'] = menu

		

		# this timeout could only be active while playing, but if mplayerd is being
		# controlled from another location, having it always on will update correctly
		# This will eventually be an option
		gobject.timeout_add(self.timeout, self.refreshStatus)

	def configUpdateGUI(self):
		"""
		I update the GUI controls with the appropriate results read from the config
		I should be called after the config class has been created
		"""

		if self.config.get("pyTunes", "startupconnect") == 'True':

			self.setStatusbar("Auto Connecting...")
			self.widgets.get_widget("checkButtonConnectStartup").set_active(1)

			print "TODO: Store host and port in config"
			host, port = ('localhost', 7400)

			self.connect(host, port)


		if self.config.get("browser", "show_all") == 'True':

			checkMenuItem = self.Browser.Show_All_CheckMenuItem
			checkMenuItem.set_active(True)

	def refreshStatus(self):

		"""
		Called to refresh that status of mplayerd
		I am triggered from a gobject.timeout_add(...)
		"""

		if self.mp.isConnected():
			self.status = self.mp.status()

			statusString = '[' + self.status['instance'] + '] ' + self.status['status']
			if not self.status['status'] == 'stopped':
				statusString += ' ' + self.status['time'] + '  ' + self.status['file'];

			self.setStatusbar( statusString )


			if self.status.has_key('length'):
				length_sec = int(self.status['length'])

				print "length_sec", length_sec

				if length_sec == -1:
					self.mp.length()
					length_sec = int(self.status['length'])

				print "upper", self.playerProgress.upper

				if self.playerProgress.upper == 0:
					self.playerProgress.upper = length_sec
				
				if length_sec > 0:

					video_time, audio_time = self.status['time'].split(" ")[0:2]

					video_time = int(float(video_time))
					audio_time = int(float(audio_time))

					percentage = int(length_sec / audio_time)

					self.playerProgress.set_value(audio_time)


			if self.status['status'] == 'stopped':
				self.playerProgress.upper = 0

		gobject.timeout_add(self.timeout, self.refreshStatus)


	def on_treeSources_cursor_changed(self, tree):

		"""
		Sources cursor changed, I update the notebookMain widget page
		"""

		treeSelection = tree.get_selection()
		treeStore, iter = treeSelection.get_selected()

		notebook_page = treeStore.get_value(iter, 1)

		notebook = self.widgets.get_widget("notebookMain")

		notebook.set_current_page(notebook_page)

	def on_togglebuttonMute_clicked(self, togButton):

		"""
		Mute button clicked event
		"""

		if not self.mp.isConnected():
			print "Not connected"
			return

		if togButton.get_active():
			print "Unmuting.."

		else:
			print "Muting.."

		self.mp.mute()

	def on_btnVolumeDown_clicked(self, button):
		"""
		Turn down the volume event
		"""

		self.mp.volume(0)

	def on_btnVolumeUp_clicked(self, button):
		"""
		Pump up the volume event
		"""
		self.mp.volume(1)

	def on_tbPlay_clicked(self, button):
		"""
		Play button event
		"""

		print "Play clicked"
		if self.status is None:
			return

		if self.status['status'] == 'stopped':
			print "TODO: I need to keep track of what file is loaded"

		elif self.status['status'] == 'paused':
			self.mp.pause()
			self.status['status'] = 'playing'

		elif self.status['status'] == 'playing':
			self.mp.pause()
			self.status['status'] = 'paused'

		else:
			print "WARNING: Unknown status: %s" % (self.status['status'])


		self.setStatus( self.status['status'] )

	def on_tbStop_clicked(self, button):
		"""
		Stop button event
		"""

		if self.status['status'] == 'stopped':
			return

		if self.mp.stop():
			self.setStatus('stopped')
		else:
			print "WARNING: stop command failed"



	def setStatus(self, status):

		"""
		Update button icons based on status
	
		"""

		print "Setting status to '%s'" % (status)

		button = self.widgets.get_widget("tbPlay")

		if status == 'playing' :
			button.set_stock_id(gtk.STOCK_MEDIA_PAUSE)

		elif status == 'stopped':
			button.set_stock_id(gtk.STOCK_MEDIA_PLAY)

		elif status == 'paused':
			button.set_stock_id(gtk.STOCK_MEDIA_PLAY)

		else:
			button.set_stock_id(gtk.STOCK_MEDIA_PLAY)

	def on_tbBack_clicked(self, button):
		"""
		Back button event. I go back in the playlist.
		"""

		print "Back clicked"

	def on_tbForward_clicked(self, button):

		"""
		Forward button event. I go forward in the playlist.
		"""
		print "Forward clicked"
		
	def on_btnConnect_clicked(self, button):
		"""
		Connect button in the Connect dialog event
		"""

		print "Connecting..."

		connectWindow = self.widgets.get_widget("winConnect")
		hostWidget = self.widgets.get_widget("entryConnectHost")
		portWidget = self.widgets.get_widget("entryConnectPort")

		host = hostWidget.get_text()
		port = int( portWidget.get_text() )

		self.connect(host, port)

		connectWindow.hide()



	def connect(self, host, port):

		"""
		Helper function to get connected to host and port
		"""

		r = self.mp.connect( host, port )

		if not r:
			self.setStatusbar("Unable to connect to %s:%d (Error: %s)" % (host, port, self.mp.error) )
			return

		progressBar = self.widgets.get_widget("progressbarConnect")

		self.loadFiles(progressBar)

		self.status = self.mp.status()

		self.setStatus( self.status['status'] )


	def on_winConnect_delete_event(self, win, gdkEvent):

		"""
		Delete and Destroy events, Hides the connect window and cancels the destroy
		"""

		connectWindow = self.widgets.get_widget("winConnect")
		connectWindow.hide()
		return True

	def on_btnConnectCancel_clicked(self, button):

		"""
		Cancel button event ine the Connect dialog
		"""

		connectWindow = self.widgets.get_widget("winConnect")
		connectWindow.hide()

	def Browser_visible_func(self, listStore, iter, None):
		"""
		I am the visible function for the Browser
		"""

		filename = listStore.get_value(iter, 2)
		
		if filename is None or filename is '..':
			return True

		if filename[0] == '.' and self.config.get("browser", "show_all") == 'False':

			return False

		return True

	def loadFiles(self, progressBar):
		"""
		Load files by issuing an ls to mplayerd. 
		Pulsing a progressBar while populating the treeBrowse listStore.
		progressBar can be None to omit the pulse.
		"""

		self.cwd = self.mp.pwd()

		print "cwd: %s" % (self.cwd)

		tree = self.widgets.get_widget("treeBrowse")

		listStore = tree.get_model()

		listStore.clear()

		ls = self.mp.ls()

		self.setStatusbar("Loading files...")

		iter = listStore.append()
		listStore.set(iter, 0, 0, 1, 'd', 2, '..')

		if progressBar:
			progressBar.show()

		show_all = False

		if self.config.get("browser", "show_all") == 'True':
			show_all = True

		print "Start load", time.time()
		for id, type, file in ls:

			if show_all is False and file[0] == '.':
				continue

			iter = listStore.append()
			listStore.set(iter, 0, id, 1, type, 2, file)


			if progressBar:
				progressBar.pulse()

		print "End load", time.time()

		if progressBar:
			progressBar.hide()

		self.setStatusbar("files loaded")


	def on_treeBrowse_row_activated(self, treeview, path, column):

		"""
		Event when a row is double-clicked
		Loads the currently selected song
		"""

		liststore = treeview.get_model()
		iter = liststore.get_iter(path)

		id = liststore.get_value(iter, 0)
		type = liststore.get_value(iter, 1)
		filename = liststore.get_value(iter, 2)

		progressBar = self.progressBar


		if type == 'd':
			if not self.mp.cd(filename):
				print "ERROR: Unable to cd to '%s'" % (filename)
				return 

			entryPath = self.widgets.get_widget("entryPath")
			entryPath.set_text( self.mp.pwd() )

			self.loadFiles(progressBar)

		else:

			if self.status['status'] == 'paused' or self.status['status'] == 'playing':
				self.mp.stop()

			self.mp.load(filename)

			self.setStatus("playing")

		print "Filename: %s" % (filename)


	def on_tbConnect_clicked(self, button):

		"""
		Toolbar connect button clicked event. I show the connect dialog
		"""
		connectWindow = self.widgets.get_widget("winConnect")
		connectWindow.show()


	def on_entryConsole_key_release_event(self, entryConsole, gdkEvent):

		command_line = entryConsole.get_text()

		if gdkEvent.keyval == 65293:
			resp = self.consoleExecute(command_line)

			ConsoleWindow = self.widgets.get_widget("txtViewConsole")
			buffer = ConsoleWindow.get_buffer()
			iter = buffer.get_end_iter()

			buffer.insert(iter, '# %s\n' % (command_line) )

			for line in resp:
				buffer.insert(iter, '>> ' + line + '\n')

			buffer.insert(iter, '\n')

			scrollmark = buffer.get_mark('scrollmark')		
			buffer.move_mark(scrollmark, buffer.get_end_iter())
			ConsoleWindow.scroll_mark_onscreen(scrollmark)

			entryConsole.set_text('')

	def consoleExecute(self, command_line):
		"""
		Execute command_line and return response
		"""

		resp = self.mp.command(command_line)

		resp_lines = resp.split("\r\n")

		return resp_lines[1:-1]

	def on_tbOptions_clicked(self, button):

		"""
		Options button clicked
		"""

		winOptions = self.widgets.get_widget("winOptions")

		winOptions.show()

	def run(self, argv):

		"""
		Start the main GTK loop
		"""
		self.argv = argv

		self.setStatusbar("No Connection")
		gtk.main()


	def setStatusbar(self, text):
	
		"""
		Update the statusbar text
		"""

		status_bar = self.widgets.get_widget("statusbar1")

		status_bar.push(status_bar.get_context_id("message"), text)


	def gtk_main_quit(self, win):
		"""
		Main application quit routine, Save config files, disconnect and exit!
		"""

		self.config.write()
		self.mp.disconnect()	
		gtk.main_quit()


	def on_entrySearch_key_press_event(self, gtkEntry, gdkEvent):

		"""
		Perform a search (for each letter keypress).
		"""

		print "Search incomplete"

	def on_btnSearch_clicked(self, button):
		"""
		Search button click event
		"""

		print "Search is incomplete"

	def on_togBrowser_clicked(self, button):
		"""
		Toggles browser window (artist, album lists)
		"""

		browser = self.widgets.get_widget('hpanBrowser')
		if button.get_active():
			button.set_label("Hide Browser")
			browser.show()
		else:
			button.set_label("Show Browser")
			browser.hide()



	# menu items
	def on_about1_activate(self, menu):
		winAbout = self.widgets.get_widget('winAbout')
		winAbout.show()
		print "About..."

	def on_btnAboutClose_clicked(self, button):
		winAbout = self.widgets.get_widget('winAbout')
		winAbout.hide()
		return True

	def on_winAbout_destroy_event(self, win, gdkEvent):

		winAbout = self.widgets.get_widget('winAbout')
		winAbout.hide()
		return True

	def on_btnUpdate_clicked(self, button):
		print "TODO: Updating library.. please wait..."
		
	def on_btnAddSource_clicked(self, button):
		print "Add Source..."

		self.AddSource = BasicObject()

		winAddSource = self.widgets.get_widget("winAddSource")
		winAddSource.show()


	# library filechooser "Destroy Window" event
	def on_filechooserLibrary_destroy_event(self, win, gdkEvent):

		fileChooser = self.widgets.get_widget("filechooserLibrary")
		fileChooser.hide()

	# library filechooser "Delete Window" event
	def on_filechooserLibrary_delete_event(self, win, gdkEvent):

		print "Delete event here!"
		fileChooser = self.widgets.get_widget("filechooserLibrary")
		fileChooser.hide()

		return True

	# library filechooser Cancel button
	def on_btnLibraryCancel_clicked(self, button):

		fileChooser = self.widgets.get_widget("filechooserLibrary")
		fileChooser.hide()

	# library filechooser Open button
	def on_btnLibraryOpen_clicked(self, button):

		print "library filechooser Open button clicked.."

		fileChooser = self.widgets.get_widget("filechooserLibrary")
		fileChooser.hide()

	# about dialog "delete" event
	def on_winAbout_delete_event(self, win, gdkEvent):
		winAbout = self.widgets.get_widget("winAbout")
		winAbout.hide()
		return True


	def on_btnMPAddSource_clicked(self, button):
		winAddSource = self.widgets.get_widget("winAddSource")

		print "MPAddSource button clicked.. I need to add source here..."

		winAddSource.hide()

	def on_btnAddSourceCancel_clicked(self, button):

		winAddSource = self.widgets.get_widget("winAddSource")

		winAddSource.hide()

	def on_winAddSource_destroy_event(self, win, gdkEvent):

		winAddSource = self.widgets.get_widget("winAddSource")
		winAddSource.hide()
		return True


	def on_btnOptionsCancel_clicked(self, button):
		winOptions = self.widgets.get_widget("winOptions")
		winOptions.hide()				

	def on_winOptions_destroy_event(self, win, gdKEvent):
		winOptions = self.widgets.get_widget("winOptions")
		winOptions.hide()				
		return True

	def on_btnOptionsOK_clicked(self, button):

		winOptions = self.widgets.get_widget("winOptions")

		checkButtonConnectStartup = self.widgets.get_widget("checkButtonConnectStartup")
		self.config.set("pyTunes", "StartUPConnect", checkButtonConnectStartup.get_active() )

		self.config.save()

		winOptions.hide()				
		

	def on_btnAddSourceConnect_clicked(self, button):

		"""
		I am fired when the connect button is clicked in the Add Source Dialog
		"""


	def on_entryPath_key_release_event(self, entry, gdkEvent):

		"""
		I am fired when the enter key is pressed in the Browser Tab
		"""

		if gdkEvent.keyval == 65293:

			if self.mp.cd(entry.get_text()):

				self.loadFiles(None)
			else:
				print "TODO: Give a better error here. This directory doesn't exist."


	def on_treeMusic_button_release_event(self, tree, gdkEvent):

		print "TODO: Pop-up context menu"
		print "INFO: tree", tree, " gdkEvent", gdkEvent
			

	def on_treeBrowse_button_release_event(self, tree, gdkEvent):
		"""
		I am the button release event for the browser tree
		"""

		if gdkEvent.button == 3:
			menu = self.menus['browse_menu']
			
			menu.popup(None, None, None, gdkEvent.button, gdkEvent.time)
	

	def on_browse_add_to_playlist1_activate(self, menu):

		print "TODO: Add to browse playlist"

	def on_browse_tog_show_all(self, tog):

		if tog.active:
		
			self.config.set("browser", "show_all", 'True')
		else:
			self.config.set("browser", "show_all", 'False')

		self.loadFiles(None)

	def on_hscrollbarProgress_value_changed(self, scrollbar):

		percentage = scrollbar.get_value()
		print "seeking to", percentage
		self.mp.seek_percent( int( percentage ) )

class BasicObject:

	"""
	For now I am just a simple object to allow hold atrributes in one spot
	"""

	pass
