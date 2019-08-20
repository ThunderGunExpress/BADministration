import requests
from prettytable import PrettyTable
from termcolor import colored
from cgi import escape
import json
import sys
from ..Common.common import BADminConsole

class Acronis_Main(BADminConsole):
	def __init__(self, context):
		BADminConsole.__init__(self, context)
		self.prompt = '[BADministration\\acronis]#'
		self.modules = ['enumerate', 'client_command', 'list_policy', 'remove_policy']
		self.enumerate = Acronis_Enumerate(context)
		self.client_command = Acronis_ClientCommand(context)
		self.list_policy = Acronis_ListPolicy(context)
		self.remove_policy = Acronis_RemovePolicy(context)	

	def do_back(self, args):
        	return True

	def do_exit(self, args):
		sys.exit()

	def do_show_modules(self, args):
 	      	print self.modules

	def do_enumerate(self, args):
		self.enumerate.cmdloop()

	def do_client_command(self, args):
		self.client_command.cmdloop()

	def do_list_policy(self, args):
		self.list_policy.cmdloop()

	def do_remove_policy(self, args):
		self.remove_policy.cmdloop()

class Acronis_Helper():

	def headerdisplay(self, text):
		print colored('-------------------------------', 'grey', 'on_blue'),
		print colored(text.center(40, ' '), 'red', 'on_blue'),
		print colored('-------------------------------', 'grey', 'on_blue')
		return

	def ac_connect(self, ac_server, username, password, port):	
		try:
			payload = {
		        	'machine': ac_server,
			        'username': username,
			        'password': password,
			        'remember': False,
		        	'type': 'ams',
			        'NonRequiredParams': ['username', 'password'],
    			}

			url = "https://" + ac_server + ":" + port + "/api/ams/session"
			requests.packages.urllib3.disable_warnings()
			mysess = requests.Session()
			mysess.verify = False
			#mysess.proxies = proxyDict
			response = mysess.post(url, data=json.dumps(payload))
		
			if response.status_code == 401:
				print colored("Invalid credentials. Connection failed to Acronis server - " + ac_server, 'yellow', 'on_blue')
				return False, None
		
			return True, mysess
		
		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to Acronis server - " + ac_server, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')

	def ac_listpolicy(self, target, username, password, port, acsession):
		try:	
			####Header
			self.headerdisplay("Acronis List Backup Policies")

			####Connection Setup
			
			if acsession is None:
				Success, acconnection = self.ac_connect(target, username, password, port)	
			else:
				acconnection = acsession
				Success = True

			if Success is False:
				print "Connection issue"
				return			

			####
			policies = acconnection.get("https://" + target + ":" + port + "/api/ams/backup/minimal_plans")

			if len(policies.json()) == 0:
        			print('No policies found.')
		       		return				

			#t = PrettyTable(['Policy Name', 'ID', 'Targets', 'BADministration Policy'])
			t = PrettyTable(['Policy Name', 'Targets', 'BADministration Policy'])
		
			BADminName = ""
			BADminId = ""

			for r in policies.json()['data']:
				poltargets = ""
				for p in r['sources']['data']:
					poltargets += p['displayName'] + ","
				if r['name'].lower() == "cpl_backup":				
					t.add_row([r['name'], poltargets[:-1], "True"])
					BADminName = r['name']
					BADminId = r['id']
				else:
					t.add_row([r['name'], poltargets[:-1], ""])
			print t
			return BADminName, BADminId
		
		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to Acronis server - " + ac_server, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')


	def ac_removepolicy(self, target, username, password, port, context, acsession):
		try:
			####Header
			self.headerdisplay("Acronis Remove BADministration Policy")

			####Connection Setup
			if acsession is None:
				Success, acconnection = self.ac_connect(target, username, password, port)	
			else:
				acconnection = acsession
				Success = True	

			if Success is False:
				print "Connection issue"
				return
	
			print "Attempting to delete BADministration task with hardcoded name - CPL_Backup"
			print "Listing current backup policies"

			BADminList = []

			BADminName, BADminId = self.ac_listpolicy(target, username, password, port, acconnection)
			if BADminId == "":
				print colored("BADministration task was not found. Exiting...", 'yellow', 'on_blue')
				return
			BADminList.insert(0, BADminId)
	
			print colored("Delete policy with the following details:", 'yellow', 'on_blue')
			print "Policy Name: " + BADminName
			print "Policy ID: " + BADminId
		
			if context.asktocontinue() is False:
				raise Exception("Stop all engines!")

			policystage = { "planIds":BADminList }
			policyheaders = {'Content-type': 'application/json; charset=utf-8'}
		
			deletestage = acconnection.post("https://" + target + ":" + port + "/api/ams/backup/plans_operations/remove_plans", data=json.dumps(policystage), headers=policyheaders)		
		
			if len(deletestage.json()) == 0:
				print colored("Policy successfully removed, running view policies one more time.", 'yellow', 'on_blue')
				self.ac_listpolicy(target, username, password, port, acconnection)
				return
			else:
				print colored("Policy NOT removed.", 'yellow', 'on_blue')
				return

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to Acronis server - " + ac_server, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')


class Acronis_Enumerate(BADminConsole):
	
	params = ['target', 'username', 'password', 'port']

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\\acronis\\enumerate]#'		
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password, "Port": self.context.Port }
	
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
			self.ac_enumerate()

	def ac_enumerate(self):
		try:		
			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			port = self.context.Port
			verbose = False
			helper = Acronis_Helper()
		
			####Header
			helper.headerdisplay("Acronis Enumeration")

			####Connection Setup
			Success, acconnection = helper.ac_connect(target, username, password, port)

			if Success is False:
				return

			####
			clients = acconnection.get("https://" + target + ":" + port + "/api/ams/infrastructure/agents")		

			if len(clients.json()) == 0:
	        		print('No nodes found.')
		       		return				

			t = PrettyTable(['Display Name', 'IP Addresses', 'Agent Version', 'Agent Type'])
			
			for r in clients.json()['data']:		
				ips = ""
				for i in r['Attributes']['ResidentialAddresses']: #Array of IPs
					ips += i + ","
				t.add_row([r['Attributes']['Name'], ips[:-1], r['Attributes']['Agents'][0]['Version'], r['Attributes']['Agents'][1]['Name']])
			print t
		
		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to Acronis server - " + ac_server, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')


class Acronis_ClientCommand(BADminConsole):
	
	params = ['target', 'username', 'password', 'port', 'systems', 'command']

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\\acronis\\client_command]#'		
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password, "Port": self.context.Port, "Systems": self.context.Systems, "Command": self.context.Command }
	
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
			self.ac_clientcmd()

	def ac_clientcmd(self):
		try:

			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			port = self.context.Port
			command = self.context.Command
			systems = self.context.Systems
			verbose = False
			helper = Acronis_Helper()
		
			####Header
			helper.headerdisplay("Acronis Backup Policy Deploy")

			####Connection Setup
			Success, acconnection = helper.ac_connect(target, username, password, port)

			if Success is False:
				return

			####
			sysformat = systems.split(',')

			####
			resources = acconnection.get("https://" + target + ":" + port + "/api/ams/resources")

			if len(resources.json()) == 0:
        			print('No nodes found.')
	       			return

			targetarray = []		

			for r in resources.json()['data']:					
				if list(r.keys())[0] == "status":
					if r['title'].lower() in map(lambda x: x.lower(), sysformat):
						targetarray.append([r['title'], r['id']])				
					elif sysformat[0].lower() == "all":
						targetarray.append([r['title'], r['id']])
					else:
						for i in r['ip']:
							if i in sysformat:
								targetarray.append([r['title'], r['id']])

			t = PrettyTable(['Display Name'])

			for z in targetarray:
				t.add_row([z[0]])

			print colored("BADministration backup policy will target the following systems:", 'yellow', 'on_blue')
			print t

			print colored("The following command will execute on target systems:", 'yellow', 'on_blue')
			print command

			if self.context.asktocontinue() is False:
				raise Exception("Stop all engines!")

			importfile = './Modules/Acronis/cpl_backup.json'
			backup = ''

			####Read in Acronis backup template. Will replace CMDGOESHERE with command variable	
			with open(importfile, 'r') as f:
				for line in f:
					if "CMDGOESHERE" in line:
						#backup += line.replace('CMDGOESHERE',json.dumps(command)[1:-1])
						backup += line.replace('CMDGOESHERE',json.dumps(command)[2:-2])
					elif "cpldisplayName" in line:
						position = -1
						for k in targetarray:				
							position += 1
							backup += "      {\r\n"
							backup += line.replace('cpldisplayName', k[0])
							backup += "	\"id\": \"" + k[1] + "\""
							if position == len(targetarray) - 1:
								backup += "\r\n      }\r\n"
							else:
								backup += "\r\n      },\r\n"
					elif "cplphmkey" in line:
						position = -1
						for k in targetarray:				
							position += 1
							backup += "      {\r\n"
							backup += line.replace('cplphmkey', k[1])
							backup += "	\"resource_key\": \"" + k[1] + "\""
							if position == len(targetarray) - 1:
								backup += "\r\n      }\r\n"
							else:
								backup += "\r\n      },\r\n"

					else:
						backup += line

			uploadstage = {
					'planfile': ('cpl_backup.json', backup, 'application/json')
			              }

			policystage = acconnection.post("https://" + target + ":" + port + "/api/ams/backup/plan_operations/import?createDraftOnError=true", files=uploadstage)

			if len(policystage.json()['data']['failedFiles']) != 0:
				print colored("Error creating backup policy, check backup policies.", 'yellow', 'on_blue')
				print "Error message: " + policystage.json()['data']['failedFiles'][0]['error']['reason']
				print "Error details: " + policystage.json()['data']['failedFiles'][0]['error']['cause']
				return

			print colored("Backup policy successfully deployed. Policy details:", 'yellow', 'on_blue')
			print "Uploaded Filename: " + policystage.json()['data']['importedPlans'][0]['fileName'] + "\r\nPlan ID: " + policystage.json()['data']['importedPlans'][0]['planId'] + "\r\n"			

			helper.ac_listpolicy(target, username, password, port, acconnection)

			enabledata = { "enabled": True }
			taskdata = { "planId":policystage.json()['data']['importedPlans'][0]['planId'] }
			taskheaders = {'Content-type': 'application/json; charset=utf-8'}

			enablestage = acconnection.put("https://" + target + ":" + port + "/api/ams/backup/plans/" + policystage.json()['data']['importedPlans'][0]['planId'] + "/enabled", data=json.dumps(enabledata), headers=taskheaders)

			print colored("Attempting to run backup task.", 'yellow', 'on_blue')
		
			taskstage = acconnection.post("https://" + target + ":" + port + "/api/ams/backup/plan_operations/run", data=json.dumps(taskdata), headers=taskheaders)			

			print colored("Proceed to remove BADministration policy, don't press \"y\" until policy command executes.", 'yellow', 'on_blue')

			if self.context.asktocontinue() is False:
				raise Exception("Stop all engines!")
		
			helper.ac_removepolicy(target, username, password, port, self.context, acconnection)
			
		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to Acronis server - " + ac_server, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')


class Acronis_ListPolicy(BADminConsole):
	
	params = ['target', 'username', 'password', 'port']

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\\acronis\\list_policy]#'		
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password, "Port": self.context.Port }
	
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
			self.ac_listpolicy()

	def ac_listpolicy(self):
		try:
			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			port = self.context.Port
			verbose = False
			helper = Acronis_Helper()

			helper.ac_listpolicy(target, username, password, port, None)			

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')


class Acronis_RemovePolicy(BADminConsole):
	
	params = ['target', 'username', 'password', 'port']

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\\acronis\\remove_policy]#'		
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password, "Port": self.context.Port }
	
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
			self.ac_removepolicy()

	def ac_removepolicy(self):
		try:
			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			port = self.context.Port
			verbose = False
			helper = Acronis_Helper()

			helper.ac_removepolicy(target, username, password, port, self.context, None)			

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')
