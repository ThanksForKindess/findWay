import heapq
import html as html_lib
from typing import Dict, List, Tuple

import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="학교 길찾기", page_icon="🏫", layout="centered")

# -----------------------------------------------------------------------------
# 장소 정보: x, y는 지도에서 출발/도착 표식을 표시할 '교실 문 앞' 좌표입니다.
# -----------------------------------------------------------------------------
PLACES: Dict[str, Dict[str, object]] = {
    "1층 중앙 현관": {"floor": 1, "node": "entrance", "x": 450, "y": 655},
    "교무실": {"floor": 1, "node": "staff_door", "x": 180, "y": 555},
    "과학실": {"floor": 1, "node": "science_door", "x": 120, "y": 200},
    "준비실": {"floor": 1, "node": "prep_door", "x": 285, "y": 200},
    "음악실": {"floor": 1, "node": "music_door", "x": 565, "y": 200},
    "컴퓨터실": {"floor": 1, "node": "computer_door", "x": 760, "y": 200},
    "미술실": {"floor": 1, "node": "art_door", "x": 180, "y": 305},
    "특별교실 1": {"floor": 1, "node": "special1_door", "x": 180, "y": 470},
    "도서관": {"floor": 1, "node": "library_door", "x": 650, "y": 305},
    "특별교실 2": {"floor": 1, "node": "special2_door", "x": 650, "y": 470},
    "보건실": {"floor": 1, "node": "health_door", "x": 650, "y": 555},

    "2층 중앙 계단": {"floor": 2, "node": "f2_stairs", "x": 450, "y": 620},
    "2학년 1반": {"floor": 2, "node": "class201_door", "x": 150, "y": 230},
    "2학년 2반": {"floor": 2, "node": "class202_door", "x": 350, "y": 230},
    "영어전용실": {"floor": 2, "node": "english_door", "x": 705, "y": 230},
    "상담실": {"floor": 2, "node": "counsel_door", "x": 650, "y": 500},

    "3층 중앙 계단": {"floor": 3, "node": "f3_stairs", "x": 450, "y": 620},
    "3학년 1반": {"floor": 3, "node": "class301_door", "x": 150, "y": 230},
    "3학년 2반": {"floor": 3, "node": "class302_door", "x": 350, "y": 230},
    "AI 융합실": {"floor": 3, "node": "ai_lab_door", "x": 705, "y": 230},
    "진로활동실": {"floor": 3, "node": "career_door", "x": 650, "y": 500},
}

# -----------------------------------------------------------------------------
# 실제 경로가 지나는 복도 중심선 좌표입니다.
# 모든 교실 노드는 복도에 맞닿은 문 앞에만 배치했습니다.
# -----------------------------------------------------------------------------
NODES: Dict[str, Tuple[int, int, int]] = {
    # 1층: 복도 중심선
    "entrance": (450, 655, 1),
    "south_center": (450, 555, 1),
    "south_west": (220, 555, 1),
    "south_east": (650, 555, 1),
    "west_lower": (220, 470, 1),
    "west_mid": (220, 305, 1),
    "west_top": (220, 200, 1),
    "top_center": (450, 200, 1),
    "east_top": (650, 200, 1),
    "east_mid": (650, 305, 1),
    "east_lower": (650, 470, 1),

    # 1층: 교실 문 앞
    "staff_door": (180, 555, 1),
    "science_door": (120, 200, 1),
    "prep_door": (285, 200, 1),
    "music_door": (565, 200, 1),
    "computer_door": (760, 200, 1),
    "art_door": (180, 305, 1),
    "special1_door": (180, 470, 1),
    "library_door": (650, 305, 1),
    "special2_door": (650, 470, 1),
    "health_door": (650, 555, 1),
    "stairs_1": (300, 555, 1),

    # 2층
    "f2_stairs": (450, 620, 2),
    "f2_south": (450, 500, 2),
    "f2_center": (450, 230, 2),
    "f2_west": (220, 230, 2),
    "f2_east": (650, 230, 2),
    "class201_door": (150, 230, 2),
    "class202_door": (350, 230, 2),
    "english_door": (705, 230, 2),
    "counsel_door": (650, 500, 2),

    # 3층
    "f3_stairs": (450, 620, 3),
    "f3_south": (450, 500, 3),
    "f3_center": (450, 230, 3),
    "f3_west": (220, 230, 3),
    "f3_east": (650, 230, 3),
    "class301_door": (150, 230, 3),
    "class302_door": (350, 230, 3),
    "ai_lab_door": (705, 230, 3),
    "career_door": (650, 500, 3),
}

# 복도 연결: 선분이 벽이나 교실을 관통하지 않도록 복도 중심선만 연결합니다.
EDGES: List[Tuple[str, str, float]] = [
    # 1층 메인 복도
    ("entrance", "south_center", 100),
    ("south_center", "south_west", 230),
    ("south_center", "south_east", 200),
    ("south_west", "west_lower", 85),
    ("west_lower", "west_mid", 165),
    ("west_mid", "west_top", 105),
    ("west_top", "top_center", 230),
    ("top_center", "east_top", 200),
    ("east_top", "east_mid", 105),
    ("east_mid", "east_lower", 165),
    ("east_lower", "south_east", 85),

    # 1층 교실 문 연결
    ("south_west", "staff_door", 40),
    ("west_top", "science_door", 100),
    ("west_top", "prep_door", 65),
    ("top_center", "music_door", 115),
    ("east_top", "computer_door", 110),
    ("west_mid", "art_door", 40),
    ("west_lower", "special1_door", 40),
    ("east_mid", "library_door", 1),
    ("east_lower", "special2_door", 1),
    ("south_east", "health_door", 1),
    ("south_west", "stairs_1", 80),

    # 층간 계단 및 2층 복도
    ("stairs_1", "f2_stairs", 210),
    ("f2_stairs", "f2_south", 120),
    ("f2_south", "f2_center", 270),
    ("f2_center", "f2_west", 230),
    ("f2_center", "f2_east", 200),
    ("f2_west", "class201_door", 70),
    ("f2_center", "class202_door", 100),
    ("f2_east", "english_door", 55),
    ("f2_south", "counsel_door", 200),

    # 3층
    ("f2_stairs", "f3_stairs", 210),
    ("f3_stairs", "f3_south", 120),
    ("f3_south", "f3_center", 270),
    ("f3_center", "f3_west", 230),
    ("f3_center", "f3_east", 200),
    ("f3_west", "class301_door", 70),
    ("f3_center", "class302_door", 100),
    ("f3_east", "ai_lab_door", 55),
    ("f3_south", "career_door", 200),
]


def build_graph() -> Dict[str, List[Tuple[str, float]]]:
    graph = {node: [] for node in NODES}
    for start, end, weight in EDGES:
        graph[start].append((end, weight))
        graph[end].append((start, weight))
    return graph


GRAPH = build_graph()


def shortest_path(start: str, end: str) -> Tuple[List[str], float]:
    queue: List[Tuple[float, str, List[str]]] = [(0.0, start, [])]
    visited: Dict[str, float] = {}

    while queue:
        cost, node, path = heapq.heappop(queue)
        if node in visited and visited[node] <= cost:
            continue
        visited[node] = cost
        new_path = path + [node]
        if node == end:
            return new_path, cost
        for next_node, weight in GRAPH[node]:
            heapq.heappush(queue, (cost + weight, next_node, new_path))
    return [], 0.0


def points_for_floor(path: List[str], floor: int) -> List[Tuple[int, int]]:
    points = [(NODES[node][0], NODES[node][1]) for node in path if NODES[node][2] == floor]
    deduplicated: List[Tuple[int, int]] = []
    for point in points:
        if not deduplicated or deduplicated[-1] != point:
            deduplicated.append(point)
    return deduplicated


def route_steps(path: List[str]) -> List[str]:
    if len(path) < 2:
        return ["출발지와 도착지가 같습니다"]

    steps = ["출발"]
    floors = [NODES[node][2] for node in path]
    if len(set(floors)) > 1:
        steps.append("계단 이동")

    directions: List[str] = []
    for first, second in zip(path, path[1:]):
        x1, y1, floor1 = NODES[first]
        x2, y2, floor2 = NODES[second]
        if floor1 != floor2:
            continue
        dx, dy = x2 - x1, y2 - y1
        direction = (
            ("오른쪽" if dx > 0 else "왼쪽")
            if abs(dx) >= abs(dy)
            else ("아래쪽" if dy > 0 else "위쪽")
        )
        if not directions or directions[-1] != direction:
            directions.append(direction)

    steps.extend(directions[:4])
    steps.append("도착")
    return steps


def rooms_svg(floor: int) -> str:
    if floor == 1:
        return '''
        <!-- 위쪽 교실 -->
        <rect class="room" x="35" y="45" width="170" height="135"/>
        <text class="label" x="120" y="112">과학실</text>
        <rect class="room" x="205" y="45" width="155" height="135"/>
        <text class="label" x="282" y="112">준비실</text>
        <rect class="room" x="360" y="45" width="120" height="135"/>
        <text class="label small" x="420" y="112">화장실</text>
        <rect class="room" x="480" y="45" width="175" height="135"/>
        <text class="label" x="568" y="112">음악실</text>
        <rect class="room target" x="655" y="45" width="210" height="135"/>
        <text class="label strong" x="760" y="112">컴퓨터실</text>

        <!-- 좌우 교실 -->
        <rect class="room" x="35" y="235" width="145" height="145"/>
        <text class="label" x="107" y="307">미술실</text>
        <rect class="room" x="35" y="400" width="145" height="145"/>
        <text class="label" x="107" y="472">특별교실 1</text>
        <rect class="room" x="650" y="235" width="215" height="145"/>
        <text class="label" x="757" y="307">도서관</text>
        <rect class="room" x="650" y="400" width="215" height="145"/>
        <text class="label" x="757" y="472">특별교실 2</text>

        <!-- 중앙 중정 복원 -->
        <rect class="courtyard" x="300" y="285" width="300" height="205" rx="8"/>
        <text class="courtyard-label" x="450" y="392">중정</text>

        <!-- 아래쪽 교실 및 계단 -->
        <rect class="room" x="35" y="575" width="285" height="105"/>
        <text class="label" x="177" y="627">교무실</text>
        <rect class="room" x="580" y="575" width="285" height="105"/>
        <text class="label" x="722" y="627">보건실</text>
        <rect class="stairs" x="255" y="515" width="90" height="60"/>
        <text class="stairs-label" x="300" y="552">계단</text>

        <!-- 실제 복도: 교실을 관통하지 않음 -->
        <path class="corridor" d="M120 200 H760"/>
        <path class="corridor" d="M220 200 V555"/>
        <path class="corridor" d="M650 200 V555"/>
        <path class="corridor" d="M180 555 H650"/>
        <path class="corridor" d="M450 555 V655"/>
        '''

    first = "2학년 1반" if floor == 2 else "3학년 1반"
    second = "2학년 2반" if floor == 2 else "3학년 2반"
    lab = "영어전용실" if floor == 2 else "AI 융합실"
    side = "상담실" if floor == 2 else "진로활동실"
    return f'''
        <rect class="room" x="35" y="45" width="205" height="160"/>
        <text class="label" x="137" y="125">{first}</text>
        <rect class="room" x="240" y="45" width="205" height="160"/>
        <text class="label" x="342" y="125">{second}</text>
        <rect class="room target" x="610" y="45" width="255" height="160"/>
        <text class="label strong" x="737" y="125">{lab}</text>
        <rect class="courtyard" x="300" y="300" width="300" height="180" rx="8"/>
        <text class="courtyard-label" x="450" y="395">중정</text>
        <rect class="room" x="650" y="390" width="215" height="155"/>
        <text class="label" x="757" y="468">{side}</text>
        <rect class="stairs" x="395" y="565" width="110" height="105"/>
        <text class="stairs-label" x="450" y="620">중앙 계단</text>
        <path class="corridor" d="M150 230 H705"/>
        <path class="corridor" d="M450 230 V620"/>
        <path class="corridor" d="M450 500 H650"/>
    '''


def floor_plan_html(floor: int, path: List[str], start_name: str, end_name: str) -> str:
    points = points_for_floor(path, floor)
    route_markup = ""

    if len(points) >= 2:
        path_d = "M " + " L ".join(f"{x} {y}" for x, y in points)
        route_markup = f'''
        <defs>
            <filter id="arrowShadow" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow dx="0" dy="1.5" stdDeviation="1.6"
                              flood-color="#0b4fb3" flood-opacity="0.45"/>
            </filter>
        </defs>

        <!-- 경로와 애니메이션이 동일한 path를 공유 -->
        <path id="routePath" d="{path_d}" fill="none" stroke="#1769e8"
              stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>

        <g filter="url(#arrowShadow)" class="moving-arrow">
            <polygon points="-12,-8 13,0 -12,8 -5,0" fill="#ffffff"/>
            <animateMotion dur="5.4s" begin="0s" repeatCount="indefinite" rotate="auto">
                <mpath href="#routePath" xlink:href="#routePath"/>
            </animateMotion>
        </g>
        <g filter="url(#arrowShadow)" class="moving-arrow">
            <polygon points="-12,-8 13,0 -12,8 -5,0" fill="#ffffff"/>
            <animateMotion dur="5.4s" begin="-1.8s" repeatCount="indefinite" rotate="auto">
                <mpath href="#routePath" xlink:href="#routePath"/>
            </animateMotion>
        </g>
        <g filter="url(#arrowShadow)" class="moving-arrow">
            <polygon points="-12,-8 13,0 -12,8 -5,0" fill="#ffffff"/>
            <animateMotion dur="5.4s" begin="-3.6s" repeatCount="indefinite" rotate="auto">
                <mpath href="#routePath" xlink:href="#routePath"/>
            </animateMotion>
        </g>
        '''

    markers = ""
    start = PLACES[start_name]
    end = PLACES[end_name]

    if int(start["floor"]) == floor:
        markers += (
            f'<circle cx="{start["x"]}" cy="{start["y"]}" r="17" '
            f'fill="#1769e8" stroke="#ffffff" stroke-width="7"/>'
            f'<text class="start-text" x="{start["x"]}" '
            f'y="{int(start["y"]) + 40}">출발지</text>'
        )

    if int(end["floor"]) == floor:
        markers += (
            f'<path transform="translate({int(end["x"]) - 15},{int(end["y"]) - 46})" '
            f'd="M15 0C6.7 0 0 6.7 0 15c0 11.5 15 29 15 29s15-17.5 15-29C30 6.7 23.3 0 15 0z" '
            f'fill="#ef5350" stroke="#ffffff" stroke-width="3"/>'
            f'<text class="end-text" x="{end["x"]}" '
            f'y="{int(end["y"]) - 55}">도착지</text>'
        )

    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; overflow: hidden; }}
body {{ font-family: Pretendard, "Noto Sans KR", Arial, sans-serif; background: transparent; }}
.shell {{
    overflow: hidden;
    border: 1px solid #dfe4ea;
    border-radius: 24px;
    background: #ffffff;
    box-shadow: 0 12px 35px rgba(22,34,52,.08);
}}
.toolbar {{
    height: 58px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 16px;
    border-bottom: 1px solid #edf0f3;
}}
.badge {{
    display: inline-block;
    padding: 7px 12px;
    margin-right: 8px;
    border-radius: 999px;
    background: #1769e8;
    color: white;
    font-weight: 800;
}}
.title {{ color: #172033; font-weight: 800; }}
.caption {{ color: #707987; font-size: 13px; }}
.map-area {{ height: 485px; padding: 4px 8px 8px; background: #fafbfc; overflow: hidden; }}
svg {{ display: block; width: 100%; height: 100%; margin: 0 auto; }}
.room {{ fill: #ffffff; stroke: #c7cbd1; stroke-width: 2.5; }}
.target {{ fill: #eef8ef; }}
.courtyard {{ fill: #f2f3f5; stroke: #d3d7dc; stroke-width: 2.5; }}
.corridor {{
    fill: none;
    stroke: #e2e5e9;
    stroke-width: 42;
    stroke-linecap: round;
    stroke-linejoin: round;
}}
.stairs {{ fill: #f5f6f8; stroke: #b9bec6; stroke-width: 2; }}
.label {{ fill: #172033; font-size: 24px; font-weight: 650; text-anchor: middle; dominant-baseline: middle; }}
.small {{ font-size: 18px; }}
.strong {{ font-weight: 800; }}
.courtyard-label {{ fill: #858d98; font-size: 24px; font-weight: 700; text-anchor: middle; dominant-baseline: middle; }}
.stairs-label {{ fill: #68717d; font-size: 17px; font-weight: 700; text-anchor: middle; }}
.start-text {{ fill: #1769e8; font-size: 18px; font-weight: 800; text-anchor: middle; }}
.end-text {{ fill: #ef5350; font-size: 18px; font-weight: 800; text-anchor: middle; }}
.moving-arrow {{ pointer-events: none; }}
</style>
</head>
<body>
<div class="shell">
    <div class="toolbar">
        <div><span class="badge">{floor}층</span><span class="title">실내 평면도</span></div>
        <div class="caption">{html_lib.escape(start_name)} → {html_lib.escape(end_name)}</div>
    </div>
    <div class="map-area">
        <svg viewBox="0 0 900 710" preserveAspectRatio="xMidYMid meet"
             xmlns="http://www.w3.org/2000/svg"
             xmlns:xlink="http://www.w3.org/1999/xlink">
            <rect width="900" height="710" rx="24" fill="#fafbfc"/>
            {rooms_svg(floor)}
            {route_markup}
            {markers}
        </svg>
    </div>
</div>
</body>
</html>'''


# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------
st.markdown('''
<style>
.stApp { background: radial-gradient(circle at top,#fff 0%,#f5f7fa 55%,#eef2f7 100%); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] { max-width: 920px; padding-top: 1.2rem; padding-bottom: 3rem; }
#MainMenu, footer { visibility: hidden; }
.hero { text-align: center; margin: .4rem 0 1.35rem; }
.hero h1 { margin: 0; color: #172033; font-size: clamp(2rem,7vw,3rem); letter-spacing: -.05em; }
.hero p { margin: .55rem 0 0; color: #727b88; }
.input-card { padding: .65rem .8rem .35rem; background: rgba(255,255,255,.96); border: 1px solid #d5dae1; border-radius: 22px; box-shadow: 0 12px 35px rgba(22,34,52,.08); margin-bottom: 1rem; }
.field-label { margin: 0 0 .35rem .25rem; font-weight: 800; font-size: .95rem; }
.start { color: #1769e8; }
.end { color: #ef5350; }
div[data-testid="stSelectbox"] > div > div { border-radius: 14px; min-height: 48px; }
div[data-testid="stButton"] button { min-height: 54px; border: 0; border-radius: 15px; font-size: 1.06rem; font-weight: 800; background: linear-gradient(135deg,#2476ed,#0959d5); color: white; box-shadow: 0 10px 25px rgba(23,105,232,.24); }
.summary-card { margin-top: 1rem; padding: 1.1rem 1.15rem; border: 1px solid #e0e5eb; border-radius: 22px; background: white; box-shadow: 0 12px 35px rgba(22,34,52,.08); }
.summary-top { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; margin-bottom: 1rem; }
.metric { padding: .9rem; border-radius: 15px; background: #f5f8fd; }
.metric-label { color: #7c8591; font-size: .85rem; font-weight: 700; }
.metric-value { margin-top: .2rem; color: #1769e8; font-size: 1.2rem; font-weight: 850; }
.route-steps { display: flex; align-items: center; gap: .45rem; overflow-x: auto; padding: .2rem 0 .35rem; }
.route-step { flex: 0 0 auto; padding: .52rem .75rem; border-radius: 999px; background: #eef4ff; color: #195dbf; font-weight: 780; font-size: .9rem; }
.chev { color: #b4bac2; font-size: 1.2rem; }
.notice { margin-top: .75rem; padding: .85rem 1rem; border-radius: 14px; background: #fff8e7; color: #7a5b0b; font-size: .9rem; line-height: 1.5; }
@media (max-width: 640px) {
    [data-testid="stMainBlockContainer"] { padding-left: .75rem; padding-right: .75rem; }
}
</style>
''', unsafe_allow_html=True)

for key, value in {
    "route": [],
    "route_cost": 0.0,
    "route_start": "1층 중앙 현관",
    "route_end": "컴퓨터실",
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown(
    '<div class="hero"><h1>학교 길찾기</h1>'
    '<p>출발지와 도착지를 선택하면 실내 최단 경로를 표시합니다.</p></div>',
    unsafe_allow_html=True,
)

names = list(PLACES.keys())
st.markdown('<div class="input-card">', unsafe_allow_html=True)
left, middle, right = st.columns([5, .9, 5], vertical_alignment="bottom")

with left:
    st.markdown('<div class="field-label start">● 출발지 입력</div>', unsafe_allow_html=True)
    start_name = st.selectbox(
        "출발지",
        names,
        index=names.index(st.session_state.route_start),
        label_visibility="collapsed",
        key="start_select",
    )

with middle:
    swap = st.button("⇄", help="출발지와 도착지를 바꿉니다", use_container_width=True)

with right:
    st.markdown('<div class="field-label end">● 도착지 입력</div>', unsafe_allow_html=True)
    end_name = st.selectbox(
        "도착지",
        names,
        index=names.index(st.session_state.route_end),
        label_visibility="collapsed",
        key="end_select",
    )

st.markdown('</div>', unsafe_allow_html=True)

if swap:
    st.session_state.route_start = end_name
    st.session_state.route_end = start_name
    st.session_state.route = []
    st.rerun()

if st.button("🪄 길 안내 생성", type="primary", use_container_width=True):
    route, cost = shortest_path(
        str(PLACES[start_name]["node"]),
        str(PLACES[end_name]["node"]),
    )
    st.session_state.route = route
    st.session_state.route_cost = cost
    st.session_state.route_start = start_name
    st.session_state.route_end = end_name

route = st.session_state.route
route_start = st.session_state.route_start
route_end = st.session_state.route_end

if route:
    route_floors = sorted(set(NODES[node][2] for node in route))
    default_floor = int(PLACES[route_end]["floor"])
    selected_floor = st.radio(
        "지도 층 선택",
        [1, 2, 3],
        index=[1, 2, 3].index(default_floor),
        horizontal=True,
        format_func=lambda floor: f"{floor}층",
        label_visibility="collapsed",
    )

    # 지도 자체 높이를 줄였기 때문에 iframe도 정확히 맞춰 전체가 한 번에 보입니다.
    html(
        floor_plan_html(selected_floor, route, route_start, route_end),
        height=552,
        scrolling=False,
    )

    distance_m = max(20, round(st.session_state.route_cost * .28 / 10) * 10)
    minutes = max(1, round(distance_m / 65))
    step_markup = "".join(
        (("<span class='chev'>›</span>" if index else "")
         + f"<span class='route-step'>{html_lib.escape(step)}</span>")
        for index, step in enumerate(route_steps(route))
    )

    notice = ""
    if len(route_floors) > 1:
        notice = (
            '<div class="notice">층별 버튼을 바꾸면 각 층의 이동 경로를 확인할 수 있습니다. '
            f'경로에 {", ".join(map(str, route_floors))}층이 포함됩니다.</div>'
        )

    st.markdown(
        f'''<div class="summary-card">
        <div class="summary-top">
            <div class="metric"><div class="metric-label">예상 거리</div><div class="metric-value">약 {distance_m}m</div></div>
            <div class="metric"><div class="metric-label">예상 시간</div><div class="metric-value">약 {minutes}분</div></div>
        </div>
        <div class="route-steps">{step_markup}</div>{notice}</div>''',
        unsafe_allow_html=True,
    )
else:
    html(
        floor_plan_html(1, [], st.session_state.route_start, st.session_state.route_end),
        height=552,
        scrolling=False,
    )
    st.info("출발지와 도착지를 선택한 뒤 **길 안내 생성** 버튼을 눌러주세요.")
