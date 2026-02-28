chrome.runtime.onInstalled.addListener(() => {
  console.log("Friction extension installed.");
});

/**
 * Retrieves the URL of a Chrome tab by its ID.
 *
 * @param {number} tabId - The ID of the tab whose URL should be retrieved.
 * @param {(url: string|null) => void} callback - Function invoked with the
 *        tab's URL on success, or `null` if an error occurs.
 */
function getTabUrl(tabId, callback) {
    chrome.tabs.get(tabId, (tab) => {
        if (chrome.runtime.lastError) {
            console.error("Error getting tab:", chrome.runtime.lastError);
            callback(null); // Return null in case of an error
        } else {
            callback(tab.url); // Return the URL via the callback
        }
    });
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    console.log("tab updated: " + tabId);
    getTabUrl(tabId, (taburl) => {
        console.log("tab updated url: " + taburl);
        if (taburl) {
            // send to backend
        }
    });
});