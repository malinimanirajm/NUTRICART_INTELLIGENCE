class RuleEngine:

    def __init__(self, plugins):

        self.plugins = plugins

    def apply(self, query, filters):

        for plugin in self.plugins:

            plugin.apply(

                query,

                filters

            )

        return filters