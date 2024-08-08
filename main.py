from threading import Thread, active_count
from colorama import Fore
from os import stat
import socket


def handel_REQUEST(request: str):
    REQUEST_DATA = request.split('\r\n')
    REQUEST_endpoint_DATA = REQUEST_DATA[0].split(' ')
    REQUEST_HEADER = request.split('\r\n')[1].split(": ")
    
    message = ""

    REQUEST_DATA = {
        "method" : REQUEST_endpoint_DATA[0],
        "endpoint" : REQUEST_endpoint_DATA[1],
        "HTTP_version" : REQUEST_endpoint_DATA[2],
        "user_agent" : REQUEST_HEADER[1], 
    }

    ENDPOINTS = ["/", "/index.html", "/echo/", "/user-agent", "/file/"]
    FILES = ["index.txt", "test.html"]
    
    if REQUEST_DATA['endpoint'].startswith('/echo/'):
        ECHO_MESSAGE = REQUEST_DATA['endpoint'].split('/echo/')[1]
        ECHO_MESSAGE_LENGTH = f'{len(ECHO_MESSAGE)}'.encode()
        
        message = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: ' + ECHO_MESSAGE_LENGTH + b'\r\n\r\n' + ECHO_MESSAGE.encode()
        
        return message

    if REQUEST_DATA["endpoint"].startswith("/files/"): 
        REQUESTED_FILE = REQUEST_DATA["endpoint"].split("/files/")[1]

        if REQUESTED_FILE in FILES:
            FILE_STAT = stat(f"codecrafters-http-server-python/app/{REQUESTED_FILE}")
            FILE_SIZE = f"{FILE_STAT.st_size}".encode()

            with open(f"codecrafters-http-server-python/app/{REQUESTED_FILE}", "r+") as file:
                FILE_CONTENT = file.read()

            message = b'HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: ' + FILE_SIZE  + b'\r\n\r\n' + FILE_CONTENT.encode()

            return message
                    
        message = b'HTTP/1.1 404 Not Found\r\n\r\n'

        return message

    if REQUEST_DATA['endpoint'] == "/user-agent":
        USER_AGENT = REQUEST_DATA["user_agent"]

        message = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: ' + str(len(USER_AGENT)).encode() + b'\r\n\r\n' + USER_AGENT.encode()
        return message
    
    for index, endpoint in enumerate(ENDPOINTS):
        if REQUEST_DATA['endpoint'] == endpoint:
            message = b'HTTP/1.1 200 OK\r\n\r\n'

            return message
            break

    else:
        message = b'HTTP/1.1 404 Not Found\r\n\r\n'
    
        return message


def start(connection: socket.socket):
    REQUEST = connection.recv(1048).decode()
    MESSAGE = handel_REQUEST(REQUEST)
    
    print(Fore.GREEN + REQUEST)
    print(Fore.MAGENTA + "---------------------")
    print(Fore.CYAN + MESSAGE.decode())
    print(Fore.MAGENTA + "---------------------")
   
    connection.sendall(MESSAGE)


def main():
    # server_socket = socket.create_server(("localhost", 4221))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("localhost", 4221))
        
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        server_socket.listen()

        while True:
            connection, address = server_socket.accept() # wait for client

            thread = Thread(target= start, args=(connection, ))
            thread.start()


if __name__ == "__main__":
    main()
