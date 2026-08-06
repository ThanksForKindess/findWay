import heapq
import html as html_lib
from typing import Dict, List, Tuple

import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="학교 길찾기", page_icon="🏫", layout="centered")

PLACES: Dict[str, Dict[str, object]] = {
    "1층 중앙 현관": {"floor": 1, "node": "entrance", "x": 450, "y": 650},
    "교무실": {"floor": 1, "node": "staff", "x": 130, "y": 610},
    "과학실": {"floor": 1, "node": "science", "x": 130, "y": 105},
    "준비실": {"floor": 1, "node": "prep", "x": 285, "y": 105},
    "음악실": {"floor": 1, "node": "music", "x": 560, "y": 105},
    "컴퓨터실": {"floor": 1, "node": "computer", "x": 770, "y": 120},
    "미술실": {"floor": 1, "node": "art", "x": 110, "y": 290},
    "특별교실 1": {"floor": 1, "node": "special1", "x": 110, "y": 455},
    "도서관": {"floor": 1, "node": "library", "x": 705, "y": 300},
    "특별교실 2": {"floor": 1, "node": "special2", "x": 705, "y": 470},
    "보건실": {"floor": 1, "node": "health", "x": 735, "y": 610},
    "2층 중앙 계단": {"floor": 2, "node": "f2_center", "x": 450, "y": 635},
    "2학년 1반": {"floor": 2, "node": "class201", "x": 145, "y": 125},
    "2학년 2반": {"floor": 2, "node": "class202", "x": 350, "y": 125},
    "영어전용실": {"floor": 2, "node": "english", "x": 735, "y": 125},
    "상담실": {"floor": 2, "node": "counsel", "x": 735, "y": 500},
    "3층 중앙 계단": {"floor": 3, "node": "f3_center", "x": 450, "y": 635},
    "3학년 1반": {"floor": 3, "node": "class301", "x": 145, "y": 125},
    "3학년 2반": {"floor": 3, "node": "class302", "x": 350, "y": 125},
    "AI 융합실": {"floor": 3, "node": "ai_lab", "x": 735, "y": 125},
    "진로활동실": {"floor": 3, "node": "career", "x": 735, "y": 500},
}

NODES: Dict[str, Tuple[int, int, int]] = {
    "entrance": (450, 625, 1), "south": (450, 545, 1),
    "center": (450, 365, 1), "north": (450, 185, 1),
    "west_s": (275, 545, 1), "west_c": (275, 365, 1), "west_n": (275, 185, 1),
    "east_s": (635, 545, 1), "east_c": (635, 365, 1), "east_n": (635, 185, 1),
    "computer_turn": (710, 185, 1),
    "staff": (130, 545, 1), "science": (130, 185, 1), "prep": (285, 185, 1),
    "music": (560, 185, 1), "computer": (770, 150, 1), "art": (130, 365, 1),
    "special1": (130, 470, 1), "library": (705, 365, 1),
    "special2": (705, 470, 1), "health": (735, 545, 1),
    "stairs": (275, 545, 1),
    "f2_center": (450, 625, 2), "f2_hall": (450, 300, 2),
    "class201": (145, 300, 2), "class202": (350, 300, 2),
    "english": (735, 300, 2), "counsel": (735, 500, 2),
    "f3_center": (450, 625, 3), "f3_hall": (450, 300, 3),
    "class301": (145, 300, 3), "class302": (350, 300, 3),
    "ai_lab": (735, 300, 3), "career": (735, 500, 3),
}

EDGES = [
    ("entrance", "south", 80), ("south", "center", 180), ("center", "north", 180),
    ("south", "west_s", 175), ("center", "west_c", 175), ("north", "west_n", 175),
    ("west_s", "west_c", 180), ("west_c", "west_n", 180),
    ("south", "east_s", 185), ("center", "east_c", 185), ("north", "east_n", 185),
    ("east_s", "east_c", 180), ("east_c", "east_n", 180),
    ("west_s", "staff", 145), ("west_c", "art", 145), ("west_c", "special1", 175),
    ("west_n", "science", 145), ("west_n", "prep", 20),
    ("east_n", "music", 75), ("east_n", "computer_turn", 75),
    ("computer_turn", "computer", 70), ("east_c", "library", 70),
    ("east_c", "special2", 125), ("east_s", "health", 100),
    ("west_s", "stairs", 1), ("stairs", "f2_center", 210),
    ("f2_center", "f2_hall", 325), ("f2_hall", "class201", 305),
    ("f2_hall", "class202", 100), ("f2_hall", "english", 285),
    ("f2_hall", "counsel", 330), ("f2_center", "f3_center", 210),
    ("f3_center", "f3_hall", 325), ("f3_hall", "class301", 305),
    ("f3_hall", "class302", 100), ("f3_hall", "ai_lab", 285),
    ("f3_hall", "career", 330),
]


def build_graph():
    graph = {node: [] for node in NODES}
    for a, b, weight in EDGES:
        graph[a].append((b, weight))
        graph[b].append((a, weight))
    return graph


GRAPH = build_graph()


def shortest_path(start: str, end: str):
    queue = [(0.0, start, [])]
    visited = {}
    while queue:
        cost, node, path = heapq.heappop(queue)
        if node in visited and visited[node] <= cost:
            continue
        visited[node] = cost
        new_path = path + [node]
        if node == end:
            return new_path, cost
        for nxt, weight in GRAPH[node]:
            heapq.heappush(queue, (cost + weight, nxt, new_path))
    return [], 0.0


def points_for_floor(path: List[str], floor: int):
    points = [(NODES[n][0], NODES[n][1]) for n in path if NODES[n][2] == floor]
    result = []
    for p in points:
        if not result or result[-1] != p:
            result.append(p)
    return result


def route_steps(path: List[str]):
    if len(path) < 2:
        return ["출발지와 도착지가 같습니다"]
    steps = ["출발"]
    floors = [NODES[n][2] for n in path]
    if len(set(floors)) > 1:
        steps.append("계단 이동")
    directions = []
    for a, b in zip(path, path[1:]):
        x1, y1, f1 = NODES[a]
        x2, y2, f2 = NODES[b]
        if f1 != f2:
            continue
        dx, dy = x2 - x1, y2 - y1
        direction = ("오른쪽" if dx > 0 else "왼쪽") if abs(dx) >= abs(dy) else ("아래쪽" if dy > 0 else "직진")
        if not directions or directions[-1] != direction:
            directions.append(direction)
    steps.extend(directions[:3])
    steps.append("도착")
    return steps


def rooms_svg(floor: int):
    if floor == 1:
        return '''
        <rect class="room" x="35" y="45" width="170" height="135"/><text class="label" x="120" y="112">과학실</text>
        <rect class="room" x="205" y="45" width="155" height="135"/><text class="label" x="282" y="112">준비실</text>
        <rect class="room" x="360" y="45" width="120" height="135"/><text class="label small" x="420" y="112">화장실</text>
        <rect class="room" x="480" y="45" width="175" height="135"/><text class="label" x="568" y="112">음악실</text>
        <rect class="room target" x="655" y="45" width="210" height="155"/><text class="label strong" x="760" y="125">컴퓨터실</text>
        <rect class="room" x="35" y="225" width="145" height="165"/><text class="label" x="107" y="310">미술실</text>
        <rect class="room" x="35" y="390" width="145" height="170"/><text class="label" x="107" y="470">특별교실 1</text>
        <rect class="room courtyard" x="315" y="270" width="230" height="215"/><text class="label muted" x="430" y="385">중정</text>
        <rect class="room" x="625" y="225" width="240" height="165"/><text class="label" x="745" y="310">도서관</text>
        <rect class="room" x="625" y="390" width="240" height="170"/><text class="label" x="745" y="470">특별교실 2</text>
        <rect class="room" x="35" y="560" width="285" height="120"/><text class="label" x="178" y="630">교무실</text>
        <rect class="room" x="580" y="560" width="285" height="120"/><text class="label" x="722" y="630">보건실</text>
        <rect class="stairs" x="210" y="500" width="85" height="60"/><text class="stairs-label" x="252" y="537">계단</text>
        <path class="corridor" d="M180 200H710V560H180V200"/><path class="corridor" d="M450 180V680"/>
        '''
    room_a = "2학년 1반" if floor == 2 else "3학년 1반"
    room_b = "2학년 2반" if floor == 2 else "3학년 2반"
    lab = "영어전용실" if floor == 2 else "AI 융합실"
    side = "상담실" if floor == 2 else "진로활동실"
    return f'''
    <rect class="room" x="35" y="45" width="205" height="170"/><text class="label" x="137" y="132">{room_a}</text>
    <rect class="room" x="240" y="45" width="205" height="170"/><text class="label" x="342" y="132">{room_b}</text>
    <rect class="room target" x="610" y="45" width="255" height="170"/><text class="label strong" x="737" y="132">{lab}</text>
    <rect class="room courtyard" x="300" y="275" width="300" height="210"/><text class="label muted" x="450" y="385">중정</text>
    <rect class="room" x="610" y="410" width="255" height="190"/><text class="label" x="737" y="510">{side}</text>
    <rect class="stairs" x="395" y="560" width="110" height="120"/><text class="stairs-label" x="450" y="625">중앙 계단</text>
    <path class="corridor" d="M110 300H790"/><path class="corridor" d="M450 215V680"/>
    '''


def overlay_svg(floor: int):
    if floor == 1:
        return '<text class="stairs-label overlay-text" x="252" y="537">계단</text>'
    return '<text class="stairs-label overlay-text" x="450" y="625">중앙 계단</text>'


def floor_plan_html(floor: int, path: List[str], start_name: str, end_name: str):
    points = points_for_floor(path, floor)
    polyline = " ".join(f"{x},{y}" for x, y in points)
    route = ""
    if len(points) >= 2:
        route = f'<polyline points="{polyline}" fill="none" stroke="#1769e8" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>'

    markers = ""
    start, end = PLACES[start_name], PLACES[end_name]
    if start["floor"] == floor:
        markers += (
            f'<circle cx="{start["x"]}" cy="{start["y"]}" r="18" fill="#1769e8" '
            f'stroke="white" stroke-width="7"/>'
            f'<text class="start-text" x="{start["x"]}" y="{int(start["y"]) + 43}">출발지</text>'
        )
    if end["floor"] == floor:
        markers += (
            f'<path transform="translate({int(end["x"]) - 15},{int(end["y"]) - 45})" '
            f'd="M15 0C6.7 0 0 6.7 0 15c0 11.5 15 29 15 29s15-17.5 15-29C30 6.7 23.3 0 15 0z" '
            f'fill="#ef5350" stroke="white" stroke-width="3"/>'
            f'<text class="end-text" x="{end["x"]}" y="{int(end["y"]) - 55}">도착지</text>'
        )

    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
    *{{box-sizing:border-box}} body{{margin:0;font-family:Pretendard,"Noto Sans KR",Arial,sans-serif;background:transparent}}
    .shell{{overflow:hidden;border:1px solid #dfe4ea;border-radius:24px;background:white;box-shadow:0 12px 35px rgba(22,34,52,.08)}}
    .toolbar{{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:1px solid #edf0f3}}
    .badge{{display:inline-block;padding:7px 12px;margin-right:8px;border-radius:999px;background:#1769e8;color:white;font-weight:800}}
    .title{{color:#172033;font-weight:800}} .caption{{color:#707987;font-size:13px}}
    .scroll{{overflow:hidden;background:#fafbfc}} svg{{display:block;width:100%;height:auto}}
    .room{{fill:#fff;stroke:#c7cbd1;stroke-width:2.5}} .target{{fill:#eef8ef}} .courtyard{{fill:#f5f6f8}}
    .stairs{{fill:#f5f6f8;stroke:#b9bec6;stroke-width:2}} .corridor{{fill:none;stroke:#e2e5e9;stroke-width:48;stroke-linecap:round;stroke-linejoin:round}}
    .label{{fill:#172033;font-size:25px;font-weight:650;text-anchor:middle;dominant-baseline:middle}} .small{{font-size:18px}} .strong{{font-weight:800}} .muted{{fill:#89919c}}
    .stairs-label{{fill:#68717d;font-size:18px;font-weight:700;text-anchor:middle}}
    .overlay-text{{paint-order:stroke;stroke:#fafbfc;stroke-width:8;stroke-linejoin:round}}
    .start-text{{fill:#1769e8;font-size:19px;font-weight:800;text-anchor:middle}} .end-text{{fill:#ef5350;font-size:19px;font-weight:800;text-anchor:middle}}
    </style></head><body><div class="shell"><div class="toolbar"><div><span class="badge">{floor}층</span><span class="title">실내 평면도</span></div><div class="caption">{html_lib.escape(start_name)} → {html_lib.escape(end_name)}</div></div><div class="scroll"><svg viewBox="0 0 900 720" preserveAspectRatio="xMidYMid meet"><rect width="900" height="720" rx="24" fill="#fafbfc"/>{rooms_svg(floor)}{route}{markers}{overlay_svg(floor)}</svg></div></div></body></html>'''

st.markdown('''<style>
.stApp{background:radial-gradient(circle at top,#fff 0%,#f5f7fa 55%,#eef2f7 100%)}
[data-testid="stHeader"]{background:transparent}[data-testid="stMainBlockContainer"]{max-width:920px;padding-top:1.2rem;padding-bottom:3rem}#MainMenu,footer{visibility:hidden}
.hero{text-align:center;margin:.4rem 0 1.35rem}.hero h1{margin:0;color:#172033;font-size:clamp(2rem,7vw,3rem);letter-spacing:-.05em}.hero p{margin:.55rem 0 0;color:#727b88}
.input-card{padding:.65rem .8rem .35rem;background:rgba(255,255,255,.96);border:1px solid #d5dae1;border-radius:22px;box-shadow:0 12px 35px rgba(22,34,52,.08);margin-bottom:1rem}
.field-label{margin:0 0 .35rem .25rem;font-weight:800;font-size:.95rem}.start{color:#1769e8}.end{color:#ef5350}
div[data-testid="stSelectbox"]>div>div{border-radius:14px;min-height:48px}div[data-testid="stButton"] button{min-height:54px;border:0;border-radius:15px;font-size:1.06rem;font-weight:800;background:linear-gradient(135deg,#2476ed,#0959d5);color:white;box-shadow:0 10px 25px rgba(23,105,232,.24)}
.summary-card{margin-top:1rem;padding:1.1rem 1.15rem;border:1px solid #e0e5eb;border-radius:22px;background:white;box-shadow:0 12px 35px rgba(22,34,52,.08)}
.summary-top{display:grid;grid-template-columns:1fr 1fr;gap:.8rem;margin-bottom:1rem}.metric{padding:.9rem;border-radius:15px;background:#f5f8fd}.metric-label{color:#7c8591;font-size:.85rem;font-weight:700}.metric-value{margin-top:.2rem;color:#1769e8;font-size:1.2rem;font-weight:850}
.route-steps{display:flex;align-items:center;gap:.45rem;overflow-x:auto;padding:.2rem 0 .35rem}.route-step{flex:0 0 auto;padding:.52rem .75rem;border-radius:999px;background:#eef4ff;color:#195dbf;font-weight:780;font-size:.9rem}.chev{color:#b4bac2;font-size:1.2rem}.notice{margin-top:.75rem;padding:.85rem 1rem;border-radius:14px;background:#fff8e7;color:#7a5b0b;font-size:.9rem;line-height:1.5}

/* 층 선택: 원형 버튼 + 아래 층 이름 */
.floor-selector-title {
    margin: 0.4rem 0 0.45rem;
    color: #667085;
    font-size: 0.88rem;
    font-weight: 800;
}
div[data-testid="stHorizontalBlock"].floor-selector-row {
    gap: 0.8rem;
}
.floor-name {
    margin-top: -0.15rem;
    text-align: center;
    color: #364152;
    font-size: 0.9rem;
    font-weight: 800;
}
/* 층 버튼 전용: 짧고 둥근 버튼 */
div[data-testid="stButton"] button[kind="secondary"] {
    width: 54px;
    min-height: 54px;
    height: 54px;
    padding: 0;
    border-radius: 999px;
    border: 2px solid #d9e0ea;
    background: #ffffff;
    color: #667085;
    box-shadow: none;
    font-size: 0;
}
div[data-testid="stButton"] button[kind="secondary"]::before {
    content: "";
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: currentColor;
    display: block;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: #1769e8;
    color: #1769e8;
    transform: none;
}
.floor-active-note {
    margin: 0.2rem 0 0.8rem;
    color: #1769e8;
    font-size: 0.88rem;
    font-weight: 800;
}
@media(max-width:640px){[data-testid="stMainBlockContainer"]{padding-left:.75rem;padding-right:.75rem}}
</style>''', unsafe_allow_html=True)

for key, value in {"route": [], "route_cost": 0.0, "route_start": "1층 중앙 현관", "route_end": "컴퓨터실", "selected_floor": 1}.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown('<div class="hero"><h1>학교 길찾기</h1><p>출발지와 도착지를 선택하면 실내 최단 경로를 표시합니다.</p></div>', unsafe_allow_html=True)

names = list(PLACES.keys())
st.markdown('<div class="input-card">', unsafe_allow_html=True)
left, middle, right = st.columns([5, .9, 5], vertical_alignment="bottom")
with left:
    st.markdown('<div class="field-label start">● 출발지 입력</div>', unsafe_allow_html=True)
    start_name = st.selectbox("출발지", names, index=names.index(st.session_state.route_start), label_visibility="collapsed", key="start_select")
with middle:
    swap = st.button("⇄", help="출발지와 도착지를 바꿉니다", use_container_width=True)
with right:
    st.markdown('<div class="field-label end">● 도착지 입력</div>', unsafe_allow_html=True)
    end_name = st.selectbox("도착지", names, index=names.index(st.session_state.route_end), label_visibility="collapsed", key="end_select")
st.markdown('</div>', unsafe_allow_html=True)

if swap:
    st.session_state.route_start = end_name
    st.session_state.route_end = start_name
    st.session_state.route = []
    st.session_state.selected_floor = int(PLACES[end_name]["floor"])
    st.rerun()

if st.button("🪄 길 안내 생성", type="primary", use_container_width=True):
    route, cost = shortest_path(str(PLACES[start_name]["node"]), str(PLACES[end_name]["node"]))
    st.session_state.route = route
    st.session_state.route_cost = cost
    st.session_state.route_start = start_name
    st.session_state.route_end = end_name
    # 길 안내를 새로 만들면 출발지가 있는 층을 먼저 보여줍니다.
    st.session_state.selected_floor = int(PLACES[start_name]["floor"])
    st.rerun()

route = st.session_state.route
route_start = st.session_state.route_start
route_end = st.session_state.route_end

if route:
    route_floors = sorted(set(NODES[n][2] for n in route))
    start_floor = int(PLACES[route_start]["floor"])

    # 경로 생성 직후에는 항상 출발지가 있는 층을 먼저 표시합니다.
    if st.session_state.selected_floor not in [1, 2, 3]:
        st.session_state.selected_floor = start_floor

    st.markdown('<div class="floor-selector-title">층별 지도</div>', unsafe_allow_html=True)
    floor_columns = st.columns([1, 1, 1, 7])
    for index, floor in enumerate([1, 2, 3]):
        with floor_columns[index]:
            is_active = st.session_state.selected_floor == floor
            if st.button(
                "선택",
                key=f"floor_button_{floor}",
                help=f"{floor}층 지도 보기",
                type="primary" if is_active else "secondary",
                use_container_width=False,
            ):
                st.session_state.selected_floor = floor
                st.rerun()
            st.markdown(f'<div class="floor-name">{floor}층</div>', unsafe_allow_html=True)

    selected_floor = int(st.session_state.selected_floor)
    st.markdown(
        f'<div class="floor-active-note">현재 {selected_floor}층 지도를 보고 있습니다.</div>',
        unsafe_allow_html=True,
    )
    html(floor_plan_html(selected_floor, route, route_start, route_end), height=670, scrolling=False)

    distance_m = max(20, round(st.session_state.route_cost * .28 / 10) * 10)
    minutes = max(1, round(distance_m / 65))
    step_markup = ''.join((('<span class="chev">›</span>' if i else '') + f'<span class="route-step">{html_lib.escape(step)}</span>') for i, step in enumerate(route_steps(route)))
    notice = ""
    if len(route_floors) > 1:
        notice = f'<div class="notice">층별 버튼을 바꾸면 각 층의 이동 경로를 확인할 수 있습니다. 경로에 {", ".join(map(str, route_floors))}층이 포함됩니다.</div>'
    st.markdown(f'<div class="summary-card"><div class="summary-top"><div class="metric"><div class="metric-label">예상 거리</div><div class="metric-value">약 {distance_m}m</div></div><div class="metric"><div class="metric-label">예상 시간</div><div class="metric-value">약 {minutes}분</div></div></div><div class="route-steps">{step_markup}</div>{notice}</div>', unsafe_allow_html=True)
else:
    preview_floor = int(PLACES[st.session_state.route_start]["floor"])
    html(
        floor_plan_html(preview_floor, [], st.session_state.route_start, st.session_state.route_end),
        height=670,
        scrolling=False,
    )
    st.info("출발지와 도착지를 선택한 뒤 **길 안내 생성** 버튼을 눌러주세요.")
