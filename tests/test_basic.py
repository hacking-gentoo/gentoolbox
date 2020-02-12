import unittest
import sys

from gentoolkit.equery import CONFIG

from gentoolbox.kwtool.bestkeywords import best_keyword
from gentoolbox.kwtool.bestkeywords import worst_keyword
from gentoolbox.kwtool.bestkeywords import make_stable
from gentoolbox.kwtool.bestkeywords import combibe_kwdicts
from gentoolbox.kwtool.bestkeywords import parse_atom
from gentoolbox.kwtool.bestkeywords import parse_list

class BasicTests(unittest.TestCase):

    def test_best_keyword(self):
        self.assertEqual(best_keyword("x86", "~x86"), "x86")
        self.assertEqual(best_keyword("~x86", "x86"), "x86")
        self.assertEqual(best_keyword("-x86", "~x86"), "~x86")
        self.assertEqual(best_keyword("~x86", "-x86"), "~x86")

    def test_worst_keyword(self):
        self.assertEqual(worst_keyword("x86", "~x86"), "~x86")
        self.assertEqual(worst_keyword("~x86", "x86"), "~x86")
        self.assertEqual(worst_keyword("-x86", "~x86"), "-x86")
        self.assertEqual(worst_keyword("~x86", "-x86"), "-x86")

    def test_make_stable(self):
        self.assertEqual(make_stable("x86"), "x86")
        self.assertEqual(make_stable("~x86"), "x86")
        self.assertEqual(make_stable("-x86"), "x86")

    def test_combibe_kwdicts_1(self):
        kwd1 = {
            "alpha": "~alpha",
            "arm" : "~arm",
            "x86": "~x86"
        }
        kwd2 = {
            "alpha": "~alpha",
            "x86": "x86"
        }
        combibe_kwdicts(kwd1, kwd2, False)
        self.assertEqual(kwd1["alpha"], "~alpha")
        self.assertEqual(kwd1["x86"], "~x86")

    def test_combibe_kwdicts_2(self):
        kwd1 = {
            "alpha": "~alpha",
            "arm" : "~arm",
            "x86": "~x86"
        }
        kwd2 = {
            "alpha": "~alpha",
            "x86": "x86"
        }
        combibe_kwdicts(kwd1, kwd2, True)
        self.assertEqual(kwd1["alpha"], "~alpha")
        self.assertEqual(kwd1["x86"], "x86")

    def test_parse_atom_dep_a(self):
        CONFIG['verbose']=False
        kwd=parse_atom("dev-test/dep-a")
        self.assertEqual(kwd["alpha"], "alpha")
        self.assertEqual(kwd["arm"], "arm")
        self.assertEqual(kwd["x86"], "x86")
        
    def test_parse_atom_dep_b(self):
        CONFIG['verbose']=False
        kwd=parse_atom("dev-test/dep-b")
        self.assertEqual(kwd["alpha"], "~alpha")
        self.assertEqual(kwd["arm"], "arm")
        self.assertEqual(kwd["x86"], "x86")
        
    def test_parse_atom_dep_c(self):
        CONFIG['verbose']=False
        kwd=parse_atom("dev-test/dep-c")
        self.assertEqual(kwd["alpha"], "~alpha")
        self.assertEqual(kwd["arm"], "~arm")
        self.assertEqual(kwd["x86"], "x86")
        
    def test_parse_list_cf(self):
        CONFIG['verbose']=False
        kwd=parse_list(["dev-test/dep-a", "dev-test/dep-b", "dev-test/dep-c"], False)
        self.assertEqual(kwd["alpha"], "~alpha")
        self.assertEqual(kwd["arm"], "~arm")
        self.assertEqual(kwd["x86"], "x86")

    def test_parse_list_ct(self):
        CONFIG['verbose']=False
        kwd=parse_list(["dev-test/dep-a", "dev-test/dep-b", "dev-test/dep-c"], True)
        self.assertEqual(kwd["alpha"], "alpha")
        self.assertEqual(kwd["arm"], "arm")
        self.assertEqual(kwd["x86"], "x86")

if __name__ == '__main__':
    unittest.main()
    