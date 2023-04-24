# General Setup

Firstly, make sure your Raspberry Pi is up to date with:

```
pi@raspberrypi:~ $ sudo apt-get update
pi@raspberrypi:~ $ sudo apt-get upgrade
pi@raspberrypi:~ $ sudo reboot
```

## Switch over to systemd-networkd

Using ```systemd-networkd``` instead of default ```dhcpcd``` is not meaningful in all cases.

**```Explanation```** ```networkd``` is a small and lean service to configure network interfaces, 
designed mostly for server use cases in a world with hotplugged and virtualized 
networking. Its configuration is similar in spirit and abstraction level to ```ifupdown```, 
but you don't need any extra packages to configure bridges, bonds, vlan etc. 
It is not very suitable for managing ```WLANs``` yet; ```NetworkManager``` is still much more 
appropriate for such Desktop use cases. But for a RasPi laying near by a TV or 
amplifier and doing its work 24/7 for streaming audio or video or for a camera etc., 
```systemd-networkd``` is a good choice.

**But you have to do a complete switch. There is no way to mix up with ```Debian networking``` 
and/or ```dhcpcd```.**

For this tutorial I assume you have setup an installation from the image with a 
network connection either wired (works out of the box) or using a wireless connection.

Do the following:
 ```
 # Deinstall classic networking
pi@raspberrypi:~ $ sudo -Es 
root@raspberrypi:~ # apt --autoremove purge ifupdown dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog
root@raspberrypi:~ # apt-mark hold ifupdown dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog raspberrypi-net-mods openresolv
root@raspberrypi:~ # rm -r /etc/network /etc/dhcp

# Setup/enable systemd-resolved and systemd-networkd
root@raspberrypi:~ # apt --autoremove purge avahi-daemon
root@raspberrypi:~ # apt-mark hold avahi-daemon libnss-mdns
root@raspberrypi:~ # apt install libnss-resolve
root@raspberrypi:~ # ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
root@raspberrypi:~ # systemctl enable systemd-networkd.service systemd-resolved.service
root@raspberrypi:~ # exit
pi@raspberrypi:~ $
```

That's it. You have now switched from standard networking to ```systemd-networkd```.
  
## Configure wpa_supplicant as access point

To configure ```wpa_supplicant``` as access point create this file with your settings 
for ```country=```, ```ssid=```, ```psk=``` and maybe ```frequency=```.

```
pi@raspberrypi:~ $ sudo nano /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
```

If the file exists, make sure to delete it or overwrite it with the following text.
 
```
network={
    ssid="RPiNet"
    mode=2
    frequency=2437
    #key_mgmt=NONE   # uncomment this for an open hotspot
    # delete next 3 lines if key_mgmt=NONE
    key_mgmt=WPA-PSK
    proto=RSN WPA
    psk="password"
}
```

Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.

```
pi@raspberrypi:~ $ sudo chmod 600 /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
pi@raspberrypi:~ $ sudo systemctl disable wpa_supplicant.service
pi@raspberrypi:~ $ sudo systemctl enable wpa_supplicant@wlan0.service
pi@raspberrypi:~ $ sudo rfkill unblock wlan
```
That's it for the general setup. You can now choose which configuration to follow from the ones bellow.

# Setting up a standalone access point

The ip addresses in this example are arbitrary. You can choose your own.
```
                   wifi
  mobile-phone <~.~.~.~.~> (wlan0)RPi(eth0)
              \             /
             (dhcp)   192.168.4.1
```

This step supposes you have completed the **"General Setup"** step. 

**```Explanation ```** Here, we will create
a file that creates an access point from the ```wlan0```. **Nothing else will be configured so
take note that you will not have access to the internet even if you are connected with
an ethernet cable!**

```
pi@raspberrypi:~ $ sudo nano /etc/systemd/network/08-wlan0.network
```

If the file exists, make sure to delete it or overwrite it with the following text.
 
```
[Match]
Name=wlan0
[Network]
Address=192.168.4.1/24 # you can choose your own ip address
MulticastDNS=yes
DHCPServer=yes
```

Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.

That's it. Reboot.

```
pi@raspberrypi:~ $ sudo reboot
```

You should now be able to see your acess point within you available wifi networks
on you laptop or any other wifi-able device. You can connect to it using the password
we defined earlier. **Again, note that you have no internet access what-so-ever at this
point.**

# Setting up an access point, with eth0, without routing 
The ip addresses in this example are arbitrary. You can choose your own.
```
                                 |
                 wifi            |           wired            wan
mobile-phone <~.~.~.~.~> (wlan0)RPi(eth0) <---------> router <---> INTERNET
            \             /      |     \             /
           (dhcp)   192.168.4.1  |    (dhcp)   192.168.50.1
```

This step supposes you have done **"Setting up a standalone access point"** step.

**```Explanation```** We will now  create a configuration for the ```eth0``` which will grant you access to the
internet from the Raspberry Pi **(but not from the devices connected to the acces point!)** if you are connected with an ethernet cable to your router.

```
pi@raspberrypi:~ $ sudo nano /etc/systemd/network/04-eth0.network
```

If the file exists, make sure to delete it or overwrite it with the following text.
 
```
[Match]
Name=eth0
[Network]
DHCP=yes # comment this line and uncomment the next one if you want static address
#Address=192.168.50.2 # you can choose your own address, this is an example
```

**```Important!```** **If you are giving the static address to the eth0 make sure it's not the
same subnet as the ```wlan0``` address!**

Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.

That's it. Reboot.

```
pi@raspberrypi:~ $ sudo reboot
```

You can now access the internet from the Raspberry Pi. Note that we have not set up
any routing as of now so you can't access the internet from your devices connected to 
the access point of the Raspberry Pi.

# Setting up an access point, with eth0, with NAT
The ip addresses in this example are arbitrary. You can choose your own.
```
                 wifi                        wired            wan
mobile-phone <~.~.~.~.~> (wlan0)RPi(eth0) <---------> router <---> INTERNET
            \             /            \
           (dhcp)   192.168.4.1       (dhcp)
```

This step supposes you have done the **"General Setup"** step.

**```Explanation```** Here, we will create
configuration for the ```wlan0``` and the ```eth0``` so you can have internet access from the
devices that are connected to the Raspberry Pi access point. If you have tried one 
of the previous setups then you can just overwrite the two files. 

If you have no access to the internet router you can fake it 
with ```NAT``` (network address translation) to tell it a lie that all packages are 
coming from your RasPi AP. *But this is not clean routing and has limitations. 
Clients on the subnet of the router cannot connect to clients on the wifi.*
But in most cases this is not needed so this setup is recommended because it 
simplifies the setup.

First, let's create a configuration for the ```wlan0```:

```
pi@raspberrypi:~ $ sudo nano /etc/systemd/network/08-wlan0.network
```

If the file exists, make sure to delete it or overwrite it with the following text.
 
```
[Match]
Name=wlan0
[Network]
Address=192.168.4.1/24 # you can choose your own ip address
MulticastDNS=yes
# IPMasquerade is doing NAT
IPMasquerade=yes
DHCPServer=yes
[DHCPServer]
DNS=84.200.69.80 1.1.1.1
```

Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.

Next, let's create it for the ```eth0```:

```
pi@raspberrypi:~ $ sudo nano /etc/systemd/network/04-eth0.network
```

If the file exists, make sure to delete it or overwrite it with the following text.
 
```
[Match]
Name=eth0
[Network]
DHCP=yes # comment this line and uncomment the next one if you want static address
#Address=192.168.50.2 # you can choose your own address
```

**```Important!```** **If you are giving the static address to the ```eth0``` make sure it's not the
same subnet as the ```wlan0``` address!**

Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.

**```Hint```** If you decided to use the ```DHCP``` for the ```eth0```, make sure you know which
ip subnet your router gave it so you can appropriately give you ```wlan0``` a different one.
On windows, connect to your network over wifi or ethernet cable and type  ```ipconfig``` in the 
command prompt to see which ip address you got. On linux, use ```ifconfig```.

That's it. Reboot.

```
pi@raspberrypi:~ $ sudo reboot
```

# Setting up an access point with a bridge
The ip addresses in this example are arbitrary. You can choose your own.
```
                              RPi
               wifi   ┌──────bridge──────┐   wired            wan
mobile-phone <.~.~.~> │(wlan0) br0 (eth0)│ <-------> router <-----> INTERNET
            \                   |                   / DHCP-server
           (dhcp              (dhcp           192.168.50.1
        from router)       from router)
```

This step supposes you have done the **"General Setup"** step. Make sure to delete all
the files in the ```/etc/systemd/network/ ```except  ```99-default.link```.

**```Explanation```** If you have already an ethernet network with ```DHCP``` server and 
internet router and you want to expand it with a wifi access point but with the 
same ip addresses then you use a bridge. This is often used as an uplink to a router.

Let's create the ```bridge``` files:

```
pi@raspberrypi:~ $ sudo nano /etc/systemd/network/02-br0.netdev
```

In the empty file editor write the following:
 
```
[NetDev]
Name=br0
Kind=bridge
```

Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.

```
pi@raspberrypi:~ $ sudo nano /etc/systemd/network/04-br0_add-eth0.network
```

In the empty file editor write the following:
 
```
[Match]
Name=eth0
[Network]
Bridge=br0
```

Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.


```
pi@raspberrypi:~ $ sudo nano /etc/systemd/network/12-br0_up.network
```

In the empty file editor write the following:
 
```
[Match]
Name=br0
[Network]
MulticastDNS=yes
DHCP=yes
# to use static IP uncomment these and comment DHCP=yes
#Address=192.168.50.60/24
#Gateway=192.168.50.1
#DNS=84.200.69.80 1.1.1.1
```

Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.

Now we have to tell ```wpa_supplicant``` to use a bridge. We do it by modifying its service with:

```
pi@raspberrypi:~ $ sudo systemctl edit wpa_supplicant@wlan0.service
```

In the empty editor insert these statements, save them and quit the editor:

```
[Service]
ExecStartPre=/sbin/iw dev %i set type __ap
ExecStartPre=/bin/ip link set %i master br0

ExecStart=
ExecStart=/sbin/wpa_supplicant -c/etc/wpa_supplicant/wpa_supplicant-%I.conf -Dnl80211,wext -i%I -bbr0

ExecStopPost=-/bin/ip link set %i nomaster
ExecStopPost=-/sbin/iw dev %i set type managed
```

That's it. Reboot.

```
pi@raspberrypi:~ $ sudo reboot
```

**```Additional details```** We have to tell ```wpa_supplicant``` that its interface ```wlan0``` 
is slave of a bridge. Otherwise it will reject client connects with "wrong password" 
means the key negotiation does not work. When we tell ```/sbin/wpa_supplicant``` with option 
```-dbr0``` to use a bridge for ```wlan0``` then the interface must already be a member of the bridge. 
That's what we do with the drop in file (overlay) for the ```wpa_supplicant service```. 
The empty statement ```ExecStart=``` deletes the old entry. Otherwise you have two lines 
```ExecStart=``` and ```wpa_supplicant``` will start two times. The original ```ExecStart=``` you can 
view with ```systemctl cat``` ```wpa_supplicant@wlan0.service```.

**```Potential problem!```**Normally the router you are connected to with the ethernet cable has a ```DHCP``` 
server enabled. The bridge is also transparent for ```DHCP``` requests from the stations 
(devices connected to the access point) so you don't have to worry about configuration 
of its interfaces with ip addresses and options. The router will serve it.

But if the router doesn't have a ```DHCP``` server, you can setup one on the RasPi. 
```systemd-networkd``` has options to configure its built-in ```DHCP``` server but the problem is 
that ```systemd-networkd``` assumes it is running on the router itself and that's not true in 
this case. It will serve wrong options to the stations, in particular the router option. 
There is no way to configure it. So we have to install ```dnsmasq``` in this case that can be 
configured as needed. Install and configure it with (example, use your own ip addresses):

```
pi@raspberrypi:~ $ sudo apt install dnsmasq
pi@raspberrypi:~ $ sudo systemctl stop dnsmasq
pi@raspberrypi:~ $ mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
```

```
pi@raspberrypi:~ $ sudo nano /etc/dnsmasq.conf 
```

Add the following at the end of the file:

```
interface=br0
    dhcp-range=192.168.50.128,192.168.50.164,255.255.255.0,24h
    dhcp-option=option:router,192.168.50.1
    dhcp-option=option:dns-server,8.8.8.8,1.1.1.1
```
Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.


```
pi@raspberrypi:~ $ sudo reboot
```

In this example ip addresses ```192.168.50.128``` to ```192.168.50.164``` are reserved to 
give to stations. For other static ip addresses use one outside this pool, also 
the ip address for the bridge itself. 

# Final word

That's it for this tutorial. For additional inquiries visit the original question
from which's answer this tutorial had been derived. [Access Point-The Easy Way](https://raspberrypi.stackexchange.com/questions/88214/setting-up-a-raspberry-pi-as-an-access-point-the-easy-way/88234#88234)