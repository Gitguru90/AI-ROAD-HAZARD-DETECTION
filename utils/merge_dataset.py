"""
Utility script to merge Pothole (Class 0) and Speed Breaker (Class 1) datasets safely.
"""
import os
import shutil
import argparse
from pathlib import Path

def copy_dataset_split(src_dir, dst_dir, prefix=""):
    src_images = Path(src_dir) / "images"
    src_labels = Path(src_dir) / "labels"
    dst_images = Path(dst_dir) / "images"
    dst_labels = Path(dst_dir) / "labels"

    dst_images.mkdir(parents=True, exist_ok=True)
    dst_labels.mkdir(parents=True, exist_ok=True)

    if not src_images.exists():
        print(f"Warning: {src_images} does not exist.")
        return 0

    copied = 0
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp"}
    for img_file in src_images.iterdir():
        if img_file.suffix.lower() in valid_exts:
            new_stem = f"{prefix}_{img_file.stem}" if prefix else img_file.stem
            new_img_name = f"{new_stem}{img_file.suffix}"
            shutil.copy2(img_file, dst_images / new_img_name)

            label_file = src_labels / f"{img_file.stem}.txt"
            if label_file.exists():
                shutil.copy2(label_file, dst_labels / f"{new_stem}.txt")
            else:
                # Create empty label file if missing
                (dst_labels / f"{new_stem}.txt").touch()
            copied += 1
    return copied

def merge_datasets(pothole_dir, speed_breaker_dir, output_dir):
    out_path = Path(output_dir)
    print(f"Merging datasets into {out_path}...")
    
    for split in ["train", "valid"]:
        print(f"Processing split: {split}")
        p_count = copy_dataset_split(Path(pothole_dir) / split, out_path / split, prefix="pothole")
        s_count = copy_dataset_split(Path(speed_breaker_dir) / split, out_path / split, prefix="speed_breaker")
        print(f"  Split {split}: {p_count} Pothole items, {s_count} Speed Breaker items merged.")

    print("Dataset merge completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge Pothole and Speed Breaker Datasets")
    parser.add_argument("--pothole-dir", required=True, help="Path to Pothole dataset root")
    parser.add_argument("--sb-dir", required=True, help="Path to Speed Breaker dataset root")
    parser.add_argument("--output-dir", required=True, help="Path to output merged dataset directory")
    args = parser.parse_args()
    merge_datasets(args.pothole_dir, args.sb_dir, args.output_dir)
