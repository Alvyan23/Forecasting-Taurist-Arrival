import os
import io
import re
import base64
import requests
import folium
import streamlit as st
import streamlit.components.v1 as components
from html import unescape
from urllib.parse import urlparse, parse_qs, urljoin

# ============================================================
# KONFIGURASI
# ============================================================
st.set_page_config(
    page_title="Prediksi Kunjungan Wisatawan Kabupaten Bangkalan",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "page" not in st.session_state:
    st.session_state.page = "landing"
if "role" not in st.session_state:
    st.session_state.role = None

ADMIN_USER = "admin"
ADMIN_PASS = "admin"
NAMA_PENGEMBANG = "Alvyan Maulana Karnawan Putra"
PETA_STYLE = "google"           # "google" atau "osm"

# Warna "biru teknik" untuk logo yang diberi "recolor": True (R, G, B)
TEKNIK_BLUE = (30, 136, 229)

ASSETS = "assets"
os.makedirs(ASSETS, exist_ok=True)

# ============================================================
# LOGO KIRI ATAS (urutan dari kiri ke kanan)
# "file"   : nama file di assets/ (dipakai lebih dulu jika ada)
# "url"    : link gambar ATAU link halaman (gambar dicari otomatis)
# "dark"   : True -> logo diberi latar biru tua gelap (untuk logo berwarna putih)
# "recolor": True -> hitam jadi putih, putih jadi biru teknik
# ============================================================
LOGOS = [
    {"file": "logo_utm.jpg", "h": 50, "dark": False, "recolor": False,
     "url": "https://www.instagram.com/p/De83c8qSJ6v/?exln=aWtueWYxaDk4ZDEw"},
    {"file": "logo_ft.png", "h": 46, "dark": False, "recolor": False,
     "url": "https://www.instagram.com/p/De83lZQSI8g/?srtk=MWg1eDc0ZjJ6dHhndA=="},
    {"file": "logo_si.png", "h": 46, "dark": False, "recolor": False,
     "url": "https://sivitas.sakera.id/images/logo-si.png"},
    {"file": "logo_bangkalan.jpg", "h": 52, "dark": False, "recolor": False,
     "url": "https://www.instagram.com/p/De832OMy3TG/?rpxt=YzY5bTdvaHVqNnlt"},
]

# ============================================================
# DATA DESTINASI
# ============================================================
DESTINASI = [
    {"nama": "Makam Syaikhona Kholil", "file": "syaikhona_kholil.jpg", "tag": "Wisata Religi",
     "icon": "🕌", "grad": "#0ea5e9,#0d9488", "color": "#ef4444",
     "url": "https://www.instagram.com/p/DXOb8I5k0WR/",
     "desk": "Makam ulama besar Madura, destinasi wisata religi utama di Bangkalan.",
     "lat": -7.0450, "lon": 112.7340},
    {"nama": "Kolla Langgundi", "file": "langgundi.jpg", "tag": "Wisata Religi",
     "icon": "🏛️", "grad": "#f59e0b,#ef4444", "color": "#f97316",
     "url": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh92G0yWlNc1fnYnq_qm52Dl195gR47Im6Ac5jJS47uz8aSiSq7wx7d1ojxVkuGp1ao_cyu9KeKJnkBti8n3nCErAjmT08oSEvXKNhTJRS6O9ZrIB7b6n9lpI6bzTwThx-_uWkKcd3pUKht/w640-h480-c/Wisata+Religi+Sultan+Abdul+Kadirun+Bangkalan.jpg",
     "desk": "Kawasan wisata sejarah dan budaya khas Bangkalan.",
     "lat": -7.0300, "lon": 112.7600},
    {"nama": "Makam Sunan Cendana", "file": "cendana.jpg", "tag": "Wisata Religi",
     "icon": "🌿", "grad": "#10b981,#0284c7", "color": "#22c55e",
     "url": "https://www.haibunda.com/moms-life/20210726124816-77-228535/9-potret-astana-giribangun-makam-keluarga-cendana-dilengkapi-masjid-pasar",
     "desk": "Wisata religi yang ramai dikunjungi peziarah dari berbagai daerah.",
     "lat": -7.0100, "lon": 112.7900},
    {"nama": "Makam Air Mata Ibu", "file": "air_mata_ibu.jpg", "tag": "Wisata Religi",
     "icon": "🕊️", "grad": "#8b5cf6,#ec4899", "color": "#a855f7",
     "url": "https://awsimages.detik.net.id/community/media/visual/2025/09/13/situs-makam-air-mata-ratu-ibu-1757752879199_169.png?w=1200",
     "desk": "Makam Air Mata Ibu, destinasi wisata religi dengan nilai sejarah tinggi.",
     "lat": -7.0000, "lon": 112.8000},
    {"nama": "Gunung Geger", "file": "gunung_geger.jpg", "tag": "Wisata Alam",
     "icon": "⛰️", "grad": "#22c55e,#0d9488", "color": "#0284c7",
     "url": "https://kataomed.com/wp-content/uploads/2023/03/Camping-Ground-Geger-Bintang-Photo-by-Wisatainfo-e1680515282467.jpg",
     "desk": "Destinasi wisata alam dengan jalur susur alam yang asri.",
     "lat": -7.1000, "lon": 112.9300},
]


# ============================================================
# HELPER UMUM
# ============================================================
def html(s: str):
    """Render HTML tanpa indentasi/baris kosong (hindari bug code-block markdown)."""
    s = "\n".join(l.strip() for l in s.splitlines() if l.strip())
    st.markdown(s, unsafe_allow_html=True)


def goto(page: str, role=None):
    st.session_state.page = page
    if role is not None or page in ("landing", "login"):
        st.session_state.role = role
    st.rerun()


# ============================================================
# HELPER GAMBAR
# ============================================================
UA_BROWSER = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
UA_CRAWLER = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"


def clean_url(url: str) -> str:
    """Jika berupa link Google 'imgres', ambil alamat gambar aslinya (parameter imgurl)."""
    if url and "google." in url and "/imgres" in url:
        q = parse_qs(urlparse(url).query)
        if q.get("imgurl"):
            return q["imgurl"][0]
    return url


def looks_like_image(url: str) -> bool:
    return bool(re.search(r"\.(jpe?g|png|webp|gif)(\?|$)", url, re.I))


def sniff_mime(data: bytes):
    """Mengembalikan mime jika data benar-benar gambar, selain itu None."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data[:4] == b"GIF8":
        return "image/gif"
    return None


def shrink(data: bytes, max_side: int = 900) -> bytes:
    """Perkecil gambar. Transparansi (PNG) dipertahankan."""
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(data))
        has_alpha = im.mode in ("RGBA", "LA") or "transparency" in im.info
        im = im.convert("RGBA" if has_alpha else "RGB")
        im.thumbnail((max_side, max_side))
        buf = io.BytesIO()
        if has_alpha:
            im.save(buf, format="PNG", optimize=True)
        else:
            im.save(buf, format="JPEG", quality=85)
        return buf.getvalue()
    except Exception:
        return data


def recolor_logo(data: bytes, blue=TEKNIK_BLUE) -> bytes:
    """Hitam -> putih, putih -> biru teknik (abu-abu diinterpolasi halus).
    Piksel berwarna (mis. kuning/merah) tidak diubah."""
    try:
        import numpy as np
        from PIL import Image
        im = Image.open(io.BytesIO(data)).convert("RGBA")
        a = np.array(im).astype(np.float32)
        rgb = a[..., :3]
        mx, mn = rgb.max(axis=2), rgb.min(axis=2)
        sat = (mx - mn) / (mx + 1e-6)
        lum = rgb.mean(axis=2) / 255.0
        gray = sat < 0.25
        white = np.array([255, 255, 255], dtype=np.float32)
        blu = np.array(blue, dtype=np.float32)
        t = lum[..., None]
        mixed = (1 - t) * white + t * blu
        out = a.copy()
        out[..., :3] = np.where(gray[..., None], mixed, rgb)
        buf = io.BytesIO()
        Image.fromarray(out.astype(np.uint8), "RGBA").save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return data


def to_uri(data: bytes) -> str:
    return f"data:{sniff_mime(data)};base64,{base64.b64encode(data).decode()}"


def find_image_in_html(text: str, base: str):
    """Cari alamat gambar utama di sebuah halaman web (logo organisasi / og:image / logo)."""
    pola = [
        r'<img[^>]+src=["\']([^"\']*uploads/(?:group|organization)/[^"\']+)',
        r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)',
        r'<img[^>]+src=["\']([^"\']*(?:uploads|logo)[^"\']*\.(?:png|jpe?g|webp)(?:\.crdownload)?)',
    ]
    for p in pola:
        m = re.search(p, text, re.I)
        if m:
            return urljoin(base, unescape(m.group(1)))
    return None


def download(url: str, depth: int = 0):
    """Unduh gambar. Jika URL berupa halaman web, cari gambarnya otomatis.
    Return (bytes, error)."""
    origin = "{u.scheme}://{u.netloc}/".format(u=urlparse(url))
    kandidat = [url]
    m = re.search(r"instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)", url)
    if m:   # Instagram: coba endpoint media dulu
        kandidat = [f"https://www.instagram.com/p/{m.group(1)}/media/?size=l", url]

    variasi = [
        {"User-Agent": UA_BROWSER, "Accept": "image/avif,image/webp,image/*,*/*;q=0.8"},
        {"User-Agent": UA_BROWSER, "Referer": origin, "Accept": "text/html,image/*,*/*;q=0.8"},
        {"User-Agent": UA_CRAWLER, "Accept": "text/html,*/*"},
    ]
    last = "tidak diketahui"
    for cand in kandidat:
        for h in variasi:
            try:
                r = requests.get(cand, headers=h, timeout=8, allow_redirects=True)
                if r.status_code != 200:
                    last = f"HTTP {r.status_code}"
                    continue
                if sniff_mime(r.content):
                    return r.content, None
                if depth < 1 and "text/html" in r.headers.get("Content-Type", ""):
                    img_url = find_image_in_html(r.text, cand)
                    if img_url:
                        data, err = download(img_url, depth + 1)
                        if data:
                            return data, None
                        last = err or last
                        continue
                last = "respons bukan gambar (halaman diblokir / butuh login)"
            except Exception as e:
                last = type(e).__name__
    return None, last


def get_image(file: str, url: str, resize: bool, label: str,
              recolor: bool = False, max_side: int = 900):
    """
    Urutan: (1) file lokal valid -> (2) unduh lalu simpan -> (3) link langsung ke browser -> None.
    Hasil disimpan di session_state agar tidak mengunduh ulang tiap rerun.
    """
    cache = st.session_state.setdefault("_img_cache", {})
    status = st.session_state.setdefault("_img_status", {})
    if file in cache:
        return cache[file]

    path = os.path.join(ASSETS, file)

    def selesai(data: bytes):
        if recolor:
            data = recolor_logo(data)
        cache[file] = to_uri(data)
        status[file] = {"label": label, "mode": "ok", "err": ""}
        return cache[file]

    # 1) file lokal
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        if sniff_mime(data):
            if resize and len(data) > 400_000:
                data = shrink(data, max_side)
            return selesai(data)
        os.remove(path)   # file rusak -> hapus

    # 2) unduh dari URL
    real = clean_url(url)
    err = "URL kosong"
    if real:
        data, err = download(real)
        if data:
            if resize:
                data = shrink(data, max_side)
            with open(path, "wb") as f:
                f.write(data)
            return selesai(data)

        # 3) fallback: biarkan browser memuat (hanya jika benar-benar link gambar)
        if looks_like_image(real) and not recolor:
            cache[file] = real
            status[file] = {"label": label, "mode": "hotlink", "err": err}
            return real

    status[file] = {"label": label, "mode": "gagal", "err": err}
    return None


def reset_image_cache():
    st.session_state.pop("_img_cache", None)
    st.session_state.pop("_img_status", None)


# ============================================================
# CSS
# ============================================================
html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp {font-family:'Plus Jakarta Sans',sans-serif;}
.stApp {background:linear-gradient(180deg,#f1f5f9 0%,#ffffff 40%,#f8fafc 100%);}
.block-container {max-width:1150px; padding-top:1.4rem; padding-bottom:2rem;}
#MainMenu, footer, header {visibility:hidden;}

/* ---------- LOGO ATAS ---------- */
.logostrip {display:inline-flex; align-items:center; gap:18px; padding:.6rem 1.2rem;
            background:#fff; border:1px solid #e2e8f0; border-radius:18px;
            box-shadow:0 6px 18px rgba(15,23,42,.07); margin-bottom:1rem;}
.logostrip img {object-fit:contain; display:block;}
.logostrip .dk {background:linear-gradient(135deg,#0a1a33,#10294d); border-radius:12px;
                padding:6px 12px; display:flex; align-items:center;}
.logostrip .sep {width:1px; height:34px; background:#e2e8f0;}
.logofb {font-size:1.6rem; letter-spacing:6px;}

/* ---------- HEADER ---------- */
.hcard {background:#fff; border:1px solid #e2e8f0; border-radius:22px; padding:1.7rem 1.8rem;
        box-shadow:0 10px 30px rgba(15,23,42,.07); min-height:250px;}
.hcard h1 {margin:0 0 .8rem 0; font-size:2.05rem; line-height:1.2; font-weight:800; color:#0f172a;}
.hcard p {margin:0 0 1rem 0; color:#475569; font-size:.92rem; line-height:1.6;}
.chip {display:inline-block; margin:0 8px 6px 0; padding:6px 14px; border-radius:999px;
       background:#f8fafc; border:1px solid #e2e8f0; color:#475569; font-size:.78rem;}
.chip b {color:#0f172a;}

.rcard {background:rgba(255,255,255,.95); border:1px solid #e2e8f0; border-radius:22px;
        padding:1.5rem 1.6rem; box-shadow:0 10px 30px rgba(15,23,42,.07); min-height:250px;}
.rcard h4 {margin:0 0 .6rem 0; color:#0f172a; font-size:1rem; font-weight:800;}
.rcard p {margin:0 0 1rem 0; color:#475569; font-size:.86rem; line-height:1.6;}
.mini {display:grid; grid-template-columns:1fr 1fr; gap:12px;}
.mini div {border:1px solid #e2e8f0; border-radius:14px; padding:.7rem .9rem; background:#fff;}
.mini small {display:block; color:#64748b; font-size:.72rem; font-weight:600;}
.mini b {color:#0f172a; font-size:1rem;}

/* ---------- WADAH HERO (biru muda -> putih) ---------- */
.herowrap {display:grid; grid-template-columns:1.5fr 1fr; gap:1.4rem; align-items:stretch;
           padding:1.5rem; border-radius:30px; border:1px solid #bfdbfe;
           background:linear-gradient(135deg,#bae6fd 0%,#e0f2fe 45%,#ffffff 100%);
           box-shadow:0 14px 40px rgba(2,132,199,.14);}
.herowrap .hcard, .herowrap .rcard {min-height:0; height:100%; box-sizing:border-box;
           background:rgba(255,255,255,.92); border:1px solid rgba(186,230,253,.9);
           box-shadow:0 8px 24px rgba(15,23,42,.06);}
.herowrap .rcard {display:flex; flex-direction:column;}
.herowrap .rcard .mini {margin-top:auto;}
@media (max-width: 800px) {.herowrap {grid-template-columns:1fr;}}

/* ---------- SECTION ---------- */
.sec {margin:2.4rem 0 1rem 0;}
.sec h2 {margin:0; font-size:1.4rem; font-weight:800; color:#0f172a;}
.sec h2::after {content:""; display:block; width:54px; height:4px; border-radius:4px; margin-top:6px;
        background:linear-gradient(90deg,#0284c7,#0d9488);}
.sec span {color:#64748b; font-size:.86rem;}

/* ---------- PETA ---------- */
iframe {border-radius:22px; border:1px solid #e2e8f0 !important;
        box-shadow:0 10px 30px rgba(15,23,42,.10);}
.legend {display:flex; flex-wrap:wrap; gap:8px; margin-top:.8rem;}
.legend span {display:inline-flex; align-items:center; gap:6px; background:#fff;
       border:1px solid #e2e8f0; border-radius:999px; padding:5px 13px; font-size:.78rem;
       color:#334155; font-weight:600;}
.legend i {width:10px; height:10px; border-radius:50%; display:inline-block;}

/* ---------- KARTU DESTINASI ---------- */
.dest {background:#fff; border:1px solid #e2e8f0; border-radius:22px; overflow:hidden;
       box-shadow:0 4px 14px rgba(15,23,42,.06); transition:.3s; margin-bottom:1rem;}
.dest:hover {transform:translateY(-6px); box-shadow:0 18px 36px rgba(2,132,199,.18);}
.dest .pic {height:175px; display:flex; align-items:center; justify-content:center;
       font-size:3.2rem; position:relative; overflow:hidden;}
.dest .pic img.pimg {position:absolute; inset:0; width:100%; height:100%; object-fit:cover;}
.dest .tag {position:absolute; top:12px; left:12px; z-index:2; background:rgba(255,255,255,.92);
       color:#0369a1; font-size:.7rem; font-weight:700; padding:4px 10px; border-radius:999px;}
.dest .body {padding:1rem 1.1rem 1.2rem 1.1rem;}
.dest h4 {margin:0 0 .3rem 0; color:#0f172a; font-size:1rem;}
.dest p {margin:0; color:#64748b; font-size:.82rem;}

/* ---------- CTA & LOGIN ---------- */
.cta {text-align:center; border-radius:26px; padding:2.4rem 1.5rem; margin-top:2.4rem; color:#fff;
      background:linear-gradient(135deg,#0f172a 0%,#0369a1 60%,#0d9488 100%);
      box-shadow:0 18px 40px rgba(15,23,42,.25);}
.cta h3 {margin:0 0 .4rem 0; color:#fff; font-size:1.5rem; font-weight:800;}
.cta p {margin:0; color:rgba(255,255,255,.85); font-size:.92rem;}

.lcard {background:#fff; border:1px solid #e2e8f0; border-radius:22px; padding:1.5rem;
        box-shadow:0 10px 28px rgba(15,23,42,.08); margin-bottom:.8rem;}
.lcard h3 {margin:0 0 .3rem 0; color:#0f172a;}
.lcard p {margin:0; color:#64748b; font-size:.88rem;}

.dash {background:linear-gradient(135deg,#0369a1,#0d9488); color:#fff; border-radius:22px;
       padding:1.4rem 1.6rem; box-shadow:0 14px 34px rgba(2,132,199,.25); margin-bottom:1rem;}
.dash h2 {margin:0; color:#fff; font-size:1.5rem; font-weight:800;}
.dash span {color:rgba(255,255,255,.88); font-size:.88rem;}

div.stButton > button, div.stFormSubmitButton > button {
    background:linear-gradient(90deg,#0284c7,#0d9488); color:#fff; border:none;
    border-radius:14px; padding:.75rem 1rem; font-weight:700; width:100%;
    box-shadow:0 8px 20px rgba(2,132,199,.30); transition:.2s;}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    color:#fff; transform:translateY(-2px); box-shadow:0 12px 26px rgba(2,132,199,.40);}
.footer {text-align:center; color:#94a3b8; font-size:.78rem; margin-top:2.2rem;}
</style>
""")


# ============================================================
# KOMPONEN
# ============================================================
def logo_strip() -> str:
    items = []
    for lg in LOGOS:
        src = get_image(lg["file"], lg["url"], True, "Logo " + lg["file"],
                        recolor=lg.get("recolor", False), max_side=500)
        if not src:
            continue
        img = (f'<img src="{src}" alt="" referrerpolicy="no-referrer" '
               f'style="height:{lg["h"]}px;"/>')
        items.append(f'<div class="dk">{img}</div>' if lg["dark"] else img)
    if not items:
        return '<div class="logostrip"><span class="logofb">🎓 🏛️ 🌴</span></div>'
    return '<div class="logostrip">' + '<div class="sep"></div>'.join(items) + "</div>"


def render_peta():
    if PETA_STYLE == "google":
        m = folium.Map(location=[-7.05, 112.83], zoom_start=10, control_scale=True,
                       tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&hl=id",
                       attr="Google Maps")
    else:
        m = folium.Map(location=[-7.05, 112.83], zoom_start=10, tiles="OpenStreetMap",
                       control_scale=True)

    for d in DESTINASI:
        pin = f"""
        <div style="position:relative; width:30px; height:42px; transform:translate(-15px,-40px);">
          <svg viewBox="0 0 30 42" width="30" height="42" xmlns="http://www.w3.org/2000/svg"
               style="filter:drop-shadow(0 3px 3px rgba(0,0,0,.35));">
            <path d="M15 0C6.7 0 0 6.7 0 15c0 11 15 27 15 27s15-16 15-27C30 6.7 23.3 0 15 0z"
                  fill="{d['color']}" stroke="white" stroke-width="2"/>
            <circle cx="15" cy="15" r="6" fill="white"/>
          </svg>
        </div>
        """
        folium.Marker(
            location=[d["lat"], d["lon"]],
            icon=folium.DivIcon(html=pin, icon_size=(0, 0)),
            tooltip=folium.Tooltip(
                f"<b>{d['nama']}</b>", permanent=True, direction="right",
                style="background:white;color:#0f172a;border-radius:8px;"
                      "border:1px solid #e2e8f0;padding:3px 8px;font-size:12px;"
                      "box-shadow:0 2px 6px rgba(0,0,0,.2);margin-left:10px;"),
            popup=folium.Popup(
                f"<b>{d['nama']}</b><br><span style='color:#64748b'>{d['tag']}</span>",
                max_width=220),
        ).add_to(m)

    m.fit_bounds([[d["lat"], d["lon"]] for d in DESTINASI], padding=(40, 40))
    peta_html = m.get_root().render()
    if hasattr(st, "iframe"):          # Streamlit baru (components.html sudah dihapus)
        st.iframe(peta_html, height=480)
    else:
        components.html(peta_html, height=480)

    legend = "".join(
        f'<span><i style="background:{d["color"]}"></i>{d["nama"]}</span>' for d in DESTINASI)
    html(f'<div class="legend">{legend}</div>')


def dest_card(d: dict) -> str:
    src = get_image(d["file"], d["url"], True, d["nama"])
    grad = f'linear-gradient(135deg,{d["grad"]})'
    img = (f'<img class="pimg" src="{src}" alt="" referrerpolicy="no-referrer"/>'
           if src else "")
    return f"""
    <div class="dest">
    <div class="pic" style="background-image:{grad};"><span class="tag">{d['tag']}</span>{d['icon']}{img}</div>
    <div class="body"><h4>{d['nama']}</h4><p>{d['desk']}</p></div>
    </div>
    """


def section(title: str, sub: str = ""):
    html(f'<div class="sec"><h2>{title}</h2><span>{sub}</span></div>')


def panel_status_gambar():
    """Panel info + upload manual untuk gambar/logo yang belum termuat dari server."""
    status = st.session_state.get("_img_status", {})
    masalah = {f: s for f, s in status.items() if s["mode"] != "ok"}
    if not masalah:
        return

    with st.expander(f"ℹ️ {len(masalah)} gambar belum diunduh server (klik untuk upload manual)"):
        st.caption(
            "Instagram dan beberapa situs memblokir unduhan otomatis. Simpan fotonya dari "
            "browser/HP Anda, lalu upload di bawah. Hasil upload tersimpan di folder assets/.")
        for file, s in masalah.items():
            st.markdown(f"**{s['label']}** · status: `{s['mode']}` · alasan: `{s['err']}`")
            up = st.file_uploader(f"Upload untuk {file}", type=["jpg", "jpeg", "png", "webp"],
                                  key=f"up_{file}")
            if up is not None:
                data = up.getvalue()
                if sniff_mime(data):
                    with open(os.path.join(ASSETS, file), "wb") as f:
                        f.write(data)
                    reset_image_cache()
                    st.rerun()
                else:
                    st.error("File bukan gambar yang valid.")
        if st.button("🔄 Coba muat ulang semua gambar", key="btn_retry"):
            reset_image_cache()
            st.rerun()


# ============================================================
# HALAMAN: LANDING
# ============================================================
def landing_page():
    html(logo_strip())

    # ---------- HERO (2 card dalam wadah biru muda -> putih) ----------
    html(f"""
    <div class="herowrap">
    <div class="hcard">
    <h1>Aplikasi Prediksi Jumlah Kunjungan Wisatawan<br>Di Kabupaten Bangkalan</h1>
    <p>Dikembangkan oleh <b>{NAMA_PENGEMBANG}</b> sebagai Tugas Akhir S1 Sistem Informasi.
    Sistem memanfaatkan metode hybrid <b>ICEEMDAN-VMD-GRU</b> untuk membantu analisis
    tren kunjungan wisata.</p>
    <span class="chip">Metode: <b>ICEEMDAN-VMD</b></span>
    <span class="chip">Model: <b>GRU</b></span>
    <span class="chip">Output: <b>Prediksi Kunjungan</b></span>
    </div>
    <div class="rcard">
    <h4>Ringkasan Metode</h4>
    <p>Kombinasi <b>ICEEMDAN</b> dan <b>Variational Mode Decomposition (VMD)</b> untuk
    dekomposisi sinyal dan <b>Gated Recurrent Unit (GRU)</b> untuk pemodelan deret waktu,
    sehingga prediksi lebih stabil terhadap noise dan pola musiman.</p>
    <div class="mini">
    <div><small>Cakupan</small><b>Kab. Bangkalan</b></div>
    <div><small>Destinasi</small><b>{len(DESTINASI)} Lokasi</b></div>
    </div>
    </div>
    </div>
    """)

    # ---------- PETA ----------
    section("Wilayah Cakupan Kabupaten Bangkalan", "Pin berwarna menandai lokasi objek wisata")
    render_peta()

    # ---------- DESTINASI ----------
    section("Destinasi Wisata yang Diprediksi", f"{len(DESTINASI)} lokasi wisata ditampilkan")
    r1 = st.columns(3, gap="medium")
    for col, d in zip(r1, DESTINASI[:3]):
        with col:
            html(dest_card(d))
    r2 = st.columns(3, gap="medium")
    for col, d in zip(r2, DESTINASI[3:]):
        with col:
            html(dest_card(d))

    # ---------- CTA ----------
    html("""
    <div class="cta">
    <h3>Siap mulai analisis prediksi?</h3>
    <p>Silakan login sebagai Admin atau User untuk mengakses fitur peramalan kunjungan wisatawan.</p>
    </div>
    """)
    st.write("")
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        if st.button("🔐 Login Admin atau User", key="btn_login"):
            goto("login")

    html(f'<div class="footer">© 2026 {NAMA_PENGEMBANG} — Aplikasi Prediksi Kunjungan '
         'Wisatawan Kabupaten Bangkalan, Tugas Akhir. All rights reserved.</div>')

    panel_status_gambar()


# ============================================================
# HALAMAN: LOGIN
# ============================================================
def login_page():
    html("""
    <div class="hcard" style="text-align:center; min-height:0;">
    <h1 style="margin:0;">Selamat Datang 👋</h1>
    <p style="margin:.5rem 0 0 0;">Pilih cara masuk untuk melanjutkan ke aplikasi peramalan.</p>
    </div>
    """)
    st.write("")
    cu, ca = st.columns(2, gap="large")

    # ----- USER: langsung masuk tanpa input -----
    with cu:
        html("""
        <div class="lcard"><h3>👤 User</h3>
        <p>Masuk langsung tanpa username dan password untuk melihat serta menjalankan peramalan.</p></div>
        """)
        if st.button("Masuk sebagai User", key="btn_user"):
            goto("app_user", role="User")

    # ----- ADMIN: username & password -----
    with ca:
        html("""
        <div class="lcard"><h3>🛠️ Admin</h3>
        <p>Masuk dengan akun admin untuk mengelola data dan model.</p></div>
        """)
        with st.form("form_admin"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            ok = st.form_submit_button("Masuk sebagai Admin")
        if ok:
            if u == ADMIN_USER and p == ADMIN_PASS:
                goto("app_admin", role="Admin")
            else:
                st.error("Username atau password salah.")

    st.write("")
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        if st.button("⬅️ Kembali ke Beranda", key="btn_back"):
            goto("landing")


# ============================================================
# HALAMAN: USER  (Dashboard Prediksi)
# ============================================================
import inspect
import pandas as pd
import plotly.graph_objects as go
import forecasting_engine as fe

BULAN_PENDEK = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

DASH_CSS = """
<style>
/* header Streamlit tetap ada (tombol sidebar di HP), hanya toolbar disembunyikan */
header[data-testid="stHeader"] {visibility:visible !important; background:transparent !important;}
[data-testid="stToolbar"], [data-testid="stDecoration"] {display:none !important;}
.block-container {max-width:1250px;}

/* ================= SIDEBAR: TETAP TERLIHAT, RAPAT, TANPA SCROLL ================= */
/* Sembunyikan tombol buka/tutup sidebar (hanya di layar lebar; di HP tetap bisa dibuka) */
/* ================= SIDEBAR ================= */
@media (min-width: 992px) {
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stExpandSidebarButton"] {display:none !important;}
    section[data-testid="stSidebar"] {
        width:310px !important; min-width:310px !important; max-width:310px !important;
        transform:none !important; visibility:visible !important;}
    [data-testid="stSidebarResizeHandle"] {display:none !important;}
}
section[data-testid="stSidebar"] {background:#f8fafc !important; border-right:1px solid #e2e8f0;}
[data-testid="stSidebarHeader"] {display:none !important;}
[data-testid="stSidebarUserContent"] {padding:1.1rem 1rem .8rem 1rem !important;}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap:.6rem !important;}

.sb-title {font-size:1.05rem; font-weight:800; color:#0f172a; padding-bottom:.65rem;
           border-bottom:1px solid #e2e8f0; margin-bottom:.1rem;}

section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    font-size:.7rem !important; font-weight:800 !important; letter-spacing:.07em !important;
    text-transform:uppercase !important; color:#64748b !important;}

section[data-testid="stSidebar"] div[role="radiogroup"] {gap:.18rem !important;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    width:100% !important; margin:0 !important; padding:.4rem .65rem !important;
    border-radius:10px !important; border:1px solid transparent !important; transition:.15s;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {background:#eef6fd !important;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background:#e0f2fe !important; border-color:#bae6fd !important;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    font-size:.86rem !important; line-height:1.25 !important; margin:0 !important;
    color:#334155 !important; text-transform:none !important; letter-spacing:0 !important;
    font-weight:500 !important;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
    color:#0369a1 !important; font-weight:700 !important;}

section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    flex-direction:column !important; align-items:stretch !important; gap:.55rem !important;
    padding:.75rem !important; background:#ffffff !important;
    border:1.5px dashed #93c5fd !important; border-radius:12px !important;}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] {
    justify-content:center !important; text-align:center !important;}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] small {
    font-size:.72rem !important; color:#64748b !important;}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
    width:100% !important; justify-content:center !important; background:#ffffff !important;
    color:#0369a1 !important; border:1px solid #bae6fd !important; border-radius:10px !important;
    font-weight:700 !important;}

section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(div.stButton) {width:100% !important;}
section[data-testid="stSidebar"] div.stButton {width:100% !important; margin:0 !important;}
section[data-testid="stSidebar"] div.stButton > button {
    width:100% !important; min-height:2.6rem !important; padding:.5rem 1rem !important;
    border-radius:12px !important; justify-content:center !important; text-align:center !important;
    box-shadow:0 4px 12px rgba(2,132,199,.25) !important; transform:none !important;}
section[data-testid="stSidebar"] div.stButton > button p {
    font-size:.9rem !important; font-weight:700 !important; margin:0 !important;}
section[data-testid="stSidebar"] div.stButton > button:hover {
    filter:brightness(1.05); box-shadow:0 6px 16px rgba(2,132,199,.35) !important;}
section[data-testid="stSidebar"] div.stButton > button:disabled {
    background:#e2e8f0 !important; color:#94a3b8 !important; box-shadow:none !important;
    opacity:1 !important; cursor:not-allowed !important; filter:none !important;}

section[data-testid="stSidebar"] .st-key-adm_back button,
section[data-testid="stSidebar"] .st-key-dash_back button {
    background:#ffffff !important; color:#334155 !important;
    border:1px solid #cbd5e1 !important; box-shadow:none !important;}
section[data-testid="stSidebar"] .st-key-adm_back button:hover,
section[data-testid="stSidebar"] .st-key-dash_back button:hover {
    border-color:#0284c7 !important; color:#0284c7 !important; background:#f0f9ff !important;
    box-shadow:none !important;}

section[data-testid="stSidebar"] .st-key-adm_go,
section[data-testid="stSidebar"] .st-key-dash_go {
    position:sticky; bottom:0; z-index:5; padding:.5rem 0 .3rem 0; background:#f8fafc;}

/* ---------- HEADER DASHBOARD ---------- */
.dwrap {position:relative; margin-bottom:1.1rem;}
.dhead {max-width:720px; margin:0 auto; padding:1.1rem 1.6rem 1.3rem 1.6rem; border-radius:24px;
        background:linear-gradient(135deg,#bae6fd 0%,#eff9ff 55%,#ffffff 100%);
        border:1px solid #dbeafe; box-shadow:0 12px 30px rgba(2,132,199,.14);}
.dlogos {display:inline-flex; align-items:center; gap:12px; background:#fff; border-radius:14px;
         padding:.4rem .8rem; box-shadow:0 3px 10px rgba(15,23,42,.08); margin-bottom:.8rem;}
.dlogos img {display:block; object-fit:contain;}
.dhead h1 {margin:0; font-size:1.7rem; font-weight:800; color:#0f172a; line-height:1.25;}
.dhead h2 {margin:.1rem 0 0 0; font-size:1.45rem; font-weight:800; color:#0f172a; line-height:1.25;}
.dbadge {position:absolute; right:0; top:0; background:#fff; border-radius:14px; padding:.45rem .6rem;
         box-shadow:0 3px 10px rgba(15,23,42,.10);}
.dbadge img {display:block; object-fit:contain;}
@media (max-width: 900px) {.dbadge {display:none;}}

/* ---------- INFO & PLACEHOLDER ---------- */
.dinfo {background:#e8f1fd; color:#1e3a8a; border-radius:10px; padding:.75rem 1rem; font-size:.84rem;
        margin:.4rem 0 1rem 0;}
.sk {background:#f1f5f9; border-radius:18px;}
.sk-row {display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem;}

/* ---------- KARTU METRIK ---------- */
.mcard {background:#fff; border:1px solid #e2e8f0; border-radius:18px; padding:1rem 1.3rem;
        box-shadow:0 6px 18px rgba(15,23,42,.06); margin-bottom:1rem;}
.mcard .ml {color:#64748b; font-size:.78rem; font-weight:700; letter-spacing:.3px;}
.mcard .mv {color:#0f172a; font-size:2rem; font-weight:800; line-height:1.2; margin:.15rem 0;}
.mcard .ms {color:#64748b; font-size:.78rem;}
.mcard.a {border-top:4px solid #0284c7;}
.mcard.b {border-top:4px solid #0d9488;}

/* ---------- KARTU GRAFIK ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {border-radius:18px;}
.ct {font-weight:800; color:#0f172a; font-size:1.05rem; margin:0;}
.cs {color:#64748b; font-size:.8rem; margin:.1rem 0 .4rem 0;}
.dfooter {text-align:center; color:#64748b; font-size:.74rem; margin-top:2.2rem; padding-top:.9rem;
          border-top:1px solid #e2e8f0;}
</style>
"""


def _fmt_id(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _tgl_id(iso):
    d = pd.Timestamp(iso)
    return f"{BULAN_PENDEK[d.month - 1]} {d.year}"


def _show(obj, kind="plot", **kw):
    """Kompatibel lintas versi Streamlit (width='stretch' vs use_container_width)."""
    fn = st.plotly_chart if kind == "plot" else st.dataframe
    if "width" in inspect.signature(fn).parameters:
        return fn(obj, width="stretch", **kw)
    return fn(obj, use_container_width=True, **kw)


def _logo_img(lg, h=None):
    src = get_image(lg["file"], lg["url"], True, "Logo " + lg["file"],
                    recolor=lg.get("recolor", False), max_side=500)
    if not src:
        return ""
    return f'<img src="{src}" alt="" referrerpolicy="no-referrer" style="height:{h or lg["h"]}px;"/>'


def dash_header():
    logos = "".join(_logo_img(lg) for lg in LOGOS)   # semua logo, termasuk Bangkalan
    html(f"""
    <div class="dwrap">
    <div class="dhead">
    <div class="dlogos">{logos or "🎓 🏛️"}</div>
    <h1>Dashboard Prediksi</h1>
    <h2>Analisis Data Kunjungan dan Peramalan Masa Depan</h2>
    </div>
    </div>
    """)


def dash_footer():
    html(f'<div class="dfooter">© 2026 {NAMA_PENGEMBANG} - Tugas Akhir S1 Sistem Informasi UTM. '
         'All rights reserved.</div>')


def dash_info(teks):
    html(f'<div class="dinfo">{teks}</div>')


def dash_skeleton():
    html("""
    <div class="sk-row"><div class="sk" style="height:96px"></div><div class="sk" style="height:96px"></div></div>
    <div class="sk" style="height:260px"></div>
    """)


def _metric_card(cls, label, nilai, sub):
    return (f'<div class="mcard {cls}"><div class="ml">{label}</div>'
            f'<div class="mv">{nilai}</div><div class="ms">{sub}</div></div>')


def _layout(fig, h=380):
    fig.update_layout(
        height=h, margin=dict(l=8, r=8, t=8, b=8), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#334155"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
        xaxis=dict(showgrid=False, tickformat="%Y", dtick="M12", linecolor="#cbd5e1"),
        yaxis=dict(title="Jumlah Pengunjung", gridcolor="#e2e8f0", tickformat=",.0f", zeroline=False),
    )
    return fig


def fig_aktual_prediksi(h):
    tgl = pd.to_datetime(h["tgl_hist"])
    tgl_uji = pd.to_datetime(h["tgl_uji"])
    fig = go.Figure()
    fig.add_vrect(x0=tgl_uji[0], x1=tgl_uji[-1], fillcolor="rgba(249,115,22,0.07)", line_width=0,
                  annotation_text="Periode uji", annotation_position="top left",
                  annotation_font=dict(size=11, color="#c2410c"))
    fig.add_trace(go.Scatter(
        x=tgl, y=h["aktual_hist"], name="Aktual", mode="lines",
        line=dict(color="#0284c7", width=2.4),
        customdata=[_tgl_id(d.strftime("%Y-%m-%d")) for d in tgl],
        hovertemplate="Aktual: %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=tgl_uji, y=h["prediksi_uji"], name="Prediksi", mode="lines+markers",
        line=dict(color="#f97316", width=2.4, dash="dash"), marker=dict(size=6),
        hovertemplate="Prediksi: %{y:,.0f}<extra></extra>"))
    return _layout(fig)


def fig_masa_depan(h):
    n_tampil = 36
    tgl = pd.to_datetime(h["tgl_hist"])[-n_tampil:]
    akt = h["aktual_hist"][-n_tampil:]
    tgl_f = pd.to_datetime(h["tgl_fut"])
    fig = go.Figure()
    fig.add_vrect(x0=tgl_f[0], x1=tgl_f[-1], fillcolor="rgba(13,148,136,0.07)", line_width=0,
                  annotation_text="12 bulan ke depan", annotation_position="top left",
                  annotation_font=dict(size=11, color="#0f766e"))
    fig.add_trace(go.Scatter(x=tgl, y=akt, name="Data historis", mode="lines",
                             line=dict(color="#0284c7", width=2.4),
                             hovertemplate="Aktual: %{y:,.0f}<extra></extra>"))
    # garis penghubung titik terakhir historis -> prediksi pertama
    fig.add_trace(go.Scatter(x=[tgl[-1], tgl_f[0]], y=[akt[-1], h["prediksi_fut"][0]],
                             mode="lines", showlegend=False, hoverinfo="skip",
                             line=dict(color="#0d9488", width=1.6, dash="dot")))
    fig.add_trace(go.Scatter(x=tgl_f, y=h["prediksi_fut"], name="Prediksi 12 bulan",
                             mode="lines+markers", line=dict(color="#0d9488", width=2.6, dash="dash"),
                             marker=dict(size=7),
                             hovertemplate="Prediksi: %{y:,.0f}<extra></extra>"))
    fig.update_xaxes(tickformat="%b %Y", dtick="M6")
    return _layout(fig)


def render_hasil(h):
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        html(_metric_card("a", "MAE (Mean Absolute Error)", _fmt_id(h["mae"], 2),
                          "rata-rata selisih absolut aktual dan prediksi"))
    with c2:
        html(_metric_card("b", "MAPE (Mean Absolute Percentage Error)", _fmt_id(h["mape"], 2) + "%",
                          "rata-rata persentase kesalahan prediksi"))

    with st.container(border=True):
        html(f'<div class="ct">Visualisasi Data Aktual dan Prediksi</div>'
             f'<div class="cs">Evaluasi pada periode uji {_tgl_id(h["tgl_uji"][0])} – '
             f'{_tgl_id(h["tgl_uji"][-1])} ({len(h["tgl_uji"])} bulan)</div>')
        _show(fig_aktual_prediksi(h), "plot", key="fig_aktual")

    st.write("")
    with st.container(border=True):
        html(f'<div class="ct">Prediksi Kunjungan 12 Bulan ke Depan</div>'
             f'<div class="cs">{_tgl_id(h["tgl_fut"][0])} – {_tgl_id(h["tgl_fut"][-1])}</div>')
        _show(fig_masa_depan(h), "plot", key="fig_future")
        tabel = pd.DataFrame({
            "Bulan": [_tgl_id(d) for d in h["tgl_fut"]],
            "Prediksi Pengunjung": [_fmt_id(v) for v in h["prediksi_fut"]],
        })
        with st.expander("Lihat tabel prediksi"):
            _show(tabel, "df", hide_index=True)

    if h.get("n_param_default", 0) > 0:
        st.caption("Catatan: pola data yang diunggah berbeda dari data acuan model, sehingga "
                   f"{h['n_param_default']} komponen memakai pengaturan standar. Hasil dapat "
                   "berbeda dari data acuan.")


def user_page():
    if st.session_state.role != "User":
        goto("login")

    html(DASH_CSS)
    names = [d["nama"] for d in DESTINASI if d["nama"] in fe.CONFIG]

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        html('<div class="sb-title">⚙️ Konfigurasi Prediksi</div>')
        dest = st.radio("Destinasi Wisata", names, key="dash_dest",
                        help="Pilih destinasi wisata yang akan diprediksi.")
        up = st.file_uploader("Dataset (.xlsx / .csv)", type=["xlsx", "csv"], key="dash_up")
        go_btn = st.button("Mulai Prediksi", key="dash_go", disabled=(up is None))
        if st.button("« Kembali ke Beranda", key="dash_back"):
            goto("landing")

    # ---------------- HALAMAN UTAMA ----------------
    dash_header()

    if up is None:
        dash_info("Silakan unggah (upload) file dataset Excel/CSV melalui sidebar di sebelah "
                  "kiri untuk memulai analisis.")
        dash_skeleton()
        dash_footer()
        return

    data_bytes = up.getvalue()
    try:
        data_clean, info = fe.siapkan_data(fe.baca_dataset(data_bytes, up.name, destinasi=dest))
    except Exception as e:
        st.error(f"Dataset tidak dapat dibaca: {e}")
        dash_footer()
        return

    key = fe.kunci_cache(dest, data_bytes)
    clean_key = fe.kunci_cache(
        dest,
        pd.util.hash_pandas_object(
            data_clean[["date", "visitors"]].reset_index(drop=True), index=False
        ).values.tobytes()
    )

    if go_btn:
        hasil = fe.muat_cache(key) or fe.muat_cache(clean_key)
        if hasil is None:
            bar = st.progress(0.0, text="Memulai proses...")
            try:
                hasil = fe.jalankan_prediksi(
                    dest, data_clean, progress=lambda f, t: bar.progress(min(max(f, 0.0), 1.0), text=t))
            except Exception as e:
                bar.empty()
                st.error(f"Proses gagal dijalankan: {e}")
                dash_footer()
                return
            bar.empty()
            fe.simpan_cache(key, hasil)
            fe.simpan_cache(clean_key, hasil)
        st.session_state["dash_result"] = {"key": key, "hasil": hasil}

    res = st.session_state.get("dash_result")
    if res and res["key"] == key:
        render_hasil(res["hasil"])
    else:
        periode = f'{_tgl_id(info["awal"].strftime("%Y-%m-%d"))} – {_tgl_id(info["akhir"].strftime("%Y-%m-%d"))}'
        dash_info(f'Dataset <b>{up.name}</b> diterima ({info["n"]} bulan, {periode}). '
                  'Klik <b>Mulai Prediksi</b> pada sidebar untuk menjalankan analisis.')
        dash_skeleton()
    dash_footer()


# ============================================================
# HALAMAN: ADMIN (Dashboard sama seperti User + pilihan metode)
# ============================================================
import admin_methods as am

def admin_page():
    if st.session_state.role != "Admin":
        goto("login")

    html(DASH_CSS)
    names = [d["nama"] for d in DESTINASI if d["nama"] in fe.CONFIG]

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        html('<div class="sb-title">⚙️ Konfigurasi Prediksi</div>')
        dest = st.radio("Destinasi Wisata", names, key="adm_dest",
                        help="Pilih destinasi wisata yang akan diprediksi.")
        metode = st.radio("Metode Peramalan", am.METODE, key="adm_metode",
                          help="Pilih metode peramalan yang akan dijalankan.")
        up = st.file_uploader("Dataset (.xlsx / .csv)", type=["xlsx", "csv"], key="adm_up")
        go_btn = st.button("Mulai Prediksi", key="adm_go", disabled=(up is None))
        if st.button("« Keluar", key="adm_back"):
            goto("landing")

    # ---------------- HALAMAN UTAMA ----------------
    dash_header()

    if up is None:
        dash_info("Silakan unggah (upload) file dataset Excel/CSV melalui sidebar di sebelah "
                  "kiri untuk memulai analisis.")
        dash_skeleton()
        dash_footer()
        return

    data_bytes = up.getvalue()
    try:
        data_clean, info = fe.siapkan_data(fe.baca_dataset(data_bytes, up.name, destinasi=dest))
    except Exception as e:
        st.error(f"Dataset tidak dapat dibaca: {e}")
        dash_footer()
        return

    key = fe.kunci_cache(f"{dest}|{metode}", data_bytes)
    state_key = f"{dest}|{metode}|{up.name}|{len(data_bytes)}"
    curr_dataset = f"{up.name}|{len(data_bytes)}"

    # Cek apakah analisis admin sudah pernah dimulai untuk dataset ini
    adm_active = st.session_state.get("adm_active_dataset") == curr_dataset

    if go_btn:
        st.session_state["adm_active_dataset"] = curr_dataset
        adm_active = True

    if adm_active:
        res = st.session_state.get("adm_result")
        # Jika hasil belum ada atau admin mengganti destinasi/metode di sidebar: langsung muat instan
        if not (res and res.get("key") == state_key):
            try:
                hasil = None
                if am.cari_folder(metode, dest) is None:
                    hasil = fe.muat_cache(key)          # cache hasil training lama
                if hasil is None:
                    hasil = am.jalankan_metode(dest, data_clean, metode)
                    if not hasil.get("loaded_from_folder"):
                        fe.simpan_cache(key, hasil)

                _kp = "adm_" + metode.replace(" ", "_").replace("-", "_")
                if metode == "Hybrid ICEEMDAN-VMD-GRU":
                    st.session_state.setdefault(f"{_kp}_menu", "Interpolasi Linear")
                    st.session_state.setdefault(f"_tahap_{_kp}_menu", "Interpolasi Linear")
                else:
                    st.session_state[f"{_kp}_menu"] = "Evaluasi & Prediksi"
                    st.session_state[f"_tahap_{_kp}_menu"] = "Evaluasi & Prediksi"

                st.session_state["adm_result"] = {"key": state_key, "hasil": hasil}
            except Exception as e:
                st.error(f"Gagal memuat hasil metode {metode}: {e}")
                dash_footer()
                return

    res = st.session_state.get("adm_result")
    if res and res.get("key") == state_key:
        n0 = int((info["raw_df"]["visitors"] == 0).sum())
        dash_info(f"Hasil metode <b>{metode}</b> untuk destinasi <b>{dest}</b>. "
                  f"Nilai 0 / kosong pada file: <b>{n0}</b>.")
        am.render_hasil_admin(res["hasil"], raw_df=info["raw_df"])
    else:
        periode = (f'{_tgl_id(info["awal"].strftime("%Y-%m-%d"))} – '
                   f'{_tgl_id(info["akhir"].strftime("%Y-%m-%d"))}')
        dash_info(f'Dataset <b>{up.name}</b> diterima ({info["n"]} bulan, {periode}). '
                  f'Metode terpilih: <b>{metode}</b>. '
                  'Klik <b>Mulai Prediksi</b> pada sidebar untuk menjalankan analisis.')
        dash_skeleton()
    dash_footer()


# ============================================================
# ROUTER
# ============================================================
page = st.session_state.page
if page == "landing":
    landing_page()
elif page == "login":
    login_page()
elif page == "app_user":
    user_page()
elif page == "app_admin":
    admin_page()
else:
    landing_page()
