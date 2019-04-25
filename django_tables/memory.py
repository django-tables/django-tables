import copy

from .base import BaseTable, BoundRow


__all__ = ('MemoryTable', 'Table',)


def sort_table(data, order_by):
    """Sort a list of dicts according to the fieldnames in the
    ``order_by`` iterable. Prefix with hypen for reverse.

    Dict values can be callables.
    """
    def _cmp(x, y):
        for name, reverse in instructions:
            lhs, rhs = x.get(name), y.get(name)
            res = cmp((callable(lhs) and [lhs(x)] or [lhs])[0],
                      (callable(rhs) and [rhs(y)] or [rhs])[0])
            if res != 0:
                return reverse and -res or res
        return 0
    instructions = []
    for o in order_by:
        if o.startswith('-'):
            instructions.append((o[1:], True,))
        else:
            instructions.append((o, False,))
    data.sort(cmp=_cmp)


class MemoryTable(BaseTable):
    """Table that is based on an in-memory dataset (a list of dict-like
    objects).
    """

    def _build_snapshot(self):
        """Rebuilds the table whenever it's options change.

        Whenver the table options change, e.g. say a new sort order,
        this method will be asked to regenerate the actual table from
        the linked data source.

        In the case of this base table implementation, a copy of the
        source data is created, and then modified appropriately.

        # TODO: currently this is called whenever data changes; it is
        # probably much better to do this on-demand instead, when the
        # data is *needed* for the first time.
        """
        # reset caches
        self._columns._reset()
        self._rows._reset()

        snapshot = copy.copy(self._data)
        # Fill in ``default`` values where needed
        for src_row in snapshot:
            # We do this now so that column ``default`` values can affect
            # sorting, even with callables
            # This is a design decision - the alternative would be to
            # resolve the values when they are accessed, and either do not
            # support sorting them at all, or run the callables during
            # sorting.
            for column in self.columns.all():
                if src_row.get(column.src_accessor, None) is None:
                    # No value was provided in the source, so use the default
                    src_row[column.src_accessor] = column.get_default(
                        BoundRow(self, src_row))

        if self.order_by:
            actual_order_by = self._resolve_sort_directions(self.order_by)
            sort_table(snapshot, self._col_names_to_src_names(actual_order_by))
        return snapshot


class Table(MemoryTable):
    def __new__(cls, *a, **kw):
        from warnings import warn
        warn('"Table" has been renamed to "MemoryTable". Please use the '+
             'new name.', DeprecationWarning)
        return MemoryTable.__new__(cls)
