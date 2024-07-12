
import socket
import re
import threading
import os
import sys

def parse_request(request):
    lines = request.split('\r\n')

    # Extract the request line
    request_line = lines[0]

    # Extract the method, path, and HTTP version
    method, path, http_version = request_line.split(' ')

    # Initiate de headers dictionary
    headers = {}

    # Process headers
    for line in lines[1:]:
        if line.strip():  # Skip empty lines
            header_name, header_value = line.split(": ", 1)
            headers[header_name.lower()] = header_value

    body = request.split('\r\n\r\n')[1] if '\r\n\r\n' in request else ""
    return method, path, http_version, headers, body





def handle_request(request, directory):
    method, path, http_version, headers, body = parse_request(request)

    # Check if the path matches /files/{filename}
    file_match = re.match(r'^/files/(.+)$', path)
    if file_match:
        filename = file_match.group(1)
        file_path = os.path.join(directory, filename)

        if method == "GET":
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    with open(file_path, 'rb') as f:
                        file_content = f.read()

                    response_headers = [
                        "HTTP/1.1 200 OK",
                        "Content-Type: application/octet-stream",
                        f"Content-Length: {len(file_content)}",
                        "\r\n"
                    ]
                    response = "\r\n".join(response_headers).encode('utf-8') + file_content
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n".encode('utf-8')
        elif method == "POST":
                with open(file_path, 'wb') as f:
                    f.write(body.encode('utf-8'))
  

    # Check if the path matches /user-agent
    elif path == '/user-agent':
        user_agent = headers.get('user-agent', 'Unknown').strip()
        response_body = user_agent

        response_headers = [
            "HTTP/1.1 200 OK",
            "Content-Type: text/plain",
            f"Content-Length: {len(response_body)}",
            "\r\n"
        ]

        response = ("\r\n".join(response_headers) + response_body).encode('utf-8')

    # Check if the path matches /echo/{str}
    elif re.match(r'^/echo/', path):
        echo_str = path.split('/')[2]
        response_body = echo_str

        response_headers = [
            "HTTP/1.1 200 OK",
            "Content-Type: text/plain",
            f"Content-Length: {len(response_body)}",
            "\r\n"
        ]

        response = ("\r\n".join(response_headers) + response_body).encode('utf-8')

    # Check if the path matches /
    elif path == '/':
        response = "HTTP/1.1 200 OK\r\n\r\n".encode('utf-8')

    # For any other path, return 404
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n".encode('utf-8')

    return response




def client_thread(client_socket, directory):
    try:
        # Receive the request
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Request: {request}")

        # Handle the request and generate a response
        response = handle_request(request, directory)

        # Send the response
        client_socket.sendall(response)
    finally:
        # Close the connection
        client_socket.close()



def main():
    directory = None
    if len(sys.argv) == 3 and sys.argv[1] == '--directory':
        directory = sys.argv[2]
        if not os.path.isdir(directory):
            print(f"The directory {directory} does not exist or is not a directory.")
            sys.exit(1)
    elif len(sys.argv) > 1:
        print("Usage: ./your_server.sh --directory <path>")
        sys.exit(1)

    print("Logs from your program will appear here!")

    # Create a server socket
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server running on localhost:4221")

    while True:
        # Accept a connection
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        # Handle the connection in a new thread
        thread = threading.Thread(target=client_thread, args=(client_socket, directory))
        thread.start()


    

if __name__ == "__main__":
    main()
