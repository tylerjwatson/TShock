#!/usr/bin/env python

###########################################################################
#
#    tsinstance.py - Tyler Watson <tyler@tw.id.au>
#
#    This file is part of TSAPI-redhat.
#
#    TSAPI-redhat is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    TSAPI-redhat is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TSAPI-redhat.  If not, see <http://www.gnu.org/licenses/>.
#
###########################################################################

import sys
import docopt
import configparser
import subprocess
import os
from pwd import getpwnam

__basedir__ = "/etc/tsapi"
__tsapi_libdir__ = "/usr/lib64/tsapi"
__version__ = 0.1
__instancefile__ = "{3}/instances.conf"
__help__ = """{0} v{1} - Tyler W. <tyler@tw.id.au>

Controls a TSAPI instance defined in {3}/instances.conf.

Usage: {0} start <instance> [-c | --config-path PATH]
  {0} create <instance>
  {0} stop <instance>
  {0} restart <instance>
  {0} -h | --help
  {0} -v | --version

Options:
  -c | --config-path PATH: Override the default instance file location (default: {2})
""".format(sys.argv[0], __version__, __instancefile__, __basedir__)

def load_options():
    return docopt.docopt(__help__)

def load_instances():
    pass

def create_instance(name):
    path = "{}/instances.d/{}".format(__basedir__, name)
    try:
        uid = getpwnam("terraria")
    except:
        raise Exception("user 'terraria' doesn't exist")

    

    if os.path.isdir(path):
        raise Exception("Instance {} directory already exists.".format(path))

    os.mkdir(path)


    # /etc/tsapi/instances.d/<name>/ServerPlugins -> /usr/lib64/plugins
    os.symlink(__tsapi_libdir__, "{}/ServerPlugins".format(path))




def main():
    options = load_options()
    print options


if __name__ == "__main__":
    main()