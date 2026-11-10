%%writefile admin_methods.py
# -*- coding: utf-8 -*-
"""Mesin pembanding metode untuk dashboard Admin.

Semua metode (ICEEMDAN-VMD-GRU, ICEEMDAN-GRU, VMD-GRU, GRU) dimuat langsung dari
folder hasil notebook skripsi sehingga tampil instan. Training ulang hanya
dilakukan sebagai fallback bila folder hasil tidak ditemukan.

Perbaikan v2 (khusus ICEEMDAN-GRU):
- Pencarian folder toleran nama (spasi/strip/underscore/huruf besar-kecil, sinonim
  "Kolla Langgundi" = "Kolla Labgudih", "Makam Sunan Cendana" = "Sunan Cendana", dst).
- Kolom 'Sinyal_Asli' di iceemdan_decomposition.xlsx tidak lagi dianggap IMF.
- Hasil gagal-muat tidak lagi di-cache selamanya, dan alasan gagal ditampilkan.
- Untuk 4 destinasi notebook ICEEMDAN-GRU tidak ada training ulang diam-diam
  (hasil yang bisa berbeda dari notebook); bila folder kurang, muncul pesan jelas.
- Evaluasi ditambah RMSE, tabel per-komponen, dan grafik PNG notebook (06/07/08).
"""
import os
import re
import gc
import glob
import inspect
import warnings
import numpy as np
import pandas as pd
import forecasting_engine as fe
from joblib import Parallel, delayed
from scipy.stats import pearsonr
from sklearn.preprocessing import MinMaxScaler

try:
    from PyEMD import EMD          # pip install EMD-signal
except ImportError:
    EMD = None
try:
    from vmdpy import VMD          # pip install vmdpy
except ImportError:
    VMD = None

try:
    import streamlit as st
except ImportError:
    st = None

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:
    go = None
    make_subplots = None

warnings.filterwarnings("ignore")

METODE = [
    "Hybrid ICEEMDAN-VMD-GRU",
    "Hybrid ICEEMDAN-GRU",
    "Hybrid VMD-GRU",
    "GRU",
]

# Parameter GRU standar (hanya dipakai pada fallback training ulang)
PARAM_STANDAR = {"units": 32, "dropout": 0.1, "lr": 0.003, "batch": 8, "epochs": 200}
VMD_K_STANDAR, VMD_ALPHA_STANDAR = 12, 100

METHOD_FOLDERS = {
    "Hybrid ICEEMDAN-VMD-GRU": "ICEEMDAN-VMD-GRU",
    "Hybrid ICEEMDAN-GRU": "ICEEMDAN-GRU",
    "Hybrid VMD-GRU": "VMD-GRU",
    "GRU": "GRU",
}

# Nama folder metode alternatif (dibandingkan setelah dinormalisasi: huruf kecil tanpa simbol)
METHOD_ALIASES = {
    "Hybrid ICEEMDAN-VMD-GRU": ["ICEEMDAN-VMD-GRU", "Hybrid ICEEMDAN-VMD-GRU", "ICEEMDAN_VMD_GRU"],
    "Hybrid ICEEMDAN-GRU": ["ICEEMDAN-GRU", "Hybrid ICEEMDAN-GRU", "ICEEMDAN_GRU", "ICEEMDAN GRU"],
    "Hybrid VMD-GRU": ["VMD-GRU", "Hybrid VMD-GRU", "VMD_GRU"],
    "GRU": ["GRU"],
}

DEST_ALIASES = {
    "gunung geger": ["Gunung Geger", "Gunung geger", "gunung geger", "gununggeger"],
    "kolla langgundi": ["Kolla Langgundi", "kolla langgundi", "Kolla Labgudih",
                        "Kolla Lab Gudih", "kolla-labgudih", "Langgundi", "Labgudih"],
    "makam air mata ibu": ["Makam Air Mata Ibu", "makam air mata ibu", "Air Mata Ibu",
                           "makamairmataibu"],
    "makam sunan cendana": ["Makam Sunan Cendana", "makam sunan cendana", "Sunan Cendana",
                            "sunan-cendana"],
    "makam syaikhona kholil": ["Makam Syaikhona Kholil", "makam syaikhona kholil",
                               "Syaikhona Kholil", "Syaikhona Cholil"],
}

# Destinasi yang hasil ICEEMDAN-GRU-nya berasal dari notebook -> tanpa training ulang
WAJIB_DARI_FOLDER = {
    "Hybrid ICEEMDAN-GRU": {"gunung geger", "kolla langgundi",
                            "makam air mata ibu", "makam sunan cendana"},
}

BULAN_PENDEK = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


class _Gagal(Exception):
    """File hasil notebook tidak lengkap; pesan berisi alasan yang bisa dibaca admin."""


# ============================================================
# HELPER UMUM
# ============================================================
def _fmt_id(x, dec=0):
    if x is None:
        return "-"
    try:
        s = f"{float(x):,.{dec}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(x)


def _tgl_id(iso):
    try:
        d = pd.Timestamp(iso)
        return f"{BULAN_PENDEK[d.month - 1]} {d.year}"
    except Exception:
        return str(iso)


def _show_chart(fig, **kw):
    if st is None or fig is None:
        return
    fn = st.plotly_chart
    if "width" in inspect.signature(fn).parameters:
        return fn(fig, width="stretch", **kw)
    return fn(fig, use_container_width=True, **kw)


def _show_df(df, **kw):
    if st is None:
        return
    fn = st.dataframe
    if "width" in inspect.signature(fn).parameters:
        return fn(df, width="stretch", **kw)
    return fn(df, use_container_width=True, **kw)


def _show_img(path, caption=None):
    """Kompatibel lintas versi Streamlit (width='stretch' vs use_container_width)."""
    if st is None:
        return
    try:
        st.image(path, caption=caption, width="stretch")
    except TypeError:
        st.image(path, caption=caption, use_container_width=True)


def _head(judul, sub=""):
    """Judul kartu grafik, gaya sama dengan dashboard User (.ct / .cs)."""
    if st is None:
        return
    st.markdown(f'<div class="ct">{judul}</div><div class="cs">{sub}</div>',
                unsafe_allow_html=True)


def _mcard(cls, label, nilai, sub):
    """Kartu metrik, gaya sama dengan dashboard User (.mcard)."""
    if st is None:
        return
    st.markdown(f'<div class="mcard {cls}"><div class="ml">{label}</div>'
                f'<div class="mv">{nilai}</div><div class="ms">{sub}</div></div>',
                unsafe_allow_html=True)


def _butuh(h, *keys):
    """True jika semua data tahap tersedia; jika tidak, tampilkan info (bukan error)."""
    if all(h.get(k) for k in keys):
        return True
    if st is not None:
        st.info("Data untuk tahap ini tidak tersedia. Pastikan folder hasil eksperimen "
                "(mis. `ICEEMDAN-VMD-GRU/<destinasi>/`) sudah diunggah ke direktori kerja.")
    return False


def _base_layout(fig, h=380):
    """Layout identik dengan _layout() pada dashboard User."""
    if fig is None:
        return None
    fig.update_layout(
        height=h, margin=dict(l=8, r=8, t=8, b=8), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#334155"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
        xaxis=dict(showgrid=False, tickformat="%Y", dtick="M12", linecolor="#cbd5e1"),
        yaxis=dict(gridcolor="#e2e8f0", tickformat=",.0f", zeroline=False),
    )
    if not (fig.layout.yaxis.title and fig.layout.yaxis.title.text):
        fig.update_layout(yaxis_title="Jumlah Pengunjung")
    return fig


# ============================================================
# PENCARIAN FOLDER HASIL NOTEBOOK (TOLERAN NAMA)
# ============================================================
def _nn(s):
    """Normalisasi nama: huruf kecil, hanya a-z0-9."""
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def _subdirs(path):
    try:
        return [d for d in sorted(os.listdir(path)) if os.path.isdir(os.path.join(path, d))]
    except Exception:
        return []


def _punya_hasil(path):
    return os.path.exists(os.path.join(path, "hasil-interpolasi",
                                       "data_cleaned_after_imputation.xlsx"))


def _akar_hasil(path):
    """Folder yang benar-benar berisi hasil notebook (boleh bersarang max 2 tingkat)."""
    if _punya_hasil(path):
        return path
    for d1 in _subdirs(path):
        p1 = os.path.join(path, d1)
        if _punya_hasil(p1):
            return p1
        for d2 in _subdirs(p1):
            p2 = os.path.join(p1, d2)
            if _punya_hasil(p2):
                return p2
    return None


def _kandidat_base(base_dir):
    out = []
    for b in (base_dir, os.getcwd()):
        try:
            b = os.path.abspath(b)
        except Exception:
            continue
        if b not in out:
            out.append(b)
    try:
        b = os.path.dirname(os.path.abspath(__file__))
        if b not in out:
            out.append(b)
    except Exception:
        pass
    return out


def cari_folder(metode, destinasi, base_dir="."):
    nama_metode = [_nn(x) for x in METHOD_ALIASES.get(metode, [METHOD_FOLDERS.get(metode, "")])]
    aliases = {_nn(a) for a in DEST_ALIASES.get(destinasi.lower(), [])} | {_nn(destinasi)}
    aliases.discard("")

    for base in _kandidat_base(base_dir):
        # 1) folder metode (nama toleran)
        m_dirs = [d for d in _subdirs(base) if _nn(d) in nama_metode]
        for md in m_dirs:
            full_m = os.path.join(base, md)
            subs = _subdirs(full_m)
            # exact (ternormalisasi) lebih dulu, lalu "mengandung"
            urut = [s for s in subs if _nn(s) in aliases] + \
                   [s for s in subs if _nn(s) not in aliases
                    and any(a in _nn(s) or _nn(s) in a for a in aliases if len(_nn(s)) >= 4)]
            for s in urut:
                akar = _akar_hasil(os.path.join(full_m, s))
                if akar:
                    return akar
    return None


def _daftar_dicari(metode, base_dir="."):
    return [os.path.join(b, METHOD_FOLDERS.get(metode, "?")) for b in _kandidat_base(base_dir)]


# ============================================================
# PEMUATAN HASIL DARI FOLDER NOTEBOOK
# ============================================================
# ============================================================
# PRA-PROSES ICEEMDAN-VMD-GRU (SAMA DENGAN NOTEBOOK)
# ============================================================
ICE_TRIALS, ICE_EPSILON, ICE_SEED, ICE_MAX_IMF = 100, 0.2, 42, 15
VMD_TAU, VMD_DC, VMD_INIT, VMD_TOL = 0.0, 0, 1, 1e-7
VMD_K_RANGE = range(2, 13)                 # K = 2..12
VMD_ALPHA_RANGE = range(100, 2100, 100)    # alpha = 100..2000
VMD_CORR_THRESHOLD = 1.2

BULAN_MAP = {"Januari": 1, "Februari": 2, "Maret": 3, "April": 4, "Mei": 5, "Juni": 6,
             "Juli": 7, "Agustus": 8, "September": 9, "Oktober": 10,
             "November": 11, "Desember": 12}


def _cache(fn):
    if st is not None and hasattr(st, "cache_data"):
        return st.cache_data(show_spinner=False)(fn)
    return fn


# ---------- 1. Baca file unggahan + deteksi nilai 0 ----------
def baca_file_unggahan(file):
    """Baca Excel format notebook (Bulan, Tahun, Pengunjung) atau (date, visitors).
    Mengembalikan DataFrame [date, visitors] apa adanya (nilai 0 belum ditangani)."""
    df = pd.read_excel(file)
    cols = {str(c).strip().lower(): c for c in df.columns}
    vcol = cols.get("pengunjung") or cols.get("visitors")
    if vcol is None:
        raise ValueError("Kolom 'Pengunjung' (atau 'visitors') tidak ditemukan di file.")

    if "date" in cols:
        dates = pd.to_datetime(df[cols["date"]])
    elif "bulan" in cols and "tahun" in cols:
        tahun = pd.to_numeric(df[cols["tahun"]], errors="coerce").ffill().astype(int)
        bulan = df[cols["bulan"]].astype(str).str.strip().str.title().map(BULAN_MAP)
        if bulan.isna().any():
            bad = df.loc[bulan.isna(), cols["bulan"]].unique().tolist()
            raise ValueError(f"Nama bulan tidak dikenali: {bad}")
        dates = pd.to_datetime(dict(year=tahun, month=bulan, day=1))
    else:
        raise ValueError("Butuh kolom 'date' atau kolom 'Bulan' + 'Tahun'.")

    out = pd.DataFrame({"date": dates,
                        "visitors": pd.to_numeric(df[vcol], errors="coerce").fillna(0.0)})
    return out.sort_values("date").reset_index(drop=True)


def deteksi_nol(df):
    """Daftar baris bernilai 0 (kolom: date, visitors)."""
    return df[df["visitors"] == 0][["date", "visitors"]].reset_index(drop=True)


def proses_interpolasi(df):
    """0 -> NaN -> interpolasi linear (identik notebook)."""
    raw = df["visitors"].astype(float)
    clean = raw.mask(raw == 0).interpolate(method="linear", limit_direction="both")
    return {
        "dates": pd.to_datetime(df["date"]).reset_index(drop=True),
        "raw": raw.values,
        "clean": clean.values,
        "idx_nol": np.where(raw.values == 0)[0],
    }


def panel_unggah_admin(key="adm_upload"):
    """Pakai di halaman Admin. Return (raw_df, data_clean) atau (None, None).
    data_clean (sudah diinterpolasi) bisa langsung dipakai untuk jalankan_metode()."""
    f = st.file_uploader("Unggah file Excel data kunjungan", type=["xlsx", "xls"], key=key)
    if f is None:
        return None, None
    try:
        raw_df = baca_file_unggahan(f)
    except Exception as e:
        st.error(f"File tidak dapat dibaca: {e}")
        return None, None
    nol = deteksi_nol(raw_df)
    if len(nol):
        st.warning(f"Terdeteksi {len(nol)} nilai 0 pada data. "
                   "Akan ditangani dengan interpolasi linear.")
    else:
        st.success("Tidak ada nilai 0 pada data.")
    pra = proses_interpolasi(raw_df)
    data_clean = pd.DataFrame({"date": pra["dates"], "visitors": pra["clean"]})
    return raw_df, data_clean


# ---------- 2. ICEEMDAN (kode notebook) ----------
def _n_extrema(x):
    d = np.diff(x)
    return int(np.sum(d[:-1] * d[1:] < 0))


def _local_mean(z):
    imfs = EMD().emd(z, max_imf=1)
    if len(imfs) < 2:
        return z.copy()
    return z - imfs[0]


def _noise_imfs(n, seed, kmax):
    w = np.random.default_rng(seed).standard_normal(n)
    imfs = EMD().emd(w)
    out = np.zeros((kmax, n))
    for k in range(min(kmax, len(imfs))):
        s = imfs[k].std()
        if s > 0:
            out[k] = imfs[k] / s
    return out


def _trial_mean(r, noise_k, beta):
    return _local_mean(r + beta * noise_k)


def _iceemdan_nb(x, trials, epsilon0, max_imf, seed, n_jobs=-1):
    x = np.asarray(x, dtype=float)
    n = len(x)
    ss = np.random.SeedSequence(seed).spawn(trials)
    seeds = [int(s.generate_state(1)[0]) for s in ss]
    noise = Parallel(n_jobs=n_jobs)(delayed(_noise_imfs)(n, sd, max_imf + 1) for sd in seeds)
    modes, r_prev = [], x.copy()
    for k in range(1, max_imf + 1):
        beta = epsilon0 * np.std(r_prev)
        means = Parallel(n_jobs=n_jobs)(
            delayed(_trial_mean)(r_prev, noise[i][k - 1], beta) for i in range(trials))
        r_k = np.mean(means, axis=0)
        modes.append(r_prev - r_k)
        r_prev = r_k
        if _n_extrema(r_prev) < 3:
            break
    modes.append(r_prev)
    return np.array(modes)


@_cache
def hitung_iceemdan(x):
    """Return dict {IMF_1..IMF_n, ICEEMDAN_Residue}. Di-cache agar tidak dihitung ulang."""
    if EMD is None:
        raise RuntimeError("Paket EMD-signal belum terpasang (pip install EMD-signal).")
    modes = _iceemdan_nb(np.asarray(x, float), ICE_TRIALS, ICE_EPSILON, ICE_MAX_IMF, ICE_SEED)
    comps = {f"IMF_{i + 1}": modes[i] for i in range(len(modes) - 1)}
    comps["ICEEMDAN_Residue"] = modes[-1]
    return comps


# ---------- 3. VMD (kode notebook) ----------
def _vmd_metrics(f, u):
    K = u.shape[0]
    cors = [abs(pearsonr(u[i], u[i + 1])[0]) for i in range(K - 1)]
    mean_corr = float(np.mean(cors)) if cors else 0.0
    elc = float(np.sum((f - np.sum(u, axis=0)) ** 2) / np.sum(f ** 2))
    bws = []
    for i in range(K):
        psd = np.abs(np.fft.fft(u[i])) ** 2
        fr = np.fft.fftfreq(len(u[i]))
        pos = fr >= 0
        p, fp = psd[pos], fr[pos]
        if p.sum() > 0:
            mf = np.sum(fp * p) / p.sum()
            bws.append(np.sum(((fp - mf) ** 2) * p) / p.sum())
        else:
            bws.append(0.0)
    return mean_corr, elc, float(np.mean(bws))


@_cache
def cari_vmd(f):
    """Pencarian K & alpha untuk SATU sinyal IMF persis seperti notebook.
    Return {'candidates': [...], 'best': {...}, 'modes': ndarray(K, N)}."""
    if VMD is None:
        raise RuntimeError("Paket vmdpy belum terpasang (pip install vmdpy).")
    f = np.asarray(f, dtype=float)
    candidates = []
    for K in VMD_K_RANGE:
        prev_corr, best_a, best_m = 999, None, None
        for alpha in VMD_ALPHA_RANGE:
            u, _, _ = VMD(f, alpha, VMD_TAU, K, VMD_DC, VMD_INIT, VMD_TOL)
            corr, elc, bw = _vmd_metrics(f, u)
            if alpha > 100 and corr > prev_corr * VMD_CORR_THRESHOLD:
                break
            best_a, best_m, prev_corr = alpha, (corr, elc, bw), corr
        if best_a is not None:
            candidates.append({"K": K, "alpha": best_a, "Corr": best_m[0],
                               "ELC": best_m[1], "BW": best_m[2]})
    filt = [c for c in candidates if c["ELC"] < 0.01] or candidates
    best = min(filt, key=lambda c: (round(c["BW"], 5), c["ELC"], c["Corr"]))
    u_opt, _, _ = VMD(f, best["alpha"], VMD_TAU, best["K"], VMD_DC, VMD_INIT, VMD_TOL)
    return {"candidates": candidates, "best": best, "modes": np.asarray(u_opt)}


def hitung_semua_vmd(imfs, progress=None):
    """Jalankan VMD untuk semua IMF (residu ICEEMDAN tidak di-VMD, sama dgn notebook)."""
    names = [k for k in imfs if "RESIDUE" not in k.upper()]
    out = {}
    for i, name in enumerate(names):
        if progress:
            progress(i / max(len(names), 1), f"Mencari parameter VMD untuk {name} "
                                             f"({i + 1}/{len(names)})...")
        out[name] = cari_vmd(np.asarray(imfs[name], float))
    if progress:
        progress(1.0, "Selesai")
    return out


def gabung_komponen(imfs, vmd_all):
    """Susun komponen final: IMF_k_VMD_m ... + ICEEMDAN_Residue (urutan = notebook)."""
    comps = {}
    for name, r in vmd_all.items():
        for m in range(r["modes"].shape[0]):
            comps[f"{name}_VMD_{m + 1}"] = r["modes"][m]
    for k in imfs:
        if "RESIDUE" in k.upper():
            comps[k] = np.asarray(imfs[k], float)
    return comps


# ---------- 4. Grafik ----------
_PAL = ["#1e293b", "#0284c7", "#0d9488", "#16a34a", "#ca8a04", "#ea580c", "#dc2626", "#9333ea"]


def _stack_fig(dates, items, h_per=150):
    """items = [(judul, y), ...] -> subplot bertumpuk."""
    n = len(items)
    fig = make_subplots(rows=n, cols=1, shared_xaxes=True,
                        vertical_spacing=min(0.035, 0.9 / max(n, 1)),
                        subplot_titles=[t.replace("_", " ") for t, _ in items])
    for i, (t, y) in enumerate(items):
        fig.add_trace(go.Scatter(
            x=dates, y=y, mode="lines", showlegend=False,
            line=dict(color=_PAL[i % len(_PAL)], width=1.6),
            hovertemplate=f"{t}: %{{y:,.2f}}<extra></extra>"), row=i + 1, col=1)
    fig.update_layout(height=max(h_per * n, 320), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                      margin=dict(l=10, r=10, t=30, b=10),
                      font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#334155"))
    return fig


def fig_deteksi_nol(pra):
    """Data aktual (sebelum interpolasi); nilai 0 ditandai merah."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pra["dates"], y=pra["raw"], mode="lines+markers",
                             name="Data Aktual", line=dict(color="#1e293b", width=1.8),
                             marker=dict(size=4),
                             hovertemplate="Aktual: %{y:,.0f}<extra></extra>"))
    i0 = pra["idx_nol"]
    if len(i0):
        fig.add_trace(go.Scatter(x=pra["dates"].iloc[i0], y=pra["raw"][i0], mode="markers",
                                 name="Nilai 0 Terdeteksi",
                                 marker=dict(size=10, color="#ef4444", symbol="diamond"),
                                 hovertemplate="Nilai 0<extra></extra>"))
    return _base_layout(fig, h=340)


def fig_interpolasi_x(pra):
    """Hasil interpolasi linear; titik 0 yang berhasil diinterpolasi diberi tanda x."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pra["dates"], y=pra["clean"], mode="lines", name="Hasil Interpolasi Linear",
                             line=dict(color="#0284c7", width=2.4),
                             hovertemplate="Interpolasi: %{y:,.0f}<extra></extra>"))
    i0 = pra["idx_nol"]
    if len(i0):
        fig.add_trace(go.Scatter(x=pra["dates"].iloc[i0], y=pra["clean"][i0], mode="markers",
                                 name="Nilai 0 → Terinterpolasi (x)",
                                 marker=dict(size=11, color="#ef4444", symbol="x",
                                             line=dict(width=2, color="#ef4444")),
                                 hovertemplate="Hasil imputasi: %{y:,.0f}<extra></extra>"))
    return _base_layout(fig, h=340)


def fig_vmd_search(cands, best):
    """3 panel: Mean Bandwidth, ELC, Mean Correlation terhadap K (K optimal garis merah)."""
    df = pd.DataFrame(cands)
    fig = make_subplots(rows=1, cols=3, horizontal_spacing=0.07,
                        subplot_titles=["Mean Bandwidth", "Energy Loss (ELC)", "Mean Correlation"])
    for i, (col, sym) in enumerate([("BW", "circle"), ("ELC", "square"), ("Corr", "diamond")], 1):
        fig.add_trace(go.Scatter(
            x=df["K"], y=df[col], mode="lines+markers", showlegend=False,
            line=dict(color="#0284c7"), marker=dict(symbol=sym, size=7), customdata=df["alpha"],
            hovertemplate="K=%{x}<br>alpha=%{customdata}<br>" + col + "=%{y:.5f}<extra></extra>"),
            row=1, col=i)
        fig.add_trace(go.Scatter(x=[best["K"]], y=[best[col]], mode="markers", showlegend=False,
                                 marker=dict(color="#ef4444", size=12), hoverinfo="skip"),
                      row=1, col=i)
        fig.add_vline(x=best["K"], line=dict(color="#ef4444", dash="dash"), row=1, col=i)
    fig.add_hline(y=0.01, line=dict(color="#f59e0b", dash="dash"), row=1, col=2)
    fig.update_xaxes(dtick=1, title_text="K")
    fig.update_layout(height=340, plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                      margin=dict(l=10, r=10, t=40, b=10),
                      font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#334155"))
    return fig


def fig_norm_pra(dates, y_raw, y_norm, nama):
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.08,
                        subplot_titles=[f"Sebelum Normalisasi — {nama}",
                                        f"Sesudah Normalisasi (0–1) — {nama}"])
    fig.add_trace(go.Scatter(x=dates, y=y_raw, mode="lines", name="Skala Asli",
                             line=dict(color="#0284c7", width=2.0),
                             hovertemplate="Nilai asli: %{y:,.2f}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=y_norm, mode="lines", name="Skala [0, 1]",
                             line=dict(color="#10b981", width=2.0),
                             hovertemplate="Normalisasi: %{y:.4f}<extra></extra>"), row=1, col=2)
    fig.update_yaxes(title_text="Nilai Asli", row=1, col=1)
    fig.update_yaxes(title_text="Value (0–1)", range=[-0.05, 1.05], row=1, col=2)
    fig.update_layout(height=380, plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                      margin=dict(l=10, r=10, t=40, b=10), showlegend=False,
                      font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#334155"))
    return fig


# ---------- 5. Penyedia data pra-proses ----------
def _raw_df_dari_h(h):
    """Bila tidak ada file unggahan, rekonstruksi data mentah dari hasil folder (gap = 0)."""
    return pd.DataFrame({"date": pd.to_datetime(h["tgl_hist"]),
                         "visitors": h.get("raw_hist", h["aktual_hist"])})


def _ambil_imfs(h, pra, dari_unggahan):
    """ICEEMDAN: dari folder notebook bila ada & tidak ada unggahan baru; selain itu hitung."""
    ice = h.get("ice_data") or {}
    if (not dari_unggahan) and h.get("loaded_from_folder") and ice:
        return {k: np.asarray(v, float) for k, v in ice.items()}
    with st.spinner("Menjalankan I-CEEMDAN (trials=100, ε0=0.2, seed=42)... "
                    "pertama kali bisa beberapa menit, selanjutnya instan."):
        return hitung_iceemdan(np.asarray(pra["clean"], float))


def _progress_ui():
    bar = st.progress(0.0, text="Memulai...")
    def cb(f, t):
        bar.progress(min(max(f, 0.0), 1.0), text=t)
    return bar, cb


# ---------- 6. Render tahap Interpolasi / ICEEMDAN / VMD / Normalisasi ----------
def render_tahap_praproses(h, tahap, kp, raw_df=None):
    if go is None or make_subplots is None:
        st.error("Plotly belum terpasang.")
        return
    df = raw_df if raw_df is not None else _raw_df_dari_h(h)
    pra = proses_interpolasi(df)
    tgl = pra["dates"]

    # ICEEMDAN/VMD hanya dihitung ulang jika data hasil interpolasi BERBEDA dari
    # data di folder notebook. Jika sama, hasil folder dipakai (instan).
    dari_unggahan = False
    if raw_df is not None:
        a = np.asarray(h["aktual_hist"], float)
        b = np.asarray(pra["clean"], float)
        dari_unggahan = (len(a) != len(b)) or float(np.max(np.abs(a - b))) > 2.0

    # ============ INTERPOLASI LINEAR ============
    if tahap == "Interpolasi Linear":
        n0 = len(pra["idx_nol"])
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            _mcard("a", "TOTAL DATA", _fmt_id(len(df)), "observasi bulanan")
        with c2:
            _mcard("b", "NILAI 0 TERDETEKSI", _fmt_id(n0),
                   f"{n0 / max(len(df), 1) * 100:.1f}% dari data")
        with c3:
            _mcard("a", "METODE PENANGANAN", "Linear", "0 → NaN → interpolasi linear")
        st.write("")
        with st.container(border=True):
            _head("Data Aktual (Sebelum Interpolasi)",
                  "Titik merah = nilai 0 yang terdeteksi pada file masukan")
            _show_chart(fig_deteksi_nol(pra), key=f"{kp}_deteksi")
        st.write("")
        with st.container(border=True):
            _head("Hasil Interpolasi Linear",
                  "Tanda x = nilai 0 yang berhasil diinterpolasi")
            _show_chart(fig_interpolasi_x(pra), key=f"{kp}_interp")
            if n0:
                with st.expander("Lihat tabel nilai 0 yang diimputasi"):
                    i0 = pra["idx_nol"]
                    _show_df(pd.DataFrame({
                        "Bulan": [_tgl_id(d) for d in tgl.iloc[i0]],
                        "Nilai Awal": [0] * n0,
                        "Hasil Interpolasi": [_fmt_id(v) for v in pra["clean"][i0]],
                    }), hide_index=True)
            else:
                st.info("Tidak ada nilai 0, data digunakan apa adanya.")
        return

    # ============ ICEEMDAN ============
    imfs = _ambil_imfs(h, pra, dari_unggahan)
    keys = list(imfs.keys())
    n_imf = len(keys) - 1

    if tahap == "Dekomposisi I-CEEMDAN":
        with st.container(border=True):
            _head("Dekomposisi I-CEEMDAN")
            items = [("Sinyal Input (Hasil Interpolasi)", pra["clean"])]
            items += [(k, imfs[k]) for k in keys]
            _show_chart(_stack_fig(tgl, items), key=f"{kp}_ice")
            rec = np.sum([imfs[k] for k in keys], axis=0)
            st.caption(f"MAE rekonstruksi (Σ IMF + residu vs sinyal): "
                       f"{_fmt_id(np.mean(np.abs(pra['clean'] - rec)), 6)}")
        return

    # ============ VMD ============
    if tahap == "Dekomposisi VMD":
        bar, cb = _progress_ui()
        try:
            vmd_all = hitung_semua_vmd(imfs, cb)
        except Exception as e:
            bar.empty()
            st.error(f"VMD gagal dijalankan: {e}")
            return
        bar.empty()

        with st.container(border=True):
            _head("Parameter VMD Terbaik per IMF")
            _show_df(pd.DataFrame([{
                "IMF": n, "K": r["best"]["K"], "Alpha": r["best"]["alpha"],
                "Corr": round(r["best"]["Corr"], 5), "ELC": round(r["best"]["ELC"], 5),
                "BW": round(r["best"]["BW"], 5)} for n, r in vmd_all.items()]),
                hide_index=True)
        st.write("")
        for i, (name, r) in enumerate(vmd_all.items()):
            b = r["best"]
            with st.expander(f"{name} — optimal K={b['K']}, Alpha={b['alpha']}", expanded=(i == 0)):
                _head(f"Pencarian Parameter VMD ({name})",
                      f"Garis merah = K optimal (K={b['K']}, Alpha={b['alpha']})")
                _show_chart(fig_vmd_search(r["candidates"], b), key=f"{kp}_vs_{name}")
                _head(f"Hasil Dekomposisi VMD ({name})", f"{b['K']} mode")
                items = [(f"Sinyal Input ({name})", imfs[name])]
                items += [(f"Mode {m + 1}", r["modes"][m]) for m in range(r["modes"].shape[0])]
                _show_chart(_stack_fig(tgl, items, h_per=130), key=f"{kp}_vm_{name}")
        return

    # ============ NORMALISASI ============
    if tahap == "Normalisasi":
        if (not dari_unggahan) and h.get("loaded_from_folder") and h.get("comps"):
            comps = {k: np.asarray(v, float) for k, v in h["comps"].items()}
        else:
            bar, cb = _progress_ui()
            vmd_all = hitung_semua_vmd(imfs, cb)
            bar.empty()
            comps = gabung_komponen(imfs, vmd_all)

        nama = st.selectbox("Pilih komponen", list(comps.keys()), key=f"{kp}_pilih_norm")
        y = comps[nama].reshape(-1, 1)
        sc = MinMaxScaler(feature_range=(0, 1))
        y_norm = sc.fit_transform(y).ravel()
        with st.container(border=True):
            _head("Normalisasi Min-Max per Komponen")
            _show_chart(fig_norm_pra(tgl, y.ravel(), y_norm, nama), key=f"{kp}_norm")
            with st.expander("Ringkasan Min–Max seluruh komponen"):
                _show_df(pd.DataFrame([{
                    "Komponen": k, "x_min": round(float(np.min(v)), 4),
                    "x_max": round(float(np.max(v)), 4),
                    "Range": round(float(np.max(v) - np.min(v)), 4)}
                    for k, v in comps.items()]), hide_index=True)


# ============================================================
# PEMUATAN HASIL DARI FOLDER NOTEBOOK  (direkonstruksi: bagian ini hilang di versi lama)
# ============================================================
def _rmse(y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    return float(np.sqrt(np.mean((y - p) ** 2)))


def _mape(y, p, eps=1e-8):
    y, p = np.asarray(y, float), np.asarray(p, float)
    return float(np.mean(np.abs((y - p) / np.maximum(np.abs(y), eps))) * 100.0)


def _cari_scaler(scaler_dir, comp_name, metode=None):
    """Cari file scaler (.pkl/.joblib) untuk satu komponen; toleran nama."""
    if not os.path.isdir(scaler_dir):
        return None
    files = [f for f in os.listdir(scaler_dir) if f.lower().endswith((".pkl", ".joblib"))]
    for cand in (f"scaler_{comp_name}.pkl", f"{comp_name}.pkl", f"scaler_{comp_name}.joblib"):
        if cand in files:
            return os.path.join(scaler_dir, cand)
    target = _nn(comp_name)
    for f in files:
        stem = _nn(os.path.splitext(f)[0])
        if stem in (target, "scaler" + target, target + "scaler"):
            return os.path.join(scaler_dir, f)
    if metode == "GRU" and len(files) == 1:       # GRU murni: hanya ada satu scaler
        return os.path.join(scaler_dir, files[0])
    return None


def _scaler_inverse(pkl, arr):
    """inverse_transform dengan scaler tersimpan; None bila gagal (dipakai fallback min-max)."""
    try:
        import joblib
        sc = joblib.load(pkl)
        return sc.inverse_transform(np.asarray(arr, float).reshape(-1, 1)).ravel()
    except Exception:
        return None


def _norm_minmax(comps):
    out = {}
    for k, v in comps.items():
        v = np.asarray(v, float)
        rng = v.max() - v.min()
        out[k] = ((v - v.min()) / (rng if rng > 0 else 1.0)).tolist()
    return out


def _ringkas_minmax(comps):
    rows = []
    for k, v in comps.items():
        v = np.asarray(v, float)
        rows.append({"Komponen": k, "x_min": float(v.min()), "x_max": float(v.max()),
                     "range": float(v.max() - v.min())})
    return rows


def _turunan_dari_comps(comps, metode):
    """Turunkan (ice_data, vmd_modes) dari komponen akhir (dipakai hasil fallback)."""
    comps = {k: np.asarray(v, float) for k, v in comps.items()}
    if metode == "Hybrid ICEEMDAN-GRU":
        return {k: v.tolist() for k, v in comps.items()}, {}
    if metode == "Hybrid VMD-GRU":
        return {}, {k: v.tolist() for k, v in comps.items()}
    if metode == "Hybrid ICEEMDAN-VMD-GRU":
        ice, vmd, grup = {}, {}, {}
        for k, v in comps.items():
            m = re.match(r"^(IMF_\d+)_VMD_\d+$", k)
            if m:
                grup.setdefault(m.group(1), []).append(v)
                vmd[k] = v.tolist()
            elif "RESIDUE" in k.upper():
                ice[k] = v.tolist()
        for imf, lst in grup.items():
            ice[imf] = np.sum(lst, axis=0).tolist()
        return dict(sorted(ice.items(), key=lambda kv: (("RESIDUE" in kv[0].upper()), kv[0]))), vmd
    return {}, {}


def _baca_tabel(path):
    try:
        if path.lower().endswith((".xlsx", ".xls")):
            return pd.read_excel(path)
        return pd.read_csv(path)
    except Exception:
        return None


def _kolom_tanggal(df):
    low = {str(c).strip().lower(): c for c in df.columns}
    for k in ("date", "tanggal", "periode"):
        if k in low:
            return pd.to_datetime(df[low[k]]).dt.to_period("M").dt.to_timestamp()
    if "bulan" in low and "tahun" in low:
        tahun = pd.to_numeric(df[low["tahun"]], errors="coerce").ffill().astype(int)
        bln = df[low["bulan"]].map(fe._bulan_ke_angka)      # Indonesia/Inggris/angka
        if bln.isna().any():
            raise _Gagal("Nama bulan pada data_cleaned_after_imputation.xlsx tidak dikenali")
        return pd.to_datetime(dict(year=tahun, month=bln.astype(int), day=1))
    raise _Gagal("Kolom tanggal (date / Bulan+Tahun) tidak ditemukan di data_cleaned_after_imputation.xlsx")


def _muat_interpolasi(folder):
    """Return (dates[str], visitors_clean[float], raw_visitors[float], gap_log[list])."""
    p = os.path.join(folder, "hasil-interpolasi", "data_cleaned_after_imputation.xlsx")
    if not os.path.exists(p):
        raise _Gagal(f"File tidak ada: {p}")
    df = _baca_tabel(p)
    if df is None or df.empty:
        raise _Gagal(f"File tidak terbaca/kosong: {p}")
    tgl = _kolom_tanggal(df)
    cols = {str(c).strip().lower(): c for c in df.columns}

    def pilih(*kunci):
        for k in kunci:
            for lc, c in cols.items():
                if k == lc:
                    return c
        for k in kunci:
            for lc, c in cols.items():
                if k in lc:
                    return c
        return None

    c_raw = pilih("raw", "original", "asli", "sebelum", "visitors_raw")
    c_clean = pilih("cleaned", "clean", "imput", "interpol", "visitors", "pengunjung")
    if c_clean is None or c_clean == c_raw:
        num = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])
               and str(c).strip().lower() not in ("tahun", "year", "bulan", "month")]
        if not num:
            raise _Gagal(f"Kolom jumlah pengunjung tidak ditemukan di {p}")
        c_clean = num[-1]
    clean = pd.to_numeric(df[c_clean], errors="coerce").astype(float).values
    raw = (pd.to_numeric(df[c_raw], errors="coerce").fillna(0.0).astype(float).values
           if c_raw is not None and c_raw != c_clean else clean.copy())
    dates = [d.strftime("%Y-%m-%d") for d in tgl]
    gap_log = [{"date": dates[i], "new_value": float(clean[i])}
               for i in np.where(raw == 0)[0] if clean[i] != 0]
    return dates, clean.tolist(), raw.tolist(), gap_log


def _muat_dekomposisi(folder, nama_komp):
    """Ambil komponen (IMF/VMD) dari hasil-dekomposisi; return (comps, ice_data)."""
    comps, ice = {}, {}
    dd = os.path.join(folder, "hasil-dekomposisi")
    files = []
    for ext in ("*.csv", "*.xlsx"):
        files += glob.glob(os.path.join(dd, ext))
    peta = {_nn(n): n for n in nama_komp}
    for f in sorted(files):
        df = _baca_tabel(f)
        if df is None:
            continue
        is_ice = "iceemdan" in os.path.basename(f).lower() and "vmd" not in os.path.basename(f).lower()
        for c in df.columns:
            key = _nn(c)
            if key in ("sinyalasli", "date", "tanggal", "bulan", "tahun", "unnamed0"):
                continue
            if not pd.api.types.is_numeric_dtype(df[c]):
                continue
            if is_ice and (re.match(r"^IMF_\d+$", str(c)) or "residue" in str(c).lower()):
                ice[str(c)] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(float).tolist()
            if key in peta and peta[key] not in comps:
                comps[peta[key]] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(float).tolist()
    return comps, ice


def _muat_inti(folder, destinasi, metode):
    """Muat seluruh hasil notebook dari satu folder. Raise _Gagal bila tidak lengkap."""
    dates, visitors_clean, raw_visitors, gap_log = _muat_interpolasi(folder)

    # ---- Prediksi uji per komponen + denormalisasi (scaler PKL) ----
    preds_dir = os.path.join(folder, "retrain-preds")
    scaler_dir = os.path.join(folder, "scaler")
    pred_files = sorted(glob.glob(os.path.join(preds_dir, "preds_*.csv"))) if os.path.isdir(preds_dir) else []
    if not pred_files:
        raise _Gagal(f"Tidak ada preds_*.csv di {preds_dir}")

    comps0, _ice0 = _muat_dekomposisi(folder, [os.path.splitext(os.path.basename(p))[0].replace("preds_", "", 1)
                                               for p in pred_files])
    min_max_summary = _ringkas_minmax(comps0) if comps0 else []
    v_min, v_max = min(visitors_clean), max(visitors_clean)
    sub_mode_preds, y_preds_den_list = {}, []
    for pf in pred_files:
        comp_name = os.path.splitext(os.path.basename(pf))[0].replace("preds_", "", 1)
        try:
            dfp = pd.read_csv(pf)
            y_true_n = dfp["y_true"].values.astype(float)
            y_pred_n = dfp["y_pred"].values.astype(float)
        except Exception as e:
            raise _Gagal(f"File prediksi tidak terbaca ({pf}): {e}")

        y_pred_den = y_true_den = None
        pkl = _cari_scaler(scaler_dir, comp_name, metode)
        if pkl:
            y_pred_den = _scaler_inverse(pkl, y_pred_n)
            y_true_den = _scaler_inverse(pkl, y_true_n)
        if y_pred_den is None or y_true_den is None:
            mm = next((m for m in min_max_summary if m["Komponen"] == comp_name), None)
            if mm and mm["range"] > 0:
                x_min, rng = mm["x_min"], mm["range"]
            elif metode == "GRU":             # GRU murni: skala = data asli
                x_min, rng = v_min, max(v_max - v_min, 1e-8)
            else:
                raise _Gagal(f"Scaler untuk komponen '{comp_name}' tidak ada/rusak di {scaler_dir} "
                             f"(butuh scaler_{comp_name}.pkl) sehingga denormalisasi tidak akurat")
            y_pred_den = y_pred_n * rng + x_min
            y_true_den = y_true_n * rng + x_min

        sub_mode_preds[comp_name] = {
            "y_true_norm": y_true_n.tolist(), "y_pred_norm": y_pred_n.tolist(),
            "y_pred_den": np.asarray(y_pred_den).tolist(),
            "y_true_den": np.asarray(y_true_den).tolist(),
            "mae_norm": float(np.mean(np.abs(y_true_n - y_pred_n))),
            "rmse_norm": _rmse(y_true_n, y_pred_n),
            "mape_norm": _mape(y_true_n, y_pred_n),
            "mae_den": float(np.mean(np.abs(y_true_den - y_pred_den))),
            "rmse_den": _rmse(y_true_den, y_pred_den),
            "mape_den": _mape(y_true_den, y_pred_den),
        }
        y_preds_den_list.append(np.asarray(y_pred_den, dtype=float))

    # ---- komponen dekomposisi, ICEEMDAN, VMD, normalisasi, ringkasan min-max ----
    comps, ice_data = _muat_dekomposisi(folder, list(sub_mode_preds.keys()))
    if metode == "Hybrid ICEEMDAN-GRU" and not ice_data:
        ice_data = dict(comps)
    if metode == "GRU" and not comps:
        comps = {"GRU": list(visitors_clean)}
    _, vmd_modes = _turunan_dari_comps(comps, metode)
    vmd_data = {"params": [], "modes": vmd_modes}
    norm_data = _norm_minmax(comps) if comps else {}

    n_uji = min(len(a) for a in y_preds_den_list)
    pred_uji_total = np.sum([a[-n_uji:] for a in y_preds_den_list], axis=0)
    split_idx = len(visitors_clean) - n_uji
    aktual_uji = visitors_clean[split_idx:]
    tgl_uji = dates[split_idx:]

    akt = np.asarray(aktual_uji, dtype=float)
    mae = float(np.mean(np.abs(akt - pred_uji_total)))
    rmse = _rmse(akt, pred_uji_total)
    mape = _mape(akt, pred_uji_total)

    # Skala normalisasi total (sama seperti notebook: min-max data asli, clip 0-1)
    rng_all = max(v_max - v_min, 1e-8)
    akt_norm_a = (akt - v_min) / rng_all
    pred_norm_a = np.clip((pred_uji_total - v_min) / rng_all, 0.0, 1.0)

    # ---- Prediksi 12 bulan ke depan ----
    fut_p = os.path.join(folder, "hasil-prediksi-future", "future_predictions_12_months.csv")
    if not os.path.exists(fut_p):
        raise _Gagal(f"File tidak ada: {fut_p}")
    try:
        df_fut = pd.read_csv(fut_p)
        tgl_fut = pd.to_datetime(df_fut["Date"]).dt.strftime("%Y-%m-%d").tolist()
        pred_fut = [float(round(v)) for v in df_fut["Predicted_Visitors"]]
    except Exception as e:
        raise _Gagal(f"File prediksi future tidak terbaca ({fut_p}): {e}")
    if not tgl_fut:
        raise _Gagal(f"File prediksi future kosong: {fut_p}")

    # ---- Grafik PNG notebook ----
    png_map = {}
    grafik_dir = os.path.join(folder, "output_hasil", "grafik")
    if os.path.isdir(grafik_dir):
        for fn in os.listdir(grafik_dir):
            if fn.lower().endswith(".png"):
                png_map[fn] = os.path.join(grafik_dir, fn).replace("\\", "/")

    return {
        "destinasi": destinasi,
        "metode": metode,
        "tgl_hist": dates,
        "aktual_hist": visitors_clean,
        "raw_hist": raw_visitors,
        "gap_log": gap_log,
        "split_idx": int(split_idx),
        "tgl_uji": tgl_uji,
        "aktual_uji": aktual_uji,
        "prediksi_uji": pred_uji_total.tolist(),
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "mae_norm": float(np.mean(np.abs(akt_norm_a - pred_norm_a))),
        "rmse_norm": _rmse(akt_norm_a, pred_norm_a),
        "mape_norm": _mape(akt_norm_a, pred_norm_a),
        "actual_test_signal_norm": akt_norm_a.tolist(),
        "x_pred_norm_final": pred_norm_a.tolist(),
        "tgl_fut": tgl_fut,
        "prediksi_fut": pred_fut,
        "comps": comps,
        "ice_data": ice_data,
        "vmd_data": vmd_data,
        "norm_data": norm_data,
        "min_max_summary": min_max_summary,
        "sub_mode_preds": sub_mode_preds,
        "png_map": png_map,
        "n_komponen": len(comps),
        "folder": folder,
        "loaded_from_folder": True,
    }


LAST_ERROR = {"msg": ""}


def muat_hasil_folder(folder, destinasi, metode):
    """API lama: kembalikan dict hasil atau None (alasan di LAST_ERROR['msg'])."""
    try:
        LAST_ERROR["msg"] = ""
        return _muat_inti(folder, destinasi, metode)
    except _Gagal as e:
        LAST_ERROR["msg"] = str(e)
        return None


def _signature(folder):
    """Tanda perubahan folder: berubah bila ada file hasil yang diganti/ditambah."""
    patt = ["hasil-interpolasi/*.xlsx", "hasil-dekomposisi/*.csv", "retrain-preds/*.csv",
            "scaler/*.pkl", "hasil-prediksi-future/*.csv", "hasil-normalisasi/*"]
    tot, mx = 0, 0.0
    for p in patt:
        for f in glob.glob(os.path.join(folder, p)):
            try:
                mx = max(mx, os.path.getmtime(f))
                tot += 1
            except Exception:
                pass
    return f"{tot}:{mx}"


def _muat_cached(folder, destinasi, metode, sig):
    """Mengembalikan (hasil, alasan). Hanya hasil sukses yang berguna di-cache; kegagalan
    ikut ter-cache tetapi kunci cache memuat signature folder sehingga otomatis ter-refresh
    begitu file diperbaiki."""
    try:
        return _muat_inti(folder, destinasi, metode), ""
    except _Gagal as e:
        return None, str(e)


# Cache agar interaksi widget (rerun Streamlit) tidak membaca ulang file Excel/CSV.
if st is not None and hasattr(st, "cache_data"):
    _muat_cached = st.cache_data(show_spinner=False)(_muat_cached)


# ============================================================
# FALLBACK: TRAINING ULANG (LAMBAT, HANYA JIKA FOLDER TIDAK ADA)
# ============================================================
def _cache_decomp(nama, sinyal, fungsi):
    import joblib
    import hashlib
    os.makedirs(fe.CACHE_DIR, exist_ok=True)
    hs = hashlib.sha1(nama.encode() + sinyal.tobytes()).hexdigest()
    f = os.path.join(fe.CACHE_DIR, f"decomp_adm_{hs}.pkl")
    if os.path.exists(f):
        try:
            return joblib.load(f)
        except Exception:
            pass
    hasil = fungsi()
    try:
        joblib.dump(hasil, f)
    except Exception:
        pass
    return hasil


def _komponen(destinasi, metode, sinyal):
    if metode == "Hybrid ICEEMDAN-GRU":
        def _ice():
            modes = fe.iceemdan(sinyal)
            comps = {f"IMF_{i + 1}": m for i, m in enumerate(modes[:-1])}
            comps["ICEEMDAN_Residue"] = modes[-1]
            return comps
        return _cache_decomp("ice_only", sinyal, _ice)

    if metode == "Hybrid VMD-GRU":
        cfg = fe.CONFIG.get(destinasi, {})
        if cfg.get("metode") == "vmd":
            K, alpha = cfg["K"], cfg["alpha"]
        else:
            K, alpha = VMD_K_STANDAR, VMD_ALPHA_STANDAR

        def _v():
            u = fe._vmd(sinyal, alpha, K)
            return {f"VMD_{k + 1}": u[k] for k in range(K)}
        return _cache_decomp(f"vmd_{K}_{alpha}", sinyal, _v)

    return {"GRU": sinyal}          # GRU murni tanpa dekomposisi


def _lengkapi(h, comps=None):
    """Isi field yang dibutuhkan UI agar hasil fallback tidak membuat error."""
    h.setdefault("raw_hist", list(h.get("aktual_hist", [])))
    h.setdefault("gap_log", [])
    h.setdefault("png_map", {})
    h.setdefault("sub_mode_preds", {})
    h.setdefault("loaded_from_folder", False)
    if comps:
        comps = {k: [float(x) for x in v] for k, v in comps.items()}
        h.setdefault("comps", comps)
        ice, vmd = _turunan_dari_comps(comps, h.get("metode", ""))
        h.setdefault("ice_data", ice)
        h.setdefault("vmd_data", {"params": [], "modes": vmd})
        h.setdefault("norm_data", _norm_minmax(comps))
        h.setdefault("min_max_summary", _ringkas_minmax(comps))
    return h


def _latih_ulang(destinasi, data_clean, metode, progress=None):
    def lapor(f, t):
        if progress:
            progress(min(max(f, 0.0), 1.0), t)

    sinyal = data_clean["visitors"].values.astype(float)
    dates = pd.to_datetime(data_clean["date"]).reset_index(drop=True)
    N = len(sinyal)
    split_idx = int(N * (1 - fe.TEST_RATIO))

    lapor(0.02, "Menyiapkan data & dekomposisi sinyal...")
    comps = _komponen(destinasi, metode, sinyal)

    table = {}
    if metode == "Hybrid VMD-GRU" and fe.CONFIG.get(destinasi, {}).get("metode") == "vmd":
        table = fe.parse_table(fe.CONFIG[destinasi]["tabel"])

    total = len(comps)
    pred_uji_total = np.zeros(N - split_idx)
    pred_fut_total = np.zeros(fe.HORIZON)
    n_default = 0
    lapor(0.12, "Menyiapkan model prediksi...")
    for i, (name, seri) in enumerate(comps.items()):
        par = table.get(name)
        if par is None:
            par = PARAM_STANDAR
            n_default += 1
        pu, pf = fe._latih_dan_prediksi(seri, par, seed=42 + i)
        pred_uji_total += pu
        pred_fut_total += pf
        lapor(0.12 + 0.86 * (i + 1) / total, f"Memproses model {i + 1} dari {total}...")

    try:
        import tensorflow as tf
        tf.keras.backend.clear_session()
    except Exception:
        pass
    gc.collect()

    pred_fut_total = np.maximum(pred_fut_total, 0.0)
    aktual_uji = sinyal[split_idx:]
    tgl_uji = dates.iloc[split_idx:]
    tgl_fut = pd.date_range(dates.iloc[-1] + pd.DateOffset(months=1),
                            periods=fe.HORIZON, freq="MS")
    lapor(1.0, "Selesai")
    hasil = {
        "destinasi": destinasi,
        "metode": metode,
        "tgl_hist": [d.strftime("%Y-%m-%d") for d in dates],
        "aktual_hist": [float(v) for v in sinyal],
        "split_idx": int(split_idx),
        "tgl_uji": [d.strftime("%Y-%m-%d") for d in tgl_uji],
        "aktual_uji": [float(v) for v in aktual_uji],
        "prediksi_uji": [float(v) for v in pred_uji_total],
        "mae": fe.hitung_mae(aktual_uji, pred_uji_total),
        "mape": fe.hitung_mape(aktual_uji, pred_uji_total),
        "tgl_fut": [d.strftime("%Y-%m-%d") for d in tgl_fut],
        "prediksi_fut": [float(round(v)) for v in pred_fut_total],
        "n_komponen": int(total),
        "n_param_default": int(n_default),
    }
    return _lengkapi(hasil, comps)


def _hentikan(pesan):
    """Tampilkan pesan jelas lalu hentikan (tanpa training ulang diam-diam)."""
    if st is not None:
        st.error(pesan)
        st.stop()
    raise FileNotFoundError(pesan)


def jalankan_metode(destinasi, data_clean, metode, progress=None):
    """Muat hasil dari folder notebook untuk SEMUA metode (cepat).
    Training ulang hanya sebagai fallback jika folder/file tidak lengkap
    (kecuali metode+destinasi di WAJIB_DARI_FOLDER, mis. ICEEMDAN-GRU 4 destinasi notebook)."""
    def lapor(f, t):
        if progress:
            progress(min(max(f, 0.0), 1.0), t)

    lapor(0.15, f"Mencari file hasil eksperimen untuk {metode}...")
    fol = cari_folder(metode, destinasi)
    alasan = ""
    if fol:
        lapor(0.40, f"Memuat hasil ({os.path.basename(fol)})...")
        res, alasan = _muat_cached(fol, destinasi, metode, _signature(fol))
        if res:
            lapor(1.0, "Selesai")
            return res
    else:
        alasan = ("Folder hasil tidak ditemukan. Dicari di: "
                  + "; ".join(_daftar_dicari(metode)) + f"/<{destinasi}>/hasil-interpolasi/...")

    if destinasi.lower() in WAJIB_DARI_FOLDER.get(metode, set()):
        _hentikan(
            f"Hasil notebook **{metode}** untuk **{destinasi}** tidak dapat dimuat.\n\n"
            f"Alasan: {alasan}\n\n"
            "Pastikan folder hasil notebook diletakkan sebagai "
            f"`{METHOD_FOLDERS.get(metode)}/<nama destinasi>/` yang berisi: `hasil-interpolasi/`, "
            "`hasil-dekomposisi/`, `hasil-normalisasi/`, `scaler/`, `retrain-preds/`, "
            "`hasil-prediksi-future/`, `output_hasil/`.")

    # ---- Fallback (lambat) ----
    lapor(0.02, "Folder hasil tidak lengkap, menjalankan ulang model...")
    if metode == "Hybrid ICEEMDAN-VMD-GRU":
        res = fe.jalankan_prediksi(destinasi, data_clean, progress=progress)
        if isinstance(res, dict):
            res.setdefault("metode", metode)
            _lengkapi(res)
        return res
    return _latih_ulang(destinasi, data_clean, metode, progress=progress)


# ============================================================
# FUNGSI GRAFIK PLOTLY
# ============================================================
def fig_interpolasi(h):
    if go is None:
        return None
    tgl = pd.to_datetime(h["tgl_hist"])
    cd = [_tgl_id(d) for d in h["tgl_hist"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tgl, y=h["aktual_hist"], mode="lines", name="Hasil Interpolasi Linear (Trend)",
        line=dict(color="#0284c7", width=2.4), customdata=cd,
        hovertemplate="Hasil Interpolasi: %{y:,.0f}<br>Tanggal: %{customdata}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=tgl, y=h["raw_hist"], mode="lines+markers", name="Data Asli (Sebelum Interpolasi)",
        line=dict(color="#1e293b", width=1.5), marker=dict(size=4, color="#0f172a"),
        customdata=cd,
        hovertemplate="Data Asli: %{y:,.0f}<br>Tanggal: %{customdata}<extra></extra>"
    ))
    if h.get("gap_log"):
        gap_dates = [pd.to_datetime(r["date"]) for r in h["gap_log"]]
        gap_vals = [r.get("new_value", 0) for r in h["gap_log"]]
        fig.add_trace(go.Scatter(
            x=gap_dates, y=gap_vals, mode="markers", name="Titik Gap (Nilai 0 Diimputasi)",
            marker=dict(size=8, color="#ef4444", symbol="diamond"),
            hovertemplate="Imputasi Gap: %{y:,.0f}<extra></extra>"
        ))
    fig.update_layout(yaxis_title="Jumlah Pengunjung", xaxis_title="Tahun & Bulan")
    return _base_layout(fig, h=400)


def fig_iceemdan(h):
    if go is None or make_subplots is None:
        return None
    ice_items = list(h.get("ice_data", {}).items())
    if not ice_items:
        return None
    tgl = pd.to_datetime(h["tgl_hist"])
    n_ice = len(ice_items)
    titles = [k.replace("_", " ") for k, _ in ice_items]
    fig = make_subplots(rows=n_ice, cols=1, shared_xaxes=True,
                        vertical_spacing=min(0.035, 0.9 / max(n_ice, 1)),
                        subplot_titles=titles)
    colors = ["#1e293b", "#0284c7", "#0d9488", "#16a34a", "#ca8a04", "#ea580c", "#dc2626", "#9333ea"]
    for idx, (k, vals) in enumerate(ice_items):
        fig.add_trace(go.Scatter(
            x=tgl, y=vals, mode="lines", name=k,
            line=dict(color=colors[idx % len(colors)], width=1.8), showlegend=False,
            hovertemplate=f"{k}: %{{y:,.2f}}<extra></extra>"
        ), row=idx + 1, col=1)
    fig.update_layout(
        height=max(140 * n_ice, 520), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#334155"))
    return fig


def fig_vmd(h, max_modes=12):
    if go is None:
        return None
    vmd_modes = h.get("vmd_data", {}).get("modes", {})
    if not vmd_modes:
        return None
    tgl = pd.to_datetime(h["tgl_hist"])
    fig = go.Figure()
    for m_name, m_vals in list(vmd_modes.items())[:max_modes]:
        fig.add_trace(go.Scatter(
            x=tgl, y=m_vals, mode="lines", name=m_name, line=dict(width=1.5),
            hovertemplate=f"{m_name}: %{{y:,.2f}}<extra></extra>"
        ))
    fig.update_layout(yaxis_title="Nilai Amplitudo Sub-Mode", xaxis_title="Periode Waktu")
    return _base_layout(fig, h=420)


def fig_normalisasi(h, comp_name=None):
    if go is None or make_subplots is None:
        return None
    comps = h.get("comps", {})
    norm_d = h.get("norm_data", {})
    if not comps:
        return None
    if not comp_name or comp_name not in comps:
        comp_name = list(comps.keys())[0]

    tgl = pd.to_datetime(h["tgl_hist"])
    y_raw = comps[comp_name]
    y_norm = norm_d.get(comp_name) or _norm_minmax({comp_name: y_raw})[comp_name]

    fig = make_subplots(
        rows=1, cols=2, horizontal_spacing=0.08,
        subplot_titles=[f"Sebelum Normalisasi (Skala Asli) — {comp_name}",
                        f"Sesudah Normalisasi (Skala 0–1 Min-Max) — {comp_name}"])
    fig.add_trace(go.Scatter(
        x=tgl, y=y_raw, mode="lines", name="Skala Asli",
        line=dict(color="#0284c7", width=2.0),
        hovertemplate="Nilai Asli: %{y:,.2f}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=tgl, y=y_norm, mode="lines", name="Skala [0, 1]",
        line=dict(color="#10b981", width=2.0),
        hovertemplate="Normalisasi: %{y:.4f}<extra></extra>"), row=1, col=2)
    fig.update_yaxes(title_text="Nilai Asli", row=1, col=1)
    fig.update_yaxes(title_text="Value (0–1)", range=[-0.05, 1.05], row=1, col=2)
    fig.update_layout(
        height=380, plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        margin=dict(l=10, r=10, t=35, b=10),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#334155"))
    return fig


def fig_denormalisasi(h, comp_name=None):
    """Tidak dipakai di menu (denormalisasi tidak ditampilkan), disediakan bila dibutuhkan."""
    if go is None or make_subplots is None:
        return None
    sub_preds = h.get("sub_mode_preds", {})
    tgl_uji = pd.to_datetime(h["tgl_uji"])

    if comp_name and comp_name in sub_preds:
        d = sub_preds[comp_name]
        s1 = (f"1. {comp_name} — Skala [0, 1] (MAE = {d['mae_norm']:.4f} | "
              f"MAPE = {d['mape_norm']:.2f}%)")
        s2 = (f"2. {comp_name} — Skala Asli (MAE = {_fmt_id(d.get('mae_den', 0), 2)} | "
              f"MAPE = {_fmt_id(d.get('mape_den', 0), 2)}%)")
        y1a, y1p, y2a, y2p = d["y_true_norm"], d["y_pred_norm"], d["y_true_den"], d["y_pred_den"]
    else:
        s1 = "1. Rekonstruksi Prediksi vs Aktual (Normalisasi 0–1)"
        s2 = (f"2. Rekonstruksi Prediksi vs Aktual (Skala Asli) — MAE = {_fmt_id(h['mae'], 2)} | "
              f"MAPE = {_fmt_id(h['mape'], 2)}%")
        y1a, y1p = h.get("actual_test_signal_norm", []), h.get("x_pred_norm_final", [])
        y2a, y2p = h["aktual_uji"], h["prediksi_uji"]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
                        subplot_titles=[s1, s2])
    for row, (ya, yp) in enumerate([(y1a, y1p), (y2a, y2p)], start=1):
        fig.add_trace(go.Scatter(x=tgl_uji, y=ya, mode="lines+markers", name="Aktual",
                                 line=dict(color="#1f77b4", width=2.2), marker=dict(size=6),
                                 showlegend=(row == 1)), row=row, col=1)
        fig.add_trace(go.Scatter(x=tgl_uji, y=yp, mode="lines+markers", name="Prediksi",
                                 line=dict(color="#ff7f0e", width=1.8, dash="dash"),
                                 marker=dict(size=7, symbol="x"),
                                 showlegend=(row == 1)), row=row, col=1)
    fig.update_yaxes(title_text="Value (0–1)", range=[-0.05, 1.05], row=1, col=1)
    fig.update_yaxes(title_text="Nilai", tickformat=",.0f", row=2, col=1)
    fig.update_layout(
        height=680, plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        margin=dict(l=10, r=10, t=55, b=10), hovermode="x unified",
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#334155"),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="left", x=0))
    fig.update_xaxes(tickformat="%b %Y", dtick="M2")
    return fig


def fig_aktual_prediksi(h):
    if go is None:
        return None
    tgl = pd.to_datetime(h["tgl_hist"])
    tgl_uji = pd.to_datetime(h["tgl_uji"])
    fig = go.Figure()
    fig.add_vrect(
        x0=tgl_uji[0], x1=tgl_uji[-1], fillcolor="rgba(249,115,22,0.07)", line_width=0,
        annotation_text="Periode uji", annotation_position="top left",
        annotation_font=dict(size=11, color="#c2410c"))
    fig.add_trace(go.Scatter(
        x=tgl, y=h["aktual_hist"], name="Aktual", mode="lines",
        line=dict(color="#0284c7", width=2.4),
        customdata=[_tgl_id(d) for d in h["tgl_hist"]],
        hovertemplate="Aktual: %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=tgl_uji, y=h["prediksi_uji"], name="Prediksi", mode="lines+markers",
        line=dict(color="#f97316", width=2.4, dash="dash"), marker=dict(size=6),
        hovertemplate="Prediksi: %{y:,.0f}<extra></extra>"))
    return _base_layout(fig, h=380)


def fig_masa_depan(h):
    if go is None:
        return None
    n_tampil = 36
    tgl = pd.to_datetime(h["tgl_hist"])[-n_tampil:]
    akt = h["aktual_hist"][-n_tampil:]
    tgl_f = pd.to_datetime(h["tgl_fut"])
    fig = go.Figure()
    fig.add_vrect(
        x0=tgl_f[0], x1=tgl_f[-1], fillcolor="rgba(13,148,136,0.07)", line_width=0,
        annotation_text="12 bulan ke depan", annotation_position="top left",
        annotation_font=dict(size=11, color="#0f766e"))
    fig.add_trace(go.Scatter(
        x=tgl, y=akt, name="Data historis", mode="lines",
        line=dict(color="#0284c7", width=2.4),
        hovertemplate="Aktual: %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=[tgl[-1], tgl_f[0]], y=[akt[-1], h["prediksi_fut"][0]],
        mode="lines", showlegend=False, hoverinfo="skip",
        line=dict(color="#0d9488", width=1.6, dash="dot")))
    fig.add_trace(go.Scatter(
        x=tgl_f, y=h["prediksi_fut"], name="Prediksi 12 bulan",
        mode="lines+markers", line=dict(color="#0d9488", width=2.6, dash="dash"),
        marker=dict(size=7), hovertemplate="Prediksi: %{y:,.0f}<extra></extra>"))
    _base_layout(fig, h=380)
    fig.update_xaxes(tickformat="%b %Y", dtick="M6")   # setelah layout agar tidak tertimpa
    return fig


# ============================================================
# MENU TAHAPAN PER METODE
# ============================================================

OPSI_PER_METODE = {
    "Hybrid ICEEMDAN-VMD-GRU": ["Interpolasi Linear", "Dekomposisi I-CEEMDAN", "Dekomposisi VMD",
                                "Normalisasi", "Evaluasi & Prediksi"],
    "Hybrid ICEEMDAN-GRU": ["Interpolasi Linear", "Dekomposisi I-CEEMDAN",
                            "Normalisasi", "Evaluasi & Prediksi"],
    "Hybrid VMD-GRU": ["Interpolasi Linear", "Dekomposisi VMD",
                       "Normalisasi", "Evaluasi & Prediksi"],
    "GRU": ["Interpolasi Linear", "Normalisasi", "Evaluasi & Prediksi"],
}


def _menu_tahapan(opsi, key):
    """Menu satu baris (segmented control); fallback radio horizontal."""
    if st.session_state.get(key) not in (None, *opsi):
        del st.session_state[key]
    if key not in st.session_state:
        st.session_state[key] = opsi[0]          # tab pertama = Interpolasi Linear

    if hasattr(st, "segmented_control"):
        kw = {}
        if "width" in inspect.signature(st.segmented_control).parameters:
            kw["width"] = "stretch"
        pilihan = st.segmented_control(
            "Pilih Visualisasi Tahapan:", opsi, selection_mode="single",
            key=key, label_visibility="collapsed", **kw)
        if pilihan is None:          # klik ulang tab aktif -> tetap di tab sebelumnya
            pilihan = st.session_state.get(f"_tahap_{key}", opsi[0])
            st.session_state[key] = pilihan
    else:
        pilihan = st.radio("Pilih Visualisasi Tahapan:", opsi, horizontal=True,
                           key=key, label_visibility="collapsed")
    st.session_state[f"_tahap_{key}"] = pilihan
    return pilihan


# ============================================================
# DETAIL EVALUASI SEPERTI NOTEBOOK (RMSE, per-komponen, grafik PNG)
# ============================================================
def _render_detail_notebook(h, kp):
    """Ringkasan tambahan yang sama dengan output notebook (sel evaluasi & future)."""
    if not h.get("loaded_from_folder"):
        return
    st.write("")
    with st.container(border=True):
        _head("Ringkasan Evaluasi Seperti Notebook",
              "Metrik rekonstruksi akhir (jumlah seluruh sub-komponen) pada data uji")
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            _mcard("a", "MAE (SKALA ASLI)", _fmt_id(h["mae"], 2), "pengunjung")
        with c2:
            _mcard("b", "RMSE (SKALA ASLI)", _fmt_id(h.get("rmse"), 2), "pengunjung")
        with c3:
            _mcard("a", "MAPE (SKALA ASLI)", _fmt_id(h["mape"], 2) + "%", "persentase kesalahan")
        if h.get("mae_norm") is not None:
            st.caption(f"Skala normalisasi 0–1: MAE = {h['mae_norm']:.4f} | "
                       f"RMSE = {h['rmse_norm']:.4f} | MAPE = {h['mape_norm']:.2f}%")

        sub = h.get("sub_mode_preds", {})
        if sub:
            with st.expander("Lihat metrik evaluasi per sub-komponen (IMF & Residu)"):
                rows = [{
                    "Sub-Komponen": k,
                    "MAE (Norm)": round(d["mae_norm"], 4),
                    "RMSE (Norm)": round(d.get("rmse_norm", float("nan")), 4),
                    "MAPE (Norm) %": round(d["mape_norm"], 2),
                    "MAE (Skala Asli)": round(d["mae_den"], 4),
                    "RMSE (Skala Asli)": round(d.get("rmse_den", float("nan")), 4),
                    "MAPE (Skala Asli) %": round(d["mape_den"], 2),
                } for k, d in sub.items()]
                _show_df(pd.DataFrame(rows), hide_index=True)

        with st.expander("Lihat tabel aktual vs prediksi rekonstruksi (data uji)"):
            akt = np.asarray(h["aktual_uji"], dtype=float)
            prd = np.asarray(h["prediksi_uji"], dtype=float)
            _show_df(pd.DataFrame({
                "Bulan": [_tgl_id(d) for d in h["tgl_uji"]],
                "Aktual": [_fmt_id(v) for v in akt],
                "Prediksi": [_fmt_id(v) for v in prd],
                "Selisih Absolut": [_fmt_id(v) for v in np.abs(akt - prd)],
            }), hide_index=True)

        png_list = [
            ("06_final_reconstruction_prediction_norm.png", "Rekonstruksi prediksi (skala 0–1)"),
            ("07_final_reconstruction_prediction_original_scale.png",
             "Rekonstruksi prediksi (skala asli)"),
            ("08_future_predictions_12_months.png", "Proyeksi 12 bulan ke depan"),
        ]
        ada = [(n, c) for n, c in png_list
               if h.get("png_map", {}).get(n) and os.path.exists(h["png_map"][n])]
        if ada:
            with st.expander("Lihat grafik evaluasi dari notebook (PNG)"):
                for n, c in ada:
                    _show_img(h["png_map"][n], c)


# ============================================================
# RENDER HASIL ADMIN (SEMUA METODE)
# ============================================================
def render_hasil_admin(h, render_user=None, raw_df=None):
    if st is None:
        return
    metode = h.get("metode", "Hybrid ICEEMDAN-VMD-GRU")
    opsi = OPSI_PER_METODE.get(metode, OPSI_PER_METODE["GRU"])
    kp = "adm_" + metode.replace(" ", "_").replace("-", "_")

    with st.container(border=True):
        _head("Pilih Visualisasi Tahapan",
              f"Alur {metode.replace('Hybrid ', '')}: dari data aktual sampai hasil peramalan")
        pilihan = _menu_tahapan(opsi, key=f"{kp}_menu")
    st.write("")

    # Tahap pra-proses (khusus ICEEMDAN-VMD-GRU); evaluasi & prediksi tetap seperti semula
    if pilihan != "Evaluasi & Prediksi":
        if metode == "Hybrid ICEEMDAN-VMD-GRU":
            render_tahap_praproses(h, pilihan, kp, raw_df)
        return

    # ---------------- Evaluasi & Prediksi (TIDAK DIUBAH) ----------------
    # ... biarkan seluruh isi lama mulai dari `if True:` sampai akhir fungsi ...

    # ---------------- Evaluasi & Prediksi ----------------
    if True:
        if render_user is not None:
            render_user(h)
            _render_detail_notebook(h, kp)
            return
        if not _butuh(h, "tgl_uji", "tgl_fut"):
            return
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            _mcard("a", "MAE (Mean Absolute Error)", _fmt_id(h["mae"], 2),
                   "rata-rata selisih absolut aktual dan prediksi ")
        with c2:
            _mcard("b", "MAPE (Mean Absolute Percentage Error)", _fmt_id(h["mape"], 2) + "%",
                   "rata-rata persentase kesalahan prediksi")
        with st.container(border=True):
            _head("Visualisasi Data Aktual dan Prediksi",
                  f'Evaluasi pada periode uji {_tgl_id(h["tgl_uji"][0])} – '
                  f'{_tgl_id(h["tgl_uji"][-1])} ({len(h["tgl_uji"])} bulan)')
            _show_chart(fig_aktual_prediksi(h), key=f"{kp}_aktual")
        st.write("")
        with st.container(border=True):
            _head("Prediksi Kunjungan 12 Bulan ke Depan",
                  f'{_tgl_id(h["tgl_fut"][0])} – {_tgl_id(h["tgl_fut"][-1])}')
            _show_chart(fig_masa_depan(h), key=f"{kp}_future")
            with st.expander("Lihat tabel prediksi"):
                _show_df(pd.DataFrame({
                    "Bulan": [_tgl_id(d) for d in h["tgl_fut"]],
                    "Prediksi Pengunjung": [_fmt_id(v) for v in h["prediksi_fut"]],
                }), hide_index=True)
        _render_detail_notebook(h, kp)


# Alias agar pemanggil lama tetap berjalan
render_hasil_iceemdan_vmd_gru = render_hasil_admin


# === AKHIR FILE admin_methods.py (jika baris ini tidak ada di file Anda, salinan terpotong) ===