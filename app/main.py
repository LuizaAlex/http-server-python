import asyncio
import os
import re
import sys
from asyncio.streams import StreamReader, StreamWriter
from pathlib import Path


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

async def handle_connection(reader: StreamReader, writer: StreamWriter) -> None:
    content = await reader.read(2**16)
    method, path, headers, body = parse_request(content)

    if path == "/":
        writer.write(b"HTTP/1.1 200 OK\r\n\r\n")
        stderr("[OUT] echo 200 OK")

    elif match := re.fullmatch(r"/files/(.+)", path):
        filename = match.group(1)
        file_path = Path(GLOBALS["DIR"]) / filename

        if method.upper() == "GET":
            if file_path.is_file():
                file_content = file_path.read_bytes()
                writer.write(
                    make_response(
                        200,
                        {"Content-Type": "application/octet-stream"},
                        file_content.decode(),
                    )
                )
            else:
                writer.write(make_response(404))
        elif method.upper() == "POST":
            file_path.write_bytes(body.encode())
            writer.write(make_response(201))
        else:
            writer.write(make_response(404))
        
        stderr(f"[OUT] file {path}")

    else:
        writer.write(make_response(404))
        stderr("[OUT] 404")

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
