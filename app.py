import streamlit as st
import streamlit.components.v1 as components

# 1. 스트림릿 페이지 설정 (와이드 모드 및 타이틀)
st.set_page_config(page_title="NEON TETRIS Pro", layout="centered")

st.markdown("""
    <style>
    .reportview-container { background: #0f172a; }
    h1 { color: #00f2fe; text-align: center; font-family: 'Segoe UI', sans-serif; text-shadow: 0 0 10px #00f2fe; }
    .stDescription { text-align: center; color: #94a3b8; }
    </style>
""", unsafe_allow_html=True)

st.title("🕹️ NEON TETRIS Pro")
st.caption("스트림릿 내부에서 100% 부드러운 키보드 조작이 가능한 고퀄리티 테트리스입니다.")

# 2. HTML5 Canvas + JavaScript 테트리스 엔진 
# 스트림릿의 한계를 넘기 위해 브라우저 자체 엔진을 활용합니다.
tetris_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background-color: #0f172a;
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        .game-container {
            display: flex;
            background: rgba(30, 41, 59, 0.7);
            padding: 20px;
            border-radius: 20px;
            box-shadow: 0 20px 50px rgba(0, 242, 254, 0.2);
            border: 1px solid rgba(0, 242, 254, 0.3);
        }
        canvas {
            border: 4px solid #334155;
            background: #020617;
            border-radius: 8px;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
        }
        .side-panel {
            margin-left: 25px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            width: 140px;
        }
        .stat-box {
            background: #1e293b;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #475569;
        }
        .stat-title {
            font-size: 12px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #00f2fe;
            text-shadow: 0 0 8px rgba(0, 242, 254, 0.5);
        }
        .controls-info {
            font-size: 11px;
            color: #64748b;
            line-height: 1.6;
            background: #1e293b;
            padding: 10px;
            border-radius: 10px;
        }
        .btn-restart {
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
            border: none;
            color: white;
            padding: 10px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: 0.2s;
        }
        .btn-restart:hover {
            transform: scale(1.05);
            box-shadow: 0 0 15px #00f2fe;
        }
    </style>
</head>
<body>

<div class="game-container">
    <canvas id="tetris" width="240" height="480"></canvas>
    <div class="side-panel">
        <div class="stat-box">
            <div class="stat-title">SCORE</div>
            <div id="score" class="stat-value">0</div>
        </div>
        <div class="stat-box">
            <div class="stat-title">LINES</div>
            <div id="lines" class="stat-value">0</div>
        </div>
        <button class="btn-restart" onclick="resetGame()">RESTART</button>
        <div class="controls-info">
            <b>[조작 방법]</b><br>
            ← → : 좌우 이동<br>
            ↑ : 블록 회전<br>
            ↓ : 소프트 드롭<br>
            Space : 하드 드롭
        </div>
    </div>
</div>

<script>
    const canvas = document.getElementById('tetris');
    const context = canvas.getContext('2d');
    context.scale(24, 24); // 10x20 그리드 스케일링

    const COLORS = [
        null,
        '#00f2fe', // I (Neon Cyan)
        '#ffe259', // O (Neon Yellow)
        '#b92b27', // Z (Neon Red)
        '#159957', // S (Neon Green)
        '#dd3e54', // J (Neon Blueish Pink)
        '#f5af19', // L (Neon Orange)
        '#8e2de2'  // T (Neon Purple)
    ];

    const SHAPES = [
        [],
        [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
        [[2,2],[2,2]],
        [[3,3,0],[0,3,3],[0,0,0]],
        [[0,4,4],[4,4,0],[0,0,0]],
        [[5,0,0],[5,5,5],[0,0,0]],
        [[0,0,6],[6,6,6],[0,0,0]],
        [[0,7,0],[7,7,7],[0,0,0]]
    ];

    let arena = createMatrix(10, 20);
    let player = {
        pos: {x: 0, y: 0},
        matrix: null,
        score: 0,
        lines: 0
    };

    function arenaSweep() {
        let rowCount = 1;
        outer: for (let y = arena.length - 1; y > 0; --y) {
            for (let x = 0; x < arena[y].length; ++x) {
                if (arena[y][x] === 0) {
                    continue outer;
                }
            }
            const row = arena.splice(y, 1)[0].fill(0);
            arena.unshift(row);
            ++y;

            player.score += rowCount * 100;
            player.lines += 1;
            rowCount *= 2;
        }
    }

    function collide(arena, player) {
        const [m, o] = [player.matrix, player.pos];
        for (let y = 0; y < m.length; ++y) {
            for (let x = 0; x < m[y].length; ++x) {
                if (m[y][x] !== 0 &&
                   (arena[y + o.y] &&
                    arena[y + o.y][x + o.x]) !== 0) {
                    return true;
                }
            }
        }
        return false;
    }

    function createMatrix(w, h) {
        const matrix = [];
        while (h--) {
            matrix.push(new Array(w).fill(0));
        }
        return matrix;
    }

    function draw() {
        // 배경 그리기
        context.fillStyle = '#020617';
        context.fillRect(0, 0, canvas.width, canvas.height);

        // 그리드 보조선 그리기
        context.strokeStyle = 'rgba(51, 65, 85, 0.3)';
        context.lineWidth = 0.05;
        for (let i = 0; i < 10; i++) {
            context.beginPath(); context.moveTo(i, 0); context.lineTo(i, 20); context.stroke();
        }
        for (let i = 0; i < 20; i++) {
            context.beginPath(); context.moveTo(0, i); context.lineTo(10, i); context.stroke();
        }

        drawMatrix(arena, {x: 0, y: 0});
        drawMatrix(player.matrix, player.pos);
    }

    function drawMatrix(matrix, offset) {
        matrix.forEach((row, y) => {
            row.forEach((value, x) => {
                if (value !== 0) {
                    // 그라데이션 및 네온 이펙트 스타일 적용
                    context.fillStyle = COLORS[value];
                    context.fillRect(x + offset.x, y + offset.y, 1, 1);
                    
                    // 블록 테두리 디테일
                    context.strokeStyle = 'rgba(255,255,255,0.2)';
                    context.lineWidth = 0.08;
                    context.strokeRect(x + offset.x, y + offset.y, 1, 1);
                }
            });
        });
    }

    function merge(arena, player) {
        player.matrix.forEach((row, y) => {
            row.forEach((value, x) => {
                if (value !== 0) {
                    arena[y + player.pos.y][x + player.pos.x] = value;
                }
            });
        });
    }

    function playerDrop() {
        player.pos.y++;
        if (collide(arena, player)) {
            player.pos.y--;
            merge(arena, player);
            playerReset();
            arenaSweep();
            updateScore();
        }
        dropCounter = 0;
    }

    function playerHardDrop() {
        while (!collide(arena, player)) {
            player.pos.y++;
        }
        player.pos.y--;
        merge(arena, player);
        playerReset();
        arenaSweep();
        updateScore();
        dropCounter = 0;
    }

    function playerMove(dir) {
        player.pos.x += dir;
        if (collide(arena, player)) {
            player.pos.x -= dir;
        }
    }

    function playerReset() {
        const pieces = '1234567';
        const type = pieces[pieces.length * Math.random() | 0] - '0';
        player.matrix = SHAPES[type];
        player.pos.y = 0;
        player.pos.x = (arena[0].length / 2 | 0) - (player.matrix[0].length / 2 | 0);
        
        if (collide(arena, player)) {
            // 게임오버 시 아레나 초기화
            arena.forEach(row => row.fill(0));
            player.score = 0;
            player.lines = 0;
            updateScore();
        }
    }

    function playerRotate() {
        const pos = player.pos.x;
        let offset = 1;
        rotate(player.matrix);
        while (collide(arena, player)) {
            player.pos.x += offset;
            offset = -(offset + (offset > 0 ? 1 : -1));
            if (offset > player.matrix[0].length) {
                rotate(player.matrix);
                player.pos.x = pos;
                return;
            }
        }
    }

    function rotate(matrix) {
        for (let y = 0; y < matrix.length; ++y) {
            for (let x = 0; x < y; ++x) {
                [
                    matrix[x][y],
                    matrix[y][x],
                ] = [
                    matrix[y][x],
                    matrix[x][y],
                ];
            }
        }
        matrix.forEach(row => row.reverse());
    }

    let dropCounter = 0;
    let dropInterval = 1000; // 블록 하강 속도 (1초)
    let lastTime = 0;

    function update(time = 0) {
        const deltaTime = time - lastTime;
        lastTime = time;

        dropCounter += deltaTime;
        if (dropCounter > dropInterval) {
            playerDrop();
        }

        draw();
        requestAnimationFrame(update);
    }

    function updateScore() {
        document.getElementById('score').innerText = player.score;
        document.getElementById('lines').innerText = player.lines;
    }

    function resetGame() {
        arena.forEach(row => row.fill(0));
        player.score = 0;
        player.lines = 0;
        updateScore();
        playerReset();
    }

    // 키보드 이벤트 리스너 (포커스 이슈 해결을 위해 윈도우 전체 바인딩)
    window.addEventListener('keydown', event => {
        if ([32, 37, 38, 39, 40].indexOf(event.keyCode) > -1) {
            event.preventDefault(); // 방향키/스페이스바 브라우저 스크롤 방지
        }

        if (event.keyCode === 37) {
            playerMove(-1);
        } else if (event.keyCode === 39) {
            playerMove(1);
        } else if (event.keyCode === 40) {
            playerDrop();
        } else if (event.keyCode === 38) {
            playerRotate();
        } else if (event.keyCode === 32) {
            playerHardDrop();
        }
    });

    playerReset();
    updateScore();
    update();
</script>
</body>
</html>
"""

# 3. 스트림릿 컴포넌트로 HTML 삽입 (창 크기에 딱 맞춤)
components.html(tetris_html, height=550)
