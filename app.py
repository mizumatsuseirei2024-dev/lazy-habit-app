# app.py
import streamlit as st
import datetime, random

st.set_page_config(page_title="Lazy Continuity", layout="centered", page_icon="🧸")
st.title("🧸 怠惰でも続けられるアプリ")

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
st.subheader("今日やる最小タスク")
st.write(f"**カテゴリ：** {t['category']}　**レベル：** {t['level']}")
st.success(f"📝 **{t['task']}**")

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

st.divider()
st.subheader("継続状況")
dates = list(st.session_state.history.keys())
st.metric("連続日数", f"{calc_streak(dates)} 日")
st.write("合計達成回数:", len(dates))

with st.expander("ログを見る"):
    for d in sorted(dates, reverse=True):
        item = st.session_state.history[d]
        st.write(f"- {d}｜{item['category']}｜{item['task']}")
