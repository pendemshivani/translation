# preprocess.py
import pandas as pd
import argparse
import os
from sklearn.model_selection import train_test_split

def preprocess(input_file, out_dir="processed", en_col="English", te_col="Telugu", test_size=0.1, val_size=0.1, random_state=42):
    # Load CSV (ensure UTF-8)
    df = pd.read_csv(input_file)
    
    # Check for required columns
    if en_col not in df.columns or te_col not in df.columns:
        raise ValueError(f"CSV must have '{en_col}' and '{te_col}' columns. Found: {df.columns.tolist()}")
    
    # Strip whitespace and convert to string
    df['en'] = df[en_col].astype(str).apply(lambda x: x.strip())
    df['te'] = df[te_col].astype(str).apply(lambda x: x.strip())
    
    # Drop empty rows
    df = df[(df['en'] != "") & (df['te'] != "")]
    
    # Split into train, validation, test
    train_df, temp_df = train_test_split(df, test_size=test_size+val_size, random_state=random_state)
    val_df, test_df = train_test_split(temp_df, test_size=test_size/(test_size+val_size), random_state=random_state)
    
    # Create output directory if it doesn't exist
    os.makedirs(out_dir, exist_ok=True)
    
    # Save as TSV with columns 'en' and 'te'
    train_df[['en', 'te']].to_csv(os.path.join(out_dir, 'train.tsv'), sep='\t', index=False)
    val_df[['en', 'te']].to_csv(os.path.join(out_dir, 'val.tsv'), sep='\t', index=False)
    test_df[['en', 'te']].to_csv(os.path.join(out_dir, 'test.tsv'), sep='\t', index=False)
    
    print(f"Preprocessing completed. Files saved in {out_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess translation dataset")
    parser.add_argument("--input", type=str, required=True, help="Path to input CSV file")
    parser.add_argument("--out_dir", type=str, default="processed", help="Output directory for processed files (default: processed)")
    parser.add_argument("--en_col", type=str, default="English", help="Column name for English text")
    parser.add_argument("--te_col", type=str, default="Telugu", help="Column name for Telugu text")
    args = parser.parse_args()
    
    preprocess(args.input, args.out_dir, en_col=args.en_col, te_col=args.te_col)
