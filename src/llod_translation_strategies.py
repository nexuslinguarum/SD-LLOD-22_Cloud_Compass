import pandas as pd
from string import Template
from sparql_wrapper import SPARQLEndpoint

class TranslationStrategy:
    name = "Abstract translation strategy"

    def translate(self, source, source_language):
        """Return a panda dataframe of translation for the source term (defined in the language for 
        which source_language is the iso8859-2 code, as a 2 letter code) 
        into all possible languages. The dataframe should contain columns target and target_language"""
        pass


class DirectDBnaryTranslationStrategy(TranslationStrategy):
    name = "Direct DBnary translation links"

    sparql_query = Template("""
        SELECT ?target ?target_language
        WHERE { 
            ?tr a dbnary:Translation;
                dbnary:isTranslationOf / rdfs:label "$source"@$lg ;
                dbnary:writtenForm ?target .
            BIND (LANG(?target) as ?target_language)
    """)

    endpoint = SPARQLEndpoint("http://kaiko.getalp.org/sparql")

    def translate(self, source, source_language):
        return endpoint.query(sparql_query.substitute({'source' : source, 'lg': source_language}))