#!/usr/bin/env python3
"""
pdf_mapper.py - PDF Generation for KCB Packing Lists
Generates professional PDF packing lists with one page per delivery branch
Uses ReportLab for PDF generation
UPDATED VERSION - Added book style summary table
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import List, Dict
from datetime import datetime
from collections import Counter
import os


class PackingListPDFMapper:
    """
    Maps packing list data to professionally formatted PDFs
    Each delivery branch gets its own page
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.page_width, self.page_height = A4
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Define styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='PackingListTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Header info style
        self.styles.add(ParagraphStyle(
            name='HeaderInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        ))
        
        # Branch title style
        self.styles.add(ParagraphStyle(
            name='BranchTitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#c62828'),
            spaceAfter=4,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
    
    def _create_book_style_summary_table(self, books: List[Dict]) -> Table:
        """Create summary table showing book styles and their counts"""
        # Count books by book style
        book_style_counts = Counter(book['book_style'] for book in books)
        
        # Sort by book style code in DESCENDING order (bigger codes first)
        sorted_styles = sorted(book_style_counts.items(), reverse=True)
        
        # Build table data
        table_data = [['Book Style', 'Number of Books']]
        
        for book_style, count in sorted_styles:
            table_data.append([book_style, str(count)])
        
        # Add total row
        total_books = sum(book_style_counts.values())
        table_data.append(['TOTAL', str(total_books)])
        
        # Create table with smaller column widths
        col_widths = [1.2*inch, 1.5*inch]
        summary_table = Table(table_data, colWidths=col_widths)
        
        # Style the table
        table_style = TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            
            # Total row (last row)
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 9),
            ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor('#1a237e')),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#1a237e')),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f9f9f9')]),
        ])
        
        summary_table.setStyle(table_style)
        return summary_table
    
    def _create_header_section(self, packing_list: Dict) -> List:
        """Create the header section with bank info, order details, and branch"""
        elements = []
        
        # Title
        title = Paragraph(
            "<b>PACKING LIST</b>",
            self.styles['PackingListTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.08*inch))
        
        # Branch information (moved here, right after title)
        branch_title = Paragraph(
            f"<b>Delivery Branch: {packing_list['delivery_branch_name']}</b> ({packing_list['delivery_branch_code']})",
            self.styles['BranchTitle']
        )
        elements.append(branch_title)
        elements.append(Spacer(1, 0.15*inch))
        
        # Header info table (2 columns)
        header_data = [
            [
                Paragraph(f"<b>Bank Name:</b> {packing_list['bank_name']}", self.styles['Normal']),
                Paragraph(f"<b>Order Number:</b> {packing_list['order_number']}", self.styles['Normal'])
            ],
            [
                Paragraph(f"<b>Order Date:</b> {packing_list['order_date']}", self.styles['Normal']),
                Paragraph(f"<b>Total Books:</b> {packing_list['total_books']}", self.styles['Normal'])
            ]
        ]
        
        header_table = Table(header_data, colWidths=[3*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 0.12*inch))
        
        # Book style summary table (smaller size, positioned after header info)
        summary_table = self._create_book_style_summary_table(packing_list['books'])
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_books_table(self, books: List[Dict], delivery_branch_name: str) -> Table:
        """Create the main table with book details"""
        # Table headers - NO SR.NO, just book code
        headers = [
            'Book Code',
            'Account Name',
            'Account Number',
            'Start Serial',
            'Branch Code',
            'Delivery Branch'
        ]
        
        # Prepare table data
        table_data = [headers]
        
        # Create paragraph style for wrapping text
        wrap_style = ParagraphStyle(
            'WrapStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=9,
            wordWrap='CJK'
        )
        
        # Sort books by book_style in descending order (bigger codes first)
        sorted_books = sorted(books, key=lambda x: x['book_style'], reverse=True)
        
        for book in sorted_books:
            row = [
                book['book_style'],  # Just the code (01, 02, 52, etc)
                Paragraph(book['account_name'], wrap_style),  # Wrap account name
                book['account_number'],
                book['start_serial'],
                book['branch_code'],
                Paragraph(delivery_branch_name, wrap_style)  # Wrap delivery branch
            ]
            table_data.append(row)
        
        # Column widths (adjusted to fit A4 page without Sr.No)
        col_widths = [0.7*inch, 2.3*inch, 1.3*inch, 1.1*inch, 0.9*inch, 1.5*inch]
        
        # Create table
        books_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Style the table
        table_style = TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Book Code centered
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#1a237e')),
            
            # Alternating row colors for better readability
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ])
        
        books_table.setStyle(table_style)
        return books_table
    
    def generate_packing_list_pdf(self, 
                                   packing_lists: List[Dict],
                                   filename: str = None) -> str:
        """
        Generate a PDF with all packing lists
        Each delivery branch gets its own page
        
        Args:
            packing_lists: List of packing list data dictionaries
            filename: Optional custom filename (without extension)
        
        Returns:
            Path to generated PDF file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"PackingList_{timestamp}"
        
        output_path = os.path.join(self.output_dir, f"{filename}.pdf")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Build the story (content)
        story = []
        
        for idx, packing_list in enumerate(packing_lists):
            # Add header section
            header_elements = self._create_header_section(packing_list)
            story.extend(header_elements)
            
            # Add books table with delivery branch name
            books_table = self._create_books_table(
                packing_list['books'], 
                packing_list['delivery_branch_name']
            )
            story.append(books_table)
            
            # Add page break after each packing list (except the last one)
            if idx < len(packing_lists) - 1:
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ PDF generated successfully: {output_path}")
        return output_path


# Example usage
if __name__ == "__main__":
    # Sample packing list data
    sample_data = [
        {
            'bank_name': 'KCB Bank Ltd',
            'order_number': 'KCB-000618',
            'order_date': '2025-09-29',
            'delivery_branch_code': '01320',
            'delivery_branch_name': 'KCB LAVINGTON',
            'total_books': 4,
            'books': [
                {
                    'book_style': '01',
                    'account_name': 'JOHN DOE',
                    'account_number': '1234567890',
                    'start_serial': '000001',
                    'branch_code': '01100',
                    'currency': 'KES',
                    'leaves': 50
                },
                {
                    'book_style': '01',
                    'account_name': 'JANE SMITH',
                    'account_number': '1234567891',
                    'start_serial': '000051',
                    'branch_code': '01100',
                    'currency': 'KES',
                    'leaves': 50
                },
                {
                    'book_style': '02',
                    'account_name': 'ACME CORPORATION',
                    'account_number': '9876543210',
                    'start_serial': '000101',
                    'branch_code': '01100',
                    'currency': 'KES',
                    'leaves': 100
                },
                {
                    'book_style': '52',
                    'account_name': 'GLOBAL TRADERS LTD',
                    'account_number': '5555555555',
                    'start_serial': '000201',
                    'branch_code': '01100',
                    'currency': 'USD',
                    'leaves': 100
                }
            ]
        }
    ]
    
    # Generate PDF
    pdf_mapper = PackingListPDFMapper(output_dir="output")
    pdf_path = pdf_mapper.generate_packing_list_pdf(
        sample_data,
        filename="Test_PackingList"
    )
    
    print(f"Test PDF created: {pdf_path}")