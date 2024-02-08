from pros.conductor import Conductor
from pros.conductor.templates import BaseTemplate 
import unittest


class TestConductor(unittest.TestCase):
    ### using __init__() with the unittest module causes errors, setUp is recognized by the module and should be used instead.
    #   it will run again before every unit test
    def setUp(self):
        self._conductor = Conductor()
        print(self._conductor.depots["pros-mainline"].location)
        # super().__init__(methodName)

    def test_resolve_template(self, name: str, version: str):
        self._okapilib_template = BaseTemplate(name="okapilib")
        self._resolved_template = self._conductor.resolve_template(identifier="okapilib")



if __name__ == "__main__":
    unittest.main()