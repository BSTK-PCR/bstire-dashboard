import base64
import os
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

# ─────────────────────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="브리지스톤 PCR 세일즈 대시보드",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# 로고 base64 인코딩
# ─────────────────────────────────────────────────────────────
def _logo_b64() -> str:
    try:
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

def _logo4_b64() -> str:
    try:
        with open("logo4.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

# ─────────────────────────────────────────────────────────────
# 글로벌 CSS  (Bridgestone brand: Barlow Condensed + Noto Sans KR)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Barlow:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

/* ── 기본 타이포그래피 ── */
html, body, [class*="css"] {
    font-family: 'Barlow', 'Noto Sans KR', sans-serif;
}
h1, h2, h3 {
    font-family: 'Barlow Condensed', 'Noto Sans KR', sans-serif !important;
    letter-spacing: 0.5px;
}

/* ── 앱 배경 ── */
.stApp {
    background: #0d1117;
}
section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1f2937;
}

/* ── KPI 카드 ── */
.kpi-card {
    background: linear-gradient(135deg, #161d2e 0%, #1a2234 100%);
    border-left: 3px solid #E2231A;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 4px 0;
    box-shadow: 0 1px 6px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.03);
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 60px; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(226,35,26,0.05));
    pointer-events: none;
}
.kpi-label {
    color: #6b7280;
    font-family: 'Barlow', 'Noto Sans KR', sans-serif;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    margin-bottom: 8px;
}
.kpi-value {
    color: #f1f5f9;
    font-family: 'Barlow Condensed', 'Noto Sans KR', sans-serif;
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.5px;
}
.kpi-delta-neg { color: #f87171; font-size: 11px; margin-top: 5px; font-weight: 600; }
.kpi-delta-pos { color: #4ade80; font-size: 11px; margin-top: 5px; font-weight: 600; }

/* ── 헤더 배너 ── */
.header-banner {
    background: linear-gradient(135deg, #111827 0%, #161d2e 100%);
    border-top: 3px solid #E2231A;
    border-radius: 8px;
    padding: 20px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 18px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.4);
}
.header-logo-box {
    background: #ffffff;
    border-radius: 6px;
    padding: 6px 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 1px 6px rgba(0,0,0,0.35);
}
.header-logo-img {
    width: 52px;
    height: 52px;
    object-fit: contain;
    flex-shrink: 0;
    display: block;
}
.header-logo-fallback {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #E2231A;
    color: #fff;
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 800;
    font-size: 14px;
    letter-spacing: 2px;
    width: 52px;
    height: 52px;
    border-radius: 4px;
    text-transform: uppercase;
    flex-shrink: 0;
}
.header-divider {
    width: 1px;
    height: 44px;
    background: #2d3748;
    flex-shrink: 0;
}
.header-text { flex: 1; }
.header-title {
    color: #f1f5f9;
    font-family: 'Barlow Condensed', 'Noto Sans KR', sans-serif;
    font-size: 24px;
    font-weight: 700;
    margin: 0 0 3px 0;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}
.header-sub {
    color: #4b5563;
    font-family: 'Barlow', sans-serif;
    font-size: 11px;
    margin: 0;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

/* ── 섹션 구분선 ── */
.section-divider {
    border: none;
    border-top: 1px solid #1f2937;
    margin: 20px 0;
}

/* ── Plotly 배경 투명 ── */
.js-plotly-plot .plotly .main-svg {
    background: transparent !important;
}

/* ── 탭 스타일 ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    border-bottom: 2px solid #1f2937;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Barlow', 'Noto Sans KR', sans-serif;
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 0.3px;
    color: #6b7280;
    border-radius: 6px 6px 0 0;
    padding: 8px 16px;
    border: none;
    background: transparent;
    transition: background 0.15s, color 0.15s;
}
.stTabs [data-baseweb="tab"]:hover {
    background: #1a2234;
    color: #e5e7eb;
}
.stTabs [aria-selected="true"] {
    background: #1a2234 !important;
    color: #E2231A !important;
    border-bottom: 2px solid #E2231A !important;
}

/* ── 사이드바 스타일 ── */
.sidebar-logo-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 0 12px 0;
}
.sidebar-logo-img {
    width: 110px;
    object-fit: contain;
}

/* ── 데이터 상태 뱃지 ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: 'Barlow', 'Noto Sans KR', sans-serif;
    font-size: 11px;
    font-weight: 600;
}
.status-dot-green { width:7px; height:7px; border-radius:50%; background:#22c55e; display:inline-block; }
.status-dot-yellow { width:7px; height:7px; border-radius:50%; background:#fbbf24; display:inline-block; }

/* ── 업로드 페이지 상태 카드 ── */
.upload-status-card {
    background: #161d2e;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.upload-status-label {
    color: #6b7280;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.upload-status-value-active {
    color: #22c55e;
    font-size: 13px;
    font-weight: 600;
}
.upload-status-value-default {
    color: #fbbf24;
    font-size: 13px;
    font-weight: 600;
}

/* ── 데이터프레임 스타일 ── */
.stDataFrame {
    border: 1px solid #1f2937 !important;
    border-radius: 6px !important;
}

/* ── Y26 사업실적 요약 테이블 ── */
.summary-wrap { overflow-x: auto; margin: 8px 0; }
.summary-table {
    width: 100%; border-collapse: collapse;
    font-family: 'Barlow', 'Noto Sans KR', sans-serif;
    font-size: 12px; color: #e5e7eb;
}
.summary-table th {
    background: #1f2937; color: #9ca3af;
    font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
    padding: 7px 12px; border: 1px solid #374151;
    text-align: center; white-space: nowrap;
}
.summary-table th.col-jun { background:#78350f !important; color:#fde68a !important; }
.summary-table td {
    padding: 5px 12px; border: 1px solid #1f2937;
    text-align: right; white-space: nowrap;
}
.summary-table td.row-label {
    text-align: left; font-weight: 700; color: #f3f4f6;
    background: #161d2e; min-width: 80px;
}
.summary-table td.row-type {
    text-align: left; color: #9ca3af; font-size: 11px;
    background: #0f1724; min-width: 90px;
}
.summary-table td.col-jun {
    background: rgba(245,158,11,0.12) !important;
    color: #fbbf24 !important; font-weight: 600;
}
.section-header-row td {
    background: #E2231A !important; color: #fff !important;
    font-weight: 700; font-size: 11px; letter-spacing: 0.8px;
    text-align: left !important; padding: 5px 12px;
}
.py-row td { background: #111827; color: #6b7280; font-size: 11px; }
.ob-row td { background: #1a2234; color: #d1d5db; }
.rf-row td { background: #1e293b; color: #d1d5db; }
.act-main-row td { background: #1c2b1c; color: #f9fafb; font-weight: 700; font-size: 13px; }
.act-main-row td.act-val { color: #34d399 !important; }
.act-sub-row td { background: #131a13; color: #9ca3af; font-size: 11px; }
.asp-row td { background: #1a1a2e; color: #d1d5db; }

/* ── 사이드바 로고 화이트 박스 ── */
.sidebar-logo-box {
    background: #ffffff;
    border-radius: 6px;
    padding: 8px 14px;
    margin-bottom: 4px;
    display: inline-block;
    box-shadow: 0 1px 6px rgba(0,0,0,0.35);
}
.sidebar-logo-box img {
    width: 130px;
    height: auto;
    display: block;
}

/* ── 업로드 컬럼 타이틀 고정 높이 (4컬럼 정렬 일치) ── */
.upload-col-title {
    min-height: 60px;
    font-family: 'Barlow Condensed', 'Noto Sans KR', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1.3;
    padding: 4px 0 10px 0;
    display: flex;
    align-items: flex-start;
}

/* ── 업로드 파일명 캡션 고정 높이 (4컬럼 정렬 일치) ── */
.upload-file-caption {
    min-height: 44px;
    font-family: 'Barlow', 'Noto Sans KR', sans-serif;
    font-size: 0.875rem;
    color: rgba(250, 250, 250, 0.6);
    line-height: 1.5;
    margin-bottom: 4px;
    display: flex;
    align-items: flex-start;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 차트 공통 레이아웃
# ─────────────────────────────────────────────────────────────
CHART_COLORS = ["#E2231A", "#FF6B35", "#FFA62B", "#5B9BD5", "#70AD47", "#9B59B6"]

def dark_layout(fig, height=400):
    fig.update_layout(
        height=height,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb",
        xaxis=dict(gridcolor="#374151", showgrid=True),
        yaxis=dict(gridcolor="#374151", showgrid=True),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#e5e7eb"),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig

# ─────────────────────────────────────────────────────────────
# KPI 카드 HTML
# ─────────────────────────────────────────────────────────────
def kpi_card(label: str, value: str, delta: float | None = None) -> str:
    delta_html = ""
    if delta is not None:
        cls = "kpi-delta-neg" if delta < 0 else "kpi-delta-pos"
        arrow = "▼" if delta < 0 else "▲"
        delta_html = f'<div class="{cls}">{arrow} {abs(delta):.1f}%</div>'
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>"""

# ─────────────────────────────────────────────────────────────
# Supabase (선택) — 없으면 로컬 파일 / 세션 상태 fallback
# ─────────────────────────────────────────────────────────────
def _get_supabase():
    try:
        from supabase import create_client
        url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
        key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None

SUPABASE = _get_supabase()
BUCKET = "xlsx-data"
SALES_KEY = "sales_latest.xlsx"
PCR_KEY = "pcr_latest.xlsx"
ORDER_KEY = "order_latest.xlsx"
PRICE_KEY = "price_latest.xlsx"
LOCAL_SALES = "data/sales data_260627.xlsx"
LOCAL_PCR = "data/(PCR) Jun sales data_260626_FCST_V2.xlsx"
LOCAL_ORDER = "data/PCR - Jul26 prod order sheet_Final.xlsx"
LOCAL_PRICE = "data/2026 브리지스톤 PCR 타이어 가격표_Final.xlsx"


def _supabase_upload(raw: bytes, filename: str) -> bool:
    if not SUPABASE:
        return False
    try:
        SUPABASE.storage.from_(BUCKET).upload(filename, raw, {"upsert": "true"})
        return True
    except Exception as e:
        st.warning(f"Supabase 저장 실패: {e}")
        return False


def _supabase_download(filename: str) -> bytes | None:
    if not SUPABASE:
        return None
    try:
        return SUPABASE.storage.from_(BUCKET).download(filename)
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────
# 파싱
# ─────────────────────────────────────────────────────────────
def _to_float(val) -> float:
    if pd.isna(val):
        return float("nan")
    s = str(val).replace("%", "").strip()
    try:
        v = float(s)
        return v if v > 1 else round(v * 100, 2)
    except ValueError:
        return float("nan")


@st.cache_data(show_spinner=False)
def parse_sales(raw: bytes) -> pd.DataFrame:
    df = pd.read_excel(BytesIO(raw), sheet_name="Sheet1")
    df.columns = df.columns.str.strip()
    for col in ["할인율(%)", "6월 할인율(%)"]:
        if col in df.columns:
            df[col] = df[col].apply(_to_float)
    for col in ["수량", "할인전 금액", "할인 금액", "6월 수량"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["이익부서"])


@st.cache_data(show_spinner=False)
def parse_monthly(raw: bytes) -> dict[str, pd.DataFrame]:
    result = {}
    targets = {"jun": "6월 매출현황(6.26)", "may": "5월 매출현황(5.31)"}
    for key, sheet in targets.items():
        try:
            df = pd.read_excel(BytesIO(raw), sheet_name=sheet, header=1)
            df.columns = df.columns.str.strip()
            df = df[pd.to_numeric(df.get("NO", pd.Series(dtype=object)), errors="coerce").notna()]
            df["합계금액"] = pd.to_numeric(df["합계금액"], errors="coerce")
            df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce")
            df = df.dropna(subset=["거래처", "합계금액"])
            result[key] = df
        except Exception as e:
            st.warning(f"[{sheet}] 로드 실패: {e}")
    return result


@st.cache_data(show_spinner=False)
def parse_main_targets(raw: bytes) -> pd.DataFrame:
    """Main 시트에서 거래처별 6월 목표/실적 수량 및 리베이트 금액 목표 파싱.

    컬럼 인덱스 기준 (0-indexed):
      1=PIC, 2=대리점, 28~32=Jan~May Act,
      33=JUN RF, 34=Jun FCST, 35=Jun Act(26), 38=1H ACT, 41=Rebate Amt 1H
    """
    try:
        df = pd.read_excel(BytesIO(raw), sheet_name="Main", header=None)
    except Exception:
        return pd.DataFrame()

    if len(df.columns) < 42:
        return pd.DataFrame()

    data = df.iloc[9:].reset_index(drop=True)
    _SKIP = {"Total", "B2C", "경영기획"}

    def _v(row, i):
        return row.iloc[i] if len(row) > i else None

    records = []
    for _, row in data.iterrows():
        dealer = _v(row, 2)
        if pd.isna(dealer) or not str(dealer).strip():
            continue
        dealer = str(dealer).strip()
        if any(kw in dealer for kw in _SKIP):
            continue
        pic = _v(row, 1)
        records.append({
            "PIC": str(pic).strip() if pd.notna(pic) else None,
            "대리점": dealer,
            "JAN_ACT": _v(row, 28), "FEB_ACT": _v(row, 29),
            "MAR_ACT": _v(row, 30), "APR_ACT": _v(row, 31),
            "MAY_ACT": _v(row, 32),
            "JUN_RF": _v(row, 33),
            "JUN_FCST": _v(row, 34),
            "JUN_ACT": _v(row, 35),
            "1H_ACT": _v(row, 38),
            "REBATE_AMT_1H": _v(row, 41),
        })

    out = pd.DataFrame(records)
    for col in ["JAN_ACT", "FEB_ACT", "MAR_ACT", "APR_ACT", "MAY_ACT",
                "JUN_RF", "JUN_FCST", "JUN_ACT", "1H_ACT", "REBATE_AMT_1H"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["PIC"] = out["PIC"].ffill()
    return out.dropna(subset=["대리점"])


@st.cache_data(show_spinner=False)
def parse_y26_plan(raw: bytes) -> dict | None:
    """Y26 Plan (2) 시트에서 분기별 사업실적 요약 파싱."""
    try:
        df = pd.read_excel(BytesIO(raw), sheet_name="Y26 Plan (2)", header=None)
    except Exception:
        return None

    PERIODS = ["1Q", "Apr", "May", "Jun", "2Q", "1H TTL", "3Q", "4Q", "2H TTL", "FY TTL"]
    # data[start:] 기준 Jan=0 상대 오프셋 (start 값과 무관하게 동일)
    # Jan=0, Feb=1, Mar=2, 1Q=3, Apr=4, May=5, Jun=6, 2Q=7, 1H TTL=8,
    # Jul=9, Aug=10, Sep=11, 3Q=12, Oct=13, Nov=14, Dec=15, 4Q=16, 2H TTL=17, FY TTL=18
    REL_IDX = {"1Q":3,"Apr":4,"May":5,"Jun":6,"2Q":7,"1H TTL":8,"3Q":12,"4Q":16,"2H TTL":17,"FY TTL":18}

    def row(i):
        return df.iloc[i].dropna().tolist()

    def extract(row_data, start):
        data = row_data[start:]
        return {p: (data[REL_IDX[p]] if REL_IDX[p] < len(data) else None) for p in PERIODS}

    try:
        return {
            "periods": PERIODS,
            "py_act_qty":    extract(row(1),  2),
            "volume": {
                "ob":       extract(row(5),  2),
                "rf":       extract(row(6),  2),
                "act":      extract(row(9),  2),
                "pct_ob":   extract(row(11), 1),
                "delta_ob": extract(row(12), 1),
                "pct_py":   extract(row(13), 1),
            },
            "amount": {
                "ob":       extract(row(16), 2),
                "rf":       extract(row(17), 2),
                "act":      extract(row(20), 2),
                "pct_ob":   extract(row(22), 1),
                "delta_ob": extract(row(23), 1),
            },
            "asp": {
                "ob":  extract(row(25), 2),
                "act": extract(row(26), 1),
            },
        }
    except Exception:
        return None


def render_y26_summary(y26: dict) -> None:
    """Y26 Plan 요약 테이블 렌더링."""
    if not y26:
        st.info("발주 파일이 없습니다. '파일 업로드'에서 오더 시트를 업로드하세요.")
        return

    PERIODS = y26["periods"]

    def _qty(v):
        try: return f"{int(round(float(v))):,}"
        except: return "—"

    def _pct(v):
        try:
            f = float(v)
            return f"{(f*100 if f <= 2 else f):.1f}%"
        except: return "—"

    def _delta(v, scale=1):
        try:
            f = float(v) / scale
            return ("+" if f >= 0 else "") + f"{int(round(f)):,}"
        except: return "—"

    def _amt(v):
        try: return f"{int(round(float(v)/1e6)):,}"
        except: return "—"

    def cells(d, fn, extra="", scale=1):
        out = ""
        for p in PERIODS:
            v = d.get(p)
            jcls = " col-jun" if p == "Jun" else ""
            ecls = (" " + extra) if (extra and p != "Jun") else ""
            if extra == "act-val" and p == "Jun":
                ecls = " act-val"
            val = fn(v) if scale == 1 else _delta(v, scale)
            out += f'<td class="{jcls}{ecls}">{val}</td>'
        return out

    NC = 2 + len(PERIODS)
    vol, amt, asp = y26["volume"], y26["amount"], y26["asp"]

    head = "".join(
        f'<th class="{"col-jun" if p=="Jun" else ""}">{p}</th>' for p in PERIODS
    )
    html = f"""
<div class="summary-wrap">
<table class="summary-table">
<thead><tr>
  <th style="text-align:left">구분</th><th style="text-align:left">항목</th>
  {head}
</tr></thead>
<tbody>
<tr class="py-row">
  <td class="row-label">25 Act</td><td class="row-type">Q'ty</td>
  {cells(y26["py_act_qty"], _qty)}
</tr>
<tr class="section-header-row"><td colspan="{NC}">Volume : pcs</td></tr>
<tr class="ob-row">
  <td class="row-label">OB</td><td class="row-type">Q'ty</td>
  {cells(vol["ob"], _qty)}
</tr>
<tr class="rf-row">
  <td class="row-label">RF</td><td class="row-type">Q'ty</td>
  {cells(vol["rf"], _qty)}
</tr>
<tr class="act-main-row">
  <td class="row-label" rowspan="4">ACT/Fcst</td><td class="row-type">Q'ty</td>
  {cells(vol["act"], _qty, "act-val")}
</tr>
<tr class="act-sub-row">
  <td class="row-type">% vs OB</td>{cells(vol["pct_ob"], _pct)}
</tr>
<tr class="act-sub-row">
  <td class="row-type">+/- vs OB</td>{cells(vol["delta_ob"], _delta)}
</tr>
<tr class="act-sub-row">
  <td class="row-type">% vs PY</td>{cells(vol["pct_py"], _pct)}
</tr>
<tr class="section-header-row"><td colspan="{NC}">Net Amount : MKkrw</td></tr>
<tr class="ob-row">
  <td class="row-label">OB</td><td class="row-type">Net AMT</td>
  {cells(amt["ob"], _amt)}
</tr>
<tr class="rf-row">
  <td class="row-label">RF</td><td class="row-type">Net AMT</td>
  {cells(amt["rf"], _amt)}
</tr>
<tr class="act-main-row">
  <td class="row-label" rowspan="3">ACT/Fcst</td><td class="row-type">Net AMT</td>
  {cells(amt["act"], _amt, "act-val")}
</tr>
<tr class="act-sub-row">
  <td class="row-type">% vs OB</td>{cells(amt["pct_ob"], _pct)}
</tr>
<tr class="act-sub-row">
  <td class="row-type">+/- vs OB</td>{"".join(f'<td class="{"col-jun" if p=="Jun" else ""}">{_delta(amt["delta_ob"].get(p), 1e6)}</td>' for p in PERIODS)}
</tr>
<tr class="section-header-row"><td colspan="{NC}">ASP</td></tr>
<tr class="asp-row">
  <td class="row-label">OB</td><td class="row-type">ASP</td>
  {cells(asp["ob"], _qty)}
</tr>
<tr class="asp-row">
  <td class="row-label">ACT/Fcst</td><td class="row-type">ASP</td>
  {cells(asp["act"], _qty)}
</tr>
</tbody>
</table>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def _get_raw(session_key: str, supabase_key: str, local_path: str) -> bytes | None:
    if session_key in st.session_state:
        return st.session_state[session_key]
    raw = _supabase_download(supabase_key)
    if raw:
        return raw
    if os.path.exists(local_path):
        with open(local_path, "rb") as f:
            return f.read()
    return None


def get_data():
    sales_raw = _get_raw("sales_raw", SALES_KEY, LOCAL_SALES)
    pcr_raw = _get_raw("pcr_raw", PCR_KEY, LOCAL_PCR)
    order_raw = _get_raw("order_raw", ORDER_KEY, LOCAL_ORDER)
    sales = parse_sales(sales_raw) if sales_raw else None
    monthly = parse_monthly(pcr_raw) if pcr_raw else None
    targets = parse_main_targets(pcr_raw) if pcr_raw else None
    y26 = parse_y26_plan(order_raw) if order_raw else None
    return sales, monthly, targets, y26

# ─────────────────────────────────────────────────────────────
# 드릴다운 패널 헬퍼
# ─────────────────────────────────────────────────────────────
def render_dealer_detail(dealer: str, sales, df_jun, targets):
    """거래처 클릭 시 상세 패널 렌더링."""
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    hc, tc = st.columns([1, 9])
    with hc:
        if st.button("✕ 닫기", key="close_dealer"):
            st.session_state.pop("sel_dealer", None)
            st.rerun()
    with tc:
        label = dealer if len(dealer) <= 28 else dealer[:28] + "…"
        st.markdown(f"### {label}")

    # KPI 수집
    pic = "—"
    fcst = act_qty = rate = None
    if targets is not None and not targets.empty:
        r_df = targets[targets["대리점"] == dealer]
        if not r_df.empty:
            r = r_df.iloc[0]
            pic = r["PIC"] if pd.notna(r.get("PIC")) else "—"
            fcst = r["JUN_FCST"] if pd.notna(r.get("JUN_FCST")) else None
            act_qty = r["JUN_ACT"] if pd.notna(r.get("JUN_ACT")) else 0
            rate = round(act_qty / fcst * 100, 1) if fcst and fcst > 0 else None

    jun_amt = jun_qty = None
    if df_jun is not None:
        d = df_jun[df_jun["거래처"] == dealer]
        if not d.empty:
            jun_amt = d["합계금액"].sum()
            jun_qty = int(d["QTY"].sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi_card("PIC", str(pic)), unsafe_allow_html=True)
    c2.markdown(kpi_card("6월 매출", f"{jun_amt/1e8:.2f}억원" if jun_amt else "—"), unsafe_allow_html=True)
    c3.markdown(kpi_card("6월 수량", f"{jun_qty:,}본" if jun_qty is not None else "—"), unsafe_allow_html=True)
    c4.markdown(kpi_card("수량 달성율", f"{rate:.1f}%" if rate is not None else "—"), unsafe_allow_html=True)

    ch1, ch2 = st.columns(2)

    with ch1:  # 월별 추이
        if targets is not None and not targets.empty:
            r_df = targets[targets["대리점"] == dealer]
            if not r_df.empty:
                r = r_df.iloc[0]
                mvals = [
                    ("1월", r.get("JAN_ACT")), ("2월", r.get("FEB_ACT")),
                    ("3월", r.get("MAR_ACT")), ("4월", r.get("APR_ACT")),
                    ("5월", r.get("MAY_ACT")), ("6월", act_qty or 0),
                ]
                mdf = pd.DataFrame(
                    [{"월": m, "수량": v} for m, v in mvals
                     if v is not None and pd.notna(v) and v >= 0]
                )
                if not mdf.empty:
                    fig_m = px.bar(
                        mdf, x="월", y="수량",
                        title="월별 판매 수량 (Jan~Jun)",
                        color_discrete_sequence=[CHART_COLORS[0]], text="수량",
                    )
                    fig_m.update_traces(texttemplate="%{text:,}", textposition="outside")
                    if fcst:
                        fig_m.add_hline(
                            y=fcst, line_dash="dash", line_color="#FFA62B",
                            annotation_text=f"Jun FCST {int(fcst):,}본",
                        )
                    st.plotly_chart(dark_layout(fig_m, height=300), use_container_width=True)

    with ch2:  # 사이즈별 판매
        done = False
        if sales is not None:
            d_s = sales[sales["대리점"] == dealer]
            if not d_s.empty and "SIZE" in d_s.columns:
                prod = (
                    d_s.groupby("SIZE")["수량"].sum()
                    .nlargest(10).reset_index().sort_values("수량")
                )
                fig_p = px.bar(
                    prod, x="수량", y="SIZE", orientation="h",
                    title="사이즈별 판매 수량 TOP 10",
                    color_discrete_sequence=[CHART_COLORS[1]], text_auto=True,
                )
                st.plotly_chart(dark_layout(fig_p, height=300), use_container_width=True)
                done = True
        if not done and df_jun is not None:
            d_j = df_jun[df_jun["거래처"] == dealer]
            if not d_j.empty and "품목분류" in d_j.columns:
                pm = d_j.groupby("품목분류")["합계금액"].sum().reset_index()
                fig_pm = px.pie(
                    pm, values="합계금액", names="품목분류",
                    title="품목분류별 매출 비중",
                    color_discrete_sequence=CHART_COLORS, hole=0.4,
                )
                fig_pm.update_traces(textfont_color="white")
                st.plotly_chart(dark_layout(fig_pm, height=300), use_container_width=True)


def render_dept_detail(dept: str, df_jun, sales, targets, df_may=None):
    """이익부서 클릭 시 상세 패널 렌더링."""
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    hc, tc = st.columns([1, 9])
    with hc:
        if st.button("✕ 닫기", key="close_dept"):
            st.session_state.pop("sel_dept", None)
            st.rerun()
    with tc:
        st.markdown(f"### {dept} 이익부서 상세")

    if df_jun is None:
        st.info("6월 매출현황 데이터가 없습니다.")
        return

    d_dept = df_jun[df_jun["이익부서"] == dept]
    if d_dept.empty:
        st.info(f"'{dept}' 데이터 없음.")
        return

    dealer_agg = (
        d_dept.groupby("거래처")
        .agg(매출=("합계금액", "sum"), 수량=("QTY", "sum"))
        .sort_values("매출", ascending=False).reset_index()
    )
    total_amt = dealer_agg["매출"].sum()
    dealer_agg["비중"] = (dealer_agg["매출"] / total_amt * 100).round(1)

    c1, c2, c3 = st.columns(3)
    c1.markdown(kpi_card("부서 총 매출", f"{total_amt/1e8:.2f}억원"), unsafe_allow_html=True)
    c2.markdown(kpi_card("거래처 수", f"{len(dealer_agg)}개"), unsafe_allow_html=True)
    c3.markdown(kpi_card("총 판매 수량", f"{int(d_dept['QTY'].sum()):,}본"), unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        fig_d = px.bar(
            dealer_agg.sort_values("매출", ascending=True),
            x="매출", y="거래처", orientation="h",
            title=f"{dept} 딜러별 매출",
            color="매출", color_continuous_scale=["#374151", "#E2231A"],
            text_auto=".2s",
        )
        fig_d.update_layout(coloraxis_showscale=False)
        st.plotly_chart(
            dark_layout(fig_d, height=max(300, len(dealer_agg) * 28)),
            use_container_width=True,
        )
    with col2:
        fig_p = px.pie(
            dealer_agg.head(10), values="비중", names="거래처",
            title=f"{dept} 딜러 구성 비중",
            color_discrete_sequence=CHART_COLORS, hole=0.4,
        )
        fig_p.update_traces(textfont_color="white")
        st.plotly_chart(dark_layout(fig_p, height=300), use_container_width=True)

    tbl = dealer_agg.copy()
    tbl["매출"] = tbl["매출"].map("{:,.0f}".format)
    tbl["수량"] = tbl["수량"].map("{:,.0f}".format)
    tbl["비중"] = tbl["비중"].map("{:.1f}%".format)
    st.dataframe(tbl, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────
# 헤더 배너 HTML 생성
# ─────────────────────────────────────────────────────────────
def _header_banner(title: str, subtitle: str) -> str:
    logo = _logo_b64()
    if logo:
        logo_html = f'<div class="header-logo-box"><img class="header-logo-img" src="data:image/png;base64,{logo}" alt="Bridgestone"></div>'
    else:
        logo_html = '<span style="font-family:\'Barlow Condensed\',\'Noto Sans KR\',sans-serif;font-weight:800;font-size:20px;color:#E2231A;letter-spacing:3px;flex-shrink:0;">BRIDGESTONE</span>'
    return f"""
    <div class="header-banner">
        {logo_html}
        <div class="header-divider"></div>
        <div class="header-text">
            <p class="header-title">{title}</p>
            <p class="header-sub">{subtitle}</p>
        </div>
    </div>
    """


# ─────────────────────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    # 로고 (사이드바 최상단 — 흰 배경 박스)
    logo4 = _logo4_b64()
    if logo4:
        st.markdown(
            f'<div class="sidebar-logo-box">'
            f'<img src="data:image/png;base64,{logo4}" alt="Bridgestone">'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<p style="font-family:\'Barlow Condensed\',sans-serif;font-weight:800;'
            'font-size:16px;color:#E2231A;letter-spacing:2px;margin:0 0 8px 0;">BRIDGESTONE</p>',
            unsafe_allow_html=True,
        )
    st.divider()
    page = st.radio("메뉴", ["대시보드", "파일 업로드"], label_visibility="collapsed")
    st.divider()
    st.caption("Supabase 연결됨" if SUPABASE else "로컬 모드")

    # 데이터 소스 상태 표시
    st.divider()
    st.caption("데이터 상태")
    for key, label, local in [
        ("sales_raw",  "영업 데이터", LOCAL_SALES),
        ("pcr_raw",    "PCR 매출",   LOCAL_PCR),
        ("order_raw",  "오더 시트",   LOCAL_ORDER),
        ("price_raw",  "가격표",      LOCAL_PRICE),
    ]:
        if key in st.session_state:
            dot, txt = "status-dot-green", "업로드 파일"
        elif os.path.exists(local):
            dot, txt = "status-dot-yellow", "기본 파일"
        else:
            dot, txt = "status-dot-yellow", "없음"
        st.markdown(
            f'<div class="status-badge"><span class="{dot}"></span> {label}: {txt}</div>',
            unsafe_allow_html=True,
        )
    st.caption("새 데이터: '파일 업로드' 메뉴 이용")

# ─────────────────────────────────────────────────────────────
# 업로드 페이지
# ─────────────────────────────────────────────────────────────
if page == "파일 업로드":
    st.markdown(
        _header_banner("파일 업로드", "Bridgestone Korea · 최신 엑셀 파일을 업로드하면 대시보드에 즉시 반영됩니다"),
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="upload-col-title">영업별 할인 현황</div>', unsafe_allow_html=True)
        # 현재 상태 표시
        if "sales_raw" in st.session_state:
            st.markdown(
                '<div class="upload-status-card">'
                '<div class="upload-status-label">현재 상태</div>'
                '<div class="upload-status-value-active">업로드된 파일 사용 중</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="upload-status-card">'
                '<div class="upload-status-label">현재 상태</div>'
                '<div class="upload-status-value-default">기본 로컬 파일 사용 중</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        st.markdown('<div class="upload-file-caption">파일명: sales data_*.xlsx · 시트: Sheet1</div>', unsafe_allow_html=True)
        up_sales = st.file_uploader("영업 데이터 선택", type=["xlsx"], key="up_sales")
        if up_sales:
            raw = up_sales.read()
            st.session_state["sales_raw"] = raw
            parse_sales.clear()
            _supabase_upload(raw, SALES_KEY)
            preview = parse_sales(raw)
            st.success(f"{len(preview):,}건 로드 완료")
            st.dataframe(preview.head(5), use_container_width=True)
            if st.button("대시보드로 이동", key="goto_dashboard_sales", type="primary"):
                st.session_state["_goto_dashboard"] = True
                st.rerun()

    with col2:
        st.markdown('<div class="upload-col-title">월별 매출현황 (PCR)</div>', unsafe_allow_html=True)
        # 현재 상태 표시
        if "pcr_raw" in st.session_state:
            st.markdown(
                '<div class="upload-status-card">'
                '<div class="upload-status-label">현재 상태</div>'
                '<div class="upload-status-value-active">업로드된 파일 사용 중</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="upload-status-card">'
                '<div class="upload-status-label">현재 상태</div>'
                '<div class="upload-status-value-default">기본 로컬 파일 사용 중</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        st.markdown('<div class="upload-file-caption">파일명: (PCR) Jun sales data_*.xlsx · 시트: Main, 6월 매출현황, 5월 매출현황</div>', unsafe_allow_html=True)
        up_pcr = st.file_uploader("PCR 데이터 선택", type=["xlsx"], key="up_pcr")
        if up_pcr:
            raw = up_pcr.read()
            st.session_state["pcr_raw"] = raw
            parse_monthly.clear()
            parse_main_targets.clear()
            _supabase_upload(raw, PCR_KEY)
            sheets = parse_monthly(raw)
            for k, df in sheets.items():
                label = "6월" if k == "jun" else "5월"
                st.success(f"{label} 매출현황: {len(df):,}건 로드 완료")
            if st.button("대시보드로 이동", key="goto_dashboard_pcr", type="primary"):
                st.session_state["_goto_dashboard"] = True
                st.rerun()

    with col3:
        st.markdown('<div class="upload-col-title">오더 시트</div>', unsafe_allow_html=True)
        if "order_raw" in st.session_state:
            st.markdown(
                '<div class="upload-status-card">'
                '<div class="upload-status-label">현재 상태</div>'
                '<div class="upload-status-value-active">업로드된 파일 사용 중</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="upload-status-card">'
                '<div class="upload-status-label">현재 상태</div>'
                '<div class="upload-status-value-default">기본 로컬 파일 사용 중</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        st.markdown('<div class="upload-file-caption">파일명: PCR - Jul26 prod order sheet_*.xlsx · 시트: Y26 Plan (2)</div>', unsafe_allow_html=True)
        up_order = st.file_uploader("오더 시트 선택", type=["xlsx"], key="up_order")
        if up_order:
            raw = up_order.read()
            st.session_state["order_raw"] = raw
            parse_y26_plan.clear()
            _supabase_upload(raw, ORDER_KEY)
            plan = parse_y26_plan(raw)
            if plan:
                st.success("Y26 Plan 요약 로드 완료")
            else:
                st.error("Y26 Plan (2) 시트를 찾을 수 없습니다.")
            if st.button("대시보드로 이동", key="goto_dashboard_order", type="primary"):
                st.session_state["_goto_dashboard"] = True
                st.rerun()

    with col4:
        st.markdown('<div class="upload-col-title">가격표 (2026)</div>', unsafe_allow_html=True)
        if "price_raw" in st.session_state:
            st.markdown(
                '<div class="upload-status-card">'
                '<div class="upload-status-label">현재 상태</div>'
                '<div class="upload-status-value-active">업로드된 파일 사용 중</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="upload-status-card">'
                '<div class="upload-status-label">현재 상태</div>'
                '<div class="upload-status-value-default">기본 로컬 파일 사용 중</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        st.markdown('<div class="upload-file-caption">파일명: 2026 브리지스톤 PCR 타이어 가격표_Final.xlsx · 시트: RE, OE, RFT</div>', unsafe_allow_html=True)
        up_price = st.file_uploader("가격표 선택", type=["xlsx"], key="up_price")
        if up_price:
            raw = up_price.read()
            st.session_state["price_raw"] = raw
            _supabase_upload(raw, PRICE_KEY)
            st.success("가격표 로드 완료")
            if st.button("대시보드로 이동", key="goto_dashboard_price", type="primary"):
                st.session_state["_goto_dashboard"] = True
                st.rerun()

# ─────────────────────────────────────────────────────────────
# 대시보드로 이동 처리 (rerun 후 page 강제 전환)
# ─────────────────────────────────────────────────────────────
if st.session_state.pop("_goto_dashboard", False):
    st.session_state["_page_override"] = "대시보드"
    st.rerun()

# ─────────────────────────────────────────────────────────────
# 대시보드 페이지
# ─────────────────────────────────────────────────────────────
elif page == "대시보드":
    # 헤더 배너
    st.markdown(
        _header_banner(
            "브리지스톤 PCR 세일즈 대시보드",
            "Bridgestone Korea · PCR Sales Performance",
        ),
        unsafe_allow_html=True,
    )

    sales, monthly, targets, y26 = get_data()

    if sales is None and not monthly and y26 is None:
        st.info("데이터가 없습니다. 사이드바 → '파일 업로드'에서 xlsx 파일을 올려주세요.")
        st.stop()

    df_jun = monthly.get("jun") if monthly else None
    df_may = monthly.get("may") if monthly else None

    # ── KPI 카드 ─────────────────────────────────────────────
    if df_jun is not None:
        jun_total = df_jun["합계금액"].sum()
        jun_qty = int(df_jun["QTY"].sum())
        avg_disc = sales["할인율(%)"].mean() if sales is not None else None

        tgt_qty = targets["JUN_FCST"].sum() if targets is not None and not targets.empty else None
        tgt_rate = (jun_qty / tgt_qty * 100) if tgt_qty and tgt_qty > 0 else None

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown(kpi_card("6월 총 매출", f"{jun_total/1e8:.2f}억원"), unsafe_allow_html=True)
        c2.markdown(kpi_card("6월 총 판매 수량", f"{jun_qty:,}본"), unsafe_allow_html=True)
        c3.markdown(kpi_card("목표 달성률(수량)", f"{tgt_rate:.1f}%" if tgt_rate else "—"), unsafe_allow_html=True)
        c4.markdown(kpi_card("거래처 수", f"{df_jun['거래처'].nunique():,}개"), unsafe_allow_html=True)
        c5.markdown(kpi_card("평균 할인율", f"{avg_disc:.1f}%" if avg_disc else "—"), unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── 탭 ───────────────────────────────────────────────────
    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["사업 실적 요약", "이익부서별 실적", "거래처 랭킹", "품목 분류", "할인율 현황", "목표 달성율"]
    )

    # ── 탭0: 사업 실적 요약 ───────────────────────────────────
    with tab0:
        st.markdown("#### 2026 Monthly Summary")
        render_y26_summary(y26)

    # ── 탭1: 이익부서 ─────────────────────────────────────────
    with tab1:
        if df_jun is not None:
            col1, col2 = st.columns(2)
            with col1:
                dept = (
                    df_jun.groupby("이익부서")["QTY"]
                    .sum().reset_index().sort_values("QTY")
                )
                fig = px.bar(
                    dept, x="QTY", y="이익부서", orientation="h",
                    title="6월 이익부서별 판매 수량",
                    color_discrete_sequence=[CHART_COLORS[0]],
                    text_auto=True,
                )
                fig.update_xaxes(title_text="수량(본)")
                evt_dept = st.plotly_chart(
                    dark_layout(fig), use_container_width=True, on_select="rerun"
                )
                if evt_dept and evt_dept.selection and evt_dept.selection.points:
                    pt = evt_dept.selection.points[0]
                    clicked = pt.get("y") or pt.get("label")
                    if clicked:
                        st.session_state["sel_dept"] = clicked
                st.caption("막대를 클릭하면 이익부서 상세 정보를 볼 수 있습니다.")

            with col2:
                if targets is not None and not targets.empty:
                    dept_map = df_jun[["거래처", "이익부서"]].drop_duplicates()
                    merged = targets.merge(dept_map, left_on="대리점", right_on="거래처", how="left")
                    if "이익부서" in merged.columns:
                        tgt_dept = merged.groupby("이익부서")["JUN_FCST"].sum().reset_index()
                        act_dept = df_jun.groupby("이익부서")["QTY"].sum().reset_index()
                        comp2 = tgt_dept.merge(act_dept, on="이익부서", how="outer").fillna(0)
                        comp2 = comp2.rename(columns={"JUN_FCST": "목표", "QTY": "실적"})
                        comp2 = comp2[comp2["목표"] > 0]
                        melt2 = comp2.melt(id_vars="이익부서", value_vars=["목표", "실적"],
                                           var_name="구분", value_name="수량")
                        fig2 = px.bar(
                            melt2, x="이익부서", y="수량", color="구분",
                            barmode="group", title="이익부서별 목표 vs 실적 (수량)",
                            color_discrete_map={"목표": "#374151", "실적": "#E2231A"},
                        )
                        fig2.update_xaxes(tickangle=-45, tickfont=dict(size=9))
                        fig2.update_layout(margin=dict(b=120))
                        fig2.update_yaxes(title_text="수량(본)")
                        st.plotly_chart(dark_layout(fig2), use_container_width=True)

        if "sel_dept" in st.session_state:
            render_dept_detail(st.session_state["sel_dept"], df_jun, sales, targets, df_may)

    # ── 탭2: 거래처 ──────────────────────────────────────────
    with tab2:
        if df_jun is not None:
            top_n = st.slider("상위 N개", 5, 30, 10, key="top_n")
            top = (
                df_jun.groupby("거래처")["QTY"]
                .sum().nlargest(top_n).reset_index().sort_values("QTY")
            )
            # PTTN별 수량 브레이크다운 (호버 말풍선용)
            _pttn_agg = (
                df_jun.groupby(["거래처", "PTTN"])["QTY"]
                .sum().reset_index()
                .sort_values(["거래처", "QTY"], ascending=[True, False])
            )
            def _pttn_lines(dealer):
                rows = _pttn_agg[_pttn_agg["거래처"] == dealer]
                return "<br>".join(f"{r['PTTN']}: {int(r['QTY']):,}본" for _, r in rows.iterrows()) or "—"
            top["pttn_detail"] = top["거래처"].apply(_pttn_lines)

            fig = px.bar(
                top, x="QTY", y="거래처", orientation="h",
                title=f"거래처 판매 수량 TOP {top_n}",
                color="QTY",
                color_continuous_scale=["#374151", "#E2231A"],
                text_auto=True,
                custom_data=["pttn_detail"],
            )
            fig.update_traces(
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "총 수량: %{x:,}본<br><br>"
                    "<b>PTTN별 수량</b><br>"
                    "%{customdata[0]}"
                    "<extra></extra>"
                )
            )
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(title_text="수량(본)")
            evt_dealer = st.plotly_chart(
                dark_layout(fig, height=max(380, top_n * 32)),
                use_container_width=True, on_select="rerun",
            )
            if evt_dealer and evt_dealer.selection and evt_dealer.selection.points:
                pt = evt_dealer.selection.points[0]
                clicked = pt.get("y") or pt.get("label")
                if clicked:
                    st.session_state["sel_dealer"] = clicked
            st.caption("막대를 클릭하면 거래처 상세 정보를 볼 수 있습니다.")

            if "sel_dealer" in st.session_state:
                render_dealer_detail(st.session_state["sel_dealer"], sales, df_jun, targets)

            tbl = (
                df_jun.groupby(["거래처", "이익부서"])
                .agg(수량=("QTY", "sum"))
                .sort_values("수량", ascending=False).reset_index()
            )
            tbl["수량"] = tbl["수량"].map("{:,.0f}".format)
            st.dataframe(tbl, use_container_width=True, hide_index=True)

    # ── 탭3: 품목 ────────────────────────────────────────────
    with tab3:
        if df_jun is not None:
            mtp = (
                df_jun.groupby("MTP분류")["QTY"]
                .sum().nlargest(10).reset_index().sort_values("QTY")
            )
            fig2 = px.bar(
                mtp, x="QTY", y="MTP분류", orientation="h",
                title="MTP분류별 판매 수량 TOP 10",
                color_discrete_sequence=[CHART_COLORS[1]],
                text_auto=True,
            )
            fig2.update_xaxes(title_text="수량(본)")
            st.plotly_chart(dark_layout(fig2), use_container_width=True)

            col3, col4 = st.columns(2)
            with col3:
                원산지 = df_jun.groupby("원산지")["QTY"].sum().reset_index()
                fig3 = px.pie(
                    원산지, values="QTY", names="원산지",
                    title="원산지별 판매 수량 비중",
                    color_discrete_sequence=CHART_COLORS,
                    hole=0.4,
                )
                fig3.update_traces(textfont_color="white")
                st.plotly_chart(dark_layout(fig3), use_container_width=True)

            with col4:
                if "SIZE" in df_jun.columns:
                    size_qty = (
                        df_jun.groupby("SIZE")["QTY"]
                        .sum().nlargest(15).reset_index().sort_values("QTY")
                    )
                    fig4 = px.bar(
                        size_qty, x="QTY", y="SIZE", orientation="h",
                        title="SIZE별 판매 수량 TOP 15",
                        color_discrete_sequence=[CHART_COLORS[2]],
                        text_auto=True,
                    )
                    fig4.update_xaxes(title_text="수량(본)")
                    st.plotly_chart(dark_layout(fig4), use_container_width=True)

            if "PTTN" in df_jun.columns:
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                pttn_qty = (
                    df_jun.groupby("PTTN")["QTY"]
                    .sum().nlargest(20).reset_index().sort_values("QTY")
                )
                fig5 = px.bar(
                    pttn_qty, x="QTY", y="PTTN", orientation="h",
                    title="패턴(PTTN)별 판매 수량 TOP 20",
                    color="QTY",
                    color_continuous_scale=["#374151", "#E2231A"],
                    text_auto=True,
                )
                fig5.update_layout(coloraxis_showscale=False)
                fig5.update_xaxes(title_text="수량(본)")
                st.plotly_chart(dark_layout(fig5, height=520), use_container_width=True)

    # ── 탭4: 할인율 ──────────────────────────────────────────
    with tab4:
        if sales is not None:
            col1, col2 = st.columns(2)
            with col1:
                dept_disc = (
                    sales.groupby("이익부서")["할인율(%)"]
                    .mean().reset_index().sort_values("할인율(%)")
                )
                dept_disc = dept_disc[dept_disc["할인율(%)"] >= 0]
                fig = px.bar(
                    dept_disc, x="할인율(%)", y="이익부서", orientation="h",
                    title="이익부서별 평균 할인율",
                    color_discrete_sequence=[CHART_COLORS[2]],
                    text_auto=".1f",
                )
                fig.update_xaxes(range=[0, None])
                st.plotly_chart(dark_layout(fig), use_container_width=True)

            with col2:
                disc_valid = sales.dropna(subset=["할인율(%)"]).copy()
                disc_valid = disc_valid[disc_valid["할인율(%)"] >= 0]
                fig2 = px.histogram(
                    disc_valid,
                    x="할인율(%)", nbins=20,
                    title="할인율 분포",
                    color_discrete_sequence=[CHART_COLORS[0]],
                )
                fig2.update_xaxes(range=[0, None])
                st.plotly_chart(dark_layout(fig2), use_container_width=True)

            tbl2 = (
                sales.groupby(["이익부서", "대리점"])
                .agg(
                    평균할인율=("할인율(%)", "mean"),
                    수량=("수량", "sum"),
                    할인전금액=("할인전 금액", "sum"),
                    할인금액=("할인 금액", "sum"),
                )
                .sort_values("평균할인율", ascending=False).reset_index()
            )
            tbl2["평균할인율"] = tbl2["평균할인율"].map("{:.1f}%".format)
            tbl2["수량"] = tbl2["수량"].map("{:,.0f}".format)
            tbl2["할인전금액"] = tbl2["할인전금액"].map("{:,.0f}".format)
            tbl2["할인금액"] = tbl2["할인금액"].map("{:,.0f}".format)
            st.dataframe(tbl2, use_container_width=True, hide_index=True)
        else:
            st.info("할인율 데이터를 보려면 'sales data' 파일을 업로드해주세요.")

    # ── 탭5: 목표 달성율 ─────────────────────────────────────
    with tab5:
        if targets is None or targets.empty:
            st.info("목표 달성율 데이터를 보려면 PCR FCST 파일을 업로드해주세요.")
        else:
            df_rate = targets[
                targets["JUN_FCST"].notna() & (targets["JUN_FCST"] > 0)
            ].copy()
            df_rate["JUN_ACT"] = df_rate["JUN_ACT"].fillna(0)
            df_rate["달성율"] = (df_rate["JUN_ACT"] / df_rate["JUN_FCST"] * 100).round(1)
            df_rate["구분"] = df_rate["달성율"].apply(
                lambda x: "달성 (≥100%)" if x >= 100
                else ("근접 (80~99%)" if x >= 80 else "미달 (<80%)")
            )
            COLOR_MAP = {
                "달성 (≥100%)": "#22c55e",
                "근접 (80~99%)": "#FFA62B",
                "미달 (<80%)": "#E2231A",
            }

            # KPI 행
            total_d = len(df_rate)
            achieved = int((df_rate["달성율"] >= 100).sum())
            near = int(((df_rate["달성율"] >= 80) & (df_rate["달성율"] < 100)).sum())
            avg_rate = df_rate["달성율"].mean()

            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(kpi_card("평균 달성율", f"{avg_rate:.1f}%"), unsafe_allow_html=True)
            c2.markdown(kpi_card("달성 거래처", f"{achieved}개"), unsafe_allow_html=True)
            c3.markdown(kpi_card("근접 거래처", f"{near}개"), unsafe_allow_html=True)
            c4.markdown(kpi_card("분석 대상", f"{total_d}개"), unsafe_allow_html=True)

            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

            # 거래처별 수량 달성율 (가로 막대)
            sorted_rate = df_rate.sort_values("달성율", ascending=True)
            fig_rate = px.bar(
                sorted_rate,
                x="달성율", y="대리점", orientation="h",
                color="구분",
                color_discrete_map=COLOR_MAP,
                title="거래처별 6월 수량 달성율 (vs Jun FCST)",
                text="달성율",
                category_orders={"구분": ["달성 (≥100%)", "근접 (80~99%)", "미달 (<80%)"]},
            )
            fig_rate.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_rate.add_vline(
                x=100, line_dash="dash", line_color="#ffffff", opacity=0.35,
                annotation_text="100%",
                annotation_position="top left",
                annotation_font_size=10,
                annotation_font_color="#9ca3af",
            )
            chart_h = max(420, len(sorted_rate) * 26)
            st.plotly_chart(dark_layout(fig_rate, height=chart_h), use_container_width=True)

            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)

            # PIC별 집계 달성율
            with col1:
                st.subheader("PIC별 6월 수량 달성율")
                pic_agg = (
                    df_rate.groupby("PIC")
                    .agg(JUN_FCST=("JUN_FCST", "sum"), JUN_ACT=("JUN_ACT", "sum"))
                    .assign(달성율=lambda x: (x["JUN_ACT"] / x["JUN_FCST"] * 100).round(1))
                    .reset_index()
                )
                pic_agg["구분"] = pic_agg["달성율"].apply(
                    lambda x: "달성 (≥100%)" if x >= 100
                    else ("근접 (80~99%)" if x >= 80 else "미달 (<80%)")
                )
                fig_pic = px.bar(
                    pic_agg, x="PIC", y="달성율",
                    color="구분",
                    color_discrete_map=COLOR_MAP,
                    text="달성율",
                    title="PIC별 6월 달성율",
                )
                fig_pic.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                fig_pic.add_hline(y=100, line_dash="dash", line_color="#ffffff", opacity=0.35)
                fig_pic.update_layout(showlegend=False)
                fig_pic.update_xaxes(tickangle=0)
                fig_pic.update_yaxes(rangemode="nonnegative")
                st.plotly_chart(dark_layout(fig_pic, height=340), use_container_width=True)

            # FCST 갭 분석 (목표 미달량 상위)
            with col2:
                st.subheader("FCST 갭 TOP 20 (미달량 기준)")
                df_gap = df_rate.copy()
                df_gap["미달량"] = (df_gap["JUN_FCST"] - df_gap["JUN_ACT"]).clip(lower=0).round(0)
                df_gap = df_gap[df_gap["미달량"] > 0].nlargest(20, "미달량").sort_values("미달량")
                if not df_gap.empty:
                    fig_gap = px.bar(
                        df_gap, x="미달량", y="대리점", orientation="h",
                        color="달성율",
                        color_continuous_scale=["#E2231A", "#FFA62B", "#22c55e"],
                        range_color=[0, 100],
                        text="미달량",
                        title="목표 미달량 상위 20 거래처",
                    )
                    fig_gap.update_traces(texttemplate="%{text:.0f}본", textposition="outside")
                    fig_gap.update_layout(coloraxis_colorbar=dict(title="달성율%"))
                    fig_gap.update_xaxes(title_text="미달량(본)")
                    st.plotly_chart(dark_layout(fig_gap, height=540), use_container_width=True)
                else:
                    st.success("목표 미달 거래처가 없습니다.")

            # 월별 수량 추이 (Jan~Jun)
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.subheader("월별 전체 판매 수량 추이 (Jan~Jun 2026)")

            MONTH_MAP = {
                "JAN_ACT": "1월", "FEB_ACT": "2월", "MAR_ACT": "3월",
                "APR_ACT": "4월", "MAY_ACT": "5월", "JUN_ACT": "6월",
            }
            monthly_total = {
                lbl: targets[col_k].sum()
                for col_k, lbl in MONTH_MAP.items()
                if targets[col_k].sum() > 0
            }
            if monthly_total:
                df_monthly = pd.DataFrame(
                    list(monthly_total.items()), columns=["월", "수량"]
                )
                fig_monthly = px.bar(
                    df_monthly, x="월", y="수량",
                    title="월별 전체 판매 수량 합계",
                    color_discrete_sequence=[CHART_COLORS[0]],
                    text_auto=True,
                )
                fig_monthly.update_yaxes(title_text="수량(본)")
                st.plotly_chart(dark_layout(fig_monthly, height=360), use_container_width=True)

            st.subheader("상위 10 거래처 월별 수량 추이")
            top10 = targets.nlargest(10, "1H_ACT")["대리점"].tolist()
            trend = targets[targets["대리점"].isin(top10)]
            rows_trend = []
            for _, r in trend.iterrows():
                for col_k, lbl in MONTH_MAP.items():
                    v = r.get(col_k)
                    if pd.notna(v) and v > 0:
                        rows_trend.append({"대리점": r["대리점"], "월": lbl, "수량": v})

            if rows_trend:
                melt_df = pd.DataFrame(rows_trend)
                fig_trend = px.line(
                    melt_df, x="월", y="수량", color="대리점",
                    title="상위 10 거래처 월별 수량 추이",
                    markers=True,
                    color_discrete_sequence=CHART_COLORS * 2,
                )
                fig_trend.update_yaxes(title_text="수량(본)")
                st.plotly_chart(dark_layout(fig_trend, height=400), use_container_width=True)
