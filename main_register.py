
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMessageBox
import sqlite3

database_dir = './Dataset/data.db'

class Main_register(QDialog):
    def __init__(self):
        super(Main_register, self).__init__()
        loadUi('GUI/ui_register.ui',self)
        self.pushButton_2.clicked.connect(self.checkPassword)

    def insert_to_db(self,user_name,password):  
        conn = sqlite3.connect(database_dir)
        query = "INSERT INTO account(USERNAME, PASSWORD) VALUES (?, ?) "
        conn.execute(query,(user_name,password))
        conn.commit()
        conn.close()

    def checkPassword(self):
        user_name = self.lineEdit.text()
        password = self.lineEdit_2.text()
        password_2 = self.lineEdit_3.text()
        while True:
            if not user_name.strip():
                QMessageBox.warning(self, "THÔNG BÁO","Vui lòng nhập tên đăng nhập")
                break
            elif " " in user_name:
                QMessageBox.warning(self, "THÔNG BÁO","Tên đăng nhập không được chứa khoảng trắng")
                break
            elif self.checkDb(user_name)== True:
                QMessageBox.warning(self, "THÔNG BÁO","Tên đăng nhập đã tồn tại")
                break
            elif not password.strip() :
                QMessageBox.warning(self, "THÔNG BÁO","Vui lòng nhập mật khẩu")
                break
            elif " " in password:
                QMessageBox.warning(self, "THÔNG BÁO","Mật khẩu không được chứa khoảng trắng")
                break
            elif  len(password.strip()) < 6:
                QMessageBox.warning(self, "THÔNG BÁO","Nhập mật khẩu lớn hơn 6 kí tự")
                break
            elif not password_2.strip():
                QMessageBox.warning(self, "THÔNG BÁO","Vui lòng xác nhận mật khẩu")
                break
            elif password_2 != password:
                QMessageBox.warning(self, "THÔNG BÁO","Mật khẩu chưa khớp")
                break
            else:
                self.insert_to_db(user_name,password)
                QMessageBox.information(self, "THÔNG BÁO","Đăng kí thành công")
                break
    def checkDb(self,name):
        conn = sqlite3.connect(database_dir)
        query="select * from account where USERNAME = ?"
        curr=conn.execute(query,(name,))
        for i in curr:
            conn.close()
            return True

def main():
    import sys
    app = QApplication(sys.argv)
    main_win = Main_register()
    main_win.show()
    try:
        sys.exit(app.exec_())
    except:
	    print('exciting')
    
if __name__ == "__main__":
    main()