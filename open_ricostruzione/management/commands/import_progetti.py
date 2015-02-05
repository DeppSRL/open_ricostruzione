__author__ = 'stefano'
#
# >>> import tablib
# >>> from import_export import resources
# >>> from core.models import Book
# >>> book_resource = resources.modelresource_factory(model=Book)()
# >>> dataset = tablib.Dataset(['', 'New book'], headers=['id', 'name'])
# >>> result = book_resource.import_data(dataset, dry_run=True)
# >>> print result.has_errors()
# False
# >>> result = book_resource.import_data(dataset, dry_run=False)