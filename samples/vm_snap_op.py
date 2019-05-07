#!/usr/bin/env python
#
# Inspired from  Michael Rice <michael@michaelrice.org> create_snapshot script in pyvmomi community samples
#
#

from __future__ import print_function

from pyVmomi import vim
from tools import tasks
import argparse
import getpass
from pyVim.connect import SmartConnectNoSSL, Disconnect
import atexit
import sys


def get_args():

    """Get command line args from the user """

    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter')

    # because -h is reserved for 'help' we use -s for service
    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vSphere service to connect to')

    # because we want -p for password, we use -o for port
    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    parser.add_argument('-vm', '--vmname',
                        required=True,
                        action='store',
                        help='VM Name whose performance data needs to be retrieved')

    parser.add_argument('-d', '--description', required=False,
                        help="Description for the snapshot")

    parser.add_argument('-n', '--name', required=True,
                        help="Name for the Snapshot")

    parser.add_argument('-memory', required=False,
                        help="Memory of snapshot boolean value",
                        choices=('yes', 'no'),
                        default=False)

    parser.add_argument('-quiesce', required=False,
                        help="Quiesce boolean",
                        choices=('yes', 'no'),
                        default=False)

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))
    return args


def get_obj(content, vimtype, name):

    """Create container view and search for object in it"""
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break

    container.Destroy()
    return obj


def create_snapshot(si, vm_obj, sn_name, description, sn_memory, sn_quiesce):

    """ Creates Snapshot given the VM object and Snapshot name and necessary description"""
    desc = None
    if description:
        desc = description

    if sn_memory == 'yes':
        sn_memory = True
    else:
        sn_memory = False

    if sn_quiesce == 'yes':
        sn_quiesce = True
    else:
        sn_quiesce = False

    task = vm_obj.CreateSnapshot_Task(name=sn_name,
                                      description=desc,
                                      memory=sn_memory,
                                      quiesce=sn_quiesce)
    tasks.wait_for_tasks(si, [task])

    if sn_memory == True:
        print("Snapshot {} is taken on VM {} with memory".format(sn_name, vm_obj.name))
    else:
        print("Snapshot {} is taken on VM {} with no in-memory".format(sn_name, vm_obj.name))


def main():

    args = get_args()

    si = None

    # Connect to the host without SSL signing
    try:
        si = SmartConnectNoSSL(
            host=args.host,
            user=args.user,
            pwd=args.password,
            port=int(args.port))
        atexit.register(Disconnect, si)

    except IOError as e:
        pass

    if not si:
        raise SystemExit("Unable to connect to host with supplied info.")

    vm_obj = get_obj(si.content, [vim.VirtualMachine], args.vmname)

    if vm_obj is None:
        raise SystemExit("Unable to locate VirtualMachine.")

    create_snapshot(si, vm_obj, args.name, args.description, args.memory, args.quiesce)

    del vm_obj


if __name__ == "__main__":
    main()
