# **RasPiUtilities**

```RasPiUtilities``` is a Python library that makes it possible to switch between the access point mode and the station mode of the Raspberry Pi. It uses ```NAT``` to enable internet access for the connected devices in the access point mode (ethernet connection must be estabished). Library also supports automatic wifi switching between available wifi networks based on signal strength. The user sets the signal strength limit and the Raspberry Pi keeps it's connection to the connected network as long as it's signal strength is above the limit. When it falls below, Raspberry Pi automatically connects the the strongest available network.

## **Setup**

It is necessary to configure the Raspberry Pi to use ```systemd-networkd``` instead of the default networking mode for this library to work. I assume you have completed a fresh install of your Raspberry Pi OS.  

**For a more detailed tutorial on the general access point setup with various different methods open [```general_access_point_setup```](general_access_point_setup.md) tutorial located in this repository.**

### Update and upgrade your Raspberry Pi  

Let's begin configuring you Raspberry Pi. Make sure you are up to date and  fully upgraded.

```
pi@raspberrypi:~ $ sudo apt-get update
pi@raspberrypi:~ $ sudo apt-get upgrade
pi@raspberrypi:~ $ sudo reboot
```
### Uninstall classic networking and switch over to systemd-networkd

For this library to work, it is necessary to completely switch over to ```systemd-networkd```.

 ```
 # Disable debian networking and dhcpcd
pi@raspberrypi:~ $ sudo -Es 
root@raspberrypi:~ # systemctl mask networking.service dhcpcd.service
root@raspberrypi:~ # sudo mv /etc/network/interfaces /etc/network/interfaces~
root@raspberrypi:~ # sed -i '1i resolvconf=NO' /etc/resolvconf.conf

# Enable systemd-networkd
root@raspberrypi:~ # systemctl enable systemd-networkd.service systemd-resolved.service
root@raspberrypi:~ # ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf
```

### Setup wpa_supplicant as wifi client with wlan0  

Setup ```wpa_supplicant``` to be in the station mode with ```wlan0``` by creating the following file:

```
pi@raspberrypi:~ $ sudo nano /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
```

If the file exists, make sure to delete it or overwrite it with the following text.

```
country=ME
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
```

Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.

```
pi@raspberrypi:~ $ sudo chmod 600 /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
pi@raspberrypi:~ $ sudo systemctl disable wpa_supplicant.service
pi@raspberrypi:~ $ sudo systemctl enable wpa_supplicant@wlan0.service
```

### Setup wpa_supplicant as access point with ap0

Setup ```wpa_supplicant``` to be in the access point mode with ```ap0``` by creating the following file:

```
pi@raspberrypi:~ $ sudo nano /etc/wpa_supplicant/wpa_supplicant-ap0.conf
```

If the file exists, make sure to delete it or overwrite it with the following text.

```
country=ME
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="RPiNet"
    mode=2
    key_mgmt=WPA-PSK
    proto=RSN WPA
    psk="password1"
    frequency=2412
}
```
Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.

```
pi@raspberrypi:~ $ sudo chmod 600 /etc/wpa_supplicant/wpa_supplicant-ap0.conf
```

### Configuring interfaces

To configure interfaces create the following files:

#### eth0

```
pi@raspberrypi:~ $ sudo nano /etc/systemd/network/04-eth0.network
```
```
[Match]
Name=eth0
[Network]
DHCP=yes
```
Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.

#### wlan0

```
pi@raspberrypi:~ $ sudo nano /etc/systemd/network/08-wlan0.network
```
```
[Match]
Name=wlan0
[Network]
DHCP=yes
```
Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.

#### ap0

```
pi@raspberrypi:~ $ sudo nano /etc/systemd/network/12-ap0.network
```
```
[Match]
Name=ap0
[Network]
Address=192.168.4.1/24
MulticastDNS=yes
IPMasquerade=yes # IPMasquerade is doing NAT
DHCPServer=yes
[DHCPServer]
DNS=84.200.69.80 1.1.1.1
```
Press ```CTRL+X``` then ```Y``` and then press ```Enter``` to save the file.

### Modify service for access point to use ap0

```ap0``` is a virtual interface and it must be created and deleted with start/stop of the service. It is also required to modify dependencies. This cannot be done with a drop in file, so we have to modify the full service. In addition this service conflicts with the client connection service with ```wlan0```.

```
pi@raspberrypi:~ $ sudo systemctl disable wpa_supplicant@ap0.service
pi@raspberrypi:~ $ sudo systemctl edit --full wpa_supplicant@ap0.service
```

Edit the file to look like this:

```
[Unit]
Description=WPA supplicant daemon (interface-specific version)
Requires=sys-subsystem-net-devices-wlan0.device
After=sys-subsystem-net-devices-wlan0.device
Before=network.target
Wants=network.target

# NetworkManager users will probably want the dbus version instead.

[Service]
Type=simple
ExecStartPre=/sbin/iw dev wlan0 interface add ap0 type __ap
ExecStart=/sbin/wpa_supplicant -c/etc/wpa_supplicant/wpa_supplicant-%I.conf -Dnl80211,wext -i%I
ExecStopPost=/sbin/iw dev ap0 del

[Install]
Alias=multi-user.target.wants/wpa_supplicant@%i.service
```

### Finished

Now you can determine in which mode the Raspberry Pi should start after bootup. Just enable that service and disable the other one. If I want to start with client connection:

```
pi@raspberrypi:~ $ sudo systemctl enable wpa_supplicant@wlan0.service
pi@raspberrypi:~ $ sudo systemctl disable wpa_supplicant@ap0.service
```

You should then be able to switch the service with:

```
pi@raspberrypi:~ $ sudo systemctl start wpa_supplicant@ap0.service
pi@raspberrypi:~ $ sudo systemctl stop wpa_supplicant@ap0.service
pi@raspberrypi:~ $ sudo systemctl start wpa_supplicant@wlan0.service
pi@raspberrypi:~ $ sudo systemctl stop wpa_supplicant@wlan0.service
```

For our purposes, it is necessary to stop ```wlan0.service``` and ```ap0.service``` after bootup with:

```
pi@raspberrypi:~ $ sudo systemctl stop wpa_supplicant@ap0.service
pi@raspberrypi:~ $ sudo systemctl stop wpa_supplicant@wlan0.service
```

## **Installation**

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install wpa_supplicant. It is the only necessary external library you need to install.

```bash
pip3 install wpa_supplicant
```

If the warning to install ```service_identity``` comes up do so.

```bash
pip3 install service_identity
```

## **Usage**

You can start the script which automates everything for you.

```bash
python3 begin.py
```
However, this calling doesn't include a wifi database so you can't really connect to any network. Better option is:

```bash
python3 begin.py -w wifis.txt
```

Here, ```wifis.txt``` includes some networks and their passwords so you can connect. Here is an example of the file:

```bash
WifiNetwork1      password123       WPA-PSK
WifiNetwork2      samplepassword    WPA-PSK
```

You can customize the calling by passing numerous parameters. Here is the example
from the begin.py script.

```python
parser = argparse.ArgumentParser(description='Raspberry Pi utility script')
parser.add_argument("-w", "--known_wifi_network_database_name", help = "known wifi network database name", default = '')
parser.add_argument("-i", "--interface_name", help = "interface name", default = 'wlan0')
parser.add_argument("-s", "--signal_strength_limit", help = "minimum signal strength", default = -60)
```
You can also make your own script which uses this library. Here is an example:

```python
from RasPUtilities import RasPUtilities

# Start the script which enables user to use the utilities
#
def main():

    # Creating a RasPUtilities object and starting logging process
    RasPiUtility = RasPUtilities(known_wifi_network_database_name = args.known_wifi_network_database_name,
                                        interface_name = 'wlan0',
                                        signal_strength_limit = -60
                                        )
    # Start the automatization process
    RasPiUtility.start()

if __name__ == '__main__':

    main()
```

To change the mode from ```wifi station (script default)``` to ```access point``` input ```'a'``` and wait for the system to set up the access point. Input ```'s'``` for the reverse procedure and wait for the system to restore it's ```wifi station mode``` settings.
