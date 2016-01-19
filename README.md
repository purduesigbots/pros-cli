# purdueros-cli

Purdueros-cli provides a command line utility to create and upgrade projects using the Purdue Robotics Operating System. Purdueros-cli uses the official kernel repository, but can be modified to utilize any other repository. This project was created using IntelliJ IDEA 15 and is a Maven-based project.

## Contributing
Feel free to contribute to this repository and add functionality to the command line interface. Create a pull request for code review.

## Outlined Functionality
```
usage: pros [-h] [--version] {create,upgrade,fetch,config} ...

Create and upgrade PROS projects from an update site.

optional arguments:
  -h, --help             show this help message and exit
  --version

command:
  {create,upgrade,fetch,config}
```

```
usage: pros create [-h] [--kernel [KERNEL]]
            [--environments ENVIRONMENTS [ENVIRONMENTS ...]] [-f] [-v]
            directory

positional arguments:
  directory              PROS project to create.

optional arguments:
  -h, --help             show this help message and exit
  --kernel [KERNEL]      Specify  kernel   version   to   target.  'latest'
                         defaults to highest  locally available repository.
                         Use  'pros  fetch   latest'   to  download  latest
                         repository from update site.
  --environments ENVIRONMENTS [ENVIRONMENTS ...]
                         define   environments    to    target.   Available
                         environments are determined  by  the kernel loader
                         and can be  found  using  'pros  fetch  KERNEL -e'
  -f, --force            Don't  prompt  to   overwrite  existing  directory
  -v, --verbose          Use this flag to  enable verbose output.
```

```
usage: pros upgrade [-h] [--kernel [KERNEL]]
            [--environments ENVIRONMENTS [ENVIRONMENTS ...]] [-f] [-v]
            directory

positional arguments:
  directory              PROS project directory to upgrade.

optional arguments:
  -h, --help             show this help message and exit
  --kernel [KERNEL]      Specify kernel version  to  upgrade  to.
  --environments ENVIRONMENTS [ENVIRONMENTS ...]
                         Define   environments    to    target.   Available
                         environments are determined by  the kernel kernels
                         and can be found by  using  'pros fetch KERNEL -e'
  -f, --force            Create/update  files  regardless   if  project  is
                         considered to be a PROS project.
  -v, --verbose          Use this flag to  enable verbose output.
```

```
usage: pros fetch [-h] [--site [SITE]] [-v] [-e | -d | -c] [kernel]

positional arguments:
  kernel                 Kernel to fetch. May be  a regular expression. May
                         be 'latest' to fetch  latest  from  online site or
                         locally available  (whichever  is  higher).  'all'
                         specifies all  kernels  if  applicable.

optional arguments:
  -h, --help             show this help message and exit
  --site [SITE]          Specify  site  to   do   online  operations  with.
  -e, --environments     List all environments that  can  be used with this
                         kernel
  -d, --download         Downloads kernel(s) from online  site. Will delete
                         kernel template if  it  exists  locally. 
  -c, --clean            Deletes kernel template(s)  from local repository.
  -v, --verbose          Use this flag to  enable verbose output.

Without -e, -d, or  -c,  will  list  if  the  specified kernel is available
locally and/or online.
```

### Roadmap

- Add better support for secured update sites (maybe jgit to enable ssh-protected git repos following site manifest)
- Migrate uniflash, Eclipse flasher into PROS CLI


