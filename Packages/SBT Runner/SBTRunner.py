import os
import re
import sublime
import string
import sublime_plugin
import subprocess
import functools
import glob
import fnmatch
import threading


class SbtTestCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		CommandRunner().run_command(edit, "test-only", self)

class SbtRunCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		CommandRunner().run_command(edit, "run-main", self)

class SbtCompile(sublime_plugin.TextCommand):
	def run(self, edit):
		CommandRunner().run_command(edit, "compile", self)

class SbtClean(sublime_plugin.TextCommand):
	def run(self, edit):
		CommandRunner().run_command(edit, "clean", self)

class SbtUpdate(sublime_plugin.TextCommand):
	def run(self, edit):
		CommandRunner().run_command(edit, "update", self)

class Runner(threading.Thread):
	def __init__(self, command, shell, env, view):
		self.stdout = None
		self.stderr = None
		self.command = command or ''
		self.shell = shell or ''
		self.env = env or ''
		self.view = view or None
		threading.Thread.__init__(self)

	def run(self):
		proc = subprocess.Popen(
			[self.shell, '-ic', self.command],
			shell=False,
			stdout=subprocess.PIPE, 
			stderr=subprocess.PIPE,
			universal_newlines=True,
			env=self.env
			)

		while True:
			out = proc.stdout.readline()
			if out == '' and proc.poll() != None:
				break
			if out != '':
				self.view.run_command('sbt_view', { 'string': out })


class SbtViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, string=''):
    	data = re.sub(r'\033\[\d*(;\d*)?\w', '', string)
    	data = re.sub(r'.\x08', '', data)
    	(cur_row, _) = self.view.rowcol(self.view.size())
    	self.view.show(self.view.text_point(cur_row, 0))
    	self.view.set_read_only(False)
    	self.view.settings().set("syntax", "Packages/SBTRunner/TestConsole.tmLanguage")
    	self.view.settings().set("color_scheme", "Packages/SBTRunner/TestConsole.hidden-tmTheme")
    	self.view.insert(edit, self.view.size(), data)
    	self.view.set_read_only(True)


class CommandRunner():

	def load_config(self):
		s = sublime.load_settings("SBT.sublime-settings")
		#print(s.has("sbt_path"))
		self.SBT = s.get("sbt_path")
		self.PLAY = s.get("play_path")
		#print("SBT PATH: "+ SBT)

	def test_if_playapp(self):
		self.play_base_dir = self.current_file.partition("/test/")[0]
		#print("Checking if: "+ self.play_base_dir + "/conf/routes")
		if os.path.exists(self.play_base_dir + "/conf/routes"):
			return True
		else:
			return False

	def run_command(self, edit, sbt_command, commander):
		#print((sbt_command))
		self.edit = edit
		self.view = commander.view
		self.load_config()
		self.current_file = self.view.file_name()
		#print((self.current_file))
		self.base_dir = self.current_file.partition("/test/scala/")[0]
		self.project_dir = self.base_dir.replace("/src", "")
		self.package_name = self.current_file.replace(self.base_dir + "/test/scala/", "").replace("/", ".").replace(".scala", "")
		#print((self.package_name))

		if sbt_command == "run-main":
			if "/test/scala" in self.current_file: 
				sbt_command = "\"test:run-main "+ self.package_name +"\""
			else:
				sbt_command = "\"run-main "+ self.package_name +"\""
		elif sbt_command == "test-only":
			sbt_command = "\"" + sbt_command +" "+ self.package_name + "\""

		if self.test_if_playapp():
			self.package_name = self.current_file.replace(self.play_base_dir+ "/test/", "").replace("/", ".").replace(".scala", "")
			self.project_dir = self.play_base_dir
			self.SBT = self.PLAY
			sbt_command = "\"test-only" + " " + self.package_name + "\""


		self.show_tests_panel()
		command = wrap_in_cd(self.project_dir, self.SBT + " " + sbt_command)

		runner = Runner(command, os.environ['SHELL'], os.environ.copy(), self.output_view)
		runner.start()

	def window(self):
		return self.view.window()

	def show_tests_panel(self):
		if not hasattr(self, 'output_view'):
			self.output_view = self.window().get_output_panel("tests")
		self.clear_test_view()
		self.window().run_command("show_panel", {"panel": "output.tests"})

	def clear_test_view(self):
		self.output_view.set_read_only(False)
		#edit = self.output_view.begin_edit()
		self.output_view.erase(self.edit, sublime.Region(0, self.output_view.size()))
		#self.output_view.end_edit(edit)
		self.output_view.set_read_only(True)

def wrap_in_cd(path, command):
	return 'cd ' + path.replace("\\", "/") + ' && ' + command
