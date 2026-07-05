"""
PDF commands
~~~~~~~~~~~~

Utilities for working with PDF files.
"""

import shutil
import subprocess
from pathlib import Path

import invoke

PDF_QUALITIES = {"screen", "ebook", "printer", "prepress", "default"}


@invoke.task(
    aliases=["compres"],
    help={
        "source": "PDF file to compress",
        "output": "Output PDF file (defaults to <name>.compressed.pdf)",
        "quality": "Ghostscript quality: screen, ebook, printer, prepress, default",
        "lossless": (
            "Use pypdf stream/object compression instead of image recompression"
        ),
    },
)
def compress(ctx, source=None, output=None, quality="ebook", lossless=False):
    """
    Compress a PDF file.

    Args:
        source: PDF file to compress
        output: Output PDF file (defaults to <name>.compressed.pdf)
        quality: Ghostscript quality preset
        lossless: Use lossless pypdf compression instead of Ghostscript
    """
    if source is None:
        print("Error: missing required option: --source")
        raise SystemExit(1)

    source_path, output_path = _paths(source, output)

    if lossless:
        _compress_lossless(source_path, output_path)
    else:
        _compress_with_ghostscript(source_path, output_path, quality)

    _print_size_report(source_path, output_path)


def _paths(source, output):
    source_path = Path(source).expanduser()
    if not source_path.exists():
        print(f"Error: PDF not found: {source_path}")
        raise SystemExit(1)

    output_path = (
        Path(output).expanduser()
        if output
        else source_path.with_suffix(".compressed.pdf")
    )
    if output_path.resolve() == source_path.resolve():
        print("Error: output must be different from source")
        raise SystemExit(1)

    return source_path, output_path


def _compress_with_ghostscript(source_path, output_path, quality):
    if quality not in PDF_QUALITIES:
        choices = ", ".join(sorted(PDF_QUALITIES))
        print(f"Error: quality must be one of: {choices}")
        raise SystemExit(1)

    gs = shutil.which("gs")
    if gs is None:
        print("Missing dependency: Ghostscript is required for image recompression.")
        print("Install it with `brew install ghostscript`, or use `--lossless`.")
        raise SystemExit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            gs,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS=/{quality}",
            "-dDetectDuplicateImages=true",
            "-dCompressFonts=true",
            "-dSubsetFonts=true",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            str(source_path),
        ],
        check=True,
    )


def _compress_lossless(source_path, output_path):
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("Missing dependency: install with `pip install 'stool[pdf]'`")
        raise SystemExit(1)

    reader = PdfReader(source_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)
        writer.pages[-1].compress_content_streams()

    writer.compress_identical_objects()

    if reader.metadata:
        writer.add_metadata(
            {key: str(value) for key, value in reader.metadata.items() if value}
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as pdf_file:
        writer.write(pdf_file)


def _print_size_report(source_path, output_path):
    before = source_path.stat().st_size
    after = output_path.stat().st_size
    saved = before - after

    print(f"Compressed {source_path} -> {output_path}")
    if saved > 0:
        percent = (saved / before * 100) if before else 0
        print(f"Size: {before:,} -> {after:,} bytes ({percent:.1f}% saved)")
    elif saved == 0:
        print(f"Size: {before:,} -> {after:,} bytes (unchanged)")
        print("No reduction: this PDF is probably already compressed.")
    else:
        percent = (-saved / before * 100) if before else 0
        print(f"Size: {before:,} -> {after:,} bytes ({percent:.1f}% larger)")
        print("No reduction: try a lower --quality or keep the original.")
