import os
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

# ─────────────────────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="브리지스톤 PCR 영업 대시보드",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# Supabase (선택) — 없으면 로컬 파일 or 세션 상태로 fallback
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

# 업로드할 때 로컬에 있는 파일 이름 (개발용 fallback)
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
# 파싱 함수
# ─────────────────────────────────────────────────────────────
def _to_float(val) -> float:
    """'24%' / 0.24 / None → float (백분율 기준)"""
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


# ─────────────────────────────────────────────────────────────
# 데이터 로드 우선순위: 세션 → Supabase → 로컬 파일
# ─────────────────────────────────────────────────────────────
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
    return sales, monthly


# ─────────────────────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("브리지스톤 PCR")
    page = st.radio("메뉴", ["대시보드", "파일 업로드"])
    st.divider()
    st.caption("Supabase 연결됨" if SUPABASE else "로컬 모드 (Supabase 미설정)")


# ─────────────────────────────────────────────────────────────
# 업로드 페이지
# ─────────────────────────────────────────────────────────────
if page == "파일 업로드":
    st.title("파일 업로드")
    st.caption("주마다 최신 엑셀 파일을 올려주세요. 업로드 즉시 대시보드에 반영됩니다.")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("영업별 할인 현황")
        st.caption("sales data_*.xlsx")
        up_sales = st.file_uploader("파일 선택", type=["xlsx"], key="up_sales")
        if up_sales:
            raw = up_sales.read()
            st.session_state["sales_raw"] = raw
            parse_sales.clear()
            _supabase_upload(raw, SALES_KEY)
            preview = parse_sales(raw)
            st.success(f"{len(preview):,}건 로드 완료")
            st.dataframe(preview.head(5), use_container_width=True)

    with col2:
        st.subheader("월별 매출현황 (PCR)")
        st.caption("(PCR) Jun sales data_*.xlsx")
        up_pcr = st.file_uploader("파일 선택", type=["xlsx"], key="up_pcr")
        if up_pcr:
            raw = up_pcr.read()
            st.session_state["pcr_raw"] = raw
            parse_monthly.clear()
            _supabase_upload(raw, PCR_KEY)
            sheets = parse_monthly(raw)
            for k, df in sheets.items():
                label = "6월" if k == "jun" else "5월"
                st.success(f"{label} 매출현황: {len(df):,}건 로드 완료")


# ─────────────────────────────────────────────────────────────
# 대시보드 페이지
# ─────────────────────────────────────────────────────────────
else:
    st.title("브리지스톤 PCR 영업 대시보드")

    sales, monthly = get_data()

    if sales is None and not monthly:
        st.info("데이터가 없습니다. 사이드바 → '파일 업로드'에서 xlsx 파일을 올려주세요.")
        st.stop()

    df_jun = monthly.get("jun") if monthly else None
    df_may = monthly.get("may") if monthly else None

    # ── KPI 카드 ─────────────────────────────────────────────
    if df_jun is not None:
        c1, c2, c3, c4 = st.columns(4)
        jun_total = df_jun["합계금액"].sum()
        jun_qty = int(df_jun["QTY"].sum())
        may_total = df_may["합계금액"].sum() if df_may is not None else None
        growth = ((jun_total - may_total) / may_total * 100) if may_total else None
        avg_disc = sales["할인율(%)"].mean() if sales is not None else None

        c1.metric("6월 총 매출", f"{jun_total / 1e8:.2f}억원",
                  delta=f"{growth:+.1f}%" if growth is not None else None)
        c2.metric("6월 총 판매 수량", f"{jun_qty:,}본")
        c3.metric("거래처 수", f"{df_jun['거래처'].nunique():,}개")
        c4.metric("평균 할인율", f"{avg_disc:.1f}%" if avg_disc is not None else "—")

    st.divider()

    # ── 탭 구성 ──────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(
        ["이익부서별 실적", "거래처 랭킹", "품목 분류", "할인율 현황"]
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
                    color_discrete_sequence=["#5B9BD5"],
                    text_auto=".2s",
                )
                fig.update_layout(height=400, xaxis_title="매출(원)", yaxis_title="")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                if df_may is not None:
                    j = df_jun.groupby("이익부서")["합계금액"].sum().rename("6월")
                    m = df_may.groupby("이익부서")["합계금액"].sum().rename("5월")
                    comp = pd.concat([m, j], axis=1).fillna(0).reset_index()
                    melt = comp.melt(id_vars="이익부서", var_name="월", value_name="매출")
                    fig2 = px.bar(
                        melt, x="이익부서", y="매출", color="월",
                        barmode="group", title="5월 vs 6월 비교",
                        color_discrete_map={"5월": "#A9C4E2", "6월": "#5B9BD5"},
                    )
                    fig2.update_layout(height=400, xaxis_title="", yaxis_title="매출(원)")
                    st.plotly_chart(fig2, use_container_width=True)

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
                color_discrete_sequence=["#70AD47"],
                text_auto=".2s",
            )
            fig.update_layout(height=max(350, top_n * 32), xaxis_title="매출(원)", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

            tbl = (
                df_jun.groupby(["거래처", "이익부서"])
                .agg(매출=("합계금액", "sum"), 수량=("QTY", "sum"))
                .sort_values("매출", ascending=False)
                .reset_index()
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
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                mtp = (
                    df_jun.groupby("MTP분류")["합계금액"]
                    .sum().nlargest(10).reset_index().sort_values("합계금액")
                )
                fig2 = px.bar(
                    mtp, x="합계금액", y="MTP분류", orientation="h",
                    title="MTP분류별 매출 TOP 10",
                    color_discrete_sequence=["#FFC000"],
                    text_auto=".2s",
                )
                fig2.update_layout(height=400, xaxis_title="매출(원)", yaxis_title="")
                st.plotly_chart(fig2, use_container_width=True)

            원산지 = df_jun.groupby("원산지")["QTY"].sum().reset_index()
            fig3 = px.pie(
                원산지, values="QTY", names="원산지",
                title="원산지별 판매 수량 비중",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            st.plotly_chart(fig3, use_container_width=True)

    # ── 탭4: 할인율 ──────────────────────────────────────────
    with tab4:
        if sales is not None:
            col1, col2 = st.columns(2)

            with col1:
                dept_disc = (
                    sales.groupby("이익부서")["할인율(%)"]
                    .mean().reset_index().sort_values("할인율(%)")
                )
                fig = px.bar(
                    dept_disc, x="할인율(%)", y="이익부서", orientation="h",
                    title="이익부서별 평균 할인율",
                    color_discrete_sequence=["#ED7D31"],
                    text_auto=".1f",
                )
                fig.update_layout(height=400, xaxis_title="할인율(%)", yaxis_title="")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig2 = px.histogram(
                    sales.dropna(subset=["할인율(%)"]),
                    x="할인율(%)", nbins=20,
                    title="할인율 분포",
                    color_discrete_sequence=["#ED7D31"],
                )
                fig2.update_layout(height=400, xaxis_title="할인율(%)", yaxis_title="건수")
                st.plotly_chart(fig2, use_container_width=True)

            tbl2 = (
                sales.groupby(["이익부서", "대리점"])
                .agg(
                    평균할인율=("할인율(%)", "mean"),
                    수량=("수량", "sum"),
                    할인전금액=("할인전 금액", "sum"),
                    할인금액=("할인 금액", "sum"),
                )
                .sort_values("평균할인율", ascending=False)
                .reset_index()
            )
            tbl2["평균할인율"] = tbl2["평균할인율"].map("{:.1f}%".format)
            tbl2["수량"] = tbl2["수량"].map("{:,.0f}".format)
            tbl2["할인전금액"] = tbl2["할인전금액"].map("{:,.0f}".format)
            tbl2["할인금액"] = tbl2["할인금액"].map("{:,.0f}".format)
            st.dataframe(tbl2, use_container_width=True, hide_index=True)
        else:
            st.info("할인율 데이터를 보려면 'sales data' 파일을 업로드해주세요.")
