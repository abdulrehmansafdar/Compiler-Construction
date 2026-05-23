"""Hash-based symbol table manager for Pascal CFG labs.

Implements:
- insert, lookup, lookup_current, delete (Task 1)
- begin_scope, end_scope with nested scope stack (Task 2)
- pretty tabular printing for debugging (Task 4)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

TABLE_SIZE = 211


@dataclass
class SymbolEntry:
    entry_id: int
    name: str
    kind: str
    type_name: str
    scope_level: int
    line: int
    next: Optional["SymbolEntry"] = None


class ScopeTable:
    def __init__(self, scope_level: int, parent: Optional["ScopeTable"]) -> None:
        self.scope_level = scope_level
        self.parent = parent
        self.slots: List[Optional[SymbolEntry]] = [None] * TABLE_SIZE
        self.entries_in_order: List[SymbolEntry] = []


class SymbolTableManager:
    def __init__(self) -> None:
        self.current_scope: Optional[ScopeTable] = None
        self.next_entry_id: int = 1

    @staticmethod
    def _hash(name: str) -> int:
        """djb2 hash function for identifier strings."""
        h = 5381
        for ch in name:
            h = ((h << 5) + h) + ord(ch)
        return h % TABLE_SIZE

    def begin_scope(self) -> ScopeTable:
        level = 0 if self.current_scope is None else self.current_scope.scope_level + 1
        new_scope = ScopeTable(scope_level=level, parent=self.current_scope)
        self.current_scope = new_scope
        return new_scope

    def end_scope(self) -> Optional[ScopeTable]:
        if self.current_scope is None:
            raise RuntimeError("No active scope to end")
        self.print_scope(self.current_scope)
        self.current_scope = self.current_scope.parent
        return self.current_scope

    def lookup_current(self, name: str) -> Optional[SymbolEntry]:
        if self.current_scope is None:
            return None
        bucket = self._hash(name)
        node = self.current_scope.slots[bucket]
        while node is not None:
            if node.name == name:
                return node
            node = node.next
        return None

    def lookup(self, name: str) -> Optional[SymbolEntry]:
        scope = self.current_scope
        bucket = self._hash(name)
        while scope is not None:
            node = scope.slots[bucket]
            while node is not None:
                if node.name == name:
                    return node
                node = node.next
            scope = scope.parent
        return None

    def insert(self, name: str, kind: str, type_name: str, line: int) -> Optional[SymbolEntry]:
        if self.current_scope is None:
            raise RuntimeError("No active scope. Call begin_scope first.")

        if self.lookup_current(name) is not None:
            return None

        bucket = self._hash(name)
        entry = SymbolEntry(
            entry_id=self.next_entry_id,
            name=name,
            kind=kind,
            type_name=type_name,
            scope_level=self.current_scope.scope_level,
            line=line,
            next=self.current_scope.slots[bucket],
        )
        self.current_scope.slots[bucket] = entry
        self.current_scope.entries_in_order.append(entry)
        self.next_entry_id += 1
        return entry

    def delete(self, name: str) -> bool:
        """Delete only from current scope."""
        if self.current_scope is None:
            return False

        bucket = self._hash(name)
        prev: Optional[SymbolEntry] = None
        node = self.current_scope.slots[bucket]

        while node is not None:
            if node.name == name:
                if prev is None:
                    self.current_scope.slots[bucket] = node.next
                else:
                    prev.next = node.next
                self.current_scope.entries_in_order = [
                    e for e in self.current_scope.entries_in_order if e.entry_id != node.entry_id
                ]
                return True
            prev = node
            node = node.next
        return False

    def update_in_parent_scope(self, name: str, **attrs) -> bool:
        """Update the first matching entry in the immediate parent scope."""
        if self.current_scope is None or self.current_scope.parent is None:
            return False

        scope = self.current_scope.parent
        bucket = self._hash(name)
        node = scope.slots[bucket]
        while node is not None:
            if node.name == name:
                for key, value in attrs.items():
                    if hasattr(node, key):
                        setattr(node, key, value)
                return True
            node = node.next
        return False

    @staticmethod
    def _compute_widths(rows: List[Tuple[str, str, str, str, str, str]]) -> Dict[str, int]:
        headers = ("ID", "Name", "Kind", "Type", "Scope", "Line")
        widths = {
            "ID": len(headers[0]),
            "Name": len(headers[1]),
            "Kind": len(headers[2]),
            "Type": len(headers[3]),
            "Scope": len(headers[4]),
            "Line": len(headers[5]),
        }
        for row in rows:
            widths["ID"] = max(widths["ID"], len(row[0]))
            widths["Name"] = max(widths["Name"], len(row[1]))
            widths["Kind"] = max(widths["Kind"], len(row[2]))
            widths["Type"] = max(widths["Type"], len(row[3]))
            widths["Scope"] = max(widths["Scope"], len(row[4]))
            widths["Line"] = max(widths["Line"], len(row[5]))
        return widths

    def print_scope(self, scope: ScopeTable) -> None:
        rows = [
            (
                str(e.entry_id),
                e.name,
                e.kind,
                e.type_name,
                str(e.scope_level),
                str(e.line),
            )
            for e in scope.entries_in_order
        ]

        print(f"[Scope {scope.scope_level}] Exit, dump:")
        if not rows:
            print("(empty)")
            return

        widths = self._compute_widths(rows)

        sep = (
            "+-" + "-" * widths["ID"] + "-+-"
            + "-" * widths["Name"] + "-+-"
            + "-" * widths["Kind"] + "-+-"
            + "-" * widths["Type"] + "-+-"
            + "-" * widths["Scope"] + "-+-"
            + "-" * widths["Line"] + "-+"
        )

        def format_row(values: Tuple[str, str, str, str, str, str]) -> str:
            return (
                "| "
                + values[0].ljust(widths["ID"]) + " | "
                + values[1].ljust(widths["Name"]) + " | "
                + values[2].ljust(widths["Kind"]) + " | "
                + values[3].ljust(widths["Type"]) + " | "
                + values[4].ljust(widths["Scope"]) + " | "
                + values[5].ljust(widths["Line"]) + " |"
            )

        print(sep)
        print(format_row(("ID", "Name", "Kind", "Type", "Scope", "Line")))
        print(sep)
        for row in rows:
            print(format_row(row))
        print(sep)

    def print_all_active_scopes(self) -> None:
        scope = self.current_scope
        while scope is not None:
            self.print_scope(scope)
            scope = scope.parent
