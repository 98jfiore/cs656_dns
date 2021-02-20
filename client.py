from socket import *

serverName = 'localhost'
serverPort = 53

clientSocket = socket(AF_INET, AF_INET)

#message = input("Input lowercase sentence: ")
query = input("Enter name of website: ")

clientSocket.sendto(query.encode(), (serverName, serverPort))

response, serverAddress = clientSocket.recvfrom(2048)

print(response.decode())

clientSocket.close()
