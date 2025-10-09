import socket
import cv2
import pickle
import struct

def stream_video(video_path, host='0.0.0.0', port=5000):
    """Streams video frames to a client."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}...")

    conn, addr = server_socket.accept()
    print(f"Connection from {addr} established.")

    cap = cv2.VideoCapture(video_path)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("End of video stream.")
                break

            # Serialize the frame and send it
            data = pickle.dumps(frame)
            conn.sendall(struct.pack("Q", len(data)) + data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        conn.close()
        server_socket.close()
        print("Server shut down.")

if __name__ == "__main__":
    #video_path = "D:/Github\Video-Streaming-using-RTP-RTSP-main/Video-Streaming-using-RTP-RTSP-main/Codes/file.mp4"
    video_path = "sample.mp4"
    stream_video(video_path)
