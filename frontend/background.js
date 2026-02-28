// chrome.runtime.onInstalled.addListener(() => {
//   console.log("Friction extension installed.");
// });

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
      fetch("http://127.0.0.1:8000/checktab", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(taburl)
      }) 
      .then(res => res.json())
      .then(data => {
        const success = data.status === "success";
        console[success ? "log" : "error"](data.msg || data);
        chrome.runtime.sendMessage({
          action: "updateUI",
          status: success ? "success" : "error",
          message: data.msg
        });

        if (success) {
          //
        }
      })
      .catch(err => {
        console.error("Error:", err);
        //
      });
    }
  });
});