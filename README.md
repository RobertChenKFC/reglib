# reglib
A library for experimentations with regular languages.

## Features
This library allows you to construct regular languages using NFAs, DFAs, regular expressions, or closure properties of regular languages, and explore properties of a language or relations between two regular languages. In particular, the features of this library include:
* Regular Expression to NFA
* NFA to DFA
* DFA Minimization
* NFA Visualization (using graphviz)
* Construct Regular Languages Using Closure Properties
  * Union
  * Intersection
  * Complement
  * Reverse
  * Concatenation
  * Star
* Explore Language Properties
  * Emptyness
  * Fullness
  * Element and Set Containment
  * Example String
  * Equality

## Limitations
This is a (incomplete) list of the current missing features or issues with the current library. Feel free to create an issue if you discover something unusual or want to propose a feature to be added to this library!
* NFA to Regular Expression
* More Complete Usage Examples
* Unoptimized Performance: minimizing large DFA's currently takes quite a while.

## Installation
Follow the steps below to install this library:
1. Clone this repository and change directory to the repository
```
git clone https://github.com/RobertChenKFC/reglib.git
cd reglib/
```
2. Install the packages in `requirements.txt`
```
pip install -r requirements.txt
```
3. Install this library as an editable pip package
```
pip install -e .
```

## Usage
*This current section provides the basic idea of how to use this library. For the time being, to see more specific examples, check out the `tests/` directory.*

This library contains the following main components:
### NFA
To create an NFA that looks like the following:

![Example of an NFA](/assets/images/nfa.png)

we can write the following code:
```
from reglib.nfa import Nfa, EPS
nfa = Nfa()
nfa.get_new_states(3)
nfa.set_initial_state(0)
nfa.set_accepting_states(2)
to = nfa.set_transition
to(0, '0', 0, 1)
to(0, '1', 0)
to(0, EPS, 1)
to(1, '0', 2)
to(2, '0', 2)
to(2, '1', 2)
```
The alphabet is automatically inferred by the symbols that appear in the given transitions (in this case, it is `{'0', '1'}`). Then, calling `nfa.to_graphviz("nfa.png")` creates the image above.
### DFA
Creating a DFA is basically the same as an NFA, just use `reglib.dfa.Dfa` instead of `reglib.nfa.Nfa`. The only differences are that DFAs have the following additional restrictions:
* Cannot create ε-transitions (i.e. `to(..., EPS, ...)`)
* Exactly one transition must be defined on each state and symbol in the alphabet
### Regular Expression
Regular expressions are defined by the following BNF:
```
<union-expr>  ::= <union-expr>'|'<concat-expr> | <concat-expr>
<concat-expr> ::= <concat-expr><star-expr> | <star-expr>
<star-expr>   ::= <term>'*' | <term>'+' | <term>'?' | <term>
<term>        ::= 'ε' | '∅' | '('<union-expr>')' | x
```
where `x` is any Unicode character that is not a reserved character in this grammar (i.e. a character that is not `|`, `*`, `+`, `?`, `ε`, or `∅`).
Informally speaking, the reserved character has the following meaning:
* `|` stands for choice
* `*` stands for 0 or more
* `+` stands for 1 or more
* `?` stands for 0 or 1
* `ε` stands for the empty string
* `∅` stands for the empty language

To create a regular expression `(0|(1(01*0)*1))*`, simply write the following code:
```
from reglib.regex import Regex
regex = Regex("(0|(1(01*0)*1))*")
```
### Language
The `Language` class is the heart of this library. It can be instantiated by a NFA/DFA or regular expression.
Below is an example that instantiates two regular languages from the objects we created above:
```
from reglib.language import Language
lang1 = Language.from_nfa(nfa)
lang2 = Language.from_regex(regex)
```
Then, `Language` objects allows us to explore properties of regular languages such as
* `lang1.intersect(lang2)` creates a regular language that is the intersection of `lang1` and `lang2`
* `lang1.complement()` creates a regular language that is the complement of `lang1` (i.e. contains all strings not in `lang1`)
* `lang1.reverse()` creates a regular language that is the reverse of `lang1` (i.e. contains all the reversed strings of `lang1`)
* `lang1.is_empty()` checks if `lang1` is the empty language (i.e. `lang1` contains no strings)
* `lang1.is_full()` checks if `lang1` is the full language (i.e. `lang1` contains all strings)
* `lang1.contains()` returns an example of a string in `lang1` (returns `None` if `lang1` is the empty language)
* `lang1.contains("0101")` checks if `lang1` contains the string `"0101"`
* `lang1.contains(lang2)` checks if `lang2` is a subset of `lang1`
* `lang1.is_equal_to(lang2)` checks if `lang1` is the same language as `lang2`

To give a concrete example, we can use this library to check if these two regular expressions `(a*c|b)*a*` and `b*(cb*|a)*` are the same:
```
from reglib.regex import Regex
from reglib.language import Language
lang1 = Language.from_regex(Regex("(a*c|b)*a*"))
lang2 = Language.from_regex(Regex("b*(cb*|a)*"))
print(lang1.is_equal_to(lang2)) # prints True
```
