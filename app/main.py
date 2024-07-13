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

    # Initiate the headers dictionary
    headers = {}

    # Process headers
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '':  # Empty line indicates the end of headers
            break
        header_name, header_value = line.split(": ", 1)
        headers[header_name.lower()] = header_value

    # The body is everything after the headers
    body = '\r\n'.join(lines[i+1:])

    return method, path, http_version, headers, body

def handle_request(request, directory):
    method, path, http_version, headers, body = parse_request(request)

    response_headers = [
        "HTTP/1.1 200 OK",
        "Content-Type: text/plain"
    ]

    response_body = ""

    # Handle POST request to /files/{filename}
    if method == 'POST' and re.match(r'^/files/(.+)$', path):
        file_match = re.match(r'^/files/(.+)$', path)
        if file_match and directory:
            # Extract file name
            filename = file_match.group(1)
            file_path = os.path.join(directory, filename)

            # Write the request body to the file
            with open(file_path, 'wb') as f:
                f.write(body.encode('utf-8'))

            # Respond with 201 Created
            response_headers = [
                "HTTP/1.1 201 Created",
                "Content-Type: text/plain",
                "Content-Length: 0",
                "\r\n"
            ]
            response = "\r\n".join(response_headers).encode('utf-8')
            return response
        else:
            # If directory not specified or invalid, return 400 Bad Request
            response_headers = [
                "HTTP/1.1 400 Bad Request",
                "Content-Type: text/plain",
                "Content-Length: 0",
                "\r\n"
            ]
            response = "\r\n".join(response_headers).encode('utf-8')
            return response

    # Handle GET request to /files/{filename}
    elif method == 'GET' and re.match(r'^/files/(.+)$', path):
        file_match = re.match(r'^/files/(.+)$', path)
        if file_match and directory:
            # Extract file name
            filename = file_match.group(1)
            file_path = os.path.join(directory, filename)

            if os.path.exists(file_path) and os.path.isfile(file_path):
                # If file exists, read its content
                with open(file_path, 'rb') as f:
                    file_content = f.read()

                response_headers = [
                    "HTTP/1.1 200 OK",
                    "Content-Type: application/octet-stream",
                    f"Content-Length: {len(file_content)}",
                    "\r\n"
                ]

                response = "\r\n".join(response_headers).encode('utf-8') + file_content
                return response
            else:
                # If file not found, return 404
                response_headers = [
                    "HTTP/1.1 404 Not Found",
                    "Content-Type: text/plain",
                    "Content-Length: 0",
                    "\r\n"
                ]
                response = "\r\n".join(response_headers).encode('utf-8')
                return response

    # Check if the path matches /user-agent
    elif method == 'GET' and path == '/user-agent':
        user_agent = headers.get('user-agent', 'Unknown').strip()
        response_body = user_agent

    # Check if the path matches /echo/{str}
    elif method == 'GET' and re.match(r'^/echo/', path):
        echo_str = path.split('/')[2]
        response_body = echo_str

        # Check for Accept-Encoding header
        accept_encoding = headers.get('accept-encoding', '')
        if 'gzip' in accept_encoding:
            response_headers.append("Content-Encoding: gzip")

    # Check if the path matches /
    elif method == 'GET' and path == '/':
        response_body = ""

    # For any other path, return 404
    else:
        response_headers = [
            "HTTP/1.1 404 Not Found",
            "Content-Type: text/plain",
            "Content-Length: 0",
            "\r\n"
        ]
        response = "\r\n".join(response_headers).encode('utf-8')
        return response

    response_headers.append(f"Content-Length: {len(response_body)}")
    response = "\r\n".join(response_headers) + "\r\n\r\n" + response_body
    return response.encode('utf-8')

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
