"""Prepare PNG or JPEG artwork for the eBadge's 320 x 240 display.

The image is resized proportionally without enlarging smaller images and saved
as an uncompressed 24-bit BMP for the MicroPython display helper.

Usage::

    python resize_image.py byui-cse.png
    python resize_image.py photo.jpg --output photo_badge.bmp
"""

import argparse
from pathlib import Path


DISPLAY_SIZE = (320, 240)
SUPPORTED_SUFFIXES = (".png", ".jpg", ".jpeg")


def resize_image(source, destination=None):
    """Resize a PNG/JPEG to fit the badge display and save a 24-bit BMP.

    Smaller images are not enlarged. The default output is written beside the
    source as ``<source-name>_badge.bmp``.

    Args:
        source: Input PNG, JPG, or JPEG file path.
        destination: Optional output BMP path.

    Returns:
        The output path as a :class:`pathlib.Path`.

    Raises:
        ImportError: If Pillow is not installed on the host computer.
        ValueError: If the source or destination extension is unsupported.
        OSError: If an image cannot be opened or written.
    """
    try:
        from PIL import Image
    except ImportError as error:
        raise ImportError(
            "Image conversion requires Pillow. Install it with "
            "'python -m pip install pillow'."
        ) from error

    source = Path(source)
    if source.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError("input must be a PNG, JPG, or JPEG image")

    if destination is None:
        destination = source.with_name(source.stem + "_badge.bmp")
    else:
        destination = Path(destination)
    if destination.suffix.lower() != ".bmp":
        raise ValueError("output filename must end in .bmp")

    resampling = getattr(Image, "Resampling", Image).LANCZOS
    with Image.open(source) as source_image:
        rgba = source_image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
        image = Image.alpha_composite(background, rgba).convert("RGB")
        image.thumbnail(DISPLAY_SIZE, resampling)
        image.save(destination, format="BMP")

    return destination


def main():
    """Run the image converter from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="source PNG, JPG, or JPEG image")
    parser.add_argument(
        "-o",
        "--output",
        help="output BMP path (default: <source-name>_badge.bmp)",
    )
    args = parser.parse_args()

    try:
        output = resize_image(args.image, args.output)
    except (ImportError, OSError, ValueError) as error:
        parser.error(str(error))
    print("Saved {}".format(output))


if __name__ == "__main__":
    main()
