_pros_completion() {
  local IFS=$'\n'
  local response
  response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _PROS_COMPLETE=bash_complete $1)
  for completion in $response; do
    IFS=',' read type value <<<"$completion"
    if [[ $type == 'dir' ]]; then
      COMPREPLY=()
      compopt -o dirnames
    elif [[ $type == 'file' ]]; then
      COMPREPLY=()
      compopt -o default
    elif [[ $type == 'plain' ]]; then
      COMPREPLY+=($value)
    fi
  done
  return 0
}
_pros_completion_setup() {
  if [[ ${BASH_VERSINFO[0]} -ge 4 ]]; then
    complete -o nosort -F _pros_completion pros
  else
    complete -F _pros_completion pros
  fi
}
_pros_completion_setup
