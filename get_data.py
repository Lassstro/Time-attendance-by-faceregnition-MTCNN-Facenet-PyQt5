import os
from utils import *
from datetime import datetime
import cv2
import sqlite3

a = os.path.dirname(os.path.abspath(__file__)) + '\\data.db'

def insertOrUpdate(ID, Name):

    conn = sqlite3.connect(a)
    query = "SELECT * FROM people WHERE ID =" +str(ID)
    cusror = conn.execute(query)
    # Kiểm tra ID đã tồn tại chưa
    isRecordExist = 0
    for row in cusror:
        isRecordExist = 1
    if(isRecordExist == 0):
        query = "INSERT INTO people(ID, Name) VALUES(" + \
            str(ID) + ", '"+str(Name) + "')"
    else:
        query = "UPDATE people SET Name='"+str(Name)+"' WHERE ID="+str(ID)
    conn.execute(query)
    conn.commit()
    conn.close()

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            return directory
    except OSError:
        print ('Error: Creating directory. ' +  directory)
        return directory

def creatImage(direc):
    name = input('Khai báo tên nhân viên: ')
    path = createFolder(direc+f'{name}')
    if path is None:
       path=PATH+f'{name}'
    return path

PATH = './Dataset/Facedata/raw/'

def get_data():
    path=creatImage(PATH)
    vc = cv2.VideoCapture(0)
    while True:
        ret, frame = vc.read()
        if not ret:
            print('Not frame')
            break
        cv2.imshow('camera', frame)
        ch=cv2.waitKey(1)
        if ch == 13: #nhấn enter
            cv2.imshow("image",frame)
            cv2.imwrite(path+ "/"+f"{datetime.now().strftime('%d_%m_%y')}"+f"__{datetime.now().strftime('%H_%M_%S')}"+".jpg",frame)
        # elif ch == 27: #nhấn esc
        # path=creatImage(PATH)
        if(ch & 0xFF == ord('q')):
            break
    vc.release()
    cv2.destroyAllWindows()
    
