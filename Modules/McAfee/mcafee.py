import requests
import urllib3
from cgi import escape
from prettytable import PrettyTable
from termcolor import colored
import os
import sys
from ..Common.common import BADminConsole

from mcafee_epo import Client

####https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input

class McAfee_Main(BADminConsole):
	def __init__(self, context):
		BADminConsole.__init__(self, context)
		self.prompt = '[BADministration\\mcafee]#'
		self.modules = ['enumerate', 'list_packages', 'remove_package', 'upload_package', 'create_task', 'list_tasks', 'remove_task', 'start_task']
		self.enumerate = McAfee_Enumerate(context)
		self.list_packages = McAfee_ListPackages(context)
		self.remove_package = McAfee_RemovePackage(context)
		self.upload_package = McAfee_UploadPackage(context)
		self.create_task = McAfee_CreateTask(context)
		self.list_tasks = McAfee_ListTasks(context)
		self.remove_task = McAfee_RemoveTask(context)
		self.start_task = McAfee_StartTask(context)

	def do_back(self, args):
        	return True

	def do_exit(self, args):
		sys.exit()

	def do_show_modules(self, args):
 	      	print self.modules

	def do_enumerate(self, args):
		self.enumerate.cmdloop()

	def do_list_pacakges(self, args):
		self.list_packages.cmdloop()

	def do_remove_pacakge(self, args):
		self.remove_package.cmdloop()
		
	def do_upload_pacakge(self, args):
		self.upload_package.cmdloop()

	def do_create_task(self, args):
		self.create_task.cmdloop()

	def do_list_tasks(self, args):
		self.list_tasks.cmdloop()

	def do_remove_task(self, args):
		self.remove_task.cmdloop()

	def do_start_task(self, args):
		self.start_task.cmdloop()


class McAfee_Helper():
	def headerdisplay(self, text):
		print colored('-------------------------------', 'grey', 'on_blue'),
		print colored(text.center(40, ' '), 'red', 'on_blue'),
		print colored('-------------------------------', 'grey', 'on_blue')

	def mc_connect(self, av_server, username, password, port):	
		try:
			requests.packages.urllib3.disable_warnings()
			mysess = requests.Session()
			mysess.verify = False
			mca = Client("https://" + av_server + ":" + port, username, password, mysess)	
			return mca

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')

	def mc_manualconnect(self, av_server, username, password, port):
		try:
			logindata = {
					'j_username':username,
					'j_password':password
			      	    }

			requests.packages.urllib3.disable_warnings()
			mcmanual = requests.session()
			mcmanual.verify = False

			mcmanual.get('https://' + av_server + ':' + port + '/core/orionSplashScreen.do')
			z = mcmanual.post('https://' + av_server + ':' + port + '/core/j_security_check', data=logindata)
	
			####Security Token Parsing
			securitytoken = None		

			for line in z.text.splitlines():
				if "name=\"orion.user.security.token\"" in line:			
					securitytoken = line.split('"')[7]
			
			if securitytoken == None:
				print "Error: Issue detecting security token."
				exit()

			mcmanual.get('https://' + av_server + ':' + port + '/core/orionSplashScreen.do')
	
			return mcmanual, securitytoken

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')
	
	def mc_lookuppkg(self, target, username, password, port, packageid):
		try:
			mcaconnection = self.mc_connect(target, username, password, port)
			pkgquery = mcaconnection('repository.findPackages', packageid)
			
			if len(pkgquery) == 0:
	        		print('No packages found.')
		       		return False, None, None, None

			if len(pkgquery) > 1:
				print('More than one package with that ID found. Exiting...')
				return False, None, None, None
		
			return True, pkgquery[0]["productDetectionProductVersion"], pkgquery[0]['packageBranch'], pkgquery[0]['packageType']

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')

	def mc_lookuptaskid(self, target, username, password, port, taskname):
		try:
			mcaconnection = self.mc_connect(target, username, password, port)
			taskquery = mcaconnection('clienttask.find', taskname)
	
			if len(taskquery) == 0:
        			print('Task not found.')
	       			return False, None

			if len(taskquery) > 1:
				print('More than one task with that name found.')
				return False, None
		
			return True, taskquery[0]["objectId"]

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')

	def mc_listtasks(self, target, username, password, port, taskname):
		try:
			####Connection
			mcaconnection = self.mc_connect(target, username, password, port)	

			####Header
			self.headerdisplay("McAfee ePO Client Task Enumeration")

			taskquery = mcaconnection('clienttask.find', taskname)	

			t = PrettyTable(['Taskname', 'Product Name', 'Type'])

			for r in taskquery:
				t.add_row([r['objectName'], r['productName'], r['typeName']])
			print t		

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')

class McAfee_Enumerate(BADminConsole):
	
	params = ['target', 'username', 'password', 'port']

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\\mcafee\\enumerate]#'		
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
			self.mc_enumerate()

	def mc_enumerate(self):
		try:
			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			port = self.context.Port
			verbose = False
			helper = McAfee_Helper()
		
			####Connection Setup
			mcaconnection = helper.mc_connect(target, username, password, port)	

			####Header
			helper.headerdisplay("McAfee ePO Enumeration")				
	
			####Query nodes
			nodequery = mcaconnection('system.find', '')

			if len(nodequery) == 0:
        			print('No nodes found.')
	       			return				

			t = PrettyTable(['ID', 'DisplayName', 'Domain', 'DNS', 'IP Address', 'Node Type', 'LoggedIn Username'])
		
			for r in nodequery:		
				t.add_row([r['EPOComputerProperties.ParentID'], r['EPOComputerProperties.ComputerName'], r['EPOComputerProperties.DomainName'], r['EPOComputerProperties.IPHostName'], r['EPOComputerProperties.IPAddress'], r['EPOComputerProperties.OSType'], r['EPOComputerProperties.UserName']])
			print t
			
		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')

class McAfee_ListPackages(BADminConsole):
	
	params = ['target', 'username', 'password', 'port']

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\\mcafee\\list_packages]#'		
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
			self.mc_listpackages()

	def mc_listpackages(self):
		try:
			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			port = self.context.Port
			verbose = False
			helper = McAfee_Helper()

			####Connection Setup
			mcaconnection = helper.mc_connect(target, username, password, port)	

			####Header
			helper.headerdisplay("McAfee ePO Package Enumeration")	

			####Query packages
			pkgquery = mcaconnection('repository.findPackages', '')
	
			if len(pkgquery) == 0:
        			print('No nodes found.')
	       			return

			t = PrettyTable(['Package ID', 'Package Type', 'Package Branch', 'Product Name', 'Product Version', 'Signer Name'])

			for r in pkgquery:
				if r['signerName'] == "McAfee":
					t.add_row([r['productID'], r['packageType'], r['packageBranch'], r['productName'], r['productDetectionProductVersion'], ""])
				else:
					t.add_row([r['productID'], r['packageType'], r['packageBranch'], r['productName'], r['productDetectionProductVersion'], r['signerName']])
			print t		
			
		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')

class McAfee_RemovePackage(BADminConsole):
	
	params = ['target', 'username', 'password', 'port', 'packageid']

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\\mcafee\\remove_package]#'		
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password, "Port": self.context.Port, "PackageId": self.context.PackageId }
	
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
			self.mc_removepackage()

	def mc_removepackage(self):
		try:
			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			port = self.context.Port
			packageid = self.context.PackageId
			verbose = False
			helper = McAfee_Helper()

			####Connection Setup
			mcaconnection = helper.mc_connect(target, username, password, port)	

			####Header
			helper.headerdisplay("McAfee ePO Remove Package")
	
			Success, nothing, pkgbranch, pkgtype = helper.mc_lookuppkg(target, username, password, port, packageid)

			if Success is False:
				return

			print colored("Removing the McAfee package is permanent, verify that the parameters are correct:", 'yellow', 'on_blue')
			print "Package ID: " + packageid
			print "Package Type: " + pkgtype
			print "Package Branch: " + pkgbranch
		
			if self.context.asktocontinue() is False:
				raise Exception("Stop all engines!")

			packageremove = mcaconnection('repository.deletePackage', packageid, pkgtype, pkgbranch)
			if packageremove == "true":
				print colored("Package remove successful", 'yellow', 'on_blue')
			else:
				print colored("Package remove failed", 'red', 'on_blue')
				
		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')

class McAfee_CreateTask(BADminConsole):
	
	params = ['target', 'username', 'password', 'port', 'taskname', 'packageid']

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\\mcafee\\create_task]#'		
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password, "Port": self.context.Port, "PackageId": self.context.PackageId, "TaskName": self.context.TaskName }
	
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
			self.mc_createdeploytask()

	def mc_createdeploytask(self):
		try:
			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			port = self.context.Port
			packageid = self.context.PackageId
			taskname = self.context.TaskName
			verbose = False
			helper = McAfee_Helper()

			####Header
			helper.headerdisplay("McAfee ePO Create Deploy Task")		

			####Get Package Version Number ... Janky :S
			Success, prodver, pkgbranch, nothing = helper.mc_lookuppkg(target, username, password, port, packageid)

			if Success is False:
				return

			####Sanity Check
			print colored("Create McAfee deploy client task, verify that the parameters are correct:", 'yellow', 'on_blue')
			print "Taskname: " + taskname
			print "Package ID & Version: " + packageid + ':' + prodver		
			print "Package Branch: " + pkgbranch
	
			if self.context.asktocontinue() is False:
				raise Exception("Stop all engines!")
	
			####Connection Setup
			mcaconnection, securitytoken = helper.mc_manualconnect(target, username, password, port)

			####Get PolicyMgmt Cookie
			mcaconnection.get('https://' + target + ':' + port + '/PolicyMgmt/taskcatalog/typePaneMenu.js')
		
			###
			taskstage1 = (
					('orion.user.security.token', securitytoken),
					('typeSelected', '2'),
					('taskType', '2'),
					('returnTo', '/PolicyMgmt/TaskCatalog.do'),
					('nodeID', '')
				     )

			taskstagereq1 = mcaconnection.post('https://' + target + ':' + port + '/PolicyMgmt/newTask.do', data=taskstage1)
				
			taskstage2 = (
					('orion.user.security.token', securitytoken),
					('orion.user.security.token', securitytoken),	#I see it too			
					('taskname', taskname), 
					('taskdesc', ''),
					('hiddenID_LocationItemIDList', '1'), 
					('hiddenID_SelectedPlatforms', 'WIN95|WIN98|WINME|WNTS|WNTW|WXPW|WXPS|WXPHE|WXPE|W2KS|W2KW|WVST|WVSTS|WNT7W|WIN8W|WIN8S|WINXW|WINXS'),
					('Checkbox_Windows', 'on'),
					('select_location_1', packageid + ':' + prodver),
					('select_action_1', 'Install'),
					('select_language_1', '0000'),
					('select_branch_1', pkgbranch),
					('select_hidden_value_1', ''),
					('cmd_line_1', ''),
					('select_platform_1', 'W2KAS|W2KDC|W2KS|W2KW|WIN8S|WIN8W|WINXS|WINXW|WNT7W|WVST|WVSTS|WXPE|WXPHE|WXPS|WXPW'),
					('maxNumberPostpone', '1'),
					('postpneTimeoutInterval', '20'),
					('postponeText', ''),
					('cmd_line_@ID', ''),
					('ajaxMode', 'standard')
				      )

			taskstagereq2 = mcaconnection.post('https://' + target + ':' + port + '/PolicyMgmt/saveTask.do', data=taskstage2)		

			if taskstagereq2.status_code != requests.codes.ok:
				print colored("Task creation failed", 'red', 'on_blue')
				return

			print colored("Verifying client task was created", 'yellow', 'on_blue')		

			helper.mc_listtasks(target, username, password, port, "")

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')


class McAfee_UploadPackage(BADminConsole):

	params = ['target', 'username', 'password', 'port', 'packagepath', 'packagebranch']

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\\mcafee\\upload_package]#'		
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password, "Port": self.context.Port, "PackagePath": self.context.PackagePath, "PackageBranch": self.context.PackageBranch }
	
	def do_show_options(self, args):
		"""Shows required parameters"""
		print colored("PackagePath is the local path to the EEDK zip file.", 'yellow', 'on_blue')
		print colored("PackageBranch is the target branch the package will be uploaded to, use Current if unsure.", 'yellow', 'on_blue')
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
			self.mc_uploadpackage()

	def mc_uploadpackage(self):
		try:

			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			port = self.context.Port
			packagelocation = self.context.PackagePath
			packagebranch = self.context.PackageBranch

			verbose = False
			helper = McAfee_Helper()
	
			####Header
			helper.headerdisplay("McAfee ePO Upload Package")

			####Connection Setup
			mcaconnection, securitytoken = helper.mc_manualconnect(target, username, password, port)

			####Sanity Check
			print colored("Uploading package, verify that the parameters are correct:", 'yellow', 'on_blue')
			print "Package Filename: " + os.path.basename(packagelocation)
			print "Package Path: " + os.path.abspath(packagelocation)
			print "Package Branch: " + packagebranch

			if self.context.asktocontinue() is False:
				raise Exception("Stop all engines!")

			####Craft Post Requests
			uploadstage1 = {
					'orion.user.security.token': (None, securitytoken), 
					'wizardCurrentPage': (None, 'choose'), 
					'packageOption': (None, '0'), 
					'packageFile': (os.path.basename(packagelocation), open(os.path.abspath(packagelocation), 'rb'), 'application/zip'), 
					'packageFileName': (None, 'C:\\fakepath\\' + os.path.basename(packagelocation)), 
					'orion.wizard.step': (None, 'next')
				       }

			packagestage1 = mcaconnection.post('https://' + target + ':' + port + '/RepositoryMgmt/updateCheckInStep1.do', files=uploadstage1)		

			uploadstage2 = {
					'orion.user.security.token': (None, securitytoken), 
					'packageVO': (None, None), 
					'wizardCurrentPage': (None, 'setup'),
					'branch': (None, 'Current'),
					'orion.wizard.step': (None, 'final')				
				       }

			packagestage2 = mcaconnection.post('https://' + target + ':' + port + '/RepositoryMgmt/updateCheckInStep2.do', files=uploadstage2)

			if packagestage2.status_code == requests.codes.ok:
				print colored("Package uploaded successful", 'yellow', 'on_blue')
			else:
				print colored("Package uploaded failed", 'red', 'on_blue')

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')

class McAfee_ListTasks(BADminConsole):

	params = ['target', 'username', 'password', 'port', ]

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\\mcafee\\list_tasks]#'		
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
			self.mc_listtasks()

	def mc_listtasks(self):
		try:
			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			port = self.context.Port
			packageid = self.context.PackageId
			taskname = ""
			verbose = False
			helper = McAfee_Helper()

			helper.mc_listtasks(target, username, password, port, "")			

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')


class McAfee_RemoveTask(BADminConsole):

	params = ['target', 'username', 'password', 'port', 'taskname' ]

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\\mcafee\\remove_task]#'
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password, "Port": self.context.Port, "TaskName": self.context.TaskName }
	
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
			self.mc_removetask()


	def mc_removetask(self):
		try:
			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			port = self.context.Port
			packageid = self.context.PackageId
			taskname = self.context.TaskName
			verbose = False
			helper = McAfee_Helper()

			mcaconnection = helper.mc_connect(target, username, password, port)	

			####Header
			helper.headerdisplay("McAfee ePO Client Task Delete")

			####Connection Setup
			mcaconnection, securitytoken = helper.mc_manualconnect(target, username, password, port)

			Success, taskid = helper.mc_lookuptaskid(target, username, password, port, taskname)

			if Success is False:
				return

			####Get PolicyMgmt Cookie
			mcaconnection.get('https://' + target + ':' + port + '/PolicyMgmt/taskcatalog/typePaneMenu.js')

			removestage1 = (
					('orion.user.security.token', securitytoken),
					('toID', taskid),
					('ajaxMode', 'standard')				
				       )
	
			####Sanity Check
			print colored("Removing the following client task:", 'yellow', 'on_blue')
			print "Task Name: " + taskname
			print "Task ID: " + str(taskid)

			if self.context.asktocontinue() is False:
				raise Exception("Stop all engines!")

			removestagereq1 = mcaconnection.post('https://' + target + ':' + port + '/PolicyMgmt/DeleteTask.do', data=removestage1)

			print colored("Verifying task was removed", 'yellow', 'on_blue')
			helper.mc_listtasks(target, username, password, port, "")

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')


class McAfee_StartTask(BADminConsole):

	params = ['target', 'username', 'password', 'port', 'taskname', 'systems' ]

	def __init__(self, context):		
		BADminConsole.__init__(self, context)		
		self.prompt = '[BADministration\\mcafee\\start_task]#'		
		self.get_params()

	def get_params(self):
		self.requiredparams = {"Target": self.context.Target,"Username": self.context.Username, "Password": self.context.Password, "Port": self.context.Port, "TaskName": self.context.TaskName, "Systems": self.context.Systems }
	
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
			self.mc_runtask()

	def mc_runtask(self):
		try:
			####Variable conversion
			target = self.context.Target
			username = self.context.Username
			password = self.context.Password
			port = self.context.Port
			packageid = self.context.PackageId
			taskname = self.context.TaskName
			systems = self.context.Systems
			verbose = False
			helper = McAfee_Helper()

			mcaconnection = helper.mc_connect(target, username, password, port)

			####Header
			helper.headerdisplay("McAfee ePO Assign Client Task")

			taskquery = mcaconnection('clienttask.find', taskname)

			if len(taskquery) == 0:
        			print('No tasks found. Exiting...')
	       			exit()

			if len(taskquery) > 1:
				print('More than one task with that name found. Exiting...')
				exit()

			if systems.lower() == "all":
				nodequery = mcaconnection('system.find', '')

				if len(nodequery) == 0:
        				print('No nodes found.')
		       			return

				nodelist = ""			

				for r in nodequery:		
					nodelist += r['EPOComputerProperties.ComputerName'] + ","
				systems = nodelist[:-1]

			####Sanity Check
			print colored("Running the client task on the following systems:", 'yellow', 'on_blue')
			print "Task Name: " + taskname
			print "Target Systems: " + systems

			if self.context.asktocontinue() is False:
				raise Exception("Stop all engines!")

			taskassign = mcaconnection._session.get('https://' + target + ':' + port + '/remote/clienttask.run?names=' + systems + '&productId=' + taskquery[0]["productId"] + '&taskId=' + str(taskquery[0]["objectId"]), auth=(username,password))

			if taskassign.status_code == requests.codes.ok:
				print colored("Client task run successful", 'yellow', 'on_blue')
			else:
				print colored("Client task run failed", 'red', 'on_blue')

		except requests.exceptions.ConnectionError as error:
			print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
		except Exception as error:
			print colored("Error message - " + str(error), 'yellow', 'on_blue')
