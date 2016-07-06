# -*- coding: utf-8 -*-
# pylint: disable=E1101, C0330, C0103
#   E1101: Module X has no Y member
#   C0330: Wrong continued indentation
#   C0103: Invalid attribute/variable/method name
#
"""
utils.py
=========

This is a collection of utilities used by the wx.lib.plot package.

"""
import functools
from warnings import warn as _warn

# TODO: New name: RevertStyle? SavedStyle? Something else?
class TempStyle(object):
    """
    Combination Decorator and Context Manager to revert pen or brush changes
    after a method call or block finish.

    :param which: The item to save and revert after execution. Can be
                  one of ``{'both', 'pen', 'brush'}``.
    :type which: str
    :param dc: The DC to get brush/pen info from.
    :type dc: :class:`wx.DC`

    ::

        # Using as a method decorator:
        @TempStyle()                        # same as @TempStyle('both')
        def func(self, dc, a, b, c):        # dc must be 1st arg (beside self)
            # edit pen and brush here

        # Or as a context manager:
        with TempStyle('both', dc):
            # do stuff

    .. Note::

       As of 2016-06-15, this can only be used as a decorator for **class
       methods**, not standard functions. There is a plan to try and remove
       this restriction, but I don't know when that will happen...


    .. epigraph::

       *Combination Decorator and Context Manager! Also makes Julienne fries!
       Will not break! Will not... It broke!*

       -- The Genie
    """
    _valid_types = {'both', 'pen', 'brush'}
    _err_str = (
        "No DC provided and unable to determine DC from context for function "
        "`{func_name}`. When `{cls_name}` is used as a decorator, the "
        "decorated function must have a wx.DC as a keyword arg 'dc=' or "
        "as the first arg."
    )

    def __init__(self, which='both', dc=None):
        if which not in self._valid_types:
            raise ValueError(
                "`which` must be one of {}".format(self._valid_types)
            )
        self.which = which
        self.dc = dc
        self.prevPen = None
        self.prevBrush = None

    def __call__(self, func):

        @functools.wraps(func)
        def wrapper(instance, dc, *args, **kwargs):
            # fake the 'with' block. This solves:
            # 1.  plots only being shown on 2nd menu selection in demo
            # 2.  self.dc compalaining about not having a super called when
            #     trying to get or set the pen/brush values in __enter__ and
            #     __exit__:
            #         RuntimeError: super-class __init__() of type
            #         BufferedDC was never called
            self._save_items(dc)
            func(instance, dc, *args, **kwargs)
            self._revert_items(dc)

            #import copy                    # copy solves issue #1 above, but
            #self.dc = copy.copy(dc)        # possibly causes issue #2.

            #with self:
            #    print('in with')
            #    func(instance, dc, *args, **kwargs)

        return wrapper

    def __enter__(self):
        self._save_items(self.dc)
        return self

    def __exit__(self, *exc):
        self._revert_items(self.dc)
        return False    # True means exceptions *are* suppressed.

    def _save_items(self, dc):
        if self.which == 'both':
            self._save_pen(dc)
            self._save_brush(dc)
        elif self.which == 'pen':
            self._save_pen(dc)
        elif self.which == 'brush':
            self._save_brush(dc)
        else:
            err_str = ("How did you even get here?? This class forces "
                       "correct values for `which` at instancing..."
                       )
            raise ValueError(err_str)

    def _revert_items(self, dc):
        if self.which == 'both':
            self._revert_pen(dc)
            self._revert_brush(dc)
        elif self.which == 'pen':
            self._revert_pen(dc)
        elif self.which == 'brush':
            self._revert_brush(dc)
        else:
            err_str = ("How did you even get here?? This class forces "
                       "correct values for `which` at instancing...")
            raise ValueError(err_str)

    def _save_pen(self, dc):
        self.prevPen = dc.GetPen()

    def _save_brush(self, dc):
        self.prevBrush = dc.GetBrush()

    def _revert_pen(self, dc):
        dc.SetPen(self.prevPen)

    def _revert_brush(self, dc):
        dc.SetBrush(self.prevBrush)


class PendingDeprecation(object):
    """
    Decorator which warns the developer about methods that are
    pending deprecation.

    :param new_func: The new class, method, or function that should be used.
    :type new_func: str

    ::

        @PendingDeprecation("new_func")
        def old_func():
            pass

        # prints the warning:
        # `old_func` is pending deprecation. Please use `new_func` instead.

    """
    _warn_txt = "`{}` is pending deprecation. Please use `{}` instead."

    def __init__(self, new_func):
        self.new_func = new_func

    def __call__(self, func):
        """Support for functions"""
        self.func = func
#        self._update_docs()

        @functools.wraps(self.func)
        def wrapper(*args, **kwargs):
            _warn(self._warn_txt.format(self.func.__name__, self.new_func),
                  PendingDeprecationWarning)
            return self.func(*args, **kwargs)
        return wrapper

    def _update_docs(self):
        """ Set the docs to that of the decorated function. """
        self.__name__ = self.func.__name__
        self.__doc__ = self.func.__doc__




if __name__ == "__main__":
    raise RuntimeError("This module is not intended to be run by itself.")
