# Enhanced CLU IDE
# Written By Connor Campagna @ 2025
# UOFG STUDENT


import sys, os, subprocess, io, contextlib
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QTabWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTextEdit, QMenuBar,
    QMenu, QLabel, QSplitter, QListWidget, QSizePolicy, QStatusBar,
    QToolBar, QMessageBox, QDialog, QFormLayout, QLineEdit, QSpinBox,
    QCheckBox, QDialogButtonBox, QTreeWidget, QTreeWidgetItem, QFrame
)
from PySide6.QtGui import (
    QFont, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QColor, QIcon,
    QAction, QPalette, QPixmap, QShortcut, QKeySequence,QTextFormat
)
from PySide6.QtCore import Qt, QTimer, QSize, QThread, QObject, Signal
import traceback


# Enhanced keyword definitions with new features
KEYWORDS = {
    "control": ["function", "if", "otherwise", "end", "repeat", "foreach"],

    "logic": ["greater", "less", "equal", "greater_equal", "less_equal", "not_equal",
              "and", "or", "not", "true", "false"],  # Added boolean literals to logic

    "math": ["add", "subtract", "multiply", "divide"],

    "core": ["var", "is", "output", "of", "in"],

    "builtin": ["sum", "max", "min", "len", "sorted", "reversed", "average",
                "first", "last", "str", "int", "float", "bool", "type",  # Added bool
                "empty", "contains", "all", "any", "is_bool"]  # Added boolean functions
}


class CluHighlighterAdvanced(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.setup_formats()

    def setup_formats(self):
        # Define all formats
        def create_format(color, bold=False, italic=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(QFont.Bold)
            if italic:
                fmt.setFontItalic(True)
            return fmt

        self.formats = {
            'comment': create_format("#aaaaaa", italic=True),
            'string': create_format("#ff66cc"),
            'number': create_format("#66ff66"),
            'var_keyword': create_format("#80dfff", bold=True),
            'var_name': create_format("#e6e6fa", bold=True),
            'keyword': create_format("#ffcc00", bold=True),
            'builtin': create_format("#008000", bold=True),
            'operator': create_format("#ff69b4"),
        }

    def highlightBlock(self, text):
        # Step 1: Comments (highest priority)
        comment_pattern = QtCore.QRegularExpression(r"#.*")
        comment_iter = comment_pattern.globalMatch(text)
        while comment_iter.hasNext():
            match = comment_iter.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['comment'])

        # Step 2: Strings
        string_patterns = [r"'[^']*'", r'"[^"]*"']
        for pattern in string_patterns:
            regex = QtCore.QRegularExpression(pattern)
            iterator = regex.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['string'])

        # Step 3: Numbers
        number_patterns = [r"\b\d+\.\d+\b", r"\b\d+\b"]
        for pattern in number_patterns:
            regex = QtCore.QRegularExpression(pattern)
            iterator = regex.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['number'])

        # Step 4: Variable declarations (var keyword + variable name)
        var_pattern = QtCore.QRegularExpression(r"\bvar\s+(\w+)")
        var_iter = var_pattern.globalMatch(text)
        while var_iter.hasNext():
            match = var_iter.next()
            # Highlight "var" keyword
            var_start = match.capturedStart()
            var_end = text.find(' ', var_start) if ' ' in text[var_start:] else len(text)
            self.setFormat(var_start, 3, self.formats['var_keyword'])  # "var" is 3 characters

            # Highlight variable name
            var_name = match.captured(1)
            var_name_start = match.capturedStart(1)
            self.setFormat(var_name_start, len(var_name), self.formats['var_name'])

        # Step 5: Other keywords
        all_keywords = []
        for category, words in KEYWORDS.items():
            if category != "core":  # Skip core since we handle them specially
                all_keywords.extend(words)
            else:
                # Add core keywords except 'var' which we handled above
                all_keywords.extend([w for w in words if w != 'var'])

        for keyword in all_keywords:
            pattern = rf"\b{keyword}\b"
            regex = QtCore.QRegularExpression(pattern)
            iterator = regex.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['keyword'])

        # Step 6: Built-in functions with "of" syntax
        builtin_pattern = QtCore.QRegularExpression(
            r"\b(sum|max|min|len|sorted|reversed|average|first|last|str|int|float|type|empty|contains)\s+of\b")
        builtin_iter = builtin_pattern.globalMatch(text)
        while builtin_iter.hasNext():
            match = builtin_iter.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['builtin'])

        # Step 7: Operators
        operator_patterns = [r"[+\-*/=<>!,\[\]()]", r"->", r"\bis\b"]
        for pattern in operator_patterns:
            regex = QtCore.QRegularExpression(pattern)
            iterator = regex.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.formats['operator'])


class CodeRunner(QObject):
    finished = Signal(str, str, dict)  # Add dict for variables

    def __init__(self, code):
        super().__init__()
        self.code = code

    def run(self):
        try:
            from clucore import Parser, Interpreter, CLUError

            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            variables = {}  # Add this

            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                try:
                    lines = self.code.split('\n')
                    parser = Parser()
                    program = parser.parse(lines)

                    interpreter = Interpreter()
                    interpreter.load_program(program)
                    interpreter.run()

                    # CAPTURE VARIABLES - Add this line
                    variables = interpreter.variables.copy()

                except CLUError as e:
                    print(f"CLU Error: {e}")
                except Exception as e:
                    print(f"Runtime Error: {e}")
                    traceback.print_exc()

            stdout_text = stdout_capture.getvalue()
            stderr_text = stderr_capture.getvalue()

            # EMIT VARIABLES - Change this line
            self.finished.emit(stdout_text, stderr_text, variables)

        except Exception as e:
            self.finished.emit("", f"Failed to run code: {e}", {})  # Add empty dict

class VariableInspector(QWidget):
    """Panel to show current variables and their values"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Variables")
        label.setFont(QFont("Menlo", 10, QFont.Bold))
        layout.addWidget(label)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Variable", "Type", "Value"])
        self.tree.setAlternatingRowColors(True)
        layout.addWidget(self.tree)

        self.setLayout(layout)

    def update_variables(self, variables):
        """Update the variable display"""
        self.tree.clear()

        for name, value in variables.items():
            item = QTreeWidgetItem()
            item.setText(0, name)
            item.setText(1, type(value).__name__)

            # Format value display
            if isinstance(value, list):
                if len(value) > 5:
                    display_value = f"[{', '.join(map(str, value[:3]))}, ...] (length: {len(value)})"
                else:
                    display_value = str(value)
            elif isinstance(value, str):
                display_value = f"'{value}'"
            else:
                display_value = str(value)

            item.setText(2, display_value)
            self.tree.addTopLevelItem(item)


class TabEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.file_path = None
        self.is_modified = False

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Create editor with enhanced features
        self.editor = CodeEditor()
        self.editor.setFont(QFont("Menlo", 12))  # Better programming font
        self.editor.setTabStopDistance(40)  # 4 spaces

        # Set up syntax highlighting
        self.highlighter = CluHighlighterAdvanced(self.editor.document())

        # Connect modification signal
        self.editor.textChanged.connect(self.on_text_changed)

        layout.addWidget(self.editor)
        self.setLayout(layout)

    def on_text_changed(self):
        self.is_modified = True

    def get_content(self):
        return self.editor.toPlainText()

    def set_content(self, content):
        self.editor.setPlainText(content)
        self.is_modified = False


class PreferencesDialog(QDialog):
    """Settings dialog for the IDE"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # Font settings
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(12)
        layout.addRow("Font Size:", self.font_size)

        # Tab settings
        self.tab_width = QSpinBox()
        self.tab_width.setRange(2, 8)
        self.tab_width.setValue(4)
        layout.addRow("Tab Width:", self.tab_width)

        # Auto-save
        self.auto_save = QCheckBox()
        layout.addRow("Auto-save:", self.auto_save)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)

        self.setLayout(main_layout)


class CluIde(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_shortcuts()
        self.apply_dark_theme()  # Default to dark theme

    def init_ui(self):
        self.setWindowTitle("CLU IDE - Enhanced Edition")
        self.setGeometry(100, 100, 1400, 900)
        self.setWindowIcon(self.create_icon())

        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main splitter (horizontal)
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel for file explorer and variables
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        # Variable inspector
        self.variable_inspector = VariableInspector()
        left_layout.addWidget(self.variable_inspector)
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(300)

        # Center area with tabs and output
        center_widget = QWidget()
        center_layout = QVBoxLayout()

        # Tab widget for editors
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Output area
        output_splitter = QSplitter(Qt.Vertical)
        output_splitter.addWidget(self.tabs)

        # Output panel
        output_widget = QWidget()
        output_layout = QVBoxLayout()

        # Output controls
        controls_layout = QHBoxLayout()

        self.run_btn = QPushButton("▶ Run (F5)")
        self.run_btn.clicked.connect(self.run_code)
        self.run_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")

        self.clear_btn = QPushButton("🗑 Clear")
        self.clear_btn.clicked.connect(self.clear_output)

        self.debug_btn = QPushButton("🐛 Debug")
        self.debug_btn.clicked.connect(self.debug_code)

        controls_layout.addWidget(self.run_btn)
        controls_layout.addWidget(self.clear_btn)
        controls_layout.addWidget(self.debug_btn)
        controls_layout.addStretch()

        # Output text area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Menlo", 10))
        self.output.setFixedHeight(200)

        output_layout.addLayout(controls_layout)
        output_layout.addWidget(self.output)
        output_widget.setLayout(output_layout)

        output_splitter.addWidget(output_widget)
        output_splitter.setSizes([600, 200])

        center_layout.addWidget(output_splitter)
        center_widget.setLayout(center_layout)

        # Add to main splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_widget)
        main_splitter.setSizes([300, 1100])

        # Set main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(main_splitter)
        central_widget.setLayout(main_layout)

        # Create menus and toolbars
        self.create_menus()
        self.create_toolbar()
        self.create_status_bar()

        # Create initial tab
        self.new_tab()

    def create_icon(self):
        """Create a simple icon for the IDE"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor("#007acc"))
        return QIcon(pixmap)

    def create_menus(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Tab", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_action)

        open_action = QAction("&Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        preferences_action = QAction("&Preferences", self)
        preferences_action.triggered.connect(self.show_preferences)
        edit_menu.addAction(preferences_action)

        # Run menu
        run_menu = menubar.addMenu("&Run")

        run_action = QAction("&Run Code", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.triggered.connect(self.run_code)
        run_menu.addAction(run_action)

        debug_action = QAction("&Debug Code", self)
        debug_action.setShortcut(QKeySequence("F9"))
        debug_action.triggered.connect(self.debug_code)
        run_menu.addAction(debug_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        theme_menu = view_menu.addMenu("&Theme")

        light_action = QAction("&Light", self)
        light_action.triggered.connect(self.apply_light_theme)
        theme_menu.addAction(light_action)

        dark_action = QAction("&Dark", self)
        dark_action.triggered.connect(self.apply_dark_theme)
        theme_menu.addAction(dark_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About CLU IDE", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        syntax_action = QAction("CLU &Syntax Help", self)
        syntax_action.triggered.connect(self.show_syntax_help)
        help_menu.addAction(syntax_action)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add common actions to toolbar
        toolbar.addAction("New", self.new_tab)
        toolbar.addAction("Open", self.open_file)
        toolbar.addAction("Save", self.save_file)
        toolbar.addSeparator()
        toolbar.addAction("Run", self.run_code)
        toolbar.addAction("Debug", self.debug_code)

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_shortcuts(self):
        # Additional shortcuts
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_current_tab)
        QShortcut(QKeySequence("Ctrl+T"), self, self.new_tab)

    def new_tab(self):
        editor_widget = TabEditor()
        idx = self.tabs.addTab(editor_widget, f"Untitled {self.tabs.count() + 1}")
        self.tabs.setCurrentIndex(idx)
        self.status_bar.showMessage("New tab created")

    def get_current_editor(self):
        widget = self.tabs.currentWidget()
        return widget if isinstance(widget, TabEditor) else None

    def close_tab(self, index):
        if self.tabs.count() <= 1:
            return  # Keep at least one tab

        widget = self.tabs.widget(index)
        if widget and widget.is_modified:
            reply = QMessageBox.question(
                self, 'Close Tab',
                'This tab has unsaved changes. Close anyway?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        self.tabs.removeTab(index)

    def close_current_tab(self):
        self.close_tab(self.tabs.currentIndex())

    def on_tab_changed(self):
        editor = self.get_current_editor()
        if editor and hasattr(editor, 'file_path') and editor.file_path:
            self.status_bar.showMessage(f"Editing: {editor.file_path}")
        else:
            self.status_bar.showMessage("Ready")

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open CLU File", "",
            "CLU Files (*.clu);;All Files (*)"
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.new_tab()
                editor = self.get_current_editor()
                editor.set_content(content)
                editor.file_path = path
                self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(path))
                self.status_bar.showMessage(f"Opened: {path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open file: {e}")

    def save_file(self):
        editor = self.get_current_editor()
        if not editor:
            return

        if hasattr(editor, 'file_path') and editor.file_path:
            self._save_to_file(editor.file_path, editor.get_content())
            editor.is_modified = False
        else:
            self.save_file_as()

    def save_file_as(self):
        editor = self.get_current_editor()
        if not editor:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save CLU File", "",
            "CLU Files (*.clu);;All Files (*)"
        )
        if path:
            self._save_to_file(path, editor.get_content())
            editor.file_path = path
            editor.is_modified = False
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(path))

    def _save_to_file(self, path, content):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.status_bar.showMessage(f"Saved: {path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save file: {e}")

    def undo(self):
        editor = self.get_current_editor()
        if editor:
            editor.editor.undo()

    def redo(self):
        editor = self.get_current_editor()
        if editor:
            editor.editor.redo()

    def run_code(self):
        editor = self.get_current_editor()
        if not editor:
            return

        code = editor.get_content().strip()
        if not code:
            self.output.append("No code to run.")
            return

        self.status_bar.showMessage("Running code...")
        self.run_btn.setEnabled(False)

        # Clear previous output
        self.output.clear()
        self.output.append("=== Running CLU Code ===")

        # Run code in separate thread
        self.runner = CodeRunner(code)
        self.runner.finished.connect(self.on_code_finished)

        # Start execution
        QTimer.singleShot(0, self.runner.run)

    def on_code_finished(self, stdout, stderr, variables):  # Add variables parameter
        if stdout:
            self.output.append("Output:")
            self.output.append(stdout)

        if stderr:
            self.output.append("Errors:")
            self.output.setTextColor(QColor("red"))
            self.output.append(stderr)
            self.output.setTextColor(QColor("white"))

        if not stdout and not stderr:
            self.output.append("Code executed successfully (no output)")

        self.output.append("=== Execution Complete ===")

        # UPDATE VARIABLES - Add these lines
        self.variable_inspector.update_variables(variables)

        self.run_btn.setEnabled(True)
        self.status_bar.showMessage("Code execution finished")

    def debug_code(self):
        # Placeholder for debug functionality
        QMessageBox.information(
            self, "Debug Mode",
            "Debug mode would show step-by-step execution,\nvariable states, and execution flow.\n\nThis feature is coming soon!"
        )

    def clear_output(self):
        self.output.clear()
        self.status_bar.showMessage("Output cleared")

    def show_preferences(self):
        dialog = PreferencesDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Apply preferences
            font_size = dialog.font_size.value()
            for i in range(self.tabs.count()):
                editor = self.tabs.widget(i)
                if editor:
                    font = editor.editor.font()
                    font.setPointSize(font_size)
                    editor.editor.setFont(font)

    def show_about(self):
        QMessageBox.about(
            self, "About CLU IDE",
            "<h3>CLU IDE - Enhanced Edition</h3>"
            "<p>A comprehensive development environment for the CLU programming language.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Syntax highlighting</li>"
            "<li>Line numbers</li>"
            "<li>Variable inspection</li>"
            "<li>Integrated interpreter</li>"
            "<li>Dark/Light themes</li>"
            "</ul>"
            "<p>Created by Connor Campagna @ 2025<br>University of Glasgow Student</p>"
        )

    def show_syntax_help(self):
        help_text = """
<h3>CLU Syntax Quick Reference</h3>

<h4>Variables:</h4>
<pre>var name is value
var numbers is 1,2,3,4,5
var text is 'Hello World'</pre>

<h4>Output:</h4>
<pre>output 'Hello'
output sum of numbers</pre>

<h4>Functions:</h4>
<pre>function greet -> name
    output 'Hello ' + name
end</pre>

<h4>Conditionals:</h4>
<pre>if x greater 5
    output 'Big number'
otherwise
    output 'Small number'
end</pre>

<h4>Loops:</h4>
<pre>repeat x less 10
    output x
    var x is x add 1
end

foreach item in list
    output item
end</pre>

<h4>Built-in Functions:</h4>
<pre>sum of numbers
len of list
str of 42
int of '123'</pre>
        """

        msg = QMessageBox()
        msg.setWindowTitle("CLU Syntax Help")
        msg.setText(help_text)
        msg.setTextFormat(Qt.RichText)
        msg.exec()

    def apply_dark_theme(self):
        dark = QPalette()
        dark.setColor(QPalette.Window, QColor("#1e1e1e"))
        dark.setColor(QPalette.WindowText, Qt.white)
        dark.setColor(QPalette.Base, QColor("#2e2e2e"))
        dark.setColor(QPalette.AlternateBase, QColor("#1e1e1e"))
        dark.setColor(QPalette.ToolTipBase, Qt.white)
        dark.setColor(QPalette.ToolTipText, Qt.white)
        dark.setColor(QPalette.Text, Qt.white)
        dark.setColor(QPalette.Button, QColor("#2e2e2e"))
        dark.setColor(QPalette.ButtonText, Qt.white)
        dark.setColor(QPalette.Highlight, QColor("#007acc"))
        dark.setColor(QPalette.HighlightedText, Qt.white)
        QApplication.instance().setPalette(dark)
        self.status_bar.showMessage("Dark theme applied")

    def apply_light_theme(self):
        app = QApplication.instance()
        app.setPalette(app.style().standardPalette())
        self.status_bar.showMessage("Light theme applied")


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_area_width)
        self.updateRequest.connect(self.update_line_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_area_width(0)
        self.highlight_current_line()

    def update_line_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 15 + self.fontMetrics().horizontalAdvance("9") * digits

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QtCore.QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def update_line_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_area_width(0)

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#333333").lighter(50)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def line_number_area_paint(self, event):
        from PySide6 import QtCore, QtGui
        painter = QtGui.QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2e2e2e"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        height = self.fontMetrics().height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.lightGray)
                painter.drawText(
                    0, int(top), self.line_number_area.width() - 4, height,
                    Qt.AlignRight, number
                )

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint(event)


if __name__ == "__main__":
    from PySide6 import QtCore

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application info
    app.setApplicationName("CLU IDE")
    app.setApplicationVersion("2.0")

    window = CluIde()
    window.show()

    sys.exit(app.exec())