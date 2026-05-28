import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

app = QApplication(sys.argv)


def test_message_bubble_creation():
    from chat_window import MessageBubble

    bubble = MessageBubble('Hello World', is_user=True)
    assert bubble.label.text() == 'Hello World'
    assert bubble.objectName() == 'UserBubble'
    assert bubble.label.wordWrap() is True
    assert bubble.label.maximumWidth() == 400


def test_ai_bubble_creation():
    from chat_window import MessageBubble

    bubble = MessageBubble('小黑回复', is_user=False)
    assert bubble.objectName() == 'AiBubble'
    assert bubble.label.wordWrap() is True


def test_bubble_short_text():
    from chat_window import MessageBubble

    bubble = MessageBubble('Hi')
    bubble.show()
    # Force layout to compute size
    bubble.activateWindow()
    app.processEvents()
    label = bubble.label
    # Word wrap on, maximum width should constrain it
    assert label.maximumWidth() == 400
    assert label.wordWrap() is True
    bubble.hide()
    assert True  # No crash


def test_bubble_long_text():
    from chat_window import MessageBubble

    long_text = 'A' * 500
    bubble = MessageBubble(long_text)
    bubble.show()
    app.processEvents()
    label = bubble.label
    assert label.wordWrap() is True
    assert label.maximumWidth() == 400
    # Text should wrap into multiple lines
    text = label.text()
    assert len(text) == 500
    bubble.hide()
    assert True


def test_bubble_updateGeometry():
    from chat_window import MessageBubble

    bubble = MessageBubble('initial')
    bubble.show()
    app.processEvents()
    # Simulate streaming update
    bubble.label.setText('initial longer text that should cause reflow')
    bubble.label.updateGeometry()
    app.processEvents()
    assert bubble.label.text() == 'initial longer text that should cause reflow'
    bubble.hide()


def test_chat_window_creation():
    from chat_window import ChatWindow

    w = ChatWindow()
    assert w.windowTitle() == '罗小黑聊天'
    w.close()


def test_add_messages():
    from chat_window import ChatWindow

    w = ChatWindow()
    w.show()
    app.processEvents()
    w.add_message('Hello', is_user=True)
    w.add_message('World', is_user=False)
    app.processEvents()
    # Two bubbles should be added + no current_bubble
    count = w._scroll_layout.count()
    assert count >= 2
    w.close()
    assert True


def test_stream_update():
    from chat_window import ChatWindow

    w = ChatWindow()
    w.show()
    app.processEvents()
    from chat_window import MessageBubble
    w._current_bubble = MessageBubble('')
    w._scroll_layout.addWidget(w._current_bubble, 0, Qt.AlignmentFlag.AlignLeft)
    w._stream_buffer = 'test stream'
    app.processEvents()
    w._update_stream()
    assert w._current_bubble.label.text() == 'test stream'
    w.close()


if __name__ == '__main__':
    test_message_bubble_creation()
    test_ai_bubble_creation()
    test_bubble_short_text()
    test_bubble_long_text()
    test_bubble_updateGeometry()
    test_chat_window_creation()
    test_add_messages()
    test_stream_update()
    print('All chat window tests passed!')
