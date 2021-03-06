# Core Library
import ast
from typing import Set

# First party
from flake8_simplify import Plugin


def _results(code: str) -> Set[str]:
    """Apply the plugin to the given code."""
    tree = ast.parse(code)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_trivial_case():
    """Check the plugins output for no code."""
    assert _results("") == set()


def test_plugin_version():
    assert isinstance(Plugin.version, str)
    assert "." in Plugin.version


def test_plugin_name():
    assert isinstance(Plugin.name, str)


def test_single_isinstance():
    ret = _results("isinstance(a, int) or foo")
    assert ret == set()


def test_fine_code():
    ret = _results("- ( a+ b)")
    assert ret == set()


def test_multiple_isinstance_multiple_lines():
    ret = _results(
        "isinstance(a, int) or isinstance(a, float)\n"
        "isinstance(b, bool) or isinstance(b, str)"
    )
    assert ret == {
        (
            "1:0 SIM101 Multiple isinstance-calls which can be merged "
            "into a single call for variable 'a'"
        ),
        (
            "2:0 SIM101 Multiple isinstance-calls which can be merged "
            "into a single call for variable 'b'"
        ),
    }


def test_first_wrong_then_multiple_isinstance():
    ret = _results(
        "foo(a, b, c) or bar(a, b)\nisinstance(b, bool) or isinstance(b, str)"
    )
    assert ret == {
        (
            "2:0 SIM101 Multiple isinstance-calls which can be merged "
            "into a single call for variable 'b'"
        ),
    }


def test_multiple_isinstance_and():
    ret = _results("isinstance(b, bool) and isinstance(b, str)")
    assert ret == set()


def test_multiple_other_function():
    ret = _results("isfoo(a, int) or isfoo(a, float)")
    assert ret == set()


def test_sim_102_pattern1():
    ret = _results(
        """if a:
    if b:
        c"""
    )
    assert ret == {
        (
            "1:0 SIM102 Use a single if-statement instead of "
            "nested if-statements"
        )
    }


def test_sim_102_pattern2():
    ret = _results(
        """if a:
    pass
elif b:
    if c:
        d"""
    )
    assert ret in [
        {  # Python 3.7+
            "3:0 SIM102 Use a single if-statement instead of "
            "nested if-statements"
        },
        {
            # Python 3.6
            "3:5 SIM102 Use a single if-statement instead of "
            "nested if-statements"
        },
    ]


def test_sim_102_not_active1():
    ret = _results(
        """if a:
    if b:
        c
    else:
        d"""
    )
    assert ret == set()


def test_sim_102_not_active2():
    ret = _results(
        """if a:
    d
    if b:
        c"""
    )
    assert ret == set()


def test_sim_103_true_false():
    ret = _results(
        """if a:
    return True
else:
    return False"""
    )
    assert ret == {"1:0 SIM103 Return the condition a directly"}


def test_sim_104():
    ret = _results(
        """for item in iterable:
    yield item"""
    )
    assert ret == {"1:0 SIM104 Use 'yield from iterable'"}


def test_sim_105():
    ret = _results(
        """try:
    foo()
except ValueError:
    pass"""
    )
    assert ret == {"1:0 SIM105 Use 'contextlib.suppress(ValueError)'"}


def test_sim_105_pokemon():
    ret = _results(
        """try:
    foo()
except:
    pass"""
    )
    assert ret == {"1:0 SIM105 Use 'contextlib.suppress(Exception)'"}


def test_sim_106():
    ret = _results(
        """if cond:
    a
    b
    c
else:
    raise Exception"""
    )
    assert ret == {"1:0 SIM106 Handle error-cases first"}


def test_sim_106_no():
    ret = _results(
        """if cond:
    raise Exception
else:
    raise Exception"""
    )
    assert ret == set()


def test_sim_107():
    ret = _results(
        """def foo():
    try:
        1 / 0
        return "1"
    except:
        return "2"
    finally:
        return "3" """
    )
    assert ret == {"8:8 SIM107 Don't use return in try/except and finally"}


def test_sim_108():
    ret = _results(
        """if a:
    b = c
else:
    b = d"""
    )
    exp = (
        "1:0 SIM108 Use ternary operator "
        "'b = c if a else d' instead of if-else-block"
    )
    assert ret == {exp}


def test_sim_109():
    ret = _results("a == b or a == c")
    assert ret == {
        "1:0 SIM109 Use 'a in [b, c]' instead of 'a == b or a == c'"
    }


def test_sim_110_any():
    ret = _results(
        """for x in iterable:
    if check(x):
        return True
return False"""
    )
    assert ret == {"1:0 SIM110 Use 'return any(check(x) for x in iterable)'"}


def test_sim_111_all():
    ret = _results(
        """for x in iterable:
    if check(x):
        return False
return True"""
    )
    assert ret == {"1:0 SIM111 Use 'return all(check(x) for x in iterable)'"}


def test_sim_110_sim111_false_positive_check():
    ret = _results(
        """for x in iterable:
    if check(x):
        return "foo"
return "bar" """
    )
    assert ret == set()


def test_sim_201():
    ret = _results("not a == b")
    assert ret == {"1:0 SIM201 Use 'a != b' instead of 'not a == b'"}


def test_sim_202_base():
    ret = _results("not a != b")
    assert ret == {("1:0 SIM202 Use 'a == b' instead of 'not a != b'")}


def test_sim_203_base():
    ret = _results("not a in b")
    assert ret == {("1:0 SIM203 Use 'a not in b' instead of 'not a in b'")}


def test_sim_204_base():
    ret = _results("not a < b")
    assert ret == {("1:0 SIM204 Use 'a >= b' instead of 'not (a < b)'")}


def test_sim_205_base():
    ret = _results("not a <= b")
    assert ret == {("1:0 SIM205 Use 'a > b' instead of 'not (a <= b)'")}


def test_sim_206_base():
    ret = _results("not a > b")
    assert ret == {("1:0 SIM206 Use 'a <= b' instead of 'not (a > b)'")}


def test_sim_207_base():
    ret = _results("not a >= b")
    assert ret == {("1:0 SIM207 Use 'a < b' instead of 'not (a >= b)'")}


def test_sim_208_base():
    ret = _results("not (not a)")
    assert ret == {("1:0 SIM208 Use 'a' instead of 'not (not a)'")}


def test_sim_210_base():
    ret = _results("True if True else False")
    assert ret == {
        ("1:0 SIM210 Use 'bool(True)' instead of 'True if True else False'")
    }


def test_sim_211_base():
    ret = _results("False if True else True")
    assert ret == {
        ("1:0 SIM211 Use 'not True' instead of 'False if True else True'")
    }


def test_sim_212_base():
    ret = _results("b if not a else a")
    assert ret == {
        ("1:0 SIM212 Use 'a if a else b' instead of 'b if not a else a'")
    }


def test_sim_220_base():
    ret = _results("a and not a")
    assert ret == {("1:0 SIM220 Use 'False' instead of 'a and not a'")}


def test_sim_221_base():
    ret = _results("a or not a")
    assert ret == {("1:0 SIM221 Use 'True' instead of 'a or not a'")}


def test_sim_222_base():
    ret = _results("a or True")
    assert ret == {("1:0 SIM222 Use 'True' instead of '... or True'")}


def test_sim_223_base():
    ret = _results("a and False")
    assert ret == {("1:0 SIM223 Use 'False' instead of '... and False'")}


def test_sim_300_string():
    ret = _results("'Yoda' == i_am")
    assert ret == {
        (
            "1:0 SIM300 Use 'i_am == \"Yoda\"' "
            "instead of '\"Yoda\" == i_am' (Yoda-conditions)"
        )
    }


def test_sim_300_int():
    ret = _results("42 == age")
    assert ret == {
        "1:0 SIM300 Use 'age == 42' instead of '42 == age' (Yoda-conditions)"
    }
