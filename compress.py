import os
import sys
import subprocess
import tempfile


def compress(source: str, target: str, power: int = 0):
    """
    Compress a given PDF file

    :param str source: source PDF file
    :param str target: target location to save the compressed PDF
    :param int power: power of the compression. Default value is 0. This can be 0: default, 1: prepress, 2: printer, 3: ebook, 4: screen
    """

    quality = {
        0: "/default",
        1: "/prepress",
        2: "/printer",
        3: "/ebook",
        4: "/screen",
    }

    if not os.path.isfile(source):
        print("Error: invalid path for input PDF file")
        sys.exit(1)

    if source.split(".")[-1].lower() != "pdf":
        print("Error: input file is not a PDF")
        sys.exit(1)

    subprocess.call(
        [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS={}".format(quality[power]),
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-sOutputFile={}".format(target),
            source,
        ],
    )


def __compress(result, target: str, power: int):
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = f"{tmp_dir}/tmp.pdf"
        with open(tmp_file, "wb") as file:
            file.write(result)
        compress(tmp_file, target, power)

