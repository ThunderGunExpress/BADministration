#!/usr/bin/python
import click
from pyfiglet import Figlet
from Solarwinds.solarwinds import *
from Mcafee.mcafee import *

#https://stackoverflow.com/questions/46440950/require-and-option-only-if-a-choice-is-made-when-using-click/46662521
class OptionRequiredIf(click.Option):
	def __init__(self, *a, **k):
        	try:
		        option = k.pop('option')
		        value  = k.pop('value')
	        except KeyError:
        		raise(KeyError("OptionRequiredIf needs the option and value keywords arguments"))

		click.Option.__init__(self, *a, **k)
	        
		self._option = option
        	self._value = value

	def full_process_value(self, ctx, value):
		value = super(OptionRequiredIf, self).full_process_value(ctx, value)
		for v in self._value:
			if value is None and ctx.params[self._option] == v:	
				msg = 'Required if --{}={}'.format(self._option, self._value)
				raise click.MissingParameter(ctx=ctx, param=self, message=msg)
		return value
		
@click.command()
#Command Commands
@click.option('-v','--verbose', is_flag=True, help="Add verbosity")
@click.option('-m','--module', required=True, help="BADministration modules", type=click.Choice(['solarwinds-enum', 'solarwinds-syscmd', 'solarwinds-listalerts', 'solarwinds-alertremove', 'mcafee-enum', 'mcafee-listpackages', 'mcafee-removepackage', 'mcafee-uploadpackage', 'mcafee-listtasks', 'mcafee-createtask', 'mcafee-runtask', 'mcafee-removetask']))
@click.option('-u','--username', required=True, help="Target webportal username")
@click.option('-p','--password', required=True, help="Target webportal password")
@click.option('-t','--target', required=True, help="Target IP address")
@click.option('-po','--port', option='module', value=['mcafee-enum', 'mcafee-listpackages', 'mcafee-removepackage', 'mcafee-uploadpackage', 'mcafee-createtask', 'mcafee-listtasks', 'mcafee-runtask', 'mcafee-removetask'], cls=OptionRequiredIf, help="Target port")
@click.option('-c','--command', option='module', value=["solarwinds-syscmd"], cls=OptionRequiredIf, help="Command to execute")
@click.option('-s','--systems', option='module', value=["mcafee-runtask"], cls=OptionRequiredIf, help="McAfee systems to target")
@click.option('-pi','--packageid', option='module', value=["mcafee-removepackage", "mcafee-createtask"], cls=OptionRequiredIf, help="McAfee package product ID")
@click.option('-pb','--packagebranch', option='module', value=["mcafee-uploadpackage"], cls=OptionRequiredIf, help="McAfee package branch")
@click.option('-pl','--packagelocation', option='module', value=["mcafee-uploadpackage"], cls=OptionRequiredIf, help="McAfee package location")
@click.option('-tn','--taskname', option='module', value=["mcafee-createtask", "mcafee-runtask", "mcafee-removetask"], cls=OptionRequiredIf, help="McAfee client taskname")

def main(verbose, module, username, password, target, port, command, packageid, packagebranch, packagelocation, taskname, systems):
	click.echo()
	if module == "solarwinds-enum":
		sw_enumerate(target, username, password, verbose)
	if module == "solarwinds-alertremove":
		sw_system_cleanup(target, username, password, verbose)
	if module == "solarwinds-listalerts":
		sw_list_alerts(target, username, password, verbose)	
	if module == "solarwinds-syscmd":
		sw_system_shell(target, username, password, command, verbose)
	if module == "mcafee-listpackages":
		mc_listpackages(target, username, password, port, verbose)
	if module == "mcafee-removepackage":
		mc_removepackage(target, username, password, port, packageid, verbose)
	if module == "mcafee-uploadpackage":
		mc_uploadpackage(target, username, password, port, packagelocation, packagebranch, verbose)
	if module == "mcafee-createtask":
		mc_createdeploytask(target, username, password, port, taskname, packageid, verbose)
	if module == "mcafee-listtasks":
		mc_listtasks(target, username, password, port, "", verbose)
	if module == "mcafee-runtask":
		mc_runtask(target, username, password, port, taskname, systems, verbose)	
	if module == "mcafee-removetask":
		mc_removetask(target, username, password, port, taskname, verbose)	
	elif module == "mcafee-enum":
		mc_enumerate(target, username, password, port, verbose)
		
if __name__ == "__main__":
    	fig = Figlet(font='standard')
	print(fig.renderText('BADministration'))
	main()