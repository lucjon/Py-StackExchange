#!/usr/bin/env python
# Quick 'n' Dirty SO Monitor

import sys
sys.path.append('..')
import stackexchange, gtk, gobject, webkit

class SOMonitor(object):
	def __init__(self):
		self.window = gtk.Window()
		self.site = stackexchange.Site(stackexchange.StackOverflow)
		self.questions = []

		self.prepare_gui()
		self.ontick()
	
	def main(self):
		self.window.show_all()
		self.sw_holder.hide()
		gtk.main()

	def prepare_gui(self):
		gobject.timeout_add(300000, self.ontick)

		# VBox 1: VBox|Webkit (hidden)
		vb_pri = gtk.VBox()
		self.window.add(vb_pri)
		self.vb_pri = vb_pri

		vb_sec = gtk.VBox()
		vb_pri.pack_start(vb_sec)
		self.vb_sec = vb_sec

		sw_holder = gtk.ScrolledWindow()
		wk_browse = webkit.WebView()
		sw_holder.add(wk_browse)
		vb_pri.pack_start(sw_holder)

		self.sw_holder = sw_holder

	def questions_update(self):
		self.vb_sec = gtk.VBox()
		
		for q in self.questions:
			text = q.title
			btn  = gtk.Button(text)

			self.vb_sec.pack_start(btn)
			btn._question = q
			btn.connect('clicked', self.qbtn_clicked)
	
	def qbtn_clicked(self, btn):
		self.wk_browse.open('http://stackoverflow.com/questions/' + str(btn._question.id))
		self.sw_holder.show()
		
	def ontick(self):
		self.questions = self.site.recent_questions()
		self.questions_update()

		return True

SOMonitor().main()
