// Cross-browser compatibility wrapper
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

/**
 * Open the options page
 */
function openOptions() {
  if (browserAPI.runtime.openOptionsPage) {
    browserAPI.runtime.openOptionsPage();
  } else {
    window.open(browserAPI.runtime.getURL('options.html'));
  }
}

// Settings button and link click handlers
document.getElementById('settings_btn').addEventListener('click', openOptions);
document.getElementById('settings_link').addEventListener('click', (e) => {
  e.preventDefault();
  openOptions();
});

// Refresh button click handler
document.getElementById('refresh').addEventListener('click', function() {
  browserAPI.tabs.query({active: true, currentWindow: true}, function(tabs) {
    if (tabs[0]) {
      browserAPI.tabs.reload(tabs[0].id);
    }
  });
});

/**
 * Saves options to storage
 * This only handles the simplified toggle switches in the popup.
 * The individual ranking checkboxes are managed in options.html.
 */
function save_options() {
  const on_off = document.getElementById('on').checked;
  const impactFactor = document.getElementById('impactFactor').checked;
  const fieldClassification = document.getElementById('fieldClassification').checked;
  const autoExpand = document.getElementById('autoExpand').checked;

  browserAPI.storage.local.get(null, function(items) {
    const newSettings = {
      ...items,
      ext_on: on_off,
      impactFactor: impactFactor,
      fieldClassification: fieldClassification,
      autoExpand: autoExpand
    };

    browserAPI.storage.local.set(newSettings, function() {
      if (on_off === false) {
        browserAPI.action.setBadgeText({ text: 'OFF' });
      } else {
        browserAPI.action.setBadgeText({ text: '' });
      }
    });
  });
}

/**
 * Restores state using the preferences stored in storage
 */
function restore_options() {
  browserAPI.storage.local.get({
    ext_on: true,
    impactFactor: true,
    fieldClassification: true,
    autoExpand: true
  }, function(items) {
    document.getElementById('on').checked = items.ext_on;
    document.getElementById('impactFactor').checked = items.impactFactor;
    document.getElementById('fieldClassification').checked = items.fieldClassification;
    document.getElementById('autoExpand').checked = items.autoExpand;

    if (items.ext_on === false) {
      browserAPI.action.setBadgeText({ text: 'OFF' });
    } else {
      browserAPI.action.setBadgeText({ text: '' });
    }
  });
}

// Event Listeners for toggles
document.getElementById('on').addEventListener('change', save_options);
document.getElementById('impactFactor').addEventListener('change', save_options);
document.getElementById('fieldClassification').addEventListener('change', save_options);
document.getElementById('autoExpand').addEventListener('change', save_options);

document.addEventListener('DOMContentLoaded', restore_options);

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

document.getElementById("joursearch_form").addEventListener('submit', function(e) {
    e.preventDefault();
    joursearch_func();
});
