import PyPDF2
import os

def extract_pdf(pdf_path, prefix, out_dir):
    reader = PyPDF2.PdfReader(pdf_path)
    total = len(reader.pages)
    print(f'Total pages: {total}')

    os.makedirs(out_dir, exist_ok=True)

    for i in range(total):
        text = reader.pages[i].extract_text()
        out_path = os.path.join(out_dir, f'{prefix}_p{i+1}.txt')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text or '[NO TEXT EXTRACTED]')
        print(f'Page {i+1}: {len(text or "")} chars')

    return total

if __name__ == '__main__':
    base = r'c:\Users\Administrator\Desktop\Intelligent-household-waste-sorting-and-disposal-assistance-system'
    out_dir = os.path.join(base, '.claude', 'pdf_text')

    # Extract design doc
    design_path = os.path.join(base, '文档包', '05-智能垃圾分类监管与积分运营系统-详细设计文档 (1).pdf')
    print('=== Design Doc ===')
    extract_pdf(design_path, 'design', out_dir)

    # Extract API doc
    api_path = os.path.join(base, '文档包', '06-智能垃圾分类监管与积分运营系统-接口文档.pdf')
    print('\n=== API Doc ===')
    extract_pdf(api_path, 'api', out_dir)
