"""
services.py - Django service layer for packing list generation
Integrates the terminal scripts with Django
"""

import os
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from .models import PackingListJob
from .utils.dat_parser_simple import DATFileParser
from .utils.packing_list_generator import PackingListGenerator
from .utils.pdf_mapper import PackingListPDFMapper


class PackingListService:
    """Service to handle packing list generation in Django"""
    
    def __init__(self):
        self.parser = DATFileParser()
        self.generator = PackingListGenerator()
        # Use MEDIA_ROOT for PDF output
        self.pdf_output_dir = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs')
        os.makedirs(self.pdf_output_dir, exist_ok=True)
        self.pdf_mapper = PackingListPDFMapper(output_dir=self.pdf_output_dir)
    
    def process_dat_file(self, job: PackingListJob) -> PackingListJob:
        """
        Process a DAT file and generate packing list PDF
        
        Args:
            job: PackingListJob instance with uploaded dat_file
        
        Returns:
            Updated PackingListJob instance
        """
        try:
            # Update status
            job.status = 'processing'
            job.save()
            
            # Get the physical file path
            dat_file_path = job.dat_file.path
            
            # Step 1: Parse DAT file
            print(f"📖 Parsing DAT file: {dat_file_path}")
            parsed_data = self.parser.parse_file(dat_file_path)
            expanded_orders = parsed_data['expanded_orders']
            
            # Step 2: Extract metadata
            metadata = self.parser.get_file_metadata()
            order_number = f"KCB-{metadata['run_number']}"
            order_date = metadata['file_date']
            
            # Update job with metadata
            job.order_number = order_number
            job.order_date = datetime.strptime(order_date, "%Y-%m-%d").date()
            job.total_orders = metadata['total_orders']
            job.total_books = metadata['total_books']
            job.save()
            
            print(f"✅ Parsed {len(parsed_data['orders'])} orders")
            print(f"✅ Expanded to {len(expanded_orders)} individual books")
            
            # Step 3: Generate packing lists
            print(f"📦 Generating packing lists...")
            packing_lists = self.generator.generate_packing_lists(
                expanded_orders,
                order_number=order_number,
                order_date=order_date
            )
            
            job.total_branches = len(packing_lists)
            job.save()
            
            print(f"✅ Generated {len(packing_lists)} packing lists")
            
            # Step 4: Generate PDF
            print(f"📄 Creating PDF document...")
            pdf_filename = f"PackingList_{order_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            pdf_path = self.pdf_mapper.generate_packing_list_pdf(
                packing_lists,
                filename=pdf_filename
            )
            
            # Step 5: Save PDF to Django model
            with open(pdf_path, 'rb') as pdf_file:
                job.pdf_file.save(
                    f"{pdf_filename}.pdf",
                    ContentFile(pdf_file.read()),
                    save=False
                )
            
            # Clean up temporary PDF
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            
            # Update job status
            job.status = 'completed'
            job.processed_at = timezone.now()
            job.save()
            
            print(f"✅ SUCCESS! Packing list generated")
            print(f"📄 Total Books: {job.total_books}")
            print(f"📦 Total Delivery Branches: {job.total_branches}")
            
            return job
            
        except Exception as e:
            # Handle errors
            job.status = 'failed'
            job.error_message = str(e)
            job.processed_at = timezone.now()
            job.save()
            
            print(f"❌ Error processing DAT file: {e}")
            raise
    
    def get_recent_jobs(self, limit=10):
        """Get recent packing list jobs"""
        return PackingListJob.objects.all()[:limit]
    
    def get_job_by_id(self, job_id):
        """Get a specific job by ID"""
        return PackingListJob.objects.get(id=job_id)