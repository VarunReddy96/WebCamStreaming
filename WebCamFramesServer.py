# This file contains the code to launch the Webcam Feeder

import socket, pickle, struct, cv2, Constants

client_socket_list = []

def webCamClientServer():
    # Socket creation

    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print("Host IP:",host_ip,"Host Name:",host_name)
    port = Constants.CLIENT_PORT
    socket_address = (host_ip,port)

    # Binding server socket to socket address

    server_socket.bind(socket_address)

    # Server socket listening for clients
    # this backlog is used to determine after how many attempts a connection is rejected
    server_socket.listen(5)
    print("Listening at:",socket_address)
    while True:
        client_socket,addr = server_socket.accept()
        print("Received connection from client:",addr)
        client_socket_list.append(client_socket)




def webCamFeederServer():
    # Creating a Socket connection to Web Cam Server

    # Socket creation

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print("Host IP:", host_ip, "Host Name:", host_name)
    port = Constants.CAM_PORT
    socket_address = (host_ip, port)

    # Binding server socket to socket address

    server_socket.bind(socket_address)

    # Server socket listening for clients
    # this backlog is used to determine after how many attempts a connection is rejected
    server_socket.listen(5)
    print("Listening at:", socket_address)
    data = b"" # data encoding taken as bytes

    payload_size = struct.calcsize("Q")

    while True:
        isStillconnected = True
        webCam_feeder_socket, addr = server_socket.accept()

        while len(data) < payload_size:
            try:
                packet = webCam_feeder_socket.recv(4*1024) # receiving buffer size 4KB min = 1KB max = 64KB
            except Exception:
                isStillconnected = False
                break

            if not packet:
                break
            data+=packet
        if not isStillconnected:
            continue
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        while len(data)<msg_size:
            data+=webCam_feeder_socket.recv(4*1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        # loads is used to load pickled data from a bytes string. The "s" in loads refers to the fact that in Python 2, the data was loaded from a string.
        #frame = pickle.loads(frame_data)

        for client_socket in list(client_socket_list):
            try:
                client_socket.sendall(packed_msg_size + frame_data)
            except Exception:
                client_socket_list.remove(client_socket) # If the Client is disconnected it is removed from the Client List
                break

        #cv2.imshow("Receiving Video. Press \'q\' to exit the screen'", frame)
        #key = cv2.waitKey(1) & 0xFF
        # cv2.getWindowProperty('window-name', 0) < 0 or
        # if key== ord('q'):
        #     break



def main():
    webCamFeederServer()
    webCamClientServer()
