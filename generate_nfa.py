"""
Generate 9 NFA JFLAP (.jff) files for the Lexical Convention Rules (A.4).
Uses SYMBOLIC labels (letter, digit, etc.) so diagrams are CLEAN and READABLE.

Rule 1: Comments        Rule 2: Whitespace/Delimiters
Rule 3: Identifiers     Rule 4: Numbers (num)
Rule 5: Keywords        Rule 6: Relop
Rule 7: Addop           Rule 8: Mulop
Rule 9: Assignop
"""
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def xml_escape(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    return s


def make_jff(states, transitions, filename, description=""):
    """Write a JFLAP .jff automaton file."""
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    lines.append('<!--Created with JFLAP 7.1.-->')
    if description:
        lines.append(f'<!--{description}-->')
    lines.append('<structure>')
    lines.append('\t<type>fa</type>')
    lines.append('\t<automaton>')
    lines.append('\t\t<!--The list of states.-->')
    for s in states:
        lines.append(f'\t\t<state id="{s["id"]}" name="{s["name"]}">')
        lines.append(f'\t\t\t<x>{s["x"]}</x>')
        lines.append(f'\t\t\t<y>{s["y"]}</y>')
        if s.get("initial"):
            lines.append('\t\t\t<initial/>')
        if s.get("final"):
            lines.append('\t\t\t<final/>')
        lines.append('\t\t</state>')
    lines.append('\t\t<!--The list of transitions.-->')
    for t in transitions:
        rv = xml_escape(str(t["read"]))
        lines.append('\t\t<transition>')
        lines.append(f'\t\t\t<from>{t["from"]}</from>')
        lines.append(f'\t\t\t<to>{t["to"]}</to>')
        lines.append(f'\t\t\t<read>{rv}</read>')
        lines.append('\t\t</transition>')
    lines.append('\t</automaton>')
    lines.append('</structure>')
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"  [OK] {filename}: {len(states)} states, {len(transitions)} transitions")


print("=" * 60)
print("Generating 9 NFA JFLAP files  (Lexical Rules A.4)")
print("Using symbolic labels for clarity")
print("=" * 60)

# ================================================================
# RULE 1 : Comments  { ... }
# Surrounded by { and }.  Content may NOT contain {.
# NFA:  q0 --{--> q1 --not_{--> q1 (loop) --}--> q2 (accept)
# ================================================================
print("\nRule 1: Comments")
s1 = [
    {"id": 0, "name": "q0",     "x": 100, "y": 200, "initial": True},
    {"id": 1, "name": "q1",     "x": 400, "y": 200},
    {"id": 2, "name": "q2",     "x": 700, "y": 200, "final": True},
]
t1 = [
    {"from": 0, "to": 1, "read": "{"},
    {"from": 1, "to": 1, "read": "letter"},
    {"from": 1, "to": 1, "read": "digit"},
    {"from": 1, "to": 1, "read": "blank"},
    {"from": 1, "to": 1, "read": "other"},
    {"from": 1, "to": 2, "read": "}"},
]
make_jff(s1, t1, "rule1_comments.jff",
         "Rule 1: Comments  { content }  content has no {")

# ================================================================
# RULE 2 : Whitespace / Delimiters
# Blanks between tokens optional.  Keywords MUST be surrounded
# by blank | newline | beginning-of-program | final dot.
# NFA:  q0 --ws--> q1(accept)  q1 --ws--> q1
#        (ws = blank | newline | tab)
# ================================================================
print("\nRule 2: Whitespace / Delimiters")
s2 = [
    {"id": 0, "name": "q0",     "x": 100, "y": 200, "initial": True},
    {"id": 1, "name": "q1",     "x": 450, "y": 200, "final": True},
]
t2 = [
    {"from": 0, "to": 1, "read": "blank"},
    {"from": 0, "to": 1, "read": "newline"},
    {"from": 0, "to": 1, "read": "tab"},
    {"from": 1, "to": 1, "read": "blank"},
    {"from": 1, "to": 1, "read": "newline"},
    {"from": 1, "to": 1, "read": "tab"},
]
make_jff(s2, t2, "rule2_whitespace.jff",
         "Rule 2: Whitespace NFA - blank+ | newline+ | tab+")

# ================================================================
# RULE 3 : Identifiers   id -> letter ( letter | digit )*
# letter = [a-zA-Z]   digit = [0-9]
# NFA:  q0 --letter--> q1(accept)  q1 --letter--> q1  q1 --digit--> q1
# ================================================================
print("\nRule 3: Identifiers")
s3 = [
    {"id": 0, "name": "q0",     "x": 100, "y": 200, "initial": True},
    {"id": 1, "name": "q1",     "x": 500, "y": 200, "final": True},
]
t3 = [
    {"from": 0, "to": 1, "read": "letter"},
    {"from": 1, "to": 1, "read": "letter"},
    {"from": 1, "to": 1, "read": "digit"},
]
make_jff(s3, t3, "rule3_identifier.jff",
         "Rule 3: Identifier NFA  id = letter (letter | digit)*")

# ================================================================
# RULE 4 : Numbers (num)
#   digits           -> digit digit*
#   optional_fraction -> . digits | epsilon
#   optional_exponent -> E ( + | - | eps ) digits | epsilon
#   num -> digits optional_fraction optional_exponent
#
# States:
#   q0  start
#   q1  (accept) got digits                     -- integer
#   q2  got '.'                                  -- need fraction digit
#   q3  (accept) got fraction digits             -- real number
#   q4  got 'E'                                  -- need exponent digits
#   q5  got E +/-                                -- need exponent digits
#   q6  (accept) got exponent digits             -- number with exponent
# ================================================================
print("\nRule 4: Numbers (num)")
s4 = [
    {"id": 0, "name": "q0",     "x": 60,  "y": 250, "initial": True},
    {"id": 1, "name": "q1",     "x": 240, "y": 250, "final": True},
    {"id": 2, "name": "q2",     "x": 430, "y": 100},
    {"id": 3, "name": "q3",     "x": 630, "y": 100, "final": True},
    {"id": 4, "name": "q4",     "x": 530, "y": 400},
    {"id": 5, "name": "q5",     "x": 730, "y": 400},
    {"id": 6, "name": "q6",     "x": 900, "y": 250, "final": True},
]
t4 = [
    # digits
    {"from": 0, "to": 1, "read": "digit"},
    {"from": 1, "to": 1, "read": "digit"},
    # optional_fraction
    {"from": 1, "to": 2, "read": "."},
    {"from": 2, "to": 3, "read": "digit"},
    {"from": 3, "to": 3, "read": "digit"},
    # optional_exponent (from integer)
    {"from": 1, "to": 4, "read": "E"},
    # optional_exponent (from fraction)
    {"from": 3, "to": 4, "read": "E"},
    # sign after E
    {"from": 4, "to": 5, "read": "+"},
    {"from": 4, "to": 5, "read": "-"},
    # exponent digits (no sign)
    {"from": 4, "to": 6, "read": "digit"},
    # exponent digits (after sign)
    {"from": 5, "to": 6, "read": "digit"},
    {"from": 6, "to": 6, "read": "digit"},
]
make_jff(s4, t4, "rule4_number.jff",
         "Rule 4: Number NFA  num = digits [.digits] [E[+-]digits]")

# ================================================================
# RULE 5 : Keywords (reserved words)
# "Keywords are reserved and appear in boldface in the grammar."
# Pascal-subset keywords:
#   program, var, begin, end, if, then, else, while, do, not
#
# Each keyword is a separate linear chain from q0 to its own
# accept state.  Shared prefixes are MERGED to keep it neat:
#   - e -> l -> s -> e  (else)
#   - e -> n -> d       (end)
#   These share the first 'e' state.
# ================================================================
print("\nRule 5: Keywords")

# Build a trie for shared-prefix merging
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None   # non-None if a keyword ends here

root = TrieNode()
kw_list = ["program", "var", "begin", "end",
           "if", "then", "else", "while", "do", "not"]

for kw in kw_list:
    node = root
    for ch in kw:
        if ch not in node.children:
            node.children[ch] = TrieNode()
        node = node.children[ch]
    node.word = kw

# BFS to assign state IDs & positions
from collections import deque
states5 = [{"id": 0, "name": "q0", "x": 60, "y": 350, "initial": True}]
trans5  = []
sid = 1

# Y slots for the 10 keywords (spread out)
kw_y = {}
y_start = 30
y_step  = 75
for i, kw in enumerate(kw_list):
    kw_y[kw] = y_start + i * y_step

queue = deque()
# (TrieNode, parent_state_id, depth, y_hint)
for ch in sorted(root.children.keys()):
    queue.append((root.children[ch], 0, 1, ch))

# We need a mapping from TrieNode -> state_id
node_to_sid = {id(root): 0}

while queue:
    node, parent_sid, depth, edge_char = queue.popleft()
    nid = sid
    sid += 1
    node_to_sid[id(node)] = nid

    # Determine y: use the keyword's y if this node is on that keyword's path
    # For shared nodes, pick the average of all keywords that pass through it
    def collect_words(n):
        words = []
        if n.word:
            words.append(n.word)
        for c2 in n.children.values():
            words.extend(collect_words(c2))
        return words

    words_under = collect_words(node)
    y = int(sum(kw_y.get(w, 350) for w in words_under) / max(len(words_under), 1))

    x = 60 + depth * 150
    nm = node.word.upper() if node.word else f"q{nid}"
    st = {"id": nid, "name": nm, "x": x, "y": y}
    if node.word:
        st["final"] = True
    states5.append(st)
    trans5.append({"from": parent_sid, "to": nid, "read": edge_char})

    for ch2 in sorted(node.children.keys()):
        queue.append((node.children[ch2], nid, depth + 1, ch2))

make_jff(states5, trans5, "rule5_keywords.jff",
         "Rule 5: Keywords NFA - program var begin end if then else while do not")

# ================================================================
# RULE 6 : Relational Operators  (relop)
# =   <>   <   <=   >=   >
# (<> means "not equal")
#
# q0 --= -->  q1 (accept)  EQ
# q0 --< -->  q2 (accept)  LT
# q2 --> -->  q3 (accept)  NE  (<>)
# q2 --= -->  q4 (accept)  LE  (<=)
# q0 --> -->  q5 (accept)  GT
# q5 --= -->  q6 (accept)  GE  (>=)
# ================================================================
print("\nRule 6: Relop")
s6 = [
    {"id": 0, "name": "q0", "x": 80,  "y": 280, "initial": True},
    {"id": 1, "name": "EQ", "x": 380, "y": 60,  "final": True},
    {"id": 2, "name": "LT", "x": 350, "y": 230, "final": True},
    {"id": 3, "name": "NE", "x": 620, "y": 160, "final": True},
    {"id": 4, "name": "LE", "x": 620, "y": 300, "final": True},
    {"id": 5, "name": "GT", "x": 350, "y": 450, "final": True},
    {"id": 6, "name": "GE", "x": 620, "y": 450, "final": True},
]
t6 = [
    {"from": 0, "to": 1, "read": "="},
    {"from": 0, "to": 2, "read": "<"},
    {"from": 2, "to": 3, "read": ">"},
    {"from": 2, "to": 4, "read": "="},
    {"from": 0, "to": 5, "read": ">"},
    {"from": 5, "to": 6, "read": "="},
]
make_jff(s6, t6, "rule6_relop.jff",
         "Rule 6: Relop NFA  =  <>  <  <=  >=  >")

# ================================================================
# RULE 7 : Addition Operators  (addop)
# +   -   or
#
# q0 --+ --> q1 (accept)
# q0 --- --> q2 (accept)
# q0 --o --> q3 --r--> q4 (accept)
# ================================================================
print("\nRule 7: Addop")
s7 = [
    {"id": 0, "name": "q0",    "x": 80,  "y": 230, "initial": True},
    {"id": 1, "name": "PLUS",  "x": 380, "y": 80,  "final": True},
    {"id": 2, "name": "MINUS", "x": 380, "y": 230, "final": True},
    {"id": 3, "name": "q3",    "x": 300, "y": 400},
    {"id": 4, "name": "OR",    "x": 530, "y": 400, "final": True},
]
t7 = [
    {"from": 0, "to": 1, "read": "+"},
    {"from": 0, "to": 2, "read": "-"},
    {"from": 0, "to": 3, "read": "o"},
    {"from": 3, "to": 4, "read": "r"},
]
make_jff(s7, t7, "rule7_addop.jff",
         "Rule 7: Addop NFA  +  -  or")

# ================================================================
# RULE 8 : Multiplication Operators  (mulop)
# *   /   div   mod   and
#
# q0 --*--> q1(accept)
# q0 --/--> q2(accept)
# q0 --d--> q3 --i--> q4 --v--> q5(accept)   DIV
# q0 --m--> q6 --o--> q7 --d--> q8(accept)   MOD
# q0 --a--> q9 --n--> q10 --d--> q11(accept) AND
# ================================================================
print("\nRule 8: Mulop")
s8 = [
    {"id": 0,  "name": "q0",    "x": 50,  "y": 300, "initial": True},
    {"id": 1,  "name": "STAR",  "x": 300, "y": 50,  "final": True},
    {"id": 2,  "name": "SLASH", "x": 300, "y": 150, "final": True},
    {"id": 3,  "name": "q3",    "x": 250, "y": 270},
    {"id": 4,  "name": "q4",    "x": 430, "y": 270},
    {"id": 5,  "name": "DIV",   "x": 620, "y": 270, "final": True},
    {"id": 6,  "name": "q6",    "x": 250, "y": 390},
    {"id": 7,  "name": "q7",    "x": 430, "y": 390},
    {"id": 8,  "name": "MOD",   "x": 620, "y": 390, "final": True},
    {"id": 9,  "name": "q9",    "x": 250, "y": 510},
    {"id": 10, "name": "q10",   "x": 430, "y": 510},
    {"id": 11, "name": "AND",   "x": 620, "y": 510, "final": True},
]
t8 = [
    {"from": 0, "to": 1,  "read": "*"},
    {"from": 0, "to": 2,  "read": "/"},
    {"from": 0, "to": 3,  "read": "d"},
    {"from": 3, "to": 4,  "read": "i"},
    {"from": 4, "to": 5,  "read": "v"},
    {"from": 0, "to": 6,  "read": "m"},
    {"from": 6, "to": 7,  "read": "o"},
    {"from": 7, "to": 8,  "read": "d"},
    {"from": 0, "to": 9,  "read": "a"},
    {"from": 9, "to": 10, "read": "n"},
    {"from": 10,"to": 11, "read": "d"},
]
make_jff(s8, t8, "rule8_mulop.jff",
         "Rule 8: Mulop NFA  *  /  div  mod  and")

# ================================================================
# RULE 9 : Assignment Operator  (assignop)
# Lexeme:  :=
#
# q0 --:--> q1 --=--> q2 (accept)
# ================================================================
print("\nRule 9: Assignop")
s9 = [
    {"id": 0, "name": "q0",     "x": 100, "y": 200, "initial": True},
    {"id": 1, "name": "q1",     "x": 380, "y": 200},
    {"id": 2, "name": "ASSIGN", "x": 660, "y": 200, "final": True},
]
t9 = [
    {"from": 0, "to": 1, "read": ":"},
    {"from": 1, "to": 2, "read": "="},
]
make_jff(s9, t9, "rule9_assignop.jff",
         "Rule 9: Assignop NFA  :=")

print("\n" + "=" * 60)
print("All 9 NFA JFLAP files generated successfully!")
print(f"Output directory: {OUTPUT_DIR}")
print("=" * 60)
print("\nOpen any .jff file in JFLAP 7.1 to see the NFA diagram.")
print("Symbolic labels: 'letter' = [a-zA-Z], 'digit' = [0-9],"
      " 'blank' = space, 'other' = any non-{ char")
