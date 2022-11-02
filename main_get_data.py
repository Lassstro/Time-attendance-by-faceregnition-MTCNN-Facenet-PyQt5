
import sys
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import os.path
import sqlite3
from datetime import datetime
import cv2
from PyQt5.QtGui import QImage,QPixmap

import align_dataset_mtcnn
import classifier


a = os.path.dirname(os.path.abspath(__file__))
database_dir = './Dataset/data.db'
PATH = './Dataset/Facedata/raw/'

class Main_getdata(QDialog):
    def __init__(self):
        super(Main_getdata, self).__init__()
        loadUi('GUI/ui_get_data.ui',self)
        self.logic= 0
        self.n1 = 0
        self.n2=0
        self.pushButton.clicked.connect(self.showCam)
        self.pushButton_2.clicked.connect(self.get_img)
        self.pushButton_3.clicked.connect(self.exittt)
        self.pushButton_4.clicked.connect(self.save_data)
        self.pushButton_5.clicked.connect(self.check)
        self.pushButton_6.clicked.connect(self.getFileNames)
        self.pushButton_7.clicked.connect(self.capnhat)
    
    def exittt(self):
        self.close()

    def capnhat(self):
        align_dataset_mtcnn.main()
        classifier.main()
        QMessageBox.about(self, "Thông báo", "Cập nhật thành công")
    
    # Tạo thư mục chứa dữ liệu ảnh nhân viên
    def createFolder(self,directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                return directory
        except OSError:
            print ('Error: Creating directory. ' +  directory)
            return directory

    def creatImage(self, direc):
        name = self.lineEdit.text()
        id = self.lineEdit_2.text()
        path = self.createFolder(direc+f'{id}'+ f'_{name}')
        if path is None:
            path=PATH+f'{id}'+ f'_{name}'
        return path

    # Kiểm tra thồng tin ID đã có trong database chưa
    def checkDb(self,id):
        conn = sqlite3.connect(database_dir)
        query="select * from nhanvien where ID = ?"
        curr=conn.execute(query,(id,))
        for i in curr:
            conn.close()
            return True

    # Thêm thông tin ID, NAME vào database
    def insert_to_db(self,id,name):  
        conn = sqlite3.connect(database_dir)
        query = "INSERT INTO nhanvien(ID, NAME) VALUES (?, ?) "
        conn.execute(query,(id,name))
        conn.commit()
        conn.close()

    # Kiểm tra thông tin nhân viên nhập vào
    def check_info(self):
        name = self.lineEdit.text()
        id = self.lineEdit_2.text()
        while True:
            if not id.strip():
                QMessageBox.warning(self, "THÔNG BÁO","Vui lòng nhập ID")
                break
            elif " " in id:
                QMessageBox.warning(self, "THÔNG BÁO","ID không được chứa khoảng trắng")
                break
            elif self.checkDb(id)== True:
                QMessageBox.warning(self, "THÔNG BÁO","ID đã tồn tại\nVui lòng nhập ID khác")
                break
            elif not name.strip() :
                QMessageBox.warning(self, "THÔNG BÁO","Vui lòng nhập Tên nhân viên")
                break
            else:
                return True
    def check(self):
        if self.check_info() == True:
            QMessageBox.information(self, "THÔNG BÁO","Thông tin hợp lệ")

    # Chọn ảnh từ bộ nhớ máy để thêm vào dữ liệu nhân viên
    def getFileNames(self):
        if self.check_info() == True:
            id = self.lineEdit_2.text()
            name = self.lineEdit.text()
            path=self.creatImage(PATH)
            response = QFileDialog.getOpenFileNames(
                caption='Chọn ảnh',
                directory = os.getcwd(),
                filter='Images (*.png *.xpm *.jpg)',
                initialFilter='Images (*.png *.xpm *.jpg)')
            for i in range(1,len(response[0])):
                img = cv2.imread(response[0][i])
                self.label_6.setText('Thêm thành công'+f' {i+1} '+'ảnh từ bộ nhớ')
                cv2.imwrite(path+ "/"+f'{id}'+ f'_{name}'+f"_{i}"+".jpg",img)
                self.n1 = i+1

    # Chụp ảnh từ camera để thêm vào dữ liệu nhân viên
    def showCam(self):
        if self.check_info() == True:
            id = self.lineEdit_2.text()
            name = self.lineEdit.text()           
            path=self.creatImage(PATH)
            vc = cv2.VideoCapture(0)
            while True:
                ret, frame = vc.read()
                if not ret:
                    print('Not frame')
                    break
                frame = cv2.resize(frame,(320,240))
                frame = cv2.flip(frame,1)
                self.displayImage(frame)
                cv2.waitKey()
                if (self.logic==2):
                    self.n2+=1
                    self.displayImage_2(frame)
                    cv2.imwrite(path+ "/"+'camera_'+f'{id}'+ f'_{name}'+f"_{self.n2}"+".jpg",frame)
                    self.label_5.setText('Thêm thành công'+f' {self.n2} '+'ảnh từ camera')
                    self.logic = 1
                if self.logic==3:
                    break
               
    def save_data(self):
        if self.check_info() == True:
            n = self.n1+self.n2
            if n>10:
                id = self.lineEdit_2.text()
                name = self.lineEdit.text()
                self.insert_to_db(id,name)
                QMessageBox.question(self, "Thông báo", "Thêm nhân viên thành công",QMessageBox.Yes, QMessageBox.Cancel)
                if QMessageBox.Yes:
                    self.logic=3
            else:
                QMessageBox.information(self, "Thông báo", "Vui lòng chọn trên 10 ảnh")
    def get_img(self):
	    self.logic=2


    def displayImage(self,img):
	    qformat=QImage.Format_RGB888
	    img = QImage(img,img.shape[1],img.shape[0],qformat)
	    img = img.rgbSwapped()
	    self.imgLabel.setPixmap(QPixmap.fromImage(img))

    def displayImage_2(self,img):
	    qformat=QImage.Format_RGB888
	    img = QImage(img,img.shape[1],img.shape[0],qformat)
	    img = img.rgbSwapped()
	    self.imgLabel_2.setPixmap(QPixmap.fromImage(img))

    

def main():
    app = QApplication(sys.argv)
    main_win = Main_getdata()
    main_win.show()
    try:
        sys.exit(app.exec_())
    except:
	    print('exciting')
    
if __name__ == "__main__":
    main()