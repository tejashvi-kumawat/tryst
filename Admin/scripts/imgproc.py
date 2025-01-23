from PIL import Image
from io import BytesIO
from django.core.files import File


def compress(file, original_file_name):
    if hasattr(file, "temporary_file_path"):
        path = file.temporary_file_path()
        img = Image.open(path)
    else:
        img = Image.open(file)

    if img.mode == "RGBA":
        img = img.convert("RGB")

    width = 500
    height = int(500 * (img.size[1] / img.size[0]))
    img = img.resize((width, height), Image.Resampling.LANCZOS)

    if hasattr(file, "temporary_file_path"):
        img.save(path, optimize=True, quality=90)
        return file
    else:
        output_io_stream = BytesIO()
        img.save(output_io_stream, format="JPEG", optimize=True, quality=90)
        output_io_stream.seek(0)
        django_file = File(output_io_stream, name=original_file_name)
        return django_file
