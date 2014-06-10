[![endorse](http://api.coderwall.com/chiappone/endorsecount.png)](http://coderwall.com/chiappone)

Sublime SBT Runner and Tester
=======================

Overview
--------

This plug-in for Sublime Text 2 enables you to:
  - Execute SBT commands from the context menu or shortcut

Supported SBT commands are:
  - sbt test-only
  - sbt run-main
  - sbt clean
  - sbt update
  - sbt compile

Detects Play projects and will run play instead of SBT if found.
Finds separate projects if multiple application folders are within a single project.

Installation
------------

Installing
----------
Download [Package Control](http://wbond.net/sublime_packages/package_control)
and use the *Package Control: Install Package* command from the command palette. Search and select SBTRunner.

Settings
--------

Modify the package user settings to include the path of SBT and PLAY.


Usage
-----

Right click for context menu or modify the shortcut keys

Keys:
- 'Command' (OSX) = 'Ctrl' (Linux / Windows)
- 'Option' (OSX) = 'Alt' (Linux / Windows)


Note
----
This plug-in assumes your project folder is organized as a standard SBT project:

- src files would be located in /src/main/scala
- test files would be located in /src/test/scala

and the SBT project files are at the top level of your project


