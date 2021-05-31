# This file contains the code to launch the Webcam Feeder

import socket, pickle, struct, cv2, Constants, threading

client_socket_list = []
threadLock = threading.Lock()

def addClientSockets(client_socket):
    threadLock.acquire()
    client_socket_list.append(client_socket)
    threadLock.release()

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
        threading.Thread(target=addClientSockets, args=[client_socket]).start()




def readWebCamFramesPackets(addr, webCam_feeder_socket):
    if webCam_feeder_socket:
        data = b""  # data encoding taken as bytes

        payload_size = struct.calcsize("Q")
        isStillconnected = True
        while True:
            try:
                while len(data) < payload_size:
                    try:
                        packet = webCam_feeder_socket.recv(Constants.PACKET_SIZE) # receiving buffer size 4KB min = 1KB max = 64KB
                    except Exception:
                        print("Exception. WebCam socket closed because of disconnecting")
                        isStillconnected = False
                        break

                    if not packet:
                        break
                    data+=packet
                if not isStillconnected:
                    webCam_feeder_socket.close()
                    break
                if not isStillconnected:
                    webCam_feeder_socket.close()
                    break
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q",packed_msg_size)[0]

                while len(data)<msg_size:
                    try:
                        data+=webCam_feeder_socket.recv(4*1024)
                    except Exception:
                        print("Exception. WebCam socket closed because of disconnecting")
                        isStillconnected = False
                        break
                frame_data = data[:msg_size]
                data = data[msg_size:]
                # loads is used to load pickled data from a bytes string. The "s" in loads refers to the fact that in Python 2, the data was loaded from a string.
                #frame = pickle.loads(frame_data)

                for client_socket in list(client_socket_list):
                    try:
                        client_socket.sendall(packed_msg_size + frame_data)
                    except Exception:
                        print("Exception.Client socket closed because of disconnecting")
                        threadLock.acquire()
                        if client_socket in client_socket_list:
                            client_socket_list.remove(client_socket) # If the Client is disconnected it is removed from the Client List
                            client_socket.close()
                        threadLock.release()
                        continue
                if not isStillconnected:
                    webCam_feeder_socket.close()
                    break
            except Exception:
                print("Exception. Due to disconnection from web cam")
                webCam_feeder_socket.close()
                break

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


    while True:
        webCam_feeder_socket, addr = server_socket.accept()
        print("Received connection from WebCam:", addr)
        thread = threading.Thread(target=readWebCamFramesPackets,args=(addr,webCam_feeder_socket))
        #readWebCamFramesPackets(addr,webCam_feeder_socket)
        thread.start()
        print("Total Web Cams Active:",threading.activeCount()-1)



def main():
    threading.Thread(target=webCamFeederServer,args=()).start()
    threading.Thread(target=webCamClientServer, args=()).start()
    # webCamFeederServer()
    # webCamClientServer()


if __name__ == '__main__':
    main()
