from config.dictionary_loader import CACHE

from agents.search.normalizer import QueryNormalizer
from agents.search.rules.rule_engine import RuleEngine

from agents.search.plugins.category_plugin import CategoryPlugin
from agents.search.plugins.brand_plugin import BrandPlugin
from agents.search.plugins.nutrition_plugin import NutritionPlugin
from agents.search.plugins.preference_plugin import PreferencePlugin

from agents.search.filters import SearchFilters


class SearchParser:

    def __init__(self):

        self.normalizer = QueryNormalizer()

        self.engine = RuleEngine(

            [

                CategoryPlugin(

                    CACHE["categories"]

                ),

                BrandPlugin(

                    CACHE["brands"]

                ),

                NutritionPlugin(),

                PreferencePlugin(),

            ]

        )

    # ---------------------------------------------------------

    def parse(self, query: str) -> SearchFilters:

        query = self.normalizer.normalize(query)

        filters = SearchFilters()

        return self.engine.apply(

            query,

            filters,

        )