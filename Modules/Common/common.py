from prettytable import PrettyTable
import argparse
import cmd
from pyfiglet import Figlet

class BADminConsole(cmd.Cmd):
	def __init__(self, context):
        	cmd.Cmd.__init__(self)
	        self.context = context

class BADminContext(object):
	def __init__(self):
        	self.Target = None
		self.Username = None
		self.Password = None
		self.Port = None
		self.Command = None
		self.PackageId = None
		self.PackagePath = None
		self.PackageBranch = None
		self.TaskName = None
		self.Systems = None

	def print_title(self):
		fig = Figlet(font='standard')
		print(fig.renderText('BADministration'))

	def asktocontinue(self):
		try:
			valid = {"yes", "y"}
			choice = raw_input("Continue? (y/n) ").lower()
			if choice not in valid:
				print "Exiting ..."
				return False
			else:
				return True

		except Exception as e:
			print e
			return

	def argumentparser(self, args):
		try:
			commands = ['target', 'username', 'password', 'port', 'command', 'packageid', 'packagepath', 'packagebranch', 'taskname', 'systems']			
			format_args = args.split()					
			if format_args[0].lower() in commands:
				for r in commands:
					format_args[0] = format_args[0].lower().replace(r, "--" + r)									
			else:
				print "Parameter issue"
				return	
			
			##Surely there is a better way
			##Don't call me Surely
			parse_list = []
			parse_list.insert(0, format_args.pop(0))
																
			s = " "
			s = s.join(format_args)
			#s.replace("\\\\", "\\")
			#s.replace("\\", "")
			parse_list.append(s)

			print parse_list
											
			parser = argparse.ArgumentParser()
			parser.add_argument('--target')
			parser.add_argument('--username')
			parser.add_argument('--password')
			parser.add_argument('--port')
			parser.add_argument('--command', nargs="*")
			parser.add_argument('--taskname')
			parser.add_argument('--packageid')
			parser.add_argument('--packagebranch')
			parser.add_argument('--packagepath')
			parser.add_argument('--systems')
			arguments = parser.parse_args(parse_list)

			if arguments.target is not None:				
				self.Target = arguments.target
			
			if arguments.username is not None:
				self.Username = arguments.username
			
			if arguments.password is not None:
				self.Password = arguments.password

			if arguments.command is not None:
				self.Command = arguments.command
			
			if arguments.port is not None:
				self.Port = arguments.port

			if arguments.taskname is not None:
				self.TaskName = arguments.taskname

			if arguments.packageid is not None:
				self.PackageId = arguments.packageid

			if arguments.packagebranch is not None:
				self.PackageBranch = arguments.packagebranch

			if arguments.packagepath is not None:
				self.PackagePath = arguments.packagepath

			if arguments.systems is not None:
				self.Systems = arguments.systems
				
		except Exception as e:
			print e
			return

	def requiredparams(self, reqparams):
		t = PrettyTable(['Required Parameter', 'Current Setting'])
		for r in reqparams:			
			param = "self." + r
			#Ew!			
			t.add_row([r, eval(param)])			
		print t
		return