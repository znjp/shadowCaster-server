import sys
from subprocess import call

#static_ip = sys.argv[1]		 # brings in the static IP as the first argument
#acName = sys.argv[2]
#acPass = sys.argv[3]

static_ip = "10.0.0"
num_addresses = 100

# before running AC setup, make sure raspian is installed and up to date

# this is the list of settings for the "router", line by line
line0  = "interface=wlan0"
line1  = "driver=nl80211"
line2  = "ssid=shadowCaster1"
line3  = "hw_mode=g"
line4  = "channel=7"
line5  = "wmm_enabled=0"
line6  = "macaddr_acl=0"
line7  = "auth_algs=1"
line8  = "ignore_broadcast_ssid=0"
#line9  = "wpa=2"
#line10 = "wpa_passphrase={}".format(acPass)
#line11 = "wpa_key_mgmt=WPA-PSK"
#line12 = "wpa_pairwise=TKIP"
#line13 = "rsn_pairwise=CCMP"



# install the two packages we need
# the "-y" argument automatically answers "yes" when it asks to confirm the install
try:
    call(["sudo", "apt-get", "-y", "install", "dnsmasq"])
    call(["sudo", "apt-get", "-y", "install", "hostapd"])
    #TODO: Install shadowcaster server dependencies here.
except Exception as e:
    print "Unable to install dependencies.", str(e)
    quit()

# stop the two packages so we can edit them
try:
    call(["sudo", "systemctl", "stop", "dnsmasq"])
    call(["sudo", "systemctl", "stop", "hostapd"])
except Exception as e:
    print "Unable to stop services.", str(e)
    quit()



# setting a static IP
# edits the existing dhcpcd config file and adds the static ip to the end
with open('/etc/dhcpcd.conf', 'a') as dhcpcd:
    dhcpcd.writelines(["interface wlan0\n", "static ip_address={}.1".format(static_ip)])

try:
    call(["sudo", "service", "dhcpcd", "restart"])
except Exception as e:
    print "Unable to restart dhcpcd", str(e)
    quit()


# editing the dnsmasq config file

# get rid of the old one
try:
    call(["sudo", "mv", "/etc/dnsmasq.conf", "/etc.dnsmasq.conf.orig"])
except Exception as e:
    print "Unable to rename dnsmasq.conf"
    quit()


# make a new one with the information we want
dnsmasq_config = open("/etc/dnsmasq.conf", "w+")
dnsmasq_config.writelines(["interface=wlan0\n", "dhcp-range={}.2,{}.".format(static_ip, static_ip) + str(num_addresses + 2) + ",255.255.255.0,24h\n", "address=/#/{}.1".format(static_ip)])
dnsmasq_config.close()


# configuring hostapd
# create and edit a new configuation file
hostapd_config = open("/etc/hostapd/hostapd.conf", "w+")
hostapd_config.writelines("\n".join([line0, line1, line2, line3, line4, line5, line6, line7, line8]))
hostapd_config.close()


# edit the hostapd file to show the location of the config file
with open('/etc/default/hostapd', 'r') as infile:
    data = infile.readlines()

data[9] = "DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"\n"

with open('/etc/default/hostapd', 'w') as outfile:
    outfile.writelines( data )


call(["sudo", "systemctl", "start", "hostapd"])
call(["sudo", "systemctl", "start", "dnsmasq"])
