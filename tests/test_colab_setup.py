"""Check the shared setup cell without network access or package installation."""

import subprocess
import sys
from pathlib import Path
from types import ModuleType

import nbformat
import pytest

PATHS = sorted((Path(__file__).resolve().parents[1] / "notebooks").glob("*.ipynb"))


@pytest.mark.parametrize("path", PATHS, ids=lambda path: path.stem)
def test_colab_setup_installs_from_repository(path, monkeypatch):
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    setup = notebook.cells[1]
    assert setup.cell_type == "code"
    assert setup.metadata.tags == ["colab-setup"]
    calls = []
    enabled = []
    colab = ModuleType("google.colab")
    output = ModuleType("google.colab.output")
    output.enable_custom_widget_manager = lambda: enabled.append(True)
    colab.output = output
    monkeypatch.setitem(sys.modules, "google.colab", colab)
    monkeypatch.setattr(subprocess, "check_call", calls.append)
    exec(compile(setup.source, str(path), "exec"), {})
    assert calls == [
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "liquid-compute[colab] @ git+https://github.com/zach189/education.git@main",
        ]
    ]
    assert enabled == [True]


def test_local_setup_preserves_environment(monkeypatch):
    setup = nbformat.read(PATHS[0], as_version=4).cells[1]
    monkeypatch.delitem(sys.modules, "google.colab", raising=False)
    calls = []
    monkeypatch.setattr(subprocess, "check_call", calls.append)
    exec(compile(setup.source, str(PATHS[0]), "exec"), {})
    assert calls == []
