import socket
import os
import conversion

HOST = "0.0.0.0"
PORT = 5001
BUFFER_SIZE = 4096

ALLOWED_EXTENSIONS = [".docx", ".pdf", ".txt", ".doc"]

def receive_file(conn):
    # Receive filename size
    filename_size = int(conn.recv(16).decode().strip())
    filename = conn.recv(filename_size).decode()

    # Receive file size
    file_size = int(conn.recv(16).decode().strip())

    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        print("File type not allowed")
        return

    with open("server_received_" + filename, "wb") as f:
        bytes_received = 0
        while bytes_received < file_size:
            remaining = file_size - bytes_received
            chunk_size = min(BUFFER_SIZE, remaining)
            data = conn.recv(chunk_size)
            if not data:
                break
            f.write(data)
            bytes_received += len(data)

    print(f"Received file: {filename}")
    converted_filename = conversion.start("server_received_" +filename)
    if not converted_filename:
        conn.sendall("FAIL".ljust(16).encode())
        return
    conn.sendall("SUCCESS".ljust(16).encode())
    send_file(conn, converted_filename)


def send_file(conn, filename):
    if not os.path.exists(filename):
        print("File not found")
        return

    file_size = os.path.getsize(filename)

    conn.send(f"{len(filename):<16}".encode())
    conn.send(filename.encode())
    conn.send(f"{file_size:<16}".encode())

    with open(filename, "rb") as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            conn.sendall(data)

    print(f"Sent file: {filename}")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Server listening...")

    while True:
        conn, addr = s.accept()
        print("Connected by", addr)

        try:
            def receive_exact(sock, size):
                data = b''
                while len(data) < size:
                    packet = sock.recv(size - len(data))
                    if not packet:
                        return None
                    data += packet
                return data

            command_data = receive_exact(conn, 16)
            if command_data is None:
                conn.close()

            command = command_data.decode().strip()

            if command.startswith("UPLOAD"):
                print("Receiving file...")
                receive_file(conn)

            elif command.startswith("DOWNLOAD"):
                parts = command.split()
                if len(parts) < 2:
                    print("Invalid DOWNLOAD request")
                else:
                    filename = parts[1]
                    print("Sending file...")
                    send_file(conn, filename)

            else:
                print("Unknown command")

        except Exception as e:
            print("Error:", e)

        conn.close()
