Building The Rackspace OVA
##########################
:date: 2014-03-28 09:51
:tags: rackspace, openstack, appliance, ova
:category: \*nix

This is a general overview on how to build the Virtual Appliance by hand. 
This is a simple how to, and is more for academia than anything else. The
actually build script does a bit more than this process in addition to 
having a slightly different architecture. This process was written as a 
basis for the ``build-ova.sh`` script. This process was targeted at 
building the appliance within desktop virtualization such as VirtualBox 
and VVMWare Fusion. 


Broad Overview
--------------

Architecture:

Here is a diagram showing how the new architecture of the OVA has been setup.

.. code-block:: bash

    == ASCII Diagram for OVA infrastructure ==

        ------------->[ ETH2 == NAT ]
        |  ---------->[ ETH1 == Host Only ]
        |  |  ------->[ ETH0 == NAT ]
        |  |  |
        v  v  |                  [  *   ] Socket Connections
    [ HOST MACHINE ]             [ <>v^ ] Network Connections
      * ^       *
      | |       |--->[ HAProxy ]<------------
      | |                                   |
      | ----------|                         |
      |           |                         |
      |           v                         |
      |<---->[ Neutron ]<------------------ |
      |*----*[ Compute ]<---------------- | |
      |*----*[ Cinder  ]<-------------- | | |
      |                               | | | |
      |                               | | | |
      |                               v v v v
      -------------*[ LXC ]*-----*[ Controller1 ]



This setup provides:

* Nova Compute

* Neutron Network Node

* Cinder

* Heat

* Ceilometer

* Glance

* Keystone

* Horizon


Networking:

- eth0: Global Networking Interface This is used to connect the OVA to the
  rest of the world. Default type NAT

- eth1: User connection Interface. This is used to provide the user the ability
  to connect to the OVA from the host machine. Default type Host Only

- eth2: System Connection Interface. This is used to provide a binding
  interface for network services. Default Type NAT


Software Stack:

- The OVA is built using the Rackspace Private Cloud software leveraging a
  single compute node, itself, and a single controller.


Building all of this by hand:

-  When Building the base system create the server using a hostname
   **RACKSPACE-SANDBOX** and set the first user with the name **openstack**.

1. Create a new Ubuntu 12.04 server with three network interfaces, when ready,
   Install some base packages

   .. code-block::

       apt-get -y install lvm2 git python-dev


#. Set the root password

   .. code-block:: bash

        echo -e "secrete\nsecrete" | (passwd $(whoami))


#. setup networking, this should be a bridged network and will need to be DHCP

#. make a key for the new system

   .. code-block:: bash

        ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''


#. make sure we have an rc.local file

   .. code-block:: bash

        if [ ! -f "/etc/rc.local" ];then
            touch /etc/rc.local
            chmod +x /etc/rc.local
        else
            chmod +x /etc/rc.local
        fi

        if [ "$(grep 'exit 0' /etc/rc.local)" ];then
            sed -i '/exit\ 0/ s/^/#\ /' /etc/rc.local
        fi


#. Login to the Host server and install HA Proxy

   .. code-block:: bash

        apt-get -y install haproxy


#. Configure HAproxy with all of the ports that are required for operation

   - Modify the init script to allow HA Proxy to run at boot

   - Place the HAproxy configuration file

     .. code-block:: bash

        global
            user haproxy
            group haproxy
            daemon

            # Terminal Command Set
            stats socket /etc/haproxy/haproxysock level admin

        defaults
            log global
            mode http
            option tcplog
            option dontlognull
            retries 3
            option redispatch
            maxconn 2000
            contimeout 5000
            clitimeout 50000
            srvtimeout 50000
            # Server logs
            log 127.0.0.1   local0 notice

            # Access logs
            log 127.0.0.1 local1

        frontend ssh_management
            bind 0.0.0.0:2222
            mode tcp
            option tcplog clf
            default_backend ssh_management_backend

        backend ssh_management_backend
            mode tcp
            balance static-rr
            server controller1 10.0.3.100:22 check port 22 inter 12000

        frontend rabbitmq_cluster_managment
            bind 0.0.0.0:15672
            mode http
            option httplog clf
            option forwardfor header x-forwarded-for
            default_backend rabbitmq_cluster_managment_backend

        backend rabbitmq_cluster_managment_backend
            mode http
            balance static-rr
            server controller1 10.0.3.100:15672 check port 15672 inter 12000

        frontend keystone1
            bind 0.0.0.0:5000
            mode http
            option forwardfor header x-forwarded-for
            option httplog clf
            default_backend keystone1_backend

        backend keystone1_backend
            mode http
            balance static-rr
            server controller1 10.0.3.100:5000 check port 35357 inter 12000

        frontend keystone2
            bind 0.0.0.0:35357
            mode http
            option forwardfor header x-forwarded-for
            option httplog clf
            default_backend keystone2_backend

        backend keystone2_backend
            mode http
            balance static-rr
            server controller1 10.0.3.100:35357 check port 35357 inter 12000

        frontend glance1
            bind 0.0.0.0:9292
            mode http
            option forwardfor header x-forwarded-for
            option httplog clf
            default_backend glance1_backend

        backend glance1_backend
            mode http
            balance static-rr
            server controller1 10.0.3.100:9292 check port 9292 inter 12000

        frontend glance2
            bind 0.0.0.0:9191
            mode tcp
            option tcplog clf
            default_backend glance2_backend

        backend glance2_backend
            mode http
            balance static-rr
            server controller1 10.0.3.100:9191 check port 9191 inter 12000

        frontend cinder1
            bind 0.0.0.0:8776
            mode http
            option forwardfor header x-forwarded-for
            option httplog clf
            default_backend cinder1_backend

        backend cinder1_backend
            mode http
            balance static-rr
            server controller1 10.0.3.100:8776 check port 8776 inter 12000

        frontend nova1
            bind 0.0.0.0:8773
            mode http
            option forwardfor header x-forwarded-for
            option httplog clf
            default_backend nova1_backend

        backend nova1_backend
            mode http
            balance static-rr
            server controller1 10.0.3.100:8773 check port 8773 inter 12000

        frontend nova2
            bind 0.0.0.0:8774
            mode http
            option httplog clf
            default_backend nova2_backend

        backend nova2_backend
            mode http
            balance static-rr
            server controller1 10.0.3.100:8774 check port 8774 inter 12000

        frontend nova3
            bind 0.0.0.0:8775
            mode tcp
            option tcplog clf
            default_backend nova3_backend

        backend nova3_backend
            mode tcp
            balance static-rr
            server controller1 10.0.3.100:8775 check port 8775 inter 12000

        frontend novnc1
            bind 0.0.0.0:6080
            mode tcp
            option tcplog clf
            default_backend novnc1_backend

        backend novnc1_backend
            mode tcp
            balance static-rr
            server controller1 10.0.3.100:6080 check port 6080 inter 12000

        frontend heat1
            bind 0.0.0.0:8000
            mode tcp
            option tcplog clf
            default_backend heat1_backend

        backend heat1_backend
            mode tcp
            balance static-rr
            server controller1 10.0.3.100:8000 check port 8000 inter 12000

        frontend heat2
            bind 0.0.0.0:8003
            mode tcp
            option tcplog clf
            default_backend heat2_backend

        backend heat2_backend
            mode tcp
            balance static-rr
            server controller1 10.0.3.100:8003 check port 8003 inter 12000

        frontend heat3
            bind 0.0.0.0:8004
            mode tcp
            option tcplog clf
            default_backend heat3_backend

        backend heat3_backend
            mode tcp
            balance static-rr
            server controller1 10.0.3.100:8004 check port 8004 inter 12000

        frontend ceilometer1
            bind 0.0.0.0:8777
            mode tcp
            option tcplog clf
            default_backend ceilometer1_backend

        backend ceilometer1_backend
            mode tcp
            balance static-rr
            server controller1 10.0.3.100:8777 check port 8777 inter 12000

        frontend neutron1
            bind 0.0.0.0:9696
            mode tcp
            option tcplog clf
            default_backend neutron1_backend

        backend neutron1_backend
            mode tcp
            balance static-rr
            server controller1 10.0.3.100:9696 check port 9696 inter 12000

        frontend dash1
            bind 0.0.0.0:80
            mode http
            option forwardfor header x-forwarded-for
            option httplog clf
            default_backend dash1_backend

        backend dash1_backend
            mode http
            balance static-rr
            server controller1 10.0.3.100:80 check port 80 inter 12000

        frontend dash2
            bind 0.0.0.0:443
            mode tcp
            option tcplog clf
            default_backend dash2_backend

        backend dash2_backend
            mode tcp
            balance static-rr
            server controller1 10.0.3.100:443 check port 443 inter 12000

        listen stats :12345
            mode http
            stats enable
            stats scope ssh_management
            stats scope ssh_management_backend
            stats scope rabbitmq_cluster_managment
            stats scope rabbitmq_cluster_managment_backend
            stats scope keystone1
            stats scope keystone1_backend
            stats scope keystone2
            stats scope keystone2_backend
            stats scope glance1
            stats scope glance1_backend
            stats scope glance2
            stats scope glance2_backend
            stats scope cinder1
            stats scope cinder1_backend
            stats scope nova1
            stats scope nova1_backend
            stats scope nova2
            stats scope nova2_backend
            stats scope nova3
            stats scope nova3_backend
            stats scope novnc1
            stats scope novnc1_backend
            stats scope heat1
            stats scope heat1_backend
            stats scope heat2
            stats scope heat2_backend
            stats scope heat3
            stats scope heat3_backend
            stats scope ceilometer1
            stats scope ceilometer1_backend
            stats scope neutron1
            stats scope neutron1_backend
            stats scope dash1
            stats scope dash1_backend
            stats scope dash2
            stats scope dash2_backend
            stats realm Haproxy\ Statistics
            stats refresh 60
            stats auth openstack:secrete
            stats uri /

#. Make sure that the system has the ability to swap when needed

   .. code-block:: bash

        if [ ! -d "/opt" ];then
          mkdir /opt
        fi


        if [ ! "$(swapon -s | grep -v Filename)" ];then
          cat > /opt/swap.sh <<EOF
        #!/usr/bin/env bash
        if [ ! "\$(swapon -s | grep -v Filename)" ];then
        SWAPFILE="/tmp/SwapFile"
        if [ -f "\${SWAPFILE}" ];then
          swapoff -a
          rm \${SWAPFILE}
        fi
        dd if=/dev/zero of=\${SWAPFILE} bs=1M count=2048
        mkswap \${SWAPFILE}
        swapon \${SWAPFILE}
        fi
        EOF

          chmod +x /opt/swap.sh
          /opt/swap.sh
        fi

        sysctl vm.swappiness=60 | tee -a /etc/sysctl.conf


#. Create an LVM backed loop file which cinder will use to build new volumes

   .. code-block:: bash

        CINDER="/opt/cinder.img"
        LOOP=$(losetup -f)
        dd if=/dev/zero of=${CINDER} bs=1 count=0 seek=1000G
        losetup ${LOOP} ${CINDER}
        pvcreate ${LOOP}
        vgcreate cinder-volumes ${LOOP}
        pvscan

        # Set Cinder Device as Persistent
        cat > /opt/cinder.sh <<EOF
        #!/usr/bin/env bash
        CINDER="${CINDER}"
        if [ ! "\$(losetup -a | grep \${CINDER})"  ];then
          LOOP=\$(losetup -f)
          CINDER="/opt/cinder.img"
          losetup \${LOOP} \${CINDER}
          pvscan
          # Restart Cinder once the volumes are online
          for srv in cinder-volume cinder-api cinder-scheduler;do
            service \${srv} restart
          done
        fi
        EOF

        if [ -f "/opt/cinder.sh" ];then
            chmod +x /opt/cinder.sh
        fi


#. Install LXC and the LXC Defiant Template.

   .. code-block:: bash

        # Add the LXC Stable back ports repo
        apt-get -y install python-software-properties
        add-apt-repository -y ppa:ubuntu-lxc/stable

        # Update
        apt-get update

        # Install LXC
        apt-get -y install lxc python3-lxc lxc-templates liblxc1 git

        # LXC Template
        git clone https://github.com/cloudnull/lxc_defiant
        cp lxc_defiant/lxc-defiant.py /usr/share/lxc/templates/lxc-defiant
        cp defiant.common.conf /usr/share/lxc/config/defiant.common.conf
        cp lxc_defiant/defiant.common.conf /usr/share/lxc/config/defiant.common.conf

        # Update the lxc-defiant.conf file
        cat > /etc/lxc/lxc-defiant.conf <<EOF
        lxc.network.type=veth
        lxc.network.name=eth0
        lxc.network.link=lxcbr0
        lxc.network.flags=up

        lxc.network.type = veth
        lxc.network.name = eth1
        lxc.network.link = lxcbr0
        lxc.network.flags = up
        EOF


#. Make the openstack user a sudoer without password

   .. code-block:: bash

        echo 'openstack   ALL = NOPASSWD: ALL' | tee -a /etc/sudoers


#. Setup the interfaces file, ``/etc/network/interfaces``. All interfaces
   should be on DHCP.

   .. code-block:: bash

        # The loopback network interface
        auto lo
        iface lo inet loopback

        # The primary network interface
        auto eth0
        iface eth0 inet dhcp

        auto eth1
        iface eth1 inet dhcp

        auto eth2
        iface eth2 inet dhcp


#. Create the container will openstack will live

   .. code-block:: bash

        lxc-create -n controller1 \
                   -t defiant \
                   -f /etc/lxc/lxc-defiant.conf \
                   -- \
                   -o curl,wget,iptables,python-dev \
                   -I eth0=10.0.3.100=255.255.255.0=10.0.3.1 \
                   -I eth1=10.0.3.101=255.255.255.0 \
                   -S ~/.ssh/id_rsa.pub \
                   -P secrete \
                   -U openstack \
                   -M 4096 \
                   -L /var/log/controller1_logs=var/log

        echo "lxc.start.auto = 1" | tee -a /var/lib/lxc/controller1/config
        echo "lxc.group = rpc_controllers" | tee -a /var/lib/lxc/controller1/config
        lxc-start -d -n controller1


----

At this point login to the container. Your IP address for the container is
``10.0.3.100`` and the user is ``openstack`` with a password of ``secrete``.

1. Set the root password for the container

   .. code-block:: bash

      echo -e "secrete\nsecrete" | (passwd $(whoami))


#. make a key for the new container

   .. code-block:: bash

        ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''


#. Make the openstack user a sudoer without password

   .. code-block:: bash

        echo 'openstack   ALL = NOPASSWD: ALL' | tee -a /etc/sudoers


#. Login to the new container and being the systems installation.

   .. code-block:: bash

        # Enable root login
        sed -i 's/PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
        /etc/init.d/ssh restart

        export COOKBOOK_VERSION="v4.2.2rc"
        GITHUB="https://raw.github.com"
        curl ${GITHUB}/pypa/pip/master/contrib/get-pip.py | python
        curl ${GITHUB}/rcbops/support-tools/master/chef-install/install-chef-rabbit-cookbooks.sh | bash


#. enable some rabbitmq plugins

   .. code-block::

        rabbitmq-plugins enable rabbitmq_shovel
        rabbitmq-plugins enable rabbitmq_management
        rabbitmq-plugins enable rabbitmq_shovel_management


#. Once Chef, Rabbit, and the cookbooks are installed, create a chef
   environment.  You will need to replace ``$SOME_KNOWN_ERLANG_COOKIE`` with
   the erlang cookie that is presented to you after running the
   ``install-chef-rabbit-cookbooks.sh`` script.

   .. code-block:: bash

        # Install the mungerator
        pip install git+https://github.com/cloudnull/mungerator

        # Drop the environment ini in place.
        ERLANG_COOKIE=$(cat /var/lib/rabbitmq/.erlang.cookie)
        cat > rpcs.ini <<EOF
        [ChefOpenstack]
        env_name = rpcs

        # Glance
        image_upload = False

        # Keystone
        username = admin
        password = secrete
        pki = False

        # Nova
        scheduler_filters = AvailabilityZoneFilter,RetryFilter

        # Libvirt
        virt_type = qemu

        # Nova Networks Configuration
        ipv4_cidr = 10.0.3.0/24

        # RabbitMQ
        rabbit_address = 10.0.3.100
        erlang_cookie = ${ERLANG_COOKIE}

        # Neutron Configuration
        label = ph-eth2
        bridge = br-eth2
        vlans = 1024:1024

        # OS Networks
        interface_bridge = br-eth2
        management_net = 10.0.3.0/24
        nova_net = 10.0.3.0/24
        public_net = 10.0.3.0/24

        # MySQL
        mysql_network_acl = 0.0.0.0

        add_users = demo=secrete=demo|demo2,demo2=secrete=demo2|demo
        EOF

        # Create the environment file
        mungerator -C rpcs.ini create-env neutron

        # Upload the environment to chef
        knife environment from file rpcs.json


#. Copy the containers SSH Key back to the HOST

   .. code-block:: bash

       ssh-copy-id 10.0.3.1


#. With the environment in place we are ready to begin building our pieces.
   From within the container, bootstrap the controller1 role. You may need to
   do this command more than once. It all really depends on the speed of your
   host.

   .. code-block:: bash

       knife bootstrap -E rpcs -r role[ha-controller1],role[heat-all] localhost


#. When that initial chef run is complete bootstrap the host machine from the
   controller1 container.  Here you are going to make the host a neutron
   controller, a compute node, and a cinder volume. You may need to
   do this command more than once. It all really depends on the speed of your
   host.

   .. code-block:: bash

       knife bootstrap -E rpcs \
                       -r role[single-network-node],role[single-compute],role[cinder-volume] \
                       --server-url https://10.0.3.100:4000 \
                       10.0.3.1


#. Now re-chef the controller node to finalize the openstack Installation

   .. code-block:: bash

      chef-client


#. Create your first Neutron Network

   .. code-block:: bash

        # Make our networks
        neutron net-create --provider:physical_network=ph-eth2 \
                           --provider:network_type=flat \
                           --shared raxova
        # Make our subnets
        neutron subnet-create raxova \
                              172.16.24.0/24 \
                              --name raxova_subnet \
                              --no-gateway \
                              --allocation-pool start=172.16.24.100,end=172.16.24.200 \
                              --dns-nameservers list=true 8.8.4.4 8.8.8.8


#. Create some security groups

   .. code-block:: bash

        # Add Default Ping Security Group
        neutron security-group-rule-create --protocol icmp \
                                           --direction ingress \
                                           default

        # Add Default SSH Security Group
        neutron security-group-rule-create --protocol tcp \
                                           --port-range-min 22 \
                                           --port-range-max 22 \
                                           --direction ingress \
                                           default


#. Remove all defined flavors and create our own

   .. code-block:: bash

        # Delete all of the m1 flavors
        for FLAVOR in $(nova flavor-list | awk '/m1/ {print $2}');do
            nova flavor-delete ${FLAVOR}
        done

        # Create a new Standard Flavor
        nova flavor-create "512MB Standard Instance" 1 512 5 1 --ephemeral 0 \
                                                               --swap 512 \
                                                               --rxtx-factor 1 \
                                                               --is-public True


#. Create a new image in glance to build with

   .. code-block:: bash

        # Get the image
        wget http://download.cirros-cloud.net/0.3.1/cirros-0.3.1-x86_64-disk.img

        # Upload the image
        glance image-create --name cirros-image \
                            --disk-format=qcow2 \
                            --container-format=bare \
                            --is-public=True \
                            --file=./cirros-0.3.1-x86_64-disk.img

        # Delete the image file
        rm cirros-0.3.1-x86_64-disk.img


----


Logout of controller 1 and back into the HOST.

1. Plugin your OVS Network

   .. code-block:: bash

        # Configure OVS
        ovs-vsctl add-port br-eth2 eth2


#. On the compute node, if you find the files
   ``/usr/lib/libvirt/connection-driver/libvirt_driver_libxl.so`` and
   ``/usr/lib/libvirt/connection-driver/libvirt_driver_xen.so`` remove them.
   These files are for the xen hypervisor and may cause libvirt to fail to
   start.

   .. code-block:: bash

        # remove the files
        rm /usr/lib/libvirt/connection-driver/libvirt_driver_xen.so
        rm /usr/lib/libvirt/connection-driver/libvirt_driver_libxl.so

        # restart compute services
        /etc/init.d/libvirt-bin restart
        /etc/init.d/nova-compute restart


#. Setup the boot splash

   .. code-block:: bash

        if [ -f "/lib/plymouth/themes/ubuntu-text/ubuntu-text.plymouth" ];then
            cat > /lib/plymouth/themes/ubuntu-text/ubuntu-text.plymouth <<EOF
        [Plymouth Theme]
        Name=Ubuntu Text
        Description=Text mode theme based on ubuntu-logo theme
        ModuleName=ubuntu-text

        [ubuntu-text]
        title=Rackspace Private Cloud, [ESC] for progress
        black=0x000000
        white=0xffffff
        brown=0xff4012
        blue=0x988592
        EOF

            update-initramfs -u
        fi


#. Setup grub for fast booting

   .. code-block:: bash

        if [ -f "/etc/default/grub" ];then
            cat > /etc/default/grub <<EOF
        GRUB_DEFAULT=0
        GRUB_HIDDEN_TIMEOUT=0
        GRUB_HIDDEN_TIMEOUT_QUIET=true
        GRUB_TIMEOUT=2
        GRUB_DISTRIBUTOR="Rackspace Private Cloud"
        GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
        GRUB_CMDLINE_LINUX=""
        GRUB_RECORDFAIL_TIMEOUT=1
        EOF

            update-grub
        fi


#. Black list some modules

   .. code-block:: bash

        echo 'blacklist i2c_piix4' | tee -a /etc/modprobe.d/blacklist.conf
        update-initramfs -u -k all


#. Set up the MOTD on boot for controller1 and the host

   .. code-block:: bash

        # Remove MOTD files
        if [ -f "/etc/motd" ];then
          rm /etc/motd
        fi

        if [ -f "/var/run/motd" ];then
          rm /var/run/motd
        fi

        # Remove PAM motd modules from config
        if [ -f "/etc/pam.d/login" ];then
          sed -i '/pam_motd.so/ s/^/#\ /' /etc/pam.d/login
        fi

        if [ -f "/etc/pam.d/sshd" ];then
          sed -i '/pam_motd.so/ s/^/#\ /' /etc/pam.d/sshd
        fi

        cat > /opt/motd.sh <<EOF
        #!/usr/bin/env bash

        SYS_IP=\$(ip a l eth1 | grep -w inet | awk -F" " '{print \$2}'| sed -e 's/\/.*$//')
        cat >/etc/motd <<EOH

        This is an Openstack Deployment based on the Rackspace Private Cloud Software
        # ===========================================================================
            Controller1 SSH command        : ssh -p 2222 openstack@\${SYS_IP}
            Your OpenStack Password is     : secrete
            Admin SSH key has been set as  : adminKey
            Openstack Cred File is located : /root/openrc
            Horizon URL is                 : https://\${SYS_IP}:443
            Horizon User Name              : admin
            Horizon Password               : secrete
            Chef User Name is              : admin
            Chef Server Password is        : secrete
            Sandbox User Name              : root
            Sandbox Password               : secrete
        # ===========================================================================

        Remember! That this system is using Neutron. To gain access to an instance
        via the command line you MUST execute commands within in the namespace.
        Example, "ip netns exec NAME_SPACE_ID bash".

        This will give you shell access to the specific namespace routing table
        Execute "ip netns" for a full list of all network namespsaces on this Server.

        EOH

        EOF

        if [ -f "/opt/motd.sh" ];then
            chmod +x /opt/motd.sh
            /opt/motd.sh
            ln -f -s /etc/motd /etc/issue
        fi


#. Place this simple init script into ``/etc/init.d/rax-rebuild``

   .. code-block:: bash

        #!/usr/bin/env bash

        # Copyright 2013, Rackspace US, Inc.
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
        #
        # Author Kevin.Carter@Rackspace.com

        # chkconfig: 2345 99 99
        # Description: Build and Rebuild a virtual environment

        ### BEGIN INIT INFO
        # Provides:
        # Required-Start: $remote_fs $network $syslog
        # Required-Stop: $remote_fs $syslog
        # Default-Start: 2 3 4 5
        # Default-Stop: 0 1 6
        # Short-Description: Rackspace Appliance init script
        # Description: Build and Rebuild a virtual environment
        ### END INIT INFO

        # Set the Path
        export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        # What is the Name of this Script, and what are we starting
        PROGRAM="RACKSPACE_PRIVATE_CLOUD:"

        # Truncate the contents of our net rules
        function udev_truncate() {
            cat > /etc/udev/rules.d/70-persistent-net.rules<<EOF
        # Net Device Rules
        EOF
        }

        # Stop Swap
        function stop_swap() {
          SWAPFILE="/tmp/SwapFile"
          echo "Stopping Swap"
          swapoff -a
          sleep 2

          if [ -f "${SWAPFILE}" ];then
            echo "Removing Swap File."
            rm ${SWAPFILE}
          fi
        }

        # Stop the VM services
        function stop_vm() {
          # Stop all containers
          for i in $(/usr/bin/lxc-ls); do /usr/bin/lxc-stop -n $i || true; done

          # Flush all of the routes on the system
          ip route flush all
          sync
        }

        # Service functions
        case "$1" in
          start)
            clear
            echo "${PROGRAM} is Initializing..."
            /etc/init.d/networking restart
            /opt/swap.sh
            /opt/cinder.sh
            /opt/motd.sh
            for i in $(/usr/bin/lxc-ls); do /usr/bin/lxc-start -d -n $i || true; done
          ;;
          stop)
            echo "${PROGRAM} is Shutting Down..."
            stop_vm
            stop_swap
            udev_truncate
          ;;
          package-instance)
            stop_vm
            stop_swap
            udev_truncate

            echo "Performing A Zero Fill"
            set +e
            pushd /tmp
            cat /dev/zero > zero.fill
            sync
            sleep 1
            rm -f zero.fill
            sync
            sleep 1
            popd
            set -e
            sync
            sleep 1

            # Nuke our history
            echo '' | tee /root/.bash_history
            history -c
            sync

            shutdown -P now
          ;;
          *)
            USAGE="{start|stop|package-instance}"
            echo "Usage: $0 ${USAGE}" >&2
            exit 1
          ;;
        esac


#. Now make the init script run at boot.

   .. code-block:: bash

        chmod +x /etc/init.d/rax-rebuild
        update-rc.d rax-rebuild defaults


----

All done, now reboot your machine and if everything comes up you are good to go.
