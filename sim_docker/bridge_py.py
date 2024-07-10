from scapy.all import Ether, Dot1Q, sendp, sniff, IP
import logging

interface_prefix = 't7-'
interface_number = 2
log = logging.getLogger('bridge_log ')
logging.basicConfig(filename='bridge.log', encoding='utf-8', level=logging.DEBUG)
test_interface_list = []
tpid = 0x8100


type_dict = {
0x0800: 'Internet Protocol version 4 (IPv4)',
0x0806: 'Address Resolution Protocol (ARP)',
0x0842: 'Wake-on-LAN[8]',
0x2000: 'Cisco Discovery Protocol[9]',
0x22EA: 'Stream Reservation Protocol',
0x22F0: 'Audio Video Transport Protocol (AVTP)',
0x22F3: 'IETF TRILL Protocol',
0x6002: 'DEC MOP RC',
0x6003: 'DECnet Phase IV, DNA Routing',
0x6004: 'DEC LAT',
0x8035: 'Reverse Address Resolution Protocol (RARP)',
0x809B: 'AppleTalk (EtherTalk)',
0x80F3: 'AppleTalk Address Resolution Protocol (AARP)',
0x8100: 'VLAN-tagged frame (IEEE 802.1Q) and Shortest Path Bridging IEEE 802.1aq with NNI compatibility[10]',
0x8102: 'Simple Loop Prevention Protocol (SLPP)',
0x8103: 'Virtual Link Aggregation Control Protocol (VLACP)',
0x8137: 'IPX',
0x8204: 'QNX Qnet',
0x86DD: 'Internet Protocol Version 6 (IPv6)',
0x8808: 'Ethernet flow control',
0x8809: 'Ethernet Slow Protocols[11] such as the Link Aggregation Control Protocol (LACP)',
0x8819: 'CobraNet',
0x8847: 'MPLS unicast',
0x8848: 'MPLS multicast',
0x8863: 'PPPoE Discovery Stage',
0x8864: 'PPPoE Session Stage',
0x887B: 'HomePlug 1.0 MME',
0x888E: 'EAP over LAN (IEEE 802.1X)',
0x8892: 'PROFINET Protocol',
0x889A: 'HyperSCSI (SCSI over Ethernet)',
0x88A2: 'ATA over Ethernet',
0x88A4: 'EtherCAT Protocol',
0x88A8: 'Service VLAN tag identifier (S-Tag) on Q-in-Q tunnel',
0x88AB: 'Ethernet Powerlink[citation needed]',
0x88B8: 'GOOSE (Generic Object Oriented Substation event)',
0x88B9: 'GSE (Generic Substation Events) Management Services',
0x88BA: 'SV (Sampled Value Transmission)',
0x88BF: 'MikroTik RoMON (unofficial)',
0x88CC: 'Link Layer Discovery Protocol (LLDP)',
0x88CD: 'SERCOS III',
0x88E1: 'HomePlug Green PHY',
0x88E3: 'Media Redundancy Protocol (IEC62439-2)',
0x88E5: 'IEEE 802.1AE MAC security (MACsec)',
0x88E7: 'Provider Backbone Bridges (PBB) (IEEE 802.1ah)',
0x88F7: 'Precision Time Protocol (PTP) over IEEE 802.3 Ethernet',
0x88F8: 'NC-SI',
0x88FB: 'Parallel Redundancy Protocol (PRP)',
0x8902: 'IEEE 802.1ag Connectivity Fault Management (CFM) Protocol / ITU-T Recommendation Y.1731 (OAM)',
0x8906: 'Fibre Channel over Ethernet (FCoE)',
0x8914: 'FCoE Initialization Protocol',
0x8915: 'RDMA over Converged Ethernet (RoCE)',
0x891D: 'TTEthernet Protocol Control Frame (TTE)',
0x893a: '1905.1 IEEE Protocol',
0x892F: 'High-availability Seamless Redundancy (HSR)',
0x9000: 'Ethernet Configuration Testing Protocol[12]',
0xF1C1: 'Redundancy Tag (IEEE 802.1CB Frame Replication and Elimination for Reliability)',
}

def process_packet(pkt):
    iface = pkt.sniffed_on
    log.info(f"pkt type: {type_dict.get(int(pkt[Ether].type))}")
    if iface == test_interface_list[0]:
        sendp(pkt, iface=test_interface_list[1])
        log.info(f"Packet from {test_interface_list[0]} forwarded to {test_interface_list[1]} \n")
    elif iface == test_interface_list[1]:
        sendp(pkt, iface=test_interface_list[0])
        log.info(f"Packet from {test_interface_list[1]} forwarded to {test_interface_list[0]}  \n")
    elif iface == test_interface_list[2]:
        sendp(pkt, iface=test_interface_list[3])
        log.info(f"Packet from {test_interface_list[2]} forwarded to {test_interface_list[3]}  \n")
    elif iface == test_interface_list[3]:
        sendp(pkt, iface=test_interface_list[2])
        log.info(f"Packet from {test_interface_list[3]} forwarded to {test_interface_list[2]}  \n")




def get_interface_list():
    global test_interface_list
    # the function is based on DockerManager naming for the veth interfaces
    all_interfaces = [f'{interface_prefix}101-{i+1}' for i in range(interface_number)]   #netifaces.interfaces()
    test_interface_list = [iface for iface in all_interfaces if iface.startswith(interface_prefix)]
    test_interface_list.sort()


if __name__ == '__main__':
    # Sniff packets on interface_3 and interface_4
    test_interface_list=["t7-1", "ens19", "t7-2", "ens20"]
    sniff(iface=test_interface_list, filter="inbound", prn=process_packet)
