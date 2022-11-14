"""
Defines a function that converts Python types from the NumPy+ ecosystem back to
built-in types.
"""

try:
    import numpy as np

    has_numpy = True
except ImportError:
    has_numpy = False


def to_primitive(value):
    """
    Converts 'value' to a built-in Python type if it is of similar type. Works only if
    the user has NumPy installed, and otherwise does nothing.
    Performs conversions such as:
    - numpy.float64(1.0) -> float(1.0)
    - numpy.complex128(1 + 1j) -> complex(1 + 1j)
    - numpy.bool_(True) -> bool(True)
    - numpy.str_("abc") -> str("abc")

    Also converts 0D arrays. This includes scalar-like, non-empty, dimensionless
    objects created by libraries such as NumPy and Xarray.
    - numpy.array(1) -> int(1)
    - numpy.array(False) -> bool(False)
    - xarray.DataArray(2.0) -> float(2.0)

    Empty array-like objects are converted to empty lists. Any objects which can't be
    handled here are passed on as usual. This includes lists, dicts, and non-empty
    ND-arrays.
    """

    # If NumPy isn't installed, do nothing
    if not has_numpy:
        return value

    # Return if value is a scalar. Includes primitive types, numpy scalars, strings.
    if np.isscalar(value):
        # Convert things like np.float64, np.bool_, np.str_ to Python primitives.
        if isinstance(value, np.generic):
            return value.item()
        else:
            return value

    # Check if value is a NumPy array or something similar, i.e. something that
    # implements the __array_ufunc__ protocol.
    # This catches Pandas Series, Xarray DataArray, pint Quantity, etc.
    # See https://numpy.org/neps/nep-0013-ufunc-overrides.html
    if hasattr(value, "__array_ufunc__") and value.__array_ufunc__ is not None:
        if np.ndim(value) == 0:
            # If receiving a 0D array, convert to scalar and return.
            # This accounts for dimensionless but non-empty quantities such as the
            # results of numpy.array(5.0) or xarray.DataArray(5.0).
            # TODO include support for Pint/AstroPy Quantity
            return value.item()
        else:
            # If receiving an ND array, convert to list
            value = list(value)
            # If empty, raise error
            if not value:
                raise ValueError("Namelists cannot contain an empty array.")
            # Recursively convert each element to primitive.
            # - If value is 1D, converts each element from NumPy scalars to built-ins.
            # - If value is ND, for N > 1, list(value) produces a list of (N - 1)D
            #   arrays.
            return [to_primitive(x) for x in value]

    # Pass through anything that didn't match the tests above
    return value
