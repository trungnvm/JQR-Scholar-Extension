// Manifest V3 compatible background service worker
// Use chrome.* APIs which work in both Chrome and Firefox with Manifest V3
chrome.runtime.onInstalled.addListener(function(details){

  if( (details.reason == "install") || (details.reason === 'update' && details.previousVersion < '4.0.0') ) {

    chrome.storage.local.set({
        ext_on: true,
        SJR: false,
        VHB: true,
        FNEGE: false,
        CoNRS: false,
        HCERE: false,
        CORE: false,
        CCF: false,
        DAEN: false,
        AJG: false,
        ABDC: false,
        FT50: false,
        VHB4: false,
        fieldClassification: true, // new feature
        impactFactor: true, // new feature
        turbo: true
    });

    chrome.runtime.openOptionsPage();

  }

});

// Message handler for content script communication
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.message) {
        // Handle different message types from popup.js
        const ratingName = request.message;
        const url = request.url;

        // Import and handle CCF data requests
        // This will be handled by the content scripts that have access to the data
        sendResponse({status: "Message received in background"});
    }
    return true; // Keep message channel open for async responses
});
