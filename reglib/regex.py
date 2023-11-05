from reglib.nfa import Nfa

_RESERVED_CHARS = {'(', ')', '*', '+', '|'}

class _Source:
    def __init__(self, string):
        self.string = string
        self.pos = 0


class _EmptyNode:
    def to_nfa(self):
        nfa = Nfa()
        q0 = nfa.get_new_state()
        nfa.set_initial_state(q0)
        return nfa


class _TermNode:
    def __init__(self, letter):
        self.letter = letter

    @staticmethod
    def parse(src):
        c = src.string[src.pos]
        src.pos += 1
        if c == 'ε':
            return _StarNode(_EmptyNode())
        elif c == '∅':
            return _EmptyNode()
        elif c == '(':
            node = _UnionNode.parse(src)
            assert src.pos < len(src.string) and src.string[src.pos] == ')', \
                f"Expected ')' at position {src.pos} of the string, got " + \
                (
                    f"{src.string[src.pos]} instead"
                    if src.pos < len(src.string)
                    else f"the end of string instead"
                )
            src.pos += 1
            return node
        elif c in _RESERVED_CHARS:
            assert False, \
                f"Unexpected character {c} at position {src.pos - 1} of " \
                f"the string"
        else:
            return _TermNode(c)

    def to_nfa(self):
        nfa = Nfa()
        q0, q1 = nfa.get_new_states(2)
        nfa.set_initial_state(q0)
        nfa.set_accepting_states(q1)
        nfa.set_transition(q0, self.letter, q1)
        return nfa


class _StarNode:
    def __init__(self, node):
        self.node = node

    @staticmethod
    def parse(src):
        node = _TermNode.parse(src)
        if src.pos >= len(src.string):
            return node
        c = src.string[src.pos]
        if c == '*':
            src.pos += 1
            return _StarNode(node)
        elif c == '+':
            src.pos += 1
            return _ConcatNode(node, _StarNode(node))
        elif c == '?':
            src.pos += 1
            return _UnionNode(node, _StarNode(_EmptyNode()))
        else:
            return node

    def to_nfa(self):
        return self.node.to_nfa().star()


class _ConcatNode:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2

    @staticmethod
    def parse(src):
        node1 = _StarNode.parse(src)
        return _ConcatNode._parseTail(node1, src)

    @staticmethod
    def _parseTail(node1, src):
        if src.pos >= len(src.string) or src.string[src.pos] in {'|', ')'}:
            return node1
        node2 = _StarNode.parse(src)
        return _ConcatNode._parseTail(_ConcatNode(node1, node2), src)

    def to_nfa(self):
        return self.node1.to_nfa().concat(self.node2.to_nfa())


class _UnionNode:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2

    @staticmethod
    def parse(src):
        node1 = _ConcatNode.parse(src)
        return _UnionNode._parseTail(node1, src)

    @staticmethod
    def _parseTail(node1, src):
        if src.pos >= len(src.string) or src.string[src.pos] == ')':
            return node1
        assert src.string[src.pos] == '|', \
                f"Expected '|' at position {src.pos} of the string, got " \
                f"{src.string[src.pos]} instead"
        src.pos += 1
        node2 = _ConcatNode.parse(src)
        return _UnionNode._parseTail(_UnionNode(node1, node2), src)

    def to_nfa(self):
        return self.node1.to_nfa().union(self.node2.to_nfa())


class Regex:
    def __init__(self, string):
        self.node = _UnionNode.parse(_Source(string))

    def to_nfa(self):
        return self.node.to_nfa()
