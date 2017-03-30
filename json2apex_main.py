import sys, os.path, imp, json
import sublime, sublime_plugin
from sys import modules
from imp import reload

BASE_PATH = os.path.abspath(os.path.dirname(__file__)).split('/')[-1]
INNER_CODE_DIRS = [
  'helpers',
]

EXT_PLUGIN_DIRS = []
MODULE_DIRS = list(map(lambda el: BASE_PATH + os.sep + el, INNER_CODE_DIRS))
MODULE_DIRS += EXT_PLUGIN_DIRS

globals_var = globals()

loader_path = os.path.abspath(os.path.dirname(__file__)) + os.sep + 'module_loader' + os.sep

fileObject, file, description = imp.find_module( 'loader', [ loader_path ] )
globals_var[ 'loader' ] = imp.load_module ( 'loader', fileObject, file, description )

loader.load ( MODULE_DIRS, globals() )

class SchemaToApexCommand(sublime_plugin.TextCommand):
	apexClassView = {}
	classList = []
	
	def run(self, edit):
		api_object = self.getContent()
		if(api_object is not None):
			print(' dwdxs')
			self.generateCode(edit, api_object)

	def getContent(self):
		try:
			contents = self.view.substr(sublime.Region(0, self.view.size()))
			return contents
		except ValueError:
			sublime.error_message('Invalid JSON')
			return None

	def generateCode(self, edit, api_object):
		pattern = PatternClass.Pattern.fromString('PatternClass', api_object)
		gen = pattern.generateCode()
		del(pattern)
		self.classList = ["PatternClass"]
		self.apexClassView = sublime.active_window().new_file()
		self.apexClassView.set_syntax_file('Packages/MavensMate/sublime/lang/Apex.sublime-syntax')
		self.apexClassView.insert(edit, 0, gen)

		self.renameClass()

	def renameClass(self):
		args = {
			'classList': self.classList
		}
		print(args)
		self.apexClassView.run_command('launch_class_renaming', args)

class JsonToApexCommand(sublime_plugin.TextCommand):
	apexClassView = {}
	classList = []

	def run(self, edit):
		api_object = self.getContent()
		if(api_object is not None):
			self.generateCode(edit, api_object)

	def getContent(self):
		try:
			contents = self.view.substr(sublime.Region(0, self.view.size()))
			api_object = json.loads(contents)
			return api_object
		except ValueError:
			sublime.error_message('Invalid JSON')
			return None

	def generateCode(self, edit, api_object):
		converter = JSON2ApexLib.SampleConverter()
		gen = converter.generateFromSample(api_object)
		self.classList = ["API", "Root_object"]
		self.classList += list(converter.formedClasses.values())
		print(self.classList)
		self.apexClassView = sublime.active_window().new_file()
		self.apexClassView.set_syntax_file('Packages/MavensMate/sublime/lang/Apex.sublime-syntax')
		self.apexClassView.insert(edit, 0, gen)

		self.renameClass()
		
		del(converter)

	def renameClass(self):
		args = {
			'classList': self.classList
		}
		print(args)
		self.apexClassView.run_command('launch_class_renaming', args)

class LaunchClassRenamingCommand(sublime_plugin.TextCommand):
	apexView = {}
	classList = []
	oldClassName = ''

	def run(self, edit, classList):
		self.apexView = self.view
		self.classList = classList
		curWin = self.apexView.window()
		self.oldClassName = self.classList.pop(0)

		matches = self.apexView.find_all(self.oldClassName)
		self.apexView.sel().clear()
		self.apexView.sel().add_all(matches)

		tryout = curWin.show_input_panel('Rename ' + self.oldClassName, self.oldClassName, self.rename, None, None)
		tryout.sel().add(tryout.visible_region())

	def rename(self, newName):
		args = {
			'oldClassName': self.oldClassName,
			'newClassName': newName,
			'classList': self.classList
		}
		self.apexView.run_command('rename_apex_class', args)

class RenameApexClassCommand(sublime_plugin.TextCommand):
	def run(self, edit, oldClassName, newClassName, classList):
		matches = self.view.find_all(oldClassName)
		reg_end = 0
		for m in matches:
			cur_m = self.view.find(oldClassName, reg_end)
			reg_end = m.end()
			self.view.replace(edit, cur_m, newClassName)
		if(0 < len(classList)):
			args = {
				'classList': classList
			}
			self.view.run_command('launch_class_renaming', args)
		else:
			self.view.sel().add(sublime.Region(0, self.view.size()))