import streamlit as st
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Moon Block Divination | CS109",
    page_icon="🌙",
    layout="wide",
)

# ─── Session State ───────────────────────────────────────────────────────────
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False

# ─── Sidebar: Measured Data ──────────────────────────────────────────────────
st.sidebar.header("📊 Measured Block Data")
st.sidebar.caption("Enter your real experimental counts (100 casts per block).")

k_A = st.sidebar.slider("Block A: flat-side-up count (out of 100)", 0, 100, 63)
k_B = st.sidebar.slider("Block B: flat-side-up count (out of 100)", 0, 100, 56)
N   = 100

# ─── Monte Carlo: 100,000 samples from Beta posterior ───────────────────────
# Prior: Beta(1,1)  →  Posterior: Beta(1+k, 1+N-k)
N_SAMPLES = 100_000
alpha_A, beta_A = 1 + k_A, 1 + N - k_A
alpha_B, beta_B = 1 + k_B, 1 + N - k_B

p_A_samples = stats.beta.rvs(alpha_A, beta_A, size=N_SAMPLES)
p_B_samples = stats.beta.rvs(alpha_B, beta_B, size=N_SAMPLES)

# Three-outcome probability distributions (one value per sample)
# p = flat-side-up probability
# Sheng 聖杯: one flat, one rounded
# Xiao 笑杯: BOTH flat sides up  (p_A × p_B)
# Yin  陰杯: BOTH rounded sides up  ((1-p_A) × (1-p_B))
P_sheng_samples = p_A_samples * (1 - p_B_samples) + (1 - p_A_samples) * p_B_samples
P_xiao_samples  = p_A_samples * p_B_samples
P_yin_samples   = (1 - p_A_samples) * (1 - p_B_samples)

# Point estimates = mean over 100k samples
P_sheng = float(np.mean(P_sheng_samples))
P_yin   = float(np.mean(P_yin_samples))
P_xiao  = float(np.mean(P_xiao_samples))

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='text-align: center;'>
        <h1>🌙 Moon Block Divination</h1>
        <h3>When Ancient Ritual Meets Modern Probability Theory</h3>
        <p style='color: grey; font-size: 0.85em;'>CS109 Probability Challenge · Winter 2026</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ─── Outcome Probabilities ───────────────────────────────────────────────────
st.subheader("Outcome Probabilities from Your Measured Data")
col1, col2, col3 = st.columns(3)
col1.metric("P(Sheng 聖杯)", f"{P_sheng:.4f}", help="One flat, one rounded — Divine YES")
col2.metric("P(Xiao 笑杯)",  f"{P_xiao:.4f}",  help="Both flat sides up — Ask again / deity laughing")
col3.metric("P(Yin 陰杯)",   f"{P_yin:.4f}",   help="Both rounded sides up — Divine NO / Rejection")

with st.expander("How are these computed?"):
    st.markdown(
        f"""
Each block's unknown landing probability **p** is modeled as a Beta random variable.
Starting from a uniform prior Beta(1, 1), after observing **k** flat-side-up results
in **N = 100** casts, the posterior is:
        """
    )
    st.latex(r"p \sim \text{Beta}(1 + k,\ 1 + N - k)")
    st.markdown(
        f"""
Rather than using a single point estimate, we draw **100,000 samples** from each
block's posterior Beta distribution:

- Block A: Beta({alpha_A}, {beta_A}) → 100,000 samples of p_A  
- Block B: Beta({alpha_B}, {beta_B}) → 100,000 samples of p_B

For each of the 100,000 sample pairs (p_A, p_B), we compute the three outcome
probabilities using the independence assumption (Block A and Block B cast independently):
        """
    )
    st.latex(r"P(\text{Sheng } \text{聖}) = p_A(1-p_B) + (1-p_A)p_B")
    st.latex(r"P(\text{Xiao } \text{笑})  = p_A \cdot p_B \quad \text{(both flat up)}")
    st.latex(r"P(\text{Yin }  \text{陰})  = (1-p_A)(1-p_B) \quad \text{(both rounded up)}")
    st.markdown(
        """
The displayed values are the **means over all 100,000 samples** — this is not a
point estimate. It reflects our full uncertainty about the true p by averaging
over the entire posterior distribution.  
*Lecture 14 (Beta distribution) · Lecture 3 (Independence)*
        """
    )

st.divider()

# ─── Mode Selector ───────────────────────────────────────────────────────────
mode = st.radio(
    "Choose a mode:",
    ["🎮 Digital Divination Experience", "🔍 Real Data Analyzer"],
    horizontal=True,
)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# MODE 1 — Digital Divination
# ════════════════════════════════════════════════════════════════════════════
if mode == "🎮 Digital Divination Experience":

    st.subheader("🎮 Digital Divination Experience")
    st.write(
        "Ask the deity a yes/no question. "
        "You need **three consecutive Sheng 聖杯** for divine confirmation."
    )

    question = st.text_input("Your question:", placeholder="Should I apply to grad school?")

    col_cast, col_reset = st.columns([1, 5])
    cast_btn  = col_cast.button("擲杯 Cast the Blocks", use_container_width=True)
    reset_btn = col_reset.button("Reset", use_container_width=False)

    if reset_btn:
        st.session_state.streak    = 0
        st.session_state.history   = []
        st.session_state.confirmed = False
        st.rerun()

    if cast_btn and not st.session_state.confirmed:
        result = np.random.choice(
            ["Sheng 聖杯", "Xiao 笑杯", "Yin 陰杯"],
            p=[P_sheng, P_xiao, P_yin],
        )
        if result == "Sheng 聖杯":
            st.session_state.streak += 1
        else:
            st.session_state.streak = 0

        st.session_state.history.append(result)

        if st.session_state.streak >= 3:
            st.session_state.confirmed = True

    # ── Display current result ──
    if st.session_state.history:
        last = st.session_state.history[-1]
        icons = {"Sheng 聖杯": "✅", "Yin 陰杯": "❌", "Xiao 笑杯": "😄"}
        labels = {
            "Sheng 聖杯": "Sheng 聖杯 — The deity says YES",
            "Yin 陰杯":   "Yin 陰杯 — The deity says NO (streak reset)",
            "Xiao 笑杯":  "Xiao 笑杯 — The deity is laughing; ask again (streak reset)",
        }
        st.markdown(f"### {icons[last]} {labels[last]}")
        st.markdown(f"**Consecutive Sheng 聖杯 streak:** {st.session_state.streak} / 3")
        st.progress(min(st.session_state.streak / 3, 1.0))

        history_icons = [icons[r] for r in st.session_state.history]
        st.caption("Cast history: " + " ".join(history_icons))

        cum_prob = 1.0
        for r in st.session_state.history:
            if r == "Sheng 聖杯":   cum_prob *= P_sheng
            elif r == "Yin 陰杯":   cum_prob *= P_yin
            else:                   cum_prob *= P_xiao
        st.caption(f"Probability of this exact sequence: {cum_prob:.4%}")

    # ── Confirmation message ──
    if st.session_state.confirmed:
        n_casts = len(st.session_state.history)
        p_confirmed = P_sheng ** 3
        st.success(
            f"🏆 **Divine confirmation received** after {n_casts} cast(s)!\n\n"
            f"The probability of obtaining three consecutive Sheng 聖杯 by pure chance is "
            f"**P(Sheng)³ = {p_confirmed:.4f} ≈ {p_confirmed:.1%}**, "
            f"{'below' if p_confirmed < 0.05 else 'above'} the standard α = 0.05 threshold.\n\n"
            "This is mathematically equivalent to a hypothesis test — the ritual "
            "was designed to require a result that would be surprising under randomness."
        )

    # ── Expected casts to confirmation ──
    with st.expander("📐 Expected number of casts to confirmation"):
        p = P_sheng
        E_casts = (1/p) + (1/p**2) + (1/p**3)
        st.write(
            f"With P(Sheng 聖) = {p:.4f}, the expected number of casts to achieve "
            f"three consecutive Sheng 聖杯 is approximately **{E_casts:.1f} casts**."
        )
        st.latex(r"E[T] = \frac{1}{p} + \frac{1}{p^2} + \frac{1}{p^3}")

# ════════════════════════════════════════════════════════════════════════════
# MODE 2 — Real Data Analyzer
# ════════════════════════════════════════════════════════════════════════════
else:
    st.subheader("🔍 Real Data Analyzer")
    st.write(
        "Input your actual temple cast sequence. "
        "The tool computes the probability, compares it to α = 0.05, "
        "and benchmarks it against the 2026 Zhanjiang case."
    )

    st.markdown("#### Build your sequence")
    st.caption("Click the buttons to add results one at a time.")

    if "seq" not in st.session_state:
        st.session_state.seq = []

    btn_cols = st.columns(4)
    if btn_cols[0].button("➕ Sheng 聖杯 (YES)"):
        st.session_state.seq.append("Sheng 聖杯")
        st.rerun()
    if btn_cols[1].button("➕ Yin 陰杯 (NO)"):
        st.session_state.seq.append("Yin 陰杯")
        st.rerun()
    if btn_cols[2].button("➕ Xiao 笑杯 (ASK AGAIN)"):
        st.session_state.seq.append("Xiao 笑杯")
        st.rerun()
    if btn_cols[3].button("🗑️ Clear sequence"):
        st.session_state.seq = []
        st.rerun()

    seq = st.session_state.seq

    # Also allow direct text input
    manual = st.text_input(
        "Or type sequence manually — use S (Sheng), Y (Yin), X (Xiao), comma-separated:",
        placeholder="S,Y,X,S,S,S",
    )
    if manual.strip():
        mapping = {
            # Single-letter shortcuts
            "s": "Sheng 聖杯", "y": "Yin 陰杯", "x": "Xiao 笑杯",
            # Chinese characters
            "聖": "Sheng 聖杯", "陰": "Yin 陰杯", "笑": "Xiao 笑杯",
            "聖杯": "Sheng 聖杯", "陰杯": "Yin 陰杯", "笑杯": "Xiao 笑杯",
            # Full english
            "sheng": "Sheng 聖杯", "yin": "Yin 陰杯", "xiao": "Xiao 笑杯",
        }
        parsed = [mapping.get(x.strip().lower(), None) for x in manual.split(",")]
        if all(v is not None for v in parsed):
            seq = parsed
        else:
            st.warning("Unrecognized entries — use S (Sheng), Y (Yin), X (Xiao), or Chinese characters 聖/陰/笑.")

    if seq:
        icons = {"Sheng 聖杯": "✅", "Yin 陰杯": "❌", "Xiao 笑杯": "😄"}
        st.markdown("**Your sequence:** " + " ".join(icons[r] for r in seq))

        prob = 1.0
        for r in seq:
            if r == "Sheng 聖杯":   prob *= P_sheng
            elif r == "Yin 陰杯":   prob *= P_yin
            else:                   prob *= P_xiao

        st.divider()
        st.markdown("#### 📊 Analysis Results")

        res_col1, res_col2 = st.columns(2)
        res_col1.metric(
            "Probability of your sequence",
            f"{prob:.4%}",
            help="P(this exact sequence) under the null hypothesis of randomness"
        )
        res_col2.metric("Significance threshold α", "5.0000%")

        if prob < 0.05:
            st.success(
                f"✅ **Statistically significant** — p = {prob:.4%} < α = 0.05\n\n"
                f"Your sequence is **{0.05/prob:.1f}× more extreme** than the standard "
                f"significance threshold. We reject H₀ (pure randomness)."
            )
        else:
            st.warning(
                f"⚠️ **Not yet significant** — p = {prob:.4%} ≥ α = 0.05\n\n"
                "The sequence does not cross the standard significance threshold."
            )

        # ── Number-line visualization ──
        st.markdown("#### 📐 Position on the Significance Scale")
        fig, ax = plt.subplots(figsize=(9, 1.6))
        ax.set_xlim(0, 0.12)
        ax.axvline(0.05, color="#e74c3c", linewidth=2, label="α = 0.05")

        zan_prob = P_yin ** 8
        ax.axvline(zan_prob, color="#8e44ad", linewidth=1.5,
                   linestyle="--", label=f"Zhanjiang (8× Yin 陰): {zan_prob:.4%}")

        user_x = min(prob, 0.115)
        ax.axvline(user_x, color="#2980b9", linewidth=2,
                   label=f"Your sequence: {prob:.4%}")

        ax.set_yticks([])
        ax.set_xlabel("Probability under H₀ (randomness)")
        ax.legend(loc="upper right", fontsize=8)
        ax.set_title("Where does your result fall?", fontsize=10)
        ax.axvspan(0, 0.05, alpha=0.08, color="#e74c3c")
        ax.text(0.025, 0.65, "Reject H₀\n(statistically significant)",
                ha="center", va="center", transform=ax.get_xaxis_transform(),
                fontsize=7, color="#e74c3c")
        st.pyplot(fig)
        plt.close(fig)

        # ── Zhanjiang comparison ──
        st.divider()
        st.markdown("#### 📰 Comparison: 2026 Zhanjiang Case")
        st.caption(
            "During the 2026 Mazu parade, a boy cast 8 consecutive Yin 陰杯 — "
            "interpreted as extreme divine rejection."
        )

        tbl_col1, tbl_col2 = st.columns(2)
        with tbl_col1:
            st.markdown("**Zhanjiang: 8 consecutive Yin 陰杯**")
            st.metric("P(Yin 陰)⁸", f"{zan_prob:.6%}")
            st.metric("Times more extreme than α = 0.05", f"{0.05/zan_prob:.0f}×")

        with tbl_col2:
            st.markdown("**Your sequence**")
            st.metric("Probability", f"{prob:.4%}")
            ratio = 0.05 / prob if prob > 0 else float("inf")
            st.metric("Times more extreme than α = 0.05",
                      f"{ratio:.1f}×" if ratio < 1e6 else "> 1,000,000×")

        if prob > 0:
            st.caption(
                f"The Zhanjiang result (p ≈ {zan_prob:.4%}) is "
                f"approximately **{zan_prob/prob:.1f}× more extreme** than your sequence."
            )

    else:
        st.info("Add casts above to begin the analysis.")

# ─── Footer ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 0.85em;'>
    CS109 Probability Challenge · Winter 2026 · 
    Outcome probabilities estimated from 100,000 samples drawn from Beta posteriors. 
    Independence assumption used for outcome derivations.
    </div>
    <div style='text-align: center; color: grey; font-size: 0.85em;'>
    Copyright 2026© by Shih-Jung Wu
    </div>
    """,
    unsafe_allow_html=True,
)