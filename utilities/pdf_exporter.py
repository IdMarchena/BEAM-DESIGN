from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import filedialog, messagebox

def export_to_pdf(content, filename=None):
    if not filename:
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar como PDF"
        )
    
    if not filename:
        return
        
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        text = c.beginText(40, height - 40)
        text.setFont("Helvetica", 10)
        
        for line in content.split("\n"):
            text.textLine(line)
            if text.getY() < 40:  # Si llega al final de la página
                c.drawText(text)
                c.showPage()
                text = c.beginText(40, height - 40)
                text.setFont("Helvetica", 10)
        
        c.drawText(text)
        c.save()
        messagebox.showinfo("Éxito", "PDF generado correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF: {str(e)}")