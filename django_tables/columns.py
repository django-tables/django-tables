import six


__all__ = (
    'Column', 'TextColumn', 'NumberColumn',
)


class Column(object):
    """Represents a single column of a table.

    ``verbose_name`` defines a display name for this column used for output.

    ``model_rel`` is the Django ORM-style name of the relationship path from
    your Model to the field represented by this column. By default, the
    column"s label is assumed to be the path to the field, but in cases where
    two different columns are both backed by the same field, you can use
    the same model_rel on two columns.

    ``default`` is the default value for this column. If the data source
    does provide ``None`` for a row, the default will be used instead. Note
    that whether this effects ordering might depend on the table type (model
    or normal). Also, you can specify a callable, which will be passed a
    ``BoundRow`` instance and is expected to return the default to be used.

    You can use ``visible`` to flag the column as hidden by default.
    However, this can be overridden by the ``visibility`` argument to the
    table constructor. If you want to make the column completely unavailable
    to the user, set ``inaccessible`` to True.

    Setting ``sortable`` to False will result in this column being unusable
    in ordering. You can further change the *default* sort direction to
    descending using ``direction``. Note that this option changes the actual
    direction only indirectly. Normal und reverse order, the terms
    django-tables exposes, now simply mean different things.
    """

    ASC = 1
    DESC = 2

    # Tracks each time a Column instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self, verbose_name=None, model_rel=None, default=None,
                 visible=True, inaccessible=False, sortable=None,
                 direction=ASC):
        self.verbose_name = verbose_name
        self.model_rel = model_rel
        self.default = default
        self.visible = visible
        self.inaccessible = inaccessible
        self.sortable = sortable
        self.direction = direction

        self.creation_counter = Column.creation_counter
        Column.creation_counter += 1

    def _set_direction(self, value):
        if isinstance(value, six.string_types):
            if value in ('asc', 'desc'):
                self._direction = (
                    (value == 'asc') and Column.ASC or Column.DESC
                )
            else:
                raise ValueError('Invalid direction value: %s' % value)
        else:
            self._direction = value

    direction = property(lambda s: s._direction, _set_direction)


class TextColumn(Column):
    pass


class NumberColumn(Column):
    pass
