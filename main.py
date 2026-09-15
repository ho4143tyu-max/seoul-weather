import streamlit as st
import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide",
)

st.title("🌡️ 서울의 100년 연평균 기온 변화")
st.write("1900년대 초부터 기록된 서울의 일평균 기온을 연도별로 평균하여 기온 변화를 보여줍니다.")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    df = df.dropna(subset=["날짜", "평균기온"])

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    # 연도별 평균기온 계산
    yearly = (
        df.groupby("연도", as_index=False)["평균기온"]
        .mean()
        .rename(columns={"평균기온": "연평균기온"})
    )

    return yearly


try:
    yearly = load_data()

    # 100년 구간을 보기 쉽게 표시
    end_year = yearly["연도"].max()
    start_year = end_year - 99

    chart_data = yearly[
        (yearly["연도"] >= start_year)
        & (yearly["연도"] <= end_year)
    ].copy()

    st.subheader(f"{start_year}년~{end_year}년 서울 연평균 기온")

    st.line_chart(
        chart_data.set_index("연도")["연평균기온"],
        height=500,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "가장 오래된 연도",
            f"{chart_data['연도'].min()}년",
        )

    with col2:
        st.metric(
            "가장 최근 연도",
            f"{chart_data['연도'].max()}년",
        )

    with col3:
        변화 = (
            chart_data.iloc[-1]["연평균기온"]
            - chart_data.iloc[0]["연평균기온"]
        )
        st.metric(
            "처음과 마지막의 기온 차이",
            f"{변화:+.1f}℃",
        )

    with st.expander("연도별 평균기온 데이터 보기"):
        표시용 = chart_data.copy()
        표시용["연평균기온"] = 표시용["연평균기온"].round(1)
        st.dataframe(
            표시용,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "자료 출처: 기상청 서울 관측자료(seoul.csv) | "
        "연평균 기온은 해당 연도의 일평균 기온을 평균한 값입니다."
    )

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
