import re
from datetime import datetime
from pypdf import PdfReader


def parse_transaction_pdf(pdf_file):
    """
    Parse a PDF file and extract transaction data.
    Returns a list of transaction dictionaries.
    
    Expected PDF format:
    - Each transaction should contain: date, description, amount, type (income/expense)
    - Supports common bank statement formats
    """
    transactions = []
    
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            transaction = parse_transaction_line(line)
            if transaction:
                transactions.append(transaction)
        
        return transactions
    
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")


def parse_transaction_line(line):
    """
    Parse a single line from PDF to extract transaction details.
    Supports multiple date formats and transaction patterns.
    """
    date_patterns = [
        r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}'
    ]
    
    amount_pattern = r'[₹$]?\s*[\d,]+\.?\d{0,2}'
    
    for date_pattern in date_patterns:
        date_match = re.search(date_pattern, line, re.IGNORECASE)
        if date_match:
            date_str = date_match.group()
            amount_matches = re.findall(amount_pattern, line)
            
            if amount_matches:
                try:
                    date_obj = parse_date(date_str)
                    
                    amount_str = amount_matches[-1].replace('₹', '').replace('$', '').replace(',', '').strip()
                    amount = float(amount_str)
                    
                    description = line.replace(date_str, '').strip()
                    for amt in amount_matches:
                        description = description.replace(amt, '').strip()
                    
                    description = ' '.join(description.split())
                    
                    if len(description) > 5:
                        transaction_type = 'expense'
                        category = categorize_transaction(description)
                        
                        return {
                            'date': date_obj,
                            'description': description[:100],
                            'amount': amount,
                            'transaction_type': transaction_type,
                            'category': category
                        }
                
                except (ValueError, Exception):
                    continue
    
    return None


def parse_date(date_str):
    """Parse various date formats."""
    date_formats = [
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%d-%m-%y',
        '%d/%m/%y',
        '%d %b %Y',
        '%d %B %Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return datetime.now().date()


def categorize_transaction(description):
    """Automatically categorize transaction based on description."""
    description_lower = description.lower()
    
    categories = {
        'Food & Dining': ['restaurant', 'cafe', 'food', 'dining', 'swiggy', 'zomato', 'uber eats', 'dominos', 'pizza', 'mcdonald'],
        'Transportation': ['uber', 'ola', 'taxi', 'metro', 'bus', 'train', 'fuel', 'petrol', 'diesel', 'parking'],
        'Shopping': ['amazon', 'flipkart', 'myntra', 'mall', 'store', 'shopping', 'purchase'],
        'Entertainment': ['movie', 'cinema', 'netflix', 'spotify', 'prime', 'hotstar', 'game'],
        'Utilities': ['electricity', 'water', 'gas', 'internet', 'phone', 'mobile', 'broadband', 'wifi'],
        'Healthcare': ['hospital', 'doctor', 'medical', 'pharmacy', 'medicine', 'health'],
        'Education': ['school', 'college', 'university', 'course', 'book', 'tuition'],
        'Groceries': ['grocery', 'supermarket', 'reliance fresh', 'big bazaar', 'dmart', 'vegetables'],
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
    
    return 'Others'
