import base64
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


def encode_image(path: str) -> str:
    with open(path, 'rb') as f:
        data = f.read()
    ext = os.path.splitext(path)[1].lower().lstrip('.')
    mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'png': 'image/png', 'gif': 'image/gif',
            'webp': 'image/webp'}.get(ext, 'image/png')
    b64 = base64.b64encode(data).decode('ascii')
    return f'data:{mime};base64,{b64}'



