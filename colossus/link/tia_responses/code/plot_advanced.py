import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from pathlib import Path
from scipy.interpolate import interp1d

UI = 1 / 106.25e9
DT = UI / 32

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

def get_freq_response(t, h):
    N = len(h)
    N_pad = max(N, 16384)
    H = np.fft.fft(h, n=N_pad) * DT
    f = np.fft.fftfreq(N_pad, d=DT)
    
    pos_idx = (f > 0) & (f < 150e9)
    f_pos = f[pos_idx]
    H_pos = H[pos_idx]
    
    mag_db = 20 * np.log10(np.abs(H_pos) + 1e-12)
    phase = np.unwrap(np.angle(H_pos))
    
    omega = 2 * np.pi * f_pos
    phase_delay = -phase / omega
    # Replace NaN or inf group delay at edges with 0 just in case
    group_delay = -np.gradient(phase, omega)
    
    return f_pos, mag_db, phase, group_delay, phase_delay

def process_csv(csv_file, output_dir, is_step):
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
            
        fig_time, axes_time = plt.subplots(2 if is_step else 1, 1, figsize=(10, 8 if is_step else 5))
        if not is_step:
            axes_time = [axes_time]
            
        fig_freq, axes_freq = plt.subplots(2, 2, figsize=(12, 8))
        ax_mag, ax_phase = axes_freq[0]
        ax_gd, ax_pd = axes_freq[1]
        
        count = 0
        for x_col, y_col in cols:
            if count >= 10: 
                break
            label = x_col.replace(' X', '')
            
            x_data = pd.to_numeric(df[x_col], errors='coerce').values
            y_data = pd.to_numeric(df[y_col], errors='coerce').values
            
            t_res, y_res = resample_waveform(x_data, y_data)
            if len(t_res) == 0:
                continue
                
            t_ui = t_res / UI
                
            if is_step:
                axes_time[0].plot(t_ui, y_res, label=label)
                dy = np.gradient(y_res, DT)
                axes_time[1].plot(t_ui, dy, label=label)
                f_pos, mag_db, phase, gd, pd_delay = get_freq_response(t_res, dy)
            else:
                axes_time[0].plot(t_ui, y_res, label=label)
                f_pos, mag_db, phase, gd, pd_delay = get_freq_response(t_res, y_res)
                
            f_ghz = f_pos / 1e9
            ax_mag.plot(f_ghz, mag_db, label=label)
            ax_phase.plot(f_ghz, phase, label=label)
            ax_gd.plot(f_ghz, gd * 1e12, label=label)
            ax_pd.plot(f_ghz, pd_delay * 1e12, label=label)
            
            count += 1
            
        axes_time[0].set_title(f"{base_name} ({polarity}) - Time Domain")
        axes_time[0].set_xlabel("Time (UI)")
        axes_time[0].set_ylabel("Amplitude")
        axes_time[0].grid(True)
        if len(cols) <= 10:
            axes_time[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
            
        if is_step:
            axes_time[1].set_title("Derivative (Impulse Response)")
            axes_time[1].set_xlabel("Time (UI)")
            axes_time[1].set_ylabel("Amplitude/s")
            axes_time[1].grid(True)
            
        fig_time.tight_layout()
        out_time = os.path.join(output_dir, f"{base_name}_{polarity}_time.png")
        fig_time.savefig(out_time)
        plt.close(fig_time)
        
        ax_mag.set_title("Magnitude")
        ax_mag.set_xlabel("Frequency (GHz)")
        ax_mag.set_ylabel("Magnitude (dB)")
        ax_mag.grid(True)
        
        ax_phase.set_title("Phase")
        ax_phase.set_xlabel("Frequency (GHz)")
        ax_phase.set_ylabel("Phase (rad)")
        ax_phase.grid(True)
        
        ax_gd.set_title("Group Delay")
        ax_gd.set_xlabel("Frequency (GHz)")
        ax_gd.set_ylabel("Group Delay (ps)")
        ax_gd.grid(True)
        
        ax_pd.set_title("Phase Delay")
        ax_pd.set_xlabel("Frequency (GHz)")
        ax_pd.set_ylabel("Phase Delay (ps)")
        ax_pd.grid(True)
        
        if len(cols) <= 10:
            ax_mag.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
            
        fig_freq.suptitle(f"{base_name} ({polarity}) - Frequency Domain")
        fig_freq.tight_layout()
        out_freq = os.path.join(output_dir, f"{base_name}_{polarity}_freq.png")
        fig_freq.savefig(out_freq)
        plt.close(fig_freq)

    _plot_subset(pos_cols, "positive")
    _plot_subset(neg_cols, "negative")

def main():
    base_dir = "temp/data"
    for sub_dir in ["single_bit_response", "step_response"]:
        is_step = (sub_dir == "step_response")
        csv_files = glob.glob(f"{base_dir}/{sub_dir}/**/*.csv", recursive=True)
        for csv_file in csv_files:
            rel_path = os.path.relpath(csv_file, base_dir)
            dir_name = os.path.dirname(rel_path)
            output_dir = os.path.join("temp/plots_advanced", dir_name)
            process_csv(csv_file, output_dir, is_step)

if __name__ == "__main__":
    main()
