import pygraphviz as pgv

class EPS:
    pass

class Nfa:
    def __init__(self):
        self._num_states = 0
        self._transitions = dict()
        self._initial_state = None
        self._accepting_states = set()

        self._alphabet = None
        self._eps_closure = None
        self._finalized = False

    def get_new_state(self):
        state = self._num_states
        self._num_states += 1
        return state

    def get_new_states(self, num_new_states):
        states = range(self._num_states, self._num_states + num_new_states)
        self._num_states += num_new_states
        return states

    def get_num_states(self):
        return self._num_states

    def get_states(self):
        return range(self._num_states)

    def set_initial_state(self, initial_state):
        assert 0 <= initial_state < self._num_states
        self._initial_state = initial_state
        self._finalized = False

    def get_initial_state(self):
        return self._initial_state

    def set_accepting_states(self, *accepting_states):
        for state in accepting_states:
            assert 0 <= state < self._num_states
        self._accepting_states = self._accepting_states.union(accepting_states)
        self._finalized = False

    def get_accepting_states(self):
        return self._accepting_states

    def set_transition(self, from_state, symbol, *to_states):
        assert 0 <= from_state < self._num_states
        assert len(to_states) >= 1

        self._transitions.setdefault(from_state, dict())
        self._transitions[from_state].setdefault(symbol, set())
        for to_state in to_states:
            assert 0 <= to_state < self._num_states
            self._transitions[from_state][symbol].add(to_state)

        self._finalized = False

    def get_transitions(self, from_state, symbol):
        if (
            from_state not in self._transitions or
            symbol not in self._transitions[from_state]
        ):
            return set()
        return self._transitions[from_state][symbol]

    def _validate(self):
        assert self._initial_state is not None

    def _finalize(self):
        if not self._finalized:
            self._alphabet = set()
            for from_state, transitions_from_state in self._transitions.items():
                self._alphabet = self._alphabet.union(
                    transitions_from_state.keys()
                )

            self._eps_closure = dict()
            for from_state in self.get_states():
                from_state_closure = set()
                unprocessed_states = {from_state}
                while unprocessed_states:
                    state = unprocessed_states.pop()
                    from_state_closure.add(state)
                    if state not in self._transitions:
                        continue
                    transitions_state = self._transitions[state]
                    if EPS in transitions_state:
                        to_states = transitions_state[EPS]
                        for to_state in to_states:
                            if (
                                to_state not in from_state_closure and
                                to_state not in unprocessed_states
                            ):
                                unprocessed_states.add(to_state)
                self._eps_closure[from_state] = from_state_closure

            if EPS in self._alphabet:
                self._alphabet.remove(EPS)

            self._finalized = True

    def get_alphabet(self):
        self._finalize()
        return self._alphabet

    def _add_transitions_from(self, nfa, state_diff=0):
        for from_state, transitions_from_state in nfa._transitions.items():
            for symbol, to_states in transitions_from_state.items():
                self.set_transition(
                    from_state + state_diff, symbol,
                    *[p + state_diff for p in to_states]
                )

    def union(self, other):
        nfa = Nfa()
        n, m = self.get_num_states(), other.get_num_states()
        nfa.get_new_states(n + m + 1)
        nfa.set_initial_state(0)
        nfa.set_accepting_states(
            *[p + 1     for p in self._accepting_states],
            *[p + n + 1 for p in other._accepting_states]
        )

        to = nfa.set_transition
        to(0, EPS, self._initial_state + 1)
        to(0, EPS, other._initial_state + n + 1)
        nfa._add_transitions_from(self, state_diff=1)
        nfa._add_transitions_from(other, state_diff=n + 1)

        return nfa

    def reverse(self):
        self._finalize()

        nfa = Nfa()
        n = self.get_num_states()
        nfa.get_new_states(n + 1)
        nfa.set_initial_state(0)
        nfa.set_accepting_states(self._initial_state + 1)

        to = nfa.set_transition
        to(0, EPS, *[p + 1 for p in self._accepting_states])
        for from_state, transitions_from_state in self._transitions.items():
            for symbol, to_states in transitions_from_state.items():
                for to_state in to_states:
                    to(to_state + 1, symbol, from_state + 1)

        return nfa

    def concat(self, other):
        self._finalize()
        other._finalize()

        nfa = Nfa()
        n, m = self.get_num_states(), other.get_num_states()
        nfa.get_new_states(n + m)
        nfa.set_initial_state(self._initial_state)
        nfa.set_accepting_states(*[p + n for p in other._accepting_states])

        to = nfa.set_transition
        for p in self._accepting_states:
            to(p, EPS, other._initial_state + n)
        nfa._add_transitions_from(self)
        nfa._add_transitions_from(other, state_diff=n)

        return nfa

    def star(self):
        self._finalize()

        nfa = Nfa()
        n = self.get_num_states()
        nfa.get_new_states(n + 1)
        nfa.set_initial_state(0)
        nfa.set_accepting_states(0, *[p + 1 for p in self._accepting_states])

        to = nfa.set_transition
        to(0, EPS, self._initial_state + 1)
        for p in self._accepting_states:
            to(p + 1, EPS, 0)
        nfa._add_transitions_from(self, state_diff=1)

        return nfa

    def to_graphviz(self, filename):
        self._finalize()

        g = pgv.AGraph(strict=False, directed=True)
        for state in self.get_states():
            if state in self._accepting_states:
                g.add_node(state, shape="doublecircle")
            else:
                g.add_node(state)

        for from_state, transitions_from_state in self._transitions.items():
            for symbol, to_states in transitions_from_state.items():
                for to_state in to_states:
                    if symbol == EPS:
                        g.add_edge(from_state, to_state, label="ε")
                    else:
                        g.add_edge(from_state, to_state, label=symbol)

        g.layout(prog="dot")
        g.draw(filename)
        
