#!/usr/bin/env python
"""
 Get ESXi Version
"""

from pyVmomi import vim
import argparse
import getpass
from pyVim.connect import SmartConnectNoSSL, Disconnect
import atexit
import sys


def get_args():
    """Get command line args from the user.
    """
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
    parser.add_argument('-esxi',
                        required=False,
                        action='store',
                        help='The ESXi host whose Version Information is needed')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))
    return args

def print_host_info(host):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """
    summary = host.summary
    print("###Name  : {}, Version : {}".format(host.name, summary.config.product.fullName))


def get_obj(content, vim_type, name):
    """

    :param content: content reference
    :param vim_type: vim object type
    :param name: Name whoes object needs to be returned
    :return: object of the type vim_type is returned
    """
    obj = None

    container = content.viewManager.CreateContainerView(content.rootFolder, vim_type, True)

    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def main():

    args = get_args()

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

    content = si.RetrieveContent()

    container = content.rootFolder  # starting point to look into
    viewType = [vim.HostSystem]  # object types to look for
    recursive = True  # whether we should look into it recursively

    if args.esxi:
        host_object = get_obj(content, [vim.HostSystem], args.esxi)
        print_host_info(host_object)

    else:
        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

        children = containerView.view
        for child in children:
            print_host_info(child)
        print("")


if __name__ == "__main__":
    main()
