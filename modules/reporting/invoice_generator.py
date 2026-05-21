
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
from core.company_config import CompanyConfig

# Try to register a font that supports Arabic (Arial is standard on Windows)
try:
    # Common path for Windows
    font_path = "C:\\Windows\\Fonts\\arial.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Arial', font_path))
        pdfmetrics.registerFont(TTFont('Arial-Bold', "C:\\Windows\\Fonts\\arialbd.ttf"))
        MAIN_FONT = 'Arial'
        BOLD_FONT = 'Arial-Bold'
    else:
        # Fallback or linux path could be added here
        MAIN_FONT = 'Helvetica'
        BOLD_FONT = 'Helvetica-Bold'
except Exception as e:
    print(f"Font Load Warning: {e}")
    MAIN_FONT = 'Helvetica'
    BOLD_FONT = 'Helvetica-Bold'

def fix_text(text):
    if not text: return ""
    text = str(text)
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except:
        return text

class InvoiceGenerator:

    @staticmethod
    def generate(filepath, order, customer, items, user_data=None, lang='en'):
        """
        Generates a PDF invoice.
        lang: 'en' or 'ar'
        """
        
        # Translation Dictionary
        LABELS = {
            'en': {
                'BRAND': 'PHONIX ENTERPRISE',
                'BILL_TO': 'BILL TO:',
                'CUST_ID': 'Customer ID:',
                'INV_NO': 'INVOICE #:',
                'DATE': 'DATE:',
                'STATUS': 'STATUS:',
                'ITEM': 'Item / Description',
                'QTY': 'Qty',
                'PRICE': 'Unit Price',
                'TAX': 'Tax',
                'DISC': 'Discount',
                'TOTAL': 'Total',
                'SUB': 'Subtotal:',
                'GRAND': 'GRAND TOTAL:',
                'PREP': 'Prepared by:',
                'THANKS': 'Thank you for your business!'
            },
            'ar': {
                'BRAND': 'فونكس انتربرايز',
                'BILL_TO': 'فاتورة إلى:',
                'CUST_ID': 'رقم العميل:',
                'INV_NO': 'رقم الفاتورة:',
                'DATE': 'التاريخ:',
                'STATUS': 'الحالة:',
                'ITEM': 'البيان / الصنف',
                'QTY': 'الكمية',
                'PRICE': 'سعر الوحدة',
                'TAX': 'الضريبة',
                'DISC': 'الخصم',
                'TOTAL': 'الإجمالي',
                'SUB': 'المجموع الفرعي:',
                'GRAND': 'الإجمالي الكلي:',
                'PREP': 'إعداد:',
                'THANKS': 'شكراً لتعاملكم معنا!'
            }
        }
        
        L = LABELS.get(lang, LABELS['en'])
        
        # Helper to maybe reshape label if Arabic
        def txt(key):
            val = L.get(key, key)
            if lang == 'ar':
                return fix_text(val)
            return val

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Update styles to use our font
        styles['Normal'].fontName = MAIN_FONT
        styles['Heading1'].fontName = BOLD_FONT
        styles['Heading2'].fontName = BOLD_FONT
        styles['Title'].fontName = BOLD_FONT
        styles['Italic'].fontName = MAIN_FONT 
        
        
        # Load company configuration
        company_info = CompanyConfig.get_company_info(lang)
        invoice_config = CompanyConfig.get_invoice_info(lang)
        
        # --- Header with Logo and Company Info ---
        header_elements = []
        
        # Try to add logo if configured
        logo_path = company_info.get('logo_path', '').strip()
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=1.5*inch, height=1.5*inch, kind='proportional')
                header_elements.append([logo])
            except:
                # Fallback to text if logo fails
                brand_style = ParagraphStyle(
                    'Brand',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#2C3E50'),
                    fontName=BOLD_FONT
                )
                header_elements.append([Paragraph(txt('BRAND'), brand_style)])
        else:
            # Text-only brand
            brand_style = ParagraphStyle(
                'Brand',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2C3E50'),
                fontName=BOLD_FONT
            )
            header_elements.append([Paragraph(txt('BRAND'), brand_style)])
        
        # Company contact info (small text below logo/brand)
        contact_style = ParagraphStyle(
            'Contact',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#7F8C8D'),
            fontName=MAIN_FONT
        )
        
        contact_info = fix_text(company_info['address']) if lang == 'ar' else company_info['address']
        contact_phone = fix_text(company_info['phone']) if lang == 'ar' else company_info['phone']
        contact_email = company_info['email']
        
        contact_text = f"{contact_info}<br/>{contact_phone}<br/>{contact_email}"
        header_elements.append([Paragraph(contact_text, contact_style)])
        
        # Create header table
        header_tbl = Table(header_elements, colWidths=[6.5*inch])
        header_tbl.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(header_tbl)
        elements.append(Spacer(1, 0.3*inch))
        
        bill_to_text = [
            Paragraph(f"<b>{txt('BILL_TO')}</b>", styles['Normal']),
            Paragraph(fix_text(customer.get('name', 'Unknown Customer')), styles['Normal']),
            Paragraph(f"{txt('CUST_ID')} {customer.get('customer_id', '')}", styles['Normal']),
        ]
        
        # Status translation
        status_val = str(order.get('status')).upper()
        # Ensure status is translated if simple? Or just keep English/Reshape?
        # Let's keep DB value but reshape if needed
        status_val = fix_text(status_val) if lang == 'ar' else status_val
        
        invoice_info_text = [
            Paragraph(f"<b>{txt('INV_NO')}</b> {order.get('order_number')}", styles['Normal']),
            Paragraph(f"<b>{txt('DATE')}</b> {order.get('order_date')}", styles['Normal']),
            Paragraph(f"<b>{txt('STATUS')}</b> {status_val}", styles['Normal']),
        ]
        
        # If Arabic, maybe swap columns? (Right to Left layout)
        # Standard: Bill To (Right), Info (Left)?
        # For simplicity in PDF (which is absolute layout), we can swap the content passed to Table.
        
        if lang == 'ar':
            # Swap content: Info on Left (0), Bill To on Right (1) for visual RTL?
            # Or usually Bill To is on Right in Arabic?
            # Let's keep it simple: First col is Left, Second is Right.
            # In English: Left=BillTo, Right=Info.
            # In Arabic: Left=Info, Right=BillTo (visually reading RTL).
             header_data = [[invoice_info_text, bill_to_text]]
        else:
             header_data = [[bill_to_text, invoice_info_text]]
        
        header_table = Table(header_data, colWidths=[4*inch, 2.5*inch] if lang=='en' else [2.5*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # --- Items Table ---
        # Headers
        headers = [txt('ITEM'), txt('QTY'), txt('PRICE'), txt('TAX'), txt('DISC'), txt('TOTAL')]
        if lang == 'ar':
            # Reverse columns for RTL? 
            # E.g. Total, Disc, Tax, Price, Qty, Item
            headers = headers[::-1]
            
        data = [headers]
        
        for item in items:
            row = [
                fix_text(item.get('name', 'Unknown')),
                str(item.get('quantity', 0)),
                f"${item.get('unit_price', 0):.2f}",
                f"${item.get('tax_amount', 0):.2f}",
                f"${item.get('discount_amount', 0):.2f}",
                f"${item.get('total_price', 0):.2f}"
            ]
            if lang == 'ar':
                row = row[::-1]
            data.append(row)
            
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), # Center align safe for both
            ('FONTNAME', (0, 0), (-1, 0), BOLD_FONT),
            ('FONTNAME', (0, 1), (-1, -1), MAIN_FONT),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ])
        
        t = Table(data, colWidths=[2.5*inch, 0.8*inch, 1.0*inch, 0.8*inch, 0.8*inch, 1.0*inch] if lang=='en' else \
                  [1.0*inch, 0.8*inch, 0.8*inch, 1.0*inch, 0.8*inch, 2.5*inch]) # Adjusted widths for reversed
        t.setStyle(table_style)
        elements.append(t)
        
        # --- Totals ---
        elements.append(Spacer(1, 0.2*inch))
        
        sub = order.get('subtotal', 0)
        tax = order.get('total_tax', 0)
        disc = order.get('total_discount', 0)
        grant = order.get('total_amount', 0)
        
        totals_data = [
            [txt('SUB'), f"${sub:.2f}"],
            [txt('TAX'), f"${tax:.2f}"],
            [txt('DISC'), f"${disc:.2f}"],
            [txt('GRAND'), f"${grant:.2f}"]
        ]
        
        # For AR totals, if we swapped columns effectively, we want label right, value left?
        # Or standard table: Label | Value
        # In RTL: Value | Label?
        if lang == 'ar':
            totals_data = [[r[1], r[0]] for r in totals_data]
        
        totals_table = Table(totals_data, colWidths=[5.5*inch, 1.0*inch] if lang=='en' else [1.0*inch, 5.5*inch])
        
        # Alignments
        # EN: Label (Right), Value (Right) -- usually
        # AR: Value (Left), Label (Left)?
        align = 'RIGHT' if lang == 'en' else 'LEFT'
        
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), align),
            ('FONTNAME', (0, 0), (-1, -1), MAIN_FONT), # Apply Main Font (Arial) to all cells
            ('FONTNAME', (-1, -1), (-1, -1), BOLD_FONT), # Override last cell with Bold
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ]))
        elements.append(totals_table)
        
        # --- Professional Footer ---
        elements.append(Spacer(1, 0.4*inch))
        
        # Separator line
        line_table = Table([['']], colWidths=[6.5*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#CCCCCC')),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Footer style
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#555555'),
            fontName=MAIN_FONT,
            leading=12
        )
        
        footer_heading_style = ParagraphStyle(
            'FooterHeading',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2C3E50'),
            fontName=BOLD_FONT,
            spaceAfter=6
        )
        
        # Terms & Conditions
        terms_label = fix_text("الشروط والأحكام") if lang == 'ar' else "Terms & Conditions"
        terms_text = fix_text(invoice_config['terms']) if lang == 'ar' else invoice_config['terms']
        
        elements.append(Paragraph(f"<b>{terms_label}</b>", footer_heading_style))
        elements.append(Paragraph(terms_text, footer_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Payment Instructions
        payment_label = fix_text("تعليمات الدفع") if lang == 'ar' else "Payment Instructions"
        payment_text = fix_text(invoice_config['payment']) if lang == 'ar' else invoice_config['payment']
        
        elements.append(Paragraph(f"<b>{payment_label}</b>", footer_heading_style))
        elements.append(Paragraph(payment_text, footer_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Prepared by and Thank you
        if user_data:
            prep_text = f"{txt('PREP')} {fix_text(user_data.get('full_name', ''))}"
            elements.append(Paragraph(prep_text, footer_style))
        
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(txt('THANKS'), footer_style))
        
        # Tax ID at bottom
        tax_label = fix_text("الرقم الضريبي") if lang == 'ar' else "Tax ID"
        tax_id = fix_text(company_info['tax_id']) if lang == 'ar' else company_info['tax_id']
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(f"<i>{tax_label}: {tax_id}</i>", footer_style))
        
        doc.build(elements)
        return filepath
