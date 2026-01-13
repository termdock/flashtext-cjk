
import json
import matplotlib.pyplot as plt
import pandas as pd
import os

RESULTS_FILE = "benchmarks/results.json"
OUTPUT_DIR = "benchmarks/report"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def load_results():
    with open(RESULTS_FILE, 'r') as f:
        return json.load(f)

def generate_charts(data):
    df = pd.DataFrame(data)
    
    # 1. Build Time
    build_df = df[df['metric'] == 'Build']
    plt.figure(figsize=(10, 6))
    for engine in build_df['engine'].unique():
        subset = build_df[build_df['engine'] == engine]
        plt.plot(subset['terms'], subset['median'], marker='o', label=engine)
    
    plt.title('Build Time vs Number of Terms')
    plt.xlabel('Terms')
    plt.ylabel('Time (s)')
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{OUTPUT_DIR}/build_time.png")
    
    # 2. Match Time (Split by Corpus)
    match_df = df[df['metric'] == 'Match']
    corpora = match_df['corpus'].unique()
    
    for corpus in corpora:
        plt.figure(figsize=(10, 6))
        subset_c = match_df[match_df['corpus'] == corpus]
        for engine in subset_c['engine'].unique():
            subset_e = subset_c[subset_c['engine'] == engine]
            plt.plot(subset_e['terms'], subset_e['median'], marker='o', label=engine)
            
        plt.title(f'Match Time - {corpus}')
        plt.xlabel('Terms')
        plt.ylabel('Time (s)')
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{OUTPUT_DIR}/match_time_{corpus}.png")
        
        # 3. Match Time (No Regex) - Zoomed In
        plt.figure(figsize=(10, 6))
        subset_c_no_re = subset_c[subset_c['engine'] != 'Regex']
        for engine in subset_c_no_re['engine'].unique():
            subset_e = subset_c_no_re[subset_c_no_re['engine'] == engine]
            plt.plot(subset_e['terms'], subset_e['median'], marker='o', label=engine)
            
        plt.title(f'Match Time (Rust vs Python) - {corpus}')
        plt.xlabel('Terms')
        plt.ylabel('Time (s)')
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{OUTPUT_DIR}/match_time_{corpus}_no_regex.png")

def generate_markdown(data):
    df = pd.DataFrame(data)
    md = "# Benchmark Report\n\n"
    
    # Environment
    md += "## Environment\n"
    # (Placeholder, ideally gather from platform module)
    md += "- OS: macOS\n- Arch: ARM64\n\n"
    
    # Summary Tables
    md += "## Results\n\n"
    
    # Pivot Build
    build_df = df[df['metric'] == 'Build'][['engine', 'terms', 'median', 'p95']]
    md += "### Build Time (s)\n\n"
    md += build_df.to_markdown(index=False) + "\n\n"
    
    # Pivot Match
    match_df = df[df['metric'] == 'Match'][['engine', 'terms', 'corpus', 'median', 'p95', 'count']]
    md += "### Match Time (s)\n\n"
    md += match_df.to_markdown(index=False) + "\n\n"
    
    with open(f"{OUTPUT_DIR}/REPORT.md", 'w') as f:
        f.write(md)
    print(f"Report saved to {OUTPUT_DIR}/REPORT.md")

def main():
    try:
        data = load_results()
        generate_charts(data)
        generate_markdown(data)
    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    main()
