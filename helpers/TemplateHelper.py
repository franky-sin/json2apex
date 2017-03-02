import sys
import os
import json
import datetime
import os.path, imp, json
import re

template_dir = 'templates/'
template_extension = '.tmp'

TEMPLATE_CONSTS = {
	'_var': '{{',
	'_code': '{${',
	'_end': '}}',
	'_code_end': '}$}'
}

# template_args = {
# 	template_vars:{
# 		name: value
# 	},
# }

class Template():
	"""Arguments to be passed to template"""
	def __init__(self, template_name):
		self.template_name = template_name
		self.template_args = TemplateArgs()
		self.output = ''
		self.getTemplateCode()

	def getTemplateCode(self):
		path_to_template = template_dir + self.template_name + template_extension
		content = None
		with open(path_to_template) as f:
			content = f.read()
		self.template = content

	def addVar(self, var_name, var_value):
		self.template_args.addVar(var_name, var_value)

	def addCodeArgument(self, var_name, var_value):
		self.template_args.addCodeArgument(var_name, var_value)

	def addArgs(self, template_args):
		for ca_name, ca_value in template_args.template_vars.items():
			self.template_args.template_vars[ca_name] = ca_value
		for var_name, var_value in template_args.template_vars.items():
			self.template_args.template_vars[var_name] = var_value

	def findCodeOccurence(self):
		code_end_length = len(TEMPLATE_CONSTS['_code_end'])
		code_start = self.output.find(TEMPLATE_CONSTS['_code'])
		template_replace = self.output[code_start:]
		code_end = code_start + template_replace.find(TEMPLATE_CONSTS['_code_end']) + code_end_length
		code_occurence = self.output[code_start:code_end]
		return code_occurence

	def compileCode(self, code):
		code_locals = self.template_args.template_vars
		code_pure = code.replace(TEMPLATE_CONSTS['_code'],'').replace(TEMPLATE_CONSTS['_code_end'],'')
		code_pure = 'output = ' + code_pure
		compiled = compile(code_pure, '<string>', 'exec')
		exec(compiled, {}, code_locals)
		return code_locals['output']

	def compile(self, debug=False):
		self.output = self.template
		code = self.findCodeOccurence()
		while code:
			self.output = self.output.replace(code, self.compileCode(code))
			code = self.findCodeOccurence()
		template_vars = {}
		pattern = TEMPLATE_CONSTS['_var'] + '\w+' + TEMPLATE_CONSTS['_end']
		template_var_occurences = re.findall(pattern, self.output)
		for var_occ in template_var_occurences:
			key = var_occ.replace(TEMPLATE_CONSTS['_var'], '').replace(TEMPLATE_CONSTS['_end'], '')
			template_vars[key] = var_occ
		for name, placeholder in template_vars.items():
			if(debug):
				print('name >> ', name)
				print('placeholder >> ', placeholder)
				print('name in self.template_args.template_vars >> ', name in self.template_args.template_vars)
				if name in self.template_args.template_vars:
					print('str(self.template_args.template_vars[name]) >> ', str(self.template_args.template_vars[name]))
			if name in self.template_args.template_vars:
				self.output = self.output.replace(placeholder, str(self.template_args.template_vars[name]))
			else:
				self.output = self.output.replace(placeholder, '')
		if(debug):
			print('template >> ', self.output)
		output_splitted = self.output.split('\n')
		self.output = ''
		empty_prev = False
		for part in output_splitted:
			if(debug):
				print('part >> ', part)
				print("re.match(r'^\s*$', part) >> ", not not re.match(r'^\s*$', part))
				print('empty_prev >> ', not not empty_prev)
			if re.match(r'^\s*$', part) and empty_prev:
				pass
			else:
				self.output += '\n' + part
				empty_prev = re.match(r'^\s*$', part)
		self.output = ' '.join(filter(lambda x: not re.match(r'^\s*$', x) , self.output.split(' ')))
		self.output = self.output[1:]
		return self.output


class TemplateArgs():
	"""Arguments to be passed to template"""
	def __init__(self):
		self.template_vars = {}

	def addVar(self, var_name, var_value):
		self.template_vars[var_name] = var_value

	def addCodeArgument(self, var_name, var_value):
		self.template_vars[var_name] = var_value
		