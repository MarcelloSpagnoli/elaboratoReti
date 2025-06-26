import socket
import os
import mimetypes
import threading
from datetime import datetime

HOST = 'localhost'
PORT = 8080
WWW_ROOT = './www'
LOG_FILE = 'server.log'

def log(message: str) -> None:
    """Fa il log su terminale e su file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = f"[{timestamp}] {message}"
    print(entry)
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(entry + '\n')
    except Exception as e:
        print(f"[!] Logging error: {e}")

def build_response(status_code: int, content: bytes, content_type: str) -> bytes:
    """Costruisce la risposta HTTP."""
    status_messages = {
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found',
        405: 'Method Not Allowed',
        500: 'Internal Server Error',
    }
    status_text = status_messages.get(status_code, 'OK')

    headers = [
        f"HTTP/1.1 {status_code} {status_text}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(content)}",
        "Connection: close"
    ]
    header_bytes = "\r\n".join(headers).encode('utf-8') + b"\r\n\r\n"

    return header_bytes + content


def handle_client(client_socket: socket.socket, client_address: tuple) -> None:
    """Gestisce la connessione del client."""
    try:
        try:
            request_line = client_socket.recv(1024).decode('utf-8', errors='ignore').splitlines()[0]
            method, path, _ = request_line.split()
        except ValueError:
            response = build_response(
                400,
                build_error("400: Malformed request"),
                "text/html; charset=utf-8"
            )
            client_socket.sendall(response)
            log(f"[{client_address[0]}] Malformed request - 400")
            return

        if method != 'GET':
            response = build_response(
                405,
                build_error(f"405: Method {method} not allowed"),
                "text/html; charset=utf-8"
            )
            client_socket.sendall(response)
            log(f"[{client_address[0]}] {method} {path} - 405")
            return

        file_path = os.path.join(WWW_ROOT, path.lstrip('/'))
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
            mime_type, _ = mimetypes.guess_type(path)
            if mime_type.startswith("text/"):
                mime_type += "; charset=utf-8"
            response = build_response(200, content, mime_type)
            client_socket.sendall(response)
            log(f"[{client_address[0]}] GET {path} - 200")
        else:
            response = build_response(
                404,
                build_error(f"404: File not found --> {path}"),
                "text/html; charset=utf-8"
            )
            client_socket.sendall(response)
            log(f"[{client_address[0]}] GET {path} - 404")
    except Exception as e:
        response = build_response(
            500,
            build_error("500: Internal Server Error"),
            "text/html; charset=utf-8"
        )
        client_socket.sendall(response)
        log(f"[{client_address[0]}] Server error: - 500")
    finally:
        client_socket.close()
    
def build_error(msg: str) -> bytes:
    """Costruisce una pagina di errore usando error.html come template."""
    error_path = os.path.join(WWW_ROOT, "error.html")
    with open(error_path, "r", encoding="utf-8") as f:
        template = f.read()
    content = template.replace("{{ message }}", msg)
    return content.encode("utf-8")

def start_server() -> None:
    """Metodo per startare il server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen()
        log(f"Server started on http://{HOST}:{PORT}")
        try:
            while True:
                client_sock, client_addr = server_sock.accept()
                threading.Thread(target=handle_client, args=(client_sock, client_addr), daemon=True).start()
        except KeyboardInterrupt:
            log("Server shutting down...")

if __name__ == "__main__":
    start_server()
