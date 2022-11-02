from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import *
import sqlite3


import main_register
import main_get_data

database_dir = './Dataset/data.db'

class Main_login(QDialog):
    def __init__(self):
        super(Main_login, self).__init__()
        loadUi('GUI/ui_login.ui',self)
        self.pushButton_2.clicked.connect(self.checkAccount)
        self.pushButton.clicked.connect(self.show_main_register)

    def show_main_register(self):
        a = main_register.Main_register()
        a.exec_()
    
    def show_main_getData(self):
        b = main_get_data.Main_getdata()
        b.exec_()

    def checkAccount(self):
        user_name = self.lineEdit.text()
        password = self.lineEdit_2.text()
        while True:
            if not user_name.strip():
                QMessageBox.warning(self, "THÔNG BÁO","Vui lòng nhập tên đăng nhập")
                break
            elif " " in user_name:
                QMessageBox.warning(self, "THÔNG BÁO","Tên đăng nhập không được chứa khoảng trắng")
                break
            elif not password.strip() :
                QMessageBox.warning(self, "THÔNG BÁO","Vui lòng nhập mật khẩu")
                break
            elif " " in user_name:
                QMessageBox.warning(self, "THÔNG BÁO","Mật khẩu không được chứa khoảng trắng")
                break
            elif self.checkDB(user_name,password) == True:
                self.close()
                self.show_main_getData()
                break
            else:
                QMessageBox.warning(self, "THÔNG BÁO","Tài khoản không chính xác")
                break
                

    def checkDB(self,name,password):
        conn = sqlite3.connect(database_dir)
        query = "SELECT * FROM account WHERE USERNAME = ? and PASSWORD = ? "
        cusror = conn.execute(query,(name,password))
        for row in cusror:
            conn.close()
            return True

def main():
    import sys
    app = QApplication(sys.argv)
    main_win = Main_login()
    main_win.show()
    try:
        sys.exit(app.exec_())
    except:
	    print('exciting')
    
if __name__ == "__main__":
    main()