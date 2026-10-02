# Privacy Policy for JQR - Journals Quality & Ranking Extension

**Last Updated:** October 2, 2026  
**Developer:** Trung V.M Nguyen  
**Repository:** [https://github.com/trungnvm/JQR-Scholar-Extension](https://github.com/trungnvm/JQR-Scholar-Extension)

---

## 1. Overview and Commitment

**JQR - Journals Quality & Ranking** is an open-source browser extension designed to help researchers, academics, and students evaluate academic journal quality metrics directly within Google Scholar search results.

We believe that user privacy is a fundamental right. **JQR operates on a strict zero-data-collection policy.** We do not collect, store, transmit, monetize, track, or share any personal information, browsing history, search queries, or user behavioral data.

---

## 2. Information We Do NOT Collect

- **No Personal Identifiable Information (PII):** We do not collect names, email addresses, IP addresses, location data, or contact details.
- **No Browsing History or Activity:** We do not track websites visited, links clicked outside the extension's scope, or general browsing sessions.
- **No Search Queries:** Any terms or topics you search for on Google Scholar are processed entirely within your local browser runtime. They are never sent to our servers or any third-party analytics provider.
- **No Financial or Payment Information:** The extension is 100% free and open-source.

---

## 3. Permissions Requested & Why They Are Necessary

JQR adheres strictly to the **Principle of Least Privilege**. Every requested permission in `manifest.json` serves a dedicated functional purpose:

1. **`storage`**:
   - **Purpose:** Used solely to save your local UI preferences (such as enabled ranking systems, e.g., CCF, ABDC, JCR, and interface language).
   - **Scope:** All preference data is stored locally in your browser using `chrome.storage.sync` or `chrome.storage.local`. None of this configuration data is ever transmitted externally.

2. **`activeTab`**:
   - **Purpose:** Allows the extension to interact with the active Google Scholar tab you are currently viewing.
   - **Scope:** Used to inject and render journal ranking badges and metric cards directly adjacent to publication entries on Google Scholar search results.

3. **Host Permissions (`https://scholar.google.*/*`)**:
   - **Purpose:** Needed exclusively to detect journal titles from Google Scholar search result pages.
   - **Scope:** The extension reads only the publication metadata (journal title, year, authors) rendered in the Scholar search DOM to match against the offline journal ranking database packaged inside the extension.

---

## 4. Network Requests & Third-Party Services

- **Offline by Default:** The core ranking database (including Clarivate JCR, Scimago SJR, CCF, CORE, ABDC, FT50, VHB, and others) is bundled entirely offline within the extension package. Lookups occur instantly in local memory without making network calls.
- **Public Academic Metadata APIs:** If an article requires DOI resolution or paper-level verification, the extension may fetch bibliographic metadata from publicly accessible academic registries:
  - **CrossRef API** (`https://api.crossref.org`)
  - **DBLP Computer Science Bibliography** (`https://dblp.org`)
  These requests contain only the bibliographic query (title or DOI). No cookies, user identifiers, or personal data are ever attached to these requests.
- **No Analytics or Trackers:** JQR does not include Google Analytics, Facebook Pixel, Mixpanel, Sentry, or any other tracking, advertising, or telemetry scripts.

---

## 5. Data Security & Storage

Because JQR does not collect or transmit personal user data to any external server:
- There is no remote database storing your personal information.
- There is zero risk of server-side data breaches involving user data through our extension.
- All configuration settings remain under the user's complete control on their local device and can be cleared at any time by uninstalling the extension or clearing extension data.

---

## 6. Open Source Verification

JQR is open-source software. Anyone can inspect, audit, and verify the extension's source code and behavior on GitHub:  
[https://github.com/trungnvm/JQR-Scholar-Extension](https://github.com/trungnvm/JQR-Scholar-Extension)

---

## 7. Changes to This Privacy Policy

If any changes are made to this policy, the updated version will be posted in this repository with a revised "Last Updated" date.

---

## 8. Contact & Support

If you have questions, feedback, or concerns regarding this Privacy Policy, please open an issue on our GitHub repository:  
- **GitHub Issues:** [https://github.com/trungnvm/JQR-Scholar-Extension/issues](https://github.com/trungnvm/JQR-Scholar-Extension/issues)
- **Developer Profile:** [https://github.com/trungnvm](https://github.com/trungnvm)
