// גשר קטן בין הבקאנד ב-Python לספרייה הפתוחה israeli-bank-scrapers.
//
// קורא מ-stdin אובייקט JSON יחיד: { companyId, credentials, monthsBack }
// ומדפיס ל-stdout שורת JSON יחידה עם התוצאה - בדיוק כמו שהספרייה מחזירה
// (success, accounts[].balance, accounts[].txns, errorType, errorMessage).
//
// שימוש בפועל (מהצד של הפייתון): backend/scraper_bridge.py

const { createScraper, CompanyTypes } = require('israeli-bank-scrapers');

function readStdin() {
  return new Promise((resolve, reject) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => { data += chunk; });
    process.stdin.on('end', () => resolve(data));
    process.stdin.on('error', reject);
  });
}

function output(result) {
  // שורה אחת ויחידה על ה-stdout - זה מה שהפייתון מפרש.
  process.stdout.write(JSON.stringify(result) + '\n');
}

async function main() {
  let input;
  try {
    input = JSON.parse(await readStdin());
  } catch (err) {
    output({ success: false, errorType: 'BAD_INPUT', errorMessage: err.message });
    return;
  }

  const { companyId, credentials, monthsBack } = input;

  if (!companyId || !CompanyTypes[companyId]) {
    output({ success: false, errorType: 'UNKNOWN_COMPANY', errorMessage: `מוסד לא נתמך: ${companyId}` });
    return;
  }

  const startDate = new Date();
  startDate.setMonth(startDate.getMonth() - (monthsBack || 2));

  const scraper = createScraper({
    companyId: CompanyTypes[companyId],
    startDate,
    combineInstallments: false,
    showBrowser: false,
    verbose: false,
  });

  try {
    const result = await scraper.scrape(credentials || {});
    output(result);
  } catch (err) {
    output({ success: false, errorType: 'EXCEPTION', errorMessage: err.message });
  }
}

main();
