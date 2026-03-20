<h1 align="center"><img src="./JQR-Scholar-Extension/icon/32x32.png" height="21px" alt=""> JQR - Kiểm Tra Chất Lượng Tạp Chí Khoa Học</h1>
<h3 align="center">Hiển thị xếp hạng tạp chí ngay trên Google Scholar</h3>

<p align="center">
  <a href="./README.md">🇬🇧 English</a> · <b>🇻🇳 Tiếng Việt</b>
</p>

---

## Giới thiệu

**JQR** là extension trình duyệt giúp bạn **kiểm tra nhanh chất lượng tạp chí khoa học** ngay trên kết quả tìm kiếm của Google Scholar — không cần mở tab khác hay tra cứu thủ công.

Khi bạn search trên Google Scholar, extension sẽ **tự động** hiển thị các chỉ số xếp hạng (SJR, Impact Factor, H-Index, ABDC, CORE...) bên cạnh mỗi kết quả tìm kiếm, với **màu sắc trực quan** từ xanh (chất lượng cao) đến đỏ (chất lượng thấp).

## Tính năng chính

- 📊 **15+ hệ thống xếp hạng**: SJR, Impact Factor (JCR), H-Index, VHB, ABDC, AJG, CORE, CCF, CNRS, FNEGE, FT50, HCERES, BFI, SNIP, CiteScore
- 🎨 **Badge màu sắc**: Xanh lá = chất lượng cao, Đỏ = chất lượng thấp
- 🔍 **Tìm kiếm tạp chí**: Tra cứu ranking của bất kỳ tạp chí nào từ popup
- 🏷️ **Phân loại lĩnh vực**: Tự động nhận diện lĩnh vực nghiên cứu
- 🖱️ **Hover xem chi tiết**: Di chuột lên badge để xem H-Index, tên tạp chí
- 🔗 **Click vào DOI**: Nhấn badge để đi tới bài báo gốc
- ⚙️ **Tùy chỉnh**: Bật/tắt từng ranking theo nhu cầu

## Hướng dẫn cài đặt

### Cách 1: Cài trên Chrome / Edge / Brave

1. **Tải extension** về máy:
   - Nhấn nút **Code** → **Download ZIP** trên trang GitHub này
   - Hoặc clone bằng terminal:
     ```bash
     git clone https://github.com/trungnvm/JQR-Scholar-Extension.git
     ```

2. **Giải nén** file ZIP (nếu tải ZIP)

3. **Mở trang quản lý extension**:
   - Chrome: gõ `chrome://extensions/` vào thanh địa chỉ
   - Edge: gõ `edge://extensions/`
   - Brave: gõ `brave://extensions/`

4. **Bật Developer mode** (Chế độ nhà phát triển) — toggle ở góc trên bên phải

5. **Nhấn "Load unpacked"** (Tải tiện ích đã giải nén)

6. **Chọn thư mục `JQR-Scholar-Extension`** (thư mục chứa file `manifest.json`)

7. ✅ Extension sẽ xuất hiện trên thanh công cụ!

### Cách 2: Cài trên Firefox

1. Tải extension về máy (như trên)

2. Mở Firefox, gõ vào thanh địa chỉ: **`about:debugging#/runtime/this-firefox`**

3. Nhấn **"Load Temporary Add-on..."** (Nạp tiện ích tạm thời)

4. Chọn file **`manifest.json`** trong thư mục `JQR-Scholar-Extension`

5. Vào **cài đặt addon** (góc trên phải) → cấp quyền cho trang Google Scholar bạn dùng (ví dụ: `https://scholar.google.com.vn`)

> ⚠️ **Lưu ý**: Cài tạm thời trên Firefox sẽ mất khi restart trình duyệt. Để cài vĩnh viễn, tải từ [Firefox Add-ons](https://addons.mozilla.org/de/firefox/addon/rapid-journal-quality-check/).

## Hướng dẫn sử dụng

### Bước 1: Mở Google Scholar
Truy cập [scholar.google.com](https://scholar.google.com) và tìm kiếm bài báo bình thường.

### Bước 2: Xem ranking tự động
Các badge xếp hạng sẽ **xuất hiện tự động** bên cạnh mỗi kết quả tìm kiếm.

### Bước 3: Tương tác
- **Di chuột** lên badge → xem thông tin chi tiết (H-Index, tên tạp chí đã nhận diện)
- **Nhấn vào badge** → mở DOI của bài báo để xác nhận đúng tạp chí

### Bước 4: Tùy chỉnh từ Popup
Nhấn vào **icon JQR** trên thanh công cụ để:
- Bật/tắt extension
- Bật/tắt hiển thị Impact Factor
- Bật/tắt phân loại lĩnh vực
- Tìm kiếm tạp chí cụ thể

### Bước 5: Cài đặt nâng cao
Nhấn **"Advanced Settings"** trong popup để chọn cụ thể ranking nào muốn hiển thị.

## Bảng xếp hạng được hỗ trợ

| Viết tắt | Tên đầy đủ | Lĩnh vực |
|----------|-----------|----------|
| **SJR** | SCImago Journal Rank | Đa ngành |
| **JCR** | Journal Citation Reports (Impact Factor) | Đa ngành |
| **ABDC** | Australian Business Deans Council | Kinh doanh |
| **AJG** | Academic Journal Guide (CABS) | Quản trị |
| **CORE** | Computing Research & Education | Công nghệ |
| **CCF** | China Computer Federation | Tin học |
| **CNRS** | Centre National de la Recherche Scientifique | Đa ngành |
| **FNEGE** | Foundation Nationale pour l'Enseignement de la Gestion | Quản trị |
| **FT50** | Financial Times Top 50 | Kinh doanh |
| **HCERES** | High Council for Evaluation of Research | Đa ngành |
| **VHB** | VHB-JOURQUAL 3 & 4 | Kinh doanh |
| **SNIP** | Source Normalized Impact per Paper | Đa ngành |
| **CiteScore** | CiteScore (Scopus) | Đa ngành |
| **BFI** | Bibliometriske Forskningsindikator | Đa ngành |

## Ghi chú

- Extension hoạt động trên **tất cả domain Google Scholar** (scholar.google.com, scholar.google.com.vn, scholar.google.co.uk, ...)
- Dữ liệu ranking được lưu **offline** trong extension, không cần kết nối internet để tra cứu
- Nếu tạp chí không tìm thấy trong database offline, extension sẽ tự động tra qua **Crossref API**

## Tác giả & Ghi nhận

- Phát triển bởi **Trung V.M Nguyen**
- Dựa trên extension gốc của [Dr. Julian R. K. Wichmann](https://de.linkedin.com/in/julianwichmann)
- Nền tảng [CCFrank](https://github.com/WenyanLiu/CCFrank4dblp) của WenyanLiu
