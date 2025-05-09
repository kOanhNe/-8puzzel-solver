# 8-Puzzle Solver

# Bài Tập Cá Nhân - Môn Trí Tuệ Nhân Tạo (ARIN330585)

# 1. Mục Tiêu

Đồ án này nhằm phát triển một công cụ giải bài toán **8-Puzzle** bằng cách triển khai và so sánh 16 thuật toán tìm kiếm, từ các phương pháp không sử dụng thông tin (uninformed search), có thông tin (informed search), tìm kiếm cục bộ (local search), đến học tăng cường (reinforcement learning). Mục tiêu chính là:
- Phân tích hiệu suất, ưu điểm và nhược điểm của từng thuật toán khi giải bài toán **8-Puzzle**.
- Xác định phương pháp tối ưu nhất về số bước, số trạng thái đã duyệt, và thời gian thực thi.
- Cung cấp giao diện trực quan bằng Pygame để người dùng nhập trạng thái ban đầu, quan sát quá trình giải, và so sánh hiệu suất các thuật toán.

# 2. Nội Dung

## 2.1. Các Thành Phần Chính của Bài Toán

**Thành phần chính:**
- **Trạng thái ban đầu**: Ma trận 3x3 chứa các số từ 1-8 và một ô trống (ký hiệu `_`), ví dụ:
  ```
  [2, 6, 5]
  [_, 8, 7]
  [4, 3, 1]
  ```
- **Trạng thái mục tiêu**: Ma trận đã sắp xếp, ví dụ:
  ```
  [1, 2, 3]
  [4, 5, 6]
  [7, 8, _]
  ```
- **Hành động**: Di chuyển ô trống theo 4 hướng (lên, xuống, trái, phải).
- **Chi phí**: Mỗi bước di chuyển có chi phí là 1.
- **Hàm mục tiêu**: Kiểm tra xem trạng thái hiện tại có khớp với trạng thái mục tiêu hay không.
- **Solution**: Chuỗi các bước di chuyển từ trạng thái ban đầu đến trạng thái mục tiêu.

## 2.2. Các Thuật Toán Tìm Kiếm Không Có Thông Tin (Uninformed Search)

Các thuật toán này không sử dụng thông tin heuristic, dựa hoàn toàn vào cấu trúc không gian trạng thái.

**Thuật toán được triển khai:**
- **Breadth-First Search (BFS)**:
  - **Nguyên lý**: Duyệt tất cả trạng thái theo từng lớp, đảm bảo tìm ra đường đi ngắn nhất.
  - **Ưu điểm**: Luôn tìm được lời giải tối ưu (ít bước nhất).
  - **Nhược điểm**: Tốn nhiều bộ nhớ do lưu trữ tất cả trạng thái ở mỗi độ sâu.
  - **Hình ảnh minh họa**: BFS mở rộng đều các hướng, nhưng chậm khi không gian trạng thái lớn.
  
    ![BFS Illustration](https://github.com/user-attachments/assets/52a4e8ac-2b50-43a5-bde5-ff1b0c488b04)

- **Depth-First Search (DFS)**:
  - **Nguyên lý**: Đi sâu vào một nhánh trước khi quay lại các nhánh khác.
  - **Ưu điểm**: Tiết kiệm bộ nhớ, nhanh nếu lời giải gần trạng thái ban đầu.
  - **Nhược điểm**: Không đảm bảo tối ưu, có thể mắc kẹt ở nhánh dài.
  - **Hình ảnh minh họa**: DFS ưu tiên một hướng, dễ đi lạc.
  
    ![DFS Illustration](https://github.com/user-attachments/assets/afc327cd-e959-4055-95a6-30b8cd7db28a)

- **Uniform Cost Search (UCS)**:
  - **Nguyên lý**: Ưu tiên trạng thái có chi phí thấp nhất.
  - **Ưu điểm**: Tìm được lời giải tối ưu khi chi phí khác nhau.
  - **Nhược điểm**: Chậm hơn BFS nếu không có heuristic.
  - **Hình ảnh minh họa**: UCS mở rộng dựa trên chi phí.
  
    ![UCS Illustration](https://github.com/user-attachments/assets/425335f0-5e10-4c2b-ade8-db352a59e6e7)

- **Iterative Deepening Search (IDS)**:
  - **Nguyên lý**: Lặp lại DFS với giới hạn độ sâu tăng dần.
  - **Ưu điểm**: Kết hợp ưu điểm của BFS (tối ưu) và DFS (tiết kiệm bộ nhớ).
  - **Nhược điểm**: Lặp lại nhiều lần, gây chậm.
  - **Hình ảnh minh họa**: IDS tăng dần độ sâu tìm kiếm.
  
    ![IDS Illustration](https://github.com/user-attachments/assets/118fb62b-b0c3-43af-910d-db4ddab8d314)

**Nhận xét hiệu suất**:
- BFS đảm bảo lời giải tối ưu nhưng tốn bộ nhớ (91,351 trạng thái). DFS nhanh nhưng không tối ưu (45 bước). UCS chậm hơn BFS (6.1250s) và có thể duyệt nhiều trạng thái hơn dự kiến. IDS là lựa chọn trung gian, nhưng lặp lại gây chậm (2.1241s).

## 2.3. Các Thuật Toán Tìm Kiếm Có Thông Tin (Informed Search)

Các thuật toán này sử dụng hàm heuristic (khoảng cách Manhattan) để định hướng tìm kiếm, giảm số trạng thái cần xét.

**Thuật toán được triển khai:**
- **A***:
  - **Nguyên lý**: Kết hợp chi phí thực tế (g(n)) và heuristic (h(n)), đảm bảo tối ưu nếu heuristic hợp lệ.
  - **Ưu điểm**: Hiệu quả cao, giảm số trạng thái duyệt (2,700 trạng thái).
  - **Nhược điểm**: Tốn bộ nhớ cho hàng đợi ưu tiên.
  - **Hình ảnh minh họa**: A* tập trung vào hướng gần mục tiêu.
  
    ![A* Illustration](https://github.com/user-attachments/assets/ca8d8b1c-67af-44ca-b529-d0455f6bc8bf)

- **Greedy Best-First Search**:
  - **Nguyên lý**: Chỉ dựa trên heuristic, ưu tiên trạng thái có h(n) nhỏ nhất.
  - **Ưu điểm**: Nhanh nhất (0.0144s), dễ triển khai.
  - **Nhược điểm**: Không đảm bảo tối ưu (51 bước), dễ mắc kẹt.
  - **Hình ảnh minh họa**: Greedy chọn hướng tốt nhất tại mỗi bước.
  
    ![Greedy Illustration](https://github.com/user-attachments/assets/453eed3b-2536-478c-b081-78ef5db1bfc7)

- **Iterative Deepening A* (IDA*)**:
  - **Nguyên lý**: Kết hợp A* với giới hạn độ sâu, giảm bộ nhớ.
  - **Ưu điểm**: Tiết kiệm bộ nhớ hơn A*, vẫn tối ưu.
  - **Nhược điểm**: Lặp lại nhiều, chậm hơn A* (0.7950s).
  - **Hình ảnh minh họa**: IDA* tăng ngưỡng chi phí dần.
  
    ![IDA* Illustration](https://github.com/user-attachments/assets/ce93f88c-94de-4f9b-8cbe-196935b3873a)

- **AO***:
  - **Nguyên lý**: Xây dựng cây AND-OR cho bài toán phân nhánh phức tạp.
  - **Ưu điểm**: Phù hợp cho môi trường đa tác tử.
  - **Nhược điểm**: Phức tạp, không hiệu quả cho 8-Puzzle.
  - **Hình ảnh minh họa**: AO* tạo cây tìm kiếm động.
  
    ![AO* Illustration](https://github.com/user-attachments/assets/263f3db5-c94e-4680-92c1-788b4d670f6c)

**Nhận xét hiệu suất**:
- A* và IDA* vượt trội nhờ heuristic (Manhattan distance), với A* nhanh nhất (0.0497s). Greedy nhanh nhưng không tối ưu. AO* quá phức tạp, không phù hợp cho 8-Puzzle.

## 2.4. Các Thuật Toán Tìm Kiếm Cục Bộ (Local Search)

Các thuật toán này tối ưu hóa từng bước dựa trên trạng thái hiện tại, không khám phá toàn bộ không gian.

**Thuật toán được triển khai:**
- **Simple Hill Climbing**:
  - **Nguyên lý**: Chọn trạng thái láng giềng tốt hơn hiện tại.
  - **Ưu điểm**: Nhanh, ít tài nguyên.
  - **Nhược điểm**: Dễ mắc kẹt ở cực đại cục bộ.
  - **Hình ảnh minh họa**: Simple HC leo dần nhưng dễ dừng sai.
  
    ![Simple HC Illustration](https://github.com/user-attachments/assets/556856ce-462b-4cdc-b880-a8c63db26102)

- **Steepest Hill Climbing**:
  - **Nguyên lý**: Chọn láng giềng tốt nhất trong tất cả láng giềng.
  - **Ưu điểm**: Ít mắc kẹt hơn Simple HC.
  - **Nhược điểm**: Vẫn không đảm bảo tối ưu.
  - **Hình ảnh minh họa**: Steepest HC chọn hướng tốt nhất.
  
    ![Steepest HC Illustration](https://github.com/user-attachments/assets/e9dd00cc-73c8-4fe6-982f-7a5f7770f2b5)

- **Stochastic Hill Climbing**:
  - **Nguyên lý**: Chọn ngẫu nhiên láng giềng cải thiện trạng thái.
  - **Ưu điểm**: Tránh cực đại cục bộ tốt hơn.
  - **Nhược điểm**: Kết quả không ổn định.
  - **Hình ảnh minh họa**: Stochastic HC chọn ngẫu nhiên.
  
    ![Stochastic HC Illustration](https://github.com/user-attachments/assets/d6223947-5ead-4f13-8278-1dd2edcd9313)

- **Simulated Annealing**:
  - **Nguyên lý**: Chấp nhận trạng thái xấu với xác suất giảm dần.
  - **Ưu điểm**: Thoát khỏi cực đại cục bộ hiệu quả.
  - **Nhược điểm**: Cần tinh chỉnh tham số, không hội tụ trong 8-Puzzle.
  - **Hình ảnh minh họa**: Simulated Annealing linh hoạt hơn HC.
  
    ![Simulated Annealing Illustration](https://github.com/user-attachments/assets/171a1257-ebc8-45ba-a61d-5b211fda76ce)

**Nhận xét hiệu suất**:
- Các thuật toán Hill Climbing (Simple, Steepest, Stochastic) không tìm được lời giải do mắc kẹt ở cực đại cục bộ, dù có khởi động lại. Simulated Annealing không hội tụ do lịch nhiệt độ chưa tối ưu.

## 2.5. Tìm Kiếm Trong Môi Trường Phức Tạp (Complex Environment Search)

**Thuật toán được triển khai:**
- **Partially Observable Search**:
  - **Nguyên lý**: Duy trì tập belief states trong môi trường không quan sát đầy đủ.
  - **Ưu điểm**: Phù hợp cho bài toán thiếu thông tin.
  - **Nhược điểm**: Quá phức tạp cho 8-Puzzle (môi trường xác định).
  - **Hình ảnh minh họa**: Belief states trong môi trường không rõ ràng.
  
    ![Partially Observable Illustration](https://github.com/user-attachments/assets/3dc1aed9-8bb8-4525-8fba-ee7a63417460)

- **Search with No Observation**:
  - **Nguyên lý**: Tìm kiếm mà không dựa vào quan sát môi trường.
  - **Ưu điểm**: Giải bài toán hoàn toàn không có thông tin.
  - **Nhược điểm**: Không phù hợp với 8-Puzzle.
  - **Hình ảnh minh họa**: Tìm kiếm mù trong không gian.
  
    ![No Observation Illustration](https://github.com/user-attachments/assets/0e53eb14-54d6-4319-9082-a9fd41beb62b)

**Nhận xét hiệu suất**:
- Các thuật toán này không hiệu quả cho 8-Puzzle vì trò chơi có môi trường xác định hoàn toàn, không cần xử lý thông tin không đầy đủ.

## 2.6. Tìm Kiếm Với Ràng Buộc (Constraint Satisfaction Problems - CSPs)

**Thuật toán được triển khai:**
- **Backtracking**:
  - **Nguyên lý**: Thử điền số vào trạng thái rỗng và quay lui khi gặp ràng buộc.
  - **Ưu điểm**: Đơn giản, cần ít bộ nhớ.
  - **Nhược điểm**: Không phù hợp với 8-Puzzle (thường di chuyển ô trống), chậm và dễ lặp lại trạng thái.
  - **Hình ảnh minh họa**: Backtracking thử và quay lui.
  
    ![Backtracking Illustration](https://github.com/user-attachments/assets/b11b69e8-088a-43b6-bebc-b030c42e4d26)

**Nhận xét hiệu suất**:
- Backtracking không hiệu quả do cách triển khai không đúng chuẩn cho 8-Puzzle (điền số thay vì di chuyển ô trống). Số liệu (49 bước, 65,764 trạng thái) cần kiểm tra lại.

## 2.7. Học Tăng Cường (Reinforcement Learning)

**Thuật toán được triển khai:**
- **Q-Learning**:
  - **Nguyên lý**: Học chính sách tối ưu qua thử và sai, dựa trên phần thưởng (ví dụ: +500 khi đạt mục tiêu, -3 mỗi bước).
  - **Ưu điểm**: Linh hoạt, không cần mô hình môi trường.
  - **Nhược điểm**: Rất chậm (32.3161s), cần thời gian huấn luyện dài (50,000 episodes).
  - **Hình ảnh minh họa**: Q-Learning cải thiện dần qua các lần thử.
  
    ![Q-Learning Illustration](https://github.com/user-attachments/assets/bbe2f6ea-4228-4975-911a-59b2a036b196)

**Nhận xét hiệu suất**:
- Q-Learning phù hợp cho môi trường động, nhưng quá chậm và tạo đường đi dài (75 bước) cho 8-Puzzle.

## 2.8. Bảng So Sánh Hiệu Năng Các Thuật Toán Giải 8-Puzzle

| Thuật toán               | Số bước giải pháp | Trạng thái đã duyệt | Thời gian chạy (s) | Ghi chú |
|--------------------------|-------------------|----------------------|---------------------|---------|
| **BFS**                 | 23                | 91,351               | 1.5397              | Tối ưu độ dài |
| **DFS**                 | 45                | 55,644               | 0.4864              | Giới hạn độ sâu 50 |
| **UCS**                 | 23                | 214,585              | 6.1250              | Chi phí đồng nhất, cần kiểm tra số trạng thái |
| **IDS**                 | 27                | 168,615              | 2.1241              | Kết hợp DFS + BFS |
| **A***                 | 23                | 2,700                | 0.0497              | Hiệu quả với heuristic |
| **Greedy**              | 51                | 724                  | 0.0144              | Nhanh nhưng không tối ưu |
| **IDA***               | 23                | 48,891               | 0.7950              | Tối ưu, tiết kiệm bộ nhớ |
| **AO***                | ✗                 | -                    | -                   | Không phù hợp |
| **Simple HC**           | ✗                 | -                    | -                   | Không tìm thấy lời giải |
| **Steepest HC**         | ✗                 | -                    | -                   | Không tìm thấy lời giải |
| **Stochastic HC**       | ✗                 | -                    | -                   | Không tìm thấy lời giải |
| **Simulated Annealing** | ✗                 | -                    | -                   | Không hội tụ |
| **Partially Observable**| ✗                 | -                    | -                   | Không hiệu quả |
| **No Observation**      | ✗                 | -                    | -                   | Không phù hợp |
| **Backtracking**        | 49                | 65,764               | 0.9086              | Không đúng chuẩn, cần kiểm tra |
| **Q-Learning**          | 75                | 1,470,475            | 32.3161             | Rất chậm, cần huấn luyện |

**Ghi chú**:
- ✗: Không tìm thấy lời giải.
- **Số bước giải pháp**: Số hành động từ trạng thái ban đầu đến mục tiêu.
- **Trạng thái đã duyệt**: Số node trong không gian trạng thái được mở rộng.
- **Thời gian chạy**: Thời gian trung bình để tìm lời giải.
- **Heuristic**: Khoảng cách Manhattan.
- **Cần kiểm tra**: Số liệu cho UCS và Backtracking cần chạy lại mã để xác minh do triển khai có thể chưa tối ưu.

## 3. Kết Luận

Dự án đã triển khai thành công 16 thuật toán tìm kiếm để giải bài toán **8-Puzzle**, với giao diện Pygame cho phép nhập trạng thái, quan sát quá trình giải, và hiển thị thống kê (nút mở rộng, độ sâu, thời gian). Kết quả cho thấy:
- **A*** và **IDA*** là các thuật toán hiệu quả nhất, cân bằng giữa tốc độ (0.0497s và 0.7950s) và độ tối ưu (23 bước).
- **BFS** và **UCS** đảm bảo lời giải tối ưu nhưng tốn tài nguyên (1.5397s và 6.1250s).
- **Greedy** nhanh nhất (0.0144s) nhưng không tối ưu (51 bước).
- **Local Search** (Hill Climbing, Simulated Annealing) không hiệu quả do mắc kẹt ở cực đại cục bộ.
- **Q-Learning** linh hoạt nhưng quá chậm (32.3161s) cho bài toán nhỏ như 8-Puzzle.
- **Complex Environment** và **AO*** không phù hợp do môi trường xác định của 8-Puzzle.

Chọn heuristic chất lượng (khoảng cách Manhattan) và cân nhắc giữa tốc độ và độ chính xác là yếu tố quyết định hiệu suất.

## 4. Hạn Chế và Hướng Phát Triển

**Hạn chế**:
- Các thuật toán Local Search (Hill Climbing, Simulated Annealing) không hiệu quả, cần cải thiện lịch nhiệt độ hoặc chiến lược thoát cực đại cục bộ.
- Q-Learning yêu cầu thời gian huấn luyện dài và thiết kế phần thưởng phức tạp.
- Backtracking không đúng chuẩn cho 8-Puzzle (điền số thay vì di chuyển ô trống), cần sửa lại.
- UCS duyệt nhiều trạng thái hơn dự kiến, có thể do xử lý trạng thái trùng chưa tối ưu.
- Giao diện chưa xuất số liệu hiệu suất ra file để phân tích.

**Hướng phát triển**:
- Sửa hàm Backtracking để di chuyển ô trống thay vì điền số.
- Tối ưu UCS bằng cách cải thiện kiểm tra trạng thái trùng.
- Tích hợp xuất số liệu hiệu suất vào file CSV để phân tích.
- Thêm heuristic kết hợp (Manhattan + số ô sai vị trí) cho A* và IDA*.
- Thêm tính năng tạo trạng thái ban đầu ngẫu nhiên và kiểm tra tính khả thi.

## Cài Đặt và Chạy

1. **Yêu cầu hệ thống**:
   - Python 3.10+
   - Thư viện: `pygame`, `time`, `heapq`, `collections`, `sys`, `random`, `math`

2. **Cài đặt**:
   ```bash
   pip install pygame
   ```

3. **Chạy chương trình**:
   ```bash
   git clone https://github.com/your-repository/8PuzzleSolver.git
   cd 8PuzzleSolver
   python 8puzzel.py
   ```

4. **Cấu trúc thư mục**:
   ```
   8PuzzleSolver/
   ├── 8puzzel.py
   ├── README.md
   ```

## Tài Liệu Tham Khảo
- *Artificial Intelligence: A Modern Approach* (Stuart Russell & Peter Norvig)
- *Introduction to Algorithms* (Thomas H. Cormen)
- "Solving 8-Puzzle using A* Algorithm", truy cập ngày 25/4/2025, [GeeksforGeeks](https://www.geeksforgeeks.org/8-puzzle-problem-using-branch-and-bound/)
- "Q-Learning", *Reinforcement Learning: An Introduction* (Sutton & Barto)
- "Local Search Algorithms", truy cập ngày 25/4/2025, [Russell & Norvig](https://www.cs.cmu.edu/~russell/book.html)