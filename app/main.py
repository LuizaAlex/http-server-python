import asyncio
import argparse
import re
import sys
from asyncio.streams import StreamReader, StreamWriter
from pathlib import Path

GLOBALS = {}

def stderr(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def parse_request(content: bytes) -> tuple[str, str, dict[str, str], str]:
    first_line, *tail = content.split(b"\r\n")
    method, path, _ = first_line.split(b" ")
    headers: dict[str, str] = {}
    while (line := tail.pop(0)) != b"":
        key, value = line.split(b": ")
        headers[key.decode()] = value.decode()
    return method.decode(), path.decode(), headers, b"".join(tail).decode()

def make_response(
    status: int,
    headers: dict[str, str] | None = None,
    body: str = "",
) -> bytes:
    headers = headers or {}
    headers_str = "\r\n".join(f"{key}: {value}" for key, value in headers.items())
    response = f"HTTP/1.1 {status} {status}\r\n{headers_str}\r\n\r\n{body}"
    return response.encode()

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
            writer.write(make_response(201))  # Fixed: Ensure correct status code and reason
        else:
            writer.write(make_response(404))
        
        stderr(f"[OUT] file {path}")

    else:
        writer.write(make_response(404))
        stderr("[OUT] 404")

    await writer.drain()
    writer.close()

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default=".")
    args = parser.parse_args()
    GLOBALS["DIR"] = args.directory
    server = await asyncio.start_server(handle_connection, "localhost", 4221)
    async with server:
        stderr("Starting server...")
        stderr(f"--directory {GLOBALS['DIR']}")
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
