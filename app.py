import collections
import os
import gradio as gr

# Load the Urdu corpus
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

# Minimum Edit Distance Function
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

# Spell Corrector Function
def correct_spelling(misspelled_word):
    # Special Urdu rules
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
    best_word, best_dist, best_freq, _ = candidates[0]
    return best_word, best_dist, "Corrected"

# Gradio Interface Function
def spell_check_interface(input_text):
    if not input_text or not input_text.strip():
        return "براہ مہربانی کچھ اردو متن درج کریں۔", ""

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

    return " ".join(corrected), "\n".join(details)

# Gradio UI
with gr.Blocks(title="اردو اسپیل چیکر", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🧠 اردو اسپیل چیکر\n**Minimum Edit Distance** سے اردو کی غلطیاں درست کریں")

    with gr.Row():
        inp = gr.Textbox(label="اردو متن درج کریں", placeholder="مین نی کھانا کھا لیا ہے", lines=3, rtl=True)
        btn = gr.Button("✅ Check کریں", variant="primary")

    with gr.Row():
        out1 = gr.Textbox(label="✅ درست شدہ جملہ", rtl=True)
        out2 = gr.Textbox(label="تفصیل", lines=6, rtl=True)

    btn.click(spell_check_interface, inputs=inp, outputs=[out1, out2])

    gr.Examples([
        ["مین نی کھانا کھا لیا ہے"],
        ["حکومٹ نے اعلان کیا ہے"],
        ["پاکستانن ایک اچھا ملک ہے"]
    ], inputs=inp)

# Important for deployment
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", 7860)))
