import os
import tempfile


def test_read_txt():
    from tools import read_document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('Hello world')
        path = f.name
    try:
        assert read_document(path) == 'Hello world'
    finally:
        os.unlink(path)


def test_encode_image_returns_data_url():
    from tools import encode_image
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        f.write(b'fake-image-data')
        path = f.name
    try:
        data = encode_image(path)
        assert data.startswith('data:image/png;base64,')
    finally:
        os.unlink(path)

