# Wealth Manager

Personal expense dashboard built from `Raj_NewTracker_2026_Claude.xlsm`.

## Files
- `template.html` — the whole app (HTML/CSS/JS, no framework). Placeholders `__DATA__` and `__MAP__` are filled at build time.
- `data.json` — extracted from the workbook by `extract.py` (sheets: Log, Home Construction, Budget vs Actual, Loan Tracker, Investments).
- `india_min.json` — India state outlines (from @svg-maps/india, CC BY 4.0) used by the Trips map.
- `build.py` — writes `wealth-manager.html`. `python build.py Tracker.xlsm` re-extracts first. Needs a password in `.wm_password` (gitignored) or `WM_PASSWORD`.

## Conventions
- "Spend" = My Share of rows with Type `Lifestyle` or `Recurring Fixed`. Investment, Capital Outlay and Loan-Lent are tracked separately.
- One-offs: any spend row >= ₹40k, or category Wedding. Excluded from forecasts.
- Forecast: typical month = median of last 3 complete months without one-offs.
- Colours are CSS tokens on `:root` with a light theme block; fonts are Manrope + Instrument Serif from Google Fonts.
- The "Ask Claude" panel uses the claude.ai artifact `sample` capability and only works when published as a Claude artifact; it hides itself elsewhere.
- Investments tab is password protected: `build.py` removes rows with Type or Category `Investment` and the Investments sheet from the page data and stores them AES-256-GCM encrypted (PBKDF2-SHA256 key) as `__VAULT__`; the page decrypts with Web Crypto when the PIN is complete on its centered number pad (password must be digits; its length is stored in the vault). Loading a workbook in the browser counts as unlocked.
- Only external script: SheetJS `xlsx@0.18.5` from cdnjs (used by "Load workbook").

## Workflow
`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`, then `.venv/bin/python build.py` and open `wealth-manager.html` in a browser.
