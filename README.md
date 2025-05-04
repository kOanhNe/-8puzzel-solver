# -8puzzel-solver

#Đồ Án Cá Nhân - môn Trí Tuệ Nhân Tạo ()

#Tổng Quan

Trình Giải 8-Puzzle là một chương trình Python giúp giải bài toán 8-puzzle (trò chơi xếp ô số) bằng nhiều thuật toán tìm kiếm khác nhau. Bài toán 8-puzzle bao gồm một lưới 3x3 với 8 ô số (từ 1 đến 8) và một ô trống (ký hiệu '_'). Mục tiêu là di chuyển các ô số bằng cách trượt vào ô trống để đạt được trạng thái mục tiêu từ trạng thái ban đầu.

Chương trình cung cấp giao diện đồ họa tương tác sử dụng thư viện Pygame, cho phép người dùng:
- Giải bài toán bằng các thuật toán tìm kiếm khác nhau.
- Tự di chuyển các ô số để giải thủ công.
- Nhập trạng thái ban đầu và mục tiêu tùy chỉnh.
- Quan sát quá trình giải và thống kê hiệu suất thuật toán.
- Với một số thuật toán (như AO*), xem trực quan hóa cây tìm kiếm.

#Yêu Cầu Cần Thiết
Để chạy chương trình, bạn cần:
- Python 3.x (khuyến nghị Python 3.6 trở lên).
- Thư viện Pygame cho giao diện đồ họa.
- Các thư viện chuẩn của Python: time, heapq, collections, sys, random, math (đã có sẵn trong Python).

#Các Tính Năng Chính
*Chọn Thuật Toán:
Nhấn vào một trong các nút thuật toán (ví dụ: "BFS", "A*", "Greedy") để chọn phương pháp giải.
Tên thuật toán được chọn sẽ sáng lên, và một thông báo xác nhận lựa chọn.
Các thuật toán được hỗ trợ được mô tả chi tiết ở phần "Các Thuật Toán Hỗ Trợ" bên dưới.

*Chạy Thuật Toán:
Sau khi chọn thuật toán, nhấn nút "Play" để bắt đầu giải.
Chương trình sẽ hiển thị animation các ô di chuyển và cập nhật lưới "Trạng Thái Đang Sắp Xếp".
Nếu bài toán không thể giải được, thông báo sẽ xuất hiện sau một số bước giới hạn.
Thống kê được cập nhật theo thời gian thực, và thông báo hoàn thành xuất hiện khi tìm được lời giải.

*Chế Độ Thủ Công:
Nhấn "Chế Độ Thủ Công" để tự giải bài toán.
Sử dụng các phím mũi tên (Lên, Xuống, Trái, Phải) để di chuyển ô trống.
Lưới "Trạng Thái Đang Sắp Xếp" sẽ cập nhật sau mỗi di chuyển.
Tắt chế độ thủ công bằng cách nhấn lại nút.
Nhập Trạng Thái Tùy Chỉnh:
Nhấn "Nhập Trạng Thái" để nhập trạng thái ban đầu và mục tiêu tùy ý.
Bước 1: Trạng Thái Ban Đầu:
Một lưới xuất hiện để nhập trạng thái ban đầu.
Sử dụng phím số (1-9) để nhập các ô (9 đại diện cho ô trống).
Di chuyển giữa các ô bằng phím mũi tên hoặc nhấp chuột để chọn ô.
Nhấn Backspace để xóa ô, Enter để xác nhận, hoặc Esc để hủy.
Trạng thái phải bao gồm các số 1-8 (mỗi số chỉ xuất hiện một lần) và một ô trống (9).
Bước 2: Trạng Thái Mục Tiêu:
Sau khi xác nhận trạng thái ban đầu, nhập trạng thái mục tiêu tương tự.
Nhấn "Xác Nhận" hoặc Enter để lưu từng trạng thái.
Nếu nhập không hợp lệ (ví dụ: số trùng lặp hoặc thiếu ô trống), thông báo lỗi sẽ xuất hiện.
Tạm Dừng/Tiếp Tục:
Nhấn "Tạm Dừng" để tạm dừng animation của thuật toán.
Nhấn lại để tiếp tục.
Tính năng này hữu ích để kiểm tra trạng thái hiện tại trong quá trình giải.
Đặt Lại:
Nhấn "Đặt Lại" để khôi phục trạng thái mặc định:
Ban đầu: [[2, 6, 5], ['_', 8, 7], [4, 3, 1]]
Mục tiêu: [[1, 2, 3], [4, 5, 6], [7, 8, '_']]
Đặt lại tất cả cài đặt (lựa chọn thuật toán, chế độ thủ công, v.v.).
Trực Quan Hóa Cây Tìm Kiếm (Chỉ Với AO)*:
Nếu chọn thuật toán AO*, một cửa sổ riêng sẽ mở ra hiển thị cây tìm kiếm.
Các nút đại diện cho trạng thái, với nút màu vàng là trạng thái đã giải.
Các cạnh hiển thị các di chuyển (ví dụ: "UP", "DOWN") giữa các trạng thái.
Sử dụng phím + và - để phóng to/thu nhỏ.

Nhấn "Quay Lại" để trở về cửa sổ chính.

Hiển Thị Belief State (Chỉ Với Partially Observable):

Với thuật toán Partially Observable, giao diện hiển thị tối đa ba trạng thái có thể có của bài toán (belief state).

Điều này thể hiện sự không chắc chắn của thuật toán về trạng thái hiện tại.
