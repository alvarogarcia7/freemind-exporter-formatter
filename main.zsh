#compdef main.py

# zsh completion for main.py

_main_py() {
    local curcontext="$curcontext" state line
    typeset -A opt_args

    _arguments -s \
        '--input[Input mindmap file]:input file:_files' \
        '--formatter[Formatter module to use]:formatter:($(ls -1 *.py 2>/dev/null | sed "s/\.py$//" | grep -v main | grep -v main_wrapper))' \
        '--output[Output file (default\: stdout)]:output file:_files' \
        '--help[Show help message]'
}

_main_py "$@"
