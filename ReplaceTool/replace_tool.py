from maya import cmds
from PySide.QtCore import Qt, QRegExp
from PySide.QtGui import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRegExpValidator, QLineEdit, QPushButton


def undo(func):
    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            ret = func(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return ret
    return wrapper


class ReplaceTool(QDialog):
    def __init__(self):
        super(ReplaceTool, self).__init__()

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Replace Tool')
        self.setFixedHeight(100)
        self.setFixedWidth(320)

        lyt_main = QVBoxLayout()

        lbl_find = QLabel('Find:')
        lbl_find.setFixedWidth(55)

        self.ledit_find = QLineEdit()

        lbl_replace = QLabel('Replace:')
        lbl_replace.setFixedWidth(55)

        self.ledit_replace = QLineEdit()

        reg_ex = QRegExp("[a-zA-Z_]+")
        text_validator = QRegExpValidator(reg_ex, self.ledit_find)
        self.ledit_find.setValidator(text_validator)
        self.ledit_replace.setValidator(text_validator)

        lyt_find = QHBoxLayout()
        lyt_find.addWidget(lbl_find)
        lyt_find.addWidget(self.ledit_find)

        lyt_main.addLayout(lyt_find)

        lyt_replace = QHBoxLayout()
        lyt_replace.addWidget(lbl_replace)
        lyt_replace.addWidget(self.ledit_replace)

        lyt_main.addLayout(lyt_replace)

        btn_submit = QPushButton('Submit')
        btn_submit.setFixedHeight(20)
        btn_submit.setFixedWidth(55)

        lyt_submit_button = QHBoxLayout()
        lyt_submit_button.setAlignment(Qt.AlignRight)
        lyt_submit_button.addWidget(btn_submit)

        lyt_main.addLayout(lyt_submit_button)

        self.setLayout(lyt_main)

        btn_submit.clicked.connect(self.submit)

    @undo
    def submit(self):
        find_text = str(self.ledit_find.text())
        replace_text = str(self.ledit_replace.text())

        selection = cmds.ls(sl=True)

        # if there are things selected, only replace the names for selection, else replace everything

        if selection:
            nodes = selection
        else:
            nodes = cmds.ls()

        nodes = [x for x in nodes if find_text in x]

        shapes = cmds.ls(nodes, s=True)
        shapes = [x for x in shapes if find_text in x]
    
        new_nodes_names = []
        failed_nodes = []

        for node in nodes:
            try:
                new_nodes_names.append((node, cmds.rename(node, '__tmp__')))
            except RuntimeError:
                failed_nodes.append(node)
    
        for shape in shapes:
            if not cmds.objExists(shape):
                try:
                    new_name = cmds.rename(shape, shape.replace(find_text, '__tmp__'))
                    new_nodes_names.append((shape, new_name))
                except RuntimeError:
                    failed_nodes.append(node)
    
        new_names = []
        for name, new_node in new_nodes_names:
            new_name = name.replace(find_text, replace_text)
            new_names.append(cmds.rename(new_node, new_name))

        if failed_nodes:
            print 'The following nodes failed to be renamed:'
            for f_node in failed_nodes:
                print str(f_node)

tool = ReplaceTool()
tool.show()
