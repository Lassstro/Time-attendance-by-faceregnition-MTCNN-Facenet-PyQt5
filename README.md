# Time-attendance-by-faceregnition-MTCNN-Facenet-PyQt5

Mô tả:
Một trình quản lí nhân viên CRUD cơ bản, có thêm chức năng chấm công hằng ngày bằng nhận diện khuôn mặt
- Backend: Python
- FontEnd: Qt5
- Database: SQLite

Bước 1: Cài đặt môi trường ảo 

	Cài Anaconda3: chạy 'Anaconda3-2020.07-Windows-x86_64.exe'
	
	=> Tạo môi trường: vào cmd chạy lệnh: conda create --name facerecognition python=3.7
	
	=> chạy tiếp lệnh: conda activate facerecognition 
	
	=> trỏ đến thư mục Facerecognition (TẤT CẢ CÁC LỆNH SAU ĐỀU CHẠY Ở ĐÂY)
	
	"""lúc đấy cmd sẽ hiện như này:(facerecognition) D:\CODE\Code Python\cham_cong\Facerecognition>"""
	
	=>chạy lệnh: pip install -r requirements.txt để cài các thư viện cần thiết
	
Bước 2: Tải dữ liệu pretrain của Facenet về máy:

	Các bạn tải weights pretrain về tại link này : https://drive.google.com/file/d/1EXPBSXwTaqrSC0OhUdXNmKSh9qJUQ55-/view

	Sau khi tải xong về, các bạn copy toàn bộ file tải về vào thư mục Models
![image](https://user-images.githubusercontent.com/107174075/199404818-58783590-207e-4d0e-aa3a-b1d7dd9cf58c.png)

Bước 3: Chạy chương trình

chạy file main_attendance.py nha. 
	
![image](https://user-images.githubusercontent.com/107174075/199405487-5156a3f8-74db-448e-8e0a-57cbe880fb4c.png)
 
 click xem chi tiết sẽ hiển thị data chi tiết
 
 ![image](https://user-images.githubusercontent.com/107174075/199405624-de33432e-2df7-42ee-a88e-c0ddacbbde88.png)

Thêm nhân viên bằng cách lấy mẫu ảnh từ camera hoặc thêm ảnh từ folder máy tính

![image](https://user-images.githubusercontent.com/107174075/199406061-0223ca8e-6fab-4415-b288-0f42759fd1d0.png)

Demo sơ sơ nên nó hơi cùi mía, mọi người thông cảm :))
