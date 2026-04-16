import calendar
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="이벤트 트렌드 캘린더",
    page_icon="📅",
    layout="wide",
)

SEOUL_TZ = ZoneInfo("Asia/Seoul")

EVENT_CATEGORIES = ["경쟁사 이벤트", "기타", "미술 전시", "지자체 행사", "팝업", "브랜드 협업"]
TARGET_OPTIONS = ["2030", "가족", "외국인", "관광객", "지역고객"]

TYPE_STYLES = {
    "미술 전시": {"bg": "#F3EEFF", "text": "#6D4CDB", "dot": "#8B5CF6"},
    "팝업": {"bg": "#FFF2E8", "text": "#E67E22", "dot": "#F59E0B"},
    "경쟁사 이벤트": {"bg": "#EEF4FF", "text": "#2563EB", "dot": "#3B82F6"},
    "지자체 행사": {"bg": "#EEF9EE", "text": "#2E9B44", "dot": "#4CAF50"},
    "브랜드 협업": {"bg": "#FCEEFF", "text": "#C442C8", "dot": "#D946EF"},
    "기타": {"bg": "#F3F4F6", "text": "#6B7280", "dot": "#9CA3AF"},
}
IMPORTANCE_SCORE = {"상": 3, "중": 2, "하": 1}


def seoul_today() -> date:
    return datetime.now(SEOUL_TZ).date()


def to_date(value):
    if pd.isna(value) or value in ("", None):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def text_or_default(value, default="-"):
    if pd.isna(value) or value is None:
        return default
    value = str(value).strip()
    return value if value else default


def split_multi(value):
    if value is None or pd.isna(value):
        return []
    return [x.strip() for x in str(value).split(",") if x.strip()]


def contains_target(value, selected_targets):
    if not selected_targets:
        return True
    row_targets = split_multi(value)
    return any(t in row_targets for t in selected_targets)


def safe_score(value):
    return IMPORTANCE_SCORE.get(str(value).strip(), 2)


def infer_status(start_date, end_date, today=None):
    today = today or seoul_today()
    if start_date is None or end_date is None:
        return "예정"
    if today < start_date:
        return "예정"
    if start_date <= today <= end_date:
        return "진행중"
    return "종료"


def format_period(start_date, end_date):
    if not start_date or not end_date:
        return "-"
    return f"{start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}"


def short_period(start_date, end_date):
    if not start_date or not end_date:
        return "-"
    return f"{start_date.strftime('%m.%d')}~{end_date.strftime('%m.%d')}"


def event_matches_day(row, day):
    if row["start_date"] is None or row["end_date"] is None:
        return False
    return row["start_date"] <= day <= row["end_date"]


def get_type_style(event_type):
    return TYPE_STYLES.get(event_type, TYPE_STYLES["기타"])


def csv_template_bytes():
    template = pd.DataFrame([
        {
            "id": 1,
            "event_name": "샘플 이벤트명",
            "event_type": "팝업",
            "host_brand": "브랜드명",
            "venue_name": "장소명",
            "region": "서울",
            "start_date": "2026-04-01",
            "end_date": "2026-04-10",
            "status": "진행중",
            "source_link": "https://example.com",
            "ai_summary": "행사 요약",
            "keywords": "키워드1, 키워드2",
            "target_estimate": "2030, 가족",
            "importance": "중",
            "benchmark_value": "중",
            "lotte_idea": "활용 아이디어",
            "one_line_summary": "한 줄 요약",
            "visual_feature": "비주얼 특징",
            "experience_element": "체험 요소",
            "buzz_basis": "화제성 근거",
            "internal_similarity": "유사 사례",
            "internal_performance": "내부 성과",
            "address": "주소",
            "main_content": "주요 콘텐츠",
        }
    ])
    return template.to_csv(index=False).encode("utf-8-sig")


def load_sample_data():
    rows = [
        {"id": 1, "event_name": "빛의 조각들", "event_type": "미술 전시", "host_brand": "예술의전당", "venue_name": "예술의전당", "region": "서울", "start_date": "2026-04-03", "end_date": "2026-04-20", "status": "진행중", "source_link": "https://example.com/1", "ai_summary": "조명과 공간 연출을 결합한 전시로 포토 포인트가 강한 사례입니다.", "keywords": "미디어아트, 포토존, 공간 연출", "target_estimate": "2030, 관광객", "importance": "중", "benchmark_value": "중", "lotte_idea": "공간 연출형 시즌 전시에 응용 가능", "one_line_summary": "공간 연출형 전시, 포토 포인트 강점", "visual_feature": "조명 설치물, 미디어월", "experience_element": "포토 체험, 동선 기반 관람", "buzz_basis": "SNS 언급 증가", "internal_similarity": "2024 아트페어 연계 전시", "internal_performance": "체류시간 증가", "address": "서울 서초구 남부순환로", "main_content": "미디어아트, 포토존, 공간 연출"},
        {"id": 2, "event_name": "스누피 팝업스토어", "event_type": "팝업", "host_brand": "롯데월드몰", "venue_name": "롯데월드몰", "region": "서울", "start_date": "2026-04-04", "end_date": "2026-04-18", "status": "진행중", "source_link": "https://example.com/2", "ai_summary": "캐릭터 IP와 굿즈 판매를 중심으로 포토존까지 결합한 체험형 팝업입니다.", "keywords": "캐릭터 IP, 굿즈, 체험형 팝업", "target_estimate": "가족, 외국인, 관광객", "importance": "상", "benchmark_value": "상", "lotte_idea": "자체 캐릭터 협업 팝업 및 굿즈존 구성 검토", "one_line_summary": "캐릭터 굿즈 중심의 체험형 팝업", "visual_feature": "대형 캐릭터 조형물, 포토월", "experience_element": "굿즈 구매, 인증샷 동선", "buzz_basis": "SNS 인증 확산", "internal_similarity": "2023 캐릭터 팝업", "internal_performance": "가족 방문 비중 높음", "address": "서울 송파구 올림픽로 300 롯데월드몰", "main_content": "포토존, 굿즈, 체험존"},
        {"id": 3, "event_name": "신세계 아트페어", "event_type": "경쟁사 이벤트", "host_brand": "신세계백화점 강남", "venue_name": "신세계백화점 강남", "region": "수도권", "start_date": "2026-04-07", "end_date": "2026-04-16", "status": "진행중", "source_link": "https://example.com/3", "ai_summary": "백화점 공간에서 전시와 판매를 결합한 이벤트로 VIP 유입에 유리한 구조입니다.", "keywords": "아트페어, VIP, 경쟁사", "target_estimate": "2030, 가족", "importance": "중", "benchmark_value": "상", "lotte_idea": "문화홀 및 VIP 대상 프리뷰 프로그램 참고", "one_line_summary": "전시+판매 결합형 경쟁사 이벤트", "visual_feature": "프리미엄 부스 구성", "experience_element": "도슨트, 프라이빗 관람", "buzz_basis": "VIP 커뮤니티 반응", "internal_similarity": "2025 VIP 아트 나이트", "internal_performance": "객단가 우수", "address": "서울 서초구 신반포로", "main_content": "전시, VIP, 판매 연계"},
        {"id": 4, "event_name": "미디어아트 서울 2026", "event_type": "미술 전시", "host_brand": "DDP", "venue_name": "DDP", "region": "서울", "start_date": "2026-04-09", "end_date": "2026-04-24", "status": "진행중", "source_link": "https://example.com/4", "ai_summary": "몰입형 콘텐츠와 미디어월 중심의 전시로 2030 관람객 주목도가 높습니다.", "keywords": "미디어아트, 몰입형, 2030", "target_estimate": "2030, 외국인, 관광객", "importance": "중", "benchmark_value": "중", "lotte_idea": "브랜드 캠페인과 연계한 미디어 전시 구성 검토", "one_line_summary": "몰입형 미디어 전시", "visual_feature": "대형 LED, 몰입형 사운드", "experience_element": "인터랙티브 체험", "buzz_basis": "예매 반응 양호", "internal_similarity": "2024 미디어 파사드 행사", "internal_performance": "브랜드 인지도 상승", "address": "서울 중구 을지로", "main_content": "미디어월, 몰입형 체험, 디지털 전시"},
        {"id": 5, "event_name": "나이키 러닝 팝업", "event_type": "브랜드 협업", "host_brand": "성수 @XYZ", "venue_name": "성수 @XYZ", "region": "서울", "start_date": "2026-04-11", "end_date": "2026-04-20", "status": "진행중", "source_link": "https://example.com/5", "ai_summary": "체험형 콘텐츠와 브랜드 커뮤니티 결합이 강한 팝업으로 팬덤 확장에 유리합니다.", "keywords": "브랜드 협업, 러닝, 커뮤니티", "target_estimate": "2030, 지역고객", "importance": "중", "benchmark_value": "중", "lotte_idea": "체험형 클래스 및 커뮤니티 기반 팝업 기획 참고", "one_line_summary": "브랜드 팬덤형 체험 팝업", "visual_feature": "브랜드 컬러 중심 공간", "experience_element": "참여형 클래스", "buzz_basis": "커뮤니티 후기 다수", "internal_similarity": "2025 스포츠 브랜드 행사", "internal_performance": "참여 만족도 높음", "address": "서울 성동구 성수동", "main_content": "체험 클래스, 브랜드 팬덤, 협업"},
        {"id": 6, "event_name": "키링 체험 팝업", "event_type": "팝업", "host_brand": "더현대 서울", "venue_name": "더현대 서울", "region": "서울", "start_date": "2026-04-14", "end_date": "2026-04-22", "status": "진행중", "source_link": "https://example.com/6", "ai_summary": "제작 체험과 굿즈 소비를 결합한 소형 팝업으로 MZ 고객 반응이 좋습니다.", "keywords": "DIY, 키링, 체험형 팝업", "target_estimate": "2030, 가족, 지역고객", "importance": "중", "benchmark_value": "중", "lotte_idea": "소형 제작형 체험 팝업 포맷 테스트 가능", "one_line_summary": "제작 체험형 소형 팝업", "visual_feature": "컬러풀 굿즈 디스플레이", "experience_element": "직접 제작 체험", "buzz_basis": "SNS 후기 증가", "internal_similarity": "2024 DIY 팝업", "internal_performance": "참여율 양호", "address": "서울 영등포구 여의대로", "main_content": "DIY 체험, 굿즈, 인증샷"},
        {"id": 7, "event_name": "캐릭터 브랜드 팝업", "event_type": "팝업", "host_brand": "OOO 캐릭터 컴퍼니", "venue_name": "롯데월드몰", "region": "서울", "start_date": "2026-04-15", "end_date": "2026-04-28", "status": "진행중", "source_link": "https://example.com/7", "ai_summary": "인기 캐릭터 IP를 활용한 체험형 팝업으로 포토존과 한정 굿즈 판매가 결합된 행사입니다.", "keywords": "캐릭터 IP, 체험형 팝업, 굿즈", "target_estimate": "가족, 외국인, 관광객", "importance": "상", "benchmark_value": "상", "lotte_idea": "자체 캐릭터 IP 개발 및 팝업 운영 검토", "one_line_summary": "가족 고객 유입이 기대되는 캐릭터 체험형 팝업", "visual_feature": "캐릭터 조형물, 포토월", "experience_element": "스탬프 투어, 굿즈 판매, 인증 이벤트", "buzz_basis": "오픈 초기 대기줄 발생 및 SNS 인증 확산", "internal_similarity": "2023 캐릭터 팝업", "internal_performance": "매출 우수 / 가족 방문 비중 높음", "address": "서울 송파구 올림픽로 300 롯데월드몰 1F", "main_content": "포토존, 굿즈, 체험존"},
        {"id": 8, "event_name": "부산 원도심 축제", "event_type": "지자체 행사", "host_brand": "부산시", "venue_name": "부산 중구 일대", "region": "부산", "start_date": "2026-04-16", "end_date": "2026-04-23", "status": "진행중", "source_link": "https://example.com/8", "ai_summary": "지역 상권과 연계한 체험형 축제로 로컬 브랜딩 관점의 참고 가치가 있습니다.", "keywords": "지역 연계, 축제, 체험", "target_estimate": "가족, 관광객, 지역고객", "importance": "중", "benchmark_value": "중", "lotte_idea": "지역 협업 행사 및 상생 캠페인 구조 검토", "one_line_summary": "로컬 연계형 체험 축제", "visual_feature": "야외 무대, 지역 부스", "experience_element": "체험부스, 공연", "buzz_basis": "지역 커뮤니티 확산", "internal_similarity": "2022 지역 상생 행사", "internal_performance": "인지도 상승", "address": "부산 중구", "main_content": "지역협업, 체험부스, 공연"},
        {"id": 9, "event_name": "한국 현대미술 기획전", "event_type": "미술 전시", "host_brand": "국립현대미술관", "venue_name": "국립현대미술관", "region": "서울", "start_date": "2026-04-18", "end_date": "2026-05-06", "status": "진행중", "source_link": "https://example.com/9", "ai_summary": "큐레이션 완성도와 공간 연출 측면의 참고 가치가 높은 기획전입니다.", "keywords": "현대미술, 큐레이션, 전시", "target_estimate": "2030, 외국인, 관광객", "importance": "중", "benchmark_value": "중", "lotte_idea": "큐레이션 구조와 도슨트 포맷 참고", "one_line_summary": "큐레이션 완성도 높은 전시", "visual_feature": "미니멀 전시 공간", "experience_element": "도슨트 관람", "buzz_basis": "전시 리뷰 증가", "internal_similarity": "2024 기획전", "internal_performance": "브랜드 호감도 상승", "address": "서울 종로구", "main_content": "큐레이션, 도슨트, 전시"},
        {"id": 10, "event_name": "현대백화점 문화워크", "event_type": "경쟁사 이벤트", "host_brand": "현대백화점 판교", "venue_name": "현대백화점 판교", "region": "수도권", "start_date": "2026-04-21", "end_date": "2026-04-27", "status": "진행중", "source_link": "https://example.com/10", "ai_summary": "매장 동선과 문화 콘텐츠를 연결한 이벤트로 체류시간 확대에 유리합니다.", "keywords": "문화 프로그램, 백화점 동선, 경쟁사", "target_estimate": "2030, 가족, 지역고객", "importance": "중", "benchmark_value": "중", "lotte_idea": "매장 동선과 연계한 체험 프로그램 설계 참고", "one_line_summary": "문화 콘텐츠 연계형 경쟁사 행사", "visual_feature": "매장 라운지 활용", "experience_element": "워크숍, 도슨트형 진행", "buzz_basis": "후기 콘텐츠 증가", "internal_similarity": "2025 문화 클래스", "internal_performance": "체류시간 증가", "address": "경기 성남시", "main_content": "체험 워크숍, 문화프로그램, 동선 연계"},
        {"id": 11, "event_name": "카카오프렌즈 팝업", "event_type": "브랜드 협업", "host_brand": "코엑스몰", "venue_name": "코엑스몰", "region": "서울", "start_date": "2026-04-23", "end_date": "2026-05-02", "status": "진행중", "source_link": "https://example.com/11", "ai_summary": "캐릭터 팬덤과 오프라인 체험을 결합한 협업형 팝업으로 바이럴 요소가 강합니다.", "keywords": "캐릭터 협업, 팝업, 바이럴", "target_estimate": "2030, 가족, 외국인", "importance": "중", "benchmark_value": "상", "lotte_idea": "협업 캐릭터 팝업 및 SNS 인증 이벤트 강화", "one_line_summary": "캐릭터 협업형 바이럴 팝업", "visual_feature": "캐릭터 오브제, 컬러 공간", "experience_element": "굿즈, 포토 인증", "buzz_basis": "SNS 확산력 높음", "internal_similarity": "2024 협업 팝업", "internal_performance": "참여율 높음", "address": "서울 강남구 영동대로", "main_content": "캐릭터, 굿즈, 협업 바이럴"},
        {"id": 12, "event_name": "뷰티 브랜드 체험존", "event_type": "기타", "host_brand": "신세계백화점 대구", "venue_name": "신세계백화점 대구", "region": "대구", "start_date": "2026-04-25", "end_date": "2026-04-30", "status": "진행중", "source_link": "https://example.com/12", "ai_summary": "테스트 체험과 포토존을 결합한 뷰티 팝업으로 제품 경험을 강화한 사례입니다.", "keywords": "뷰티, 체험존, 포토존", "target_estimate": "2030, 관광객, 지역고객", "importance": "중", "benchmark_value": "중", "lotte_idea": "뷰티 카테고리 체험존 확대 검토", "one_line_summary": "제품 체험형 뷰티 팝업", "visual_feature": "브랜드 포토존", "experience_element": "테스트 체험", "buzz_basis": "뷰티 커뮤니티 언급", "internal_similarity": "2024 뷰티 위크", "internal_performance": "체험 만족도 양호", "address": "대구 동구 동부로", "main_content": "뷰티체험, 포토존, 샘플링"},
        {"id": 13, "event_name": "전주 문화주간", "event_type": "지자체 행사", "host_brand": "전주 한옥마을", "venue_name": "전주 한옥마을", "region": "기타", "start_date": "2026-04-27", "end_date": "2026-05-05", "status": "진행중", "source_link": "https://example.com/13", "ai_summary": "로컬 체험과 관광 동선을 결합한 행사로 지역 연계형 콘텐츠 참고 가치가 높습니다.", "keywords": "로컬, 지역문화, 관광", "target_estimate": "외국인, 관광객, 지역고객", "importance": "하", "benchmark_value": "중", "lotte_idea": "지역 특산/문화 연계 행사 포맷 참고", "one_line_summary": "관광 동선 연계형 지역 문화 행사", "visual_feature": "전통 공간 활용", "experience_element": "로컬 체험", "buzz_basis": "지역 여행 콘텐츠 확산", "internal_similarity": "2023 로컬 페스티벌", "internal_performance": "브랜딩 효과 양호", "address": "전북 전주시", "main_content": "지역문화, 체험, 관광"},
        {"id": 14, "event_name": "사진, 시대를 담다", "event_type": "미술 전시", "host_brand": "서울시립미술관", "venue_name": "서울시립미술관", "region": "서울", "start_date": "2026-04-29", "end_date": "2026-05-18", "status": "진행중", "source_link": "https://example.com/14", "ai_summary": "메시지 전달이 명확한 전시로 기획 의도 전달 방식이 참고할 만합니다.", "keywords": "사진전, 큐레이션, 메시지", "target_estimate": "2030, 외국인, 관광객", "importance": "중", "benchmark_value": "중", "lotte_idea": "시즌 메시지형 전시 기획 시 참고", "one_line_summary": "메시지 전달이 명확한 사진전", "visual_feature": "아카이브형 전시", "experience_element": "도슨트 및 감상형 관람", "buzz_basis": "문화 기사 노출", "internal_similarity": "2024 메시지형 기획전", "internal_performance": "브랜드 호감도 상승", "address": "서울 중구 덕수궁길", "main_content": "사진전, 감상형, 큐레이션"},
    ]
    return prepare_dataframe(pd.DataFrame(rows))


def render_upload_download():
    st.markdown("#### CSV 업로드")
    c1, c2 = st.columns(2)
    with c1:
        uploaded_file = st.file_uploader("CSV 파일", type=["csv"], label_visibility="collapsed")
    with c2:
        st.download_button(
            "Download",
            data=csv_template_bytes(),
            file_name="event_calendar_template.csv",
            mime="text/csv",
            use_container_width=True,
        )
    return uploaded_file


def render_sidebar(df):
    with st.sidebar:
        st.markdown("## 이벤트 트렌드 캘린더")
        st.caption("AI 기반 이벤트·전시·팝업 트렌드 분석")

        uploaded_file = render_upload_download()
        uploaded_df = None
        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            except Exception:
                uploaded_file.seek(0)
                uploaded_df = pd.read_csv(uploaded_file, encoding="cp949")
            st.success(f"업로드 완료: {len(uploaded_df)}건")

        st.markdown("---")
        st.markdown("### 필터")
        st.markdown("#### 이벤트 성격")

        selected_types = []
        for t in EVENT_CATEGORIES:
            checked = st.checkbox(t, value=(t != "기타"), key=f"type_{t}")
            if checked:
                selected_types.append(t)

        st.markdown("#### 타겟")
        selected_targets = []
        for t in TARGET_OPTIONS:
            checked = st.checkbox(t, value=False, key=f"target_{t}")
            if checked:
                selected_targets.append(t)

        keyword = st.text_input("검색", placeholder="행사명, 키워드")
        return selected_types, selected_targets, keyword, uploaded_df


def render_top_controls():
    selected_date = st.session_state["selected_date"]
    view_type = st.session_state["view_type"]

    c1, c2, c3, c4, c5 = st.columns([0.7, 2.2, 2.0, 1.1, 1.1])
    prev_month = (selected_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    next_month = (selected_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    with c1:
        if st.button("‹", use_container_width=True):
            st.session_state["selected_date"] = prev_month
            if (
                st.session_state["selected_day"].month != prev_month.month
                or st.session_state["selected_day"].year != prev_month.year
            ):
                st.session_state["selected_day"] = prev_month
            st.rerun()

    with c2:
        st.markdown(f'<div class="top-title">{selected_date.year}년 {selected_date.month}월</div>', unsafe_allow_html=True)

    with c3:
        current_index = ["월", "주", "리스트"].index(view_type)
        selected_view = st.radio("보기", ["월", "주", "리스트"], index=current_index, horizontal=True, label_visibility="collapsed")
        st.session_state["view_type"] = selected_view

    with c4:
        if st.button("오늘", use_container_width=True):
            today = seoul_today()
            st.session_state["selected_date"] = today.replace(day=1)
            st.session_state["selected_day"] = today
            st.rerun()

    with c5:
        if st.button("›", use_container_width=True):
            st.session_state["selected_date"] = next_month
            if (
                st.session_state["selected_day"].month != next_month.month
                or st.session_state["selected_day"].year != next_month.year
            ):
                st.session_state["selected_day"] = next_month
            st.rerun()

    picked = st.date_input("선택 날짜", value=st.session_state["selected_day"])
    st.session_state["selected_day"] = picked


def render_event_badge(row):
    style = get_type_style(row["event_type"])
    st.markdown(
        f"""
        <div class="event-card" style="background:{style['bg']};">
            <div class="event-type" style="color:{style['text']};">{row['event_type']}</div>
            <div class="event-title">{row['event_name']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_day_number(day, is_selected):
    if is_selected:
        st.markdown(
            f"""
            <div style="
                display:inline-block;
                min-width:24px;
                text-align:center;
                padding:4px 6px;
                border-radius:999px;
                background:#111827;
                color:#FFFFFF;
                font-size:10px;
                font-weight:800;
                line-height:1;
                margin-bottom:6px;
            ">
                {day.day}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        if st.button(str(day.day), key=f"day_btn_{day.isoformat()}"):
            st.session_state["selected_day"] = day
            st.rerun()


def render_month_calendar(df, selected_date):
    year = selected_date.year
    month = selected_date.month
    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(year, month)

    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
    weekday_colors = ["#111827", "#111827", "#111827", "#111827", "#111827", "#2563EB", "#DC2626"]

    header_cols = st.columns(7, gap="small")
    for i, wd in enumerate(weekday_names):
        with header_cols[i]:
            st.markdown(f'<div class="calendar-header" style="color:{weekday_colors[i]};">{wd}</div>', unsafe_allow_html=True)

    for week in weeks:
        cols = st.columns(7, gap="small")
        for i, day in enumerate(week):
            daily = df[df.apply(lambda row: event_matches_day(row, day), axis=1)].sort_values(
                ["importance_score", "benchmark_score", "sort_end"], ascending=[False, False, True]
            )
            in_month = day.month == month
            bg = "#FFFFFF" if in_month else "#F3F4F6"

            with cols[i]:
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="
                            background:{bg};
                            min-height:96px;
                            margin:-1rem;
                            padding:0.45rem;
                            border-radius:0.75rem;
                        ">
                        """,
                        unsafe_allow_html=True,
                    )
                    render_day_number(day, day == st.session_state["selected_day"])

                    if not daily.empty:
                        for _, row in daily.head(2).iterrows():
                            render_event_badge(row)
                        extra = len(daily) - 2
                        if extra > 0:
                            st.caption(f"+ {extra}건")
                    else:
                        st.markdown("<div style='height:0.15rem;'></div>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)


def render_week_view(df, selected_date):
    week_start = selected_date - timedelta(days=selected_date.weekday())
    days = [week_start + timedelta(days=i) for i in range(7)]
    cols = st.columns(7)
    for idx, day in enumerate(days):
        with cols[idx]:
            st.markdown(f"**{day.strftime('%m.%d')}**")
            if st.button("이 날짜 보기", key=f"week_{day.isoformat()}"):
                st.session_state["selected_day"] = day
                st.rerun()
            daily = df[df.apply(lambda row: event_matches_day(row, day), axis=1)]
            if daily.empty:
                st.caption("일정 없음")
            else:
                for _, row in daily.iterrows():
                    render_event_badge(row)


def render_list_view(df):
    if df.empty:
        st.info("조건에 맞는 행사가 없습니다.")
        return
    for _, row in df.iterrows():
        style = get_type_style(row["event_type"])
        st.markdown(
            f"""
            <div class="panel-card" style="margin-bottom:10px;">
                <div style="font-size:12px; font-weight:800; color:{style['text']}; margin-bottom:5px;">{row['event_type']}</div>
                <div style="font-size:18px; font-weight:800; color:#111827;">{row['event_name']}</div>
                <div style="font-size:13px; color:#6B7280; margin-top:4px;">{short_period(row['start_date'], row['end_date'])}</div>
                <div style="font-size:13px; color:#374151; margin-top:8px;">{text_or_default(row['one_line_summary'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def get_daily_events(df, selected_day):
    return df[df.apply(lambda row: event_matches_day(row, selected_day), axis=1)].sort_values(
        ["importance_score", "benchmark_score", "sort_end"], ascending=[False, False, True]
    )


def render_day_events_center(df, selected_day):
    daily = get_daily_events(df, selected_day)
    st.markdown("### 선택 날짜 일정")
    st.caption(f"{selected_day.strftime('%Y.%m.%d')} 기준")

    if daily.empty:
        st.info("선택한 날짜에 진행 중인 일정이 없습니다.")
        return

    cols = st.columns(2)
    for idx, (_, row) in enumerate(daily.iterrows()):
        with cols[idx % 2]:
            style = get_type_style(row["event_type"])
            st.markdown(
                f"""
                <div class="panel-card" style="margin-bottom:10px;">
                    <div style="display:inline-block; background:{style['bg']}; color:{style['text']};
                        padding:5px 10px; border-radius:999px; font-size:12px; font-weight:800; margin-bottom:10px;">
                        {row['event_type']}
                    </div>
                    <div style="font-size:18px; font-weight:800; color:#111827; margin-bottom:4px;">{row['event_name']}</div>
                    <div style="font-size:13px; color:#6B7280; margin-bottom:6px;">{short_period(row['start_date'], row['end_date'])}</div>
                    <div style="font-size:13px; color:#374151; line-height:1.55;">{text_or_default(row['one_line_summary'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_detail_field(label, value):
    st.markdown(f'<div class="detail-label">{label}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="detail-value">{text_or_default(value)}</div>', unsafe_allow_html=True)


def render_right_panel(filtered_df, selected_day):
    st.markdown("### 상세 이벤트")

    daily = get_daily_events(filtered_df, selected_day)
    if daily.empty:
        st.info("선택 날짜에 표시할 상세 이벤트가 없습니다.")
        return

    options = {f"[{row['event_type']}] {row['event_name']}": idx for idx, row in daily.iterrows()}
    selected_label = st.selectbox("상세 이벤트 선택", list(options.keys()), label_visibility="collapsed")
    row = daily.loc[options[selected_label]]
    style = get_type_style(row["event_type"])

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:inline-block; background:{style['bg']}; color:{style['text']};
                padding:6px 10px; border-radius:999px; font-size:12px; font-weight:800; margin-bottom:10px;">
                {row['event_type']}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f"## {row['event_name']}")
        st.write(row["venue_name"])
        st.caption(format_period(row["start_date"], row["end_date"]))
        st.caption(f"📍 {text_or_default(row['address'])}")

        st.markdown("---")
        st.markdown("#### 핵심 요약")
        st.write(text_or_default(row["ai_summary"]))

        st.markdown("---")
        st.markdown("#### 상세 정보")
        render_detail_field("이벤트 성격", row["event_type"])
        render_detail_field("타겟", row["target_estimate"])
        render_detail_field("주요 콘텐츠", row["main_content"])
        render_detail_field("주최/브랜드", row["host_brand"])


def render_bottom_cards(df, insights):
    total_count = len(df)
    exhibition_count = (df["event_type"] == "미술 전시").sum()
    popup_count = (df["event_type"] == "팝업").sum()
    municipal_count = (df["event_type"] == "지자체 행사").sum()
    competitor_count = (df["event_type"] == "경쟁사 이벤트").sum()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="mini-card">
                <div style="font-size:15px; font-weight:800; margin-bottom:16px;">이번 달 한눈에 보기</div>
                <div style="display:flex; gap:16px; align-items:end; flex-wrap:wrap;">
                    <div><div style="font-size:40px; font-weight:800;">{total_count}</div><div class="sub-muted">전체 이벤트</div></div>
                    <div><div style="font-size:24px; font-weight:800; color:#8B5CF6;">{exhibition_count}</div><div class="sub-muted">미술 전시</div></div>
                    <div><div style="font-size:24px; font-weight:800; color:#F59E0B;">{popup_count}</div><div class="sub-muted">팝업</div></div>
                    <div><div style="font-size:24px; font-weight:800; color:#4CAF50;">{municipal_count}</div><div class="sub-muted">지자체 행사</div></div>
                    <div><div style="font-size:24px; font-weight:800; color:#3B82F6;">{competitor_count}</div><div class="sub-muted">경쟁사</div></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        lines = "".join([f"<li style='margin-bottom:8px;'>{line}</li>" for line in insights["summary_lines"]])
        st.markdown(
            f"""
            <div class="mini-card">
                <div style="font-size:15px; font-weight:800; margin-bottom:16px;">AI 트렌드 요약</div>
                <ul style="padding-left:18px; margin:0; color:#374151; font-size:14px;">
                    {lines}
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        pills = "".join([f"<span class='pill'># {kw}</span>" for kw in insights["keywords"]])
        st.markdown(
            f"""
            <div class="mini-card">
                <div style="font-size:15px; font-weight:800; margin-bottom:16px;">주목할 키워드</div>
                <div>{pills}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main():
    inject_css()

    today = seoul_today()
    if "selected_date" not in st.session_state:
        st.session_state["selected_date"] = today.replace(day=1)
    if "view_type" not in st.session_state:
        st.session_state["view_type"] = "월"
    if "selected_day" not in st.session_state:
        st.session_state["selected_day"] = today

    df = load_sample_data()
    selected_types, selected_targets, keyword, uploaded_df = render_sidebar(df)

    if uploaded_df is not None:
        try:
            df = prepare_dataframe(uploaded_df)
        except Exception as e:
            st.error(f"업로드한 CSV 처리 중 오류가 발생했습니다: {e}")
            st.stop()

    filtered = filter_dataframe(
        df=df,
        view_type=st.session_state["view_type"],
        selected_date=st.session_state["selected_date"],
        selected_types=selected_types,
        selected_targets=selected_targets,
        keyword=keyword,
    )
    insights = build_insights(filtered, st.session_state["selected_date"])

    main_col, right_col = st.columns([5.2, 1.8], gap="large")

    with main_col:
        render_top_controls()
        if st.session_state["view_type"] == "월":
            render_month_calendar(filtered, st.session_state["selected_date"])
        elif st.session_state["view_type"] == "주":
            render_week_view(filtered, st.session_state["selected_date"])
        else:
            render_list_view(filtered)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        render_day_events_center(filtered, st.session_state["selected_day"])

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        render_bottom_cards(filtered, insights)

    with right_col:
        render_right_panel(filtered, st.session_state["selected_day"])


if __name__ == "__main__":
    main()
