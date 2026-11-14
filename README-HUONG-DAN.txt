# Gói cập nhật tự động – Học tập chính trị số Ban CHQS xã Cư Pui V3.17

## Phiên bản V3.17 – nâng cấp lịch lời Bác theo giờ Việt Nam
- Giữ nguyên cấu trúc, chức năng học tập, quản trị và nguyên tắc một tài khoản quản trị của nền V3.16.
- Ghim khung “Mỗi ngày một lời Bác Hồ dạy” ngay đầu trang chủ, nổi bật và hiển thị cả ngày, câu trích dẫn, xuất xứ, ý nghĩa và liên kết bài gốc.
- Có nút cập nhật thủ công ngay tại khung lời Bác; đồng thời tự tải dữ liệu khi mở trang, quay lại tab và khi dữ liệu ngày thay đổi.
- Đồng bộ ngày, ngày/tháng, đồng hồ và thời điểm tự chuyển ngày theo múi giờ `Asia/Ho_Chi_Minh`, không phụ thuộc múi giờ cài trên thiết bị.
- Khi qua 00:00 giờ Việt Nam, trang tự tải lại nội dung ngày mới trong vòng tối đa khoảng 30 giây.
- Vẫn ưu tiên bài đúng ngày từ nguồn; nếu nguồn chưa có bài, dùng tư liệu lưu kho theo cơ chế luân phiên và ghi rõ đó là lời gợi ý học tập.

## Nội dung gói
- `index.html`: Bản V3.17 giữ nguyên các chức năng trước đó; khung lời Bác được ghim ngay đầu trang chủ, có cập nhật thủ công và tự động tải lại dữ liệu.
- `data/daily-content.json`: Lời Bác hôm nay và danh sách văn bản mới.
- `data/loi-bac-365.json`: Kho lời Bác theo ngày. Khi ngày hiện tại chưa có bài riêng, trang chủ tự luân phiên một câu có trong kho để không còn khung trống; nhãn hiển thị phân biệt lời gợi ý với bài đúng ngày.
- `update_daily_content.py`: Chương trình lấy dữ liệu nguồn.
- `.github/workflows/daily-content.yml`: Lịch tự chạy hằng ngày lúc 00:10 giờ Việt Nam.

## Cách đưa lên GitHub Pages
1. Giải nén ZIP.
2. Trong repository GitHub đang chạy phần mềm, thay `index.html` bằng `index.html` trong gói này.
3. Tải lên cả thư mục `data`, tệp `update_daily_content.py` và thư mục `.github/workflows` (bật hiển thị file ẩn nếu cần).
4. Vào tab **Actions** của repository, chọn workflow **Cap nhat loi Bac va van ban phap luat hang ngay**, bấm **Run workflow** để chạy lần đầu.
5. Chờ workflow hoàn thành. Mỗi ngày workflow sẽ tự chạy và commit dữ liệu mới vào GitHub; GitHub Pages sẽ tự hiển thị dữ liệu mới.

## Nguồn dữ liệu và giới hạn
- Lời Bác: https://loibacday.com/ – lấy câu trích dẫn, xuất xứ, liên kết bài gốc. Bộ đồng bộ nhập kho các bài được liệt kê ở trang tác giả nguồn (hiện danh mục hiển thị 37 trang) rồi bổ sung lời của ngày mới theo trang chủ. Số lượng câu khác nhau phụ thuộc tư liệu thực tế có trên nguồn. Khi chưa có bài đúng ngày, phần mềm luân phiên câu đã có trong kho; không gán sai ngày phát ngôn/ngày đăng nguyên tác.
- Văn bản pháp luật: RSS Công báo điện tử Chính phủ https://congbao.chinhphu.vn/cac-van-ban-moi-ban-hanh.rss; ưu tiên văn bản có từ khóa quốc phòng, quân sự, dân quân, nghĩa vụ quân sự, dự bị động viên và các lĩnh vực liên quan. Có thể tra cứu bổ sung tại https://vbpl.vn/.
- Dữ liệu văn bản RSS chỉ hiển thị tiêu đề, mô tả nguồn, ngày đăng Công báo và ngày hiệu lực nếu nguồn cung cấp. Cần mở văn bản gốc để kiểm tra phạm vi áp dụng và tình trạng hiệu lực trước khi tham mưu hoặc triển khai.

## Lưu ý
- Tự động cập nhật cần repository GitHub có bật GitHub Actions và quyền ghi nội dung. Chỉ tải HTML riêng lẻ về máy sẽ không chạy lịch tự động.
- Nếu workflow không chạy, kiểm tra tab Actions và quyền `Read and write permissions` trong Settings → Actions → General.
- Không đưa mật khẩu, dữ liệu cá nhân hoặc tài liệu mật lên repository công khai.


BO SUNG V3.17 - KHO LOI BAC TICH HOP
- Trang chu co kho loi Bac duoc nhung san trong index.html, nen van hien thi khi khong co Internet va khong can nguoi dung tra cuu thu cong.
- Khi co mang, he thong van dong bo them du lieu tu thu muc data; du lieu moi duoc uu tien.
- Kho hien co 3 muc du lieu dau vao (13, 14, 15/11/2026); cac ngay chua co bai rieng se luan phien tu kho, khong gan nham ngay phat ngon goc.
- Muon co 365 cau khac nhau can bo sung du lieu vao data/loi-bac-365.json tu nguon tin cay; khong tu tao cau trich dan.


V3.17 – BỔ SUNG QUẢN TRỊ LỊCH HỌC HẰNG TUẦN
- Đăng nhập quản trị, mở mục Quản trị, kéo đến “Quản lý lịch học hằng tuần”.
- Có thể thêm/xóa tuần; sửa tên tuần, mục tiêu; thêm/xóa ngày; sửa thứ/ngày, chủ đề và hướng dẫn học.
- Bấm “Lưu lịch học” để người học nhìn thấy tại mục “Lịch học”.
- Lịch và kết quả vẫn lưu cục bộ trong trình duyệt/thiết bị; chưa đồng bộ tự động giữa nhiều thiết bị nếu chưa có máy chủ dùng chung.
