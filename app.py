import streamlit as st
import collections

# ====================== LOAD CORPUS ======================
@st.cache_data
def load_corpus():
    file_path = "cleaned.txt"
    try:
        with open(file_path, 'r', encoding='utf-16') as f:
            text = f.read()
    except:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    
    tokens = text.split()
    unigram_counts = collections.Counter(tokens)
    vocabulary = set(unigram_counts.keys())
    return vocabulary, unigram_counts

vocabulary, unigram_counts = load_corpus()

# ====================== MIN EDIT DISTANCE ======================
def min_edit_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if word1[i-1] == word2[j-1] else 1
            dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + cost)
    return dp[m][n]

# ====================== SPELL CORRECTOR ======================
def correct_spelling(misspelled_word):
    special_rules = {"مین": "میں", "نی": "نے", "مینں": "میں", "نیی": "نے", "مں": "میں"}
    
    if misspelled_word in special_rules:
        suggested = special_rules[misspelled_word]
        if suggested in vocabulary:
            return suggested, 1, "Special Rule"

    if misspelled_word in vocabulary:
        return misspelled_word, 0, "Correct"

    candidates = []
    max_freq = max(unigram_counts.values()) if unigram_counts else 1

    for correct_word in vocabulary:
        dist = min_edit_distance(misspelled_word, correct_word)
        if dist <= 3:
            freq = unigram_counts.get(correct_word, 1)
            score = 0.65 * (dist / 4) - 0.35 * (freq / max_freq)
            candidates.append((correct_word, dist, freq, score))

    if not candidates:
        return misspelled_word, 0, "No suggestion"

    candidates.sort(key=lambda x: (x[1], -x[2]))
    best_word, best_dist, _, _ = candidates[0]
    return best_word, best_dist, "Corrected"

# ====================== STREAMLIT UI ======================
st.set_page_config(page_title="اردو اسپیل چیکر", layout="centered", page_icon="🧠")

st.title("🧠 اردو اسپیل چیکر")
st.markdown("**Minimum Edit Distance** کے ذریعے اردو ٹیکسٹ کی غلطیاں درست کریں")

# Text Input
input_text = st.text_area(
    "اردو متن درج کریں:", 
    placeholder="مثال: مین نی کھانا کھا لیا ہے",
    height=120,
    key="input_box"
)

# Check Button
if st.button("✅ Spelling Check کریں", type="primary", use_container_width=True):
    if input_text.strip():
        words = input_text.strip().split()
        corrected = []
        details = []

        for word in words:
            fixed, dist, status = correct_spelling(word)
            if status in ["Corrected", "Special Rule"]:
                corrected.append(fixed)
                details.append(f"❌ {word} → ✅ {fixed} (dist={dist})")
            else:
                corrected.append(word)
                details.append(f"✅ {word} (صحیح)")

        st.success("**درست شدہ جملہ:**")
        st.write(" ".join(corrected))

        st.subheader("تفصیلی رپورٹ")
        for d in details:
            st.write(d)
    else:
        st.warning("براہ مہربانی کچھ متن درج کریں۔")

# ====================== EXAMPLES (Fixed) ======================
st.subheader("📌 مثالیں (Click karein)")

examples = [
    "مین نی کھانا کھا لیا ہے",
    "حکومٹ نے اعلان کیا ہے",
    "پاکستانن ایک خوبصورت ملک ہے",
    "تعلییم بہت اہم ہے",
    "اسلآم میں قرآن پڑھتا ہوں"
]

cols = st.columns(3)

for i, ex in enumerate(examples):
    col = cols[i % 3]
    if col.button(ex, key=f"ex_{i}"):
        st.session_state.input_box = ex   # Yeh line important hai
        st.rerun()

# Footer
st.caption("Developed as Final Semester Project | FA23-BAI-007 - Aftab Ahmad")
