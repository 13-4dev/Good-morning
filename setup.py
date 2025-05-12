from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "utils_cy",
        ["cython_modules/utils.pyx"],
        include_dirs=[numpy.get_include()],
    ),
    Extension(
        "generation_cy",
        ["cython_modules/generation.pyx"],
    ),
]

setup(
    name="good_morning_cy",
    ext_modules=cythonize(extensions, compiler_directives={
        'language_level': "3",
        'boundscheck': False,
        'wraparound': False,
        'initializedcheck': False,
    }),
    zip_safe=False,
) 