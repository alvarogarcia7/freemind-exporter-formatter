function source_if_exists(){
    local target
    target="$1"
    if [[ -f "${target}" ]]; then
        . "${target}"
    fi
}

[[ "" = "$VIRTUAL_ENV" ]] && source_if_exists "./venv/bin/activate"
[[ "" = "$VIRTUAL_ENV" ]] && source_if_exists "./.venv/bin/activate"
