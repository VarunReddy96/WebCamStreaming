# This file contains the code to launch the Client

import socket, pickle, struct, cv2,Constants


def Client():
    # Creating a Client socket

    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_ip = Constants.HOST_IP
    port = Constants.CLIENT_PORT
    client_socket.connect((host_ip,port)) # socket address is a tuple
    data = b"" # data encoding taken as bytes

    payload_size = struct.calcsize("Q")
    while True:
        while len(data) < payload_size:
            packet = client_socket.recv(4*1024) # receiving buffer size 4KB min = 1KB max = 64KB
            if not packet:
                break
            data+=packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        while len(data)<msg_size:
            data+=client_socket.recv(4*1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        # loads is used to load pickled data from a bytes string. The "s" in loads refers to the fact that in Python 2, the data was loaded from a string.
        frame = pickle.loads(frame_data)
        cv2.imshow("Receiving Video. Press \'q\' to exit the screen'", frame)
        key = cv2.waitKey(1) & 0xFF
        # cv2.getWindowProperty('window-name', 0) < 0 or
        if key== ord('q'):
            break
    client_socket.close()

def main():
    Client()

if __name__ == '__main__':
    main()


