from reglib.dfa import Dfa
from collections import deque

class Language:
    def __init__(self, nfa):
        self._nfa = nfa
        self._dfa = None

    @staticmethod
    def from_regex(regex):
        return Language(regex.to_nfa())

    @staticmethod
    def from_nfa(nfa):
        return Language(nfa)

    def _finalize(self):
        if self._dfa is None:
            if isinstance(self._nfa, Dfa):
                self._dfa = self._nfa
            else:
                self._dfa = Dfa.from_nfa(self._nfa)
            self._dfa.minimize()

    def union(self, other):
        return Language(self._nfa.union(other._nfa))

    def intersect(self, other):
        self._finalize()
        other._finalize()
        return Language(self._dfa.intersect(other._dfa))

    def complement(self):
        self._finalize()
        return Language(self._dfa.complement())

    def reverse(self):
        return Language(self._nfa.reverse())

    def concat(self, other):
        return Language(self._nfa.concat(other._nfa))

    def star(self):
        return Language(self._nfa.star())

    def contains(self, x=None):
        self._finalize()
        if x is None:
            # Returns some string in the language; if this is the empty
            # language, returns None
            q = deque()
            initial_state = self._dfa.get_initial_state()
            q.append((initial_state, ""))
            visited = {initial_state}
            accepting_states = self._dfa.get_accepting_states()
            alphabet = self._dfa.get_alphabet()
            while len(q) > 0:
                from_state, cur_str = q.popleft()
                if from_state in accepting_states:
                    return cur_str
                for symbol in alphabet:
                    to_state = self._dfa.get_transition(from_state, symbol)
                    if to_state not in visited:
                        visited.add(to_state)
                        q.append((to_state, cur_str + symbol))
            return None
        elif isinstance(x, str):
            # Checks if the string is in the language
            state = self._dfa.get_initial_state()
            alphabet = self._dfa.get_alphabet()
            for symbol in x:
                if symbol not in alphabet:
                    return False
                state = self._dfa.get_transition(state, symbol)
            return state in self._dfa.get_accepting_states()
        elif isinstance(x, Language):
            # Checks if the entire language x is contained in this language
            return self.complement().intersect(x).is_empty()

    def is_empty(self):
        return self.contains() is None

    def is_full(self):
        return self.complement().is_empty()

    def is_equal_to(self, other):
        return self.contains(other) and other.contains(self)
            
