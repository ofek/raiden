#!/usr/bin/env python

import click
import json
from genesis_builder import generate_accounts, mk_genesis
from startcluster import RAIDEN_PORT as START_PORT
from startcluster import create_node_configuration, update_bootnodes, to_cmd


def build_node_list(hosts, nodes_per_host):
    node_list = []
    for host in hosts:
        for i in range(nodes_per_host):
            node_list.append('{}:{}'.format(host, START_PORT + i))
    return node_list


@click.group()
def cli():
    pass


@click.argument(
    'hosts',
    nargs=-1,
    type=str,
)
@click.argument(
    'nodes_per_host',
    default=1,
    type=int
)
@cli.command()
def nodes(hosts, nodes_per_host):
    if hosts is None:
        hosts = ['127.0.0.1']
    node_list = build_node_list(hosts, nodes_per_host)
    print json.dumps(node_list, indent=2)


@click.argument(
    'hosts',
    nargs=-1,
    type=str,
)
@click.argument(
    'nodes_per_host',
    default=1,
    type=int
)
@cli.command()
def genesis(hosts, nodes_per_host):
    node_list = build_node_list(hosts, nodes_per_host)
    accounts = generate_accounts(node_list)
    genesis = mk_genesis([acc['address'] for acc in accounts.values()])
    print json.dumps(genesis, indent=2)


@click.argument(
    'hosts',
    nargs=-1,
    type=str,
)
@click.argument(
    'nodes_per_host',
    default=1,
    type=int
)
@cli.command()
def accounts(hosts, nodes_per_host):
    node_list = build_node_list(hosts, nodes_per_host)
    print json.dumps(generate_accounts(node_list), indent=2)


@click.argument(
    'geth_hosts',
    nargs=-1,
    type=str,
)
@click.argument(
    'datadir',
    type=str,
)
@cli.command()
def geth_commands(geth_hosts, datadir):
    """This is helpful to setup a private cluster of geth nodes that won't need discovery
    (because they will have their `bootnodes` parameter pointed at each other).
    """
    nodes = []
    for i, host in enumerate(geth_hosts):
        nodes.append(create_node_configuration(host=host, node_key_seed=i))
    for node in nodes:
        node.pop('unlock')
    update_bootnodes(nodes)
    print json.dumps(
        {'{host}:{port}'.format(**node): ' '.join(to_cmd(node, datadir=datadir)) for node in nodes},
        indent=2)


@cli.command()
def usage():
    print "Example usage:"
    print "==============\n"
    print "\tconfig_builder.py genesis 5 127.0.0.1 127.0.0.2"
    print "\t-> create a genesis json with funding for 10 accounts on the two hosts (see also 'accounts')."
    print "\n"
    print "\tconfig_builder.py nodes 5 127.0.0.1 127.0.0.2"
    print "\t-> create json list 10 raiden endpoint addresses on the two hosts."
    print "\n"
    print "\tconfig_builder.py accounts 5 127.0.0.1 127.0.0.2"
    print "\t-> create full account-spec {endpoint: (privatekey, address)} for 10 nodes on the two hosts."
    print "\n"
    print "\tconfig_builder.py geth_commands /tmp/foo 127.0.0.1 127.0.0.2"
    print "\t-> create commands for geth nodes on both hosts with the datadir set to /tmp/foo."

if __name__ == '__main__':
    cli()
