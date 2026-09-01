"""
Utility script to validate dataset integrity, labels, bounding box coordinates, and counts.
"""
import os
import argparse
from pathlib import Path

def validate_dataset(dataset_dir):
    root = Path(dataset_dir)
    if not root.exists():
        print(f"Error: Dataset directory '{dataset_dir}' does not exist.")
        return

    print(f"\n==========================================")
    print(f"  DATASET VALIDATION REPORT: {dataset_dir}")
    print(f"==========================================\n")

    total_images = 0
    total_labels = 0
    missing_labels = 0
    invalid_labels = 0
    empty_labels = 0
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp"}

    for split in ["train", "valid", "val", "test"]:
        split_dir = root / split
        if not split_dir.exists():
            continue
        
        img_dir = split_dir / "images"
        lbl_dir = split_dir / "labels"

        if not img_dir.exists():
            continue

        images = [f for f in img_dir.iterdir() if f.suffix.lower() in valid_exts]
        total_images += len(images)

        for img in images:
            lbl_path = lbl_dir / f"{img.stem}.txt"
            if not lbl_path.exists():
                missing_labels += 1
                continue
            
            total_labels += 1
            with open(lbl_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            if not lines:
                empty_labels += 1
                continue

            for line_idx, line in enumerate(lines):
                parts = line.strip().split()
                if len(parts) != 5:
                    invalid_labels += 1
                    continue
                
                try:
                    cls_id = int(parts[0])
                    xc, yc, w, h = map(float, parts[1:])
                    if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0 and 0.0 <= w <= 1.0 and 0.0 <= h <= 1.0):
                        invalid_labels += 1
                    if cls_id not in [0, 1]:
                        print(f"Notice: Non-standard Class ID {cls_id} found in {lbl_path.name}")
                except ValueError:
                    invalid_labels += 1

    print(f"Total Images Checked : {total_images}")
    print(f"Total Labels Found  : {total_labels}")
    print(f"Missing Label Files : {missing_labels}")
    print(f"Empty Label Files   : {empty_labels}")
    print(f"Invalid Bounding Box: {invalid_labels}")
    print("------------------------------------------")
    if missing_labels == 0 and invalid_labels == 0:
        print("Status: 🟢 DATASET IS VALID AND READY FOR YOLO TRAINING")
    else:
        print("Status: ⚠️ ISSUES DETECTED - PLEASE REVIEW LOGS ABOVE")
    print("==========================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate YOLO dataset")
    parser.add_argument("--dataset-dir", required=True, help="Path to YOLO dataset root directory")
    args = parser.parse_args()
    validate_dataset(args.dataset_dir)
