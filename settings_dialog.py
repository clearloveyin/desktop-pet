from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDialogButtonBox, QMessageBox,
)
from settings import load, save


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('API 配置')
        self.resize(480, 400)
        self._config = load()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._endpoint = QLineEdit(self._config['api_endpoint'])
        form.addRow('API Endpoint:', self._endpoint)

        self._api_key = QLineEdit(self._config['api_key'])
        self._api_key.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow('API Key:', self._api_key)

        self._model = QLineEdit(self._config['model'])
        form.addRow('Model:', self._model)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_save(self):
        config = {
            'api_endpoint': self._endpoint.text().strip(),
            'api_key': self._api_key.text().strip(),
            'model': self._model.text().strip(),
        }
        if not config['api_endpoint']:
            QMessageBox.warning(self, '错误', 'API Endpoint 不能为空')
            return
        if not config['api_key']:
            QMessageBox.warning(self, '错误', 'API Key 不能为空')
            return
        save(config)
        self._config = config
        self.accept()

    @property
    def config(self) -> dict:
        return self._config
