Rackspace Openstack Sandbox
###########################
:date: 2013-11-06 09:51
:tags: rackspace, openstack, private cloud, development, chef, cookbooks
:category: \*nix

This simple repo will turn a server into an Openstack Sandbox environment.

Requirments
^^^^^^^^^^^

1. Two network Devices

   - eth0: Network interface required to communicate to the Openstack Cluster.

   - eth1: Network interface required for Neutron.

#. Minimum 2 CPU Cores, recommended >= 4 CPU Cores

#. Minimum 2048MB Ram, recommended >= 4096MB Ram


Usage
-----

1. To use this, simply clone the repository to your server.

#. change your directory to the repository dirctory.

#. As root execute the ``build-ova.sh`` script.

#. wait... this process can take a while and is ALL dependent on the speed
   of your machine.


Example Execution
^^^^^^^^^^^^^^^^^

.. code-block:: bash

    git clone https://github.com/cloudnull/c rcbops-lxc-openstack
    pushd rcbops-lxc-openstack
    bash build-ova.sh
    popd


Architecture
^^^^^^^^^^^^

Here is a diagram showing the new architecture of the All in one server.

.. code-block:: bash

    ====== ASCII Diagram for OVA infrastructure ======


           ---------->[ ETH1 == Local Network ]
           |  ------->[ ETH0 == Public Network ]
           |  |
           |  |
           v  |                  [  *   ] Socket Connections
    [ HOST MACHINE ]             [ <>v^ ] Network Connections
      *    ^  *
      |    |  |
      |    |  |--->[ HAProxy ]<--------------
      |    |                                |
      |    -------|                         |
      |           |                         |
      |           v                         |
      |<---->[ Neutron ]<------------------ |
      |*----*[ Compute ]<---------------- | |
      |*----*[ Cinder  ]<-------------- | | |
      |                               | | | |
      |                               | | | |
      |                               v v v v
      -------------*[ LXC ]*-----*[ Controller1 ]


    ====== ASCII Diagram for OVA infrastructure ======


What the setup provides
^^^^^^^^^^^^^^^^^^^^^^^

The OVA is built using the Rackspace Private Cloud software

* Nova Compute

* Neutron Network Node

* Cinder

* Heat

* Ceilometer

* Glance

* Keystone

* Horizon
