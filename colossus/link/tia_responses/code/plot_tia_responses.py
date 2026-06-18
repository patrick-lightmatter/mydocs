import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from pathlib import Path

def plot_csv_data(csv_file, output_dir):
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return

    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(csv_file).stem
    
    # We will create two plots: one for positive steps (isign=1) and one for negative steps (isign=-1)
    # If a column doesn't have isign, we might just put it in a generic plot, but let's try to split based on isign.
    
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
            # If it doesn't specify, we can just put it in both or positive by default
            pos_cols.append((x_col, y_col))

    def _plot_subset(cols, suffix, title_suffix):
        if not cols:
            return
        
        plt.figure(figsize=(10, 6))
        
        count = 0
        for x_col, y_col in cols:
            if count >= 20:
                break
            label = x_col.replace(' X', '')
            
            x_data = pd.to_numeric(df[x_col], errors='coerce')
            y_data = pd.to_numeric(df[y_col], errors='coerce')
            
            plt.plot(x_data, y_data, label=label)
            count += 1

        plt.title(f"Responses from {base_name} ({title_suffix})")
        plt.xlabel("Time (s)")
        plt.ylabel("Value")
        plt.grid(True)
        
        if len(cols) <= 20:
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
            
        plt.tight_layout()
        
        out_file = os.path.join(output_dir, f"{base_name}_{suffix}.png")
        plt.savefig(out_file)
        plt.close()
        print(f"Saved plot: {out_file}")

    _plot_subset(pos_cols, "positive", "Positive Steps")
    _plot_subset(neg_cols, "negative", "Negative Steps")

def main():
    base_dir = "temp/data"
    
    # Find CSV files only in specific directories
    csv_files = []
    for sub_dir in ["single_bit_response", "step_response"]:
        csv_files.extend(glob.glob(f"{base_dir}/{sub_dir}/**/*.csv", recursive=True))
    
    for csv_file in csv_files:
        rel_path = os.path.relpath(csv_file, base_dir)
        dir_name = os.path.dirname(rel_path)
        
        output_dir = os.path.join("temp/plots", dir_name)
        plot_csv_data(csv_file, output_dir)

if __name__ == "__main__":
    main()
