# Time-attendance-by-faceregnition-MTCNN-Facenet-PyQt5

Bước 1: Cài đặt môi trường ảo 
	Cài Anaconda3: chạy 'Anaconda3-2020.07-Windows-x86_64.exe' trong foder Anaconda để setup
	=> Tạo môi trường: vào cmd chạy lệnh: conda create --name facerecognition python=3.7
	=> chạy tiếp lệnh: conda activate facerecognition 
	=> trỏ đến thư mục Facerecognition (TẤT CẢ CÁC LỆNH SAU ĐỀU CHẠY Ở ĐÂY)
	"""lúc đấy cmd sẽ hiện như này:(facerecognition) D:\CODE\Code Python\cham_cong\Facerecognition>"""
	=>chạy lệnh: pip install -r requirements.txt để cài các thư viện cần thiết
Tải dữ liệu pretrain của Facenet về máy:

Các bạn tải weights pretrain về tại link này : https://drive.google.com/file/d/1EXPBSXwTaqrSC0OhUdXNmKSh9qJUQ55-/view
Sau khi tải xong về, các bạn copy toàn bộ file tải về vào thư mục Models
![image](https://user-images.githubusercontent.com/107174075/199404818-58783590-207e-4d0e-aa3a-b1d7dd9cf58c.png)

Bước 2: Chạy chương trình
	chạy file main_attendance.py nha. 
