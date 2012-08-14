# ~/.profile: executed by Bourne-compatible login shells.

if [ "$BASH" ]; then
  if [ -f ~/.bashrc ]; then
    . ~/.bashrc
  fi
fi

mesg n

alias ll='ls -al'
alias l=ll

PS1='\u@\W\$ '
export LANG="zh_CN.UTF-8"
