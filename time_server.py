import socket
import threading
from datetime import datetime
import logging

class ClientHandler(threading.Thread):
    def __init__(self, connection, address):
        super().__init__()
        self.connection = connection
        self.address = address

    def run(self):
        try:
            while True:
                data = self.connection.recv(1024)
                if not data:
                    break
                request = data.decode('utf-8').strip()
                
                if request == "QUIT":
                    logging.info(f"Client {self.address} disconnected.")
                    break
                
                if request.startswith("TIME"):
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    response = f"JAM {current_time}\r\n"
                    self.connection.sendall(response.encode('utf-8'))
                else:
                    self.connection.sendall(b"Invalid request\r\n")
        except Exception as e:
            logging.error(f"Error with client {self.address}: {e}")
        finally:
            self.connection.close()

class TimeServer(threading.Thread):
    def __init__(self, host='0.0.0.0', port=45000):
        super().__init__()
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_threads = []

    def run(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"Time Server started on {self.host}:{self.port}")
        try:
            while True:
                client_conn, client_addr = self.server_socket.accept()
                logging.info(f"Connection from {client_addr}")
                client_thread = ClientHandler(client_conn, client_addr)
                client_thread.start()
                self.client_threads.append(client_thread)
        except KeyboardInterrupt:
            logging.info("Shutting down server.")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    server = TimeServer()
    server.start()
