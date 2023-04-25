from socket import *
import os
import sys
import struct
import time

import requests
import select
import binascii

import geoip2.database

f=open("traceroute.txt","w", encoding="utf-8")

def lookup_ip(ip_address):
    # Set up the API endpoint URL with the IP address parameter
    endpoint_url = f"https://ipinfo.io/{ip_address}/json"
    # Make a GET request to the endpoint
    response = requests.get(endpoint_url)
    # Check if the response was successful
    if response.status_code == 200:
        # Parse the response JSON data
        data = response.json()
        # Extract the city, region, and country properties
        city = data.get("city")
        region = data.get("region")
        country = data.get("country")
        # Return the location information as a tuple
        return city, region, country
    else:
        return None

# default valuse set from start
ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1

from socket import *
import os
import struct
import time

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1

cities=[]

def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def build_packet():
    myID = os.getpid() & 0xFFFF
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, myID, 1)
    data = struct.pack("d", time.time())
    myChecksum = checksum(header + data)

    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)

    packet = header + data
    return packet


def get_route(hostname):
    destAddr = gethostbyname(hostname)
    tracelist = []


    for ttl in range(1, MAX_HOPS):
        mySocket = socket(AF_INET, SOCK_RAW, getprotobyname("icmp"))
        mySocket.bind(("", 0))
        mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
        mySocket.settimeout(TIMEOUT)

        try:
            d = build_packet()
            mySocket.sendto(d, (hostname, 0))
            t = time.time()

            whatReady = select.select([mySocket], [], [], TIMEOUT)
            if whatReady[0] == []:
                tracelist.append(f"{ttl} * * * Request timed out.")
            else:
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                tracelist.append(f"{ttl} {addr[0]} {round((timeReceived - t) * 1000)}ms")
                city = lookup_ip(addr[0])[0]
                if city is not None:
                    cities.append(city)
                else:
                    cities.append("Unknown")

                if addr[0] == destAddr:
                    break

        except timeout:
            tracelist.append(f"{ttl} * * * Request timed out.")

        finally:
            mySocket.close()

    return tracelist


if __name__ == '__main__':
    trace_list = get_route("japantimes.co.jp")
    for trace in trace_list:
        print(trace)

    # print(cities)

    for i in range(len(cities)):
        f.write(str(cities[i]) + "\n")

