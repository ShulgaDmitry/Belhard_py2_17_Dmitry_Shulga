import socket
import json

HOST = ('127.0.0.1', 7771)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(HOST)

response = {'command': input('Input "reg" or "signin" or "stop": '), 'login': input('Login: '), 'password': input('Password: ')}
response_json = json.dumps(response)
sock.sendall(response_json.encode())
data = sock.recv(1024).decode()
print(data)


sock.close()