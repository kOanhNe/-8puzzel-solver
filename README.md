# -8puzzel-solver

# Bài Tập Cá Nhân - môn Trí Tuệ Nhân Tạo (ARIN330585)

# 1. Mục Tiêu

Đồ án này hướng tới việc phát triển một công cụ giải bài tự game 8-Puzzle bằng cách tích hợp một loạt các thuật toán tìm kiếm, từ những phương pháp cơ bản đến các kỹ thuật nâng cao. Mục tiêu chính là phân tích và so sánh hiệu suất cũng như ưu, nhược điểm của từng thuật toán khi áp dụng vào bài toán xem thử thuật toán nào tối ưu cũng như hiệu quả hơn, đồng thời cung cấp một giao diện trực quan để người dùng có thể dễ dàng nhập dữ liệu, tương tác và quan sát quá trình giải quyết bài toán một cách sinh động.

# 2. Nội Dung
  #2.1. Các Thuật Toán Tìm kiếm không có thông tin (Uninformed Search):
  
  Thành phần chính của bài toán:
  Trạng thái ban đầu: Ma trận 3x3 chứa các số từ 1-8 và ô trống.
  Trạng thái mục tiêu: Ma trận đã sắp xếp theo trạng thái mục tiêu (trạng thái đích) có thể chỉnh sửa tùy vào người muốn.
  Hành động: Di chuyển ô trống lên, xuống, trái, phải.
  Solution: Chuỗi các bước di chuyển để đưa từ trạng thái ban đầu về trạng thái mục tiêu.
  
  Các thuật toán được triển khai bao gồm:
  
    BFS (Breadth-First Search): Thuật toán này duyệt qua tất cả các trạng thái theo từng lớp, đảm bảo tìm ra lời giải ngắn nhất. Tuy nhiên, nó đòi hỏi lượng bộ nhớ lớn do phải lưu trữ nhiều trạng thái cùng lúc. Hình ảnh minh họa cho thấy BFS mở rộng đều các hướng, nhưng tốc độ chậm khi không gian trạng thái mở rộng.
    
  ![Image](https://github.com/user-attachments/assets/52a4e8ac-2b50-43a5-bde5-ff1b0c488b04)
  
    DFS (Tìm kiếm theo chiều sâu): DFS đi sâu vào một nhánh cụ thể, có thể nhanh chóng tìm ra lời giải trong một số trường hợp. Tuy nhiên, thuật toán này không đảm bảo tính tối ưu và dễ mắc kẹt trong các nhánh vô hạn nếu không giới hạn độ sâu.
    
![Image](https://github.com/user-attachments/assets/afc327cd-e959-4055-95a6-30b8cd7db28a)
    
    
    UCS (Tìm kiếm đồng nhất): Phương pháp này ưu tiên các đường đi có chi phí thấp nhất, phù hợp khi các bước di chuyển có trọng số khác nhau. Dù vậy, UCS kém hiệu quả hơn so với các thuật toán sử dụng heuristic do thiếu định hướng rõ ràng.
    
![Image](https://github.com/user-attachments/assets/425335f0-5e10-4c2b-ade8-db352a59e6e7)

  ID (Iterative Deepening - Tìm Kiếm Lặp Sâu):Kết hợp ưu điểm của BFS và DFS, ID tăng dần giới hạn độ sâu để cân bằng giữa bộ nhớ và thời gian. Tuy nhiên, việc lặp lại các bước tìm kiếm khiến thuật toán chậm hơn đáng kể.
  
  ![Image](https://github.com/user-attachments/assets/118fb62b-b0c3-43af-910d-db4ddab8d314)
  
  Nhận xét hiệu suất:
  BFS luôn tìm được lời giải tối ưu nhưng đòi hỏi nhiều tài nguyên. Trong khi đó, DFS phù hợp cho các bài toán có lời giải nằm gần trạng thái ban đầu, nhưng không đảm bảo hiệu quả trong mọi trường hợp. UCS và ID là lựa chọn trung gian, nhưng vẫn kém linh hoạt so với phương pháp heuristic.
  
  #2.2. Các Thuật Toán Tìm Kiếm Có Thông Tin
  Các thuật toán này sử dụng hàm heuristic (như khoảng cách Manhattan hoặc số ô sai vị trí) để ước lượng chi phí từ trạng thái hiện tại đến mục tiêu, từ đó định hướng tìm kiếm hiệu quả hơn.

  Các thuật toán được triển khai bao gồm:
  A*: Kết hợp giữa chi phí thực tế và heuristic, A đảm bảo tìm ra lời giải tối ưu nếu heuristic được thiết kế chính xác. Hình ảnh minh họa cho thấy thuật toán tập trung vào các hướng có triển vọng, giảm thiểu số trạng thái cần xét.
  
  ![Image](https://github.com/user-attachments/assets/ca8d8b1c-67af-44ca-b529-d0455f6bc8bf)
  
  Greedy: Chỉ dựa trên heuristic, Greedy nhanh chóng hội tụ về mục tiêu nhưng không đảm bảo tính tối ưu. Trong một số trường hợp, thuật toán này có thể đi lạc vào các nhánh không mong muốn do bỏ qua chi phí thực tế.
  
  ![Image](https://github.com/user-attachments/assets/453eed3b-2536-478c-b081-78ef5db1bfc7)
  
  IDA* (Iterative Deepening A): Phiên bản cải tiến của A với việc giới hạn độ sâu, IDA* tiết kiệm bộ nhớ hơn nhưng chậm hơn do phải lặp lại quá trình tìm kiếm.
  
  ![Image](https://github.com/user-attachments/assets/ce93f88c-94de-4f9b-8cbe-196935b3873a)

  AO*: Được thiết kế cho bài toán AND-OR, AO xây dựng cây tìm kiếm động và tối ưu hóa quá trình quyết định. Tuy nhiên, việc triển khai phức tạp và đòi hỏi cấu trúc dữ liệu tinh vi nên tôi chỉ có thể hiển thị vài bước bằng cây.
  
![Image](https://github.com/user-attachments/assets/263f3db5-c94e-4680-92c1-788b4d670f6c)
  
  Search with No Observation
  
  ![Image](https://github.com/user-attachments/assets/0e53eb14-54d6-4319-9082-a9fd41beb62b)
  
  Nhận xét hiệu suất:
Nhận xét:
A* và IDA* vượt trội nhờ khả năng cân bằng giữa hiệu suất và tối ưu. Trong khi đó, Greedy phù hợp cho các bài toán yêu cầu tốc độ nhưng chấp nhận rủi ro về độ chính xác. AO* tỏ ra hiệu quả trong môi trường đa tác tử hoặc có cấu trúc phân nhánh phức tạp.
  
  #2.3. Các Thuật Toán Tìm kiếm cục bộ (Local Search):
  Phương pháp này tập trung vào việc tối ưu hóa từng bước di chuyển dựa trên trạng thái hiện tại, thay vì khám phá toàn bộ không gian tìm kiếm.
  
  Steepest Hill Climbing: Luôn chọn bước đi tốt nhất trong các láng giềng, nhưng dễ mắc kẹt ở cực đại địa phương nếu không có đường đi lên dốc.
  
  ![Image](https://github.com/user-attachments/assets/e9dd00cc-73c8-4fe6-982f-7a5f7770f2b5)

  Simple Hill Climbing
  
  ![Image](https://github.com/user-attachments/assets/556856ce-462b-4cdc-b880-a8c63db26102)
  
  Stochastic Hill Climbing: Chọn ngẫu nhiên một bước đi tốt hơn trạng thái hiện tại, giúp tránh các điểm tối ưu cục bộ.
  
  ![Image](https://github.com/user-attachments/assets/d6223947-5ead-4f13-8278-1dd2edcd9313)
  
  Simulated Annealing: Mô phỏng quá trình ủ kim loại, thuật toán chấp nhận các bước đi xấu với xác suất giảm dần theo thời gian. Phương pháp này linh hoạt và hiệu quả trong việc thoát khỏi cực đại địa phương.
  ![Image](https://github.com/user-attachments/assets/171a1257-ebc8-45ba-a61d-5b211fda76ce)
    
    Nhận xét:
  Local Search hiệu quả với không gian nhỏ nhưng thiếu tính ổn định, phù hợp cho bài toán có không gian tìm kiếm rộng nhưng yêu cầu tốc độ. Tuy nhiên, chúng không đảm bảo tìm ra lời giải tối ưu toàn cục và phụ thuộc nhiều vào trạng thái khởi tạo.
  
  #2.4. Tìm kiếm trong môi trường phức tạp (Complex Environment Search)
  Partially Observable: Trong môi trường không quan sát đầy đủ, thuật toán duy trì một tập các belief states (trạng thái có thể) và cập nhật dựa trên hành động. Phương pháp này đòi hỏi xử lý phức tạp nhưng mô phỏng tốt các tình huống thực tế.
  
  ![Image](https://github.com/user-attachments/assets/3dc1aed9-8bb8-4525-8fba-ee7a63417460)
  
  #2.5.Tìm kiếm với ràng buộc (Constraint Satisfaction Problems - CSPs):
  Backtracking: Thử nghiệm từng bước đi và quay lui khi gặp ràng buộc, phù hợp cho bài toán yêu cầu độ chính xác cao. Tuy nhiên, hiệu suất giảm mạnh khi số biến tăng.
  
  ![Image](https://github.com/user-attachments/assets/b11b69e8-088a-43b6-bebc-b030c42e4d26)
  
  #2.6. Học tăng cường được thể hiện qua Q-Learning, một phương pháp học cách chọn hành động tối ưu thông qua thử và sai.
  
  Q-Learning: Học cách chọn hành động tối ưu thông qua việc thử nghiệm và nhận phần thưởng. Trong 8-Puzzle, phần thưởng được thiết kế dựa trên khoảng cách đến mục tiêu. Hình ảnh minh họa cho thấy quá trình huấn luyện chậm nhưng dần cải thiện theo thời gian.
  
  ![Image](https://github.com/user-attachments/assets/bbe2f6ea-4228-4975-911a-59b2a036b196)
  
  Nhận xét:
  Q-Learning linh hoạt trong môi trường động nhưng đòi hỏi thời gian huấn luyện dài và thiết kế phần thưởng tinh vi.
# 3. Kết Luận
Dự án đã triển khai thành công 16 thuật toán tìm kiếm khác nhau cho bài toán 8-puzzle từ đơn giản (BFS, DFS) đến phức tạp (A*, Q-Learning). Xây dựng giao diện trực quan, cho phép người dùng quan sát quá trình di chuyển ô số và so sánh hiệu suất thông qua các chỉ số như số nút mở rộng, thời gian thực thi đồng thời hỗ trợ chế độ thủ công và tự động. Kết quả cho thấy các thuật toán heuristic (A, IDA) vượt trội về tốc độ, trong khi Local Search phù hợp cho bài toán yêu cầu tốc độ nhưng chấp nhận rủi ro, còn Q-Learning và AO* linh hoạt trong môi trường phức tạp nhưng đòi hỏi tài nguyên tính toán lớn.

Việc lựa chọn hàm heuristic chất lượng và cân nhắc giữa tốc độ - độ chính xác là yếu tố quyết định hiệu suất của thuật toán.

# 4. Hạn chế và Hướng Phát Triển 


# Tài Liệu Tham Khảo
Code tham khảo ý tưởng từ các nguồn mở về AI, đặc biệt là cách triển khai heuristic cho 8-puzzle:

Solving 8-Puzzle using A* Algorithm, ngày truy cập 25/4/2025, link truy cập: https://www.geeksforgeeks.org/8-puzzle-problem-using-branch-and-bound/

Triển khai AO*, ngày truy cập: 25/4/2025, link truy cập:
https://www.researchgate.net/publication/228750393_Federalism_Governance_and_Financial_Reporting_Where_Decentralisation_is_not_Appropriate_in_Regulating_Financial_Accounting

Q-Learning: Sutton & Barto, Reinforcement Learning: An Introduction

Local Search: Russell & Norvig, Artificial Intelligence: A Modern Approach
