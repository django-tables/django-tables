==================================
DataTabler - Easy Tables in Django
==================================

:Version: 0.1.0dev
:Web: http://github.com/winhamwr/django-tables/
:Source: http://github.com/winhamwr/django-tables/

.. datatabler-synopsis:

DataTabler is an easy way to turn your Django Querysets, dictionary lists or
other structured data in to an HTML table with server-side sorting and
consistent formatting. Define the data relationship you want to display in one
place, and then DRY to table victory.

DataTabler was derived from `django-tables`_ and is a very similar library.

.. datatabler-overview:

Overview
========

Dealing with sorting, consistent formatting and derived fields when deplaying
querysets and other structured data can be a pain. How much do you put in
your view, versus the template and how much should you try to DRY with include
templates and templatetags? What about creating CRUD links, but only for users
with permissions on the individual objects?

With DataTabler, you define the columns you want to expose in the table up
front, along with sensible names, free sorting and the power of python for
DRYing up any non-display logic.

.. datatabler-example:

Example
=======

Let's say you'd like to display a table of documents in a document management
system. You need an edit link, author (sortable by last name) and a preview
of the document. On another page you don't need the preview anymore, but you
need to be able to . Your Document model looks like this:
::

    # models.py
    class Document(models.Model):
        name = models.CharField(max_length=200)
        html = models.TextField(blank=True)
        author = models.ForeignKey(User, related_name='documents_authored_set')


With DataTabler, you'd define a ``Table`` (anywhere, but tables.py is nice) like
so:
::

    # tables.py
    class DocumentTable(datatabler.ModelTable):
        edit_link = Column(sortable=False, verbose_name=' ')
::

    # view.py
    def list_documents(request):

License
=======

This software is licensed under the `New BSD License`. See the ``LICENSE``
file in the top distribution directory for the full license text.
