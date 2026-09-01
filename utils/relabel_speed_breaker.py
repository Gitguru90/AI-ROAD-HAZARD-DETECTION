"""
Utility script to convert speed breaker dataset labels from class 0 to class 1.
Usage: python relabel_speed_breaker.py --labels-dir path/to/speed_breaker/labels
"""
import os
import argparse
from pathlib import Path

def relabel_speed_breaker_dir(labels_dir):
    labels_path = Path(labels_dir)
    if not labels_path.exists():
        print(f"Error: Directory '{labels_dir}' does not exist.")
        return 0

    count = 0
    txt_files = list(labels_path.glob("*.txt"))
    for file in txt_files:
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = []
        modified = False
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 5:
                if parts[0] == "0":
                    parts[0] = "1"
                    modified = True
                new_lines.append(" ".join(parts) + "\n")
            else:
                new_lines.append(line)
        
        if modified:
            with open(file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            count += 1

    print(f"Successfully relabeled {count} text files in {labels_dir}.")
    return count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Relabel speed breaker class 0 to 1")
    parser.add_argument("--labels-dir", required=True, help="Path to labels directory")
    args = parser.parse_args()
    relabel_speed_breaker_dir(args.labels_dir)
