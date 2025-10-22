#!/usr/bin/env python3
"""
packing_list_generator.py - KCB Packing List Generator
Groups books by delivery branch and generates organized packing lists
Each delivery branch gets its own page with book details
"""

from typing import List, Dict
from collections import defaultdict
from datetime import datetime


class PackingListGenerator:
    """
    Generates packing lists grouped by delivery branch
    Each branch gets a separate page with all books being delivered there
    """
    
    def __init__(self):
        self.bank_name = "KCB Bank Ltd"
        
    def group_books_by_delivery_branch(self, expanded_orders: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group books by delivery branch code
        Returns: {delivery_branch_code: [list of books]}
        """
        grouped = defaultdict(list)
        
        for order in expanded_orders:
            delivery_code = order.get('delivery_branch_code', '').strip()
            if delivery_code:
                grouped[delivery_code].append(order)
        
        return dict(grouped)
    
    def get_book_style_name(self, book_style: str, book_type_desc: str) -> str:
        """
        Generate a readable book style name
        Format: "CORPORATE CHEQUE (KES - 50)" or "PERSONAL CHEQUE (USD - 100)"
        """
        # Extract key info from book_type_desc
        if "Personal" in book_type_desc:
            style = "PERSONAL CHEQUE"
        elif "Corporate" in book_type_desc:
            style = "CORPORATE CHEQUE"
        elif "Banker" in book_type_desc:
            style = "BANKER'S CHEQUE"
        else:
            style = book_type_desc.upper()
        
        return style
    
    def generate_packing_lists(self, 
                               expanded_orders: List[Dict], 
                               order_number: str,
                               order_date: str) -> List[Dict]:
        """
        Generate packing list data grouped by delivery branch
        
        Returns: List of packing list pages, one per delivery branch
        [
            {
                'delivery_branch_code': '01320',
                'delivery_branch_name': 'KCB LAVINGTON',
                'total_books': 5,
                'books': [...]
            },
            ...
        ]
        """
        # Group by delivery branch
        grouped_books = self.group_books_by_delivery_branch(expanded_orders)
        
        packing_lists = []
        
        for branch_code in sorted(grouped_books.keys()):
            books = grouped_books[branch_code]
            
            # Get branch name from first book (all should have same delivery branch)
            branch_name = books[0].get('delivery_branch_name', 'UNKNOWN BRANCH').strip()
            
            # Prepare book entries for the table
            book_entries = []
            for book in books:
                book_entries.append({
                    'book_style': book.get('book_style', ''),
                    'account_name': book.get('account_name', '').strip(),
                    'account_number': book.get('account_number', '').strip(),
                    'start_serial': book.get('serial_number', '').strip(),
                    'branch_code': book.get('delivery_branch_code', '').strip(),  # <-- now uses delivery_branch_code
                    'currency': book.get('currency', 'KES'),
                    'leaves': book.get('leaves', 50)
                })
            
            packing_lists.append({
                'bank_name': self.bank_name,
                'order_number': order_number,
                'order_date': order_date,
                'delivery_branch_code': branch_code,
                'delivery_branch_name': branch_name,
                'total_books': len(books),
                'books': book_entries
            })
        
        return packing_lists
    
    def print_packing_list_summary(self, packing_lists: List[Dict]):
        """Print a summary of packing lists for verification"""
        print(f"\n{'='*70}")
        print(f"📦 PACKING LIST SUMMARY")
        print(f"{'='*70}")
        print(f"Total Delivery Branches: {len(packing_lists)}")
        print(f"Total Books Across All Branches: {sum(p['total_books'] for p in packing_lists)}")
        print(f"\nBreakdown by Branch:")
        print(f"{'-'*70}")
        
        for idx, plist in enumerate(packing_lists, 1):
            print(f"{idx}. {plist['delivery_branch_name']} ({plist['delivery_branch_code']})")
            print(f"   📚 Books: {plist['total_books']}")
        
        print(f"{'='*70}\n")


# Example usage
if __name__ == "__main__":
    # Test with sample data
    sample_orders = [
        {
            'book_style': '01',
            'book_type_description': 'Personal KES',
            'account_name': 'JOHN DOE',
            'account_number': '1234567890',
            'serial_number': '000001',
            'branch_code': '01100',
            'delivery_branch_code': '01320',
            'delivery_branch_name': 'KCB LAVINGTON',
            'currency': 'KES',
            'leaves': 50
        },
        {
            'book_style': '02',
            'book_type_description': 'Corporate KES',
            'account_name': 'ACME CORP',
            'account_number': '9876543210',
            'serial_number': '000101',
            'branch_code': '01100',
            'delivery_branch_code': '01320',
            'delivery_branch_name': 'KCB LAVINGTON',
            'currency': 'KES',
            'leaves': 100
        }
    ]
    
    generator = PackingListGenerator()
    packing_lists = generator.generate_packing_lists(
        sample_orders,
        order_number="KCB-000618",
        order_date="2025-09-29"
    )
    
    generator.print_packing_list_summary(packing_lists)
    
    # Show first packing list details
    if packing_lists:
        print("\nSample Packing List (First Branch):")
        print(f"Branch: {packing_lists[0]['delivery_branch_name']}")
        print(f"Books: {packing_lists[0]['total_books']}")
        for book in packing_lists[0]['books'][:3]:
            print(f"  - {book['account_name']}: {book['start_serial']}")