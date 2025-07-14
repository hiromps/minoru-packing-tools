import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# main.pyを実行
from src import main

if __name__ == "__main__":
    main.main()