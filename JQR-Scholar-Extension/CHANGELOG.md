# Changelog - JQR Scholar Extension

All notable changes to the **JQR Scholar Extension** will be documented in this file.

---

## [v1.1] - 2026-10-02

### 🚀 Cập nhật cơ sở dữ liệu xếp hạng mới 2026 (Updated 2026 Journal Ranking List)
- **Tích hợp CSDL Clarivate JCR 2026 mới nhất**:
  - Cập nhật toàn diện hơn **22.600+ tạp chí khoa học toàn cầu** thuộc các danh mục SCIE, SSCI, AHCI và ESCI.
  - Tối ưu hóa từ điển tra cứu offline siêu tốc với gần **40.000 mã ISSN/eISSN** và hơn **70.000 tên tạp chí & tên viết tắt chuẩn hóa**.
  - Bổ sung thông tin chi tiết về thứ hạng chuyên ngành, phân vị phần trăm (Percentile) và Quartile đa lĩnh vực khi di chuột qua tooltip.

### 🎯 Cơ chế Fallback Q thông minh (Smart Q-Ranking Fallback)
- **Tự động liên thông giữa Scopus SJR và Clarivate JCR**:
  - Khi một tạp chí chưa được Scopus SJR xếp hạng hoặc mới đổi tên / đổi mã ISSN (ví dụ: *Micro and Nanostructures*), hệ thống sẽ tự động lấy Quartile chính thức từ Clarivate JCR 2026 để hiển thị huy hiệu [Q2].
  - Sửa lỗi nhận diện khi tạp chí chỉ có eISSN hoặc định dạng tên đặc thù (như *Advances in Natural Sciences: Nanoscience and Nanotechnology*), đảm bảo hiển thị đầy đủ cả Quartile và Impact Factor.
  - Tooltip hiển thị rõ ràng nguồn dữ liệu xếp hạng: `SJR Quartile: Q... (Scopus)` hoặc `JCR Quartile: Q... (Clarivate Web of Science)`.

### 🎨 Đồng bộ hóa bảng màu hiển thị (Color System Harmonization)
- **Chuẩn hóa màu sắc huy hiệu Impact Factor và Quartile**:
  - Khắc phục triệt để hiện tượng lệch màu giữa các mức chỉ số tương đương.
  - Phân cấp màu sắc thống nhất, trực quan:
    - **IF >= 10.0**: Xanh lá đậm (Nhóm tạp chí hàng đầu / Top Tier)
    - **Q1 hoặc IF >= 5.0**: Xanh lá tươi
    - **Q2 hoặc IF từ 3.0 đến dưới 5.0**: Vàng chuẩn (Đồng bộ cả mức IF 3.0 và 3.1)
    - **Q3 hoặc IF từ 1.5 đến dưới 3.0**: Cam
    - **Q4 hoặc IF < 1.5**: Đỏ

### ⚡ Tối ưu hiệu năng & Trải nghiệm người dùng (Performance & UX)
- **Tra cứu tức thì (0ms Latency)**: Tận dụng cơ sở dữ liệu nội bộ sẵn có, hiển thị kết quả ngay khi tải trang mà không phụ thuộc vào kết nối API bên ngoài.
- **Khắc phục triệt để tình trạng xoay mòng mòng (Anti-Spin)**: Thêm cơ chế ngắt thời gian chờ (timeout) thông minh cho các truy vấn trực tuyến phụ trợ, tự động ẩn biểu tượng chờ khi không có phản hồi.
- **Hỗ trợ cuộn trang liên tục (Infinite Scroll)**: Tự động nhận diện và gắn huy hiệu xếp hạng ngay lập tức cho các bài báo mới xuất hiện khi người dùng cuộn xem thêm kết quả trên Google Scholar.
- **Cập nhật hình ảnh giao diện**: Làm mới ảnh minh họa giao diện thực tế của tiện ích trên Google Scholar trong tài liệu hướng dẫn.

---

## [v1.0] - Trước đây
- Phiên bản ban đầu hỗ trợ hiển thị SJR, H-Index, VHB, CORE, CCF trên Google Scholar.
