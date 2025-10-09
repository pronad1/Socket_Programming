import socket
import cv2
import pickle
import struct
import threading
import tkinter as tk
from tkinter import Button, Label
from PIL import Image, ImageTk

class VideoClient:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server {self.host}:{self.port}.")

        self.data = b""
        self.payload_size = struct.calcsize("Q")
        self.running = False  # Control video streaming

        self.root = tk.Tk()
        self.root.title("Video Client")
        self.root.geometry("800x600")

        self.video_label = Label(self.root)
        self.video_label.pack(pady=20)

        self.play_button = Button(self.root, text="Play", command=self.start_streaming, font=("Arial", 12))
        self.play_button.pack(side="left", padx=10)

        self.pause_button = Button(self.root, text="Pause", command=self.pause_streaming, font=("Arial", 12))
        self.pause_button.pack(side="left", padx=10)

    def start_streaming(self):
        """Starts the video streaming."""
        if not self.running:
            self.running = True
            threading.Thread(target=self.update_frame, daemon=True).start()

    def pause_streaming(self):
        """Pauses the video streaming."""
        self.running = False

    def update_frame(self):
        """Continuously updates the frame in the GUI."""
        while self.running:
            try:
                while len(self.data) < self.payload_size:
                    packet = self.client_socket.recv(4096)  # Receive 4096 bytes at a time
                    if not packet:
                        return
                    self.data += packet

                packed_msg_size = self.data[:self.payload_size]
                self.data = self.data[self.payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(self.data) < msg_size:
                    self.data += self.client_socket.recv(4096)

                frame_data = self.data[:msg_size]
                self.data = self.data[msg_size:]

                # Deserialize and display frame
                frame = pickle.loads(frame_data)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (600, 400))
                img = ImageTk.PhotoImage(Image.fromarray(frame))
                self.video_label.config(image=img)
                self.video_label.image = img

            except Exception as e:
                print(f"Error: {e}")
                self.running = False
                break

    def run(self):
        """Starts the GUI event loop."""
        self.root.mainloop()
        self.client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    client = VideoClient()
    client.run()
