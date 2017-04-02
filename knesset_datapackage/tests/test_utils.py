from unittest import TestCase
from ..utils import uncast_value, cast_value
from datetime import datetime, date


class UncastValueTestCase(TestCase):

    def assertUncastValue(self, type_or_partial_schema, casted_value, expected_uncasted_value):
        schema = {"type": type_or_partial_schema} if isinstance(type_or_partial_schema, (str, unicode)) else type_or_partial_schema
        schema.setdefault("name", "void")
        uncasted_value = uncast_value(casted_value, schema)
        self.assertEqual(uncasted_value, expected_uncasted_value)
        # now cast the value back - there are some edge-cases for this
        recasted_value = cast_value(uncasted_value, schema)
        if schema["type"] == "string" and casted_value is None:
            self.assertEqual(recasted_value, u"")
        else:
            self.assertEqual(recasted_value, casted_value)

    def test(self):
        for args in (("date", date(2014, 3, 2), "2014-03-02"),
                     ({"type": "datetime", "format": "fmt:%d/%m/%Y %H:%M"}, datetime(2016, 1, 11, 5, 4), "11/01/2016 05:04"),
                     ("integer", None, ""),
                     ("string", None, ""),):
            self.assertUncastValue(*args)
