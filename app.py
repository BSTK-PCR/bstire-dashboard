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
@st.cache_data(show_spinner=False)
def _logo_b64() -> str:
    try:
        with open("logo.png", "rb") as f:
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
.header-logo-img {
    width: 52px;
    height: 52px;
    object-fit: contain;
    flex-shrink: 0;
    filter: brightness(1.05);
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
LOCAL_SALES = "data/sales data_260627.xlsx"
LOCAL_PCR = "data/(PCR) Jun sales data_260626_FCST_V2.xlsx"


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
    sales = parse_sales(sales_raw) if sales_raw else None
    monthly = parse_monthly(pcr_raw) if pcr_raw else None
    targets = parse_main_targets(pcr_raw) if pcr_raw else None
    return sales, monthly, targets

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
        logo_html = f'<img class="header-logo-img" src="data:image/png;base64,{logo}" alt="Bridgestone">'
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
    # 로고 (사이드바 최상단)
    try:
        st.image("logo.png", width=110)
    except Exception:
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
    sales_status = "업로드 파일" if "sales_raw" in st.session_state else "기본 파일"
    pcr_status = "업로드 파일" if "pcr_raw" in st.session_state else "기본 파일"
    sales_dot = "status-dot-green" if "sales_raw" in st.session_state else "status-dot-yellow"
    pcr_dot = "status-dot-green" if "pcr_raw" in st.session_state else "status-dot-yellow"
    st.markdown(
        f'<div class="status-badge"><span class="{sales_dot}"></span> 영업 데이터: {sales_status}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="status-badge"><span class="{pcr_dot}"></span> PCR 데이터: {pcr_status}</div>',
        unsafe_allow_html=True,
    )
    if "sales_raw" not in st.session_state or "pcr_raw" not in st.session_state:
        st.caption("새 데이터를 적용하려면 '파일 업로드' 메뉴를 이용하세요.")

# ─────────────────────────────────────────────────────────────
# 업로드 페이지
# ─────────────────────────────────────────────────────────────
if page == "파일 업로드":
    st.markdown(
        _header_banner("파일 업로드", "Bridgestone Korea · 최신 엑셀 파일을 업로드하면 대시보드에 즉시 반영됩니다"),
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("영업별 할인 현황")
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
        st.caption("파일명: sales data_*.xlsx · 시트: Sheet1")
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
        st.subheader("월별 매출현황 (PCR)")
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
        st.caption("파일명: (PCR) Jun sales data_*.xlsx · 시트: Main, 6월 매출현황, 5월 매출현황")
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

    sales, monthly, targets = get_data()

    if sales is None and not monthly:
        st.info("데이터가 없습니다. 사이드바 → '파일 업로드'에서 xlsx 파일을 올려주세요.")
        st.stop()

    df_jun = monthly.get("jun") if monthly else None
    df_may = monthly.get("may") if monthly else None

    # ── KPI 카드 ─────────────────────────────────────────────
    if df_jun is not None:
        jun_total = df_jun["합계금액"].sum()
        jun_qty = int(df_jun["QTY"].sum())
        may_total = df_may["합계금액"].sum() if df_may is not None else None
        growth = ((jun_total - may_total) / may_total * 100) if may_total else None
        avg_disc = sales["할인율(%)"].mean() if sales is not None else None

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(kpi_card("6월 총 매출", f"{jun_total/1e8:.2f}억원", growth), unsafe_allow_html=True)
        c2.markdown(kpi_card("6월 총 판매 수량", f"{jun_qty:,}본"), unsafe_allow_html=True)
        c3.markdown(kpi_card("거래처 수", f"{df_jun['거래처'].nunique():,}개"), unsafe_allow_html=True)
        c4.markdown(kpi_card("평균 할인율", f"{avg_disc:.1f}%" if avg_disc else "—"), unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── 탭 ───────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["이익부서별 실적", "거래처 랭킹", "품목 분류", "할인율 현황", "목표 달성율"]
    )

    # ── 탭1: 이익부서 ─────────────────────────────────────────
    with tab1:
        if df_jun is not None:
            col1, col2 = st.columns(2)
            with col1:
                dept = (
                    df_jun.groupby("이익부서")["합계금액"]
                    .sum().reset_index().sort_values("합계금액")
                )
                fig = px.bar(
                    dept, x="합계금액", y="이익부서", orientation="h",
                    title="6월 이익부서별 매출",
                    color_discrete_sequence=[CHART_COLORS[0]],
                    text_auto=".2s",
                )
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
                if df_may is not None:
                    j = df_jun.groupby("이익부서")["합계금액"].sum().rename("6월")
                    m = df_may.groupby("이익부서")["합계금액"].sum().rename("5월")
                    comp = pd.concat([m, j], axis=1).fillna(0).reset_index()
                    melt = comp.melt(id_vars="이익부서", var_name="월", value_name="매출")
                    fig2 = px.bar(
                        melt, x="이익부서", y="매출", color="월",
                        barmode="group", title="5월 vs 6월 비교",
                        color_discrete_map={"5월": "#374151", "6월": "#E2231A"},
                    )
                    fig2.update_xaxes(tickangle=-45, tickfont=dict(size=9))
                    fig2.update_layout(margin=dict(b=120))
                    st.plotly_chart(dark_layout(fig2), use_container_width=True)

        if "sel_dept" in st.session_state:
            render_dept_detail(st.session_state["sel_dept"], df_jun, sales, targets, df_may)

    # ── 탭2: 거래처 ──────────────────────────────────────────
    with tab2:
        if df_jun is not None:
            top_n = st.slider("상위 N개", 5, 30, 10, key="top_n")
            top = (
                df_jun.groupby("거래처")["합계금액"]
                .sum().nlargest(top_n).reset_index().sort_values("합계금액")
            )
            fig = px.bar(
                top, x="합계금액", y="거래처", orientation="h",
                title=f"거래처 매출 TOP {top_n}",
                color="합계금액",
                color_continuous_scale=["#374151", "#E2231A"],
                text_auto=".2s",
            )
            fig.update_layout(coloraxis_showscale=False)
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
                .agg(매출=("합계금액", "sum"), 수량=("QTY", "sum"))
                .sort_values("매출", ascending=False).reset_index()
            )
            tbl["매출"] = tbl["매출"].map("{:,.0f}".format)
            tbl["수량"] = tbl["수량"].map("{:,.0f}".format)
            st.dataframe(tbl, use_container_width=True, hide_index=True)

    # ── 탭3: 품목 ────────────────────────────────────────────
    with tab3:
        if df_jun is not None:
            col1, col2 = st.columns(2)
            with col1:
                품목 = df_jun.groupby("품목분류")["합계금액"].sum().reset_index()
                fig = px.pie(
                    품목, values="합계금액", names="품목분류",
                    title="품목분류별 매출 비중",
                    color_discrete_sequence=CHART_COLORS,
                    hole=0.4,
                )
                fig.update_traces(textfont_color="white")
                st.plotly_chart(dark_layout(fig), use_container_width=True)

            with col2:
                mtp = (
                    df_jun.groupby("MTP분류")["합계금액"]
                    .sum().nlargest(10).reset_index().sort_values("합계금액")
                )
                fig2 = px.bar(
                    mtp, x="합계금액", y="MTP분류", orientation="h",
                    title="MTP분류별 매출 TOP 10",
                    color_discrete_sequence=[CHART_COLORS[1]],
                    text_auto=".2s",
                )
                st.plotly_chart(dark_layout(fig2), use_container_width=True)

            원산지 = df_jun.groupby("원산지")["QTY"].sum().reset_index()
            fig3 = px.pie(
                원산지, values="QTY", names="원산지",
                title="원산지별 판매 수량 비중",
                color_discrete_sequence=CHART_COLORS,
                hole=0.4,
            )
            fig3.update_traces(textfont_color="white")
            st.plotly_chart(dark_layout(fig3), use_container_width=True)

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
                x=100, line_dash="dash", line_color="#ffffff",
                opacity=0.35, annotation_text="100%"
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

            # 금액 달성율 (Rebate Target 1H / 6 기준)
            with col2:
                st.subheader("거래처별 6월 금액 달성율")
                df_amt = targets[
                    targets["REBATE_AMT_1H"].notna() & (targets["REBATE_AMT_1H"] > 0)
                ].copy()

                if df_jun is not None and not df_amt.empty:
                    jun_amt = df_jun.groupby("거래처")["합계금액"].sum().reset_index()
                    jun_amt.columns = ["대리점", "JUN_AMT_ACT"]
                    df_amt = df_amt.merge(jun_amt, on="대리점", how="left")
                    df_amt_m = df_amt[df_amt["JUN_AMT_ACT"].notna()].copy()

                    if not df_amt_m.empty:
                        df_amt_m["AMT_MON_TGT"] = df_amt_m["REBATE_AMT_1H"] / 6
                        df_amt_m["금액달성율"] = (
                            df_amt_m["JUN_AMT_ACT"] / df_amt_m["AMT_MON_TGT"] * 100
                        ).round(1)
                        df_amt_m["구분"] = df_amt_m["금액달성율"].apply(
                            lambda x: "달성 (≥100%)" if x >= 100
                            else ("근접 (80~99%)" if x >= 80 else "미달 (<80%)")
                        )
                        sorted_amt = df_amt_m.sort_values("금액달성율", ascending=True)
                        fig_amt = px.bar(
                            sorted_amt,
                            x="금액달성율", y="대리점", orientation="h",
                            color="구분",
                            color_discrete_map=COLOR_MAP,
                            text="금액달성율",
                            title="6월 금액 달성율 (리베이트 1H 목표 ÷ 6 기준)",
                        )
                        fig_amt.update_traces(
                            texttemplate="%{text:.1f}%", textposition="outside"
                        )
                        fig_amt.add_vline(
                            x=100, line_dash="dash", line_color="#ffffff", opacity=0.35
                        )
                        fig_amt.update_layout(showlegend=False)
                        st.plotly_chart(
                            dark_layout(fig_amt, height=340), use_container_width=True
                        )
                        st.caption("※ 금액 목표 = 리베이트 1H 목표 ÷ 6개월 (월별 할당 추정)")
                    else:
                        st.info("거래처명 매칭 실패. 수량 달성율을 참고해주세요.")
                else:
                    st.info("6월 매출현황 데이터 없음. 수량 달성율만 표시됩니다.")

            # 월별 수량 추이 (Jan~Jun) — 상위 10 거래처
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.subheader("상위 거래처 월별 수량 추이 (Jan~Jun 2026)")

            top10 = targets.nlargest(10, "1H_ACT")["대리점"].tolist()
            trend = targets[targets["대리점"].isin(top10)]
            MONTH_MAP = {
                "JAN_ACT": "1월", "FEB_ACT": "2월", "MAR_ACT": "3월",
                "APR_ACT": "4월", "MAY_ACT": "5월", "JUN_ACT": "6월",
            }
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
                st.plotly_chart(dark_layout(fig_trend, height=400), use_container_width=True)
