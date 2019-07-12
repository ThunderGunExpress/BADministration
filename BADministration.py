#!/usr/bin/python
import click
from pyfiglet import Figlet
from Solarwinds.solarwinds import *

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
@click.option('-m','--module', required=True, help="BADministration modules", type=click.Choice(['solarwinds-enum', 'solarwinds-syscmd', 'solarwinds-listalerts', 'solarwinds-alertremove']))
@click.option('-u','--username', required=True, help="Target webportal username")
@click.option('-p','--password', required=True, help="Target webportal password")
@click.option('-c','--command', option='module', value=["solarwinds-syscmd"], cls=OptionRequiredIf, help="Command to execute")
@click.option('-t','--target', required=True, help="Target IP address")
@click.option('-d','--disablechecks', is_flag=True, help="Disable santiy checks, very risky")
@click.option('-lp','--librarypath', option='module', value=["solarwinds-wmibomb"], cls=OptionRequiredIf, help="Placeholder")
@click.option('-sp','--scriptpath', option='module', value=["solarwinds-wmibomb"], cls=OptionRequiredIf, help="Placeholder")


def main(verbose, module, username, password, target, command, disablechecks, librarypath, scriptpath):
	click.echo()
	if module == "solarwinds-enum":
		sw_enumerate(target, username, password, verbose)
	if module == "solarwinds-alertremove":
		sw_system_cleanup(target, username, password, verbose)
	if module == "solarwinds-listalerts":
		sw_list_alerts(target, username, password, verbose)	
	elif module == "solarwinds-syscmd":
		sw_system_shell(target, username, password, command, verbose)
		
if __name__ == "__main__":
    	fig = Figlet(font='standard')
	print(fig.renderText('BADministration'))
	main()