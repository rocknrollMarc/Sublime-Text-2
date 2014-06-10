# -*- coding: utf-8 -*-
# Plugin-balance_brackets.py
#
# Balances Objective-J brackets.
#
# (c) 2011 Aparajita Fishman and licensed under the MIT license.
# URL: http://github.com/aparajita
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import sublime
import sublime_plugin
import os
import os.path
from subprocess import Popen, PIPE, STDOUT


class BalanceBracketsCommand(sublime_plugin.TextCommand):
    PARSER_PATH = "Support/lib/objj_parser.rb"

    def is_enabled(self):
        return self.view.settings().get("syntax").endswith("/Objective-J.tmLanguage")

    def run(self, edit):
        selections = self.view.sel()

        # For now we don't try to balance multiple or non-empty selections, just insert as usual
        if len(selections) > 1:
            for selection in reversed(selections):
                self.insert(edit, selection)
            return

        selection = selections[0]

        if not selection.empty():
            self.insert(edit, selection)
            return

        point = selection.end()
        line = self.view.line(point)
        os.environ["TM_CURRENT_LINE"] = self.view.substr(line).encode("utf-8")
        os.environ["TM_LINE_INDEX"] = unicode(self.view.rowcol(point)[1])
        os.environ["TM_SUPPORT_PATH"] = os.getcwd().encode("utf-8")
        pipe = Popen(["ruby", os.path.join(self.package_path(), self.PARSER_PATH)], shell=False, stdout=PIPE, stderr=STDOUT).stdout
        snippet = pipe.read()
        pipe.close()

        self.view.erase(edit, line)
        self.view.run_command("insert_snippet", {"contents": unicode(snippet, "utf-8")})

    def package_path(self):
        dataPath = os.path.dirname(sublime.packages_path())
        relativePackagePath = os.path.dirname(self.view.settings().get('syntax'))
        return os.path.join(dataPath, relativePackagePath)

    def insert(self, edit, selection):
        # If the selection is empty and the character to the right of the cursor is ']',
        # then replace it, don't insert another one. This is standard ST2 behavior.
        if selection.empty() and self.view.substr(selection.end()) == "]":
            selection = sublime.Region(selection.begin(), selection.begin() + 1)

        point = selection.begin()
        self.view.erase(edit, selection)
        self.view.insert(edit, point, "]")
