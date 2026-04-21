from zip_logic import METHOD_MSPAINT, METHOD_PILLOW
from gui import get_method_gui, get_pillow_settings, get_mspaint_settings

if __name__ == "__main__":
    selected_method = get_method_gui()

    if selected_method == METHOD_PILLOW:
        get_pillow_settings()
    elif selected_method == METHOD_MSPAINT:
        get_mspaint_settings()
