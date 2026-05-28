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
    background-color: #FFFFFF;
    border: 1px solid #D0E0D0;
    border-radius: 16px;
}
QWidget#InputBottomRow {
    background-color: transparent;
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
    background-color: transparent;
    border: none;
    font-size: 13px;
    color: #3E5A3E;
    padding: 4px 0px;
}
QPushButton#SendBtn {
    background-color: transparent;
    color: #3E5A3E;
    border: none;
    border-radius: 20px;
    min-width: 28px;
    min-height: 28px;
    font-size: 16px;
    font-weight: bold;
}
QPushButton#SendBtn:hover {
    background-color: #F0F0F0;
}
QPushButton#SendBtn:pressed {
    background-color: #E0E0E0;
}
QPushButton#FileBtn {
    background-color: transparent;
    border: none;
    border-radius: 20px;
    padding: 4px;
    font-size: 20px;
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
