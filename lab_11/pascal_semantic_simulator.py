"""Pascal-CFG-oriented semantic simulation using SymbolTableManager.

This driver is intentionally simple and evaluation-friendly:
- It tokenizes tiny Pascal-like examples into line-wise events.
- It triggers symbol-table operations at CFG-relevant points.
- It demonstrates duplicate declaration and undeclared-use detection.
"""

from dataclasses import dataclass
from typing import List, Optional

from symbol_table import SymbolTableManager


@dataclass
class Event:
    line: int
    action: str
    name: Optional[str] = None
    kind: Optional[str] = None
    type_name: Optional[str] = None


def parse_events(program_text: str) -> List[Event]:
    """Very small event extractor for demonstration test files.

    Supported patterns:
    - program <id>;
    - var <id>(, <id>)* : <type>;
    - begin / end
    - identifier use via assignment or expression mention
    """
    events: List[Event] = []
    lines = program_text.splitlines()

    for idx, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("{"):
            continue

        lowered = line.lower()
        if lowered.startswith("program "):
            name = line.split()[1].rstrip(";")
            events.append(Event(idx, "program_decl", name=name, kind="program", type_name="void"))
            continue

        if lowered == "begin":
            events.append(Event(idx, "begin_block"))
            continue

        if lowered == "end" or lowered == "end;":
            events.append(Event(idx, "end_block"))
            continue

        if lowered.startswith("var "):
            # Example: var x, y : integer;
            body = line[4:].rstrip(";")
            if ":" not in body:
                continue
            left, right = body.split(":", 1)
            ids = [x.strip() for x in left.split(",") if x.strip()]
            type_name = right.strip().lower()
            for name in ids:
                events.append(Event(idx, "var_decl", name=name, kind="variable", type_name=type_name))
            continue

        if ":=" in line:
            lhs, rhs = line.split(":=", 1)
            lhs_name = lhs.strip().split()[0]
            if lhs_name.isidentifier():
                events.append(Event(idx, "identifier_use", name=lhs_name))

            rhs_tokens = [token.strip(";()+-*/,[] ") for token in rhs.replace("(", " ").replace(")", " ").split()]
            for token in rhs_tokens:
                if token.isidentifier() and token.lower() not in {"div", "mod", "and", "or", "not"}:
                    events.append(Event(idx, "identifier_use", name=token))
            continue

        # Procedure-like call: foo(x, y);
        if "(" in line and line.endswith(");"):
            callee = line.split("(", 1)[0].strip()
            if callee.isidentifier():
                events.append(Event(idx, "identifier_use", name=callee))
            args = line.split("(", 1)[1].rsplit(")", 1)[0]
            for token in [p.strip() for p in args.split(",")]:
                if token.isidentifier():
                    events.append(Event(idx, "identifier_use", name=token))

    return events


class SemanticRunner:
    def __init__(self) -> None:
        self.symtab = SymbolTableManager()
        self.errors: List[str] = []

    def run(self, events: List[Event]) -> None:
        self.symtab.begin_scope()
        print("[Scope 0] Enter")

        for ev in events:
            if ev.action == "program_decl":
                inserted = self.symtab.insert(ev.name or "", ev.kind or "program", ev.type_name or "void", ev.line)
                if inserted is None:
                    self.errors.append(f"ERROR line {ev.line}: duplicate declaration '{ev.name}'")
                else:
                    print(
                        f"[Scope {inserted.scope_level}] insert {inserted.name} : "
                        f"{inserted.kind}, {inserted.type_name}, line {inserted.line}"
                    )

            elif ev.action == "begin_block":
                new_scope = self.symtab.begin_scope()
                print(f"[Scope {new_scope.scope_level}] Enter")

            elif ev.action == "end_block":
                if self.symtab.current_scope is not None:
                    self.symtab.end_scope()

            elif ev.action == "var_decl":
                inserted = self.symtab.insert(ev.name or "", ev.kind or "variable", ev.type_name or "unknown", ev.line)
                if inserted is None:
                    self.errors.append(f"ERROR line {ev.line}: duplicate declaration '{ev.name}'")
                else:
                    print(
                        f"[Scope {inserted.scope_level}] insert {inserted.name} : "
                        f"{inserted.kind}, {inserted.type_name}, line {inserted.line}"
                    )

            elif ev.action == "identifier_use":
                found = self.symtab.lookup(ev.name or "")
                if found is None:
                    self.errors.append(f"ERROR line {ev.line}: undeclared variable '{ev.name}'")
                else:
                    active_level = self.symtab.current_scope.scope_level if self.symtab.current_scope else -1
                    print(f"[Scope {active_level}] lookup {ev.name} -> found at scope {found.scope_level}")

        while self.symtab.current_scope is not None:
            self.symtab.end_scope()

        if self.errors:
            for err in self.errors:
                print(err)
        else:
            print("Semantic checks passed with no declaration/use errors.")


def run_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        program_text = f.read()
    events = parse_events(program_text)
    runner = SemanticRunner()
    runner.run(events)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python lab_11/pascal_semantic_simulator.py <test_file>")
        print("Example: python lab_11/pascal_semantic_simulator.py lab_11/test_cases/valid_nested.pas")
        raise SystemExit(1)

    run_file(sys.argv[1])
