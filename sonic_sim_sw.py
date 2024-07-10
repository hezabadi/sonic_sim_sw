import copy

from scapy.all import Ether, Dot1Q, sendp, sniff, IP
import time, random
import netifaces
import logging

# TODO: Homayoon get this parameter from docker manager
interface_prefix = 'evth_'      #based on what we have in docker manager
interface_number = 12           # based on what we have in doecker mamager
log = logging.getLogger('sonic sim ')
test_interface_list = []

def process_packet(pkt):
    if Dot1Q in pkt:
        vlan_id = int(pkt[Dot1Q].vlan)
        if 1000<vlan_id <1020:    # from pensando cards
            sublayer = pkt[Dot1Q].payload
            subtype = pkt[Dot1Q].type
            del pkt[Dot1Q]
            pkt.type = subtype
            pkt /= sublayer
            sendp(pkt, iface=test_interface_list[vlan_id - 1001])
        else:
            # TODO homayoon: this pkt should be q in q with proper tpid and send to pensando
            pass
        log.info(f"Packet with VLAN {vlan_id} forwarded to {test_interface_list[vlan_id - 1001]}")

    else:
        iface = pkt.sniffed_on
        vlan_id = 1001 + test_interface_list.index(iface)
        pkt_vlan = copy.deepcopy(pkt)
        pkt_vlan[Ether].remove_payload()
        pkt_vlan = pkt_vlan[Ether] / Dot1Q(vlan=vlan_id) / pkt[Ether].payload
        pensando_iface = random.choice([test_interface_list[-4:]])
        sendp(pkt, iface=pensando_iface)
        log.info(f"Packet from {iface} forwarded to pensando {pensando_iface} vlan {vlan_id}")


def get_interface_list():
    global test_interface_list
    # the function is based on DockerManager naming for the veth interfaces
    all_interfaces = netifaces.interfaces()
    test_interface_list = [iface for iface in all_interfaces if iface.startswith(interface_prefix)]
    test_interface_list.sort()


if __name__ == '__main__':
    # Sniff packets on interface_3 and interface_4
    while len(test_interface_list) < interface_number:
        get_interface_list()
        time.sleep(5)
    sniff(iface=test_interface_list, filter="inbound", prn=process_packet)
