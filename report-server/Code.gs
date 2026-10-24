/**
 * Under the Hammer 回報系統（Google Apps Script）
 *
 * 遊戲裡按「回報問題」送出的內容，會一筆一筆寫進這個試算表的「回報」工作表，
 * 也可以順便寄一封通知信給你自己。
 *
 * 設定方式見同一個資料夾的 README.md。
 */

// 收到回報時寄信通知自己（改成 false 就不寄）
const NOTIFY_EMAIL = true;
// 一分鐘內最多收幾筆，超過的先丟掉，避免被灌爆
const MAX_PER_MINUTE = 20;

const SHEET_NAME = '回報';
const HEAD = ['收到時間', '類型', '內容', '聯絡方式', '版本', '來源', '遊戲日期', '地點', '頁面', '經費', '星級', '裝置', '螢幕', '語言', '錯誤紀錄', '存檔代碼', '處理狀態'];

function doPost(e) {
  try {
    const d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    // 不是遊戲送來的、或填了隱藏欄位（機器人），直接忽略
    if (d.game !== 'under-the-hammer' || d.hp) return out_('ignored');
    if (!rateOk_()) return out_('busy');

    const clip = (v, n) => String(v == null ? '' : v).slice(0, n);
    const row = [
      new Date(),
      clip(d.type, 20),
      clip(d.msg, 2000),
      clip(d.contact, 100),
      clip(d.ver, 20),
      clip(d.src, 20),
      clip(d.date, 40),
      clip(d.where, 60),
      clip(d.view, 20),
      typeof d.money === 'number' ? d.money : '',
      typeof d.star === 'number' ? d.star : '',
      clip(d.ua, 300),
      clip(d.scr, 40),
      clip(d.lang, 20),
      clip(Array.isArray(d.errors) ? d.errors.join('\n') : '', 3000),
      clip(d.save, 45000),
      '未處理'
    ];
    // 防止內容被試算表當成公式執行
    for (let i = 1; i < row.length; i++) {
      if (typeof row[i] === 'string' && /^[=+\-@]/.test(row[i])) row[i] = "'" + row[i];
    }
    const sh = sheet_();
    sh.appendRow(row);

    if (NOTIFY_EMAIL) {
      const me = Session.getEffectiveUser().getEmail();
      if (me) {
        MailApp.sendEmail(me,
          `【Under the Hammer 回報】${row[1]}：${clip(d.msg, 40)}`,
          `類型：${row[1]}\n\n${row[2]}\n\n聯絡方式：${row[3] || '（沒有填）'}\n版本：${row[4]}（${row[5]}）\n` +
          `遊戲日期：${row[6] || '—'}・${row[7] || '—'}\n裝置：${row[11] || '—'}\n螢幕：${row[12] || '—'}\n` +
          (row[14] ? `\n錯誤紀錄：\n${row[14]}\n` : '') +
          `\n完整內容（含存檔代碼）在試算表：${SpreadsheetApp.getActiveSpreadsheet().getUrl()}`);
      }
    }
    return out_('ok');
  } catch (err) {
    console.error(err);
    return out_('error');
  }
}

// 用瀏覽器打開網址時看到這句，代表部署成功
function doGet() {
  return out_('Under the Hammer 回報系統正常運作中。');
}

// 在編輯器裡選這個函式按「執行」，可以先試寫一筆、順便完成授權
function testReport() {
  const res = doPost({ postData: { contents: JSON.stringify({ game: 'under-the-hammer', type: '測試', msg: '這是一筆測試回報。', ver: 'test', src: '編輯器' }) } });
  console.log(res.getContent());
}

function sheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) sh = ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEAD);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEAD.length).setFontWeight('bold');
    sh.setColumnWidth(3, 360);
  }
  return sh;
}

function rateOk_() {
  const c = CacheService.getScriptCache();
  const k = 'n' + Math.floor(Date.now() / 60000);
  const n = Number(c.get(k) || 0) + 1;
  c.put(k, String(n), 120);
  return n <= MAX_PER_MINUTE;
}

function out_(t) {
  return ContentService.createTextOutput(t);
}
