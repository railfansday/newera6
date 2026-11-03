import sqlite3
import os
import re
import json
import html as html_mod
from pathlib import Path
from datetime import datetime

# ==========================================================================
# KONFIGURASI
# ==========================================================================
BASE_DIR = Path(__file__).parent.resolve()
DB_PATH = str(BASE_DIR / "database_hasil5" / "database.sqlite")
OUTPUT_DIR = str(BASE_DIR)

# ⚠️ GANTI DENGAN URL GITHUB PAGES ANDA
BASE_URL = "https://railfansday.github.io/newera6" 

SITE_NAME = "Portal Berita Indonesia"

# ==========================================================================
# HELPER
# ==========================================================================
def esc(text):
    return html_mod.escape(str(text)) if text else ""

def format_date(date_str):
    if not date_str:
        return "-"
    try:
        return datetime.fromisoformat(str(date_str).replace('Z', '+00:00')).strftime('%d %B %Y')
    except:
        return str(date_str)[:10]

# ==========================================================================
# TEMPLATE HTML DENGAN SEO ON-PAGE
# ==========================================================================
def render_article_page(artikel_id, judul, konten, gambar, tanggal_publish, link_sumber):
    """Membuat satu file HTML untuk satu artikel dengan optimasi SEO maksimal."""
    
    # 1. Meta Title (50-60 karakter, unik, topik di depan)
    meta_title = f"{judul[:55]}..." if len(judul) > 55 else judul
    meta_title = f"{meta_title} | {SITE_NAME}"
    
    # 2. Meta Description (120-160 karakter, spesifik, memancing klik)
    # Ambil cuplikan teks dari konten (bersihkan tag HTML)
    clean_text = re.sub(r'<[^>]+>', ' ', konten) # Hapus tag HTML
    clean_text = re.sub(r'\s+', ' ', clean_text).strip() # Rapikan spasi
    meta_desc = clean_text[:155] + "..." if len(clean_text) > 155 else clean_text
    if not meta_desc:
        meta_desc = f"Baca berita terbaru tentang {judul} di {SITE_NAME}."
    
    # 3. URL Kanonis (mutlak, https, tanpa parameter)
    canonical_url = f"{BASE_URL}/artikel_{artikel_id}.html"
    
    # 4. Gambar (jika ada)
    img_tag = ""
    if gambar:
        img_tag = f'<img src="{esc(gambar)}" alt="{esc(judul)}" style="max-width:100%; height:auto; border-radius:8px; margin-bottom:20px;" loading="lazy">'
    
    # 5. Schema Markup NewsArticle (JSON-LD) untuk Rich Snippets
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": judul[:110],
        "image": [gambar] if gambar else [],
        "datePublished": tanggal_publish or datetime.now().isoformat(),
        "dateModified": tanggal_publish or datetime.now().isoformat(),
        "author": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": BASE_URL
        },
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "logo": {
                "@type": "ImageObject",
                "url": f"{BASE_URL}/logo.png",
                "width": 600,
                "height": 60
            }
        },
        "description": meta_desc,
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": canonical_url
        },
        "url": link_sumber  # Sumber asli
    }
    schema_json = json.dumps(schema, ensure_ascii=False)

    # 6. Struktur HTML
    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
    
    <title>{esc(meta_title)}</title>
    <meta name="description" content="{esc(meta_desc)}">
    <link rel="canonical" href="{esc(canonical_url)}">
    
    <!-- Open Graph untuk Media Sosial -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{esc(meta_title)}">
    <meta property="og:description" content="{esc(meta_desc)}">
    <meta property="og:url" content="{esc(canonical_url)}">
    <meta property="og:site_name" content="{esc(SITE_NAME)}">
    <meta property="og:image" content="{esc(gambar) if gambar else ''}">
    
    <!-- Schema JSON-LD -->
    <script type="application/ld+json">
    {schema_json}
    </script>
    
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.7; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }}
        .container {{ background: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
        .back-link {{ display: inline-block; margin-bottom: 20px; color: #0066cc; text-decoration: none; font-weight: 500; }}
        .back-link:hover {{ text-decoration: underline; }}
        h1 {{ font-size: 28px; color: #1a1a1a; margin-bottom: 10px; line-height: 1.3; }}
        .meta {{ font-size: 14px; color: #666; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px; }}
        .content img {{ max-width: 100%; height: auto; border-radius: 8px; }}
        .content p {{ margin-bottom: 15px; }}
        .ad-container {{ margin: 30px 0; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-link">&larr; Kembali ke Daftar Berita</a>
        
        <h1>{esc(judul)}</h1>
        
        <div class="meta">
            📅 {format_date(tanggal_publish)} | Sumber: <a href="{esc(link_sumber)}" target="_blank" rel="nofollow noopener">Baca Asli</a>
        </div>
        
        <div class="content">
            {img_tag}
            {konten}
        </div>
        
        <div class="ad-container">
            <script type="text/javascript">
                atOptions = {{'key' : 'f9e40eb3b3cd05f1038aac7b36b33ad2','format' : 'iframe','height' : 90,'width' : 728,'params' : {{}}}};
            </script>
            <script type="text/javascript" src="https://upholdbrilliancerecast.com/f9e40eb3b3cd05f1038aac7b36b33ad2/invoke.js"></script>
        </div>
    </div>
</body>
</html>"""
    return html

# ==========================================================================
# FUNGSI UTAMA EXPORT
# ==========================================================================
def jalankan_export():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database tidak ditemukan di {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, judul, konten, gambar, tanggal_publish, link FROM artikel ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("Tidak ada artikel di database.")
        return

    print(f"[*] Membuat {len(rows)} file HTML (1 artikel per file) dengan SEO...")

    # 1. BUAT FILE HTML UNTUK SETIAP ARTIKEL
    for item in rows:
        artikel_id, judul, konten, gambar, tanggal, link_sumber = item
        
        # Render halaman
        html_content = render_article_page(artikel_id, judul, konten, gambar, tanggal, link_sumber)
        
        # Simpan file
        filename = f"artikel_{artikel_id}.html"
        with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
            f.write(html_content)

    # 2. BUAT INDEX.HTML (Daftar Berita)
    index_html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SITE_NAME} - Daftar Berita Terkini</title>
    <meta name="description" content="Kumpulan berita terbaru dan terpopuler hari ini. Update informasi terkini seputar peristiwa nasional dan internasional.">
    <link rel="canonical" href="{BASE_URL}/index.html">
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f4f4f9; }}
        .container {{ max-width: 800px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 10px; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
        a {{ text-decoration: none; color: #0066cc; font-size: 18px; font-weight: bold; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Daftar Berita Terkini</h1>
        <ul>
"""
    for item in rows:
        artikel_id, judul, konten, gambar, tanggal, link = item
        index_html += f'        <li><a href="artikel_{artikel_id}.html">{esc(judul)}</a></li>\n'
    
    index_html += """        </ul>
    </div>
</body>
</html>"""
    
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # 3. BUAT SITEMAP.XML (Hanya URL Kanonis)
    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        # Homepage
        f.write(f'    <url><loc>{BASE_URL}/</loc><priority>1.0</priority></url>\n')
        # Setiap Artikel
        for item in rows:
            f.write(f'    <url><loc>{BASE_URL}/artikel_{item[0]}.html</loc><priority>0.8</priority></url>\n')
        f.write('</urlset>')

    # 4. BUAT ROBOTS.TXT
    with open(os.path.join(OUTPUT_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n\n")
        f.write(f"Sitemap: {BASE_URL}/sitemap.xml\n")

    print(f"[SELESAI] Berhasil membuat {len(rows)} file HTML + sitemap.xml + robots.txt")

if __name__ == "__main__":
    jalankan_export()
