const { readFile } = require("fs/promises")

const logsDir = __dirname + "/logs";

(async () => {
    const bapTxnIds = {};
    const bppTxnIds = {};

    let bapLogs = (await readFile(`${logsDir}/bap.log`)).toString("utf8").match(/{[^}]+}/gm).map(jsonStr => jsonStr);
    let bppLogs = (await readFile(`${logsDir}/bpp.log`)).toString("utf8").match(/{[^}]+}/gm).map(jsonStr => jsonStr);
    for (let i = 0; i < bapLogs.length; i++) {
        if (bapLogs[i].match(/\'transactionId\'\: \'.*\'\,/gm)) {
            const txnId = (/\'transactionId\'\: \'(.*)\'\,/gm).exec(bapLogs[i])[1];
            bapTxnIds[txnId] = bapTxnIds[txnId] ? bapTxnIds[txnId] + 1 : 1;
        }
    }
    for (let i = 0; i < bppLogs.length; i++) {
        if (bppLogs[i].match(/\'transactionId\'\: \'.*\'\,/gm)) {
            const txnId = (/\'transactionId\'\: \'(.*)\'\,/gm).exec(bppLogs[i])[1];
            bppTxnIds[txnId] = bppTxnIds[txnId] ? bppTxnIds[txnId] + 1 : 1;
        }
    }

    const failedOnsearchBapTxnIds = []
    const failedSearchBPPTxnIds = []
    for (let txnId in bapTxnIds) {
        if (bapTxnIds.hasOwnProperty(txnId) && bapTxnIds[txnId] != 2) {
            if(!bppTxnIds[txnId]) failedSearchBPPTxnIds.push(txnId)
            else failedOnsearchBapTxnIds.push(txnId);
        }
    }
    const anomalySearchTxnIdsFromGateway = []
    for (let txnId in bppTxnIds) {
        if (bppTxnIds.hasOwnProperty(txnId) && !bapTxnIds.hasOwnProperty(txnId)) {
            anomalySearchTxnIdsFromGateway.push(txnId)
        }
    }
    console.log("Total /search transactions Broadcasted from BAP to Gateway : " + Object.keys(bapTxnIds).length)
    console.log("Total /search transactions Broadcasted from Gateway to BPP : " + Object.keys(bppTxnIds).length)
    console.log("Total anomaly /search transactions Broadcasted from Gateway to BPP that were not sent by our BAP : " + anomalySearchTxnIdsFromGateway.length)
    console.log("Total /search transactions that were Broadcasted from BAP but not recieved on BPP by Gateway : " + failedSearchBPPTxnIds.length)
    console.log("Total /search transactions that were Broadcasted from BAP and recieved on BPP by Gateway but their /on_search failed to come to BAP : " + failedOnsearchBapTxnIds.length)
})()