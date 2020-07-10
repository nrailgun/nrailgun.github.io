主要看几个基本函数：

- `co_create`
- `co_resume`
- `co_get_epoll_ct`
- `co_event_loop`
- `co_poll`

## `co_create`

- 如果 thread local var `stCoroutineEnv_t *gCoEnvPerThread` 没有初始化，调用 `co_init_cur_thread_env`。
  - alloc`env`.
  - `co_create_env` one `stCoroutine_t self`, fill its `ctx` with `0`s.
  - push `self` into `env->pCallStack`.
  - `stCoEpoll_t *ev = AllocEpoll()`
    - `ctx->iEpollFd = epoll_create()`
    - `ctx->pTimeout = new stTimeout_t`
  - `SetEpoll`: `env->ePoll = ev`

- return `co_create_env()`.

---

`co_create_env`

- malloc stack `stStackMem_t` with `co_alloc_stackmem()`,
- set `occupy_co` of stack mem to null,
- and assign to `stCoroutine_t.ctx.ss_sp`.

## `co_resume`

- `stCoroutineEnv *env = co->env`(`gCoEnvPerThread`)
- 取出`env->pCallStack` 顶部 `pcr`
- if `!co->cStart`
  - `coctx_make(&co->ctx, CoRoutineFunc, co, 0)`
  - `co->cStart = 1`
- push `co` into `env->pCallStack`
- `co_swap(pcr, co)`

---

`coctx_make`

- copy addr of `pfn` function to the top of stack,
- copy parameters to `ctx->regs`.

---

`co_swap`

- save cur stack sp to `curr->stack_sp`.
- `env->pending_co = pending_co`
- 把 `pending_co->stack_mem` 的 `occupy_co` 设置成新的 `pending_co`。
- 把旧的 `occupy_co` 存在 `env->occupy_co` 上。
- 如果就 `occupy_co != nullptr && occupy_co != pending_co`
  - `save_stack_buffer`
- `coctx_swap` 是汇编写的，把 `coctx_t` 里的寄存器数据 load 上去（`esp` / `bbp`）。
- ...

注意，由于 `coctx_swap` 切的 `ebp` 指针，这会导致在 `ret` 的时候，取出来刚刚 load 上去的栈上的 `eip` 寄存器，间接实现了代码跳跃。

显然，由于 `eip` 发生了切换，函数下面部分是暂时不会执行的，而会去执行 coroutine 函数。如果过程中不发生 yield，就会一直执行（这符合我们的一般认知，没有问题）。

## `co_event_loop`

`co_get_epoll_ct` 比较简单，从 `co_get_cur_thread_env()` 中取出 `eEpoll`。

