# Refactoring ideas

## Refactorings to try:
 - extract variable (extract a complex expression into a variable)
 - extract methods/functions (extracting a block of code into a new funtion)
 - changing the signature of a method/function (adding and removing parameters)
 - inline a method/function (replace calls with definition)
 - introducing constants
 - encapsulation field (introducing getters and setters for attributes)
 - promoting local variable to funtion parameters
 - extracting superclass/interface from existing classes
 - sorting imports

## Refactoring tools to try:
 - IDE's built in tools, `RedBaron`, `Bowler`, `Rope`, maybe `Coala`
 - Python fixers like `2to3`, `modernize`, `futurize` or `fissix`
 - `PyUpgrade`
 - Code formatters like `autopep8` or `black`

## Storing data
 - `MongodDb` for storing different refactorings to a given source file and converting to csv files