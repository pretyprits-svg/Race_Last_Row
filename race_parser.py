import re, math, pdfplumber
try:
    import fitz  # PyMuPDF
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

MONTH_RE  = re.compile(r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b')
DIST_RE   = re.compile(r'(\d{2})m[A-Za-z0-9]*')
RTIME_RE  = re.compile(r'\b(\d)-(\d{2}\.\d{2})\b')
DMET_RE   = re.compile(r'(\d{4})\s*Mts\.')
HORSE_RE  = re.compile(r'^(\d+)\.\s+([A-Z][A-Z\s\.\-\/\']+?)\s+(\d+\.?\d*)')
# Pattern to extract weight allowance like "(-2.5)" or "(-3)"
WEIGHT_ALLOWANCE_RE = re.compile(r'\((-?\d+\.?\d*)\)')

def parse_odds(token):
    if not token: return 0
    token = re.sub(r'^[xXsS]', '', token.strip())
    if '/' in token:
        p = token.split('/')
        try: return round(float(p[0]) / float(p[1]), 2)
        except: return 0
    try: return float(token)
    except: return 0

def parse_record(line):
    if not MONTH_RE.search(line): return None
    dm = DIST_RE.search(line)
    if not dm: return None
    rt_m = RTIME_RE.search(line)
    if not rt_m: return None

    date_m = MONTH_RE.search(line)
    between = line[date_m.end():dm.start()].strip()
    tokens = between.split()
    odds_tok = None
    for t in tokens:
        if re.match(r'^[a-zA-Z]+$', t) and len(t) <= 3: continue
        if re.match(r'^[xXsS]?\d', t):
            odds_tok = t; break
    odds = parse_odds(odds_tok)

    distance = int(dm.group(1)) * 100
    rest = line[dm.end():]
    wm = re.search(r'(\d+\.?\d*)', rest)
    if not wm: return None
    weight = float(wm.group(1))

    win_min = int(rt_m.group(1))
    win_sec = float(rt_m.group(2))
    after_rt = line[rt_m.end():].strip()
    pnr_m = re.match(r'(\d+(?:\.\d+)?)', after_rt)
    if not pnr_m: return None
    pnr = float(pnr_m.group(1))

    after_pnr = after_rt[pnr_m.end():].strip()
    ht_m = re.match(r'(\d{2}\.\d{2})f?', after_pnr)
    if not ht_m: return None
    ht_sec = float(ht_m.group(1))
    mins = win_min + (1 if ht_sec < win_sec else 0)
    horse_time = round(mins * 60 + ht_sec, 2)

    return {'distance': distance, 'weight': weight,
            'pnr': pnr, 'horse_time': horse_time, 'odds': odds}

# Global EasyOCR reader (initialized once for performance)
_easy_ocr_reader = None

def get_easyocr_reader():
    """Get or create EasyOCR reader instance."""
    global _easy_ocr_reader
    if _easy_ocr_reader is None and EASYOCR_AVAILABLE:
        import easyocr
        print("  🔍 Initializing EasyOCR (this may take a moment)...")
        _easy_ocr_reader = easyocr.Reader(['en'], gpu=False)
    return _easy_ocr_reader

def extract_text_from_pdf(file_path):
    """Extract text from PDF - tries pdfplumber first, falls back to OCR if needed."""
    all_text = []

    # Try pdfplumber first
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)

    # If we got text, return it
    if all_text and any(len(t.strip()) > 100 for t in all_text):
        return all_text

    # No text found - try OCR if available
    if not OCR_AVAILABLE:
        print("⚠️  PDF has no extractable text and OCR libraries not installed.")
        print("Install with: py -m pip install pymupdf")
        return []

    print("📷 PDF appears to be image-based. Using OCR to extract text...")

    # Use PyMuPDF to convert pages to images and OCR them
    ocr_text = []

    if not EASYOCR_AVAILABLE:
        print("  ⚠️ EasyOCR not installed. Install with: py -m pip install easyocr")
        return []

    try:
        from PIL import Image
        import numpy as np

        # Get EasyOCR reader
        reader = get_easyocr_reader()
        if not reader:
            print("  ❌ Failed to initialize EasyOCR")
            return []

        doc = fitz.open(file_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render page to image (higher DPI = better OCR accuracy)
            pix = page.get_pixmap(dpi=200)  # Lower DPI for faster processing
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Convert PIL image to numpy array for EasyOCR
            img_np = np.array(img)

            # Perform OCR
            result = reader.readtext(img_np, detail=0)  # detail=0 returns only text
            text = '\n'.join(result)

            print(f"  ✓ OCR page {page_num + 1}/{len(doc)} - extracted {len(text)} chars")
            ocr_text.append(text)

        doc.close()
        return ocr_text
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def parse_pdf(file_path):
    races, current_race, current_horse = [], None, None

    def save_horse():
        if current_horse and current_race:
            current_race['horses'].append(current_horse)

    def save_race():
        save_horse()
        if current_race:
            races.append(current_race)

    # Extract text (with OCR fallback if needed)
    page_texts = extract_text_from_pdf(file_path)

    if not page_texts:
        print("❌ Could not extract any text from PDF")
        return []

    # Parse the extracted text
    for text in page_texts:
        if not text: continue
        lines = text.split('\n')
        for i, raw in enumerate(lines):
            line = raw.strip()
            dm = DMET_RE.search(line)
            if dm and current_race:
                current_race['current_dist'] = int(dm.group(1))

            rh = re.match(r'^(\d+)\s*$', line)
            if rh and i + 1 < len(lines) and lines[i+1].strip().startswith('('):
                save_race()
                current_race = {'race_num': int(rh.group(1)),
                                'race_name': lines[i+1].strip(),
                                'current_dist': 1100, 'horses': []}
                current_horse = None
                continue

            hm = HORSE_RE.match(line)
            if hm and current_race:
                save_horse()
                horse_num = int(hm.group(1))
                horse_name = hm.group(2).strip()
                base_weight = float(hm.group(3))  # This is the HORSE weight from first line

                # Look for jockey allowance in next 5 lines
                # Format: "55 (-2.5) A" where 55 is jockey weight, (-2.5) is allowance
                # ONLY subtract if there's a NEGATIVE value in brackets
                allowance = 0.0

                # Search next 5 lines for allowance pattern like (-2.5) or (-3)
                for offset in range(1, 6):
                    if i + offset < len(lines):
                        search_line = lines[i + offset].strip()
                        allowance_match = WEIGHT_ALLOWANCE_RE.search(search_line)
                        if allowance_match:
                            # Extract allowance value (e.g., -2.5 from "(-2.5)")
                            allowance_value = float(allowance_match.group(1))

                            # ONLY apply if it's negative (like -2.5, -3)
                            if allowance_value < 0:
                                allowance = abs(allowance_value)  # Convert -2.5 to 2.5
                            break

                # Calculate final weight: horse_weight - allowance (allowance is 0 if no negative found)
                final_weight = base_weight - allowance

                current_horse = {'num': horse_num,
                                 'name': horse_name,
                                 'new_weight': final_weight,
                                 'records': []}
                continue

            if current_horse:
                rec = parse_record(line)
                if rec:
                    current_horse['records'].append(rec)

    save_race()
    return races

def compute_race(race, std_pnr=3.5):
    cur_dist = race['current_dist']
    rows = []
    for h in race['horses']:
        recs = h['records']
        if not recs:
            rows.append({'Sl.No': h['num'], 'Name': h['name'] + ' ⚠️ First Timer',
                         'Old Weight': 'NA', 'New Weight': h['new_weight'],
                         'Old Distance': 'NA', 'Current Distance': cur_dist,
                         'Old Time(sec)': 'NA', 'PNR Race': 'NA',
                         'Standard PNR': 'NA', 'Adjusted Time': 'NA',
                         'Speed Rating': 'NA', 'ODDS': 'NA',
                         'Final Rating': 'NA', 'Speed Rank': 'NA',
                         'Odds Rank': 'NA', 'Value Score': 'NA'})
            continue
        latest = recs[-1]
        old_w  = latest['weight']
        old_d  = latest['distance']
        old_t  = latest['horse_time']
        old_p  = latest['pnr']
        odds   = latest['odds']
        adj_t  = round(old_t - (old_d - cur_dist)*0.0625 - (old_w - h['new_weight'])/10 - (old_p - std_pnr)*2, 2)
        sr     = math.ceil((cur_dist / adj_t)*100 - 1000) if adj_t > 0 else 0
        rows.append({'Sl.No': h['num'], 'Name': h['name'],
                     'Old Weight': old_w, 'New Weight': h['new_weight'],
                     'Old Distance': old_d, 'Current Distance': cur_dist,
                     'Old Time(sec)': old_t, 'PNR Race': old_p,
                     'Standard PNR': std_pnr, 'Adjusted Time': adj_t,
                     'Speed Rating': sr, 'ODDS': odds,
                     'Final Rating': 0, 'Speed Rank': 0, 'Odds Rank': 0, 'Value Score': 0})

    valid = [r for r in rows if isinstance(r['Speed Rating'], (int, float)) and r['Speed Rating'] != 0]
    speeds = sorted(set(r['Speed Rating'] for r in valid), reverse=True)
    odds_s = sorted(set(r['ODDS'] for r in valid))
    for r in valid:
        r['Speed Rank'] = speeds.index(r['Speed Rating']) + 1
        r['Odds Rank']  = odds_s.index(r['ODDS']) + 1
        r['Final Rating'] = round(r['Speed Rating'] * (1/(r['ODDS']+1)), 2) if r['ODDS'] else 0
        r['Value Score']  = round(r['Speed Rank']/r['Odds Rank'], 2) if r['Odds Rank'] else 0
    return rows
