#!/usr/bin/env python3
import json, re, time, html as html_lib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
DAILY_FILE = DATA / "daily-content.json"
ARCHIVE_FILE = DATA / "loi-bac-365.json"
QUOTE_HOME = "https://loibacday.com/"
MONTH_ARCHIVE = "https://loibacday.com/loi-bac-day-ngay-nay-nam-xua-thang-{month}/"
RSS_URL = "https://congbao.chinhphu.vn/cac-van-ban-moi-ban-hanh.rss"
TZ = ZoneInfo("Asia/Ho_Chi_Minh")
HEADERS = {"User-Agent": "BanCHQSCuPui-LearningPortal/1.1-V3.17 (daily educational content; contact site administrator)"}

def get(url):
    r = requests.get(url, headers=HEADERS, timeout=35)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text

def clean(s):
    return re.sub(r"\s+", " ", html_lib.unescape(s or "")).strip()

def quote_from_article(url, label):
    soup = BeautifulSoup(get(url), "html.parser")
    paras = [clean(p.get_text(" ", strip=True)) for p in soup.find_all("p")]
    paras = [p for p in paras if p]
    q_idx = next((i for i,p in enumerate(paras) if p.startswith(("“", '"', "‘", "…", "...")) and len(p) > 12), None)
    if q_idx is None:
        raise ValueError("Không tìm thấy đoạn trích dẫn trong bài " + url)
    quote = paras[q_idx]
    source = ""
    meaning_parts = []
    for p in paras[q_idx+1:]:
        if not source and any(k in p.lower() for k in ("là lời", "đây là lời", "đây là sự", "lời dạy", "lời khẳng định", "đó là lời", "được trích")):
            source = p
        elif source and len(p) > 50:
            meaning_parts.append(p)
        if len(meaning_parts) >= 3:
            break
    return {
        "quote": quote,
        "source": source or "Xem xuất xứ trong bài viết gốc.",
        "meaning": " ".join(meaning_parts)[:1800],
        "url": url,
        "label": label
    }

def parse_listing_page(url):
    soup = BeautifulSoup(get(url), "html.parser")
    found = {}
    links = soup.find_all("a", href=re.compile(r"/loi-bac-day-ngay-nay-nam-xua/"))
    for a in links:
        title = clean(a.get_text(" ", strip=True))
        m = re.search(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})", title, re.I)
        if not m:
            continue
        day, month = int(m.group(1)), int(m.group(2))
        key = f"{month:02d}-{day:02d}"
        href = a.get("href", "")
        if href.startswith("/"):
            href = "https://loibacday.com" + href
        if not href.startswith("https://loibacday.com/"):
            continue
        heading = a.find_parent(["h2", "h3", "h4"])
        candidate = heading.parent if heading else a.parent
        paragraphs = []
        node = candidate
        for _ in range(4):
            if node is None:
                break
            paragraphs = [clean(p.get_text(" ", strip=True)) for p in node.find_all("p")]
            paragraphs = [p for p in paragraphs if p]
            if any(p.startswith(("“", '"', "‘", "…", "...")) for p in paragraphs):
                break
            node = node.parent
        q = next((p for p in paragraphs if p.startswith(("“", '"', "‘", "…", "...")) and len(p)>12), "")
        if not q:
            continue
        source = next((p for p in paragraphs[paragraphs.index(q)+1:] if any(k in p.lower() for k in ("là lời", "đây là lời", "lời dạy", "lời khẳng định", "được trích", "đó là lời"))), "")
        found[key] = {"label": f"{day:02d}/{month:02d}", "quote": q, "source": source or "Xem xuất xứ trong bài viết gốc.", "url": href, "date": ""}
    return found

def backfill_archive(entries):
    # Lấy kho theo từng tháng từ chính chuyên mục nguồn; mỗi trang phân trang được thử tối đa 5 lần.
    # Dừng sớm khi gặp hai trang liên tiếp không có bài, tránh gọi thừa.
    for month in range(1, 13):
        empty_pages = 0
        base = MONTH_ARCHIVE.format(month=month)
        for page in range(1, 6):
            url = base if page == 1 else base + f"page-{page}/"
            try:
                found = parse_listing_page(url)
                if found:
                    entries.update(found)
                    empty_pages = 0
                else:
                    empty_pages += 1
                    if empty_pages >= 2:
                        break
            except Exception as e:
                empty_pages += 1
                print(f"WARNING: Không đọc được kho lời Bác tháng {month}, trang {page}: {e}")
                if empty_pages >= 2:
                    break
            time.sleep(0.12)
    return entries

def fetch_current_quote(now, archive):
    soup = BeautifulSoup(get(QUOTE_HOME), "html.parser")
    links = soup.find_all("a", href=re.compile(r"/loi-bac-day-ngay-nay-nam-xua/"))
    chosen = None
    for a in links:
        title = clean(a.get_text(" ", strip=True))
        m = re.search(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})", title, re.I)
        if m and int(m.group(1)) == now.day and int(m.group(2)) == now.month:
            chosen = a
            break
    if not chosen:
        # Fallback: author archive can still supply the exact day/month entry.
        key = f"{now.month:02d}-{now.day:02d}"
        if key in archive:
            item = archive[key].copy()
            item["date"] = now.date().isoformat()
            item["meaning"] = ""
            return item
        raise RuntimeError("Trang nguồn chưa có bài tương ứng ngày hôm nay; giữ nguyên dữ liệu hôm trước.")
    href = chosen.get("href", "")
    if href.startswith("/"):
        href = "https://loibacday.com" + href
    title = clean(chosen.get_text(" ", strip=True))
    item = quote_from_article(href, title)
    item["date"] = now.date().isoformat()
    return item

def parse_rss():
    raw = get(RSS_URL)
    root = ET.fromstring(raw)
    records = []
    for node in root.iter():
        if node.tag.split("}")[-1].lower() not in ("item", "entry"):
            continue
        fields = {}
        for child in list(node):
            tag = child.tag.split("}")[-1].lower()
            fields[tag] = clean("".join(child.itertext()))
            if tag == "link" and not fields[tag]:
                fields[tag] = child.attrib.get("href", "")
        title = fields.get("title", "")
        link = fields.get("link", "")
        desc = BeautifulSoup(fields.get("description", fields.get("summary", "")), "html.parser").get_text(" ", strip=True)
        pub = fields.get("pubdate", fields.get("published", fields.get("updated", "")))
        if not title or not link:
            continue
        published = ""
        try:
            published = parsedate_to_datetime(pub).astimezone(TZ).strftime("%d/%m/%Y") if pub else ""
        except Exception:
            published = pub[:30]
        effective = ""
        m = re.search(r"(?:có hiệu lực|hiệu lực)\s*(?:kể từ|từ)?\s*ngày\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})", desc, re.I)
        if m:
            effective = m.group(1)
        title_low = (title + " " + desc).lower()
        keywords = ("quốc phòng","quân sự","dân quân","dự bị động viên","nghĩa vụ quân sự","lực lượng vũ trang","quân đội","cán bộ","công chức","viên chức","chính quyền địa phương","ngân sách","phổ biến, giáo dục pháp luật","xử phạt","an ninh")
        score = sum(1 for k in keywords if k in title_low)
        records.append({
            "title": title, "url": link, "description": desc[:700],
            "published": published, "effective_date": effective,
            "type": "ƯU TIÊN QUỐC PHÒNG, QUÂN SỰ" if score else "VĂN BẢN MỚI",
            "_score": score, "_pub": pub
        })
    records.sort(key=lambda x: (x["_score"], x["_pub"]), reverse=True)
    for x in records:
        x.pop("_score", None); x.pop("_pub", None)
    return records[:12]

def main():
    now = datetime.now(TZ)
    daily = json.loads(DAILY_FILE.read_text(encoding="utf-8")) if DAILY_FILE.exists() else {}
    archive_doc = json.loads(ARCHIVE_FILE.read_text(encoding="utf-8")) if ARCHIVE_FILE.exists() else {"entries": {}}
    archive = archive_doc.get("entries", {})
    print("Đang đồng bộ và bổ sung kho lời Bác từ danh mục nguồn...")
    archive = backfill_archive(archive)
    try:
        current = fetch_current_quote(now, archive)
        key = f"{now.month:02d}-{now.day:02d}"
        archive[key] = {**archive.get(key, {}), **current}
        daily["quote"] = current
    except Exception as e:
        print("WARNING: Không cập nhật được lời Bác hôm nay:", e)
    try:
        laws = parse_rss()
        if laws:
            daily["laws"] = laws
    except Exception as e:
        print("WARNING: Không cập nhật được RSS pháp luật:", e)
    daily["updated_at"] = now.isoformat(timespec="minutes")
    daily["sources"] = {"quote": QUOTE_HOME, "laws": RSS_URL, "legal_database": "https://vbpl.vn/"}
    archive_doc["updated_at"] = now.isoformat(timespec="minutes")
    archive_doc["entries"] = archive
    DAILY_FILE.write_text(json.dumps(daily, ensure_ascii=False, indent=2), encoding="utf-8")
    ARCHIVE_FILE.write_text(json.dumps(archive_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã cập nhật. Kho lời Bác hiện có {len(archive)} ngày; tin pháp luật: {len(daily.get('laws', []))} mục.")

if __name__ == "__main__":
    main()
