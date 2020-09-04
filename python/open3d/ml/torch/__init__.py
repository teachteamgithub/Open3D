"""This module loads the op library."""
import os as _os
import sys as _sys
import torch as _torch
from open3d import _build_config

if not _build_config["Pytorch_VERSION"]:
    raise Exception('Open3D was not built with PyTorch support!')

_o3d_torch_version = _build_config["Pytorch_VERSION"].split('.')
if _torch.__version__.split('.')[:2] != _o3d_torch_version[:2]:
    _o3d_torch_version[2] = '*'  # Any patch level is OK
    match_torch_ver = '.'.join(_o3d_torch_version)
    raise Exception('Version mismatch: Open3D needs Pytorch version {}, but '
                    'version {} is installed!'.format(match_torch_ver,
                                                      _torch.__version__))

_lib_path = []
# allow overriding the path to the op library with an env var.
if 'OPEN3D_TORCH_OP_LIB' in _os.environ:
    _lib_path.append(_os.environ['OPEN3D_TORCH_OP_LIB'])

_this_dir = _os.path.dirname(__file__)
_package_root = _os.path.join(_this_dir, '..', '..')
_lib_ext = {'linux': '.so', 'darwin': '.dylib', 'win32': '.dll'}[_sys.platform]
_lib_suffix = '_debug' if _build_config['CMAKE_BUILD_TYPE'] == 'Debug' else ''
_lib_arch = ('cuda', 'cpu') if _build_config["BUILD_CUDA_MODULE"] else ('cpu',)
_lib_path.extend([_os.path.join(_package_root, la, 'open3d_torch_ops' +
                                _lib_suffix + _lib_ext) for la in _lib_arch])

_load_except = None
_loaded = False
for _lp in _lib_path:
    try:
        _torch.ops.load_library(_lp)
        _loaded = True
        break
    except Exception as ex:
        _load_except = ex
        if not _os.path.isfile(_lp):
            print('The op library at "{}" was not found. Make sure that '
                  'BUILD_PYTORCH_OPS was enabled.'.format(
                      _os.path.realpath(_lp)))

if not _loaded:
    raise _load_except

from . import nn
