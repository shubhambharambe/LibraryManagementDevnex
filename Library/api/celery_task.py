from __future__ import absolute_import, unicode_literals
import os
import json
from datetime import datetime
from celery import shared_task
from .models import Author, Book, BorrowRecord

@shared_task
def generate_report():
    report_data = {
        'msg':"Library_Report",
        'total_authors': Author.objects.count(),
        'total_books': Book.objects.count(),
        'books_currently_borrowed': BorrowRecord.objects.filter(return_date__isnull=True).count(),
    }
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_dir = os.path.join(os.getcwd(), 'reports')
    print("its working")
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    report_file = os.path.join(report_dir, f'report_{timestamp}.json')
    with open(report_file, 'w') as f:
        json.dump(report_data, f)
    return report_file