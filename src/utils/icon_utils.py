from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os


icon_shape = {
    "background_color": (0, 122, 255),  # 蓝色背景
    "text_color": (255, 255, 255),      # 白色文字
    "icon_color": (255, 255, 255),      # 白色图标
    "text": "工作工具包",                  # 显示文本
    "rounded_corners": True,            # 是否启用圆角
    "corner_radius": 15,                # 圆角半径
}


def generate_icon(config: dict, output_path: str = "icons"):
    """
    Generate an application icon according to the given configuration.

    :param dict config:
        Icon configuration dictionary. Example::

            {
                "background_color": (0, 122, 255),   # RGB background color
                "text_color": (255, 255, 255),       # RGB text color
                "icon_color": (255, 255, 255),       # RGB icon color
                "text": "工作工具包",                   # Displayed text
                "rounded_corners": True,             # Whether to use rounded corners
                "corner_radius": 15                  # Radius for rounded corners
            }

    :param str output_path:
        Directory path where the generated icons will be saved. Default is ``"icons"``.

    :returns: Paths of the generated PNG and ICO files.
    :rtype: tuple[pathlib.Path, pathlib.Path]

    The function performs the following steps:

    1. Create a 512x512 transparent canvas.
    2. Draw background (rounded rectangle or plain rectangle).
    3. Draw a simple symbolic icon (rectangular shape).
    4. Add text below the icon.
    5. Save the result as both PNG and multi-size ICO files.
    """
    # Create a transparent image (512x512)
    size = (512, 512)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw background (rounded or rectangular)
    if config.get("rounded_corners", False):
        radius = config.get("corner_radius", 0)
        background = Image.new("RGBA", size, config["background_color"] + (255,))
        mask = Image.new("L", size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), size], radius=radius, fill=255)
        image.paste(background, (0, 0), mask)
    else:
        draw.rectangle([(0, 0), size], fill=config["background_color"])

    # Draw simplified icon (two rectangles combined)
    icon_width = size[0] * 0.6
    icon_height = size[1] * 0.3
    icon_left = (size[0] - icon_width) / 2
    icon_top = size[1] * 0.2

    # Horizontal bar
    draw.rectangle(
        [(icon_left, icon_top), (icon_left + icon_width, icon_top + icon_height * 0.3)],
        fill=config["icon_color"]
    )
    # Vertical bar
    draw.rectangle(
        [(icon_left, icon_top), (icon_left + icon_width * 0.2, icon_top + icon_height)],
        fill=config["icon_color"]
    )

    # Add text
    try:
        font_size = int(size[0] * 0.15)
        font = ImageFont.truetype("simhei.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
        font_size = int(size[0] * 0.1)

    text = config.get("text", "")
    if hasattr(draw, 'textsize'):
        text_width, text_height = draw.textsize(text, font=font)
    elif hasattr(font, 'getbbox'):
        bbox = font.getbbox(text)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    else:
        text_width, text_height = font.getsize(text) if hasattr(font, 'getsize') else (font_size * len(text), font_size)

    text_left = (size[0] - text_width) / 2
    text_top = size[1] * 0.65
    draw.text((text_left, text_top), text, font=font, fill=config["text_color"])

    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)

    # Save PNG file
    png_file_path = Path(output_path) / "app_icon.png"
    image.save(png_file_path.as_posix())

    # Save ICO file with multiple sizes
    ico_file_path = Path(output_path) / "app_icon.ico"
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = [image.resize(size, Image.LANCZOS) for size in icon_sizes]
    icons[0].save(
        ico_file_path.as_posix(),
        sizes=[(ic.width, ic.height) for ic in icons],
        append_images=icons[1:]
    )

    return png_file_path, ico_file_path
