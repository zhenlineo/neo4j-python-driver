#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright (c) 2002-2016 "Neo Technology,"
# Network Engine for Objects in Lund AB [http://neotechnology.com]
#
# This file is part of Neo4j.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Usage:   runtests.py
         --test=name : run this specific test
         --test      : run all unit tests
         --examples  : run all example tests
         --tck       : run tck tests
         -h          : show this help message
example:
         python ./runtests.py --test --examples --tck
"""
from sys import argv, stdout, exit
from os import name, path
from atexit import register
import subprocess
import getopt

UNITTEST_RUNNER = "coverage run -m unittest discover -vfs "
BEHAVE_RUNNER="behave --tags=-db --tags=-tls --tags=-fixed_session_pool test/tck"

NEORUN_PATH = path.abspath('./neokit/neorun.py')
NEO4J_HOME = path.abspath('./resources/neo4jhome')

is_windows = (name == 'nt')


def runcommand(command):
    commands = command.split()
    return runcommands(commands)


def runcommands(commands):
    if is_windows:
        commands = ['powershell.exe'] + commands
    return run0(commands)


def run0(commands):
    stdout.write("Running commands: %s\n" % commands)
    p = subprocess.Popen(commands, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    retcode = p.wait()
    stdout.write(out)
    stdout.write(err)
    return retcode


def neorun(command):
    runcommand('python ' + NEORUN_PATH + ' ' + command)


def main():
    if len(argv) <= 1:
        print_help()
        exit(2)
    try:
        opts, args = getopt.getopt(argv[1:], "h", ["test=", "test", "examples", "tck"])
    except getopt.GetoptError as err:
        print(str(err))
        print_help()
        exit(2)
    else:

        stdout.write("Using python version:\n")
        runcommand('python --version')
        runcommand('pip install --upgrade -r ./test_requirements.txt')
        retcode = 0

        register(neorun, '--stop=' + NEO4J_HOME)
        neorun('--start=' + NEO4J_HOME + ' -v 3.0.1 -p password')
        for opt, arg in opts:
            if opt == '-h':
                print_help()
                retcode = 2

            elif opt == "--test":
                retcode = retcode or runcommand(UNITTEST_RUNNER + "test")
            elif opt == "--test=":
                retcode = retcode or runcommand(UNITTEST_RUNNER + arg)
            elif opt == "--example":
                retcode = retcode or runcommand(UNITTEST_RUNNER + "examples")
            elif opt == "--tck":
                retcode = runcommand('coverage report --show-missing') or\
                runcommands(["python", "-c", "from test.tck.configure_feature_files import *; set_up()"]) or\
                runcommand(BEHAVE_RUNNER) or\
                runcommands(["python", "-c", "from test.tck.configure_feature_files import *; clean_up()"])

            if retcode != 0:
                break

    return retcode


def print_help():
    print(__doc__)


if __name__ == "__main__":
    main()