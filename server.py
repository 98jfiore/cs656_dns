from socket import *
import struct
import re
from os.path import dirname, join
current_dir = dirname(__file__)


txtfile = open(join(current_dir, "dns.txt"), "r")
readtext = txtfile.readlines()

serverName = 'localhost'
serverPort = 53
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("The server is ready to receive")

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    #print(message)
    queryencode = (message[12:-4])
    queryencode2 = (message[11:-4])
    strqueryencode = str(message[12:-4])
    pattern = r'[0-9]'
    querydecode = re.sub(pattern, '.', strqueryencode)
    querystrip = querydecode.split("'.")[1]
    query = querystrip.split(".'")[0]
    #print(queryencode2)

    found = False

    for record in readtext:
        if query in record:
            answer = (record.split("\n")[0])
            ttl = int(answer.split(" ")[1]) #59
            clas = answer.split(" ")[2] #IN
            type = answer.split(" ")[3] #A
            data = answer.split(" ")[4] #208.56.54.454
            a = int(data.split(".")[0])
            b = int(data.split(".")[1])
            c = int(data.split(".")[2])
            d = int(data.split(".")[3])
            qlenght = len(data) #10

            #print(clas)
            #print(ttl)
            #print(a,b,c,d)

            clasencode= clas.encode()
            typeencode= type.encode()
            dataencode = data.encode()

            class_typepack = struct.pack("!ss", typeencode, clasencode)
            #print(class_typepack)

            querypack = struct.pack("!{}s".format(len(queryencode2)), queryencode2)
            #print(querypack)

            ttlpack = struct.pack("!i", ttl)
            #print(ttlpack)

            lenpack = struct.pack("!i", qlenght)
            #print(lenpack)

            datapack = struct.pack("!iiii", a, b, c, d)
            #print(datapack)

            pack_all = querypack + class_typepack  + ttlpack + lenpack + datapack
            #print(pack_all)

            serverSocket.sendto(pack_all, clientAddress)

            found = True
            break
    if not found:
        answer = query
        serverSocket.sendto(answer.encode(), clientAddress)

#NAME
#TYPE
#CLASS
#TTL
#RDLENGTH
#RDATA


#DNS ANSWER PACKET FORMAT - PENDING
#NAME The domain name that was queried, in the same format as the QNAME in the questions.
#TYPE Two octets containing one of th type codes. This field specifies the meaning of the data in
#the RDATA field. You should be prepared to interpret type 0x0001 (A record) and type 0x0005
#(CNAME). If you are completing the graduate version of this project, you should also be prepared to
#accept type 0x0002 (name servers) and 0x000f (mail servers).
#CLASS Two octets which specify the class of the data in the RDATA field. You should expect 0x0001 for this project, representing Internet addresses.
#TTL The number of seconds the results can be cached.
#RDLENGTH The length of the RDATA field.
