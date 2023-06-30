from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

ext_modules = [
    Extension("polish_anime_downloader", ["polish_anime_downloader.pyx"], include_dirs=['requests']),
]

setup(
    ext_modules=cythonize(ext_modules, compiler_directives={"language_level": "3"}),
)

