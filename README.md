# Parsing Visualizer

Interactive GUI for visualizing **Backtracking** and **Operator Precedence** parsers with step-by-step execution and visual feedback.

## Quick Start

```bash
python gui.py
```

## Features

- **Backtracking Parser**: Top-down parsing with visual parse tree
- **Operator Precedence Parser**: Bottom-up parsing with step table
- **Step-by-step execution**: See each parsing decision
- **Error detection**: Left recursion, precedence conflicts, depth limits
- **Visual feedback**: Color-coded trees and tables

## Grammar Format

```
S -> a A b
A -> c | d
```

- Non-terminals: Uppercase (`S`, `A`, `E`)
- Terminals: Lowercase (`a`, `id`, `+`)
- Alternatives: Use `|`
- Epsilon: `ε` or `epsilon`

## Test Examples

### Backtracking Parser

```
┌────┬─────────────────────────────────────────┬──────────────┬──────────────────────┐
│ #  │ Grammar                                 │ Input        │ Result               │
├────┼─────────────────────────────────────────┼──────────────┼──────────────────────┤
│ 1  │ S -> a A b                              │ a c b        │ ✓ Accept             |
│    │ A -> c | d                              │              │                      │
├────┼─────────────────────────────────────────┼──────────────┼──────────────────────┤
│ 2  │ S -> A B                                │ b            │ ✓ Accept             │
│    │ A -> a | ε                              │              │                      │
│    │ B -> b                                  │              │                      │
├────┼─────────────────────────────────────────┼──────────────┼──────────────────────┤
│ 3  │ S -> a S b | ε                          │ a a b b      │ ✓ Accept             │
├────┼─────────────────────────────────────────┼──────────────┼──────────────────────┤
│ 4  │ S -> A B                                │ a a a b      │ ✓ Accept             │
│    │ A -> a A | a                            │              │                      │
│    │ B -> b                                  │              │                      │
├────┼─────────────────────────────────────────┼──────────────┼──────────────────────┤
│ 5  │ S -> S a | b                            │ b a          │ ✗ Left Recursion     │
├────┼─────────────────────────────────────────┼──────────────┼──────────────────────┤
│ 6  │ S -> a                                  │ b            │ ✗ Reject             │
├────┼─────────────────────────────────────────┼──────────────┼──────────────────────┤
│ 7  │ S -> a b c                              │ a b          │ ✗ Reject             │
├────┼─────────────────────────────────────────┼──────────────┼──────────────────────┤
│ 8  │ S -> A B C                              │ a b c        │ ✓ Accept             │
│    │ A -> a                                  │              │                      │
│    │ B -> b                                  │              │                      │
│    │ C -> c                                  │              │                      │
└────┴─────────────────────────────────────────┴──────────────┴──────────────────────┘
```

### Operator Precedence Parser

```
┌────┬─────────────────────────────────────────┬──────────────────────┬──────────────────────┐
│ #  │ Grammar                                 │ Input                │ Result               │
├────┼─────────────────────────────────────────┼──────────────────────┼──────────────────────┤
│ 9  │ E -> E + T | T                          │ id + id * id         │ ✓ Accept             │
│    │ T -> T * F | F                          │                      │                      │
│    │ F -> ( E ) | id                         │                      │                      │
├────┼─────────────────────────────────────────┼──────────────────────┼──────────────────────┤
│ 10 │ E -> E + T | T                          │ ( ( ( id + id ) ) )  │ ✓ Accept             │
│    │ T -> T * F | F                          │                      │                      │
│    │ F -> ( E ) | id                         │                      │                      │
├────┼─────────────────────────────────────────┼──────────────────────┼──────────────────────┤
│ 11 │ E -> E + E | id                         │ id + id + id         │ ✓ Accept             │
├────┼─────────────────────────────────────────┼──────────────────────┼──────────────────────┤
│ 12 │ E -> E * E | E + E | id                 │ id + id * id         │ ✓ Accept             │
├────┼─────────────────────────────────────────┼──────────────────────┼──────────────────────┤
│ 13 │ S -> ( S ) | a                          │ ( ( a ) )            │ ✓ Accept             │
├────┼─────────────────────────────────────────┼──────────────────────┼──────────────────────┤
│ 14 │ E -> E + T | T                          │ id + id              │ ✓ Accept             │
│    │ T -> id                                 │                      │                      │
├────┼─────────────────────────────────────────┼──────────────────────┼──────────────────────┤
│ 15 │ S -> A B                                │ a b                  │ ✗ Adjacent           │
│    │ A -> a                                  │                      │   Non-terminals      │
│    │ B -> b                                  │                      │                      │
├────┼─────────────────────────────────────────┼──────────────────────┼──────────────────────┤
│ 16 │ S -> a | ε                              │ a                    │ ✗ Epsilon            │
│    │                                         │                      │   Not Allowed        │
└────┴─────────────────────────────────────────┴──────────────────────┴──────────────────────┘
```

## Usage

1. Enter grammar in text box
2. Click "Load Grammar"
3. Enter input string
4. Select parser type
5. Click "Next Step" to visualize parsing

## Project Structure

```
├── gui.py                          # Main GUI application
├── parsing_core.py                 # Core classes (Grammar, Production, TreeNode)
├── backtracking_parser.py          # Backtracking parser implementation
├── operator_precedence_parser.py   # Operator precedence parser
├── precedence_table.py             # Precedence table builder
└── tests_and_more/                 # Test files and documentation
```





