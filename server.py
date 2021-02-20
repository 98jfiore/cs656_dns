from socket import *

serverName = 'localhost'
serverPort = 53
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("The server is ready to receive")

while True:
    query, clientAddress = serverSocket.recvfrom(2048)
    response = query.decode().upper()
    serverSocket.sendto(response.encode(), clientAddress)
