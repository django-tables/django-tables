=================
All about Columns
=================

Columns are what defines a table. Therefore, the way you configure your
columns determines to a large extend how your table operates.

``django_tables.columns`` currently defines three classes, ``Column``,
``TextColumn`` and ``NumberColumn``. However, the two subclasses currently
don't do anything special at all, so you can simply use the base class.
While this will likely change in the future (e.g. when grouping is added),
the base column class will continue to work by itself.

There are no required arguments. The following is fine:

.. code-block:: python

    class MyTable(tables.MemoryTable):
        count = tables.Column()

It will result in a column named ``count`` in the table that references the
value ``count`` in your source data (if present). . You can specify the
``model_rel`` to override the source data this field is referencing :

.. code-block:: python

    count = tables.Column(model_rel="src_count")

The column is still called and accessed via "count", but now the table will
 use ``src_count`` to read it's values from the source.

This is useful for occasions where you'd like to place meaningful names mapping
to input fields with less-useful names.

.. code-block:: python

    class BookTable(tables.ModelTable):
        book_name = tables.Column(model_rel="name")
        author_name = tables.Column(model_rel="info__author__name")
        class Meta:
            model = Book

The overwritten ``Book.name`` field will now be exposed via the table as
the ``book_name`` column, and the new ``author_name`` column retrieves it's
values from ``Book.info.author.name``.

Apart from their internal name, you can define a string that will be used
when for display via ``verbose_name``:

.. code-block:: python

    pubdate = tables.Column(verbose_name="Published")

The verbose name will be used, for example, if you put in a template:

.. code-block:: django

    {{ column }}

If you don't want a column to be sortable by the user:

.. code-block:: python

    pubdate = tables.Column(sortable=False)

Sorting is also affected by ``direction``, which can be used to change the
*default* sort direction to descending. Note that this option only indirectly
translates to the actual direction. Normal und reverse order, the terms
django-tables exposes, now simply mean different things.

.. code-block:: python

    pubdate = tables.Column(direction='desc')

If you don't want to expose a column (but still require it to exist, for
example because it should be sortable nonetheless):

.. code-block:: python

    pubdate = tables.Column(visible=False)

The column and it's values will now be skipped when iterating through the
table, although it can still be accessed manually.

Finally, you can specify default values for your columns:

.. code-block:: python

    health_points = tables.Column(default=100)

Note that how the default is used and when it is applied differs between
table types.
