/**
 * 學分補考系統 - Google Sheets 自動上傳腳本
 *
 * 功能：將 Google Sheets 匯出為 Excel 並上傳到後端 API
 */

// ============ 請修改以下設定 ============
const CONFIG = {
  // 你的後端 API 網址（部署後請改為正式網址）
  API_URL: "http://你的伺服器IP/admin/upload",

  // Secret Token（從 docker logs 取得）
  SECRET_TOKEN: "在這裡貼上你的64字元Token"
};
// ========================================

/**
 * 上傳補考名單到資料庫
 */
function uploadToDatabase() {
  try {
    // 取得目前的試算表
    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    const spreadsheetId = spreadsheet.getId();

    // 匯出為 Excel 格式
    const url = `https://docs.google.com/spreadsheets/d/${spreadsheetId}/export?format=xlsx`;
    const token = ScriptApp.getOAuthToken();

    const response = UrlFetchApp.fetch(url, {
      headers: {
        'Authorization': 'Bearer ' + token
      }
    });

    const excelBlob = response.getBlob().setName('makeup_exam.xlsx');

    // 上傳到後端 API
    const uploadResponse = UrlFetchApp.fetch(CONFIG.API_URL, {
      method: 'POST',
      headers: {
        'X-Admin-Token': CONFIG.SECRET_TOKEN
      },
      payload: {
        file: excelBlob
      }
    });

    // 解析回應
    const result = JSON.parse(uploadResponse.getContentText());

    if (result.success) {
      SpreadsheetApp.getUi().alert(
        '上傳成功',
        `已成功上傳 ${result.count} 筆補考資料！`,
        SpreadsheetApp.getUi().ButtonSet.OK
      );
    } else {
      throw new Error(result.detail || '上傳失敗');
    }

  } catch (error) {
    SpreadsheetApp.getUi().alert(
      '上傳失敗',
      `錯誤訊息：${error.message}`,
      SpreadsheetApp.getUi().ButtonSet.OK
    );
    Logger.log('Upload error: ' + error.message);
  }
}

/**
 * 建立自訂選單
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('📚 補考系統')
    .addItem('🚀 上傳到資料庫', 'uploadToDatabase')
    .addItem('🔍 測試連線', 'testConnection')
    .addToUi();
}

/**
 * 測試連線
 */
function testConnection() {
  try {
    const response = UrlFetchApp.fetch(
      CONFIG.API_URL.replace('/admin/upload', '/health'),
      { method: 'GET' }
    );

    const result = JSON.parse(response.getContentText());

    if (result.status === 'healthy') {
      SpreadsheetApp.getUi().alert('連線成功', '後端伺服器運作正常！', SpreadsheetApp.getUi().ButtonSet.OK);
    }
  } catch (error) {
    SpreadsheetApp.getUi().alert('連線失敗', `無法連接到伺服器：${error.message}`, SpreadsheetApp.getUi().ButtonSet.OK);
  }
}
