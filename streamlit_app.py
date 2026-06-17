import streamlit as st
import random
import time

# 페이지 설정
st.set_page_config(page_title="스트림릿 테트리스", layout="centered")

# 게임 상수 설정
ROWS = 20
COLS = 10

# 테트로미노 모양 및 색상 정의
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

COLORS = {
    'I': '❄️', 'O': '🟡', 'T': '🟣', 'S': '🟢', 'Z': '🔴', 'J': '🔵', 'L': '🟠', 'E': '⬛'
}

# 세션 상태(State) 초기화
if 'grid' not in st.session_state:
    st.session_state.grid = [['E'] * COLS for _ in range(ROWS)]
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.current_piece = None
    st.session_state.p_x = 0
    st.session_state.p_y = 0

def spawn_piece():
    shape_name = random.choice(list(SHAPES.keys()))
    st.session_state.current_piece = SHAPES[shape_name]
    st.session_state.current_type = shape_name
    st.session_state.p_x = COLS // 2 - len(st.session_state.current_piece[0]) // 2
    st.session_state.p_y = 0
    
    if check_collision(st.session_state.p_x, st.session_state.p_y, st.session_state.current_piece):
        st.session_state.game_over = True

def check_collision(nx, ny, piece):
    for r, row in enumerate(piece):
        for c, val in enumerate(row):
            if val:
                if nx + c < 0 or nx + c >= COLS or ny + r >= ROWS:
                    return True
                if st.session_state.grid[ny + r][nx + c] != 'E':
                    return True
    return False

def lock_piece():
    piece = st.session_state.current_piece
    for r, row in enumerate(piece):
        for c, val in enumerate(row):
            if val:
                st.session_state.grid[st.session_state.p_y + r][st.session_state.p_x + c] = st.session_state.current_type
    clear_lines()
    spawn_piece()

def clear_lines():
    new_grid = [row for row in st.session_state.grid if any(cell == 'E' for cell in row)]
    cleared = ROWS - len(new_grid)
    if cleared > 0:
        st.session_state.score += cleared * 100
        for _ in range(cleared):
            new_grid.insert(0, ['E'] * COLS)
        st.session_state.grid = new_grid

def move(dx, dy):
    if st.session_state.game_over: return
    if not check_collision(st.session_state.p_x + dx, st.session_state.p_y + dy, st.session_state.current_piece):
        st.session_state.p_x += dx
        st.session_state.p_y += dy
    elif dy > 0:
        lock_piece()

def rotate():
    if st.session_state.game_over: return
    # 행렬 회전 (시계 방향)
    rotated = list(zip(*st.session_state.current_piece[::-1]))
    rotated = [list(row) for row in rotated]
    if not check_collision(st.session_state.p_x, st.session_state.p_y, rotated):
        st.session_state.current_piece = rotated

def reset_game():
    st.session_state.grid = [['E'] * COLS for _ in range(ROWS)]
    st.session_state.score = 0
    st.session_state.game_over = False
    spawn_piece()

# 게임 시작 시 첫 블록 생성
if st.session_state.current_piece is None:
    spawn_piece()

# --- 화면 UI 레이아웃 ---
st.title("🧱 Streamlit Tetris")
st.subheader(f"Score: {st.session_state.score}")

if st.session_state.game_over:
    st.error("🚨 Game Over! 버튼을 눌러 재시작하세요.")
    if st.button("다시 시작하기"):
        reset_game()
        st.rerun()

# 임시 렌더링용 그리드 생성 (현재 떨어지는 블록 합성)
render_grid = [row[:] for row in st.session_state.grid]
if not st.session_state.game_over and st.session_state.current_piece:
    for r, row in enumerate(st.session_state.current_piece):
        for c, val in enumerate(row):
            if val:
                py, px = st.session_state.p_y + r, st.session_state.p_x + c
                if 0 <= py < ROWS and 0 <= px < COLS:
                    render_grid[py][px] = st.session_state.current_type

# 이모지를 이용해 보드판 그리기
board_html = ""
for row in render_grid:
    board_html += " ".join([COLORS[cell] for cell in row]) + "<br>"

st.markdown(
    f"<div style='font-size: 24px; line-height: 1.2; font-family: monospace; letter-spacing: 2px;'>{board_html}</div>", 
    unsafe_allow_html=True
)

st.write("---")

# 컨트롤 버튼 (스트림릿은 버튼 클릭으로 조작)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("⬅️ 왼쪽"):
        move(-1, 0)
        st.rerun()
with col2:
    if st.button("🔄 회전"):
        rotate()
        st.rerun()
with col3:
    if st.button("⬇️ 아래로"):
        move(0, 1)
        st.rerun()
with col4:
    if st.button("➡️ 오른쪽"):
        move(1, 0)
        st.rerun()
with col5:
    if st.button("⏬ 하드드롭"):
        while not check_collision(st.session_state.p_x, st.session_state.p_y + 1, st.session_state.current_piece):
            st.session_state.p_y += 1
        lock_piece()
        st.rerun()

# 중력 효과 (아래로 자연스럽게 떨어지도록 유도하는 자동 리프레시 버튼)
if not st.session_state.game_over:
    if st.button("시간 진행 (결과 반영) ⏳"):
        move(0, 1)
        st.rerun()
