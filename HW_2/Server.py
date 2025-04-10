import socket
import json
from datetime import datetime


def current_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def send_file(file_name, conn):
    try:
        with open(file_name.lstrip('/'), 'rb') as f:
            if file_name.endswith('.html'):
                conn.send(OK)
                conn.send(b'Content-Type: text/html\r\n\r\n')
            elif file_name.endswith(('.jpg', '.jpeg')):
                conn.send(OK)
                conn.send(b'Content-Type: image/jpeg\r\n\r\n')
            conn.sendfile(f)
    except IOError:
        print('Not found')
        conn.send(ERR_404)


def is_file(path):
    if path[-4:] in ['.jpg','.png','.gif', '.ico', '.txt']:
        return True
    return False


HOST = ('127.0.0.1', 7771)


OK = b'HTTP/1.1 200 OK\n'
ERR_404 = b'HTTP/1.1 404 Not Found\n\n'

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(HOST)
    sock.listen()
    print("----start-----")

    while True:
        print("---listen----")
        conn, addr = sock.accept()
        print(f"Connected by {addr}")

        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            if "HTTP/1.1" in data:
                method, path, ver = data.split('\n')[0].split(" ", 2)
                print('-----', method, path, ver)
                if path == '/':
                    send_file('1.html', conn)
                elif path.startswith('/test/'):
                    test_number = path.split('/')[2]
                    conn.sendall(f"HTTP/1.1 200 OK\r\n\r\nTest with number {test_number} started".encode())
                elif path.startswith('/message/'):
                    login = path.split('/')[2]
                    text = path.split('/')[3]
                    conn.send(f"HTTP/1.1 200 OK\r\n\r\n{current_time()} - text from user {login} - {text}".encode())
                elif is_file(path):
                    file = path.lstrip('/')
                    send_file('cat.jpg', conn)
                else:
                    conn.send(f"HTTP/1.1 400 Bad Request\r\n\r\nUnknown data from HTTP - path {path}".encode())
            else:
                response = json.loads(data)
                with open('users.json', 'r', encoding='utf-8') as json_file:
                    try:
                        new_data = json.load(json_file)
                    except json.JSONDecodeError:
                        new_data = []

                if response['command'] == 'reg':
                    if (len(response['login']) >= 6 and
                            all(char.isalnum() for char in response['login']) and
                            len(response['password']) >= 8 and
                            any(char.isdigit() for char in response['password'])):
                        new_data.append(response)
                        with open('users.json', 'w', encoding='utf-8') as json_file:
                            json.dump(new_data, json_file)
                        conn.send(f"{current_time()} - user {response['login']} - registered".encode())
                    else:
                        conn.send(f"{current_time()} - registration error {response['login']} - incorrect password/login".encode())
                elif response['command'] == 'signin':
                    users_json = json.dumps(new_data)
                    if response['login'] in users_json:
                        conn.send(f"{current_time()} - user {response['login']} - login made".encode())
                    else:
                        conn.send(f"{current_time()} - user {response['login']} - incorrect password/login".encode())
                elif response['command'] == 'stop':
                    break
                else:
                    conn.send(f"{current_time()} - user {response['command']} - unknown data".encode())

        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()

except socket.error as e:
    print(f"Socket error: {e}")

finally:
    sock.close()
    print("Server close.")