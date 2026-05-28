import os


def read_document(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.txt', '.md', '.csv', '.json', '.py', '.js', '.ts', '.html', '.css'):
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    elif ext == '.pdf':
        import fitz
        try:
            doc = fitz.open(path)
        except Exception as e:
            return f'PDF 文件读取失败：{e}'
        text = ''.join(page.get_text() for page in doc)
        doc.close()
        return text
    else:
        return f'Unsupported file type: {ext}'






