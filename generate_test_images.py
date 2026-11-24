
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

Path("tests").mkdir(exist_ok=True)


def create_image(file_path, text):
    image = Image.new(
    "RGB",
    (1800, 300),
    "white"
    )

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        r"C:\Windows\Fonts\arial.ttf",
        48
    )

    draw.text(
        (50, 100),
        text,
        fill="black",
        font=font
    )

    image.save(file_path)

    print(f"Created: {file_path}")


create_image(
    "tests/safe.png",
    "This is a normal image."
)

create_image(
    "tests/sensitive.png",
    "This contains WALLED_SENSITIVE"
)
