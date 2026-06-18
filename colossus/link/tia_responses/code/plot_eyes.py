import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from pathlib import Path
from scipy.interpolate import interp1d

UI = 1 / 106.25e9
SPS = 32
DT = UI / SPS

def resample_waveform(x, y):
    mask = ~(np.isnan(x) | np.isnan(y))
    x = x[mask]
    y = y[mask]
    if len(x) < 2:
        return np.array([]), np.array([])
    x, unique_idx = np.unique(x, return_index=True)
    y = y[unique_idx]
    
    t_new = np.arange(x[0], x[-1], DT)
    # Using linear interpolation to avoid ringing on sharp edges (like the Ipd stimulus)
    f = interp1d(x, y, kind='linear', fill_value="extrapolate")
    y_new = f(t_new)
    return t_new, y_new

def generate_eye(sbr):
    # SBR is the single bit response
    N_symbols = 2000
    symbols = np.random.choice([-3, -1, 1, 3], size=N_symbols)
    
    # Upsample by SPS
    symbols_up = np.zeros(N_symbols * SPS)
    symbols_up[::SPS] = symbols
    
    # Extract DC baseline to prevent it from being integrated by the convolution
    baseline = sbr[0]
    sbr_ac = sbr - baseline
    
    # Convolve to create continuous waveform and restore the DC baseline
    waveform = np.convolve(symbols_up, sbr_ac, mode='full') + baseline
    
    # Skip the transient part at the beginning (e.g., 50 symbols)
    start_idx = 50 * SPS
    end_idx = len(waveform) - 2 * SPS
    
    # We will overlay 2-UI segments
    t_ui = np.linspace(0, 2, 2 * SPS, endpoint=False)
    
    segments = []
    for i in range(start_idx, min(end_idx, start_idx + 1000 * SPS), SPS):
        segments.append(waveform[i : i + 2 * SPS])
        
    return t_ui, np.array(segments)

def process_csv(csv_file, output_dir):
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return

    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(csv_file).stem
    
    pos_cols = []
    neg_cols = []
    
    num_cols = len(df.columns)
    for i in range(0, num_cols, 2):
        x_col = df.columns[i]
        y_col = df.columns[i+1]
        
        if 'isign=1' in x_col:
            pos_cols.append((x_col, y_col))
        elif 'isign=-1' in x_col:
            neg_cols.append((x_col, y_col))
        else:
            pos_cols.append((x_col, y_col))

    def _plot_subset(cols, polarity):
        if not cols:
            return
            
        fig, axes = plt.subplots(len(cols), 1, figsize=(8, 3 * len(cols)))
        if len(cols) == 1:
            axes = [axes]
            
        count = 0
        for ax, (x_col, y_col) in zip(axes, cols):
            if count >= 10: 
                break
            label = x_col.replace(' X', '')
            
            x_data = pd.to_numeric(df[x_col], errors='coerce').values
            y_data = pd.to_numeric(df[y_col], errors='coerce').values
            
            t_res, y_res = resample_waveform(x_data, y_data)
            if len(t_res) == 0:
                continue
                
            t_ui, segments = generate_eye(y_res)
            
            # Plot segments
            for seg in segments:
                ax.plot(t_ui, seg, color='b', alpha=0.05, linewidth=0.5)
                
            ax.set_title(f"Eye Diagram: {label}")
            ax.set_xlabel("Time (UI)")
            ax.set_ylabel("Amplitude")
            ax.grid(True)
            
            count += 1
            
        fig.suptitle(f"{base_name} ({polarity}) - PAM4 Eye Diagrams")
        fig.tight_layout()
        out_file = os.path.join(output_dir, f"{base_name}_{polarity}_eye.png")
        fig.savefig(out_file)
        plt.close(fig)
        print(f"Saved: {out_file}")

    # Only process a small number of columns to keep the plots readable
    _plot_subset(pos_cols[:5], "positive")
    _plot_subset(neg_cols[:5], "negative")

def main():
    base_dir = "temp/data/single_bit_response"
    csv_files = glob.glob(f"{base_dir}/**/*.csv", recursive=True)
    
    for csv_file in csv_files:
        rel_path = os.path.relpath(csv_file, base_dir)
        dir_name = os.path.dirname(rel_path)
        output_dir = os.path.join("temp/plots_eyes/single_bit_response", dir_name)
        process_csv(csv_file, output_dir)

if __name__ == "__main__":
    np.random.seed(42) # For reproducible random sequences
    main()
