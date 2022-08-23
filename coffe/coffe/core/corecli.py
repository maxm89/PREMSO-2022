# -*- coding: utf-8 -*-

"""Console script for coffe's core commands. cli = command line interface."""

from __future__ import absolute_import, division, print_function

import click
from coffe.core import cluster


@click.command()
@click.argument("status", type=str)
@click.argument("file", type=click.Path(exists=True))
def update_cluster_status(status, file):
    """Update the status of a cluster job.
    This script is called by all instances of :class:`~cluster.ClusterJob`

     - once they start running (change status to "running")
     - once they are completed (change status to "completed")
    """
    cluster.Status.write(file, status)
