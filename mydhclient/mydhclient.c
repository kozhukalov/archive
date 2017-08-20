#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <pcap/pcap.h>
#include <inttypes.h>
#include <net/ethernet.h>
#include <net/if.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/udp.h>

/* TODO: Substitute C types with user defined types (typedef) */


#define VERSION "0.1"
#define MAC_STR_LEN 17
#define IP_STR_LEN 15
#define DEV_STR_LEN 32

#define DHCP_SERVER_PORT 67
#define DHCP_CLIENT_PORT 68

#define DHCP_CHADDR_LEN 16
#define DHCP_SNAME_LEN  64
#define DHCP_FILE_LEN   128

#define DHCP_REQUEST 1
#define DHCP_RESPONSE 2
/* Ethernet 10Mb
 * https://tools.ietf.org/html/rfc1700
 */
#define DHCP_HTYPE 1

/* This 4-bytes field is set at the beginning of Options field */
#define DHCP_MAGIC_COOKIE   0x63825363

/*
 * DHCP options are listed in https://tools.ietf.org/html/rfc2132
 */
#define DHCP_OPTION_SUBNET_MASK 1
#define DHCP_OPTION_TIME_OFFSET 2
#define DHCP_OPTION_ROUTER 3
#define DHCP_OPTION_DOMAIN_NAME_SERVER 6
#define DHCP_OPTION_HOST_NAME 12
#define DHCP_OPTION_DOMAIN_NAME 15
#define DHCP_OPTION_BROADCAST_ADDRESS 28
#define DHCP_OPTION_NTP_SERVERS 42
#define DHCP_OPTION_REQUESTED_IP_ADDRESS 50
#define DHCP_OPTION_MESSAGE_TYPE 53
#define DHCP_OPTION_SERVER_IDENTIFIER 54
#define DHCP_OPTION_PARAMETER_REQUEST_LIST 55
#define DHCP_OPTION_DOMAIN_SEARCH 119
#define DHCP_OPTION_END 255

#define DHCP_MESSAGE_TYPE_DISCOVER 1
#define DHCP_MESSAGE_TYPE_OFFER    2
#define DHCP_MESSAGE_TYPE_REQUEST  3
#define DHCP_MESSAGE_TYPE_ACK      5

#define SESSION_INIT 0
#define SESSION_DISCOVER_SENT 1
#define SESSION_OFFER_RECEIVED 2
#define SESSION_REQUEST_SENT 3
#define SESSION_ACK_RECEIVED 4
#define SESSION_DONE 5

#define LOG(format, args...)                                           \
  do {                                                                 \
    fprintf(stdout, "%s:%d:%s:: ", __FILE__, __LINE__, __FUNCTION__);  \
    fprintf(stdout, format, ##args);                                   \
    fprintf(stdout, "\n");                                             \
  } while(0)


/*
 * http://www.tcpipguide.com/free/t_DHCPMessageFormat.htm
 * https://tools.ietf.org/html/rfc2131
 */
typedef struct dhcph
{
  u_int8_t    op;
  u_int8_t    htype;
  u_int8_t    hlen;
  u_int8_t    hops;
  u_int32_t   xid;
  u_int16_t   secs;
  u_int16_t   flags;
  u_int32_t   ciaddr;
  u_int32_t   yiaddr;
  u_int32_t   siaddr;
  u_int32_t   giaddr;
  u_int8_t    chaddr[DHCP_CHADDR_LEN];
  u_int8_t    sname[DHCP_SNAME_LEN];
  u_int8_t    file[DHCP_FILE_LEN];
  u_int32_t   magic_cookie;
} dhcph_t;

/* typedef struct ether_addr etha_t; */
typedef struct ether_header eth_t;
typedef struct ip ip_t;
typedef struct udphdr udp_t;

typedef struct session
{
  u_int32_t xid;
  u_int32_t status;
  u_int8_t etha[ETH_ALEN];
  u_int32_t client_ip;
  u_int32_t server_ip;
  u_int32_t router;
  u_int32_t broadcast;
  u_int32_t mask;
  /* TODO There could be more than one dns */
  u_int32_t dns;
  /* Could be one of DHCP_MESSAGE_TYPE_* */
  u_int8_t message_type;
  struct session *next;
} session_t;


session_t *session_storage = NULL;
pcap_t *pcap_handle;

void put_session(const session_t *session_p)
{
  /*
   * Be careful when allocating memory for session.
   * Use memset to set allocated memory to zero or set next
   * field to NULL explicitly before adding session to storage.
   */
  if (session_storage == NULL){
    session_storage = session_p;
    return;
  }

  session_t *cur = session_storage;
  while (1){
    if (cur->next == NULL)
      break;
    cur = cur->next;
  }
  cur->next = session_p;
}

session_t *get_session(const u_int32_t xid)
{
  if (session_storage == NULL){
    return NULL;
  }
  session_t *cur = session_storage;
  while (1){
    if (cur->xid == xid){
      return cur;
    }
    if (cur->next == NULL)
      return NULL;
    cur = cur->next;
  }
}


static void print_packet(const u_int8_t *data, int len)
{
  for (int i = 0; i < len; i++) {
    if (i % 0x10 == 0)
      printf("\n %04x :: ", i);
    printf("%02x ", data[i]);
    }
  printf("\n");
  printf("========================================================\n");
}

/* This function calculates checksum of a set of 16 bit words
   That is why we cast to poiter to unsigned short */
unsigned short checksum(unsigned short *ptr, int nbytes)
{
  unsigned long sum;
  unsigned char tmp;

  sum = 0;
  while (nbytes > 1) {
    sum += *(ptr++);
    nbytes -= 2;
  }

  /* If originally there was an odd number of bytes */
  if (nbytes == 1) {
    tmp = *(u_char *)ptr;
    sum += tmp;
  }

  sum = (sum >> 16) + (sum & 0x0000ffff);
  sum = sum + (sum >> 16);
  return (unsigned short)~sum;
}

int mac2etha(u_int8_t *etha, const char *mac)
{
  sscanf(mac, "%02x:%02x:%02x:%02x:%02x:%02x%c",
         &etha[0], &etha[1], &etha[2],
         &etha[3], &etha[4], &etha[5]);
}

void etha2mac(char *mac, const u_int8_t *etha)
{
  sprintf(mac, "%02x:%02x:%02x:%02x:%02x:%02x",
          etha[0], etha[1], etha[2],
          etha[3], etha[4], etha[5]);
}

void ip2s(char *s, const u_int32_t ip)
{
  sprintf(s, "%d.%d.%d.%d",
          (u_int8_t)ip,
          (u_int8_t)(ip >> 8),
          (u_int8_t)(ip >> 16),
          (u_int8_t)(ip >> 24));
}

/* TODO change src_mac and dst_mac types to struct ether_addr */
void prepare_ether_header(eth_t *eth_p, int *len_p, const u_int8_t *src_etha, const u_int8_t *dst_etha)
{
  *len_p += sizeof(eth_t);
  memcpy(eth_p->ether_shost, src_etha, sizeof(u_int8_t) * ETH_ALEN);
  memcpy(eth_p->ether_dhost, dst_etha, sizeof(u_int8_t) * ETH_ALEN);
  eth_p->ether_type = htons(ETHERTYPE_IP);
}



void prepare_ip_header(ip_t *ip_p, int *len_p, const u_int32_t src_ip, const u_int32_t dst_ip)
{
  *len_p += sizeof(ip_t);
  ip_p->ip_hl = 5;
  ip_p->ip_v = IPVERSION;
  ip_p->ip_tos = 0x10;
  ip_p->ip_len = htons(*len_p);
  ip_p->ip_id = htonl(0xffff);
  ip_p->ip_off = 0;
  ip_p->ip_ttl = 16;
  ip_p->ip_p = IPPROTO_UDP;
  ip_p->ip_sum = 0;
  ip_p->ip_src.s_addr = src_ip;
  ip_p->ip_dst.s_addr = dst_ip;
  ip_p->ip_sum = checksum((unsigned short *)ip_p, sizeof(ip_t));
}

void prepare_udp_header(udp_t *udp_p, int *len_p, const short src_port, const short dst_port)
{
  /* TODO: What is it? */
  if (*len_p & 1)
    *len_p += 1;
  *len_p += sizeof(udp_t);
  udp_p->uh_sport = htons(src_port);
  udp_p->uh_dport = htons(dst_port);
  udp_p->uh_ulen = htons(*len_p);
  udp_p->uh_sum = 0;
}


void prepare_dhcp_header(dhcph_t *dhcph_p, int *len_p, session_t *session_p)
{
  *len_p += sizeof(dhcph_t);
  memset(dhcph_p, 0, sizeof(dhcph_t));
  dhcph_p->op = DHCP_REQUEST;
  dhcph_p->htype = DHCP_HTYPE;
  dhcph_p->hlen = ETH_ALEN;
  dhcph_p->hops = 0;
  dhcph_p->xid = session_p->xid;
  dhcph_p->secs = 0;
  dhcph_p->flags = 0x8000;
  dhcph_p->ciaddr = 0;
  dhcph_p->yiaddr = 0;
  dhcph_p->siaddr = 0;
  dhcph_p->giaddr = 0;
  /*
   * Size of DHCP chaddr field is 16 bytes (to support other hardware address types)
   * while ETH_ALEN is equal to 6
   */
  memcpy(dhcph_p->chaddr, session_p->etha, sizeof(u_int8_t) * ETH_ALEN);
  memset(dhcph_p->sname, 0, sizeof(u_int8_t) * DHCP_SNAME_LEN);
  memset(dhcph_p->file, 0, sizeof(u_int8_t) * DHCP_FILE_LEN);
  dhcph_p->magic_cookie = htonl(DHCP_MAGIC_COOKIE);
}


void prepare_dhcp_discover_options(u_int8_t *dhcpo_p, int *len_p)
{
  int offset = 0;
  int option_len;

  /* Set DHCP message type */
  option_len = 3 * sizeof(u_int8_t);
  memset(dhcpo_p + offset, DHCP_OPTION_MESSAGE_TYPE, sizeof(u_int8_t));
  memset(dhcpo_p + offset + 1, 1, sizeof(u_int8_t));
  memset(dhcpo_p + offset + 2, DHCP_MESSAGE_TYPE_DISCOVER, sizeof(u_int8_t));
  *len_p += option_len;
  offset += option_len;

  /* Set DHCP parameter request list */
  u_int8_t parameter_request_list_data[] = {
    DHCP_OPTION_SUBNET_MASK,
    DHCP_OPTION_ROUTER,
    DHCP_OPTION_BROADCAST_ADDRESS,
    DHCP_OPTION_DOMAIN_NAME,
    DHCP_OPTION_DOMAIN_NAME_SERVER
  };
  option_len = 2 * sizeof(u_int8_t) + sizeof(parameter_request_list_data);
  memset(dhcpo_p + offset, DHCP_OPTION_PARAMETER_REQUEST_LIST, sizeof(u_int8_t));
  memset(dhcpo_p + offset + 1, sizeof(parameter_request_list_data), sizeof(u_int8_t));
  memcpy(dhcpo_p + offset + 2, parameter_request_list_data, sizeof(parameter_request_list_data));
  *len_p += option_len;
  offset += option_len;

  /* Set DHCP option ending */
  option_len = 2 * sizeof(u_int8_t);
  memset(dhcpo_p + offset, DHCP_OPTION_END, sizeof(u_int8_t));
  memset(dhcpo_p + offset + 1, 0, sizeof(u_int8_t));
  *len_p += option_len;
  offset += option_len;
}


void prepare_dhcp_request_options(u_int8_t *dhcpo_p, int *len_p, session_t *session_p)
{
  int offset = 0;
  int option_len;

  /* Set DHCP message type */
  option_len = 3 * sizeof(u_int8_t);
  memset(dhcpo_p + offset, DHCP_OPTION_MESSAGE_TYPE, sizeof(u_int8_t));
  memset(dhcpo_p + offset + 1, 1, sizeof(u_int8_t));
  memset(dhcpo_p + offset + 2, DHCP_MESSAGE_TYPE_REQUEST, sizeof(u_int8_t));
  *len_p += option_len;
  offset += option_len;

  /* Set DHCP server identifier */
  option_len = 2 * sizeof(u_int8_t) + sizeof(u_int32_t);
  memset(dhcpo_p + offset, DHCP_OPTION_SERVER_IDENTIFIER, sizeof(u_int8_t));
  memset(dhcpo_p + offset + 1, sizeof(u_int32_t), sizeof(u_int8_t));
  memcpy(dhcpo_p + offset + 2, &session_p->server_ip, sizeof(u_int32_t));
  *len_p += option_len;
  offset += option_len;

  /* Set requested IP */
  option_len = 2 * sizeof(u_int8_t) + sizeof(u_int32_t);
  memset(dhcpo_p + offset, DHCP_OPTION_REQUESTED_IP_ADDRESS, sizeof(u_int8_t));
  memset(dhcpo_p + offset + 1, sizeof(u_int32_t), sizeof(u_int8_t));
  memcpy(dhcpo_p + offset + 2, &session_p->client_ip, sizeof(u_int32_t));
  *len_p += option_len;
  offset += option_len;

  /* Set DHCP parameter request list */
  u_int8_t parameter_request_list_data[] = {
    DHCP_OPTION_SUBNET_MASK,
    DHCP_OPTION_ROUTER,
    DHCP_OPTION_BROADCAST_ADDRESS,
    DHCP_OPTION_DOMAIN_NAME,
    DHCP_OPTION_DOMAIN_NAME_SERVER
  };
  option_len = 2 * sizeof(u_int8_t) + sizeof(parameter_request_list_data);
  memset(dhcpo_p + offset, DHCP_OPTION_PARAMETER_REQUEST_LIST, sizeof(u_int8_t));
  memset(dhcpo_p + offset + 1, sizeof(parameter_request_list_data), sizeof(u_int8_t));
  memcpy(dhcpo_p + offset + 2, parameter_request_list_data, sizeof(parameter_request_list_data));
  *len_p += option_len;
  offset += option_len;

  /* Set DHCP option ending */
  option_len = 2 * sizeof(u_int8_t);
  memset(dhcpo_p + offset, DHCP_OPTION_END, sizeof(u_int8_t));
  memset(dhcpo_p + offset + 1, 0, sizeof(u_int8_t));
  *len_p += option_len;
  offset += option_len;
}

void prepare_dhcp_discover(dhcph_t *dhcph_p, int *len_p, session_t *session_p)
{
  prepare_dhcp_header(dhcph_p, len_p, session_p);
  prepare_dhcp_discover_options(dhcph_p + 1, len_p);
}

void prepare_dhcp_request(dhcph_t *dhcph_p, int *len_p, session_t *session_p)
{
  prepare_dhcp_header(dhcph_p, len_p, session_p);
  prepare_dhcp_request_options(dhcph_p + 1, len_p, session_p);
}

void send_dhcp_message(session_t *session_p,
                       void (*prepare_dhcp_payload)(dhcph_t *, int *, session_t *))
{

  u_int8_t buffer[4096];
  int buffer_len = 0;
  int send_result;

  /*
   * in all DHCP frames that we are going to send to a server
   * source/destination IPs and destination MAC are the same
   * we are not going to send RENEW or other messages that assume
   * having valid client IP or particular (not broadcast) server address
   */
  const u_int32_t src_ip = inet_addr("0.0.0.0");
  const u_int32_t dst_ip = inet_addr("255.255.255.255");

  const char *dst_mac = "ff:ff:ff:ff:ff:ff";

  u_int8_t *src_etha = session_p->etha;
  u_int8_t dst_etha[ETH_ALEN];
  mac2etha(dst_etha, dst_mac);

  eth_t *eth_p;
  ip_t *ip_p;
  udp_t *udp_p;
  void *dhcp_p;

  /* Initializing frame header pointers */
  eth_p = (eth_t *)buffer;
  ip_p = (ip_t *)(eth_p + 1);
  udp_p = (udp_t *)(ip_p + 1);
  dhcp_p = (void *)(udp_p + 1);

  /* LOG("Prepare dhcp payload"); */
  prepare_dhcp_payload(dhcp_p, &buffer_len, session_p);

  /* LOG("Wrap into udp"); */
  prepare_udp_header(udp_p, &buffer_len, DHCP_CLIENT_PORT, DHCP_SERVER_PORT);

  /* LOG("Wrap into ip"); */
  prepare_ip_header(ip_p, &buffer_len, src_ip, dst_ip);

  /* LOG("Wrap into ethernet"); */
  prepare_ether_header(eth_p, &buffer_len, src_etha, dst_etha);

  /* printf("Packet lenght: %d\n", buffer_len); */
  /* printf("Packet content: \n"); */
  /* print_packet(buffer, buffer_len); */

  /* Send data buffer to the interface */
  send_result = pcap_inject(pcap_handle, buffer, buffer_len);
  if (send_result == -1)
    pcap_perror(pcap_handle, "ERROR: ");
  else
    LOG("Buffer len: %d Bytes sent: %d", buffer_len, send_result);

}


void parse_dhcp_options(session_t *session_p, const u_int8_t *dhcpo_p)
{
  u_int8_t *cur_p = dhcpo_p;
  u_int8_t option = 0;
  u_int8_t option_len;

  while (option != (u_int8_t)DHCP_OPTION_END) {
    option = (u_int8_t)*cur_p;
    if (option == DHCP_OPTION_MESSAGE_TYPE)
      session_p->message_type = *(cur_p + 2);
    else if (option == DHCP_OPTION_SERVER_IDENTIFIER)
      session_p->server_ip = *(u_int32_t *)(cur_p + 2);
    else if (option == DHCP_OPTION_ROUTER)
      session_p->router = *(u_int32_t *)(cur_p + 2);
    else if (option == DHCP_OPTION_BROADCAST_ADDRESS)
      session_p->broadcast = *(u_int32_t *)(cur_p + 2);
    else if (option == DHCP_OPTION_SUBNET_MASK)
      session_p->mask = *(u_int32_t *)(cur_p + 2);
    else if (option == DHCP_OPTION_DOMAIN_NAME_SERVER)
      /* TODO There could be more than one dns */
      session_p->dns = *(u_int32_t *)(cur_p + 2);
    option_len = *(cur_p + 1);
    cur_p += 2 + option_len;
  }
}

void handle_dhcp_offer(session_t *session_p, const dhcph_t *dhcph_p)
{
  char ip[IP_STR_LEN];
  char mac[MAC_STR_LEN];

  LOG("Handling DHCP offer message");
  session_p->client_ip = dhcph_p->yiaddr;
  session_p->status = SESSION_OFFER_RECEIVED;

  ip2s(ip, session_p->client_ip);
  etha2mac(mac, session_p->etha);
  LOG("Offered IP: %s for MAC: %s", ip, mac);

  LOG("Sending DHCP request");
  send_dhcp_message(session_p, &prepare_dhcp_request);
  session_p->status = SESSION_REQUEST_SENT;
}

void print_sessions()
{
  session_t *cur = session_storage;

  char ip[IP_STR_LEN];
  char mac[MAC_STR_LEN];

  while (1){
    ip2s(ip, cur->client_ip);
    etha2mac(mac, cur->etha);
    printf("XID: 0x%x MAC: %s IP: %s\n", cur->xid, mac, ip);

    if (cur->next == NULL)
      break;
    cur = cur->next;
  }
}

void check_sessions_done()
{
  session_t *cur = session_storage;
  while (1){
    if (cur->status != SESSION_DONE){
      LOG("There are sessions that are not DONE");
      return;
    }
    if (cur->next == NULL)
      break;
    cur = cur->next;
  }
  LOG("All sessions are DONE. Closing pcap loop.");
  pcap_breakloop(pcap_handle);
  print_sessions();
}

void handle_dhcp_ack(session_t *session_p, const dhcph_t *dhcph_p)
{
  LOG("Handling DHCP ack message");
  session_p->status = SESSION_ACK_RECEIVED;
  /* TODO Do some handling here */
  session_p->status = SESSION_DONE;

  check_sessions_done();
}

void parse_dhcp_response(const dhcph_t *dhcph_p)
{
  LOG("DHCP payload with op code 0x%x 1-request 2-reply", dhcph_p->op);
  session_t *session_p;

  if (dhcph_p->op == DHCP_RESPONSE){
    /*
     * Trying to find DHCP session by xid
     * If there is no respective DHCP session,
     *  we just skip handling DHCP response
     */
    session_p = get_session(dhcph_p->xid);
    if (session_p == NULL){
      fprintf(stderr, "Couldn't get session with xid = 0x%x\n", dhcph_p->xid);
      return;
    }

    parse_dhcp_options(session_p, dhcph_p + 1);

    if (session_p->message_type == DHCP_MESSAGE_TYPE_OFFER)
      handle_dhcp_offer(session_p, dhcph_p);
    else if (session_p->message_type == DHCP_MESSAGE_TYPE_ACK)
      handle_dhcp_ack(session_p, dhcph_p);
  }
}

void parse_udp_header(const struct udphdr *udp_p)
{
  LOG("UDP frame uh_sport 0x%x", udp_p->uh_sport);
  if (ntohs(udp_p->uh_sport) == DHCP_SERVER_PORT){
    parse_dhcp_response(udp_p + 1);
  }
}

void parse_ip_header(const struct ip *ip_p)
{
  LOG("IP packet ip_p 0x%x", ip_p->ip_p);
  if (ip_p->ip_p == IPPROTO_UDP){
    parse_udp_header(ip_p + 1);
  }
}

void parse_ether_header(u_char *user, const struct pcap_pkthdr *header, const u_char *buffer)
{
  /*
   * TODO: Here we could use some advanced filtering on Ethernet level
   * For exmaple, we could filter out or count packages that have a particular
   * destination hardware address.
   * If we'd like to emulate DHCP requests from many different MAC addresses
   * then we need to be able to answer ARP requests. Otherwise we would need to
   * create hundreds of interfaces and plug them in to the bridge.
   * Need additional research.
   */
  /* print_packet(buffer, header->caplen); */

  eth_t *eth_p = (eth_t *)buffer;

  LOG("Ethernet frame ether_type 0x%x", eth_p->ether_type);
  if (ntohs(eth_p->ether_type) == ETHERTYPE_IP){
    parse_ip_header(eth_p + 1);
  }
}


const char *file_basename(const char *filename)
{
  const char *s;
  s = strrchr(filename, '/');
  if (s == NULL)
    return (filename);
  return (s + 1);
}

static void usage(const char *progname)
{
  printf("%s %s\n", progname, VERSION);
  printf("Usage: %s\n", progname);
  exit(1);
}

int main(int argc, char** argv)
{
  char *progname = NULL;
  progname = file_basename(argv[0]);
  const char *dev = "dhclient";

  /* Open interface to send and receive data frames  */
  char errbuf[PCAP_ERRBUF_SIZE];
  pcap_handle = pcap_open_live(dev, BUFSIZ, 0, 10, errbuf);
  if (pcap_handle == NULL) {
    fprintf(stderr, "Couldn't open device %s: %s\n", dev, errbuf);
    return 1;
  }

  char *src_macs[10];
  src_macs[0] = "8a:1a:3d:01:59:70";
  src_macs[1] = "8a:1a:3d:01:59:71";
  src_macs[2] = "8a:1a:3d:01:59:72";
  src_macs[3] = "8a:1a:3d:01:59:73";
  src_macs[4] = "8a:1a:3d:01:59:74";
  src_macs[5] = "8a:1a:3d:01:59:75";
  src_macs[6] = "8a:1a:3d:01:59:76";
  src_macs[7] = "8a:1a:3d:01:59:77";
  src_macs[8] = "8a:1a:3d:01:59:78";
  src_macs[9] = "8a:1a:3d:01:59:79";

  session_t *session_p;
  for (int i = 0; i < 10; i++){
    /* Prepare dhcp session */
    session_p = (session_t *)malloc(sizeof(session_t));
    memset(session_p, 0, sizeof(session_t));
    session_p->xid = random();
    session_p->status = SESSION_INIT;
    mac2etha(session_p->etha, src_macs[i]);

    put_session(session_p);

    send_dhcp_message(session_p, &prepare_dhcp_discover);
    session_p->status = SESSION_DISCOVER_SENT;
  }

  pcap_loop(pcap_handle, 0, parse_ether_header, NULL);
  pcap_close(pcap_handle);

  return 0;
}
