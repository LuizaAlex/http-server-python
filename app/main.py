import asyncio
import os
import re
import sys

async def parse_request(reader):
    request_line = await reader.readline()
    method, path, http_version = request_line.decode().strip().split()
    
    headers = {}
    while True:
        header_line = await reader.readline()
        if header_line == b'\r\n':
            break
        header_name, header_value = header_line.decode().strip().split(': ', 1)
        headers[header_name.lower()] = header_value
    
    # Read the request body if it exists
    content_length = int(headers.get('content-length', 0))
    if content_length > 0:
        request_body = await reader.read(content_length)
    else:
        request_body = b''
    
    return method, path, http_version, headers, request_body

async def handle_request(reader, writer, directory):
    method, path, http_version, headers, request_body = await parse_request(reader)
    
    file_match = re.match(r'^/files/(.+)$', path)
    if file_match:
        filename = file_match.group(1)
        file_path = os.path.join(directory, filename)

        if method == 'POST':
            with open(file_path, 'wb') as f:
                f.write(request_body)
            
            response = "HTTP/1.1 201 Created\r\n\r\n"
            writer.write(response.encode('utf-8'))

        elif method == 'GET':
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
                writer.write(response)
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
                writer.write(response.encode('utf-8'))
        else:
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
            writer.write(response.encode('utf-8'))

    elif path == '/user-agent':
        user_agent = headers.get('user-agent', 'Unknown').strip()
        response_body = user_agent
        response_headers = [
            "HTTP/1.1 200 OK",
            "Content-Type: text/plain",
            f"Content-Length: {len(response_body)}",
            "\r\n"
        ]
        response = "\r\n".join(response_headers).encode('utf-8') + response_body.encode('utf-8')
        writer.write(response)

    elif re.match(r'^/echo/', path):
        echo_str = path.split('/')[2]
        response_body = echo_str
        response_headers = [
            "HTTP/1.1 200 OK",
            "Content-Type: text/plain",
            f"Content-Length: {len(response_body)}",
            "\r\n"
        ]
        response = "\r\n".join(response_headers).encode('utf-8') + response_body.encode('utf-8')
        writer.write(response)

    elif path == '/':
        response = "HTTP/1.1 200 OK\r\n\r\n"
        writer.write(response.encode('utf-8'))

    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        writer.write(response.encode('utf-8'))

    await writer.drain()
    writer.close()

async def main(directory):
    server = await asyncio.start_server(
        lambda r, w: handle_request(r, w, directory),
        'localhost', 4221)

    async with server:
        print(f'Server running on {server.sockets[0].getsockname()}')
        await server.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != '--directory':
        print("Usage: ./your_server.sh --directory <path>")
        sys.exit(1)

    directory = sys.argv[2]

    if not os.path.isdir(directory):
        print(f"The directory {directory} does not exist or is not a directory.")
        sys.exit(1)

    print("Logs from your program will appear here!")
    asyncio.run(main(directory))
