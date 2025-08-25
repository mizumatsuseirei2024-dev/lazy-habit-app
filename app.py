# app.py
import streamlit as st
import datetime, random

#theme
THEME = {
    "学習": ("📘", "#2d6cdf"),
    "運動": ("🏃", "#2ca02c"),
    "掃除": ("🧹", "#ff7f0e"),
    "創作": ("🎨", "#d62728"),
    "日記": ("📝", "#9467bd"),
}

st.set_page_config(
    page_title="Lazy Continuity",
    layout="centered",
    page_icon="🧸",
    initial_sidebar_state="expanded"
)

# ===== ヘルパー関数 =====
def render_card(html: str):
    st.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)
    

# --- 初期化 ---
if "history" not in st.session_state:
    st.session_state.history = {}  # {"YYYY-MM-DD": {"task": "...", "category": "..."}}
if "today_task" not in st.session_state:
    st.session_state.today_task = None
if "seed" not in st.session_state:
    st.session_state.seed = 42

# --- 設定UI（最小） ---
with st.sidebar:
    st.header("設定")
    category = st.selectbox("カテゴリ", ["学習", "運動", "掃除", "創作", "日記"])
    lazy_level = st.slider("怠惰レベル（高いほど易しい）", 1, 5, 4)
    st.caption("※ MVPではレベルが高いほど“より小さい”タスクを出します。")
    weekly_goal = st.slider("今週の目標回数（7日間）", 1, 7, 4)


# --- タスク候補（初期セット） ---
CANDIDATES = {
    "学習": {
        1: ["英単語を5個覚える", "教科書1ページ読む"],
        3: ["英単語を1個覚える", "教科書の見出しだけ読む"],
        5: ["英単語を1個眺めるだけ", "ノートを1分だけ開く"],
    },
    "運動": {
        1: ["スクワット10回", "腕立て10回"],
        3: ["スクワット3回", "ストレッチを1分"],
        5: ["立ち上がって深呼吸3回", "肩回しを10回"],
    },
    "掃除": {
        1: ["机の上を3分片付け", "床を掃除機で3分"],
        3: ["机の一角だけ拭く", "ゴミを1つ捨てる"],
        5: ["ティッシュで机をひと拭き", "床に落ちた紙切れ1つ拾う"],
    },
    "創作": {
        1: ["スケッチを3分", "文章を100字書く"],
        3: ["スケッチを1分", "文章を30字書く"],
        5: ["点と線を10本描く", "文章を1文だけ書く"],
    },
    "日記": {
        1: ["今日の出来事を3行", "よかったことを3つ"],
        3: ["よかったことを1つ", "今日の気分を1行"],
        5: ["今日の気分を1語", "顔文字1つ（例: 🙂）"],
    },
}

def pick_task(cat: str, level: int) -> str:
    # 1/3/5の近いバケツに丸める
    bucket = 5 if level >= 4 else (3 if level >= 2 else 1)
    random.seed(st.session_state.seed + datetime.date.today().toordinal())
    return random.choice(CANDIDATES[cat][bucket])

# --- 今日のタスク生成 ---
today = datetime.date.today().isoformat()
if st.session_state.today_task is None or st.session_state.today_task.get("date") != today:
    st.session_state.today_task = {
        "task": pick_task(category, lazy_level),
        "category": category,
        "level": lazy_level,
        "date": today,
    }

# --- タスクカード ---
t = st.session_state.today_task
emoji, color = THEME[t["category"]]

task_html = f"""
  <div class="task-card" style="border-color:{color}66;">
    <div class="title">{emoji} 今日やる最小タスク</div>
    <div class="main">{t['task']}</div>
    <div class="meta">カテゴリ: {t['category']} ／ レベル: {t['level']}</div>
  </div>
"""

# 👇ここで render_card を呼び出す
render_card(task_html)

col1, col2 = st.columns(2)

with col1:
    # 「別の提案」= セカンダリ（ゴースト調）
    if st.button("🧠 別の提案", use_container_width=True):
        st.session_state.seed += 1
        st.session_state.today_task = {
            "task": pick_task(category, lazy_level),
            "category": category,
            "level": lazy_level,
            "date": today,
        }
        st.rerun()

with col2:
    # 「やった！」= プライマリ（ネオングラデ）
    if st.button("✅ やった！", type="primary", use_container_width=True):
        st.session_state.history[today] = {
            "task": t["task"],
            "category": t["category"],
            "level": t["level"],
        }
        st.toast("記録しました！", icon="✅")
        st.balloons()
        st.rerun()



# --- 継続メトリクス ---
def calc_streak(dates: list[str]) -> int:
    if not dates: return 0
    dates_sorted = sorted(dates, reverse=True)
    cur = datetime.date.today()
    streak = 0
    for d in dates_sorted:
        dt = datetime.date.fromisoformat(d)
        if dt == cur:
            streak += 1
            cur = cur - datetime.timedelta(days=1)
        else:
            break
    return streak

today_dt = datetime.date.today()
last7 = [(today_dt - datetime.timedelta(days=i)).isoformat() for i in range(7)]
done_last7 = sum(d in st.session_state.history for d in last7)

# --- ダッシュボードカード群 ---
col1, col2 = st.columns(2)

with col1:
    render_card("""
      <h3>Quest Progress</h3>
      <div class="progress-bar"><span style="width:38%"></span></div>
      <p>38%</p>
    """)

    render_card("""
      <h3>Level 15</h3>
      <div class="level-badge">15</div>
    """)

with col2:
    render_card("""
      <h3>Daily Missions</h3>
      <div class="circular-progress"><span>78%</span></div>
    """)

    render_card("""
      <h3>Dungeon Stats</h3>
      <div class="stats">
        <div class="stat">
          <div class="label">Attack</div>
          <div class="bar"><span style="width:80%"></span></div>
        </div>
        <div class="stat">
          <div class="label">Defense</div>
          <div class="bar"><span style="width:50%"></span></div>
        </div>
        <div class="stat">
          <div class="label">Health</div>
          <div class="bar"><span style="width:65%"></span></div>
        </div>
      </div>
    """)


neon_css = """
<style>
  /* ====== Global ====== */
  .stApp { background:#0a0f1c; color:#e6edf3; font-family:'Inter',ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Meiryo,sans-serif }
  div[data-testid="block-container"]{ max-width:1100px; padding-top:20px }

  /* ====== Card ====== */
  .card{
    background: rgba(20,30,60,.6);
    border: 1px solid rgba(0,200,255,.30);
    border-radius:16px; padding:20px; min-width:220px;
    text-align:center; position:relative;
    box-shadow:0 0 15px rgba(0,200,255,.20);
    transition:.3s;
  }
  .card:hover{ box-shadow:0 0 25px rgba(0,200,255,.6) }

  /* ====== Progress Bar (linear) ====== */
  .progress-bar{ background:rgba(0,200,255,.20); border-radius:10px; height:10px; margin-top:10px; overflow:hidden }
  .progress-bar span{
    display:block; height:100%; width:38%;
    background:linear-gradient(90deg,#00f6ff,#007bff);
    border-radius:10px; box-shadow:0 0 10px #00f6ff; transition:width .4s ease;
  }

  /* ====== Circular Progress ====== */
  .circular-progress{ width:120px; height:120px; border-radius:50%;
    background: conic-gradient(#00f6ff 78%, rgba(0,200,255,.1) 0);
    display:flex; align-items:center; justify-content:center; margin:0 auto 10px; position:relative }
  .circular-progress::before{ content:''; width:90px; height:90px; background:#0a0f1c; border-radius:50%; position:absolute }
  .circular-progress span{ position:absolute; font-size:22px; font-weight:700; color:#00f6ff }

  /* ====== Stats Bars ====== */
  .stats{ text-align:left; margin-top:15px }
  .stats .stat{ margin-bottom:10px }
  .stats .label{ font-size:14px; opacity:.7 }
  .stats .bar{ background:rgba(0,200,255,.2); border-radius:6px; height:8px; margin-top:4px; overflow:hidden }
  .stats .bar span{ display:block; height:100%;
    background:linear-gradient(90deg,#00f6ff,#007bff);
    border-radius:6px; box-shadow:0 0 6px #00f6ff }

  /* ====== Level Badge ====== */
  .level-badge{
    font-size:28px; font-weight:700; color:#00f6ff;
    padding:20px; border:2px solid rgba(0,200,255,.4);
    border-radius:12px; background:rgba(0,200,255,.1);
    box-shadow:0 0 20px rgba(0,200,255,.4); margin:20px auto; display:inline-block
  }

  /* タスク表示カード（既存のTHEME色を枠色に） */
  .task-card{
    background:rgba(10,16,28,.7); border-radius:16px; padding:18px; text-align:left;
    border:1px solid rgba(0,200,255,.25); box-shadow:0 0 14px rgba(0,200,255,.15)
  }
  .task-card .title{ font-weight:800; color:#c8e9ff; letter-spacing:.2px }
  .task-card .main { font-size:1.15rem; font-weight:700; color:#ffffff }
  .task-card .meta { color:#9db1c7; margin-top:6px }

  /* Secondary（=通常）ボタン：透明×シアン枠のゴースト調 */
  .stButton > button {
    background: rgba(0,200,255,.08) !important;
    border: 1px solid rgba(0,200,255,.35) !important;
    color: #c8e9ff !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-weight: 700 !important;
    letter-spacing: .2px !important;
    box-shadow: inset 0 0 10px rgba(0,200,255,.12), 0 0 10px rgba(0,200,255,.12) !important;
    transition: all .15s ease !important;
  }
  .stButton > button:hover {
    background: rgba(0,200,255,.16) !important;
    border-color: #00f6ff !important;
    box-shadow: 0 0 18px rgba(0,246,255,.35) !important;
  }

  /* Primaryボタン：ネオングラデ＋強い発光（=「やった！」用） */
  button[kind="primary"] {
    background: linear-gradient(90deg,#00f6ff,#007bff) !important;
    border: none !important;
    color: #06131c !important;       /* 文字色：暗背景に黒字で近未来っぽく */
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-weight: 800 !important;
    letter-spacing: .2px !important;
    box-shadow: 0 0 20px rgba(0,246,255,.45) !important;
  }
  button[kind="primary"]:hover {
    filter: brightness(1.07) !important;
    box-shadow: 0 0 26px rgba(0,246,255,.60) !important;
  }
</style>
"""
st.markdown(neon_css, unsafe_allow_html=True)
