# bash completion for main.py
# Source this file to enable completions

_main_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Available options
    opts="--input --formatter --output --help"

    # If the previous word is an option that takes a value, provide file completion
    case "${prev}" in
        --input)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --formatter)
            # List available formatter modules (Python files)
            COMPREPLY=( $(compgen -W "$(ls -1 *.py 2>/dev/null | sed 's/\.py$//' | grep -v main | grep -v main_wrapper)" -- ${cur}) )
            return 0
            ;;
        --output)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
    esac

    # Complete option names
    if [[ ${cur} == -* ]]; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}

complete -o bashdefault -o default -o nospace -F _main_completions main.py
complete -o bashdefault -o default -o nospace -F _main_completions python main.py
