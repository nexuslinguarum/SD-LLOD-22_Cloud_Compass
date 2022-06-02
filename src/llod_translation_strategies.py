import pandas as pd
from string import Template
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET, POSTDIRECTLY, CSV, TURTLE

class TranslationStrategy:
    name = "Abstract translation strategy"

    def translate(self, source, source_language):
        """Return a panda dataframe of translation for the source term (defined in the language for 
        which source_language is the iso8859-2 code, as a 2 letter code) 
        into all possible languages. The dataframe should contain columns target and target_language"""
        pass


class SPARQLTranslationStrategy(TranslationStrategy):
    sparql_query = ""

    endpoint = None

    def translate(self, source, source_language):
      qq = self.sparql_query.substitute({'source' : source, 'lg': source_language})
      #print('Querying with: ' + qq)
      return self.endpoint.query_as_dataframe(qq)

class DirectDBnaryTranslationStrategy(SPARQLTranslationStrategy):
    name = "Direct DBnary"

    sparql_query = Template("""
        SELECT ?target ?target_language
        WHERE { 
            ?tr a dbnary:Translation;
                dbnary:isTranslationOf / rdfs:label "$source"@$lg ;
                dbnary:writtenForm ?target .
            BIND (LANG(?target) as ?target_language)
        }
    """)

    endpoint = SPARQLEndpoint("http://kaiko.getalp.org/sparql")

class CrossDBnaryTranslationStrategy(SPARQLTranslationStrategy):
    name = "Cross Translation DBnary"

    sparql_query = Template("""
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterm: <http://purl.org/dc/terms/>
PREFIX lexvo: <http://lexvo.org/id/iso639-3/>
PREFIX lime: <http://www.w3.org/ns/lemon/lime#>

SELECT ?target ?target_language
WHERE { 
  ?le a ontolex:LexicalEntry ; rdfs:label "${source}"@${lg} .
  ?tr a dbnary:Translation ;
     dbnary:isTranslationOf ?le ;
     dbnary:writtenForm ?trans.
  ?le2 a ontolex:LexicalEntry ; rdfs:label ?trans .
  ?tr2 a dbnary:Translation ;
    dbnary:isTranslationOf ?le2;
    dbnary:writtenForm ?target.
  BIND (LANG(?target) as ?target_language)
}
    """)

    endpoint = SPARQLEndpoint("http://kaiko.getalp.org/sparql")


class GeneralOntologyTranslationStrategy(SPARQLTranslationStrategy):
    name = "General Shared Label From Ontology"

    sparql_query = Template("""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?target ?target_language
WHERE { 
    ?stuff rdfs:label "${source}"@${lg} ; 
        rdfs:label ?target.
  BIND (LANG(?target) as ?target_language)
}
    """)

class DBpediaTranslationStrategy(GeneralOntologyTranslationStrategy):
    name = GeneralOntologyTranslationStrategy.name + ": DBpedia"

    endpoint = SPARQLEndpoint('http://dbpedia.org/sparql', http_query_method=GET)

    def translate(self, source, source_language):
      if(source[0].islower()):
        source = source.capitalize()
      return super().translate(source, source_language)

class WikiDataTranslationStrategy(GeneralOntologyTranslationStrategy):
    name = GeneralOntologyTranslationStrategy.name + ": WikiData"
    
    endpoint = SPARQLEndpoint('https://query.wikidata.org/sparql')

