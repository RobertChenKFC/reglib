from reglib.regex import Regex
from reglib.dfa import Dfa

def test_regex_0():
    regex = Regex("(0|1)*(001)(0|1)*")
    dfa = Dfa.from_regex(regex)
    dfa.minimize()

    assert dfa.get_num_states() == 4
    e1 = dfa.get_initial_state()
    to = dfa.get_transition
    e2   = to(e1, '0')
    assert to(e1, '1') == e1
    e3   = to(e2, '0')
    assert to(e2, '1') == e1
    assert to(e3, '0') == e3
    e4   = to(e3, '1')
    assert to(e4, '0') == e4
    assert to(e4, '1') == e4
    assert dfa.get_accepting_states() == {e4}


def test_regex_1():
    regex = Regex("(c|b+c)*")
    dfa = Dfa.from_regex(regex)
    dfa.minimize()

    assert dfa.get_num_states() == 2
    q0 = dfa.get_initial_state()
    to = dfa.get_transition
    q1   = to(q0, 'b')
    assert to(q0, 'c') == q0
    assert to(q1, 'b') == q1
    assert to(q1, 'c') == q0
    assert dfa.get_accepting_states() == {q0}


def test_regex_2():
    regex = Regex("ab(a|c|b+c)*b+a")
    dfa = Dfa.from_regex(regex)
    dfa.minimize()

    assert dfa.get_num_states() == 6
    q0 = dfa.get_initial_state()
    to = dfa.get_transition
    q2   = to(q0, 'a')
    q1   = to(q0, 'b')
    assert to(q0, 'c') == q1
    assert to(q1, 'a') == q1
    assert to(q1, 'b') == q1
    assert to(q1, 'c') == q1
    assert to(q2, 'a') == q1
    q3   = to(q2, 'b')
    assert to(q2, 'c') == q1
    assert to(q3, 'a') == q3
    q4   = to(q3, 'b')
    assert to(q3, 'c') == q3
    q5   = to(q4, 'a')
    assert to(q4, 'b') == q4
    assert to(q4, 'c') == q3
    assert to(q5, 'a') == q1
    assert to(q5, 'b') == q1
    assert to(q5, 'c') == q1
    assert dfa.get_accepting_states() == {q5}

    
def test_regex_3():
    regex = Regex("0+|(1|0+1)(11|10+1|01*0)*10+")
    dfa = Dfa.from_regex(regex)
    dfa.minimize()

    assert dfa.get_num_states() == 4
    q0 = dfa.get_initial_state()
    to = dfa.get_transition
    q1   = to(q0, '0')
    q2   = to(q0, '1')
    assert to(q1, '0') == q1
    assert to(q1, '1') == q2
    q3   = to(q2, '0')
    assert to(q2, '1') == q0
    assert to(q3, '0') == q2
    assert to(q3, '1') == q3
    assert dfa.get_accepting_states() == {q1}

def test_regex_4():
    regex = Regex("0?(1|ε)")
    dfa = Dfa.from_regex(regex)
    dfa.minimize()

    assert dfa.get_num_states() == 4
    q0 = dfa.get_initial_state()
    to = dfa.get_transition
    q1   = to(q0, '0')
    q2   = to(q0, '1')
    q3   = to(q1, '0')
    assert to(q1, '1') == q2
    assert to(q2, '0') == q3
    assert to(q2, '1') == q3
    assert to(q3, '0') == q3
    assert to(q3, '1') == q3
    assert dfa.get_accepting_states() == {q0, q1, q2}
