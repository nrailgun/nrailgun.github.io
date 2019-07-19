
## Materials

- *Programming in Lua*, 2nd edition.
- Lua 5.3 manual
- Lua 5.4 source code


## Possible pitfalls

1. extra return values are discarded.
2. parameters are filled with nil if not provided.
3. if `<=` is not provided, lua uses`<`.
4. undefined variable as nil (metamethods help us out). 
5. lua converts variables silently.
6. `0` is treated as `true`.
7. function calls fill return values only as the last parameter of expression. the same for return statement.
8. tail calls won't exceed the stack.
9. `a <= b` is converted to `b > a`. that's error prone if order is partial.
11. lua interact with c by manipulating stack, which reminds me how to call functions in asm. hardcore.
12. lua interpreter is actually ***not** so ANSI C*. It uses some gnu extensions.


## Interpreter

### lua_newstate

`lua_newstate`:
- set fields 0
- `luaD_rawrunprotected` run in protected mode
    - `f_luaopen`
        - `stack_init`: alloc stack, set top.
        - `init_registry`
        - `luaS_init`
        - `luaT_init`
        - `luaX_init`
        - `g->gcrunning = 1`
        - `setnilvalue`

### lua_pop

`lua_pop` is a alias of `lua_settop`, which subtracts stack pointer.

### lua_pushnumber

`lua_pushnumber`:

- `setfltvalue`: `L->top(StkId) -> val(TValue) -> value_(Value) -> n(lua_number/double)`
- `lua_incr_top`

### luaL_requiref

`luaL_requiref`:
- `lua_getsubtable` if `REGISTY['__LOADED']` not loaded, create empty table.
- `lua_getfield` check if module name is in `REGISTY['__LOADED']`.
    - if not, load it.
- remove loaded from stack.
- `lua_setglobal` register to global.

`lua_getfield`:
- `lua_lock`
- `index2value`
    - check idx range
    - index stack
    - s2v (`StackValue` to `TValue`)
- `auxgetstr`
    - `luaS_new`
        - check cache (a little dumb)
        - `luaS_newlstr`
    - `luaV_fastget` (without check metatable)
        - `luaH_gestr`
            - short string `luaH_getshortstr` iter hash table.
            - long string `getgeneric`
        - `setobj2s` copy `TValue`
        - `api_incr_top` top + 1
    - `luaV_finishget` (check metatable)
    - `lua_unlock`
    - `ttype` to type code

`lua_setglobal`:
- `lua_state` -> `global_state` -> `l_registry` -> `hvalue` -> `Table`
- `luaH_getint(reg, LUA_RID_GLOBALS)`
- `auxsetstr`

### lua_pcall

`luaD_pcall`:
- `luaD_rawrunprotected` protected
- `f_call(L, CallS)`
    - `luaD_callnoyield`
        - `incXCcalls` disallow yield
        - `luaDCall`
            - check `ttypetag`, c or lua?
            - if c, f(L).
            - else (lua), `luaV_execute`.
        - `decXCcalls` allow yield

luaV_execute main loop:
- fetch an instruction
- switch instruction code

lua switch opcode and jump among `vmcase`. Label pointer (*&&LABEL*) is GNU extension, and is not part of ansi C.


## Vim

Vim doesn't treat `class:function` as a whole key word as ctags does, which make us unable to locate symbol by pressing `<C-]>`. To enable tag searching, add following lines to `.vimrc`.

```vim
augroup filetype_lua
        autocmd!
        autocmd FileType lua setlocal iskeyword+=:
augroup END
```
