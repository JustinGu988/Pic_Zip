Pack .exe with PyInstaller:

-Install:
python -m venv pack_env
pack_env\Scripts\activate
pip install pyinstaller pillow
pyinstaller -F -w main.py

-Update:
python -m venv pack_env
pack_env\Scripts\activate
pyinstaller main.spec
