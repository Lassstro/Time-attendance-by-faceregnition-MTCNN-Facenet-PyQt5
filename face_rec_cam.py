from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from imutils.video import VideoStream
import sqlite3
import datetime

import facenet
import pickle
import detect_face
import numpy as np
import cv2
import collections
from sklearn.svm import SVC


def face_rec_cam():
        MINSIZE = 20
        THRESHOLD = [0.6, 0.7, 0.7]
        FACTOR = 0.709
        IMAGE_SIZE = 182
        INPUT_IMAGE_SIZE = 160
        CLASSIFIER_PATH = 'Models/facemodel.pkl'
        FACENET_MODEL_PATH = 'Models/20180402-114759.pb'
        data_dir = './Dataset/data.db'

        # Load The Custom Classifier
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
                            
                                    if best_class_probabilities > 0.8:
                                        
                                        # Ve khung mau xanh quanh khuon mat
                                        cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (0, 255, 0), 2)
                                        text_x = bb[i][0]
                                        text_y = bb[i][3] + 20

                                        name = class_names[best_class_indices[0]]
                                        cv2.putText(frame, name, (text_x, text_y), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                                    1, (255, 255, 255), thickness=1, lineType=2)
                                        cv2.putText(frame, str(round(best_class_probabilities[0], 3)), (text_x, text_y + 17),
                                                    cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                                    1, (255, 255, 255), thickness=1, lineType=2)
                                        person_detected[best_name] += 1 
                                        ids = best_name.split()[0]
                                        a =  best_name.split()[1]
                                        ids = int(ids)
                                        print( "ID,Name: {}, Probability: {}".format(best_name, best_class_probabilities))
                                        datenow = datetime.datetime.now().strftime('%d/%m/%Y')
                                        timenow = datetime.datetime.now().strftime('%H:%M:%S')
                                        conn = None
                                        conn = sqlite3.connect(data_dir)
                                        q="select * from chamcong where ID=? and DATE=?"
                                        curr=conn.execute(q,(ids,datenow))
                                        isRecord=0
                                        for i in curr:
                                            isRecord=1
                                        if isRecord==0:
                                            cur = conn.cursor()
                                            query = "INSERT INTO chamcong VALUES (?, ?, ?, ?) "
                                            cur.execute(query, (ids,a,datenow,timenow))
                                            conn.commit()

                                            cur.execute("SELECT * FROM nhanvien WHERE ID=?", (ids,))
                                            rows = cur.fetchall()
                                            socong = int(rows[0][2])
                                            socong = socong + 1
                                
                                            a = "UPDATE nhanvien SET SOCONG = ? WHERE ID=?"
                                            cur.execute(a,(socong,ids))
                                            conn.commit()
                                            conn.close()               
                                    else:
                                        name = "Unknown"
                    except:
                        pass
                    cv2.waitKey(1)
                    cv2.imshow('Face Recognition', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                cap.release()
                cv2.destroyAllWindows()
face_rec_cam()
