import requests
import urllib3
from cgi import escape
from prettytable import PrettyTable
from termcolor import colored
import os

from mcafee_epo import Client

####https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input

####BADministration header display
####Private
####
def headerdisplay(text):
	print colored('-------------------------------', 'grey', 'on_blue'),
	print colored(text.center(40, ' '), 'red', 'on_blue'),
	print colored('-------------------------------', 'grey', 'on_blue')
	return

####
####McAfee ePO API connection function
####Returns McAfee API connection client
####Private
####
def mc_connect(av_server, username, password, port):	
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

####
####McAfee ePO manual connection function
####Returns McAfee requests connection and security token used on most pages
####Private
####
def mc_manualconnect(av_server, username, password, port):
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

####
####McAfee lookup package information, used in task creation function
####Private
####
def mc_lookuppkg(target, username, password, port, packageid):
	try:
		mcaconnection = mc_connect(target, username, password, port)
		pkgquery = mcaconnection('repository.findPackages', packageid)
		
		if len(pkgquery) == 0:
        		print('No packages found. Exiting...')
	       		exit()

		if len(pkgquery) > 1:
			print('More than one package with that ID found. Exiting...')
			exit()
		
		return pkgquery[0]["productDetectionProductVersion"], pkgquery[0]['packageBranch'], pkgquery[0]['packageType']

	except requests.exceptions.ConnectionError as error:
		print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
	except Exception as error:
		print colored("Error message - " + str(error), 'yellow', 'on_blue')

####
####McAfee lookup task id, used in task removal function
####Private
####
def mc_lookuptaskid(target, username, password, port, taskname):
	try:
		mcaconnection = mc_connect(target, username, password, port)
		taskquery = mcaconnection('clienttask.find', taskname)
	
		if len(taskquery) == 0:
        		print('Task not found. Exiting...')
	       		exit()

		if len(taskquery) > 1:
			print('More than one task with that name found. Exiting...')
			exit()
		
		return taskquery[0]["objectId"]

	except requests.exceptions.ConnectionError as error:
		print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
	except Exception as error:
		print colored("Error message - " + str(error), 'yellow', 'on_blue')

####
####McAfee enumeration function
####Public
####
def mc_enumerate(target, username, password, port, verbose):
	try:
		####Connection Setup
		mcaconnection = mc_connect(target, username, password, port)	

		####Header
		headerdisplay("McAfee ePO Enumeration")				
	
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

####
####McAfee list packages
####Public
####
def mc_listpackages(target, username, password, port, verbose):
	try:
		####Connection Setup
		mcaconnection = mc_connect(target, username, password, port)	

		####Header
		headerdisplay("McAfee ePO Package Enumeration")	

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

####
####McAfee remove target package
####Public
####
def mc_removepackage(target, username, password, port, packageid, verbose):
	try:
		####Connection Setup
		mcaconnection = mc_connect(target, username, password, port)	

		####Header
		headerdisplay("McAfee ePO Remove Package")
	
		nothing, pkgbranch, pkgtype = mc_lookuppkg(target, username, password, port, packageid)

		print colored("Removing the McAfee package is permanent, verify that the parameters are correct:", 'yellow', 'on_blue')
		print "Package ID: " + packageid
		print "Package Type: " + pkgtype
		print "Package Branch: " + pkgbranch

		valid = {"yes", "y"}
		choice = raw_input("Continue? (y/n) ").lower()

		if choice in valid:		
			packageremove = mcaconnection('repository.deletePackage', packageid, pkgtype, pkgbranch)
			if packageremove == "true":
				print colored("Package remove successful", 'yellow', 'on_blue')
			else:
				print colored("Package remove failed", 'red', 'on_blue')
		else:
			print colored("Exiting...", 'yellow', 'on_blue')
			return
			
	except requests.exceptions.ConnectionError as error:
		print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
	except Exception as error:
		print colored("Error message - " + str(error), 'yellow', 'on_blue')

####
####McAfee create deploy task
####Public
####
def mc_createdeploytask(target, username, password, port, taskname, packageid, verbose):
	try:
		####Header
		headerdisplay("McAfee ePO Create Deploy Task")		

		####Get Package Version Number ... Janky :S
		prodver, pkgbranch, nothing = mc_lookuppkg(target, username, password, port, packageid)

		####Sanity Check
		print colored("Create McAfee deploy client task, verify that the parameters are correct:", 'yellow', 'on_blue')
		print "Taskname: " + taskname
		print "Package ID & Version: " + packageid + ':' + prodver		
		print "Package Branch: " + pkgbranch

		valid = {"yes", "y"}
		choice = raw_input("Continue? (y/n) ").lower()

		if choice not in valid:					
			print colored("Exiting...", 'yellow', 'on_blue')
			return

		####Connection Setup
		mcaconnection, securitytoken = mc_manualconnect(target, username, password, port)

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

		mc_listtasks(target, username, password, port, taskname, False)

	except requests.exceptions.ConnectionError as error:
		print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')
	except Exception as error:
		print colored("Error message - " + str(error), 'yellow', 'on_blue')

####
####McAfee upload package
####Public
####
def mc_uploadpackage(target, username, password, port, packagelocation, packagebranch, verbose):
	try:
		####Header
		headerdisplay("McAfee ePO Upload Package")

		####Connection Setup
		mcaconnection, securitytoken = mc_manualconnect(target, username, password, port)

		####Sanity Check
		print colored("Uploading package, verify that the parameters are correct:", 'yellow', 'on_blue')
		print "Package Filename: " + os.path.basename(packagelocation)
		print "Package Path: " + os.path.abspath(packagelocation)
		print "Package Branch: " + packagebranch

		valid = {"yes", "y"}
		choice = raw_input("Continue? (y/n) ").lower()

		if choice not in valid:					
			print colored("Exiting...", 'yellow', 'on_blue')
			return

		####Craft Post Requests
		uploadstage1 =  {
				'orion.user.security.token': (None, securitytoken), 
				'wizardCurrentPage': (None, 'choose'), 
				'packageOption': (None, '0'), 
				'packageFile': (os.path.basename(packagelocation), open(os.path.abspath(packagelocation), 'rb'), 'application/zip'), 
				'packageFileName': (None, 'C:\\fakepath\\' + os.path.basename(packagelocation)), 
				'orion.wizard.step': (None, 'next')
			       }

		packagestage1 = mcaconnection.post('https://' + target + ':' + port + '/RepositoryMgmt/updateCheckInStep1.do', files=uploadstage1)		

		uploadstage2 =  {
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

####
####McAfee list client tasks
####Public
####
def mc_listtasks(target, username, password, port, taskname, verbose):
	try:
		mcaconnection = mc_connect(target, username, password, port)	

		####Header
		headerdisplay("McAfee ePO Client Task Enumeration")

		taskquery = mcaconnection('clienttask.find', taskname)	

		t = PrettyTable(['Taskname', 'Product Name', 'Type'])

		for r in taskquery:
			t.add_row([r['objectName'], r['productName'], r['typeName']])
		print t		

	except requests.exceptions.ConnectionError as error:
		print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
	except Exception as error:
		print colored("Error message - " + str(error), 'yellow', 'on_blue')

####
####McAfee remove client task
####Public
####
def mc_removetask(target, username, password, port, taskname, verbose):
	try:
		mcaconnection = mc_connect(target, username, password, port)	

		####Header
		headerdisplay("McAfee ePO Client Task Delete")

		####Connection Setup
		mcaconnection, securitytoken = mc_manualconnect(target, username, password, port)

		taskid = mc_lookuptaskid(target, username, password, port, taskname)

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

		valid = {"yes", "y"}
		choice = raw_input("Continue? (y/n) ").lower()

		if choice not in valid:					
			print colored("Exiting...", 'yellow', 'on_blue')
			return

		removestagereq1 = mcaconnection.post('https://' + target + ':' + port + '/PolicyMgmt/DeleteTask.do', data=removestage1)

		print colored("Verifying task was removed", 'yellow', 'on_blue')
		mc_listtasks(target, username, password, port, "", False)

	except requests.exceptions.ConnectionError as error:
		print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
	except Exception as error:
		print colored("Error message - " + str(error), 'yellow', 'on_blue')

####
####McAfee run client task
####Public
####
def mc_runtask(target, username, password, port, taskname, systems, verbose):
	try:
		mcaconnection = mc_connect(target, username, password, port)

		####Header
		headerdisplay("McAfee ePO Assign Client Task")

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

		valid = {"yes", "y"}
		choice = raw_input("Continue? (y/n) ").lower()

		if choice not in valid:					
			print colored("Exiting...", 'yellow', 'on_blue')
			return
				
		taskassign = mcaconnection._session.get('https://' + target + ':' + port + '/remote/clienttask.run?names=' + systems + '&productId=' + taskquery[0]["productId"] + '&taskId=' + str(taskquery[0]["objectId"]), auth=(username,password))

		if taskassign.status_code == requests.codes.ok:
			print colored("Client task run successful", 'yellow', 'on_blue')
		else:
			print colored("Client task run failed", 'red', 'on_blue')

	except requests.exceptions.ConnectionError as error:
		print colored("Connection failed to ePO server - " + target, 'yellow', 'on_blue')	
	except Exception as error:
		print colored("Error message - " + str(error), 'yellow', 'on_blue')
