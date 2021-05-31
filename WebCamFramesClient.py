# This file contains the code to launch the Client

import socket, pickle, struct, cv2,Constants,threading
from functools import partial
from tkinter import *

class WebCamClient():

    def startWebCamClient(self,isCorrectIP=None):
        Window = Tk()
        # Renaming the window title
        Window.title("WebCam Streaming Window")

        Window.geometry('500x200')

        ip_text = StringVar()
        ip_label = Label(Window, text='Enter the IP address of the Server', font=['bold']).pack()
        # ip_label.grid(row=0, column=0, sticky=W)
        ip_entry = Entry(Window, textvariable=ip_text).pack()
        # ip_entry.grid(row=0, column=0, padx=350)

        # Creating the connect Button
        # print(ip_text.get(),"--------------------------")
        add_btn = Button(Window, text='Connect', width=12, command=partial(self.webCamClient, ip_text, Window)).pack()
        # add_btn.grid(row=2, column=0, padx=320)
        if not isCorrectIP:
            ip_label = Label(Window, text='Please enter correct IP address', font=['bold']).pack()
        Window.mainloop()
        # If terminated by using the Close Button, Shutting down the web cam
        print("Here!!!!!!!!!!!!!!!!!!!!!!!!!")

    def webCamClient(self, ip_text,Window):
        # destroying the current window

        print("destroying window")
        Window.destroy()

        # Socket creation
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_ip = ip_text.get()
        # print("host ip add:", host_ip)
        port = Constants.CLIENT_PORT
        try:
            client_socket.connect((host_ip, port))  # socket address is a tuple
        except Exception:
            self.startWebCamClient(False)
            return

        print("Receiving web cam feed")
        self.receiveWebCamFeed(client_socket)


    def receiveWebCamFeed(self,client_socket):
        # Creating a Client socket

        # client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # host_ip = Constants.HOST_IP
        # port = Constants.CLIENT_PORT
        # client_socket.connect((host_ip,port)) # socket address is a tuple
        data = b"" # data encoding taken as bytes

        payload_size = struct.calcsize("Q")
        while True:
            try:
                while len(data) < payload_size:
                    packet = client_socket.recv(Constants.PACKET_SIZE) # receiving buffer size 4KB min = 1KB max = 64KB
                    if not packet:
                        break
                    data+=packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q",packed_msg_size)[0]
                while len(data)<msg_size:
                    data+=client_socket.recv(Constants.PACKET_SIZE)
                frame_data = data[:msg_size]
                data = data[msg_size:]
                # loads is used to load pickled data from a bytes string. The "s" in loads refers to the fact that in Python 2, the data was loaded from a string.
                frame = pickle.loads(frame_data)
                cv2.imshow("Receiving Video. Press \'q\' to exit the screen'", frame)
                key = cv2.waitKey(1) & 0xFF
                # cv2.getWindowProperty('window-name', 0) < 0 or
                if key== ord('q'):
                    break
            except Exception:
                print("Exception. Streaming stopped from server")
                break
        client_socket.close()

def main():
    web_cam_client = WebCamClient()
    web_cam_client.startWebCamClient(True)

if __name__ == '__main__':
    main()


