# src/generator.py
import os
import sys

def generate_chessboard_pdf(config):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
    except ImportError:
        print("ReportLab library not found. Installing now...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas

    # Retrieve board properties from configuration file
    cols = config['board']['squares_x']
    rows = config['board']['squares_y']
    sq_size_mm = config['board']['square_size_mm']
    
    # Calculate expected internal intersections for calibration verification
    internal_x = cols - 1
    internal_y = rows - 1
    
    print(f"\nGenerating printable pattern matching physical specs:")
    print(f" - Grid Layout: {cols} x {rows} squares")
    print(f" - Square size: {sq_size_mm} mm")
    print(f" - Target detector size (internal intersections): ({internal_x}, {internal_y})")

    # Dimensions calculation (ReportLab uses points: 1 inch = 72 points, 1 cm = 28.3465 points)
    cm = 28.3465
    square_size = (sq_size_mm / 10.0) * cm

    width, height = landscape(A4)
    grid_width = cols * square_size
    grid_height = rows * square_size

    # Ensure the grid physically fits on an A4 sheet
    if grid_width > width or grid_height > height:
        print(f"\n[!] Warning: Grid size ({grid_width/cm:.1f}x{grid_height/cm:.1f} cm) exceeds A4 boundaries!")
        print("    Try reducing the number of squares or square_size_mm in config.yaml.")
        return

    # Calculate offsets to perfectly center the board on the A4 page
    x_offset = (width - grid_width) / 2
    y_offset = (height - grid_height) / 2

    # Create target directory and output PDF filename
    os.makedirs('data/pattern', exist_ok=True)
    pdf_filename = "data/pattern/perfect_calibration_chessboard.pdf"
    
    c = canvas.Canvas(pdf_filename, pagesize=landscape(A4))

    # Draw the alternating chessboard pattern
    for r in range(rows):
        for c_idx in range(cols):
            if (r + c_idx) % 2 == 1:
                c.setFillColorRGB(0, 0, 0)  # Black square
            else:
                c.setFillColorRGB(1, 1, 1)  # White square
                
            x = x_offset + (c_idx * square_size)
            y = y_offset + (r * square_size)
            
            c.rect(x, y, square_size, square_size, fill=1, stroke=0)

    c.save()
    print(f"Success! Perfect vector PDF generated: '{pdf_filename}'")