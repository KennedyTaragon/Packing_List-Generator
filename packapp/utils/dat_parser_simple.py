#!/usr/bin/env python3
"""
dat_parser_simple.py - Simplified KCB DAT File Parser for Packing Lists
Handles parsing of KCB cheque book order files
NO DEPENDENCIES - Standalone version
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import re
import os


@dataclass
class OrderRecord:
    """Order record structure"""
    bank_id: str
    order_id: str
    priority: str
    sort_code: str
    account_number: str
    check_digit: str
    cheque_voucher_digits: str
    credits_voucher_digits: str
    book_style: str
    number_of_books: int
    cheque_start_serial: str
    credits_start_serial: str
    personalization: str
    branch_title: str
    branch_address: str
    signature_required: str
    beneficiary_name: str
    delivery_branch_code: str
    delivery_branch_name: str


class DATFileParser:
    """Simple parser for KCB DAT files - Packing List focused"""
    
    # Book style mapping
    BOOK_STYLES = {
        "01": {"type": "Personal KES", "currency": "KES", "leaves": 50},
        "02": {"type": "Corporate KES", "currency": "KES", "leaves": 100},
        "25": {"type": "South African Rand Small", "currency": "ZAR", "leaves": 50},
        "45": {"type": "South African Rand Large", "currency": "ZAR", "leaves": 100},
        "31": {"type": "Sterling Pound Small", "currency": "GBP", "leaves": 50},
        "51": {"type": "Sterling Pound Large", "currency": "GBP", "leaves": 100},
        "32": {"type": "USA Dollar Small", "currency": "USD", "leaves": 50},
        "52": {"type": "USA Dollar Large", "currency": "USD", "leaves": 100},
        "40": {"type": "EURO Small", "currency": "EUR", "leaves": 50},
        "69": {"type": "EURO Large", "currency": "EUR", "leaves": 100},
        "71": {"type": "KES Banker's Cheques", "currency": "KES", "leaves": 100},
        "72": {"type": "USD Banker's Cheques", "currency": "USD", "leaves": 100},
        "73": {"type": "GBP Banker's Cheques", "currency": "GBP", "leaves": 100},
        "74": {"type": "EUR Banker's Cheques", "currency": "EUR", "leaves": 100},
    }
    
    # Serial increment rules
    SERIAL_INCREMENTS = {
        "01": 50, "02": 100, "25": 50, "45": 100, "31": 50, "51": 100,
        "32": 50, "52": 100, "40": 50, "69": 100, "71": 100, "72": 100,
        "73": 100, "74": 100,
    }

    def __init__(self):
        self.orders: List[OrderRecord] = []
        self.filename: str = ""
        self.extracted_order_number: str = ""

    def extract_order_number_from_filename(self, file_path: str) -> str:
        """Extract order number from filename"""
        filename = os.path.basename(file_path)
        self.filename = filename
        
        # Pattern 1: "KCB-618" or "KCB-000618"
        match = re.search(r'KCB-(\d+)', filename, re.IGNORECASE)
        if match:
            return match.group(1).zfill(6)
        
        # Pattern 2: Any 3-6 digit number
        match = re.search(r'(\d{3,6})', filename)
        if match:
            return match.group(1).zfill(6)
        
        # Fallback: timestamp
        return datetime.now().strftime("%m%d%H").zfill(6)

    def parse_date(self, date_str: str) -> str:
        """Parse date from various formats"""
        if not date_str or not date_str.strip():
            return datetime.now().strftime("%Y-%m-%d")
        
        date_str = date_str.strip()
        
        # Try different formats
        formats = ["%d/%m/%y", "%d%m%y", "%d/%m/%Y", "%Y-%m-%d"]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return datetime.now().strftime("%Y-%m-%d")

    def parse_file(self, file_path: str) -> Dict:
        """Parse DAT file and return order data"""
        self.extracted_order_number = self.extract_order_number_from_filename(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [line.rstrip('\n\r') for line in file.readlines()]
        
        # Parse all lines as order records (skip header/trailer if present)
        for line in lines:
            if not line.strip():
                continue
            
            # Skip header (order_id = '0') and trailer (order_id = '4')
            if len(line) >= 3:
                order_id = line[2]
                if order_id == '1':  # Only process order records
                    order = self._parse_order_record(line)
                    if order:
                        self.orders.append(order)
        
        return {
            'orders': self.orders,
            'expanded_orders': self._expand_orders_with_books(),
            'extracted_order_number': self.extracted_order_number
        }

    def _parse_order_record(self, line: str) -> Optional[OrderRecord]:
        """Parse order record from DAT line"""
        if len(line) < 210:
            line = line.ljust(210)
        
        try:
            num_books_str = line[26:30].strip()
            num_books = int(num_books_str) if num_books_str else 1
            
            return OrderRecord(
                bank_id=line[0:2].strip(),
                order_id=line[2:3].strip(),
                priority=line[3:4].strip(),
                sort_code=line[4:9].strip(),
                account_number=line[9:19].strip(),
                check_digit=line[19:20].strip(),
                cheque_voucher_digits=line[20:22].strip(),
                credits_voucher_digits=line[22:24].strip(),
                book_style=line[24:26].strip(),
                number_of_books=num_books,
                cheque_start_serial=line[30:36].strip(),
                credits_start_serial=line[36:42].strip(),
                personalization=line[42:78].strip(),
                branch_title=line[78:108].strip(),
                branch_address=line[108:138].strip(),
                signature_required=line[138:139].strip(),
                beneficiary_name=line[139:169].strip(),
                delivery_branch_code=line[169:174].strip(),
                delivery_branch_name=line[174:210].strip()
            )
        except (ValueError, IndexError) as e:
            print(f"⚠️  Error parsing line: {e}")
            return None

    def _expand_orders_with_books(self) -> List[Dict]:
        """Expand orders based on number of books"""
        expanded = []
        
        for order in self.orders:
            book_style = order.book_style
            increment = self.SERIAL_INCREMENTS.get(book_style, 50)
            
            # Add the original order
            expanded.append(self._order_to_dict(order, order.cheque_start_serial))
            
            # Add additional books with incremented serials
            current_serial = int(order.cheque_start_serial)
            for book_num in range(1, order.number_of_books):
                current_serial += increment
                new_serial = str(current_serial).zfill(6)
                expanded.append(self._order_to_dict(order, new_serial))
        
        return expanded

    def _order_to_dict(self, order: OrderRecord, serial: str) -> Dict:
        """Convert order to dictionary"""
        book_info = self.BOOK_STYLES.get(order.book_style, {})
        
        return {
            'book_style': order.book_style,
            'book_type_description': book_info.get('type', 'Unknown'),
            'currency': book_info.get('currency', 'KES'),
            'leaves': book_info.get('leaves', 50),
            'branch_code': order.sort_code,
            'account_number': order.account_number,
            'serial_number': serial,
            'account_name': order.personalization.strip(),
            'branch_title': order.branch_title.strip(),
            'branch_address': order.branch_address.strip(),
            'delivery_branch_code': order.delivery_branch_code,
            'delivery_branch_name': order.delivery_branch_name.strip(),
            'number_of_books': order.number_of_books
        }

    def get_file_metadata(self) -> Dict:
        """Extract file metadata"""
        # Try to parse date from first order if available
        file_date = datetime.now().strftime("%Y-%m-%d")
        
        return {
            'bank_id': '01',
            'run_number': self.extracted_order_number,
            'supplier_code': 'TD',
            'file_date': file_date,
            'total_orders': len(self.orders),
            'total_books': sum(order.number_of_books for order in self.orders),
            'filename': self.filename
        }