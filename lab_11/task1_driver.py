"""Task 1 driver: single-scope hash table operations.

Required by lab manual:
- at least 10 inserts
- 5 lookups (including misses)
- 3 deletes
"""

from symbol_table import SymbolTableManager


def main() -> None:
    sm = SymbolTableManager()
    sm.begin_scope()

    inserts = [
        ("x", "variable", "integer", 1),
        ("y", "variable", "integer", 1),
        ("z", "variable", "real", 2),
        ("sum", "function", "integer", 3),
        ("avg", "function", "real", 4),
        ("count", "variable", "integer", 5),
        ("temp", "variable", "real", 6),
        ("flag", "variable", "boolean", 7),
        ("arr", "array", "integer[]", 8),
        ("i", "variable", "integer", 9),
    ]

    print("=== INSERT TESTS (10) ===")
    for name, kind, type_name, line in inserts:
        result = sm.insert(name, kind, type_name, line)
        print(f"insert({name}) -> {'OK' if result else 'DUPLICATE'}")

    print("\n=== LOOKUP TESTS (5, with misses) ===")
    for name in ["x", "avg", "arr", "unknown", "missing"]:
        found = sm.lookup(name)
        if found:
            print(f"lookup({name}) -> FOUND (scope={found.scope_level}, type={found.type_name})")
        else:
            print(f"lookup({name}) -> NOT FOUND")

    print("\n=== DELETE TESTS (3) ===")
    for name in ["temp", "flag", "ghost"]:
        deleted = sm.delete(name)
        print(f"delete({name}) -> {'DELETED' if deleted else 'NOT FOUND'}")

    print("\n=== FINAL SCOPE DUMP ===")
    sm.end_scope()


if __name__ == "__main__":
    main()
