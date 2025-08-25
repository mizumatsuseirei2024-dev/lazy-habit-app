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
card_html = f"""
<div class="task-card" style="border-color:{color}66;">
  <div class="title">{emoji} 今日やる最小タスク</div>
  <div class="main">{t['task']}</div>
  <div class="meta">カテゴリ: {t['category']} ／ レベル: {t['level']}</div>
</div>
"""
st.markdown(card_html, unsafe_allow_html=True)



col1, col2 = st.columns(2)
with col1:
    if st.button("🔁 別の提案"):
        st.session_state.seed += 1
        st.session_state.today_task = {
            "task": pick_task(category, lazy_level),
            "category": category,
            "level": lazy_level,
            "date": today,
        }
        st.rerun()
with col2:
    if st.button("✅ やった！"):
        st.session_state.history[today] = {"task": t["task"], "category": t["category"]}
        st.toast("記録しました！", icon="✅")
        st.balloons()


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

st.subheader("今週の進捗")
st.progress(min(done_last7 / weekly_goal, 1.0), text=f"{done_last7}/{weekly_goal}")
st.divider()
st.subheader("継続状況")
dates = list(st.session_state.history.keys())
st.metric("連続日数", f"{calc_streak(dates)} 日")
st.write("合計達成回数:", len(dates))

with st.expander("ログを見る"):
    for d in sorted(dates, reverse=True):
        item = st.session_state.history[d]
        st.write(f"- {d}｜{item['category']}｜{item['task']}")

dark_css = """
<style>
  /* ページ全体（本文サイズ/行間UP） */
  .stApp {
    background-color:#0d1117 !important;
    color:#e6edf3 !important;
    font-family: ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Hiragino Kaku Gothic ProN",Meiryo,sans-serif !important;
    font-size:16px !important;
    line-height:1.65 !important;
  }

  /* 中央カラムの幅・余白（読みやすく） */
  div[data-testid="block-container"]{
    max-width: 900px !important;
    padding-top: 24px !important;
  }

  /* サイドバー（確実に明るめ文字に） */
  section[data-testid="stSidebar"]{ background:#161b22 !important; }
  section[data-testid="stSidebar"] *{ color:#c9d1d9 !important; }

  /* 見出しのコントラスト */
  h1,h2,h3{ color:#f0f6fc !important; letter-spacing:.2px !important; }
  h2{ font-weight:800 !important; }

  /* 文章/ラベル */
  .stMarkdown p, label, span{ color:#c9d1d9 !important; }

  /* ボタン（白文字を強制） */
  button[kind="primary"]{
    background:linear-gradient(90deg,#1f6feb,#2ea043) !important;
    color:#ffffff !important; border-radius:10px !important;
    border:1px solid #1b4b91 !important; font-weight:650 !important;
  }
  button[kind="primary"]:hover{ filter:brightness(1.06) !important; }

  /* スライダー */
  .stSlider [role="slider"]{
    background:#58a6ff !important;
    box-shadow:0 0 0 3px rgba(88,166,255,.25) !important;
  }
  .stSlider div[data-testid="stTickBar"]{ background:#30363d !important; }

  /* プログレスバー */
  .stProgress > div > div > div > div{ background:#1f6feb !important; }
  .stProgress > div > div{ background:#30363d !important; }

  /* タスクカード：背景もう少し明るく、文字くっきり */
  .task-card{
    background:#161b22 !important;
    border:1.5px solid rgba(56,139,253,.55) !important;
    border-radius:14px !important;
    padding:16px 18px !important;
    box-shadow:0 6px 18px rgba(0,0,0,.35) !important;
  }
  .task-card .title{ color:#f0f6fc !important; font-size:1.15rem !important; font-weight:750 !important; }
  .task-card .main { color:#fefefe  !important; font-size:1.08rem !important; font-weight:650 !important; }
  .task-card .meta { color:#a3b1c9  !important; font-size:.9rem  !important; }
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

