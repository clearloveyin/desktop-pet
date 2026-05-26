CHAT_WINDOW_STYLE = """
QWidget#ChatWindow {
    background-color: #F5FAF5;
}
QWidget#HeaderBar {
    background-color: #E8F5E8;
    border-bottom: 1px solid #D0E0D0;
}
QScrollArea#ChatScroll {
    border: none;
    background-color: transparent;
}
QWidget#ScrollContainer {
    background-color: transparent;
}
QWidget#InputContainer {
    background-color: #F5FAF5;
}
QFrame#UserBubble {
    background-color: #D4E9D6;
    border-radius: 16px;
    font-size: 13px;
    color: #3E5A3E;
}
QFrame#AiBubble {
    background-color: #FFFFFF;
    border: 1px solid #E0EBE0;
    border-radius: 16px;
    font-size: 13px;
    color: #3E5A3E;
}
QTextEdit#ChatInput {
    background-color: #FFFFFF;
    border: 1px solid #D0E0D0;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 13px;
    color: #3E5A3E;
}
QTextEdit#ChatInput:focus {
    border: 1px solid #8BC48B;
}
QPushButton#SendBtn {
    background-color: #8BC48B;
    color: white;
    border: none;
    border-radius: 16px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: bold;
    min-width: 60px;
}
QPushButton#SendBtn:hover {
    background-color: #6EAF6E;
}
QPushButton#SendBtn:pressed {
    background-color: #5A9E5A;
}
QPushButton#FileBtn {
    background-color: transparent;
    border: none;
    border-radius: 16px;
    padding: 4px 12px;
    font-size: 18px;
}
QPushButton#FileBtn:hover {
    background-color: #E8F5E8;
}
"""

MENU_STYLE = """
QMenu {
    background-color: #FAFCFA;
    border: 1px solid #D0E0D0;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 6px;
    color: #3E5A3E;
    font-size: 13px;
}
QMenu::item:selected {
    background-color: #D4E9D6;
    color: #2D4A2D;
}
QMenu::separator {
    height: 1px;
    background-color: #E0EBE0;
    margin: 4px 8px;
}
"""
