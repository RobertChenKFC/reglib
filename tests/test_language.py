from reglib.regex import Regex
from reglib.dfa import Dfa
from reglib.language import Language

def test_language_contains():
    lang = Language.from_regex(Regex("ab*c?"))
    example = lang.contains()
    assert len(example) > 0
    assert example[0] == 'a'
    b_cnt = 0
    c_cnt = 0
    for symbol in example[1:]:
        if symbol == b:
            assert c_cnt == 0
            b_cnt += 1
        elif symbol == c:
            assert c_cnt == 0
            c_cnt += 1

    assert lang.contains("abbbbbbbbbc")
    assert not lang.contains("abbbbbbcb")

    lang2 = Language.from_regex(Regex("a+b*c*"))
    assert lang2.contains(lang)


def build_lang_multiple_of(x):
    dfa = Dfa()
    dfa.get_new_states(x)
    dfa.set_initial_state(0)
    dfa.set_accepting_states(0)
    for r in range(x):
        for s in range(2):
            dfa.set_transition(r, str(s), (2 * r + s) % x)
    return Language.from_nfa(dfa)


def test_language_union():
    lang5 = build_lang_multiple_of(5)
    lang7 = build_lang_multiple_of(7)
    lang5_or_7 = lang5.union(lang7)
    assert lang5_or_7.contains(bin(5 * 123839)[2:])
    assert lang5_or_7.contains(bin(7 * 824098)[2:])
    assert not lang5_or_7.contains(bin(5 * 7 + 3)[2:])
    assert lang5_or_7.contains(lang5)
    assert lang5_or_7.contains(lang7)


def test_language_intersect():
    lang11 = build_lang_multiple_of(11)
    lang13 = build_lang_multiple_of(13)
    lang11_and_13 = lang11.intersect(lang13)
    assert not lang11_and_13.contains(bin(11)[2:])
    assert not lang11_and_13.contains(bin(13)[2:])
    assert lang11_and_13.contains(bin(11 * 13 * 31829)[2:])
    assert lang11.contains(lang11_and_13)
    assert lang13.contains(lang11_and_13)


def test_language_reverse():
    lang_not_abc = Language.from_regex(
        Regex("(a|b|c)*cba(a|b|c)*")
    ).complement().reverse()
    assert lang_not_abc.contains("cbacbacba")
    assert lang_not_abc.contains("aaaaaaaaabbbbbbbbacbbbbbbaaaaa")
    assert not lang_not_abc.contains("aaaaaaaaabbbbbbbbabcbbbbbbaaaaa")


def test_language_concat():
    lang3 = build_lang_multiple_of(3)
    lang5 = build_lang_multiple_of(5)
    lang3_concat_5 = lang3.concat(lang5)
    assert lang3_concat_5.contains(bin(3 * 1345 * (2 ** 30) + 5 * 12389)[2:])
    assert not lang3_concat_5.contains(bin(3 * (2 ** 30) + 2)[2:])
    assert lang3_concat_5.contains(lang3)
    assert lang3_concat_5.contains(lang5)


def test_language_star():
    lang_not_abc = Language.from_regex(
        Regex("(a|b|c)*(abc)(a|b|c)*")
    ).complement()
    lang_not_abc_equiv = lang_not_abc.star()

    assert lang_not_abc_equiv.contains(lang_not_abc)
    assert lang_not_abc_equiv.contains(lang_not_abc.complement())


def test_language_relations():
    lang_ab = Language.from_regex(Regex("a+b"))
    lang_ba = Language.from_regex(Regex("b+a"))
    assert lang_ab.intersect(lang_ba).is_empty()

    lang_ab = Language.from_regex(Regex("a*b"))
    lang_ba = Language.from_regex(Regex("b*a"))
    assert lang_ab.union(lang_ba).star().is_full()

    lang_no_ab = Language.from_regex(Regex("(a*c|b)*a*"))
    lang_no_ab_equiv = Language.from_regex(Regex("b*(cb*|a)*"))
    assert lang_no_ab.is_equal_to(lang_no_ab_equiv)
