
 # Backtracking Parser and Operator Precedence Parser

## Run

```
python gui.py
```

Requires Python 3 with Tkinter (included with most Python installations).

## Usage

1. Enter a grammar (format: `A -> x y | z`)
2. Click "Load Grammar"
3. Enter an input string
4. Click a parser button
5. Click "Next Step" to step through

## Grammar Format

- Non-terminals: uppercase (e.g., `S`, `A`, `E`)
- Terminals: lowercase (e.g., `a`, `id`, `+`)
- Alternatives: separated by `|`
- Epsilon: `ε` or `epsilon`

Example:
```
S -> a A b
A -> c | d
```





