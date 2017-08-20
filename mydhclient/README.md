## Mydhclient ##

This is a dummy implementation of DHCP protocol that allows you to
emulate high load DHCP floods like what is usually the case in data centers
when, for example, a thousand of nodes are powered on at once.
The use case for such a tool is to test various DHCP server implementations
like dnsmasq or isc-dhcp with various configurations and figure out
how they behave under high load.

### Helper scripts ###

There are a few helper shell scripts in the `./scripts` directory. These scripts
could be used for preparing a testing lab and run DHPC performance tests.

### Implementation ###

DHCP protocol is implemented from scratch. Network interaction is implemented
using pcap features.

### TODO ###
  * Use puppet for managing dnsmasq and isc-dhcp
