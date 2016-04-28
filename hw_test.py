import argparse, socket
from datetime import datetime

MAX_BYTES = 65535

def server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 67))
    print('Listening at {}'.format(sock.getsockname()))
    while True:
        data, address = sock.recvfrom(MAX_BYTES)
        if len(data) > 0 :
            offer_text = offer(data)
            sock.sendto(offer_text, ('127.0.0.1', 8888))
            print('offer done !')
            break
    while True :
        data, address = sock.recvfrom(MAX_BYTES)
        if len(data) > 0 :
            print('accept request')
            break
    ack_data = ack(data)
    sock.sendto(ack_data, ('127.0.0.1', 8888))

def client(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 8888))
    #text = 'The time is {}'.format(datetime.now())
    #data = text.encode('ascii')
    discover_text = discover()
    sock.sendto(discover_text, ('127.0.0.1', 67))
    print('discovery packet send !')
    while True:
        data, address = sock.recvfrom(MAX_BYTES)
        if len(data) > 0 :
            print('accept offer !')
            break
    request_data = request(data)
    sock.sendto(request_data, ('127.0.0.1', 67))


#DHCPDiscover

def discover():
    #macb = getMacInBytes()
    macb = b'\x00\x0c\x29\x7b\xa1\x6c'
    packet = b''
    packet += b'\x01'   #Message type: Boot Request (1)
    packet += b'\x01'   #Hardware type: Ethernet
    packet += b'\x06'   #Hardware address length: 6
    packet += b'\x00'   #Hops: 0 
    #packet += self.transactionID       #Transaction ID
    packet += b'\x39\x03\xF3\x26'
    packet += b'\x00\x00'    #Seconds elapsed: 0
    packet += b'\x80\x00'   #Bootp flags: 0x8000 (Broadcast) + reserved flags
    packet += b'\x00\x00\x00\x00'   #Client IP address: 0.0.0.0
    packet += b'\x00\x00\x00\x00'   #Your (client) IP address: 0.0.0.0
    packet += b'\x00\x00\x00\x00'   #Next server IP address: 0.0.0.0
    packet += b'\x00\x00\x00\x00'   #Relay agent IP address: 0.0.0.0
    #packet += b'\x00\x26\x9e\x04\x1e\x9b'   #Client MAC address: 00:26:9e:04:1e:9b
    packet += macb
    packet += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'   #Client hardware address padding: 00000000000000000000
    packet += b'\x00' * 67  #Server host name not given
    packet += b'\x00' * 125 #Boot file name not given
    packet += b'\x63\x82\x53\x63'   #Magic cookie: DHCP
    packet += b'\x35\x01\x01'   #Option: (t=53,l=1) DHCP Message Type = DHCP Discover
    #packet += b'\x3d\x06\x00\x26\x9e\x04\x1e\x9b'   #Option: (t=61,l=6) Client identifier
    packet += b'\x3d\x06' + macb
    packet += b'\x37\x03\x03\x01\x06'   #Option: (t=55,l=3) Parameter Request List
    packet += b'\xff'   #End Option
    return packet

def offer(data):
    c_mac = b''
    c_mac += data[28:34]
    packet = b''
    packet += b'\x02' 
    packet += b'\x01'
    packet += b'\x06'  
    packet += b'\x00' 
    packet += b'\x39\x03\xF3\x26'
    packet += b'\x00\x00'  
    packet += b'\x00\x00'   
    packet += b'\x00\x00\x00\x00'  
    packet += b'\xC0\xA8\x01\x64'   
    packet += b'\xC0\xA8\x01\x01'   
    packet += b'\x00\x00\x00\x00'  
    #packet += b'\x00\x26\x9e\x04\x1e\x9b'   #Client MAC address: 00:26:9e:04:1e:9b
    packet += c_mac
    packet += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'   
    packet += b'\x00' * 67  
    packet += b'\x00' * 125 
    packet += b'\x63\x82\x53\x63'   
    packet += b'\x35\x01\x02'   
    #packet += b'\x3d\x06\x00\x26\x9e\x04\x1e\x9b'   
    #packet += b'\x3d\x06' + c_mac
    #packet += b'\x35\x01\x02'   
    packet += b'\xff'   #
    return packet

def request(data):
    c_mac = b''
    c_mac += data[28:34]
    packet = b''
    packet += b'\x01' 
    packet += b'\x01'
    packet += b'\x06'  
    packet += b'\x00' 
    packet += b'\x39\x03\xF3\x27'
    packet += b'\x00\x00'  
    packet += b'\x00\x00'   
    packet += b'\x00\x00\x00\x00'  
    packet += b'\x00\x00\x00\x00'   
    packet += b'\xC0\xA8\x01\x01'   
    packet += b'\x00\x00\x00\x00'  
    #packet += b'\x00\x26\x9e\x04\x1e\x9b'   #Client MAC address: 00:26:9e:04:1e:9b
    packet += c_mac
    packet += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'   
    packet += b'\x00' * 67  
    packet += b'\x00' * 125 
    packet += b'\x63\x82\x53\x63'   
    packet += b'\x35\x01\x03'   
    #packet += b'\x3d\x06\x00\x26\x9e\x04\x1e\x9b'   
    #packet += b'\x3d\x06' + c_mac
    #packet += b'\x35\x01\x03'   
    packet += b'\xff'   #
    return packet

def ack(data):
    c_mac = b''
    c_mac += data[28:34]
    packet = b''
    packet += b'\x02' 
    packet += b'\x01'
    packet += b'\x06'  
    packet += b'\x00' 
    packet += b'\x39\x03\xF3\x27'
    packet += b'\x00\x00'  
    packet += b'\x00\x00'   
    packet += b'\x00\x00\x00\x00'  
    packet += b'\xC0\xA8\x01\x64'   
    packet += b'\xC0\xA8\x01\x01'   
    packet += b'\x00\x00\x00\x00'  
    #packet += b'\x00\x26\x9e\x04\x1e\x9b'   #Client MAC address: 00:26:9e:04:1e:9b
    packet += c_mac
    packet += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'   
    packet += b'\x00' * 67  
    packet += b'\x00' * 125 
    packet += b'\x63\x82\x53\x63'   
    packet += b'\x35\x01\x05'   
    #packet += b'\x3d\x06\x00\x26\x9e\x04\x1e\x9b'   
    #packet += b'\x3d\x06' + c_mac
    #packet += b'\x35\x01\x04'   
    packet += b'\xff'   #
    return packet

if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Send and receive UDP locally')
    parser.add_argument('role', choices=choices, help='which role to play')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='UDP port (default 1060)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.p)
