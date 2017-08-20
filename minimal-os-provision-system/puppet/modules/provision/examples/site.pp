$domain_name = $::domain
$network_address = hiera('network_address')
$network_mask = hiera('network_mask')
$broadcast_address = hiera('broadcast_address')
$start_address = hiera('start_address')
$end_address = hiera('end_address')
$router = hiera('router')
$next_server = hiera('next_server')
$dns_address = hiera('dns_address')
$reverse_zone = hiera('reverse_zone')
$forwarders = hiera('forwarders')
$ddns_key = hiera('ddns_key')
$ddns_key_algorithm = hiera('ddns_key_algorithm')
$ddns_key_name = hiera('ddns_key_name')
$known_hosts = hiera('known_hosts')
$bootstrap_menu_label = hiera('bootstrap_menu_label')
$bootstrap_kernel_path = hiera('bootstrap_kernel_path')
$bootstrap_initrd_path = hiera('bootstrap_initrd_path')
$bootstrap_kernel_params = hiera('bootstrap_kernel_params')
$chain32_files = tftp_files("/var/lib/tftpboot/pxelinux.cfg", $known_hosts)
$bootstrap_kernel_params = inline_template("ksdevice=bootif lang= console=ttyS0,9600 console=tty0 toram locale=en_US text fetch=http://<%= @next_server %>:8080/bootstraps/active_bootstrap/root.squashfs boot=live biosdevname=0 components ip=frommedia ethdevice-timeout=120 net.ifnames=1 panic=60 hostname=bootstrap domain=<%= @domain_name %>")

class { "::provision::dhcpd" :
  network_address => $network_address,
  network_mask => $network_mask,
  broadcast_address => $broadcast_address,
  start_address => $start_address,
  end_address => $end_address,
  router => $router,
  next_server => $next_server,
  dns_address => $dns_address,
  domain_name => $domain_name,
  reverse_zone => $reverse_zone,
  ddns_key => $ddns_key,
  ddns_key_algorithm => $ddns_key_algorithm,
  ddns_key_name => $ddns_key_name,
  known_hosts => $known_hosts,
}

class { "::provision::named" :
  domain_name => $domain_name,
  reverse_zone => $reverse_zone,
  dns_address => $dns_address,
  forwarders => $forwarders,
  ddns_key => $ddns_key,
  ddns_key_algorithm => $ddns_key_algorithm,
  ddns_key_name => $ddns_key_name,
}

class { "::provision::tftp" :
  bootstrap_menu_label => $bootstrap_menu_label,
  bootstrap_kernel_path => $bootstrap_kernel_path,
  bootstrap_initrd_path => $bootstrap_initrd_path,
  bootstrap_kernel_params => $bootstrap_kernel_params,
  chain32_files => $chain32_files,
}
