# Ideas

## Equivalence

### Arithmetic

- [ ] `+` and `*` are commutative (for number constants)

### Logic

- [x] `(not not a)` is `(a)`
- [x] De Morgan's law

### Rename

- [ ] a variable, function or class can be renamed to a **new** name
- [ ] a **new** alias can be introduced for any import

### Trivial

- [ ] a `pass` can be introduced at the end of any `def`
- [ ] a `continue` can be introduced at the end of any `for`

### Other

- [ ] `try: open(...) excep: ...` to `with open(...)`
- [ ] code obfuscation
- [ ] shuffle kwargs

## Implementation ideas

- Create smaller 'sub-patterns' for more complex transformations (i.e.: for transformations)
- Make rules "bidirectional"
- CFGs
- Rules may be easier to implement like this:
  - matcher:
    - function that matches and *deconstructs* a node
    - returns the nodes components or `None` if it isn't a match
  - changer:
    - function that creates the change based on a matched node
    - returns a change object or `None` if no changes are possible
