from socket import *
import numpy as np

serverName = 'localhost'
serverPort = 53

clientSocket = socket(AF_INET, AF_INET)

#Find the name of the website to request the IP address of
query = input("Enter name of website: ")

#Set up first header (32 bits)
first_header = 0

#Get a number to identify the request
ident = np.random.randint(0, 65535)

#Put the identifier in the header
first_header = ident

#Set up the 16 bits of flags
flags = 0

#If response make first bit 1, request make it 0
flags = flags << 1
#Opcode is next 4 bits, we are doing a standard query so it is 0
flags = flags << 4
#Next bit is 1 if you are looking for an authoritative answer, we are not right now
flags = flags << 1
#Next bit is to indicate if the reply is truncated, this is not a reply
flags = flags << 1
#Next bit is if you want recursion from the server, we do so we'll set this to one
flags = flags << 1
flags += 1
#Next bit is if the response has recursion available, this is not a response
flags = flags << 1
#Next 3 nbits must be zero
flags = flags << 3
#Next 4 bits are for the return code, which is for the reply
flags = flags << 4

#Put the flags in the header
first_header = first_header << 16
first_header += flags


#Set up second header (32 bits)
second_header = 0

#First 16 bits is the number of questions
num_questions = 1
second_header = num_questions

#Next 16 bits is the number of answers, this is a query so it's zero
second_header = second_header << 16


#Set up third header (32 bits)
third_header = 0

#Third header is about resource record counts, which as a query this does not have

#Convert header to bytes
fh_bytes = first_header.to_bytes(4, "big")
sh_bytes = second_header.to_bytes(4, "big")
th_bytes = third_header.to_bytes(4, "big")

#Header is 12 bytes
header_bytes = fh_bytes + sh_bytes + th_bytes

#Convert query into a queryname
zero = 0
query_name_bytes = zero.to_bytes(1, "big")

non_dot_count = 0
this_part = ''
for i in range(len(query)-1, -1, -1):
    this_char = query[i]
    if (this_char == '.'):
        query_name_bytes = non_dot_count.to_bytes(1, "big") + this_part.encode('utf-8') + query_name_bytes
        this_part = ''
        non_dot_count = 0
    else:
        this_part = this_char + this_part
        non_dot_count += 1
query_name_bytes = non_dot_count.to_bytes(1, "big") + this_part.encode('utf-8') + query_name_bytes


#Set up query type
#Type A has a value of 1
query_type = 1

#Set up query class
#The internet address type is 1
query_class = 1

#Make query type and class a 32 bit footer
footer = query_type
footer = footer << 16
footer += query_class

#print(footer)
footer_bytes = footer.to_bytes(4, 'big')
#print(footer_bytes)

#print(int.from_bytes(footer_bytes, "big"))

message = header_bytes + query_name_bytes + footer_bytes
#message = query.encode("utf-8") #hemali - test
#'prior message encoded \xae\xd9\x01\x00\x00\x00\x00\x01\x00\x00\x00\x003api4njit3edu0\x00\x01\x00\x01
# print(message)
# print(message[:12])
# print(message[12:-4])
# print(message[-4:])

clientSocket.sendto(message, (serverName, serverPort))

received = False
while(not received):
    print("Receiving")
    response, serverAddress = clientSocket.recvfrom(2048)

    response_ident = int.from_bytes(response[0:2], "big")
    if(response_ident != ident):
        continue

    response_flags = int.from_bytes(response[2:4], "big")
    #Rcode should be 1, if not drop
    if response_flags & 15 != 0:
        if response_flags & 15 == 3:
            print("Name Error")
            break
        else:
            print(response_flags & 15)
        continue
    response_flags = response_flags >> 4
    #Move over zero field
    response_flags = response_flags >> 3
    #Next bit is recusion available, ignore
    response_flags = response_flags >> 1
    #Next bit is recusion desired, ignore
    response_flags = response_flags >> 1
    #Next bit is truncated, this is for udp, ignore it
    response_flags = response_flags >> 1
    #Next bit is authoritative answer, 
    if response_flags & 1 == 1:
        print("Authoritative Answer")
    response_flags = response_flags >> 1
    #We're only set up to handle opcode 0
    if response_flags & 15 > 0:
        print("Received a non-zero opcode")
        continue
    response_flags = response_flags >> 4
    #Next bit is QR, it should be 0, for query
    if response_flags & 1 != 1:
        print("Not a response")
        continue
    response_flags = response_flags >> 1

    num_recv_qustions = int.from_bytes(response[4:6], "big")
    num_answers = int.from_bytes(response[6:8], "big")
    num_authority_rrs = int.from_bytes(response[8:10], "big")
    num_additional_rrs = int.from_bytes(response[10:12], "big")

    response = response[12:]

    if(num_recv_qustions != 0):
        print("Received questions")
        continue

    for i in range(num_answers):
        #Get the query name you are looking for
        r_domain_name = ""
        point_in_dom = 1
        dname_next_sect_bytes = int.from_bytes(response[0:1], "big")
        while(dname_next_sect_bytes != 0):
            dom_next_sect = response[point_in_dom : point_in_dom + dname_next_sect_bytes].decode('utf-8')
            r_domain_name += dom_next_sect
            r_domain_name += '.'
            point_in_dom += dname_next_sect_bytes + 1
            dname_next_sect_bytes = int.from_bytes(response[point_in_dom - 1:point_in_dom], "big")
        r_domain_name = r_domain_name[0:-1]
        
        response = response[point_in_dom:]

        ans_type = int.from_bytes(response[0:2], 'big')
        ans_class = int.from_bytes(response[2:4], 'big')
        response = response[4:]

        r_ttl = int.from_bytes(response[0:4], "big")
        response = response[4:]

        data_len = int.from_bytes(response[0:2], "big")
        response = response[2:]

        if(ans_type == 1 and data_len == 4):
            a = int.from_bytes(response[0:1], "big")
            b = int.from_bytes(response[1:2], "big")
            c = int.from_bytes(response[2:3], "big")
            d = int.from_bytes(response[3:4], "big")
            print(r_domain_name + ": " + str(a) + "." + str(b) + "." + str(c) + "." + str(d) + " ttl " + str(r_ttl))
            received = True

#print(response)

clientSocket.close()
