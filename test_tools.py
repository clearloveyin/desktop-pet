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




