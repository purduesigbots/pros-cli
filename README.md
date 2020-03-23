# PROS CLI

PROS is the only open source development environment for the VEX EDR Platform.

This project provides all of the project management related tasks for PROS. It is currently responsible for:

- Downloading kernel templates
- Creating, upgrading projects
- Uploading binaries to VEX Microcontrollers

This project is built in Python 3.6, and executables are built on cx_Freeze.

## Changes from purduesigbots

- Unhide certain commands for uploading and interacting with the V5
- Add support for uploading binary files without being part of a project
- Add support for uploading custom .ini files with program

## Installing for development

PROS CLI can be installed directly from source with the following prerequisites:

- Python 3.5
- PIP (default in Python 3.6)
- Setuptools (default in Python 3.6)

Clone this repository, then run `pip install -e <dir>`. Pip will install all the dependencies necessary.

## About this project

Here's a quick breakdown of the packages involved in this project:

- `pros.cli`: responsible for parsing arguments and running requested command
- `pros.common.ui`: provides user interface functions used throughout the PROS CLI (such as logging facilities, machine-readable output)
- `pros.conductor`: provides all project management related tasks
  - `pros.conductor.depots`: logic for downloading templates
  - `pros.conductor.templates`: logic for maintaining information about a template
- `pros.config`: provides base classes for configuration files in PROS (and also the global cli.pros config file)
- `pros.jinx`: JINX parsing and server
- `pros.serial`: package for all serial communication with VEX Microcontrollers
- `pros.upgrade`: package for upgrading the PROS CLI, including downloading and executing installation sequence

See <https://pros.cs.purdue.edu/v5/cli> for end user documentation and developer notes.
