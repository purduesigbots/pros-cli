# purdueros-cli

PurdueROS-cli provides a command line utility to create and upgrade projects using the Purdue Robotics Operating System. PurdueROS-cli uses the official kernel repository, but can be modified to utilize any other repository.
```
usage: pros [-h] [--version] [-k V] [-s SITE] [-d] [-f] [-n NAME]
               [--verbose]
               [directory]

Create and upgrade PROS projects.

positional arguments:
  directory             Directory to create or upgrade. Defaults to current
                        directory. Without -f or equivalent flag, will default 
                        to upgrade if a valid PROS directory is found.                        

optional arguments:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  -k V, --kernel V      Kernel version to create or upgrade project to
  -s SITE, --site SITE  Use a different site to pull kernels from.
  -d, --download        Forces a redownload of the kernel' template. Works
                        even when --kernel is not provided.
  -f, --force, --fresh  Deletes all contents in the directory and fills it
                        with a new PROS template.
  -n NAME, --name NAME, --project-name NAME
                        Name of the project. Defaults to the name of the
                        current directory
  --verbose             Prints verbosely.
  ```
