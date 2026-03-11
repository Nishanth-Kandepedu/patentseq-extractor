#!/usr/bin/env python3
"""
Batch Patent Antibody Sequence Extractor

Simple script to process a list of mixed-format patent IDs and export to CSV/Excel.
Perfect for processing your patent ID list.
"""

import pandas as pd
import sys
import os
from enhanced_patent_extractor import EnhancedPatentExtractor

def load_patent_ids_from_file(filename):
    """Load patent IDs from various file formats"""
    if filename.endswith('.csv'):
        # Try to read CSV - assume patent IDs are in first column
        df = pd.read_csv(filename)
        return df.iloc[:, 0].astype(str).tolist()
    elif filename.endswith(('.txt', '.text')):
        # Read text file - one patent ID per line
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    elif filename.endswith(('.xlsx', '.xls')):
        # Read Excel file - assume patent IDs are in first column
        df = pd.read_excel(filename)
        return df.iloc[:, 0].astype(str).tolist()
    else:
        raise ValueError("Unsupported file format. Use CSV, TXT, or Excel files.")

def process_patent_list(patent_ids, output_filename=None):
    """Process a list of patent IDs and export results"""
    
    print(f"🧬 Processing {len(patent_ids)} patent IDs...")
    print("-" * 50)
    
    # Initialize extractor
    extractor = EnhancedPatentExtractor()
    
    # Show normalization preview
    print("📋 Patent ID Normalization Preview:")
    for i, patent_id in enumerate(patent_ids[:10]):  # Show first 10
        normalized, _ = extractor.normalize_patent_id(patent_id)
        print(f"  {i+1:2d}. {patent_id:<15} → {normalized}")
    
    if len(patent_ids) > 10:
        print(f"  ... and {len(patent_ids) - 10} more patents")
    print()
    
    # Extract sequences
    print("🔍 Extracting antibody sequences...")
    sequences = extractor.process_mixed_patents(patent_ids, delay=0.1)  # Faster for batch
    
    if sequences:
        print(f"✅ Successfully extracted {len(sequences)} sequences!")
        
        # Generate output filename if not provided
        if not output_filename:
            output_filename = "/mnt/user-data/outputs/batch_antibody_extraction.xlsx"
        
        # Export results
        extractor.export_to_excel_enhanced(sequences, output_filename)
        
        # Show summary
        print("\n📊 Extraction Summary:")
        print("-" * 30)
        
        # Count by patent
        patents_with_sequences = {}
        for seq in sequences:
            if seq.original_patent_id not in patents_with_sequences:
                patents_with_sequences[seq.original_patent_id] = 0
            patents_with_sequences[seq.original_patent_id] += 1
        
        print(f"Patents processed: {len(patent_ids)}")
        print(f"Patents with sequences: {len(patents_with_sequences)}")
        print(f"Total sequences found: {len(sequences)}")
        
        # Count by type
        heavy_count = len([s for s in sequences if s.chain_type == "Heavy"])
        light_count = len([s for s in sequences if s.chain_type == "Light"])
        cdr_count = len([s for s in sequences if s.sequence_type == "CDR"])
        variable_count = len([s for s in sequences if s.sequence_type == "Variable Region"])
        
        print(f"Heavy chain sequences: {heavy_count}")
        print(f"Light chain sequences: {light_count}")
        print(f"CDR sequences: {cdr_count}")
        print(f"Variable region sequences: {variable_count}")
        
        # Show patents with most sequences
        print(f"\nTop 5 patents by sequence count:")
        sorted_patents = sorted(patents_with_sequences.items(), key=lambda x: x[1], reverse=True)
        for patent, count in sorted_patents[:5]:
            print(f"  {patent}: {count} sequences")
        
        print(f"\n💾 Results saved to: {output_filename}")
        return output_filename
    
    else:
        print("❌ No sequences found in any patents.")
        return None

def main():
    """Main function for batch processing"""
    print("🧬 Batch Patent Antibody Sequence Extractor")
    print("=" * 50)
    print("Process multiple patents with mixed formats")
    print()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        try:
            patent_ids = load_patent_ids_from_file(input_file)
            print(f"📂 Loaded {len(patent_ids)} patent IDs from {input_file}")
            process_patent_list(patent_ids, output_file)
        except Exception as e:
            print(f"❌ Error processing file: {e}")
            return
    
    else:
        # Interactive mode
        print("💡 Usage Options:")
        print("1. Command line: python batch_extractor.py input_file.csv [output_file.xlsx]")
        print("2. Interactive mode (enter patent IDs manually)")
        print()
        
        choice = input("Choose option (1 or 2): ").strip()
        
        if choice == "1":
            input_file = input("Enter path to input file (CSV/TXT/Excel): ").strip()
            output_file = input("Enter output filename (optional, press Enter for default): ").strip()
            
            if not output_file:
                output_file = None
            
            try:
                patent_ids = load_patent_ids_from_file(input_file)
                print(f"📂 Loaded {len(patent_ids)} patent IDs from {input_file}")
                process_patent_list(patent_ids, output_file)
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "2":
            print("\n📝 Enter patent IDs (one per line, press Enter twice to finish):")
            patent_ids = []
            while True:
                patent_id = input().strip()
                if not patent_id:
                    break
                patent_ids.append(patent_id)
            
            if patent_ids:
                process_patent_list(patent_ids)
            else:
                print("No patent IDs entered.")
        
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
