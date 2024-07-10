
import socket
import re

def handle_request(request):
    #Split request into lines
    lines = request.split('\r\n')

    #Extract the request line
    request_line = lines[0]

    #Extract the method, path, and HTTP version
    method, path, http_version = request_line.split(' ')

    #Check if the path matches /echo/{str}

    # Check if the path matches /echo/{str}
    match = re.match(r'^/echo/(.*)$', path)
    if match:
        echo_str = match.group(1)
        response_body = echo_str
        response_headers = [
            "HTTP/1.1 200 OK",
            "Content-Type: text/plain",
            f"Content-Length: {len(response_body)}",
            "\r\n"
        ]
        response = "\r\n".join(response_headers) + response_body
    elif path == '/':
        response = "HTTP/1.1 200 OK\r\n\r\n"
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
    
    return response

    


def main():
   
    print("Logs from your program will appear here!")

    # Create a server socket
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server running on localhost:4221")

    while True:

        #Accept a connection 
        client_socket, client_address = server_socket.accept()

        #Receive the request
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Request: {request}")

        #Handle the response and generate a response
        response = handle_request(request)
        
        #Send the response
        client_socket.sendall(response.encode('utf-8'))

        #Close the connection
        client_socket.close()





    #server_socket.accept() # wait for client
    #server_socket.accept()[0].sendall(b"HTTP/1.1 200 OK\r\n\r\n")


if __name__ == "__main__":
    main()
