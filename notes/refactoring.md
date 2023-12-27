# Refactoring ideas

## Refactorings to implement

- extract variable (extract a complex expression into a variable)
- extract methods/functions (extracting a block of code into a new funtion)
- inline a method/function (replace calls with definition)
- introducing getters and setters for attributes
- extracting superclass/interface from existing classes
- swapping lines if it produces equivalent code

## Refactoring tools to try

- IDE's built in tools
- `Bowler`, `Rope`, maybe `Coala`
- Python fixers like `modernize`
- `PyUpgrade`
- Code formatters like `autopep8` or `black`
- Python IDE `PyCharm` (it supports auto refactoring)

## Storing data

- `MongodDb` for storing different refactorings to a given source file and converting to `.csv` files

## Inequivalent code

- data for non equivalent code pairs may also be provided
