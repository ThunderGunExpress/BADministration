#!/usr/bin/python
import cmd
from Modules.Solarwinds.solarwinds import *
from Modules.McAfee.mcafee import *
from Modules.Acronis.acronis import *
from Modules.Common.common import *

#https://stackoverflow.com/questions/5822164/object-inheritance-and-nested-cmd
#https://stackoverflow.com/questions/34145686/handling-argparse-escaped-character-as-option

class MainMenu(BADminConsole):
	def __init__(self, context):
        	BADminConsole.__init__(self, context)
	        self.solarwinds = Solarwinds_Main(context)	
		self.mcafee = McAfee_Main(context)      
		self.acronis = Acronis_Main(context)
		context.print_title()  	        
		self.prompt = '[BADministration]#'
		self.modules = ['mcafee', 'solarwinds', 'acronis']

	def do_solarwinds(self, args):
		"""Solarwinds parent BADministration module"""
        	self.solarwinds.cmdloop()

	def do_mcafee(self, args):
		"""McAfee parent BADministration module"""		
		self.mcafee.cmdloop()

	def do_acronis(self, args):
		"""Acronis parent BADministration module"""		
		self.acronis.cmdloop()

	def do_show_modules(self, args):
		"""Prints available parent modules"""
		print self.modules

	def do_exit(self, args):
		"""Exit"""
        	return True

if __name__ == '__main__':
	context = BADminContext()
	con = MainMenu(context)
	con.cmdloop()