<h1 align="center"><img src="./icon/32x32.png" height="21px" alt=""> JQR Scholar Extension (v1.1) </h1> 
<h3 align="center"> Rapid Journal Quality & Impact Factor Check for Google Scholar Search Results </h3>
</br>

**JQR Scholar Extension** automatically displays journal rankings, Impact Factor (JIF), Quartiles (Q1–Q4), H-Index, and multi-category metrics directly beside search results in Google Scholar.

Building upon CCFrank and the original work by [Dr. Julian Wichmann](https://de.linkedin.com/in/julianwichmann), this version has been extensively refactored, modernized, and expanded with the complete **Clarivate JCR 2026 Database**, smart multi-tier Q fallbacks, high-speed local dictionary lookup, and unified color synchronization.

---

## Key Features in v1.1

- **2026 Clarivate JCR Impact Factor & Ranking Database Integration**:
  - Complete Clarivate JCR 2026 database covering over **22,600 academic journals** across SCIE, SSCI, AHCI, and ESCI.
  - Pre-compiled into high-speed in-memory datasets: **39,913 ISSN/eISSN keys** and **70,266 journal title aliases and abbreviations**.
  - Displays official **2025/2026 JIF scores**, **JIF Quartiles (Q1–Q4)**, **JCI percentiles**, and **comprehensive multi-category subject ranking breakdown** in hover tooltips.
- **Smart Q Ranking Fallback (SJR Scopus & JCR Clarivate)**:
  - Intelligently checks Scopus SJR Q rating first. If missing, newly renamed, or unranked in Scopus (e.g., *Micro and Nanostructures*, *Advances in Natural Sciences: Nanoscience and Nanotechnology*), it automatically falls back to the official Clarivate JCR Quartile.
  - Informative tooltips show the exact quartile source: `SJR Quartile: Q... (Scopus)` or `JCR Quartile: Q... (Clarivate Web of Science)`.
- **Harmonized Color Hierarchy (Zero Discrepancy)**:
  - Synchronized CSS variables and badge logic so numeric IF thresholds perfectly match Quartile tiers:
    - **Top Tier / Super Elite (IF >= 10.0)**: Deep Green (`#28a745`)
    - **Q1 / High Quality (IF >= 5.0)**: Vibrant Green (`#34ce57`)
    - **Q2 / Very Good (IF 3.0 to < 5.0)**: Clean Yellow (`#ffc107`) — *Both IF 3.0 and IF 3.1 are consistently yellow!*
    - **Q3 / Moderate (IF 1.5 to < 3.0)**: Warm Orange (`#ff8800`)
    - **Q4 / Low (IF < 1.5)**: Coral Red (`#dc3545`)
- **Instant Local Lookups (0ms Latency)**:
  - Resolves journal rankings instantly from memory without waiting for external API calls, eliminating rate limits and slow load times.
- **Anti-Spin & Network Timeout Safeguards**:
  - CrossRef API timeout set to 3.0s and DBLP timeout to 2.5s with guaranteed spinner removal (`ccf-waiting`).
- **Seamless Infinite Scroll & Dynamic Observation**:
  - `MutationObserver` on `#gs_res_ccl_mid` plus debounced scroll listeners ensure newly loaded search results receive badges automatically.
- **Multi-Rank Support**:
  - Supports JCR, Scopus SJR, CORE (Journals & Conferences), CCF, ABDC, AJG (ABS), FT50, VHB, FNEGE, CoNRS, HCERES, and Danish BFI.

---

## Preview

Journal rankings and Impact Factors are directly added to Google Scholar search results with real-time badges and modern HUD tooltip cards.

### 1. Inline Search Result Badges
<p align="center">
  <img src="./img/preview.png" alt="JQR Scholar Extension in action on Google Scholar" width="850px" />
</p>

- **Instant Badges**: Displays `[Q1]`, `[Q2]`, `[Q3]`, `[IF: 48.9]`, `[IF: 2.1]`, `[BFI]`, etc. directly beside search results.
- **Harmonized Colors**: Color coding automatically reflects quality: Green (Q1 / IF >= 5.0), Yellow (Q2 / IF >= 3.0), Orange (Q3 / IF >= 1.5), and Red (Q4).
- **DOI Link**: Clicking rankings navigates directly to the publication via its DOI.

### 2. Academic Card Tooltip (UI/UX Pro Max)
Hovering over any Quartile or Impact Factor badge instantly displays an interactive, glassmorphic inspection card:

<p align="center">
  <img src="./img/preview_tooltip.png" alt="Academic Card Tooltip with full metrics breakdown" width="850px" />
</p>

- **Key Metrics Grid**: Shows Impact Factor, Quartile, Release Year, Database, and H-Index at a glance.
- **Subject Categories & Rankings Breakdown**: Shows every official subject category with Quartile badge, Exact Rank within field (e.g. `1/180`), and JCI Percentile (e.g. `99.7%`).
- **Bilingual Support (EN / VI)**: Clean toggle between English and Vietnamese, including playful subtitle *(Kính chiếu yêu)* in Vietnamese mode.

---

## Installation Guide

### Google Chrome (Recommended)
1. Clone or download this repository to your local computer.
2. Open Google Chrome and navigate to `chrome://extensions/`.
3. Enable **Developer mode** toggle in the top-right corner.
4. Click **Load unpacked** and select the extension folder:
   - `JQR-Scholar-Extension`
5. Visit [Google Scholar](https://scholar.google.com) and search for any topic or author to see instant journal rankings and Impact Factors!

### Mozilla Firefox
1. Open Firefox and go to `about:debugging#/runtime/this-firefox`.
2. Click **Load Temporary Add-on...**.
3. Select the `manifest.json` file inside the extension folder.

---

## Automated Verification

The repository includes a comprehensive 8-suite self-test suite covering:
1. Syntax check across all JavaScript files
2. In-memory data loading (39,913 ISSN keys & 70,266 Name keys)
3. Google Scholar `div.gs_a` text parsing (author vs venue separation)
4. Dual ISSN/eISSN and multi-category ranking extraction
5. Tooltip & badge HTML generation
6. Network timeouts and guaranteed spinner cleanup
7. Infinite scroll and `MutationObserver` deduplication
8. Specific edge cases (*Micro and Nanostructures*, *Advances in Natural Sciences*, color harmonization)

Run the test suite at any time:
```bash
node test_jqr_extension.js
```

---

## Ranking Sources & References

- **Clarivate Journal Citation Reports (JCR 2025/2026)**: Web of Science Group
- **SCImago Journal & Country Rank (SJR)**: http://www.scimagojr.com
- **Crossref Public API**: https://api.crossref.org/
- **DBLP Computer Science Bibliography**: https://dblp.org/
- **Australian Business Deans Council (ABDC)**: https://abdc.edu.au/
- **Chartered Association of Business Schools (AJG/ABS)**: https://charteredabs.org/
- **China Computer Federation (CCF)**: https://www.ccf.org.cn/
- **Computing Research & Education Association of Australasia (CORE)**: http://portal.core.edu.au/
- **Financial Times Research Rank (FT50)**: https://www.ft.com/

---

## Changelog

- **v1.1 (2026-10-02)**:
  - **Cập nhật danh sách mới 2026**: Nhúng trực tiếp CSDL Clarivate JCR 2026 mới nhất (`data/2026-newJCRimpactfactor.xlsx`) với **22.643 tạp chí**, **39.913 mã ISSN/eISSN**, và **70.266 tên & tên viết tắt** chuẩn hóa.
  - **Bóc tách JSON đa ngành**: Hỗ trợ hiển thị đầy đủ Quartile và thứ hạng các ngành liên ngành từ Cột AG.
  - **Cơ chế Fallback Q thông minh**: Tự động chuyển giao giữa Scopus SJR và Clarivate JCR, khắc phục triệt để lỗi thiếu Q ở *Micro and Nanostructures* và *Advances in Natural Sciences*.
  - **Đồng bộ hóa 100% hệ màu**: Triệt tiêu hoàn toàn mâu thuẫn màu cũ (IF 3.0 và IF 3.1 đều đồng nhất mang màu vàng Q2).
  - **Chống xoay mòng mòng & Cuộn vô tận**: Thêm timeout 3.0s/2.5s và MutationObserver.
  - Chi tiết xem tại [CHANGELOG.md](./CHANGELOG.md).

---

## License & Credits

- MIT License
- Based on CCFrank by WenyanLiu (https://github.com/WenyanLiu/CCFrank4dblp) and CCFrank4Scholar by Julian R. K. Wichmann.
- Maintained & upgraded by Trung V.M Nguyen.
