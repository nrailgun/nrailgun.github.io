在写入操作时会触发 `BackgroundCompaction()`，如果 `imm_ != NULL` 会触发 `CompactMemTable()`，否则会 `PickCompaction` 再去做。

---

`CompactMemTable()` 除了操作 version set，主要是调用 `WriteLevel0Table()`，再通过 `BuildTable()` 去创建 ldb 文件。逻辑比较直观，遍历，统计 min / max，写入。

此时，一个 `MemTable`（`Skiplist`）成为一个单独的 ldb 文件。

---

`PickCompaction` 会选一个最需要 compact 的 level，这个是在 `Version::Finalize(version)` 的时候根据 size 定下来的（`Version::compaction_level_`）。然后 *pick the first file that comes after compact_pointer_[level]*，否则 pick 第一个。

`compact_pointer_[level]` 是在 ` SetupOtherInputs` 中设置的。

---

如果一个 compact 不是 trivial 的，那么 `DBImpl::DoCompactionWork`。

- x

