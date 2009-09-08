
import Globals  # import Zope 2 dependencies in order

from zope.interface import Attribute
from zope.interface import Interface
from Products.PluginIndexes.interfaces import IPluggableIndex


class ISolrIndex(IPluggableIndex):
    """A ZCatalog multi-index that uses Solr for storage and queries."""
    solr_uri = Attribute("The URI of the Solr server")
    connection_manager = Attribute("""
        An ISolrConnectionManager that is specific to the ZODB connection.
        """)


class ISolrConnectionManager(Interface):
    """Provides a SolrConnection, schema info, and transaction integration"""
    connection = Attribute("An instance of solr.SolrConnection (from solrpy)")
    schema = Attribute("An ISolrSchema instance")

    def set_changed():
        """Adds the Solr connection to the current transaction.

        Call this before sending change requests to Solr.
        """


class ISolrSchema(Interface):
    """The relevant part of the schema installed in a Solr instance.
    """
    uniqueKey = Attribute("The name of the unique field")
    defaultSearchField = Attribute("""
        The name of the field to search when no field has been
        specified in the query
        """)
    fields = Attribute("A sequence of ISolrField")


class ISolrField(Interface):
    """A field in Solr"""
    name = Attribute("The name")
    type = Attribute("The type (an arbitrary string; don't rely on it)")
    java_class = Attribute("""
        The fully qualified name of the Java class that handles the field
        """)
    indexed = Attribute("True if the field is searchable")
    stored = Attribute("True if the value of the field can be retrieved")
    required = Attribute("True if a value is required for indexing")
    multiValued = Attribute("True if the field supports multiple values")
    handler = Attribute("An ISolrFieldHandler")


class ISolrFieldHandler(Interface):
    """Adjust field input to fit Solr.

    Register instances providing this interface as utilities.
    Register by field name (most specific), Java class name (less
    specific), or no name (most general).
    """
    def parse_query(field, field_query):
        """Convert a field-specific part of a catalog query to Solr query text.

        field is an ISolrField. field_query is the field-specific part
        of the catalog query. Most implementations should extend
        DefaultFieldHandler.

        If the field query actually contains nothing to constrain the
        search, this method should return None.

        The returned text must include a prefix specifying the field name
        to be queried, and some characters must be escaped according to
        Lucene rules. For example, r'SearchableText:"I say \"potato\"\!"'.
        See:

            http://lucene.apache.org/java/2_4_0/queryparsersyntax.html
            http://wiki.apache.org/solr/SolrQuerySyntax

        The returned query text must be a string or unicode. Before
        passing the query to Solr, SolrIndex will join the query with
        other query texts using ' AND '.
        """

    def convert(value):
        """Convert a field value to unicode for inclusion in Solr.

        Return a unicode object or something that can be converted to
        unicode using the unicode() builtin.  May return None to
        indicate no data.
        """


class ISolrIndexingWrapper(Interface):
    """Optional wrapper for indexing.

    Just before indexing, the SolrIndex class adapts the object it
    is indexing to this interface.  To fill field values, the SolrIndex
    class pulls attribute values out of the adapter.  If no such adapter
    exists, the SolrIndex pulls attribute values out of the object
    directly.
    """