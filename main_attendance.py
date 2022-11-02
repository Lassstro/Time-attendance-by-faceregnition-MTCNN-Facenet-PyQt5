from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import *

import tensorflow as tf
from imutils.video import VideoStream
import sys
import pickle
import numpy as np
import collections
import cv2
import datetime

import facenet
import detect_face
from main_data import Main_data
from main_login import Main_login

data_dir = './Dataset/data.db'
TIME_DELAY = 1   ## thời gian giữa 2 lần điểm danh (phút)

class Main_attendance(QMainWindow):
    def __init__(self):
        super(Main_attendance, self).__init__()
        loadUi('GUI/ui_attendance.ui',self)
        timer = QTimer(self) #Bộ đểm thời gian
        timer.timeout.connect(self.displayTime_Data) 
        timer.start(1000)
        self.pushButton.clicked.connect(self.face_rec_cam)
        self.pushButton_2.clicked.connect(self.show_main_login)
        self.pushButton_3.clicked.connect(self.exitt)
        self.pushButton_5.clicked.connect(self.show_main_data)
    
    def show_main_login(self):
        b = Main_login()
        b.exec_()

    def show_main_data(self):
        a = Main_data()
        a.exec_()

    def exitt(self):
        exit()

    def displayImage(self,img): #Hiển thị ảnh ra giao diện
	    qformat=QImage.Format_RGB888
	    img = QImage(img,img.shape[1],img.shape[0],qformat)
	    img = img.rgbSwapped()
	    self.imgLabel.setPixmap(QPixmap.fromImage(img))

    def displayTime_Data(self): #Hiển thị thời gian, data ra giao diện 
        self.loaddata()
        DateTime = datetime.datetime.now()
        self.labelDate.setText(DateTime.strftime('%d/%m/%Y'))
        self.labelDate_2.setText(DateTime.strftime('%d/%m/%Y'))
        self.labelTime.setText(DateTime.strftime('%H:%M:%S'))

    def loaddata(self): # Lấy dữ liệu từ database và hiển thị ra mà hình
        datenow = datetime.datetime.now().strftime('%d/%m/%Y') #giá trị ngày 
        conn = sqlite3.connect(data_dir) #tạo kết nối database
        sqlstr = 'SELECT ID,NAME,TIMEIN,TIMEOUT FROM chamcong WHERE DATE = ?'
        result = conn.execute(sqlstr,(datenow,)) # lấy ra giá trị ID,NAME,TIMEIN,TIMEOUT của ngày hôm nay
        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number,column_number,QTableWidgetItem(str(data)))

    def face_rec_cam(self):
        MINSIZE = 20
        THRESHOLD = [0.6, 0.7, 0.7]
        FACTOR = 0.709
        INPUT_IMAGE_SIZE = 160
        CLASSIFIER_PATH = 'Models/facemodel.pkl'
        FACENET_MODEL_PATH = 'Models/20180402-114759.pb'

        # Tải trình phân loại tùy chỉnh
        with open(CLASSIFIER_PATH, 'rb') as file:
            model, class_names = pickle.load(file)
        print("Custom Classifier, Successfully loaded")

        with tf.Graph().as_default():
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
            sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))

            with sess.as_default():

                # Load the model
                print('Loading feature extraction model')
                facenet.load_model(FACENET_MODEL_PATH)

                # Get input and output tensors
                images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
                embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
                phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
                embedding_size = embeddings.get_shape()[1]

                pnet, rnet, onet = detect_face.create_mtcnn(sess,"")

                # people_detected = set()
                person_detected = collections.Counter()

                cap  = VideoStream(src=0).start()
                
                while (True):
                    frame = cap.read()
                    frame = cv2.resize(frame, (640,480))
                    frame = cv2.flip(frame, 1)
                    
                    bounding_boxes, _ = detect_face.detect_face(frame, MINSIZE, pnet, rnet, onet, THRESHOLD, FACTOR)
                    faces_found = bounding_boxes.shape[0]
                    try:
                        if faces_found > 1:
                            cv2.putText(frame, "Only one face", (0, 100), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                        1, (255, 255, 255), thickness=1, lineType=2)
                        elif faces_found > 0:
                            det = bounding_boxes[:, 0:4]
                            bb = np.zeros((faces_found, 4), dtype=np.int32)
                            for i in range(faces_found):
                                bb[i][0] = det[i][0]
                                bb[i][1] = det[i][1]
                                bb[i][2] = det[i][2]
                                bb[i][3] = det[i][3]
                                # print(bb[i][3]-bb[i][1])
                                # print(frame.shape[0])
                                # print((bb[i][3]-bb[i][1])/frame.shape[0])
                                if (bb[i][3]-bb[i][1])/frame.shape[0]>0.25:
                                    # Cat phan khuon mat tim duoc
                                    cropped = frame[bb[i][1]:bb[i][3], bb[i][0]:bb[i][2], :]
                                    scaled = cv2.resize(cropped, (INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE),
                                                        interpolation=cv2.INTER_CUBIC)
                                    scaled = facenet.prewhiten(scaled)
                                    scaled_reshape = scaled.reshape(-1, INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE, 3)
                                    feed_dict = {images_placeholder: scaled_reshape, phase_train_placeholder: False}
                                    emb_array = sess.run(embeddings, feed_dict=feed_dict)

                                    # Dua vao model de classifier
                                    predictions = model.predict_proba(emb_array)
                                    best_class_indices = np.argmax(predictions, axis=1)
                                    best_class_probabilities = predictions[
                                        np.arange(len(best_class_indices)), best_class_indices]

                                    # Lay ra ten va ty le % cua class co ty le cao nhat
                                    best_name = class_names[best_class_indices[0]]

                                    if best_class_probabilities > 0.75:
                                        # vẽ khung ảnh màu xanh khuôn mạt
                                        cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (0, 255, 0), 2)
                                        text_x = bb[i][0]
                                        text_y = bb[i][3] + 20
                                        name = class_names[best_class_indices[0]]
                                        # viết tên và accuracy lên dưới khung ảnh khuôn mặt
                                        cv2.putText(frame, name, (text_x, text_y), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                                    1, (255, 255, 255), thickness=1, lineType=2)
                                        cv2.putText(frame, str(round(best_class_probabilities[0], 3)), (text_x, text_y + 17),
                                                    cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                                    1, (255, 255, 255), thickness=1, lineType=2)
                                        person_detected[best_name] += 1

                                        ids = best_name.split()[0]
                                        Name =  best_name.split()[1]
                                        ids = int(ids)
                                        
                                        print("ID, Name: {}, Probability: {}".format(best_name, best_class_probabilities))
                                        datenow = datetime.datetime.now().strftime('%d/%m/%Y')
                                        timenow = datetime.datetime.now().strftime('%H:%M:%S')
                                        # Thêm dữ liệu vào database
                                        conn = None
                                        conn = sqlite3.connect(data_dir)
                                        q = "select * from chamcong where ID=? and DATE=?"
                                        cur=conn.execute(q,(ids,datenow))
                                        print(cur)
                                        isRecord =0
                                        timess=0
                                        for i in cur:
                                            isRecord += 1
                                        print(isRecord)
                                        if isRecord == 0:
                                            conn = sqlite3.connect(data_dir)
                                            query = "INSERT INTO chamcong(ID,NAME,DATE,TIMEIN) VALUES (?, ?, ?, ?)"
                                            conn.execute(query, (ids,Name,datenow,timenow))
                                            conn.commit()
                                        else:
                                            if isRecord % 2 == 1:
                                                conn = sqlite3.connect(data_dir)
                                                sqlstr = 'SELECT * FROM chamcong WHERE DATE = ? and ID = ? and SOLAN = ?'
                                                cur = conn.execute(sqlstr,(datenow,ids,isRecord))
                                                rows = cur.fetchall() # rows gồm các giá trị ID,NAME,DATE,TIMEIN,TIMEOUT,SOLAN
                                                # rows[0][3] là giá trị tại TIMEIN. vd: "15:45:06"
                                                # rows[0][3].slip(":") = (15,45,06)
                                                hourin = rows[0][3].split(":")[0] #giá trị giờ 
                                                minutesin = rows[0][3].split(":")[1] #giá trị phút
                                                hournow = datetime.datetime.now().strftime('%H') # giờ hiện tại
                                                minutesnow = datetime.datetime.now().strftime('%M') # phút hiện tại
                                                timess = 60*(int(hournow)-int(hourin)) + (int(minutesnow)-int(minutesin))
                                                print(hournow,hourin,minutesnow,minutesin)
                                                print(timess)
                                                #khoảng thời gian từ thời gian hiệu tại đến thời gian điểm danh trước
                                                if timess > TIME_DELAY: #nếu nó lớn hơn TIME_DElAY
                                                    #Thêm thời gian hiện tại vào TIMEOUT
                                                    query = "INSERT INTO chamcong(ID,NAME,DATE,TIMEOUT,SOLAN) VALUES (?, ?, ?, ?,?)"
                                                    conn.execute(query, (ids,Name,datenow,timenow,isRecord+1))
                                                    conn.commit()
                                                    conn.close()
                                            else:
                                                conn = sqlite3.connect(data_dir)
                                                sqlstr = 'SELECT * FROM chamcong WHERE DATE = ? and ID = ? and SOLAN = ?'
                                                cur = conn.execute(sqlstr,(datenow,ids,isRecord))
                                                rows = cur.fetchall()
                                                hourin = rows[0][4].split(":")[0]
                                                minutesin = rows[0][4].split(":")[1]
                                                hournow = datetime.datetime.now().strftime('%H')
                                                minutesnow = datetime.datetime.now().strftime('%M')
                                                timess = 60*(int(hournow)-int(hourin)) + (int(minutesnow)-int(minutesin))
                                                if timess > TIME_DELAY:
                                                    query = "INSERT INTO chamcong(ID,NAME,DATE,TIMEIN,SOLAN) VALUES (?, ?, ?, ?,?)"
                                                    conn.execute(query, (ids,Name,datenow,timenow,isRecord+1))
                                                    conn.commit()
                                                    conn.close()
                                    else:
                                        cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (0, 255, 0), 2)
                                        text_x = bb[i][0]
                                        text_y = bb[i][3] + 20
                                        name = "Unknown"
                                        cv2.putText(frame, name, (text_x, text_y), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                                    1, (255, 255, 255), thickness=1, lineType=2)
                                        cv2.putText(frame, str(round(best_class_probabilities[0], 3)), (text_x, text_y + 17),
                                                    cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                                    1, (255, 255, 255), thickness=1, lineType=2)
                                        person_detected[name] += 1
                    except:
                        pass
                    self.displayImage(frame)
                    cv2.waitKey()         
def main():
    app = QApplication(sys.argv)
    main_win = Main_attendance()
    main_win.show()
    try:
        sys.exit(app.exec_())
    except:
	    print('exciting')
    
if __name__ == "__main__":
    main()