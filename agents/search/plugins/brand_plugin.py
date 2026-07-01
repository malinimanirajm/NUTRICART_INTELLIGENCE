from .base_plugin import SearchPlugin


class BrandPlugin(SearchPlugin):

    def __init__(self, brands):

        self.brands = brands

    def apply(self, query, filters):

        for alias, brand in sorted(

            self.brands.items(),

            key=lambda x: len(x[0]),

            reverse=True

        ):

            if alias in query:

                filters.brand = brand

                return