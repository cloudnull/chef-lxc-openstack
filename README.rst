Rackspace Openstack Sandbox
###########################
:date: 2013-11-06 09:51
:tags: rackspace, openstack, private cloud, development, chef, cookbooks
:category: \*nix

This simple repo will turn a server into an Openstack Sandbox environment.

Requirements
^^^^^^^^^^^^

1. Two network Devices

   - eth0: Network interface required to communicate to the Openstack Cluster.

   - eth1: Network interface required for Neutron.

#. Minimum 2 CPU Cores, recommended >= 4 CPU Cores

#. Minimum 2048MB Ram, recommended >= 4096MB Ram


Usage
-----

1. To use this, simply clone the repository to your server.

#. change your directory to the repository directory.

#. As root execute the ``build-ova.sh`` script.

#. wait... this process can take a while and is ALL dependent on the speed
   of the machine you are installing on. 


Example Execution
^^^^^^^^^^^^^^^^^

.. code-block:: bash

    git clone https://github.com/cloudnull/rcbops-lxc-openstack rcbops-lxc-openstack
    pushd rcbops-lxc-openstack
    bash build-ova.sh
    popd


Variables:
    PASSWD=Set the password, if not set it will be generated.
    
    CONTAINER_USER=The name of the user that will be built within the 
    container.
    
    COOKBOOK_VERSION=Version number of the cookbooks being used for 
    deployment.
    
    PRIMARY_DEVICE=The device name for the primary network interface. 
    This is the network device that will the default gateway.
                   
    NEUTRON_DEVICE=The device name that neutron will be attached to.
    
    VIRT_TYPE=The Virtualization type, if your System supports KVM you 
    should set this to "kvm". Default, "qemu"


All variables are *environment variables* and should be set prior to executing the 
``build-ova.sh`` script.


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

The ``build-ova.sh`` script will build a self contained environment using the 
Rackspace Private Cloud software. Upon completion you will have a fully 
functional Openstack environment which will allow you to easily test and or 
develop on Openstack.


This installation supports the following services

==========  ==============
name        type
==========  ==============
ceilometer  metering
cinder      volume
ec2         ec2
glance      image
heat        orchestration
heat-cfn    cloudformation
keystone    identity
neutron     network
nova        compute
horizon     dashboard
==========  ==============


The installation also sets up the following:
    * A flat network with a CIDR 172.16.24.0/24 named "raxova"

    * A router named "internalRouter" with the "raxova" network as the attached 
      interface

    * A Cinder volume type "RaxVolType"

    * A Glance image, named "cirros-image"

    * A Key Pair named "adminKey"

    * A Nova flavor type for "512MB Standard Instance"


Limitations
^^^^^^^^^^^

While this build process attempts to make every effort to provide you a fully 
functional environment for development and testing purposes it does not attempt 
to ensure that the neutron network created by the script has public internet 
access. The script builds a *flat* **gre** type network which can be used for 
inter-instance communication. If you would like to provide your instance with 
the ability to communicate to the to the internet you would need to create 
a gateway network, based on your local network setup and attach it to your 
neutron router. 


By default the virtualization type set is `QEMU`. The `QEMU` virtualization 
type is slow.  If your machine has the ability to support the virtualization 
type "KVM" I highly recommend you set the environment variable **VIRT_TYPE** to
kvm prior to running the ``build-ova.sh`` script. 


This script **ONLY** supports the Host Operating System Ubuntu 12.04 Precise 
Pangolin. **THIS DOES NOT WORK ON RHEL-ish SYSTEMS**.  If the you request 
RHEL-ish support I will be happy to begin looking into how to extend the 
present build scripts for RHEL-ish support. For now, if you would like to 
have a similar like system please use the 
"https://github.com/cloudnull/rcbops_allinone_inone" script as Ubuntu and 
RHEL-ish operating systems are fully supported using that script.


At no time should you run this for a production setup. This was built ONLY for 
test / development purposes.
