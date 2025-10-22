from django.shortcuts import render
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import os
import tempfile
from datetime import datetime

from .utils.dat_parser_simple import DATFileParser
from .utils.packing_list_generator import PackingListGenerator
from .utils.pdf_mapper import PackingListPDFMapper


def home(request):
    """Simple home page with upload form"""
    return render(request, 'home.html')


def process_dat_file(request):
    """
    Process uploaded DAT file and generate PDF
    Returns the PDF file for download
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    if 'dat_file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
    
    uploaded_file = request.FILES['dat_file']
    
    # Validate file extension
    if not uploaded_file.name.endswith('.dat'):
        return JsonResponse({'error': 'Only .dat files are allowed'}, status=400)
    
    # Validate file size (10MB max)
    if uploaded_file.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'File size must not exceed 10MB'}, status=400)
    
    try:
        # Create temp directory for processing
        temp_dir = tempfile.mkdtemp()
        
        # Save uploaded file temporarily
        temp_dat_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_dat_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Process the file
        parser = DATFileParser()
        generator = PackingListGenerator()
        pdf_mapper = PackingListPDFMapper(output_dir=temp_dir)
        
        # Step 1: Parse DAT file
        parsed_data = parser.parse_file(temp_dat_path)
        expanded_orders = parsed_data['expanded_orders']
        
        # Step 2: Extract metadata
        metadata = parser.get_file_metadata()
        order_number = f"KCB-{metadata['run_number']}"
        order_date = metadata['file_date']
        
        # Step 3: Generate packing lists
        packing_lists = generator.generate_packing_lists(
            expanded_orders,
            order_number=order_number,
            order_date=order_date
        )
        
        # Step 4: Generate PDF
        pdf_filename = f"PackingList_{order_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        pdf_path = pdf_mapper.generate_packing_list_pdf(
            packing_lists,
            filename=pdf_filename
        )
        
        # Return the PDF file
        pdf_file = open(pdf_path, 'rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pdf_filename}.pdf"'
        
        # Clean up temp DAT file immediately
        if os.path.exists(temp_dat_path):
            os.remove(temp_dat_path)
        
        # Note: temp_dir and PDF will be cleaned up after response is sent
        # You might want to implement cleanup in a signal or middleware
        
        return response
        
    except Exception as e:
        # Clean up on error
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        return JsonResponse({
            'error': f'Error processing file: {str(e)}'
        }, status=500)