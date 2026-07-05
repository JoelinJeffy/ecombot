"""
generate_sample_pdfs.py -- Generate sample PDF documents for Day 06 testing
----------------------------------------------------------------------------
Creates realistic eCommerce knowledge base PDFs with proper structure,
sections, and content that will be indexed into ChromaDB.

Run:
    python scripts/generate_sample_pdfs.py
"""

import logging
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
except ImportError:
    print("reportlab not installed. Install with: pip install reportlab")
    exit(1)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def create_faq_pdf():
    """Generate eCommerce FAQ PDF with sections."""
    output_path = DATA_DIR / "ecom_faq.pdf"
    DATA_DIR.mkdir(exist_ok=True)
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='darkblue',
        spaceAfter=12,
        spaceBefore=20
    )
    
    story = []
    
    # Title page
    story.append(Paragraph("E-Commerce Support FAQ", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Complete Customer Service Guide", styles['Heading3']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Version 3.0 | 2026", styles['Normal']))
    story.append(PageBreak())
    
    # Shipping & Delivery
    story.append(Paragraph("Shipping & Delivery", heading_style))
    story.append(Paragraph(
        "<b>Q: What are your shipping options?</b><br/>"
        "We offer standard shipping (5-7 business days) and express shipping (2-3 business days). "
        "Free standard shipping is available on orders over ₹1,000.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Q: How can I track my order?</b><br/>"
        "Once your order ships, you'll receive a tracking number via email. "
        "You can track your package on our website or the carrier's tracking page.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Q: Do you ship internationally?</b><br/>"
        "Currently, we only ship within India. International shipping support is planned for 2027.",
        styles['Normal']
    ))
    story.append(Spacer(1, 24))
    
    # Returns & Refunds
    story.append(Paragraph("Returns & Refunds", heading_style))
    story.append(Paragraph(
        "<b>Q: What is your return policy?</b><br/>"
        "We accept returns within 30 days of delivery for most products. "
        "Items must be unused, in original packaging, with all accessories and documentation. "
        "Refunds are processed within 7-10 business days after we receive the return.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Q: How do I initiate a return?</b><br/>"
        "Log into your account, go to Order History, select the item you want to return, "
        "and click 'Request Return'. You'll receive a prepaid return label via email within 24 hours.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Q: Are there any items that cannot be returned?</b><br/>"
        "Yes, software products, opened personal care items, custom-configured laptops, "
        "and clearance items marked 'Final Sale' are not eligible for return.",
        styles['Normal']
    ))
    story.append(Spacer(1, 24))
    
    # Warranty & Support
    story.append(Paragraph("Warranty & Support", heading_style))
    story.append(Paragraph(
        "<b>Q: What warranty do you offer?</b><br/>"
        "All electronics come with a manufacturer's warranty (typically 1 year). "
        "Extended warranty options are available at checkout. Warranty covers manufacturing defects "
        "but does not cover accidental damage or normal wear and tear.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Q: How do I file a warranty claim?</b><br/>"
        "Contact our support team with your order number and description of the issue. "
        "We'll guide you through troubleshooting steps. If the product is defective, "
        "we'll arrange repair or replacement at no charge.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Q: Do you offer technical support?</b><br/>"
        "Yes! Our technical support team is available Monday-Friday, 9 AM to 6 PM IST. "
        "You can reach us via phone, email, or live chat on our website.",
        styles['Normal']
    ))
    story.append(PageBreak())
    
    # Payment & Billing
    story.append(Paragraph("Payment & Billing", heading_style))
    story.append(Paragraph(
        "<b>Q: What payment methods do you accept?</b><br/>"
        "We accept credit cards (Visa, MasterCard, American Express), debit cards, "
        "UPI, net banking, and digital wallets like Paytm and PhonePe.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Q: Is my payment information secure?</b><br/>"
        "Absolutely. We use industry-standard SSL encryption and never store your complete "
        "card details. All payments are processed through secure, PCI-compliant gateways.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Q: Can I get an invoice for my purchase?</b><br/>"
        "Yes, an invoice is emailed to you immediately after your order is confirmed. "
        "You can also download invoices from your account's Order History section.",
        styles['Normal']
    ))
    story.append(Spacer(1, 24))
    
    # Account & Orders
    story.append(Paragraph("Account & Orders", heading_style))
    story.append(Paragraph(
        "<b>Q: Do I need an account to place an order?</b><br/>"
        "You can checkout as a guest, but creating an account lets you track orders, "
        "save addresses, earn rewards, and access faster customer support.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Q: How do I cancel my order?</b><br/>"
        "Orders can be cancelled within 1 hour of placement through your Order History page. "
        "After that, the order enters processing and cannot be cancelled, but you can "
        "return it once delivered.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Q: Can I modify my shipping address after ordering?</b><br/>"
        "If your order hasn't shipped yet, contact our support team immediately. "
        "We'll do our best to update the address. Once shipped, address changes are not possible.",
        styles['Normal']
    ))
    
    doc.build(story)
    logger.info(f"Generated FAQ PDF: {output_path}")
    print(f"✓ Created {output_path}")


def create_product_catalog_pdf():
    """Generate product catalog PDF with detailed specs."""
    output_path = DATA_DIR / "product_catalog.pdf"
    DATA_DIR.mkdir(exist_ok=True)
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='darkblue',
        spaceAfter=12,
        spaceBefore=20
    )
    
    story = []
    
    # Title
    story.append(Paragraph("Product Catalog 2026", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Electronics & Computing", styles['Heading3']))
    story.append(PageBreak())
    
    # Dell XPS 15
    story.append(Paragraph("Dell XPS 15 9530 Laptop", heading_style))
    story.append(Paragraph(
        "<b>Product ID:</b> DELL-XPS15-001<br/>"
        "<b>Price:</b> ₹89,999<br/>"
        "<b>Category:</b> Laptops",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Description:</b><br/>"
        "Premium ultrabook perfect for professionals and creators. Features a stunning "
        "15.6-inch InfinityEdge display, 12th Gen Intel processor, and dedicated NVIDIA graphics. "
        "Ideal for content creation, software development, and demanding productivity tasks.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Technical Specifications:</b>", styles['Normal']))
    story.append(Paragraph(
        "• Processor: Intel Core i7-12700H (14 cores, up to 4.7 GHz)<br/>"
        "• RAM: 16GB DDR5 4800MHz<br/>"
        "• Storage: 512GB NVMe SSD<br/>"
        "• Display: 15.6-inch FHD+ (1920x1200) IPS, 500 nits<br/>"
        "• Graphics: NVIDIA GeForce RTX 3050 Ti 4GB GDDR6<br/>"
        "• Operating System: Windows 11 Pro<br/>"
        "• Battery: 86Wh, up to 12 hours<br/>"
        "• Weight: 1.86 kg<br/>"
        "• Ports: 2x Thunderbolt 4, 2x USB-C, SD card reader, 3.5mm audio",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Warranty:</b> 1 year on-site service + 1 year accidental damage protection<br/>"
        "<b>In Box:</b> Laptop, 130W USB-C adapter, user manual, warranty card<br/>"
        "<b>Best For:</b> Professional work, video editing, software development",
        styles['Normal']
    ))
    story.append(PageBreak())
    
    # Sony WH-1000XM5
    story.append(Paragraph("Sony WH-1000XM5 Wireless Headphones", heading_style))
    story.append(Paragraph(
        "<b>Product ID:</b> SONY-WH1000XM5<br/>"
        "<b>Price:</b> ₹29,990<br/>"
        "<b>Category:</b> Audio",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Description:</b><br/>"
        "Industry-leading noise cancellation meets exceptional sound quality. "
        "Perfect for travelers, remote workers, and audiophiles who demand the best wireless experience.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Key Features:</b>", styles['Normal']))
    story.append(Paragraph(
        "• Advanced noise cancellation with 8 microphones<br/>"
        "• 30-hour battery life with quick charge (3 min = 3 hours)<br/>"
        "• Multipoint Bluetooth connection<br/>"
        "• Adaptive Sound Control<br/>"
        "• Hi-Res Audio and LDAC support<br/>"
        "• Speak-to-Chat technology<br/>"
        "• Premium soft-fit leather ear cushions",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Warranty:</b> 1 year manufacturer warranty<br/>"
        "<b>In Box:</b> Headphones, carrying case, USB-C cable, audio cable, adapter<br/>"
        "<b>Best For:</b> Travel, work-from-home, music enthusiasts",
        styles['Normal']
    ))
    story.append(PageBreak())
    
    # Samsung S24 Ultra
    story.append(Paragraph("Samsung Galaxy S24 Ultra", heading_style))
    story.append(Paragraph(
        "<b>Product ID:</b> SAMSUNG-S24U-512<br/>"
        "<b>Price:</b> ₹1,34,999<br/>"
        "<b>Category:</b> Smartphones",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Description:</b><br/>"
        "The ultimate flagship smartphone with AI-powered features, exceptional camera system, "
        "and all-day battery life. Includes built-in S Pen for productivity and creativity.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Specifications:</b>", styles['Normal']))
    story.append(Paragraph(
        "• Display: 6.8-inch Dynamic AMOLED 2X, QHD+, 120Hz<br/>"
        "• Processor: Snapdragon 8 Gen 3<br/>"
        "• RAM: 12GB | Storage: 512GB<br/>"
        "• Camera: 200MP main + 50MP telephoto + 12MP ultrawide + 10MP telephoto<br/>"
        "• Front Camera: 12MP<br/>"
        "• Battery: 5000mAh with 45W fast charging<br/>"
        "• S Pen: Built-in with low latency<br/>"
        "• Titanium frame with Gorilla Armor glass",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Warranty:</b> 1 year manufacturer warranty<br/>"
        "<b>In Box:</b> Phone, S Pen, USB-C cable, SIM ejector tool<br/>"
        "<b>Best For:</b> Photography, gaming, business professionals",
        styles['Normal']
    ))
    
    doc.build(story)
    logger.info(f"Generated product catalog PDF: {output_path}")
    print(f"✓ Created {output_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Generating sample PDFs for Day 06...")
    create_faq_pdf()
    create_product_catalog_pdf()
    print("\n✓ PDF generation complete!")
    print(f"  Files created in: {DATA_DIR}")
