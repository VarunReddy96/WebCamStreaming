# This file contains the code to launch the Webcam Feeder

import socket, pickle, struct, cv2, Constants


def webCamServer():
    # Socket creation

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print("Host IP:", host_ip, "Host Name:", host_name)
    port = 9999
    socket_address = (host_ip, port)

    # Binding server socket to socket address

    server_socket.bind(socket_address)

    # Server socket listening for clients
    # this backlog is used to determine after how many attempts a connection is rejected
    server_socket.listen(5)
    print("Listening at:", socket_address)

    # Accepting a connection from a Client
    while True:
        client_socket, addr = server_socket.accept()
        print("Received connection from:", addr)
        if client_socket:
            vid = cv2.VideoCapture(0)
            while vid.isOpened():
                isImgRead, frame = vid.read()
                if not isImgRead:
                    print("Can't Receive any streaming frames. Exiting.....")
                    break
                framePickle = pickle.dumps(frame)
                frameMessage = struct.pack("Q", len(framePickle)) + framePickle
                try:
                    client_socket.sendall(frameMessage)
                except Exception:
                    break
                cv2.imshow('Transmitting Video. Press \'q\' to exit the screen', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    client_socket.close()
                    break
            vid.release()
            cv2.destroyAllWindows()


def webCamClient():
    # Socket creation

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = Constants.HOST_IP
    port = Constants.CAM_PORT
    client_socket.connect((host_ip, port))  # socket address is a tuple

    # Accepting a connection from a Client
    while True:
        vid = cv2.VideoCapture(0)
        while vid.isOpened():
            isImgRead, frame = vid.read()
            if not isImgRead:
                print("Can't Receive any streaming frames. Exiting.....")
                break
            framePickle = pickle.dumps(frame)
            frameMessage = struct.pack("Q", len(framePickle)) + framePickle
            try:
                client_socket.sendall(frameMessage)
            except Exception:
                break
            cv2.imshow('Transmitting Video. Press \'q\' to exit the screen', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                client_socket.close()
                break
        vid.release()
        cv2.destroyAllWindows()


def main():
    webCamClient()


if __name__ == '__main__':
    main()
