if (typeof browser === 'undefined') {
    window.browser = window.chrome;
}
window.browserAPI = window.browser || window.chrome;
