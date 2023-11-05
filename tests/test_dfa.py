from reglib.nfa import Nfa, EPS
from reglib.dfa import Dfa

def test_from_nfa_0():
    nfa = Nfa()
    q0, q1 = nfa.get_new_states(2)
    nfa.set_initial_state(q0)
    nfa.set_accepting_states(q1)
    nfa.set_transition(q0, '0', q1)

    dfa = Dfa.from_nfa(nfa)
    q0 = dfa.get_initial_state()
    to = dfa.get_transition
    q1 = to(q0, '0')
    q2 = to(q1, '0')
    assert to(q2, '0') == q2
    assert dfa.get_accepting_states() == {q1}


def test_from_nfa_1():
    nfa = Nfa()
    q1, q2, q3 = nfa.get_new_states(3)
    nfa.set_initial_state(q1)
    nfa.set_accepting_states(q1)
    to = nfa.set_transition
    to(q1, 'b', q2)
    to(q1, EPS, q3)
    to(q2, 'a', q2, q3)
    to(q2, 'b', q3)
    to(q3, 'a', q1)

    dfa = Dfa.from_nfa(nfa)
    q13 = dfa.get_initial_state()
    to = dfa.get_transition
    assert to(q13,  'a') == q13
    q2   = to(q13,  'b')
    q23  = to(q2,   'a')
    q3   = to(q2,   'b')
    q123 = to(q23,  'a')
    assert to(q23,  'b') == q3
    assert to(q3,   'a') == q13
    q    = to(q3,   'b')
    assert to(q123, 'a') == q123
    assert to(q123, 'b') == q23
    assert to(q,    'a') == q
    assert to(q,    'b') == q
    assert set(dfa.get_accepting_states()) == {q13, q123}


def test_minimize_0():
    dfa = Dfa()
    dfa.get_new_states(3)
    dfa.set_initial_state(0)
    dfa.set_accepting_states(0, 1)
    to = dfa.set_transition
    to(0, '0', 1)
    to(0, '1', 2)
    to(1, '0', 1)
    to(1, '1', 2)
    to(2, '0', 0)
    to(2, '1', 2)

    dfa.minimize()
    assert dfa.get_num_states() == 2
    q0 = dfa.get_initial_state()
    to = dfa.get_transition
    assert to(q0, '0') == q0
    q1   = to(q0, '1')
    assert to(q1, '0') == q0
    assert to(q1, '1') == q1
    assert set(dfa.get_accepting_states()) == {q0}


def test_minimize_1():
    dfa = Dfa()
    dfa.get_new_states(6)
    dfa.set_initial_state(0)
    dfa.set_accepting_states(5)
    to = dfa.set_transition
    to(0, '0', 1)
    to(0, '1', 0)
    to(1, '0', 3)
    to(1, '1', 0)
    to(2, '0', 1)
    to(2, '1', 1)
    to(3, '0', 4)
    to(3, '1', 5)
    to(4, '0', 4)
    to(4, '1', 5)
    to(5, '0', 5)
    to(5, '1', 5)

    dfa.minimize()
    assert dfa.get_num_states() == 4
    q0 = dfa.get_initial_state()
    to = dfa.get_transition
    q1   = to(q0, '0')
    assert to(q0, '1') == q0
    q3   = to(q1, '0')
    assert to(q1, '1') == q0
    assert to(q3, '0') == q3
    q5   = to(q3, '1')
    assert to(q5, '0') == q5
    assert to(q5, '1') == q5
    assert set(dfa.get_accepting_states()) == {q5}


def test_from_nfa_and_minimize():
    nfa = Nfa()
    a, b, c, d, e, f = nfa.get_new_states(6)
    nfa.set_initial_state(a)
    nfa.set_accepting_states(f)
    to = nfa.set_transition
    to(a, '0', b)
    to(a, '1', d)
    to(b, '0', c)
    to(b, '1', c, f)
    to(c, '0', c)
    to(c, '1', b)
    to(c, EPS, b)
    to(d, '0', c, f)
    to(d, '1', a, e)
    to(e, '0', a, b, c, d, e, f)
    to(e, '1', e)
    to(f, '0', f)
    to(f, '1', f)

    dfa = Dfa.from_nfa(nfa)
    q1   = dfa.get_initial_state()
    to   = dfa.get_transition
    q4   = to(q1, '0')
    q7   = to(q1, '1')
    q5   = to(q4, '0')
    q6   = to(q4, '1')
    assert to(q7, '0') == q6
    q3   = to(q7, '1')
    assert to(q5, '0') == q5
    assert to(q5, '1') == q6
    assert to(q6, '0') == q6
    assert to(q6, '1') == q6
    q2   = to(q3, '0')
    q8   = to(q3, '1')
    assert to(q2, '0') == q2
    assert to(q2, '1') == q2
    assert to(q8, '0') == q2
    assert to(q8, '1') == q3

    dfa.minimize()
    assert dfa.get_num_states() == 4
    q1 = dfa.get_initial_state()
    to = dfa.get_transition
    q45  = to(q1,   '0')
    q378 = to(q1,   '1')
    assert to(q45,  '0') == q45
    q26  = to(q45,  '1')
    assert to(q378, '0') == q26
    assert to(q378, '1') == q378
    assert to(q26,  '0') == q26
    assert to(q26,  '1') == q26
    assert set(dfa.get_accepting_states()) == {q26}
