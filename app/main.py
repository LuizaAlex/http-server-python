import socket
import re
import sys
import threading
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
    if os.path.exists(filepath):
        print("file exist")
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
    else:
        print("file not found")
        response = "HTTP/1.1 404 Not Found" "\r\n" "\r\n"
    return response


def handle_file_post(request, filepath):
    # extract the text content from the request
    request_part = request.split("\r\n")
    request_body = request_part[-1]
    # open the file using the file path and write the content
    with open(filepath, "w") as f:
        f.write(request_body)
    # return response 201
    response = "HTTP/1.1 201 Created" "\r\n" "\r\n"
    return response
def endpoint_file(request, request_method):
    FILE_DIRECTORY = sys.argv[2]
    filename = re.search(r"/files/([^ ]+)", request).group(1)
    filepath = os.path.join(FILE_DIRECTORY, filename)
    match request_method:
        case "GET":
            response = handle_file_get(filepath)
        case "POST":
            response = handle_file_post(request, filepath)
        case _:
            response = "invalid method"
    return response


def endpoint_user_agent(request):
    print(request)
    user_agent_value = re.search(r"User-Agent:\s*(.+)", request).group(1).strip()
    response = (
        "HTTP/1.1 200 OK"
        "\r\n"
        f"Content-Type: text/plain\r\nContent-Length: {len(user_agent_value)}\r\n"
        "\r\n"
        f"{user_agent_value}"
    )
    return response
def handle_client_connection(client_socket):
    # handle client socket
    request = client_socket.recv(1024).decode("utf-8")
    match = re.match(r"([^ ]*) (/[^ ]*) HTTP/1.1", request)
    if match:
        request_method = match.group(1)
        endpoint = match.group(2)
    else:
        endpoint = "/"

        # handling different endpoint
    match endpoint:
        case "/":  # null
            response = "HTTP/1.1 200 OK" + "\r\n" + "\r\n"
        case endpoint if endpoint.startswith("/echo/"):  # echo
            response = endpoint_echo(request)
        case endpoint if endpoint.startswith("/files/"):  # file
            response = endpoint_file(request, request_method)
        case "/user-agent":  # user-agent
            response = endpoint_user_agent(request)
        case _:  # not found
            response = "HTTP/1.1 404 Not Found" + "\r\n" + "\r\n"
    print(response)
    client_socket.sendall(response.encode())
    client_socket.close()


    def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
        print("Logs from your program will appear here!")
    # create the server socket
        server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    # Main server loop to accept connections
    while True:
            client_socket, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(
                target=handle_client_connection, args=(client_socket,)
            )
            client_handler.start()
            
if __name__ == "__main__":
    main()