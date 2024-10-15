from os import path


class GlobalVariables:
    # Scrolling
    MIN_SCROLL_SPEED = 5
    DEFAULT_SCROLL_SPEED = 10
    DEFAULT_MAX_SCROLL_SPEED = 25
    MAX_SCROLL_SPEED = 100
    SCROLL_SPEED_INCREMENT = 5
    EMPTY_SCROLL_VALUE = 60
    # DPI
    MIN_DPI_VALUE = 50
    DEFAULT_DPI_VALUE = 100
    MAX_DPI_VALUE = 150
    # Sizes and graphics
    ICON_SIZE = 32
    # Directory names
    DATA = 'data'
    TEMP = 'temp'
    # File names and localisation
    TEMPORARY_IMAGE = path.join(DATA, 'temporary_image.jpg')
    LOGO_ICON = path.join(DATA, 'logo.png')
    ADD_ICON = path.join(DATA, 'add.png')
    REMOVE_ICON = path.join(DATA, 'remove.png')
    DOWNLOAD_ICON = path.join(DATA, 'download.png')
    RESET_ICON = path.join(DATA, 'reset.png')
    SETTINGS_ICON = path.join(DATA, 'settings.png')
    ROTATE_ICON = path.join(DATA, 'rotate.png')
    SETTINGS = path.join(DATA, "settings.json")
    # File extensions
    PDF = '.pdf'
    # Other
    FONT = 'arial.ttf'
