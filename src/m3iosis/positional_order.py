"""Use the workspace's shared positional-order implementation."""
import importlib.util
import os
from pathlib import Path

_workspace = Path(__file__).resolve().parents[3]
_source = _workspace / 'Vox' / 'ordering.py'
if not _source.is_file():
    _source = Path.home() / 'imsgct' / 'Vox' / 'ordering.py'
_spec = importlib.util.spec_from_file_location('imsgct_positional_order', _source)
_shared = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_shared)


selected_braid = _shared.selected_braid


def intercept():
    _shared.intercept(default_site='braid')
