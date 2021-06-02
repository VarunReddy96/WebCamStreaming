# This file contains the code to launch the Webcam Feeder

import socket, pickle, struct, cv2, Constants, threading, WebStreamingFlask
from imutils.video import VideoStream
from motiondetection.SingleMotionDetector import SingleMotionDetector
from flask import Response
from flask import Flask
from flask import render_template
import argparse
import datetime
import imutils
import time
import cv2

outputFrame = None
lock = threading.Lock()
# # initialize a flask object
app = Flask(__name__)


@app.route('/')
def index():
    # return the rendered template
    return render_template("index.html")


class AWSServer:

    def __init__(self):
        self.client_socket_list = []
        self.threadLock = threading.Lock()

    def add_client_sockets(self, client_socket):
        self.threadLock.acquire()
        self.client_socket_list.append(client_socket)
        self.threadLock.release()

    def webcam_client_server(self):
        # Socket creation

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        print("Host IP:", host_ip, "Host Name:", host_name)
        port = Constants.CLIENT_PORT
        socket_address = (host_ip, port)

        # Binding server socket to socket address

        server_socket.bind(socket_address)

        # Server socket listening for clients
        # this backlog is used to determine after how many attempts a connection is rejected
        server_socket.listen(5)
        print("Listening at:", socket_address)
        while True:
            client_socket, addr = server_socket.accept()
            print("Received connection from client:", addr)
            threading.Thread(target=self.add_client_sockets, args=[client_socket]).start()

    def read_webcam_frames_packets(self, addr, webCam_feeder_socket):
        if webCam_feeder_socket:
            data = b""  # data encoding taken as bytes

            payload_size = struct.calcsize("Q")
            is_still_connected = True
            total = 0
            while True:
                try:
                    while len(data) < payload_size:
                        try:
                            packet = webCam_feeder_socket.recv(
                                Constants.PACKET_SIZE)  # receiving buffer size 4KB min = 1KB max = 64KB
                        except Exception:
                            print("Exception. WebCam socket closed because of disconnecting")
                            is_still_connected = False
                            break

                        if not packet:
                            break
                        data += packet
                    if not is_still_connected:
                        webCam_feeder_socket.close()
                        break
                    if not is_still_connected:
                        webCam_feeder_socket.close()
                        break
                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    msg_size = struct.unpack("Q", packed_msg_size)[0]

                    while len(data) < msg_size:
                        try:
                            data += webCam_feeder_socket.recv(4 * 1024)
                        except Exception:
                            print("Exception. WebCam socket closed because of disconnecting")
                            is_still_connected = False
                            break
                    frame_data = data[:msg_size]
                    data = data[msg_size:]
                    # loads is used to load pickled data from a bytes string. The "s" in loads refers to the fact that in Python 2, the data was loaded from a string.
                    frame = pickle.loads(frame_data)
                    print("Frame processed")
                    # self.detect_motion_from_server(frame, total)
                    self.show_video(frame)
                    # for client_socket in list(self.client_socket_list):
                    #     try:
                    #         client_socket.sendall(packed_msg_size + frame_data)
                    #     except Exception:
                    #         print("Exception.Client socket closed because of disconnecting")
                    #         self.threadLock.acquire()
                    #         if client_socket in self.client_socket_list:
                    #             self.client_socket_list.remove(
                    #                 client_socket)  # If the Client is disconnected it is removed from the Client List
                    #             client_socket.close()
                    #         self.threadLock.release()
                    #         continue
                    if not is_still_connected:
                        webCam_feeder_socket.close()
                        break
                    total += 1
                except Exception:
                    print("Exception. Due to disconnection from web cam")
                    webCam_feeder_socket.close()
                    break

    def webcam_feeder_server(self):
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
            thread = threading.Thread(target=self.read_webcam_frames_packets, args=(addr, webCam_feeder_socket))
            # readWebCamFramesPackets(addr,webCam_feeder_socket)
            thread.start()
            print("Total Web Cams Active:", threading.activeCount() - 1)


    def show_video(self,frame):
        print("In detect motion sensor")
        global outputFrame, lock
        try:
            with lock:
                outputFrame = frame.copy()
        except Exception:
            print('Exception here when updating output frame and locking')


    def detect_motion_from_server(self, frame, total, frameCount=32):
        print("In detect motion sensor")
        global outputFrame, lock
        # initialize the motion detector and the total number of frames
        # read thus far
        md = SingleMotionDetector(accumWeight=0.1)
        frame = imutils.resize(frame, width=400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        # grab the current timestamp and draw it on the frame
        timestamp = datetime.datetime.now()
        cv2.putText(frame, timestamp.strftime(
            "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        # if the total number of frames has reached a sufficient
        # number to construct a reasonable background model, then
        # continue to process the frame
        try:
            if total > frameCount:
                # detect motion in the image
                try:
                    motion = md.detect(gray)
                except Exception:
                    print('Exception. detecting motion failed here check SingleMotionDetector')
                # check to see if motion was found in the frame
                if motion is not None:
                    # unpack the tuple and draw the box surrounding the
                    # "motion area" on the output frame
                    (thresh, (minX, minY, maxX, maxY)) = motion
                    cv2.rectangle(frame, (minX, minY), (maxX, maxY),
                                  (0, 0, 255), 2)
        except Exception:
            print('Exception. Checking for motion detection')
            print(Exception)
            return

        # update the background model and increment the total number
        # of frames read thus far
        md.update(gray)
        total += 1
        print("total upgraded to",total)
        # acquire the lock, set the output frame, and release the
        # lock
        try:
            with lock:
                outputFrame = frame.copy()
        except Exception:
            print('Exception here when updating output frame and locking')


def generate():
    # grab global references to the output frame and lock variables
    print("Yolo Herer check_____________________________------------------")
    global outputFrame, lock
    # loop over frames from the output stream
    try:
        while True:
            # wait until the lock is acquired
            with lock:
                # check if the output frame is available, otherwise skip
                # the iteration of the loop
                if outputFrame is None:
                    print('Output Frame is None')
                    continue
                # encode the frame in JPEG format
                (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
                # ensure the frame was successfully encoded
                if not flag:
                    continue
            # yield the output frame in the byte format
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encodedImage) + b'\r\n')
    except Exception:
        print("Error in streaming to web. Generate function")


def text_feed():
    return "Hello"


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


def main():
    aws_server = AWSServer()
    threading.Thread(target=aws_server.webcam_feeder_server, args=()).start()
    # threading.Thread(target=aws_server.webcam_client_server, args=()).start()
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)
    # webCamFeederServer()
    # webCamClientServer()


if __name__ == '__main__':
    main()
