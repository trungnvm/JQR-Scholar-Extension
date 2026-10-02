// Cross-browser compatibility wrapper
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

// List of all checkbox IDs
const checkboxIds = [
    'on', 'turbo', 'fieldClassification', 'impactFactor', 'autoExpand',
    'ABDC', 'AJG', 'DAEN', 'CCF', 'CoNRS', 'CORE', 'FNEGE', 'FT50', 'HCERE', 'SJR', 'VHB', 'VHB4'
];

// List of ranking checkboxes (a subset of checkboxIds)
const rankingIds = [
    'ABDC', 'AJG', 'DAEN', 'CCF', 'CoNRS', 'CORE', 'FNEGE', 'FT50', 'HCERE', 'SJR', 'VHB', 'VHB4'
];

const i18n = {
  en: {
    optTitle: "Settings",
    funSubtitle: "",
    showFunSubtitle: false,
    headerInfo: "Customize which rankings appear in Google Scholar. We recommend enabling CORE for CS, SJR/BFI for broad coverage, and domain-specific lists like ABDC/VHB for Economics.",
    hdrCore: "Core Features",
    lblOn: "Enable JQR",
    subOn: "Turn extension on/off",
    lblTurbo: "Turbo Mode",
    subTurbo: "Direct title crawling (faster but may trigger CAPTCHA)",
    lblField: "Field Classification",
    subField: "Auto-detect research fields",
    lblIf: "Impact Factor",
    subIf: "Show JIF/SJR metrics",
    lblExpand: "Auto Expand",
    subExpand: "Show all rankings by default",
    hdrRankings: "Select Rankings",
    lblEnableAll: "Enable All",
    subEnableAll: "Select all rankings below",
    subAbdc: "Australian Business Deans Council",
    subAjg: "Academic Journal Guide",
    subBfi: "Danish Ministry Ranking",
    subCcf: "China Computer Federation",
    subCnrs: "Economics & Management",
    subCore: "Computing Research & Education",
    subFnege: "Management Sciences",
    subFt50: "Financial Times Top 50",
    subHceres: "Social Sciences & Humanities",
    subSjr: "SCImago Journal Rank",
    subVhb: "Business Administration",
    subVhb4: "VHB 4th Edition",
    hdrSearch: "Journal Search",
    searchPlaceholder: "Search for a journal...",
    lblVersion: "JQR Extension v1.1",
    lblCoffee: "☕ Buy me a coffee"
  },
  vi: {
    optTitle: "Cài đặt",
    funSubtitle: "(Kính chiếu yêu)",
    showFunSubtitle: true,
    headerInfo: "Tùy chỉnh các bảng xếp hạng hiển thị trên Google Scholar. Khuyến nghị bật CORE cho ngành CNTT, SJR/JCR cho độ phủ toàn diện, và ABDC/VHB cho khối ngành Kinh tế.",
    hdrCore: "Tính năng cốt lõi",
    lblOn: "Bật JQR",
    subOn: "Bật hoặc tắt tiện ích trên toàn trình duyệt",
    lblTurbo: "Chế độ Turbo",
    subTurbo: "Thu thập tiêu đề trực tiếp (nhanh hơn nhưng có thể gặp CAPTCHA)",
    lblField: "Phân loại chuyên ngành",
    subField: "Tự động nhận diện lĩnh vực nghiên cứu",
    lblIf: "Hệ số tác động (IF)",
    subIf: "Hiển thị chỉ số JCR / SJR",
    lblExpand: "Tự động mở rộng",
    subExpand: "Mặc định mở đầy đủ thứ hạng",
    hdrRankings: "Chọn bảng xếp hạng",
    lblEnableAll: "Bật tất cả",
    subEnableAll: "Chọn tất cả các bảng xếp hạng bên dưới",
    subAbdc: "Hội đồng Trưởng khoa Kinh doanh Úc",
    subAjg: "Hiệp hội các trường Kinh doanh (ABS / AJG)",
    subBfi: "Bảng xếp hạng Bộ Giáo dục Đan Mạch",
    subCcf: "Bảng xếp hạng Hiệp hội Tin học Trung Quốc",
    subCnrs: "Trung tâm Nghiên cứu Khoa học Pháp (Kinh tế & Quản lý)",
    subCore: "Bảng xếp hạng Nghiên cứu Khoa học Máy tính CORE",
    subFnege: "Quỹ Giáo dục Quản lý Doanh nghiệp Pháp",
    subFt50: "Top 50 Tạp chí Kinh doanh của Financial Times",
    subHceres: "Hội đồng Đánh giá Nghiên cứu và Giáo dục Pháp",
    subSjr: "Bảng xếp hạng tạp chí Scopus SCImago",
    subVhb: "Hiệp hội Giáo sư Quản trị Kinh doanh Đức",
    subVhb4: "Xếp hạng VHB phiên bản 4",
    hdrSearch: "Tra cứu tạp chí",
    searchPlaceholder: "Nhập tên tạp chí hoặc ISSN...",
    lblVersion: "JQR Extension v1.1",
    lblCoffee: "☕ Ủng hộ tác giả (Buy me a coffee)"
  }
};

let currentLang = 'vi';

function applyLanguage(lang) {
  currentLang = lang === 'en' ? 'en' : 'vi';
  const t = i18n[currentLang];

  const setText = (id, text) => {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  };

  setText('opt_title', t.optTitle);
  const funSub = document.getElementById('opt_fun_label');
  if (funSub) {
    if (t.showFunSubtitle) {
      funSub.textContent = t.funSubtitle;
      funSub.style.display = 'inline-block';
    } else {
      funSub.style.display = 'none';
    }
  }

  setText('opt_header_info', t.headerInfo);
  setText('hdr_core', t.hdrCore);
  setText('lbl_on', t.lblOn);
  setText('sub_on', t.subOn);
  setText('lbl_turbo', t.lblTurbo);
  setText('sub_turbo', t.subTurbo);
  setText('lbl_field', t.lblField);
  setText('sub_field', t.subField);
  setText('lbl_if', t.lblIf);
  setText('sub_if', t.subIf);
  setText('lbl_expand', t.lblExpand);
  setText('sub_expand', t.subExpand);

  setText('hdr_rankings', t.hdrRankings);
  setText('lbl_enableAll', t.lblEnableAll);
  setText('sub_enableAll', t.subEnableAll);
  setText('sub_abdc', t.subAbdc);
  setText('sub_ajg', t.subAjg);
  setText('sub_bfi', t.subBfi);
  setText('sub_ccf', t.subCcf);
  setText('sub_cnrs', t.subCnrs);
  setText('sub_core', t.subCore);
  setText('sub_fnege', t.subFnege);
  setText('sub_ft50', t.subFt50);
  setText('sub_hceres', t.subHceres);
  setText('sub_sjr', t.subSjr);
  setText('sub_vhb', t.subVhb);
  setText('sub_vhb4', t.subVhb4);

  setText('hdr_search', t.hdrSearch);
  const searchInput = document.getElementById('journal_query');
  if (searchInput) searchInput.setAttribute('placeholder', t.searchPlaceholder);

  setText('lbl_version', t.lblVersion);
  const coffeeEl = document.getElementById('lbl_coffee');
  if (coffeeEl) {
    coffeeEl.innerHTML = `<span>☕</span> ${t.lblCoffee.replace('☕ ', '')}`;
  }

  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === currentLang);
  });
}

function setLanguage(lang) {
  applyLanguage(lang);
  browserAPI.storage.local.get(null, function(items) {
    const updated = { ...items, language: currentLang };
    browserAPI.storage.local.set(updated);
  });
}

/**
 * Saves options to storage
 */
function save_options() {
    browserAPI.storage.local.get(null, function(items) {
        const newSettings = { ...items, language: currentLang };

        // Save standard checkboxes
        checkboxIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                // Map 'on' to 'ext_on'
                const key = (id === 'on') ? 'ext_on' : id;
                newSettings[key] = element.checked;
            }
        });

        // Save 'Enable All' state (not used by extension logic, but good for UI consistency)
        const enableAllEl = document.getElementById('enableAll');
        if (enableAllEl) {
            newSettings['enableAll'] = enableAllEl.checked;
        }

        browserAPI.storage.local.set(newSettings, function() {
            if (newSettings.ext_on === false) {
                if (browserAPI.action && browserAPI.action.setBadgeText) {
                    browserAPI.action.setBadgeText({ text: 'OFF' });
                } else if (browserAPI.browserAction && browserAPI.browserAction.setBadgeText) {
                    browserAPI.browserAction.setBadgeText({ text: 'OFF' });
                }
            } else {
                if (browserAPI.action && browserAPI.action.setBadgeText) {
                    browserAPI.action.setBadgeText({ text: '' });
                } else if (browserAPI.browserAction && browserAPI.browserAction.setBadgeText) {
                    browserAPI.browserAction.setBadgeText({ text: '' });
                }
            }
        });
    });
}

/**
 * Restores state using the preferences stored in storage
 */
function restore_options() {
    // Default values
    const defaults = {
        ext_on: true,
        turbo: true,
        fieldClassification: true,
        impactFactor: true,
        autoExpand: true,
        ABDC: true,
        AJG: true,
        DAEN: true,
        CCF: true,
        CoNRS: true,
        CORE: true,
        FNEGE: true,
        FT50: true,
        HCERE: true,
        SJR: true,
        VHB: true,
        VHB4: true,
        language: 'vi'
    };

    browserAPI.storage.local.get(defaults, function(items) {
        checkboxIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                // Map 'on' to 'ext_on'
                const key = (id === 'on') ? 'ext_on' : id;
                if (items[key] !== undefined) {
                    element.checked = items[key];
                }
            }
        });

        // Restore 'Enable All' toggle
        const enableAllEl = document.getElementById('enableAll');
        if (enableAllEl && items['enableAll'] !== undefined) {
            enableAllEl.checked = items['enableAll'];
        }

        applyLanguage(items.language || 'vi');

        // Update badge initially too
        if (items.ext_on === false) {
             if (browserAPI.action && browserAPI.action.setBadgeText) {
                browserAPI.action.setBadgeText({ text: 'OFF' });
            } else if (browserAPI.browserAction && browserAPI.browserAction.setBadgeText) {
                browserAPI.browserAction.setBadgeText({ text: 'OFF' });
            }
        } else {
             if (browserAPI.action && browserAPI.action.setBadgeText) {
                browserAPI.action.setBadgeText({ text: '' });
            } else if (browserAPI.browserAction && browserAPI.browserAction.setBadgeText) {
                browserAPI.browserAction.setBadgeText({ text: '' });
            }
        }
    });
}

// Add event listeners
document.addEventListener('DOMContentLoaded', restore_options);
checkboxIds.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
        element.addEventListener('change', () => {
            // If any ranking checkbox is unchecked manually, uncheck "Enable All"
            if (rankingIds.includes(id) && !element.checked) {
                const enableAllEl = document.getElementById('enableAll');
                if (enableAllEl) enableAllEl.checked = false;
            }
            save_options();
        });
    }
});

// "Enable All" logic
const enableAllEl = document.getElementById('enableAll');
if (enableAllEl) {
    enableAllEl.addEventListener('change', function() {
        const isChecked = this.checked;
        rankingIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.checked = isChecked;
            }
        });
        save_options();
    });
}

// Language Switcher Event Listeners
const optLangEnBtn = document.getElementById('lang_en');
if (optLangEnBtn) optLangEnBtn.addEventListener('click', () => setLanguage('en'));
const optLangViBtn = document.getElementById('lang_vi');
if (optLangViBtn) optLangViBtn.addEventListener('click', () => setLanguage('vi'));

/* ############# Journal Search Function ############# */

function toUnicodeVariant(str, variant, flags) {
    const offsets = {
        m: [0x1d670, 0x1d7f6],
        b: [0x1d400, 0x1d7ce],
        i: [0x1d434, 0x00030],
        bi: [0x1d468, 0x00030],
        c: [0x1d49c, 0x00030],
        bc: [0x1d4d0, 0x00030],
        g: [0x1d504, 0x00030],
        d: [0x1d538, 0x1d7d8],
        bg: [0x1d56c, 0x00030],
        s: [0x1d5a0, 0x1d7e2],
        bs: [0x1d5d4, 0x1d7ec],
        is: [0x1d608, 0x00030],
        bis: [0x1d63c, 0x00030],
        o: [0x24B6, 0x2460],
        p: [0x249C, 0x2474],
        w: [0xff21, 0xff10],
        u: [0x2090, 0xff10]
    }

    const variantOffsets = {
        'monospace': 'm',
        'bold': 'b',
        'italic': 'i',
        'bold italic': 'bi',
        'script': 'c',
        'bold script': 'bc',
        'gothic': 'g',
        'gothic bold': 'bg',
        'doublestruck': 'd',
        'sans': 's',
        'bold sans': 'bs',
        'italic sans': 'is',
        'bold italic sans': 'bis',
        'parenthesis': 'p',
        'circled': 'o',
        'fullwidth': 'w'
    }

    var special = {
        m: { ' ': 0x2000, '-': 0x2013 },
        i: { 'h': 0x210e },
        g: { 'C': 0x212d, 'H': 0x210c, 'I': 0x2111, 'R': 0x211c, 'Z': 0x2128 },
        o: { '0': 0x24EA, '1': 0x2460, '2': 0x2461, '3': 0x2462, '4': 0x2463, '5': 0x2464, '6': 0x2465, '7': 0x2466, '8': 0x2467, '9': 0x2468 },
        p: {}, w: {}
    }
    for (var i = 97; i <= 122; i++) { special.p[String.fromCharCode(i)] = 0x249C + (i - 97) }
    for (var i = 97; i <= 122; i++) { special.w[String.fromCharCode(i)] = 0xff41 + (i - 97) }

    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    const numbers = '0123456789';

    var getType = function (variant) {
        if (variantOffsets[variant]) return variantOffsets[variant]
        if (offsets[variant]) return variant;
        return 'm';
    }
    var getFlag = function (flag, flags) {
        if (!flags) return false
        return flags.split(',').indexOf(flag) > -1
    }

    var type = getType(variant);
    var underline = getFlag('underline', flags);
    var strike = getFlag('strike', flags);
    var result = '';

    for (var k of str) {
        let index
        let c = k
        if (special[type] && special[type][c]) c = String.fromCodePoint(special[type][c])
        if (type && (index = chars.indexOf(c)) > -1) {
            result += String.fromCodePoint(index + offsets[type][0])
        } else if (type && (index = numbers.indexOf(c)) > -1) {
            result += String.fromCodePoint(index + offsets[type][1])
        } else {
            result += c
        }
        if (underline) result += '\u0332'
        if (strike) result += '\u0336'
    }
    return result
}

function joursearch_func() {
    const input = document.getElementById("journal_query").value;
    if (!input) return;

    let query = input.toUpperCase();
    query = query.replace(/&AMP;/g, "&");
    query = query.replace(/ AND /g, "");
    query = query.replace(/^THE /g, "");
    query = query.replace(/, THE$/g, "");
    query = query.normalize('NFD');
    query = query.replace(/[^A-Z0-9]/ig, "");

    browserAPI.storage.local.get(null, function(settings) {
        browserAPI.runtime.sendMessage({
            action: "searchJournal",
            query: query,
            settings: settings
        }, function(response) {
            if (response && response.found) {
                displayResults(input, response.results);
            } else {
                alert("Journal not found, please check the spelling.");
            }
        });
    });
}

function displayResults(input, results) {
    let text2 = "";
    let i = 0;
    while (i < 14 && results[i] !== undefined) {
        text2 += results[i].name + ": " + toUnicodeVariant(results[i].value, 'bold') + ";       "
        i++;
    }
    alert(toUnicodeVariant(input, 'bold italic') + ": \n" + text2);
}

const searchForm = document.getElementById("joursearch_form");
if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        joursearch_func();
    });
}
