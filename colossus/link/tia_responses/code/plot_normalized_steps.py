import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import re
from pathlib import Path

UI = 1 / 106.25e9

def get_crossing_time(t, y, level, rising):
    if rising: idx = np.where(y >= level)[0]
    else: idx = np.where(y <= level)[0]
    if len(idx) == 0: return np.nan
    idx = idx[0]
    if idx == 0: return t[0]
    t0, t1 = t[idx-1], t[idx]
    y0, y1 = y[idx-1], y[idx]
    if y1 == y0: return t0
    return t0 + (t1 - t0) * (level - y0) / (y1 - y0)

def main():
    base_dir = "temp/data/step_response"
    csv_files = glob.glob(f"{base_dir}/**/*.csv", recursive=True)
    col_pattern = re.compile(r"vswing=([\d.]+).*?isign=(-?1)")
    
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        rel_path = os.path.relpath(csv_file, base_dir)
        dir_name = os.path.dirname(rel_path)
        output_dir = os.path.join("temp/plots_norm", dir_name)
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = Path(csv_file).stem
        
        pos_cols = []
        neg_cols = []
        
        for i in range(0, len(df.columns), 2):
            x_col = df.columns[i]
            y_col = df.columns[i+1]
            m = col_pattern.search(x_col)
            if not m: continue
            vswing = float(m.group(1))
            isign = int(m.group(2))
            
            if isign == 1: pos_cols.append((vswing, x_col, y_col))
            else: neg_cols.append((vswing, x_col, y_col))
            
        def plot_normalized(cols, pol):
            if not cols: return
            cols.sort(key=lambda x: x[0])
            
            plt.figure(figsize=(10, 6))
            isign_val = 1 if pol == "positive" else -1
            
            for vswing, x_col, y_col in cols:
                x_data = pd.to_numeric(df[x_col], errors='coerce').values
                y_data = pd.to_numeric(df[y_col], errors='coerce').values
                
                mask = ~(np.isnan(x_data) | np.isnan(y_data))
                x = x_data[mask]
                y = y_data[mask]
                
                if len(x) < 10: continue
                x, unique_idx = np.unique(x, return_index=True)
                y = y[unique_idx]
                
                baseline = np.mean(y[:max(1, len(y)//20)])
                steady_state = np.mean(y[-max(1, len(y)//20):])
                
                step_amp = steady_state - baseline
                lvl10 = baseline + 0.1 * step_amp
                rising = step_amp > 0
                
                t10 = get_crossing_time(x, y, lvl10, rising)
                if np.isnan(t10): t10 = x[0]
                
                t_aligned = (x - t10) / UI
                
                # Normalize so that both positive and negative steps swing upwards,
                # and scale by the input vswing. If linear, all curves will overlay perfectly.
                y_norm = (y - baseline) / (vswing * isign_val)
                
                plt.plot(t_aligned, y_norm, label=f"Vswing = {vswing}")
                
            plt.title(f"Normalized Step Responses - {base_name} ({pol})\nAligned to 10% crossing")
            plt.xlabel("Time relative to 10% crossing (UI)")
            plt.ylabel("Normalized Amplitude (y - baseline) / input_step")
            plt.grid(True)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.xlim(-5, 30) # View a reasonable window around the step
            plt.tight_layout()
            
            out_file = os.path.join(output_dir, f"{base_name}_{pol}_norm.png")
            plt.savefig(out_file)
            plt.close()
            print(f"Saved: {out_file}")
            
        plot_normalized(pos_cols, "positive")
        plot_normalized(neg_cols, "negative")

if __name__ == "__main__":
    main()
