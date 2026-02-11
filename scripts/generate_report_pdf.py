from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import os

MD_PATH = 'reports/eda_report.md'
OUT_PDF = 'reports/eda_report.pdf'

def read_markdown(md_path):
    with open(md_path, 'r') as f:
        return f.read()


def md_to_para_lines(md_text):
    # Very lightweight markdown to paragraphs: headings (#) and bullets (-)
    lines = md_text.splitlines()
    out = []
    for L in lines:
        s = L.strip()
        if not s:
            out.append(('\n', 'normal'))
            continue
        if s.startswith('## '):
            out.append((s[3:], 'heading2'))
        elif s.startswith('# '):
            out.append((s[2:], 'title'))
        elif s.startswith('- '):
            out.append((s[2:], 'bullet'))
        else:
            out.append((s, 'normal'))
    return out


def build_pdf(md_path, out_pdf):
    text = read_markdown(md_path)
    elems = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='title', fontSize=18, leading=22))
    styles.add(ParagraphStyle(name='heading2', fontSize=14, leading=18))
    styles.add(ParagraphStyle(name='bullet', leftIndent=12, bulletIndent=6))

    for t,kind in md_to_para_lines(text):
        if kind=='bullet':
            p = Paragraph('&bull; ' + t, styles['bullet'])
        elif kind=='title':
            p = Paragraph(t, styles['title'])
        elif kind=='heading2':
            p = Paragraph(t, styles['heading2'])
        else:
            p = Paragraph(t, styles['Normal'])
        elems.append(p)
        elems.append(Spacer(1,4))

    # Try to attach available images from reports folder
    imgs = [f for f in os.listdir('reports') if f.lower().endswith('.png')]
    for im in sorted(imgs):
        elems.append(Spacer(1,8))
        img_path = os.path.join('reports', im)
        try:
            im_obj = Image(img_path, width=160*mm)
            elems.append(im_obj)
            elems.append(Spacer(1,8))
        except Exception:
            pass

    doc = SimpleDocTemplate(out_pdf, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    doc.build(elems)

if __name__ == '__main__':
    if not os.path.exists(MD_PATH):
        print('Markdown not found:', MD_PATH)
    else:
        build_pdf(MD_PATH, OUT_PDF)
        print('Created PDF:', OUT_PDF)
