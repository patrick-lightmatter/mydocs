"""Generate figures for the CTLE optimisation framework document."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from scipy.signal import bessel, group_delay, sosfilt, sosfreqz, tf2sos, lfilter

from optical_serdes.channel.electrical import BesselChannel
from optical_serdes.rx.ctle import CtleZPK
from optical_serdes.rx.ctle_design import (
    baud_pulse_response,
    candidate_sweep_peaking,
    channel_cursor,
    ctle_score,
    design_grid_search,
)

OUT    = Path("/home/patrick/mydocs/nuggets/ctle_optimization/figures")
OUT.mkdir(parents=True, exist_ok=True)

DATA_RATE    = 106.25e9
SPS          = 32
SAMPLE_RATE  = DATA_RATE * SPS
F_NYQ        = DATA_RATE / 2.0
BW_LIMIT_HZ  = 80e9
N_FREQ       = 4096
PLOT_F_MAX   = 100e9
N_UI         = 64

PEAKING_LEVELS = [3.0, 6.0, 9.0]
COLORS         = {3.0: "#1f77b4", 6.0: "#ff7f0e", 9.0: "#2ca02c"}
MODES          = [("LPM", 0, 0), ("DFE-4", 0, 4), ("FFE+DFE", 2, 4)]
MODE_COLORS    = {"LPM": "#1f77b4", "DFE-4": "#ff7f0e", "FFE+DFE": "#2ca02c"}
NOISE_RMS      = 0.01

# ── shared helpers ─────────────────────────────────────────────────────────────

def freq_response_sos(sos):
    w, H = sosfreqz(sos, worN=N_FREQ, fs=SAMPLE_RATE)
    mag_db = 20.0 * np.log10(np.maximum(np.abs(H), 1e-12))
    gd = np.zeros(N_FREQ)
    for sec in sos:
        _, g = group_delay((sec[:3], sec[3:]), w=N_FREQ, fs=SAMPLE_RATE)
        gd += g
    gd_ps = gd / SAMPLE_RATE * 1e12
    m = w <= PLOT_F_MAX
    return w[m], mag_db[m], gd_ps[m]

def bessel_sos(bw_factor, order=4):
    wn = bw_factor * F_NYQ / (SAMPLE_RATE / 2.0)
    b, a = bessel(N=order, Wn=min(wn, 0.9999), btype="low", analog=False, norm="mag")
    return tf2sos(b, a)

def get_ch_ir(bw_factor):
    ch = BesselChannel(bw_factor=bw_factor, order=4, data_rate=DATA_RATE,
                       samples_per_symbol=SPS)
    delta = np.zeros(N_UI * SPS); delta[0] = 1.0
    return ch.filter(delta)

SAVE_OPTS = dict(scale=2, width=900, height=500)

def save(fig, name):
    fig.write_image(str(OUT / f"{name}.png"), **SAVE_OPTS)
    print(f"  saved {name}.png")

# ══════════════════════════════════════════════════════════════════════════════
# Figure 1 — CTLE transfer function: magnitude + group delay
# ══════════════════════════════════════════════════════════════════════════════

print("Figure 1: CTLE transfer function")

fig1 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                     subplot_titles=["Magnitude  |H(f)| (dB)", "Group Delay (ps)"],
                     vertical_spacing=0.08)

for pk in PEAKING_LEVELS:
    color = COLORS[pk]
    # Unbounded
    ct = CtleZPK.from_peaking(pk, data_rate=DATA_RATE, samples_per_symbol=SPS)
    f, m, gd = freq_response_sos(ct.second_order_sections())
    fig1.add_trace(go.Scatter(x=f/1e9, y=m, name=f"{pk:.0f} dB",
                              line=dict(color=color, width=2), legendgroup=f"{pk}",
                              showlegend=True), row=1, col=1)
    fig1.add_trace(go.Scatter(x=f/1e9, y=gd, name=f"{pk:.0f} dB",
                              line=dict(color=color, width=2), legendgroup=f"{pk}",
                              showlegend=False), row=2, col=1)
    # BW-limited
    ct_bw = CtleZPK.from_peaking_with_bw_limit(pk, BW_LIMIT_HZ, 2,
                                                 data_rate=DATA_RATE,
                                                 samples_per_symbol=SPS)
    f_bw, m_bw, gd_bw = freq_response_sos(ct_bw.second_order_sections())
    fig1.add_trace(go.Scatter(x=f_bw/1e9, y=m_bw,
                              name=f"{pk:.0f} dB + BW limit",
                              line=dict(color=color, width=2, dash="dash"),
                              legendgroup=f"{pk}_bw", showlegend=True), row=1, col=1)
    fig1.add_trace(go.Scatter(x=f_bw/1e9, y=gd_bw,
                              name=f"{pk:.0f} dB + BW limit",
                              line=dict(color=color, width=2, dash="dash"),
                              legendgroup=f"{pk}_bw", showlegend=False), row=2, col=1)

# Reference lines
fig1.add_hline(y=0,  line=dict(color="gray", dash="dot",  width=1), row=1, col=1)
fig1.add_hline(y=-3, line=dict(color="gray", dash="dash", width=1), row=1, col=1)
for row in [1, 2]:
    fig1.add_vline(x=F_NYQ/1e9,      line=dict(color="black", dash="dot",  width=1), row=row, col=1)
    fig1.add_vline(x=BW_LIMIT_HZ/1e9, line=dict(color="gray",  dash="dash", width=1), row=row, col=1)

fig1.update_xaxes(title_text="Frequency (GHz)", range=[0, PLOT_F_MAX/1e9], row=2, col=1)
fig1.update_yaxes(title_text="|H(f)| (dB)", row=1, col=1)
fig1.update_yaxes(title_text="Group Delay (ps)", range=[-15, 15], row=2, col=1)
fig1.update_layout(template="plotly_white", height=600, width=900,
                   legend=dict(x=0.02, y=0.98, xanchor="left", yanchor="top"))
save(fig1, "ctle_transfer_function")

# ══════════════════════════════════════════════════════════════════════════════
# Figure 2 — C-metric illustration (annotated baud-rate pulse)
# ══════════════════════════════════════════════════════════════════════════════

print("Figure 2: C-metric illustration")

ch_ir  = get_ch_ir(0.75)
hint   = channel_cursor(ch_ir, SPS)
ct_opt = CtleZPK.from_peaking(9.0, data_rate=DATA_RATE, samples_per_symbol=SPS)
pulse, _ = baud_pulse_response(ch_ir, ct_opt, SPS, cursor_hint=hint)

# trim to window
WINDOW = 20
start = max(0, hint - 4)
pulse_w = pulse[start : start + WINDOW]
ui_w    = np.arange(len(pulse_w)) - (hint - start)

N_PRE, N_DFE = 2, 4
cursor_local = hint - start

fig2 = go.Figure()

# Colour the bars: uncancelled pre / FFE-cancelled pre / cursor /
#                  DFE-cancelled post / uncancelled post
BAR_COLORS = []
for i, u in enumerate(ui_w):
    if u < -N_PRE:
        BAR_COLORS.append("#d62728")   # uncancelled pre-ISI  (red)
    elif u < 0:
        BAR_COLORS.append("#aec7e8")   # FFE-cancelled        (light blue)
    elif u == 0:
        BAR_COLORS.append("#2ca02c")   # cursor h0            (green)
    elif u <= N_DFE:
        BAR_COLORS.append("#ffbb78")   # DFE-cancelled        (light orange)
    else:
        BAR_COLORS.append("#d62728")   # uncancelled post-ISI (red)

fig2.add_trace(go.Bar(x=ui_w, y=pulse_w, marker_color=BAR_COLORS,
                       name="Baud-rate pulse", showlegend=False))

# Noise floor band
sigma = NOISE_RMS * abs(pulse_w[cursor_local])
fig2.add_hrect(y0=-sigma, y1=sigma, fillcolor="rgba(180,180,180,0.3)",
               line_width=0, annotation_text="σ (noise)", annotation_position="right")

# Legend patches
for label, color in [
    ("Uncancelled ISI", "#d62728"),
    ("FFE pre-cursor (cancelled)", "#aec7e8"),
    ("Cursor h₀", "#2ca02c"),
    ("DFE post-cursor (cancelled)", "#ffbb78"),
]:
    fig2.add_trace(go.Bar(x=[None], y=[None], marker_color=color, name=label,
                          showlegend=True))

# h0 annotation
h0_val = pulse_w[cursor_local]
fig2.add_annotation(x=0, y=h0_val, text=f"<b>h₀</b>", showarrow=True,
                    arrowhead=2, ax=30, ay=-30, font=dict(size=14, color="#2ca02c"))

fig2.update_layout(
    title="C-metric: baud-rate pulse decomposition  (n_pre=2, n_dfe=4)",
    xaxis_title="UI (relative to cursor)",
    yaxis_title="Amplitude",
    xaxis=dict(range=[ui_w[0]-0.5, ui_w[-1]+0.5]),
    template="plotly_white", height=500, width=900,
    legend=dict(x=0.65, y=0.98, xanchor="left", yanchor="top"),
    barmode="relative",
)
save(fig2, "c_metric_illustration")

# ══════════════════════════════════════════════════════════════════════════════
# Figure 3 — C vs peaking_db for mild and lossy channels
# ══════════════════════════════════════════════════════════════════════════════

print("Figure 3: C vs peaking")

CHANNEL_CFGS = {
    "Mild (bw=0.75×Nyq)":  dict(bw_factor=0.75, f_z_ratio=0.25, pk_max=10.0),
    "Lossy (bw=0.40×Nyq)": dict(bw_factor=0.40, f_z_ratio=0.15, pk_max=14.0),
}

fig3 = make_subplots(rows=1, cols=2,
                     subplot_titles=list(CHANNEL_CFGS.keys()),
                     shared_yaxes=False)

for col, (ch_name, cfg) in enumerate(CHANNEL_CFGS.items(), 1):
    ir  = get_ch_ir(cfg["bw_factor"])
    hnt = channel_cursor(ir, SPS)
    pks = np.arange(1.0, cfg["pk_max"] + 0.5)
    cands = candidate_sweep_peaking(DATA_RATE, SPS, pks.tolist(),
                                    f_z_ratio=cfg["f_z_ratio"])
    pks = pks[:len(cands)]

    for label, n_pre, n_dfe in MODES:
        scores = []
        for ct in cands:
            p, _ = baud_pulse_response(ir, ct, SPS, cursor_hint=hnt)
            scores.append(ctle_score(p, hnt, n_pre, n_dfe, NOISE_RMS))

        best_idx = int(np.argmax(scores))
        fig3.add_trace(go.Scatter(x=pks, y=scores, name=label,
                                  mode="lines+markers",
                                  line=dict(color=MODE_COLORS[label], width=2),
                                  showlegend=(col == 1),
                                  legendgroup=label), row=1, col=col)
        fig3.add_trace(go.Scatter(x=[pks[best_idx]], y=[scores[best_idx]],
                                  mode="markers", showlegend=False,
                                  marker=dict(color=MODE_COLORS[label],
                                              size=12, symbol="star"),
                                  legendgroup=label), row=1, col=col)

    fig3.update_xaxes(title_text="CTLE Peaking (dB)", row=1, col=col)
    fig3.update_yaxes(title_text="C", row=1, col=col)

fig3.update_layout(template="plotly_white", height=480, width=900,
                   legend=dict(x=0.02, y=0.98, xanchor="left", yanchor="top"))
save(fig3, "c_vs_peaking")

# ══════════════════════════════════════════════════════════════════════════════
# Figure 4 — Equalization effect: channel / CTLE / combined magnitude
# ══════════════════════════════════════════════════════════════════════════════

print("Figure 4: Equalization effect")

def cascade(s1, s2): return np.vstack([s1, s2])

sos_ch = bessel_sos(0.75)
f_ch, m_ch, _ = freq_response_sos(sos_ch)

fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=f_ch/1e9, y=m_ch, name="Channel (Bessel bw=0.75)",
                           line=dict(color="black", width=2.5)))

for pk in PEAKING_LEVELS:
    color = COLORS[pk]
    ct = CtleZPK.from_peaking(pk, data_rate=DATA_RATE, samples_per_symbol=SPS)
    sos_ct = ct.second_order_sections()
    f_ct, m_ct, _ = freq_response_sos(sos_ct)
    f_cb, m_cb, _ = freq_response_sos(cascade(sos_ch, sos_ct))

    fig4.add_trace(go.Scatter(x=f_ct/1e9, y=m_ct, name=f"CTLE {pk:.0f} dB",
                               line=dict(color=color, width=1.5, dash="dot")))
    fig4.add_trace(go.Scatter(x=f_cb/1e9, y=m_cb, name=f"Combined {pk:.0f} dB",
                               line=dict(color=color, width=2.5)))

fig4.add_hline(y=0,  line=dict(color="gray", dash="dot",  width=1))
fig4.add_vline(x=F_NYQ/1e9, line=dict(color="gray", dash="dash", width=1),
               annotation_text="f_Nyq", annotation_position="top right")

fig4.update_layout(
    title="Channel, CTLE, and combined magnitude response (Bessel bw=0.75, 106.25 GBd)",
    xaxis_title="Frequency (GHz)", xaxis=dict(range=[0, PLOT_F_MAX/1e9]),
    yaxis_title="|H(f)| (dB)",
    template="plotly_white", height=500, width=900,
    legend=dict(x=0.02, y=0.02, xanchor="left", yanchor="bottom"),
)
save(fig4, "equalization_effect")

# ══════════════════════════════════════════════════════════════════════════════
# Figure 5 — Baud-rate pulse: unequalized vs optimal CTLE per mode
# ══════════════════════════════════════════════════════════════════════════════

print("Figure 5: Baud-rate pulse")

ch_ir = get_ch_ir(0.75)
hint  = channel_cursor(ch_ir, SPS)
base_pulse, _ = baud_pulse_response(ch_ir, None, SPS, cursor_hint=hint)
ui_base = np.arange(len(base_pulse)) - hint

fig5 = go.Figure()
fig5.add_trace(go.Scatter(
    x=ui_base, y=base_pulse, name="No CTLE",
    mode="lines+markers", marker=dict(size=5),
    line=dict(color="black", width=2, dash="dash")))

cands_mild = candidate_sweep_peaking(DATA_RATE, SPS, np.arange(1.0, 11.0).tolist())
for label, n_pre, n_dfe in MODES:
    best_score, best_ct = -np.inf, None
    for ct in cands_mild:
        p, _ = baud_pulse_response(ch_ir, ct, SPS, cursor_hint=hint)
        s = ctle_score(p, hint, n_pre, n_dfe, NOISE_RMS)
        if s > best_score:
            best_score, best_ct = s, ct
    pk_best = round(best_ct.zeros[0] / (F_NYQ * 0.25) * 3)  # rough label
    p_best, _ = baud_pulse_response(ch_ir, best_ct, SPS, cursor_hint=hint)
    ui_best = np.arange(len(p_best)) - hint
    # Find actual peaking: check all candidates
    for pk, ct in zip(np.arange(1.0, 11.0), cands_mild):
        if ct is best_ct:
            pk_best = float(pk)
            break
    fig5.add_trace(go.Scatter(
        x=ui_best, y=p_best,
        name=f"{label} (opt {pk_best:.0f} dB)",
        mode="lines+markers", marker=dict(size=5),
        line=dict(color=MODE_COLORS[label], width=2)))

fig5.update_layout(
    title="Baud-rate pulse response — Bessel bw=0.75, optimal CTLE per mode",
    xaxis_title="UI (relative to cursor)", yaxis_title="Amplitude",
    xaxis=dict(range=[-4, 18]),
    template="plotly_white", height=500, width=900,
    legend=dict(x=0.65, y=0.98, xanchor="left", yanchor="top"),
)
save(fig5, "baud_pulse_comparison")

print("\nAll figures generated.")
