
import socket
import re
import threading
import os
import sys


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



def handle_request(request,directory):
   method, path, http_version, headers = parse_request(request)

   # Check if the path matches /files/{filename}
   file_match = re.match(r'^/files/(.+)$', path)
   if file_match:
        # Extract file name
        filename = file_match.group(1)
        file_path = os.path.join(directory, filename)

 # Check if the path matches /user-agent
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
            # If file not found, return 404
            response = "HTTP/1.1 404 Not Found\r\n\r\n".encode('utf-8')


       #Check if the path matches /user-agent     
   elif path == '/user-agent':
        
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
       
        response = "HTTP/1.1 200 OK\r\n\r\n".encode('utf-8')
   else:
       
        response = "HTTP/1.1 404 Not Found\r\n\r\n".encode('utf-8')

   return response





def client_thread(client_socket, directory): 
    try: 
        #Receive the request
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Request: {request}")

        #Handle the request and generate a response:
        response = handle_request(request, directory)

        #Send the response
        client_socket.sendall(response.encode('utf-8'))
    finally:
        #Close de connection 
        client_socket.close()


def main():
   
   if len(sys.argv) != 3 or sys.argv[1] != '--directory':
        print("Usage: ./your_server.sh --directory <path>")
        sys.exit(1)
    
   directory = sys.argv[2]
    
   if not os.path.isdir(directory):
        print(f"The directory {directory} does not exist or is not a directory.")
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





    #server_socket.accept() # wait for client
    #server_socket.accept()[0].sendall(b"HTTP/1.1 200 OK\r\n\r\n")


if __name__ == "__main__":
    main()
