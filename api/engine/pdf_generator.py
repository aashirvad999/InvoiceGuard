"""
Generates real sample invoice PDFs using PyMuPDF (fitz)
for end-to-end testing, live upload demonstration, and download actions.
"""

import os
import pymupdf as fitz

def generate_sample_pdf(invoice_data: dict, output_path: str, tamper_font: bool = False) -> str:
    """Creates a stylized sample invoice PDF matching the B2B invoice parameters."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = fitz.open()
    page = doc.new_page(width=595, height=842) # A4 size

    # Background header banner
    rect_header = fitz.Rect(30, 30, 565, 95)
    page.draw_rect(rect_header, color=(0.07, 0.08, 0.09), fill=(0.07, 0.08, 0.09))

    # Header Title
    page.insert_text(fitz.Point(45, 65), "TAX INVOICE", fontsize=18, fontname="helv", color=(0.9, 0.9, 0.9))
    page.insert_text(fitz.Point(45, 82), f"ORIGINAL FOR RECIPIENT · {invoice_data.get('invoice_number', 'INV-001')}", fontsize=9, fontname="helv", color=(0.6, 0.7, 0.8))

    # Vendor info
    page.insert_text(fitz.Point(45, 125), invoice_data.get("vendor_name", "Vendor"), fontsize=14, fontname="helv", color=(0.1, 0.1, 0.1))
    page.insert_text(fitz.Point(45, 142), f"GSTIN: {invoice_data.get('gstin', '27AAACA1234A1Z5')}", fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))
    page.insert_text(fitz.Point(45, 156), f"Bank: {invoice_data.get('bank_name', 'HDFC Bank')} | A/C: {invoice_data.get('bank_account', '5020004901')} | IFSC: {invoice_data.get('ifsc', 'HDFC0000240')}", fontsize=8.5, fontname="helv", color=(0.3, 0.3, 0.3))

    # Dates & Metadata
    page.insert_text(fitz.Point(380, 125), f"Invoice Date: {invoice_data.get('issue_date', 'Oct 24, 2026')}", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
    page.insert_text(fitz.Point(380, 142), f"Due Date: Immediate", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
    page.insert_text(fitz.Point(380, 156), f"Place of Supply: Maharashtra (27)", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))

    # Table Header
    table_top = 185
    page.draw_rect(fitz.Rect(40, table_top, 555, table_top + 22), color=(0.92, 0.94, 0.96), fill=(0.92, 0.94, 0.96))
    page.insert_text(fitz.Point(50, table_top + 15), "Item Description", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
    page.insert_text(fitz.Point(320, table_top + 15), "Qty", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
    page.insert_text(fitz.Point(380, table_top + 15), "Unit Price", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
    page.insert_text(fitz.Point(480, table_top + 15), "Total (INR)", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))

    # Line Items
    y = table_top + 38
    for item in invoice_data.get("line_items", []):
        desc = item.get("description", "Item")
        qty = item.get("qty", 1)
        price = item.get("unit_price", 0)
        amt = item.get("amount", qty * price)

        page.insert_text(fitz.Point(50, y), desc[:35], fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1))
        
        # If tampered item (e.g. keyboard), inject font difference
        if tamper_font and "keyboard" in desc.lower():
            # Inject '5' in standard font and '0' in bold/different size to simulate font tampering
            page.insert_text(fitz.Point(320, y), "5", fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1))
            page.insert_text(fitz.Point(326, y), "0", fontsize=9.8, fontname="helv", color=(0.12, 0.12, 0.12))
        else:
            page.insert_text(fitz.Point(320, y), str(qty), fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1))

        page.insert_text(fitz.Point(380, y), f"₹{price:,.2f}", fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1))
        page.insert_text(fitz.Point(480, y), f"₹{amt:,.2f}", fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1))
        
        page.draw_line(fitz.Point(40, y + 8), fitz.Point(555, y + 8), color=(0.9, 0.9, 0.9), width=0.5)
        y += 28

    # Totals block
    y += 15
    tot = invoice_data.get("total_amount", 0)
    taxable = invoice_data.get("taxable_amount", tot * 0.84)
    cgst = invoice_data.get("cgst_amount", 0)
    sgst = invoice_data.get("sgst_amount", 0)
    igst = invoice_data.get("igst_amount", 0)

    page.insert_text(fitz.Point(360, y), "Taxable Subtotal:", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))
    page.insert_text(fitz.Point(480, y), f"₹{taxable:,.2f}", fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1))
    
    if cgst > 0 or sgst > 0:
        y += 18
        page.insert_text(fitz.Point(360, y), "CGST (9%):", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))
        page.insert_text(fitz.Point(480, y), f"₹{cgst:,.2f}", fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1))
        y += 18
        page.insert_text(fitz.Point(360, y), "SGST (9%):", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))
        page.insert_text(fitz.Point(480, y), f"₹{sgst:,.2f}", fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1))
    elif igst > 0:
        y += 18
        page.insert_text(fitz.Point(360, y), "IGST (18%):", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))
        page.insert_text(fitz.Point(480, y), f"₹{igst:,.2f}", fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1))

    y += 24
    page.draw_rect(fitz.Rect(350, y - 14, 555, y + 14), color=(0.07, 0.08, 0.09), fill=(0.07, 0.08, 0.09))
    page.insert_text(fitz.Point(360, y + 4), "GRAND TOTAL:", fontsize=10, fontname="helv", color=(1.0, 1.0, 1.0))
    page.insert_text(fitz.Point(475, y + 4), f"₹{tot:,.2f}", fontsize=10, fontname="helv", color=(0.3, 0.87, 0.64))

    # Set metadata
    meta = {
        "producer": "Skia/PDF m122" if tamper_font else "Adobe PDF Library 15.0",
        "creator": "iText® 5.5.10 (Modified)" if tamper_font else "Invoice Engine v4",
        "title": f"Tax Invoice {invoice_data.get('invoice_number')}"
    }
    doc.set_metadata(meta)

    doc.save(output_path)
    doc.close()
    return output_path
