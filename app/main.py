import socket
import re
import threading
import sys
import os

def endpoint_echo(request):
    echo_pattern = re.compile(r"/echo/([^ ]+)")
    body = re.search(echo_pattern, request).group(1)
    response = (
        "HTTP/1.1 200 OK"
        "\r\n"
        f"Content-Type: text/plain\r\nContent-Length: {len(body)}\r\n"
        "\r\n"
        f"{body}"
    )
    return response

def handle_file_get(filepath):
    try:
        with open(filepath, "r") as f:
            file_content = f.read()
        response = (
            "HTTP/1.1 200 OK"
            "\r\n"
            f"Content-Type: application/octet-stream\r\n"
            f"Content-Length: {len(file_content)}\r\n"
            "\r\n"
            f"{file_content}"
        )
    except FileNotFoundError:
        response = "HTTP/1.1 404 Not Found" "\r\n" "\r\n"
    except Exception as e:
        response = "HTTP/1.1 500 Internal Server Error" "\r\n" "\r\n"
    return response

def handle_file_post(request, filepath):
    try:
        request_part = request.split("\r\n")
        request_body = request_part[-1]
        with open(filepath, "w") as f:
            f.write(request_body)
        response = "HTTP/1.1 201 Created" "\r\n" "\r\n"
    except Exception as e:
        response = "HTTP/1.1 500 Internal Server Error" "\r\n" "\r\n"
    return response

def endpoint_file(request, request_method, file_directory):
    filename = re.search(r"/files/([^ ]+)", request).group(1)
    filepath = os.path.join(file_directory, filename)
    
    if request_method == "GET":
        response = handle_file_get(filepath)
    elif request_method == "POST":
        response = handle_file_post(request, filepath)
    else:
        response = "HTTP/1.1 405 Method Not Allowed" "\r\n" "\r\n"
    
    return response

def endpoint_user_agent(request):
    user_agent_value = re.search(r"User-Agent:\s*(.+)", request).group(1).strip()
    response = (
        "HTTP/1.1 200 OK"
        "\r\n"
        f"Content-Type: text/plain\r\nContent-Length: {len(user_agent_value)}\r\n"
        "\r\n"
        f"{user_agent_value}"
    )
    return response

def handle_client_connection(client_socket, file_directory):
    request = client_socket.recv(1024).decode("utf-8")
    
    match = re.match(r"([^ ]*) (/[^ ]*) HTTP/1.1", request)
    if match:
        request_method = match.group(1)
        endpoint = match.group(2)
    else:
        endpoint = "/"
    
    if endpoint == "/":
        response = "HTTP/1.1 200 OK" "\r\n" "\r\n"
    elif endpoint.startswith("/echo/"):
        response = endpoint_echo(request)
    elif endpoint.startswith("/files/"):
        response = endpoint_file(request, request_method, file_directory)
    elif endpoint == "/user-agent":
        response = endpoint_user_agent(request)
    else:
        response = "HTTP/1.1 404 Not Found" "\r\n" "\r\n"
    
    client_socket.sendall(response.encode())
    client_socket.close()

def main():
    if len(sys.argv) != 3:
        print("Usage: ./your_server.sh <port> <directory>")
        sys.exit(1)
    
    port = int(sys.argv[1])
    file_directory = sys.argv[2]

    server_socket = socket.create_server(("localhost", port), reuse_port=True)
    print(f"Server running on localhost:{port}")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        
        client_handler = threading.Thread(
            target=handle_client_connection, args=(client_socket, file_directory)
        )
        client_handler.start()

if __name__ == "__main__":
    main()
