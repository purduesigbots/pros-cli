from pros.conductor import Conductor
from pros.conductor.templates import LocalTemplate 
import unittest


class TestConductor(unittest.TestCase):
    ### using __init__() with the unittest module causes errors, setUp is recognized by the module and should be used instead.
    #   setUp will run before every unit test
    def setUp(self):
        self._conductor = Conductor()

    def test_resolve_template(self):
        okapilib_template = LocalTemplate(name="okapilib", version="5.0.0")
        resolved_template = self._conductor.resolve_template(identifier="okapilib")
        self.assertTrue(resolved_template == okapilib_template)


if __name__ == "__main__":
    unittest.main()