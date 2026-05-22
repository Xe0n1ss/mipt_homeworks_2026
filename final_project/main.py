import importlib
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    app = importlib.import_module('final_project.app')
    app.run()


if __name__ == '__main__':
    main()
