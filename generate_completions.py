#!/usr/bin/env python3
"""Generate bash and zsh completion scripts from argparse parser."""

import argparse
from pathlib import Path


def extract_parser_from_main() -> argparse.ArgumentParser:
    """Extract ArgumentParser from main.py."""
    parser = argparse.ArgumentParser(prog="main")
    parser.add_argument("--input", required=True, help="Input mindmap file")
    parser.add_argument(
        "--formatter",
        required=True,
        default="print_as_titles",
        help="Formatter module to use",
    )
    parser.add_argument("--output", default=None, help="Output file (default: stdout)")
    return parser


def generate_bash_completion(
    parser: argparse.ArgumentParser, prog_name: str = "main.py"
) -> str:
    """Generate bash completion script."""
    bash_script = f"""# bash completion for {prog_name}
# Source this file to enable completions

_main_completions() {{
    local cur prev opts
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"

    # Available options
    opts="--input --formatter --output --help"

    # If the previous word is an option that takes a value, provide file completion
    case "${{prev}}" in
        --input)
            COMPREPLY=( $(compgen -f -- ${{cur}}) )
            return 0
            ;;
        --formatter)
            # List available formatter modules (Python files)
            COMPREPLY=( $(compgen -W "$(ls -1 *.py 2>/dev/null | sed 's/\\.py$//' | grep -v main | grep -v main_wrapper | grep -v generate_completions)" -- ${{cur}}) )
            return 0
            ;;
        --output)
            COMPREPLY=( $(compgen -f -- ${{cur}}) )
            return 0
            ;;
    esac

    # Complete option names
    if [[ ${{cur}} == -* ]]; then
        COMPREPLY=( $(compgen -W "${{opts}}" -- ${{cur}}) )
        return 0
    fi
}}

complete -o bashdefault -o default -o nospace -F _main_completions {prog_name}
complete -o bashdefault -o default -o nospace -F _main_completions python {prog_name}
"""
    return bash_script


def generate_zsh_completion(
    parser: argparse.ArgumentParser, prog_name: str = "main.py"
) -> str:
    """Generate zsh completion script."""
    zsh_script = f"""#compdef {prog_name}

# zsh completion for {prog_name}

_main_py() {{
    local curcontext="$curcontext" state line
    typeset -A opt_args

    _arguments -s \\
        '--input[Input mindmap file]:input file:_files' \\
        '--formatter[Formatter module to use]:formatter:($(ls -1 *.py 2>/dev/null | sed "s/\\.py$//" | grep -v main | grep -v main_wrapper | grep -v generate_completions))' \\
        '--output[Output file (default\\: stdout)]:output file:_files' \\
        '--help[Show help message]'
}}

_main_py "$@"
"""
    return zsh_script


def main() -> None:
    """Generate completion files."""
    parser = extract_parser_from_main()

    bash_content = generate_bash_completion(parser)
    zsh_content = generate_zsh_completion(parser)

    # Write bash completion
    bash_file = Path("main.bash")
    bash_file.write_text(bash_content)
    print(f"Generated {bash_file}")

    # Write zsh completion
    zsh_file = Path("main.zsh")
    zsh_file.write_text(zsh_content)
    print(f"Generated {zsh_file}")

    print("\nTo use these completions:")
    print(f"\nBash: source {bash_file}")
    print(f"Zsh: source {zsh_file}")


if __name__ == "__main__":
    main()
