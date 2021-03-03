from socket import *
import struct
serverName = 'localhost'
serverPort = 53
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("The server is ready to receive")


while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    query = 'api.njit.com'
    txtfile = open("dns.txt", "r")
    readtext = txtfile.readlines()
    for record in readtext:
        if query in record:
            answer = (record.split("\n")[0])
            #print(answer)
            send = answer.encode()
            serverSocket.sendto(send, clientAddress)

#DNS ANSWER PACKET FORMAT - PENDING
#NAME The domain name that was queried, in the same format as the QNAME in the questions.
#TYPE Two octets containing one of th type codes. This field specifies the meaning of the data in
#the RDATA field. You should be prepared to interpret type 0x0001 (A record) and type 0x0005
#(CNAME). If you are completing the graduate version of this project, you should also be prepared to
#accept type 0x0002 (name servers) and 0x000f (mail servers).
#CLASS Two octets which specify the class of the data in the RDATA field. You should expect 0x0001 for this project, representing Internet addresses.
#TTL The number of seconds the results can be cached.
#RDLENGTH The length of the RDATA field.
