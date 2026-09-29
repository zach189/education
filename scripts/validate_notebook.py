"""Execute the lesson in this interpreter's fresh kernel and save baseline outputs."""

import argparse
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import nbformat
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "notebook", nargs="?", default="notebooks/01_compute_business.ipynb"
    )
    path = root / parser.parse_args().notebook
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    with TemporaryDirectory(prefix="liquid-compute-check-") as directory:
        temporary = Path(directory)
        kernel_dir = temporary / "kernels" / "liquid-compute-check"
        kernel_dir.mkdir(parents=True)
        (kernel_dir / "kernel.json").write_text(
            json.dumps(
                {
                    "argv": [
                        sys.executable,
                        "-m",
                        "ipykernel_launcher",
                        "-f",
                        "{connection_file}",
                    ],
                    "display_name": "Liquid Compute validation",
                    "language": "python",
                }
            )
        )
        kernel = KernelManager(
            kernel_name="liquid-compute-check",
            kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernel_dir.parent)]),
        )
        environment = os.environ | {
            "IPYTHONDIR": str(temporary / "ipython"),
            "MPLCONFIGDIR": str(temporary / "matplotlib"),
        }
        client = NotebookClient(
            notebook,
            km=kernel,
            timeout=120,
            resources={"metadata": {"path": str(root)}},
        )
        try:
            client.execute(env=environment)
        finally:
            if kernel.has_kernel:
                kernel.shutdown_kernel(now=True)

    # Preserve worked outputs for reading without a kernel; remove cache chatter.
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.outputs = [
                output
                for output in cell.outputs
                if not (
                    output.output_type == "stream"
                    and output.get("text", "").strip()
                    == "Matplotlib is building the font cache; this may take a moment."
                )
            ]
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    print("Notebook schema and fresh-kernel execution passed; baseline outputs saved.")


if __name__ == "__main__":
    main()
