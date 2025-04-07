from collections import OrderedDict

import six

from django.core.exceptions import FieldError
from .base import (
    BaseTable,
    DeclarativeColumnsMetaclass,
    Column,
    BoundRow,
    Rows,
    TableOptions,
)


__all__ = ('ModelTable',)


class ModelTableOptions(TableOptions):
    def __init__(self, options=None):
        super(ModelTableOptions, self).__init__(options)
        self.model = getattr(options, 'model', None)
        self.columns = getattr(options, 'columns', None)
        self.exclude = getattr(options, 'exclude', None)


def columns_for_model(model, columns=None, exclude=None):
    """
    Returns a ``SortedDict`` containing form columns for the given model.

    ``columns`` is an optional list of field names. If provided, only the
    named model fields will be included in the returned column list.

    ``exclude`` is an optional list of field names. If provided, the named
    model fields will be excluded from the returned list of columns, even
    if they are listed in the ``fields`` argument.
    """

    field_list = []
    opts = model._meta
    for f in opts.fields + opts.many_to_many:
        if (columns and f.name not in columns) or \
           (exclude and f.name in exclude):
            continue
        # TODO: chose correct column type, with right options
        column = Column(verbose_name=f.verbose_name)
        if column:
            field_list.append((f.name, column))
    field_dict = OrderedDict(field_list)
    if columns:
        field_dict = OrderedDict(
            [(c, field_dict.get(c)) for c in columns
                if ((not exclude) or (exclude and c not in exclude))]
        )
    return field_dict


class BoundModelRow(BoundRow):
    """Special version of the BoundRow class that can handle model instances
    as data.

    We could simply have ModelTable spawn the normal BoundRow objects
    with the instance converted to a dict instead. However, this way allows
    us to support non-field attributes and methods on the model as well.
    """

    def _default_render(self, boundcol):
        """
        In the case of a model table, the accessor may use ``__`` to
        span instances. We need to resolve this.
        """
        # try to resolve relationships spanning attributes
        bits = boundcol.src_accessor.split('__')
        current = self.data
        for bit in bits:
            # note the difference between the attribute being None and not
            # existing at all; assume "value doesn't exist" in the former
            # (e.g. a relationship has no value), raise error in the latter.
            # a more proper solution perhaps would look at the model meta
            # data instead to find out whether a relationship is valid; see
            # also ``_validate_column_name``, where such a mechanism is
            # already implemented).
            if not hasattr(current, bit):
                raise ValueError("Could not resolve %s from %s" % (
                    bit,
                    boundcol.src_accessor,
                ))

            current = getattr(current, bit)
            if callable(current):
                current = current()
            # important that we break in None case, or a relationship
            # spanning across a null-key will raise an exception in the
            # next iteration, instead of defaulting.
            if current is None:
                break

        if current is None:
            # ...the whole name (i.e. the last bit) resulted in None
            if boundcol.column.default is not None:
                return boundcol.get_default(self)
        return current


class ModelRows(Rows):
    row_class = BoundModelRow

    def __init__(self, *args, **kwargs):
        super(ModelRows, self).__init__(*args, **kwargs)

    def _reset(self):
        self._length = None

    def __len__(self):
        """Use the queryset count() method to get the length, instead of
        loading all results into memory. This allows, for example,
        smart paginators that use len() to perform better.
        """
        if getattr(self, '_length', None) is None:
            # This import cannot be at the top otherwise the settings will
            # configure early.
            data = self.table.data
            if isinstance(data, list):
                self._length = len(self.table.data)
            elif hasattr(data, 'count') and hasattr(data.count, '__call__'):
                self._length = self.table.data.select_related(None).prefetch_related(None).count()  # noqa E501
            else:
                self._length = len(list(self.table.data))
        return self._length

    # for compatibility with django.core.paginator.Paginator
    count = __len__


class ModelTableMetaclass(DeclarativeColumnsMetaclass):
    def __new__(cls, name, bases, attrs):
        # Let the default form meta class get the declared columns; store
        # those in a separate attribute so that ModelTable inheritance with
        # differing models works as expected (the behaviour known from
        # ModelForms).
        self = super(ModelTableMetaclass, cls).__new__(
            cls, name, bases, attrs, parent_cols_from='declared_columns')
        self.declared_columns = self.base_columns

        opts = self._meta = ModelTableOptions(getattr(self, 'Meta', None))
        # if a model is defined, then build a list of default columns and
        # let the declared columns override them.
        if opts.model:
            columns = columns_for_model(opts.model, opts.columns, opts.exclude)
            columns.update(self.declared_columns)
            self.base_columns = columns
        return self


class ModelTable(six.with_metaclass(ModelTableMetaclass, BaseTable)):
    """Table that is based on a model.

    Similar to ModelForm, a column will automatically be created for all
    the model's fields. You can modify this behaviour with a inner Meta
    class:

        class MyTable(ModelTable):
            class Meta:
                model = MyModel
                exclude = ['fields', 'to', 'exclude']
                columns = ['fields', 'to', 'include']

    One difference to a normal table is the initial data argument. It can
    be a queryset or a model (it's default manager will be used). If you
    just don't any data at all, the model the table is based on will
    provide it.
    """

    rows_class = ModelRows

    def __init__(self, data=None, *args, **kwargs):
        if data == []:
            data = None
        if data is None:
            if self._meta.model is None:
                raise ValueError(
                    'Table without a model association needs to be initialized with data',  # noqa
                )
            self.queryset = self._meta.model._default_manager.none()
        elif hasattr(data, '_default_manager'):  # saves us db.models import
            self.queryset = data._default_manager.all()
        else:
            self.queryset = data

        super(ModelTable, self).__init__(self.queryset, *args, **kwargs)

    def _validate_column_name(self, name, purpose):
        """
        Overridden. Only allow model-based fields and valid model
        spanning relationships to be sorted.
        """
        # let the base class sort out the easy ones
        result = super(ModelTable, self)._validate_column_name(name, purpose)
        if not result:
            return False

        if purpose == 'order_by':
            column = self.columns[name]

            # TODO: It might be faster to try to resolve the given name
            # manually recursing the model metadata rather than
            # constructing a queryset.
            try:
                # Let Django validate the lookup by asking it to build
                # the final query; the way to do this has changed in
                # Django 1.2, and we try to support both versions.

                # Using the model._default_manager to get a standard manager
                # in case we're sorting on a "fake" queryset that doesn't
                # implement the SQL compiler
                _temp = self.queryset.model._default_manager.order_by(
                    column.src_accessor).query
                from django.db import DEFAULT_DB_ALIAS
                _temp.get_compiler(DEFAULT_DB_ALIAS).as_sql()
            except FieldError:
                return False
        else:
            return False

        # if we haven't failed by now, the column should be valid
        return True

    def _build_snapshot(self):
        """
        Overridden. The snapshot in this case is simply a queryset
        with the necessary filters etc. attached.
        """
        # reset caches
        self._columns._reset()
        self._rows._reset()

        queryset = self.queryset
        if self.order_by:
            actual_order_by = self._resolve_sort_directions(self.order_by)
            queryset = queryset.order_by(
                *self._col_names_to_src_names(actual_order_by))

        return queryset
