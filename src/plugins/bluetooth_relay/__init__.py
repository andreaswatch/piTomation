"""
Provides a RFCOMM Server to receive messages.


From: https://forums.raspberrypi.com/viewtopic.php?t=108581:

sudo nano /etc/dbus-1/system.d/bluetooth.conf

  <policy user="pi">
    <allow send_destination="org.bluez"/>
    <allow send_interface="org.bluez.Agent1"/>
    <allow send_interface="org.bluez.GattCharacteristic1"/>
    <allow send_interface="org.bluez.GattDescriptor1"/>
    <allow send_interface="org.freedesktop.DBus.ObjectManager"/>
    <allow send_interface="org.freedesktop.DBus.Properties"/>
  </policy>
"""