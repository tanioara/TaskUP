import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import TaskUPApp

if __name__ == "__main__":
    db_path = "./tasks.db"
    app = QApplication(sys.argv)
    task_up_app = TaskUPApp(db_path)
    task_up_app.show()
    sys.exit(app.exec_())
