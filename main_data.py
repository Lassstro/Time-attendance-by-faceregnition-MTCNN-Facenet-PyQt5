import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import sys

data_dir = './Dataset/data.db'

class Main_data(QDialog):
    def __init__(self):
        super(Main_data, self).__init__()
        loadUi('GUI/ui_data.ui',self)
        self.loaddata()

    def loaddata(self):
        conn = sqlite3.connect(data_dir)
        sqlstr = 'SELECT * FROM chamcong'
        result = conn.execute(sqlstr)
        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number,column_number,QTableWidgetItem(str(data)))
def main():
    app = QApplication(sys.argv)
    main_win = Main_data()
    main_win.show()
    try:
        sys.exit(app.exec_())
    except:
	    print('exciting')
    
if __name__ == "__main__":
    main()