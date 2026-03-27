import socket
import os

SERVER_IP = "10.1.20.110"   # change if needed
PORT = 5001
BUFFER_SIZE = 4096

ALLOWED_EXTENSIONS = [".docx", ".pdf", ".txt", ".doc"]


def receive_exact(sock, size):
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data


def send_file(sock, filepath):
    if not os.path.exists(filepath):
        print("❌ File does not exist")
        return False

    filename = os.path.basename(filepath)

    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        print("❌ File type not allowed")
        return False

    file_size = os.path.getsize(filepath)

    sock.sendall(f"{len(filename):<16}".encode())
    sock.sendall(filename.encode())
    sock.sendall(f"{file_size:<16}".encode())

    with open(filepath, "rb") as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            sock.sendall(data)

    print(f"✅ Uploaded: {filename}")
    return True


def receive_file(sock):
    filename_size = int(receive_exact(sock, 16).decode().strip())
    filename = receive_exact(sock, filename_size).decode()
    file_size = int(receive_exact(sock, 16).decode().strip())

    save_name = "client_received_" + filename

    with open(save_name, "wb") as f:
        bytes_received = 0
        while bytes_received < file_size:
            data = sock.recv(min(BUFFER_SIZE, file_size - bytes_received))
            if not data:
                return
            f.write(data)
            bytes_received += len(data)

    print(f"✅ Downloaded converted file: {filename}")


def main():
    filepath = input("Enter full file path to upload: ")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, PORT))

        # Send command
        s.sendall("UPLOAD".ljust(16).encode())

        if send_file(s, filepath):

            print("📥 Waiting for conversion result...")

            status = receive_exact(s, 16).decode().strip()

            if status == "SUCCESS":
                receive_file(s)
            else:
                print("❌ Server failed to convert file")


if __name__ == "__main__":
    while(True):
        main()
