from django.db.models import JSONField

class UTF8JSONField(JSONField):
    """JSONField for postgres databases.
    Deprecated.
    Displays UTF-8 characters directly in the admin, i.e. äöü instead of
    unicode escape sequences.
    """
    pass
