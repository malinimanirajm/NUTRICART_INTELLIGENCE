from .base_plugin import SearchPlugin


class CategoryPlugin(SearchPlugin):

    def __init__(self, categories):

        self.categories = categories

    def apply(self, query, filters):

        for alias, category in sorted(

            self.categories.items(),

            key=lambda x: len(x[0]),

            reverse=True

        ):

            if alias in query:

                filters.category = category

                return