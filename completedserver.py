import socket
import os
import threading
import time
from queue import Queue
import conversion

HOST = "0.0.0.0"
PORT = 5001
BUFFER_SIZE = 4096

ALLOWED_EXTENSIONS = [".docx", ".pdf", ".txt", ".doc"]

# Job queue
job_queue = Queue()


def receive_exact(conn, size):
    data = b""
    while len(data) < size:
        packet = conn.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data


def receive_file(conn):
    raw = receive_exact(conn, 16)
    if not raw:
        return None

    filename_size = int(raw.decode().strip())
    filename = receive_exact(conn, filename_size).decode()

    file_size = int(receive_exact(conn, 16).decode().strip())

    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        print("❌ File type not allowed")
        return None

    with open(filename, "wb") as f:
        bytes_received = 0
        while bytes_received < file_size:
            data = conn.recv(min(BUFFER_SIZE, file_size - bytes_received))
            if not data:
                return None
            f.write(data)
            bytes_received += len(data)

    print("📥 File received:", filename)
    return os.path.abspath(filename)


def send_file(conn, filepath):
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)

    conn.sendall(f"{len(filename):<16}".encode())
    conn.sendall(filename.encode())
    conn.sendall(f"{file_size:<16}".encode())

    with open(filepath, "rb") as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            conn.sendall(data)

    print("📤 Sent:", filename)


# ---------------- WORKER THREAD ----------------

def worker(worker_id): # they are made first and they keep waiting for a job to take and complete(FSFC)
    while True:
        conn, filepath = job_queue.get() # if no jobs are present inside queue, the code will not go forward

        try:
            print(f"⚙️ Worker {worker_id} processing:", filepath)

            # simulate heavy processing (demo)
            time.sleep(5)

            converted_file = conversion.start(filepath)

            if converted_file and os.path.exists(converted_file):
                conn.sendall("SUCCESS".ljust(16).encode())
                send_file(conn, converted_file)
            else:
                conn.sendall("FAILED".ljust(16).encode())

        except Exception as e:
            print("Worker error:", e)

        conn.close()
        job_queue.task_done()


# ---------------- CLIENT HANDLER ----------------

def handle_client(conn, addr):
    print("🔗 Connected:", addr)

    try:
        command = receive_exact(conn, 16).decode().strip()

        if command == "UPLOAD":

            filepath = receive_file(conn) # calls the binary file transfer file

            if filepath:
                print("📌 Job added to queue")
                job_queue.put((conn, filepath)) # job added inside the job queue
            else:
                conn.sendall("FAILED".ljust(16).encode())
                conn.close()

        else:
            print("❌ Unknown command")
            conn.close()

    except Exception as e:
        print("Server error:", e)
        conn.close()


# ---------------- SERVER ----------------

def start_server():

    # Start multiple workers (parallel job processing)
    for i in range(3):
        threading.Thread(target=worker, args=(i+1,), daemon=True).start() # makes worker threads and keep them waiting at the queue for a job to complete

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind((HOST, PORT)) 
        s.listen()

        print("📡 Server listening on port", PORT)

        while True:
            conn, addr = s.accept()

            # concurrent client handling
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()


if __name__ == "__main__":
    start_server()