import socket

def send_request(request_text):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 8080))
        s.sendall(request_text.encode())
        response = s.recv(4096)
        print(response.decode(errors='ignore'))
        print('-' * 50)

def test_200():
    print("Test 200: richiesta valida GET /index.html")
    req = "GET /index.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(req)

def test_404():
    print("Test 404: richiesta GET file inesistente")
    req = "GET /nofile.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(req)

def test_405():
    print("Test 405: metodo non supportato POST")
    req = "POST /index.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(req)

def test_400():
    print("Test 400: richiesta malformata")
    req = "/index.html\r\n\r\n"
    send_request(req)

def test_500():
    print("Test 500: errore interno (test500.html non ha permessi di lettura)")
    req = "GET /test500.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(req)

if __name__ == "__main__":
    test_200()
    test_404()
    test_405()
    test_400()
    test_500()