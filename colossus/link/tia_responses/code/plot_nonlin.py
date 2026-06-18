import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import re
from pathlib import Path

def get_crossing_time(t, y, level, rising):
    if rising:
        idx = np.where(y >= level)[0]
    else:
        idx = np.where(y <= level)[0]
        
    if len(idx) == 0:
        return np.nan
        
    idx = idx[0]
    if idx == 0:
        return t[0]
        
    # Interpolate
    t0, t1 = t[idx-1], t[idx]
    y0, y1 = y[idx-1], y[idx]
    if y1 == y0:
        return t0
    
    return t0 + (t1 - t0) * (level - y0) / (y1 - y0)

def extract_metrics(t, y, vswing):
    mask = ~(np.isnan(t) | np.isnan(y))
    t = t[mask]
    y = y[mask]
    
    if len(t) < 10:
        return np.nan, np.nan, np.nan
        
    t, unique_idx = np.unique(t, return_index=True)
    y = y[unique_idx]
    
    # Estimate baseline from first 5% of samples
    baseline = np.mean(y[:max(1, len(y)//20)])
    # Estimate steady state from last 5% of samples
    steady_state = np.mean(y[-max(1, len(y)//20):])
    
    step_amplitude = steady_state - baseline
    
    # 1. Steady State Gain = (Actual Output Step Amplitude) / (Input Vswing)
    steady_state_gain = abs(step_amplitude) / vswing
    
    # 2. Rise time (10-90%)
    lvl10 = baseline + 0.1 * step_amplitude
    lvl90 = baseline + 0.9 * step_amplitude
    rising = step_amplitude > 0
    t10 = get_crossing_time(t, y, lvl10, rising)
    t90 = get_crossing_time(t, y, lvl90, rising)
    rise_time = t90 - t10
    
    # 3. Overshoot (%)
    if rising:
        peak_val = np.max(y)
        overshoot = max(0, peak_val - steady_state) / abs(step_amplitude) * 100
    else:
        peak_val = np.min(y)
        overshoot = max(0, steady_state - peak_val) / abs(step_amplitude) * 100

    return rise_time, steady_state_gain, overshoot

def main():
    base_dir = "temp/data/step_response"
    csv_files = glob.glob(f"{base_dir}/**/*.csv", recursive=True)
    col_pattern = re.compile(r"vswing=([\d.]+).*?isign=(-?1)")
    
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        rel_path = os.path.relpath(csv_file, base_dir)
        dir_name = os.path.dirname(rel_path)
        output_dir = os.path.join("temp/plots_nonlin", dir_name)
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = Path(csv_file).stem
        pos_data, neg_data = [], []
        
        num_cols = len(df.columns)
        for i in range(0, num_cols, 2):
            x_col = df.columns[i]; y_col = df.columns[i+1]
            m = col_pattern.search(x_col)
            if not m: continue
                
            vswing = float(m.group(1))
            isign = int(m.group(2))
            
            x_data = pd.to_numeric(df[x_col], errors='coerce').values
            y_data = pd.to_numeric(df[y_col], errors='coerce').values
            
            tr, gain, over = extract_metrics(x_data, y_data, vswing)
            
            if isign == 1:
                pos_data.append((vswing, tr, gain, over))
            else:
                neg_data.append((vswing, tr, gain, over))
                
        def plot_polarity(data, pol):
            if not data: return
            
            data.sort(key=lambda x: x[0])
            vswings = [x[0] for x in data]
            trs_ps = [x[1] * 1e12 for x in data]
            gains = [x[2] for x in data]
            overshoots = [x[3] for x in data]
            
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 12))
            
            ax1.plot(vswings, trs_ps, marker='o', color='b')
            ax1.set_title("10-90% Rise Time vs Vswing")
            ax1.set_ylabel("Rise Time (ps)"); ax1.grid(True)
            
            ax2.plot(vswings, gains, marker='o', color='g')
            ax2.set_title("Steady State Gain vs Vswing")
            ax2.set_ylabel("Gain (V/V)"); ax2.grid(True)
            
            ax3.plot(vswings, overshoots, marker='o', color='r')
            ax3.set_title("Overshoot % vs Vswing")
            ax3.set_xlabel("Vswing"); ax3.set_ylabel("Overshoot (%)"); ax3.grid(True)
            
            fig.suptitle(f"Non-linearity Analysis - {base_name} ({pol})")
            fig.tight_layout()
            
            out_file = os.path.join(output_dir, f"{base_name}_{pol}_nonlin.png")
            fig.savefig(out_file)
            plt.close(fig)
            print(f"Saved: {out_file}")
            
        plot_polarity(pos_data, "positive")
        plot_polarity(neg_data, "negative")

if __name__ == "__main__":
    main()
