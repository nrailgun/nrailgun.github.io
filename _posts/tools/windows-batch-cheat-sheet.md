基本语法

```bat
:: command-line args
@echo off
echo %1
echo %2
echo %3

:: variables
setlocal
set msg=lorem ipsum
echo %msg%
endlocal

:: numeric
set /a a = 1
set /a b = 1
set /a c = %a% + %b%
```

后台运行

```bat
@echo off
call "cmd /c start /b kubectl port-forward beta-0 6003:6003"
call "cmd /c start /b kubectl port-forward beta-1 6013:6013"
pause
```

忽略大小写

```bash
echo 'set completion-ignore-case On' >> ~/.inputrc
```

