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
    recursion = False
    #print(message)
    #print(queryencode2)

    found = False

    #Get identification number
    response_ident = int.from_bytes(message[0:2], "big")

    request_flags = int.from_bytes(message[2:4], "big")
    #Cheack request flags
    #Rcode should be 0, if not drop
    if request_flags & 15 > 0:
        continue
    request_flags = request_flags >> 4
    #Move over zero field
    request_flags = request_flags >> 3
    #Next bit is recusion available, this is hopefully a request so ignore
    request_flags = request_flags >> 1
    #Next bit is recusion desired
    if request_flags & 1 > 0:
        recursion = True
    request_flags = request_flags >> 1
    #Next bit is truncated, this is for udp, ignore it
    request_flags = request_flags >> 1
    #Next bit is authoritative answer, this is hopefully a request so ignore
    request_flags = request_flags >> 1
    #We're only set up to handle opcode 0
    if request_flags & 15 > 0:
        continue
    request_flags = request_flags >> 4
    #Next bit is QR, it should be 0, for query
    if request_flags & 1 > 0:
        continue
    request_flags = request_flags >> 1

    #Set up the 16 bits of response_flags
    #If response make first bit 1, request make it 0
    response_flags = 1
    #Opcode is next 4 bits, we are doing a standard query so it is 0
    response_flags = response_flags << 4
    #Next bit is 1 if this is an authoritative name server, which it is
    response_flags = response_flags << 1
    response_flags += 1
    #Next bit is to indicate if the reply is truncated, this is not
    response_flags = response_flags << 1
    #Next bit is if you want recursion from the server, this is a response
    response_flags = response_flags << 1
    #Next bit is if the response has recursion available, this is not yet implemented
    response_flags = response_flags << 1
    #Next 3 nbits must be zero
    response_flags = response_flags << 3
    #Next 4 bits are for the return code, set to zero, but set to 3 if the name isn't found
    response_flags = response_flags << 4

    #Figure out how many questions there are
    num_questions = int.from_bytes(message[4:6], "big")


    num_answers = 0
    answers = b''

    queries = message[12:]
    for i in range(num_questions):
        #Get the query name you are looking for
        query_name = ""
        point_in_query = 1
        qname_next_sect_bytes = int.from_bytes(queries[0:1], "big")
        while(qname_next_sect_bytes != 0):
            #print(query_name)
            query_next_sect = queries[point_in_query : point_in_query + qname_next_sect_bytes].decode('utf-8')
            query_name += query_next_sect
            query_name += '.'
            point_in_query += qname_next_sect_bytes + 1
            qname_next_sect_bytes = int.from_bytes(queries[point_in_query - 1:point_in_query], "big")
        query_name = query_name[0:-1]
        
        queryencoded = queries[0:point_in_query]
        queries = queries[point_in_query:]

        query_type = int.from_bytes(queries[0:2], 'big')
        query_class = int.from_bytes(queries[2:4], 'big')
        queries = queries[4:]
        
        #We only have A records, so the if type's not 1, we won't check.
        #We also only return IP addresses so if class isn't 1, we won't check
        if(query_type == 1 and query_class == 1):
            found = False
            for record in readtext:
                if query_name in record:
                    answer = (record.split("\n")[0])
                    ttl = int(answer.split(" ")[1]) #59
                    clas = answer.split(" ")[2] #IN
                    query_type = answer.split(" ")[3] #A

                    answer_bytes = queryencoded
                    resource_bytes = b''

                    resource_type = 0
                    resource_class = 0
                    resource_length = 0

                    if(query_type == 'A'):
                        resource_type = 1
                        resource_length = 4
                        data = answer.split(" ")[4] #208.56.54.454
                        a = int(data.split(".")[0])
                        b = int(data.split(".")[1])
                        c = int(data.split(".")[2])
                        d = int(data.split(".")[3])
                        resource_bytes = a.to_bytes(1, 'big')
                        resource_bytes += b.to_bytes(1, 'big')
                        resource_bytes += c.to_bytes(1, 'big')
                        resource_bytes += d.to_bytes(1, 'big')
                    else:
                        #We are only working with A types now
                        continue

                    answer_bytes += resource_type.to_bytes(2, 'big')

                    if(clas == 'IN'):
                        resource_class = 1
                    else:
                        #We are only working with IN class answers now
                        continue

                    answer_bytes += resource_class.to_bytes(2, 'big')

                    answer_bytes += ttl.to_bytes(4, 'big')

                    answer_bytes += resource_length.to_bytes(2, 'big')

                    answer_bytes += resource_bytes

                    answers += answer_bytes
                    num_answers += 1

                    found = True
                    break
            if not found:
                response_flags = response_flags | 3


    response_first_header = response_ident
    response_first_header = response_first_header << 16
    response_first_header += response_flags
    rfh_bytes = response_first_header.to_bytes(4, 'big')

    response_sec_header = 0
    response_sec_header = response_sec_header << 16
    response_sec_header += num_answers
    rsh_bytes = response_sec_header.to_bytes(4, 'big')

    #There should be no RRs.
    response_third_header = 0
    rth_bytes = response_third_header.to_bytes(4, 'big')

    response_bytes = rfh_bytes + rsh_bytes + rth_bytes + answers

    serverSocket.sendto(response_bytes, clientAddress)
    

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
