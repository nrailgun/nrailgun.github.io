有时候需要在多个窗口打开不同程序观察日志输出（比如C/S），窗体跳转非常不方便。我发现了一个简单的技巧。

```Makefile
.PHONY: all p c cls k

all: cls
        #tmux send-keys -t 1 './LogCabin --config logcabin-1.conf --bootstrap' C-m
        tmux send-keys -t 1 './LogCabin --config logcabin-1.conf' C-m
        tmux send-keys -t 2 './LogCabin --config logcabin-2.conf' C-m
        tmux send-keys -t 3 './LogCabin --config logcabin-3.conf' C-m

p:
        tmux split -vd -p 50
        tmux split -hd -p 50
        tmux select-pane -t 2
        tmux split -hd -p 50
        tmux select-pane -t 0

c:
        tmux send-keys -t 1 C-c
        tmux send-keys -t 2 C-c
        tmux send-keys -t 3 C-c

cls: c
        tmux send-keys -t 1 'clear' C-m
        tmux send-keys -t 2 'clear' C-m
        tmux send-keys -t 3 'clear' C-m

k:
        tmux kill-pane -t 3
        tmux kill-pane -t 2
        tmux kill-pane -t 1
```

另外一个非常好用的技巧就是可以用 `<Prefix>,q,{PANE_NUM}` 来切换 pane，或者改一下 `~/.tmux.conf`。

```bash
set -g default-shell /bin/zsh
set -g default-terminal "xterm-256color"
set -g status-keys vi
set -g history-limit 32768
setw -g mode-keys vi

unbind C-b
set -g prefix C-a
bind C-a send-prefix

bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

unbind %
unbind '"'
bind | splitw -h
bind - splitw -v

bind 0 select-pane -t 0
bind 1 select-pane -t 1
bind 2 select-pane -t 2
bind 3 select-pane -t 3
bind 4 select-pane -t 4
bind 5 select-pane -t 5
bind 6 select-pane -t 6
bind 7 select-pane -t 7
bind 8 select-pane -t 8
bind 9 select-pane -t 9
```