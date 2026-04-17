from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3

class PacketDropController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority,
            match=match, instructions=inst)

        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser

        # NORMAL forwarding
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(
            datapath.ofproto.OFPP_FLOOD)]
        self.add_flow(datapath, 0, match, actions)

        # DROP rule (Example: Drop ICMP packets)
        match = parser.OFPMatch(eth_type=0x0800, ip_proto=1)
        actions = []  # No action = DROP
        self.add_flow(datapath, 10, match, actions)