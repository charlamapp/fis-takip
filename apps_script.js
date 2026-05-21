// Bu kodu Google Apps Script'e yapıştır
// Detaylar: KURULUM.md → Adım 2

const TOKEN = "fistakip2024"; // Bunu değiştirmek istersen APPS_SCRIPT_TOKEN ile aynı olmalı

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    if (data.token !== TOKEN) return _respond("unauthorized");

    const ss    = SpreadsheetApp.getActiveSpreadsheet();
    let sheet   = ss.getSheetByName("Fişler");
    if (!sheet) {
      sheet = ss.insertSheet("Fişler");
      const header = sheet.getRange(1, 1, 1, 7);
      header.setValues([["Tarih", "Mağaza", "Tutar (₺)", "Kategori", "Notlar", "Fotoğraf", "Eklenme"]]);
      header.setFontWeight("bold");
      header.setBackground("#2563eb");
      header.setFontColor("#ffffff");
      sheet.setFrozenRows(1);
    }

    sheet.appendRow([
      data.tarih,
      data.magaza,
      data.toplam,
      data.kategori,
      data.notlar,
      data.foto,
      data.eklenme,
    ]);

    return _respond("ok");
  } catch (err) {
    return _respond("error: " + err.message);
  }
}

function doGet(e) {
  if (!e.parameter || e.parameter.token !== TOKEN) return _respond("unauthorized");

  const ss    = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName("Fişler");
  if (!sheet || sheet.getLastRow() <= 1) {
    return ContentService.createTextOutput("[]").setMimeType(ContentService.MimeType.JSON);
  }

  const values = sheet.getDataRange().getValues();
  const rows   = values.slice(1).map(row => ({
    tarih    : String(row[0] || ""),
    magaza   : String(row[1] || ""),
    toplam   : String(row[2] || "0"),
    kategori : String(row[3] || ""),
    notlar   : String(row[4] || ""),
    link     : String(row[5] || ""),
  }));

  return ContentService.createTextOutput(JSON.stringify(rows))
    .setMimeType(ContentService.MimeType.JSON);
}

function _respond(msg) {
  return ContentService.createTextOutput(msg);
}
