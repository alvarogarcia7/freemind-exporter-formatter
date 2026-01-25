# Shell Completions for main.py

This project includes bash and zsh shell completion scripts for `main.py`.

## Generating Completions

### Automatic Generation (Recommended)

To generate or regenerate the completion scripts, run:

```bash
make completions
```

Or directly:

```bash
python generate_completions.py
```

This generates:
- `main.bash` - Bash completion script
- `main.zsh` - Zsh completion script

## Installation

### Bash

Add this to your `~/.bashrc` or `~/.bash_profile`:

```bash
source /path/to/project/main.bash
```

Then reload your shell:

```bash
source ~/.bashrc
```

### Zsh

Add this to your `~/.zshrc`:

```bash
source /path/to/project/main.zsh
```

Or, for a more permanent installation, copy the script to your zsh completions directory:

```bash
mkdir -p ~/.zsh/completions
cp main.zsh ~/.zsh/completions/_main
```

Then add to `~/.zshrc`:

```bash
fpath=(~/.zsh/completions $fpath)
autoload -U compinit && compinit
```

Then reload your shell:

```bash
source ~/.zshrc
```

## Usage

Once installed, TAB completion works for:

- **Option names**: Type `main.py --<TAB>` to see available options
- **`--input`**: Type `main.py --input <TAB>` to complete filenames
- **`--formatter`**: Type `main.py --formatter <TAB>` to complete available formatter modules
- **`--output`**: Type `main.py --output <TAB>` to complete filenames

### Example

```bash
$ python main.py --<TAB>
--formatter  --help     --input    --output

$ python main.py --formatter <TAB>
json_formatter       orgmode            titles
```

## How It Works

The `generate_completions.py` script:

1. Defines the command-line arguments from `main.py`
2. Generates bash and zsh completion scripts with TAB completion support
3. Handles file/directory completion for file arguments
4. Lists available formatter modules for the `--formatter` option

If you modify `main.py`'s command-line arguments, simply run `make completions` again to update the completion scripts.
