
import socket
import re


def parse_request(request):
    lines = request.split('\r\n')

    #Extract the request line
    request_line = lines[0]

    #Extract the method, path, and HTTP version
    method, path, http_version = request_line.split(' ')


    #Initiate de headers dictionary
    headers = {} 

    #Process headers

    for line in lines[1:]:
        if line.strip(): #Skip empty lines
            header_name, header_value = line.split(": ", 1)
            headers[header_name.lower()] = header_value 

    return method, path, http_version, headers



def handle_request(request):
   method, path, http_version, headers = parse_request(request)

 # Check if the path matches /user-agent
   if path == '/user-agent':
        user_agent = headers.get('user-agent', 'Unknown').strip()
        response_body = user_agent
        response_headers = [
            "HTTP/1.1 200 OK",
            "Content-Type: text/plain",
            f"Content-Length: {len(response_body)}",
            "\r\n"
        ]
        response = "\r\n".join(response_headers) + response_body
        
   elif re.match(r'^/echo/', path):
        echo_str = path.split('/')[2]
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
