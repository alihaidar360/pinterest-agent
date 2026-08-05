# Lumière & Luxe — Pinterest 6-Agent Automation System

Ye system 6 AI agents ka combination hai jo roz khud-ba-khud Pinterest ke liye
content taiyar karta hai (Google Sheet mein), aur har 15 din khud ko optimize
karta hai based on real performance data.

---

## SYSTEM KAISE KAAM KARTA HAI (Recap)

1. **Agent 1** — Gemini se Western trending jewelry keywords nikalta hai
2. **Agent 2** — Etsy API se un keywords ke matching products dhoondta hai
3. **Agent 3** — Gemini vision se products ko brand-aesthetic ke hisab se judge karta hai
4. **Agent 4** — Claude independently dobara verify karta hai (cross-check)
5. **Agent 5** — Claude portrait image design + SEO title/description/tags/alt-text banata hai
6. **Agent 6** (har 15 din) — Pinterest analytics dekh kar Agents 1,3,5 ke prompts khud rewrite karta hai

Roz ka output ek **Google Sheet** mein aata hai — aap phone se dekh kar 10-15 min
mein review + Pinterest pe post karte ho.

---

## STEP-BY-STEP SETUP (Laptop pe, EK BAAR karna hai)

### STEP 1 — GitHub Account + Repository

1. [github.com](https://github.com) pe free account banao (agar nahi hai)
2. "New Repository" banao — naam do jaise `pinterest-agent` — **Private** rakhna
   (taaki API keys se related koi cheez public na ho)
3. Is poore folder (jo maine banaya hai) ko apne naye GitHub repo mein upload karo:
   - GitHub website pe "Add file" → "Upload files" → sab files/folders drag-drop karo
   - Ya agar Git command-line pata hai: `git init`, `git add .`, `git commit`, `git push`

---

### STEP 2 — Gemini API Key

1. [aistudio.google.com](https://aistudio.google.com) pe jao
2. Google account se login karo
3. "Get API Key" → "Create API Key" pe click karo
4. Key copy kar lo (ye baad mein GitHub Secret mein daalni hai)

---

### STEP 3 — Claude API Key

1. [console.anthropic.com](https://console.anthropic.com) pe jao
2. Sign up karo (email verify karna hoga)
3. Left menu mein "API Keys" → "Create Key"
4. Key copy kar lo

---

### STEP 4 — Etsy API Key

1. [etsy.com/developers/register](https://www.etsy.com/developers/register) pe jao
2. "Create a New App" — koi bhi naam do (jaise "Lumiere Luxe Sourcing")
3. App type: "Personal use" select karo
4. Approval ke baad Keystring (API Key) mil jayegi

---

### STEP 5 — Etsy Affiliate Program (Commission ke liye — Developer API se ALAG hai)

1. [awin.com](https://www.awin.com) pe publisher account banao (free)
2. Awin ke andar "Etsy" merchant ko search karke apply karo affiliate program ke liye
3. Approval ke baad apna **Publisher ID** milega — ye `AWIN_PUBLISHER_ID` secret mein jayega

---

### STEP 6 — Google Sheets Setup (Service Account)

Ye thoda technical hai lekin ek baar ka kaam hai:

1. [console.cloud.google.com](https://console.cloud.google.com) pe jao, naya project banao
2. "APIs & Services" → "Enable APIs" → "Google Sheets API" enable karo, phir "Google Drive API" bhi enable karo
3. "Credentials" → "Create Credentials" → "Service Account" banao
4. Service account create hone ke baad, uspe click karo → "Keys" tab → "Add Key" → "JSON" — ek JSON file download hogi
5. Us JSON file ko text editor mein kholo, **poora content copy karo** (ye `GOOGLE_SERVICE_ACCOUNT_JSON` secret banega)
6. Ab Google Sheets mein jao, ek nayi Sheet banao (naam do "Lumiere Luxe Pins")
7. Us Sheet ko **share karo** us service account ke email address ke sath (JSON file ke andar `client_email` field mein milega) — Editor access do
8. Sheet ke URL se ID nikalo: `https://docs.google.com/spreadsheets/d/YAHAN_WALA_ID/edit` — ye `GOOGLE_SHEET_ID` secret banega

**Ye Sheet ka link hi aapka roz ka "address" hai** — ise phone mein bookmark kar lena.

---

### STEP 7 — Pinterest Access Token (Agent 6 ke liye)

1. [developers.pinterest.com](https://developers.pinterest.com) pe jao, app register karo
2. App approve hone ke baad OAuth se apna Pinterest Business account connect karo
3. Isse ek **Access Token** milega — ye `PINTEREST_ACCESS_TOKEN` secret banega

(Ye step thoda mushkil ho sakta hai — agar atko to bata dena, alag se detailed guide bana dunga)

---

### STEP 8 — Sab Keys ko GitHub Secrets mein Daalna (JAO KAAM PUCHA THA)

1. Apne GitHub repository pe jao
2. **Settings** tab pe click karo (repo ke andar, top mein)
3. Left sidebar mein **"Secrets and variables"** → **"Actions"** pe click karo
4. **"New repository secret"** button dabao
5. Ek-ek karke ye sab secrets add karo (Name aur Value dono daalne hain):

| Secret Name | Kahan se milega |
|---|---|
| `GEMINI_API_KEY` | Step 2 se |
| `CLAUDE_API_KEY` | Step 3 se |
| `ETSY_API_KEY` | Step 4 se |
| `AWIN_PUBLISHER_ID` | Step 5 se |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Step 6 se (poora JSON content paste karo) |
| `GOOGLE_SHEET_ID` | Step 6 se |
| `PINTEREST_ACCESS_TOKEN` | Step 7 se |

Har secret ke liye: "New repository secret" → Name daalo (exactly jaisa upar likha hai) → Value paste karo → "Add secret"

---

### STEP 9 — Reference Images Daalo

`assets/` folder mein apne 1-2 best-performing pins (jo 800+ clicks le rahe the)
ki images daalo, naam do `reference_pin_1.jpg`. Ye Agent 3 ke liye zaroori hai
taaki wo naye products ko isi style se compare kare.

---

### STEP 10 — Test Run

1. GitHub repo mein **"Actions"** tab pe jao
2. Left mein "Daily Pin Generation" workflow select karo
3. "Run workflow" button dabao (manual trigger)
4. 2-5 minute wait karo, phir apni Google Sheet check karo — naye rows aaye hain ya nahi

Agar error aaye, "Actions" tab mein us run pe click karke red/failed step dekho —
error message copy karke mujhe bhej dena, main fix bata dunga.

---

## ROZ KA KAAM (Phone se)

1. Subah Google Sheet kholo (bookmark kiya hua link)
2. Aaj ki date wali rows dekho (Date column se filter kar sakte ho)
3. Har row: Image + Title + Description + Hashtags dekho, check karo theek lagta hai
4. Pinterest app kholo → naya Pin banao → Sheet se copy-paste karo → image download karke upload karo → Affiliate link lagao → Post karo
5. Sheet mein "Status" column ko "Posted" kar do us row ka

---

## AUTOMATIC SCHEDULE

- **Daily Pipeline**: Roz raat 2 AM UTC (Pakistan subah ~7 AM) khud chalega
- **15-Day Optimizer**: Har mahine ki 1st aur 16th tareekh ko khud chalega, prompts update karega

Dono workflows GitHub Actions se **free** chalti hain (GitHub free tier mein
mahine ke 2000 minutes free milte hain — ye system usse bohot kam use karega).

---

## AGAR KUCH KAAM NA KARE

- **Etsy search results empty**: API key check karo, ya keyword bohot specific hoga
- **Sheet mein kuch nahi aa raha**: Service account email sheet share mein hai ya nahi check karo
- **Pinterest analytics fail**: Access token expire ho sakta hai, dobara generate karna padega

Kisi bhi step pe atko, exact error message ke sath poochna — turant fix batunga.
