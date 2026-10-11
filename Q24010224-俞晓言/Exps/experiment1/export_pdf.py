"""Export the Markdown report with original screenshot viewports into an A4 PDF."""
from pathlib import Path
import re
from html import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('CJK', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
WIDTH = 483
styles = {
    'body': ParagraphStyle('body', fontName='CJK', fontSize=10, leading=16, spaceAfter=8, wordWrap='CJK'),
    'h1': ParagraphStyle('h1', fontName='CJK', fontSize=22, leading=31, spaceAfter=20, textColor=colors.HexColor('#18324b')),
    'h2': ParagraphStyle('h2', fontName='CJK', fontSize=17, leading=25, spaceAfter=12, textColor=colors.HexColor('#18324b')),
    'code': ParagraphStyle('code', fontName='CJK', fontSize=8.4, leading=12, wordWrap='CJK'),
    'cell': ParagraphStyle('cell', fontName='CJK', fontSize=8.3, leading=12, wordWrap='CJK'),
    'caption': ParagraphStyle('caption', fontName='CJK', fontSize=8, leading=12, textColor=colors.HexColor('#526275'), spaceAfter=8),
}

def inline(text):
    parts = re.split(r'(`[^`]+`)', text)
    return ''.join(
        '<font color="#285475">'+escape(part[1:-1], quote=False)+'</font>'
        if part.startswith('`') and part.endswith('`') else escape(part, quote=False)
        for part in parts
    )

class Screenshot(Flowable):
    """Clip empty desktop space in PDF only; source screenshot files stay intact."""
    def __init__(self, path, height):
        Flowable.__init__(self)
        self.path = str(path)
        self.sx, self.sy, self.sw, self.sh = 50, 143, 850, height
        self.width = WIDTH
        self.height = height * WIDTH / self.sw
    def draw(self):
        c = self.canv
        c.saveState()
        p = c.beginPath(); p.rect(0, 0, self.width, self.height)
        c.clipPath(p, stroke=0, fill=0)
        scale = self.width/self.sw
        c.scale(scale, scale)
        c.drawImage(self.path, -self.sx, self.sh+self.sy-1080, width=1600, height=1080)
        c.restoreState()

def footer(c, doc):
    c.setFont('CJK', 8)
    c.setFillColor(colors.HexColor('#64748b'))
    c.drawString(56, 28, 'Q24010224 俞晓言 | Experiment 1')
    c.drawRightString(539, 28, str(doc.page))

def main():
    lines=(ROOT/'实验报告.md').read_text().splitlines()
    story=[]; i=0
    shot_heights=[325,315,255,400,510,365]
    while i<len(lines):
        line=lines[i]
        if not line.strip(): i+=1; continue
        if line.startswith('# '):
            story.append(Paragraph(escape(line[2:]), styles['h1']))
        elif line.startswith('## '):
            story.extend([PageBreak(), Paragraph(escape(line[3:]), styles['h2'])])
        elif line.startswith('```'):
            block=[]; i+=1
            while i<len(lines) and not lines[i].startswith('```'):
                block.append(escape(lines[i]).replace(' ','&#160;')); i+=1
            code=Paragraph('<br/>'.join(block),styles['code'])
            box=Table([[code]],colWidths=[WIDTH])
            box.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f1f5f9')),('BOX',(0,0),(-1,-1),.4,colors.HexColor('#dbe3eb')),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
            story.extend([box,Spacer(1,10)])
        elif line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[c.strip() for c in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',c) for c in cells):
                    rows.append([Paragraph(inline(c),styles['cell']) for c in cells])
                i+=1
            i-=1
            widths=[155,100,228] if len(rows[0])==3 else [165,318]
            t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5edf5')),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#cbd5e1')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.extend([t,Spacer(1,10)])
        elif line.startswith('!['):
            match=re.match(r'!\[(.*?)\]\((.*?)\)',line)
            label,path=match.groups(); n=int(Path(path).name[:2])-1
            story.append(KeepTogether([Paragraph(inline(label),styles['caption']),Screenshot(ROOT/path,shot_heights[n])]))
        else:
            text=('• '+line[2:]) if line.startswith('- ') else line
            story.append(Paragraph(inline(text),styles['body']))
        i+=1
    out=ROOT/'Experiment1-Q24010224-俞晓言-实验报告.pdf'
    doc=SimpleDocTemplate(str(out),pagesize=(595.28,841.89),rightMargin=56,leftMargin=56,topMargin=45,bottomMargin=45,title='Experiment 1：Linux 基础操作综合实验',author='俞晓言 Q24010224')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(out)

if __name__=='__main__': main()
