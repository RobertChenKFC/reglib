from reglib.nfa import Nfa, EPS
from reglib.regex import Regex

class Dfa(Nfa):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._minimized = False

    def get_new_state(self, *args, **kwargs):
        self._minimized = False
        return super().get_new_state(*args, **kwargs)

    def get_new_states(self, *args, **kwargs):
        self._minimized = False
        return super().get_new_states(*args, **kwargs)

    def set_initial_state(self, *args, **kwargs):
        self._minimized = False
        return super().set_initial_state(*args, **kwargs)

    def set_accepting_states(self, *args, **kwargs):
        self._minimized = False
        return super().set_accepting_states(*args, **kwargs)

    def set_transition(self, from_state, symbol, to_state):
        assert symbol != EPS
        super().set_transition(from_state, symbol, to_state)
        self._minimized = False

    def get_transition(self, from_state, symbol):
        to_states = self.get_transitions(from_state, symbol)
        to_state, = to_states
        return to_state
        
    def _validate(self):
        super._validate()
        assert len(self._transitions) == self.num_states
        alphabet = self.get_alphabet()
        for from_state, transitions_from_state in self._transitions.items():
            assert len(transitions_from_state) == len(alphabet)
            for symbol, to_states in transitions_from_state.items():
                assert len(to_states) == 1

    def _add_transitions_from(self, *args, **kwargs):
        self._minimized = False
        return super()._add_transitions_from(*args, **kwargs)

    @staticmethod
    def from_nfa(nfa):
        nfa._finalize()
        dfa_initial_state = frozenset(nfa._eps_closure[nfa._initial_state])
        unprocessed_dfa_states = {dfa_initial_state}
        dfa_states = dict()
        dfa_transitions = list()
        while unprocessed_dfa_states:
            dfa_state = unprocessed_dfa_states.pop()
            dfa_states[dfa_state] = len(dfa_states)
            for symbol in nfa._alphabet:
                new_dfa_state = set()
                for from_state in dfa_state:
                    if from_state not in nfa._transitions:
                        continue
                    transitions_from_state = nfa._transitions[from_state]
                    if symbol not in transitions_from_state:
                        continue
                    to_states = transitions_from_state[symbol]
                    for to_state in to_states:
                        new_dfa_state = new_dfa_state.union(
                            nfa._eps_closure[to_state]
                        )
                new_dfa_state = frozenset(new_dfa_state)
                if (
                    new_dfa_state not in unprocessed_dfa_states and
                    new_dfa_state not in dfa_states
                ):
                    unprocessed_dfa_states.add(new_dfa_state)
                dfa_transitions.append((dfa_state, symbol, new_dfa_state))

        dfa = Dfa()
        dfa.get_new_states(len(dfa_states))
        dfa.set_initial_state(0)
        for dfa_state, dfa_state_num in dfa_states.items():
            if dfa_state.intersection(nfa._accepting_states):
                dfa.set_accepting_states(dfa_state_num)
        for from_dfa_state, symbol, to_dfa_state in dfa_transitions:
            from_dfa_state_num = dfa_states[from_dfa_state]
            to_dfa_state_num = dfa_states[to_dfa_state]
            dfa.set_transition(from_dfa_state_num, symbol, to_dfa_state_num)
        return dfa

    @staticmethod
    def from_regex(regex):
        return Dfa.from_nfa(regex.to_nfa())

    def minimize(self):
        if self._minimized:
            return

        self._finalize()

        dist = [[False] * (i + 1) for i in range(self._num_states)]
        for i in range(self._num_states):
            for j in range(i):
                dist[i][j] = (
                    (i in self._accepting_states) !=
                    (j in self._accepting_states)
                )
        changed = True
        while changed:
            changed = False
            for i in range(self._num_states):
                for j in range(i):
                    if dist[i][j]:
                        continue
                    for symbol in self._alphabet:
                        i2 = self.get_transition(i, symbol)
                        j2 = self.get_transition(j, symbol)
                        if dist[max(i2, j2)][min(i2, j2)]:
                            dist[i][j] = True
                            changed = True
                            break

        partition = list(range(self._num_states))
        def get_partition(p):
            if partition[p] == p:
                return p
            partition[p] = get_partition(partition[p])
            return partition[p]

        for i in range(self._num_states):
            for j in range(i):
                if not dist[i][j]:
                    partition[i] = get_partition(j)

        stack = [get_partition(self._initial_state)]
        processed = [False] * self._num_states
        processed[stack[0]] = True
        transitions = []
        partition_to_state = dict()
        while stack:
            p = stack.pop()
            if p not in partition_to_state:
                partition_to_state[p] = len(partition_to_state)
            for symbol in self._alphabet:
                q = get_partition(self.get_transition(p, symbol))
                transitions.append((p, symbol, q))
                if not processed[q]:
                    stack.append(q)
                    processed[q] = True

        self._num_states = 0
        self._transitions = dict()
        self.get_new_states(len(partition_to_state))
        self.set_initial_state(
            partition_to_state[get_partition(self._initial_state)]
        )
        new_accepting_states = [
            partition_to_state[get_partition(p)] for p in self._accepting_states
        ]
        self._accepting_states = set()
        self.set_accepting_states(*new_accepting_states)
        for p, symbol, q in transitions:
            self.set_transition(
                partition_to_state[p], symbol, partition_to_state[q]
            )

        self.minimized = True

    def complement(self):
        self._finalize()

        dfa = Dfa()
        dfa.get_new_states(self._num_states)
        dfa.set_initial_state(self._initial_state)
        dfa.set_accepting_states(*[
            p for p in self.get_states() if p not in self._accepting_states
        ])
        dfa._add_transitions_from(self)

        return dfa

    def intersect(self, other):
        self._finalize()
        if not isinstance(other, Dfa):
            other = Dfa.from_nfa(other)
        return Dfa.from_nfa(
            self.complement().union(other.complement())
        ).complement()

