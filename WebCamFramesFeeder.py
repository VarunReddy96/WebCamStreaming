# This file contains the code to launch the Webcam Feeder

import socket, pickle, struct, cv2, Constants, threading
from functools import partial
from tkinter import *
from imutils.video import VideoStream
import time

class Webcam:

    def __init__(self):
        self.isWebCamAlive = True
        self.successfulConnection = False

    # def webCamServer(self):
    #     # Socket creation
    #
    #     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     host_name = socket.gethostname()
    #     host_ip = socket.gethostbyname(host_name)
    #     print("Host IP:", host_ip, "Host Name:", host_name)
    #     port = 9999
    #     socket_address = (host_ip, port)
    #
    #     # Binding server socket to socket address
    #
    #     server_socket.bind(socket_address)
    #
    #     # Server socket listening for clients
    #     # this backlog is used to determine after how many attempts a connection is rejected
    #     server_socket.listen(5)
    #     print("Listening at:", socket_address)
    #
    #     # Accepting a connection from a Client
    #     while True:
    #         client_socket, addr = server_socket.accept()
    #         print("Received connection from:", addr)
    #         if client_socket:
    #             vid = cv2.VideoCapture(0)
    #             while vid.isOpened() and isWebCamAlive:
    #                 isImgRead, frame = vid.read()
    #                 if not isImgRead:
    #                     print("Can't Receive any streaming frames. Exiting.....")
    #                     break
    #                 framePickle = pickle.dumps(frame)
    #                 frameMessage = struct.pack("Q", len(framePickle)) + framePickle
    #                 try:
    #                     client_socket.sendall(frameMessage)
    #                 except Exception:
    #                     break
    #                 cv2.imshow('Transmitting Video. Press \'q\' to exit the screen', frame)
    #                 key = cv2.waitKey(1) & 0xFF
    #                 if key == ord('q'):
    #                     client_socket.close()
    #                     break
    #             vid.release()
    #             cv2.destroyAllWindows()


    # def start_webcam_client(self, isCorrectIP=None):
    #     Window = Tk()
    #     # Renaming the window title
    #     Window.title("WebCam Streaming Window")
    #
    #     Window.geometry('500x200')
    #
    #     ip_text = StringVar()
    #     ip_label = Label(Window, text='Enter the IP address of the Server', font=['bold']).pack()
    #     #ip_label.grid(row=0, column=0, sticky=W)
    #     ip_entry = Entry(Window, textvariable=ip_text).pack()
    #     #ip_entry.grid(row=0, column=0, padx=350)
    #
    #     # Creating the connect Button
    #     # print(ip_text.get(),"--------------------------")
    #     add_btn = Button(Window, text='Connect', width=12, command=partial(self.webcam_client, ip_text, Window)).pack()
    #     #add_btn.grid(row=2, column=0, padx=320)
    #     if not isCorrectIP:
    #         ip_label = Label(Window, text='Please enter correct IP address', font=['bold']).pack()
    #     Window.mainloop()
    #     # If terminated by using the Close Button, Shutting down the web cam
    #     print("Here!!!!!!!!!!!!!!!!!!!!!!!!!")
    #     #self.isWebCamAlive = False
    #     # print("WebCam Started")

    def webcam_client(self):

        # destroying the current window

        # print("destroying window")
        # Window.destroy()

        # Socket creation
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_ip = Constants.SERVER_IP
        #print("host ip add:", host_ip)
        port = Constants.CAM_PORT
        try:
            client_socket.connect((host_ip, port))  # socket address is a tuple
        except Exception:
            # self.start_webcam_client(False)
            print("Enter wrong IP information or the wrong port")
            return
        # self.successfulConnection = True

        print("web cam started")
        # threading.Thread(target=self.webcam_client_feeder, args=[client_socket]).start()
        threading.Thread(target=self.webcam_feeder_test, args=[client_socket]).start()

        # Creating a new window to terminate the web cam feed
        new_window = Tk()
        # Renaming the window title
        new_window.title("WebCam Streaming Window")

        new_window.geometry('500x100')

        ip_text = StringVar()
        ip_label = Label(new_window, text='WebCam is Active.', font=('bold', 14)).pack()
        # ip_label.grid(row=0, column=0)

        # Creating the Terminate Button
        # print(ip_text.get(),"--------------------------")

        add_btn = Button(new_window, text='Terminate Feed', width=12, command=partial(self.shutdown_thread, new_window)).pack()
        new_window.mainloop()
        # If the window is closed using the close button, shutting down the thread
        self.isWebCamAlive = False
        # add_btn.grid(row=1, column=0)




    # def webcam_client_feeder(self, client_socket):
    #
    #     vid = cv2.VideoCapture(0)  # Opening the WebCam using the 0 index or the 1st available camera
    #
    #     # Accepting a connection from a Client
    #     if client_socket:
    #
    #         while vid.isOpened() and self.isWebCamAlive:
    #             try:
    #
    #                 isImgRead, frame = vid.read()
    #                 if not isImgRead:
    #                     print("Can't Receive any streaming frames. Exiting.....")
    #                     break
    #                 framePickle = pickle.dumps(frame)
    #                 frameMessage = struct.pack("Q", len(framePickle)) + framePickle
    #
    #                 client_socket.sendall(frameMessage)
    #
    #                 # cv2.imshow('Transmitting Video. Press \'q\' to exit the screen', frame)
    #                 key = cv2.waitKey(1) & 0xFF
    #                 if key == ord('q'):
    #                     client_socket.close()
    #                     break
    #             except Exception:
    #                 break
    #     vid.release()
    #     cv2.destroyAllWindows()
    #     print("Completed the feeding thread")

    def webcam_feeder_test(self,client_socket):
        vid = VideoStream(src=0).start()
        time.sleep(2.0)
        if client_socket:

            while self.isWebCamAlive:
                try:

                    frame = vid.read()
                    framePickle = pickle.dumps(frame)
                    frameMessage = struct.pack("Q", len(framePickle)) + framePickle

                    client_socket.sendall(frameMessage)

                    # cv2.imshow('Transmitting Video. Press \'q\' to exit the screen', frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        client_socket.close()
                        break
                except Exception:
                    break
        vid.stop()
        cv2.destroyAllWindows()
        print("Completed the feeding thread")


    def shutdown_thread(self, Window):
        self.isWebCamAlive= False
        Window.destroy()
        print("Destroyed the terminate window")



def main():
    webcam = Webcam()
    webcam.webcam_client()





if __name__ == '__main__':
    try:
        main()
    except RuntimeError:
        pass