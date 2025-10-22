#!/usr/bin/env python3
"""
generate_packing_list.py - Main Orchestrator for Packing List Generation
Integrates dat_parser_simple, packing_list_generator, and pdf_mapper
Creates professional packing lists from KCB DAT files
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Import our modules
from dat_parser_simple import DATFileParser
from packing_list_generator import PackingListGenerator
from pdf_mapper import PackingListPDFMapper


class PackingListOrchestrator:
    """
    Main orchestrator that coordinates the entire packing list generation process
    """
    
    def __init__(self, output_dir: str = "output/packing_lists"):
        self.output_dir = output_dir
        self.parser = DATFileParser()
        self.generator = PackingListGenerator()
        self.pdf_mapper = PackingListPDFMapper(output_dir=output_dir)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def process_dat_file(self, dat_file_path: str, custom_output_name: str = None) -> str:
        """
        Complete workflow: Parse DAT file → Generate packing lists → Create PDF
        
        Args:
            dat_file_path: Path to the DAT file
            custom_output_name: Optional custom name for output PDF
        
        Returns:
            Path to generated PDF
        """
        print(f"\n{'='*70}")
        print(f"🚀 PACKING LIST GENERATION WORKFLOW")
        print(f"{'='*70}")
        print(f"📁 Input File: {dat_file_path}")
        
        # Step 1: Parse DAT file
        print(f"\n📖 Step 1: Parsing DAT file...")
        try:
            parsed_data = self.parser.parse_file(dat_file_path)
            expanded_orders = parsed_data['expanded_orders']
            print(f"✅ Parsed {len(parsed_data['orders'])} orders")
            print(f"✅ Expanded to {len(expanded_orders)} individual books")
        except Exception as e:
            print(f"❌ Error parsing DAT file: {e}")
            raise
        
        # Step 2: Get metadata for order number and date (NO PARAMETERS)
        print(f"\n📊 Step 2: Extracting metadata...")
        metadata = self.parser.get_file_metadata()
        order_number = f"KCB-{metadata['run_number']}"
        order_date = metadata['file_date']
        print(f"✅ Order Number: {order_number}")
        print(f"✅ Order Date: {order_date}")
        print(f"✅ Total Books: {metadata['total_books']}")
        
        # Step 3: Generate packing lists grouped by delivery branch
        print(f"\n📦 Step 3: Generating packing lists...")
        try:
            packing_lists = self.generator.generate_packing_lists(
                expanded_orders,
                order_number=order_number,
                order_date=order_date
            )
            print(f"✅ Generated {len(packing_lists)} packing lists (one per delivery branch)")
            self.generator.print_packing_list_summary(packing_lists)
        except Exception as e:
            print(f"❌ Error generating packing lists: {e}")
            raise
        
        # Step 4: Generate PDF
        print(f"\n📄 Step 4: Creating PDF document...")
        try:
            # Determine output filename
            if custom_output_name:
                pdf_filename = custom_output_name
            else:
                # Use order number from filename
                base_name = Path(dat_file_path).stem
                pdf_filename = f"PackingList_{base_name}_{datetime.now().strftime('%Y%m%d')}"
            
            pdf_path = self.pdf_mapper.generate_packing_list_pdf(
                packing_lists,
                filename=pdf_filename
            )
            
            print(f"\n{'='*70}")
            print(f"✅ SUCCESS! Packing list generated")
            print(f"📄 PDF Location: {pdf_path}")
            print(f"📦 Total Delivery Branches: {len(packing_lists)}")
            print(f"📚 Total Books: {sum(p['total_books'] for p in packing_lists)}")
            print(f"{'='*70}\n")
            
            return pdf_path
            
        except Exception as e:
            print(f"❌ Error creating PDF: {e}")
            raise
    
    def process_multiple_files(self, dat_files: list) -> list:
        """
        Process multiple DAT files in batch
        
        Args:
            dat_files: List of DAT file paths
        
        Returns:
            List of generated PDF paths
        """
        generated_pdfs = []
        
        print(f"\n🔄 Batch Processing: {len(dat_files)} files")
        print(f"{'='*70}")
        
        for idx, dat_file in enumerate(dat_files, 1):
            print(f"\n[{idx}/{len(dat_files)}] Processing: {dat_file}")
            try:
                pdf_path = self.process_dat_file(dat_file)
                generated_pdfs.append(pdf_path)
            except Exception as e:
                print(f"⚠️  Failed to process {dat_file}: {e}")
                continue
        
        print(f"\n{'='*70}")
        print(f"✅ Batch processing complete!")
        print(f"📊 Successfully generated: {len(generated_pdfs)}/{len(dat_files)} PDFs")
        print(f"{'='*70}\n")
        
        return generated_pdfs


def main():
    """Main entry point with command line argument support"""
    
    if len(sys.argv) < 2:
        print("Usage: python generate_packing_list.py <dat_file_path> [output_name]")
        print("\nExample:")
        print("  python generate_packing_list.py KCB-618.dat")
        print("  python generate_packing_list.py KCB-618.dat CustomPackingList")
        print("\nOr for batch processing:")
        print("  python generate_packing_list.py file1.dat file2.dat file3.dat")
        sys.exit(1)
    
    # Get command line arguments
    dat_files = [arg for arg in sys.argv[1:] if arg.endswith('.dat')]
    custom_name = None
    
    # Check if last arg is a custom name (doesn't end with .dat)
    if len(sys.argv) > 2 and not sys.argv[-1].endswith('.dat'):
        custom_name = sys.argv[-1]
    
    # Create orchestrator
    orchestrator = PackingListOrchestrator()
    
    # Process files
    if len(dat_files) == 1:
        # Single file processing
        orchestrator.process_dat_file(dat_files[0], custom_name)
    else:
        # Batch processing
        orchestrator.process_multiple_files(dat_files)


if __name__ == "__main__":
    # If run directly without arguments, use example file
    if len(sys.argv) == 1:
        print("No arguments provided. Using example file...")
        example_file = "KCB-618.dat"
        
        if os.path.exists(example_file):
            orchestrator = PackingListOrchestrator()
            orchestrator.process_dat_file(example_file)
        else:
            print(f"❌ Example file '{example_file}' not found")
            print("Please provide a DAT file path as argument")
            sys.exit(1)
    else:
        main()