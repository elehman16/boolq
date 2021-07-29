
class Article(object):
    """Text to annotate.

    Provides an interface for text to be
    annotated by forcing certain information
    about the Article to be provded.
    """

    def __init__(self, id_, title, text):
        self.id_ = id_
        self.title = title
        self.text = text
        self.extra = {}

    def get_extra(self):
        """Returns a dictionary of any extra variables required"""
        return self.extra
