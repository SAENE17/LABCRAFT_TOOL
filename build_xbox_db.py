import csv
import io
import json
import urllib.request

CSV_URL = "https://raw.githubusercontent.com/xboxoneresearch/errorcodes/main/postcodes.csv"

def parse_console_mask(console_str):
    mask = 0
    c_lower = console_str.lower()
    
    # 1=Fat, 2=One S, 4=One X, 8=Series S, 16=Series X
    if "phat" in c_lower or "fat" in c_lower or "original" in c_lower:
        mask |= (1 << 0)
    if "one s" in c_lower:
        mask |= (1 << 1)
    if "one x" in c_lower:
        mask |= (1 << 2)
    if "series s" in c_lower:
        mask |= (1 << 3)
    if "series x" in c_lower:
        mask |= (1 << 4)
        
    if mask == 0 or "all" in c_lower:
        mask = 0xFF
        
    return mask

def main():
    print(f"Descargando postcodes.csv desde {CSV_URL}...")
    req = urllib.request.Request(CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    csv_text = response.read().decode('utf-8', errors='ignore')

    reader = csv.DictReader(io.StringIO(csv_text))
    entries = []
    seen = set()

    for row in reader:
        raw_code = row.get("Code", "").strip()
        name = row.get("Name", "").strip()
        desc = row.get("Description", "").strip()
        consoles = row.get("Console", "").strip()

        if not raw_code:
            continue

        clean_code = raw_code.split()[0].upper()
        if not clean_code.startswith("0X"):
            clean_code = "0X" + clean_code.zfill(4)

        mask = parse_console_mask(consoles)
        final_desc = name if name else "POST CODE"
        final_cause = desc if desc else "Falla en etapa de arranque"

        key = (clean_code, mask, final_desc)
        if key in seen:
            continue
        seen.add(key)

        entries.append({
            "c": clean_code,
            "m": mask,
            "d": final_desc[:31],
            "r": final_cause[:47]
        })

    out_file = "xbox_codes.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, separators=(',', ':'), ensure_ascii=False)

    print(f"Completado con exito: {len(entries)} codigos generados en {out_file}")

if __name__ == "__main__":
    main()