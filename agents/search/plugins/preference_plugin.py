from config.search_config import PREFERENCES

from .base_plugin import SearchPlugin


class PreferencePlugin(SearchPlugin):

    def apply(self, query, filters):

        query = query.lower()

        for _, config in PREFERENCES.items():

            attribute = config["attribute"]

            keywords = config["keywords"]

            if any(keyword in query for keyword in keywords):

                setattr(

                    filters,

                    attribute,

                    True

                )