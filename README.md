# -8puzzel-solver

#Đồ Án Cá Nhân - môn Trí Tuệ Nhân Tạo ()

#1. Mục Tiêu

Đồ án này hướng tới việc phát triển một công cụ giải bài tự game 8-Puzzle bằng cách tích hợp một loạt các thuật toán tìm kiếm, từ những phương pháp cơ bản đến các kỹ thuật nâng cao. Mục tiêu chính là phân tích và so sánh hiệu suất cũng như ưu, nhược điểm của từng thuật toán khi áp dụng vào bài toán, đồng thời cung cấp một giao diện trực quan để người dùng có thể dễ dàng nhập dữ liệu, tương tác và quan sát quá trình giải quyết bài toán một cách sinh động.

#2. Nội Dung
  #2.1. Các Thuật Toán Tìm kiếm không có thông tin (Uninformed Search):
  
  Thành phần chính của bài toán:
  Trạng thái ban đầu: Ma trận 3x3 chứa các số từ 1-8 và ô trống.
  Trạng thái mục tiêu: Ma trận đã sắp xếp theo thứ tự tăng dần với ô trống ở góc dưới cùng.
  Hành động: Di chuyển ô trống lên, xuống, trái, phải.
  Solution: Chuỗi các bước di chuyển để đưa từ trạng thái ban đầu về trạng thái mục tiêu.
  
  Các thuật toán được triển khai bao gồm:
  
    BFS (Breadth-First Search): Duyệt qua tất cả trạng thái theo từng lớp, đảm bảo tìm ra lời giải ngắn nhất nhưng tốn nhiều bộ nhớ.
  ![Image](https://github.com/user-attachments/assets/52a4e8ac-2b50-43a5-bde5-ff1b0c488b04)
  
    DFS (Tìm kiếm theo chiều sâu): Đi sâu vào một nhánh, có thể nhanh trong một số trường hợp nhưng không đảm bảo tối ưu.
![Image](https://github.com/user-attachments/assets/afc327cd-e959-4055-95a6-30b8cd7db28a)
    
    
    UCS (Tìm kiếm đồng nhất): Ưu tiên đường đi có chi phí thấp nhất, phù hợp cho bài toán có trọng số.
![Image](https://github.com/user-attachments/assets/425335f0-5e10-4c2b-ade8-db352a59e6e7)

  ID (Iterative Deepening)
  ![Image](https://github.com/user-attachments/assets/118fb62b-b0c3-43af-910d-db4ddab8d314)
  
  Nhận xét hiệu suất:
  BFS luôn tìm được lời giải tối ưu nhưng đòi hỏi nhiều tài nguyên do mở rộng nhiều trạng thái.
  DFS nhanh hơn trong một số trường hợp nhưng dễ mắc kẹt trong nhánh vô hạn.
  UCS cân bằng giữa thời gian và bộ nhớ nhưng kém hiệu quả hơn so với các thuật toán heuristic.
  
  #2.2. Các Thuật Toán Tìm Kiếm Có Thông Tin
  Thành phần chính:
  Hàm heuristic: Sử dụng khoảng cách Manhattan hoặc số ô sai vị trí để ước lượng chi phí.

  Các thuật toán được triển khai bao gồm:
  A*: Kết hợp chi phí thực tế và heuristic, đảm bảo tối ưu và hiệu quả.
  ![Image](https://github.com/user-attachments/assets/ca8d8b1c-67af-44ca-b529-d0455f6bc8bf)
  
  Greedy: Chọn hành động dựa trên heuristic, nhanh nhưng không đảm bảo tối ưu.
  ![Image](https://github.com/user-attachments/assets/453eed3b-2536-478c-b081-78ef5db1bfc7)
  
  IDA* (Iterative Deepening A): Cải tiến của A để tiết kiệm bộ nhớ bằng cách giới hạn độ sâu.
  ![Image](https://github.com/user-attachments/assets/ce93f88c-94de-4f9b-8cbe-196935b3873a)

  AO*: Tối ưu cho bài toán AND-OR với cây tìm kiếm động.
![Image](https://github.com/user-attachments/assets/263f3db5-c94e-4680-92c1-788b4d670f6c)
  
  Search with No Observation
  ![Image](https://github.com/user-attachments/assets/0e53eb14-54d6-4319-9082-a9fd41beb62b)
  
  Nhận xét hiệu suất:
  A* và IDA* cho kết quả chính xác và nhanh hơn BFS/DFS nhờ heuristic.
  Greedy có tốc độ nhanh nhưng dễ bị lệch hướng do chỉ tập trung vào heuristic.
  
  #2.3. Các Thuật Toán Tìm kiếm cục bộ (Local Search):
  Steepest Hill Climbing: Tối ưu cục bộ bằng cách leo đồi, dễ mắc kẹt ở cực đại địa phương.
  ![Image](https://github.com/user-attachments/assets/e9dd00cc-73c8-4fe6-982f-7a5f7770f2b5)

  Simple Hill Climbing
  ![Image](https://github.com/user-attachments/assets/556856ce-462b-4cdc-b880-a8c63db26102)
  
  Stochastic Hill Climbing
  ![Image](https://github.com/user-attachments/assets/d6223947-5ead-4f13-8278-1dd2edcd9313)
  
  Simulated Annealing: Sử dụng nhiệt độ ảo để chấp nhận bước đi xấu, tránh cực đại địa phương.
  ![Image](https://github.com/user-attachments/assets/171a1257-ebc8-45ba-a61d-5b211fda76ce)
    
    Nhận xét:
  Local Search hiệu quả với không gian nhỏ nhưng thiếu tính ổn định.
  
  #2.4. Tìm kiếm trong môi trường phức tạp (Complex Environment Search)
  Partially Observable
  ![Image](https://github.com/user-attachments/assets/3dc1aed9-8bb8-4525-8fba-ee7a63417460)
  
  #2.5.Tìm kiếm với ràng buộc (Constraint Satisfaction Problems - CSPs):
  Backtracking: Thử-sai và quay lui, phù hợp cho bài toán với ràng buộc.
  ![Image](https://github.com/user-attachments/assets/b11b69e8-088a-43b6-bebc-b030c42e4d26)
  
  #2.6. Học tăng cường được thể hiện qua Q-Learning, một phương pháp học cách chọn hành động tối ưu thông qua thử và sai.
  
  Q-Learning: Học chính sách tối ưu thông qua phần thưởng, phù hợp cho môi trường không xác định.
  ![Image](https://github.com/user-attachments/assets/bbe2f6ea-4228-4975-911a-59b2a036b196)
  Nhận xét:
  Q-Learning cần thời gian huấn luyện dài nhưng linh hoạt trong môi trường phức tạp.
  

  
   
#3. Kết Luận
Dự án đã triển khai thành công 16 thuật toán tìm kiếm khác nhau cho bài toán 8-puzzle, bao gồm cả phương pháp cổ điển và hiện đại. Ứng dụng cung cấp giao diện trực quan, cho phép người dùng quan sát quá trình di chuyển ô số và so sánh hiệu suất thông qua các chỉ số như số nút mở rộng, thời gian thực thi. Kết quả cho thấy các thuật toán heuristic (A, IDA) vượt trội về tốc độ, trong khi Q-Learning và AO* phù hợp cho bài toán phức tạp hơn.

#Tài Liệu Tham Khảo
Code tham khảo ý tưởng từ các nguồn mở về AI, đặc biệt là cách triển khai heuristic cho 8-puzzle:
Solving 8-Puzzle using A* Algorithm
Q-Learning for Puzzle Games
