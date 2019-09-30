# In Search of an Understandable Consensus Algorithm

# LogCabin

## Hello

和 Etcd 类似，连接集群进行键值对读写。

```c++
// 连接集群
Cluster cluster(options.cluster);
Tree tree = cluster.getTree();

// 写 KV
tree.makeDirectoryEx("/etc");
tree.writeEx("/etc/passwd", "ha");

// 读 KV
std::string contents = tree.readEx("/etc/passwd");
assert(contents == "ha");
```

## LogCabin

`Global` 是初始化顺序受控的全局变量集合。其初始化过程包含：

- 初始化 RPC，以及3 个 RPC 服务：`controlService`、`raftService`，和 `ClientService`。分别转发集群成员操作，日志同步，和键值对操作，实现较为简单。

- 初始化 Raft 实例。
- 初始化 `StateMachine` 实例。

初始化后，LogCabin 开始 IO 复用循环，响应 RPC 请求。

## SegmentedLog

要理解 `RaftConsensus`，需要先理解 `SegmentedLog`。

```c++
SegmentedLog::SegmentedLog(const FS::File& parentDir,
                           Encoding encoding,
                           const Core::Config& config)
    // : ... 构造列表
{
    // 把目录下的 log segment 文件全部读出来
    std::vector<Segment> segments = readSegmentFilenames();

    // 读 metadata 文件
    SegmentedLogMetadata::Metadata metadata1;
    // ... 从 metadata1 和 metadata2 之间取一个可用的，简化一下代码。
    metadata = metadata1;

    // 写 metadata 文件
    logStartIndex = metadata.entries_start();
    Log::metadata = metadata.raft_metadata();
    updateMetadata();
    updateMetadata(); // 可靠存储。
    FS::fsync(dir);

    // 读 segment 文件，读出所有的 log entries。
    for (auto it = segments.begin(); it != segments.end(); ++it) {
        Segment& segment = *it;
        bool keep = segment.isOpen
            ? loadOpenSegment(segment, logStartIndex)
            : loadClosedSegment(segment, logStartIndex);
        if (keep) {
            // 这个 segment 文件应该保留。
            uint64_t startIndex = segment.startIndex;
            std::string filename = segment.filename;
            auto result = segmentsByStartIndex.insert(
                {startIndex, std::move(segment)});
        }
    }

    // 创建一个新的日志 segment 文件，`preparedSegments` 中存储了若干个 `OpenSegment`
    // （实质上是 std::pair<文件名, 文件>）。
    uint64_t fileId = preparedSegments.waitForDemand();
    preparedSegments.submitOpenSegment(prepareNewSegment(fileId));
    openNewSegment();

    // 开线程建 open segment。
    segmentPreparer = std::thread(&SegmentedLog::segmentPreparerMain, this);
}

// 在配置限制（默认为 3）下，尽可能创建 open segment 文件。
void SegmentedLog::segmentPreparerMain()
{
    while (true) {
        uint64_t fileId = 0;
        fileId = preparedSegments.waitForDemand();

        preparedSegments.submitOpenSegment(
            prepareNewSegment(fileId));
    }
}
```

构造函数比较复杂，读写反而比较简单。读写操作不会直接进行，而是提交到 `SegmentedLog::currentSync` 中，稍后通过 `RaftConsensus` 的线程取出后执行。

```c++
// 从 index 位置读 log，实现很显然了。
const SegmentedLog::Entry&
SegmentedLog::getEntry(uint64_t index) const
{
    auto it = segmentsByStartIndex.upper_bound(index);
    --it;
    const Segment& segment = it->second;
    return segment.entries.at(index - segment.startIndex).entry;
}

// 添加 log entries。
std::pair<uint64_t, uint64_t>
SegmentedLog::append(const std::vector<const Entry*>& entries)
{
    Segment* openSegment = &getOpenSegment();
    uint64_t startIndex = openSegment->endIndex + 1;
    uint64_t index = startIndex;
    
    // 逐个写入
    for (auto it = entries.begin(); it != entries.end(); ++it) {
        Segment::Record record(openSegment->bytes);
        record.entry = **it;
        if (!record.entry.has_index())
            record.entry.set_index(index);
        Core::Buffer buf = serializeProto(record.entry);

        // 如果行的 entry 比较大，那么建一个新的 segment 文件。
        if (openSegment->bytes > sizeof(SegmentHeader) &&
            openSegment->bytes + buf.getLength() > MAX_SEGMENT_SIZE) {

            // 关闭 open segment 文件。
            currentSync->ops.emplace_back(openSegmentFile.fd,
                                          Sync::Op::TRUNCATE);
            currentSync->ops.back().size = openSegment->bytes;
            currentSync->ops.emplace_back(openSegmentFile.fd,
                                          Sync::Op::FSYNC);
            currentSync->ops.emplace_back(openSegmentFile.release(),
                                          Sync::Op::CLOSE);

            // 重命名为 closed segment 文件。
            std::string newFilename = openSegment->makeClosedFilename();
            currentSync->ops.emplace_back(dir.fd, Sync::Op::RENAME);
            currentSync->ops.back().filename1 = openSegment->filename;
            currentSync->ops.back().filename2 = newFilename;
            currentSync->ops.emplace_back(dir.fd, Sync::Op::FSYNC);
            openSegment->filename = newFilename;

            openSegment->isOpen = false;
            totalClosedSegmentBytes += openSegment->bytes;

            // 新 open segment。
            openNewSegment();
            openSegment = &getOpenSegment();
            record.offset = openSegment->bytes;
        }

        // 将 log entry 加入 open segment。
        openSegment->entries.emplace_back(std::move(record));
        openSegment->bytes += buf.getLength();
        currentSync->ops.emplace_back(openSegmentFile.fd, Sync::Op::WRITE);
        currentSync->ops.back().writeData = std::move(buf);
        ++openSegment->endIndex;
        ++index;
    }

    // 冲刷到硬盘。
    currentSync->ops.emplace_back(openSegmentFile.fd, Sync::Op::FDATASYNC);
    currentSync->lastIndex = getLastLogIndex();
    return {startIndex, getLastLogIndex()};
}
```

## Membership Changes

最初集群中只有一个节点，管理员通过 `ClientImpl` 发起请求 `SetConfiguration`，要求为集群增加（改变）成员。`ClientImpl` 包含了一个 `LeaderRPC` 用于与集群 Leader 通信，`SetConfiguration`  的请求通过 `LeaderRPC` 送出（***TODO*** 如何确保通信对象为 Leader，如果过程中突然失去 leadership 会如何？）。

```c++
ConfigurationResult
ClientImpl::setConfiguration(uint64_t oldId,
                             const Configuration& newConfiguration,
                             TimePoint timeout)
{
    // RPC 参数
    Protocol::Client::SetConfiguration::Request request;
    request.set_old_id(oldId);
    for (auto it = newConfiguration.begin(); it != newConfiguration.end(); ++it) {
        // 新成员编号与地址
        Protocol::Client::Server* s = request.add_new_servers();
        s->set_server_id(it->serverId);
        s->set_addresses(it->addresses);
    }
    Protocol::Client::SetConfiguration::Response response;
    
    // RPC 请求
    typedef LeaderRPCBase::Status RPCStatus;
    RPCStatus status = leaderRPC->call(
        OpCode::SET_CONFIGURATION, request, response, timeout);
    
    // ... 取出 RPC 响应
}
```

服务器的响应全部委托给 Raft 实现 `RaftConsensus`。

```c++
void ClientService::setConfiguration(RPC::ServerRPC rpc)
{
    PRELUDE(SetConfiguration);
    
    Result result = globals.raft->setConfiguration(request, response);
    if (result == Result::RETRY || result == Result::NOT_LEADER) {
        // ... 错误提示
    }
    rpc.reply(response);
}
```

`RaftConsensus` 的初始化如下，依赖于 `SegmentedLog`。

```c++
RaftConsensus::init()
{
    std::lock_guard<Mutex> lockGuard(mutex);

	// 创建存储文件夹 lock / log / snapshot。
    storageLayout.init(globals.config, serverId);

    // 表征所知集群中节点，最初只有一个 `LocalServer` 表征自身节点。
    configuration.reset(new Configuration(serverId, *this));
    configurationManager.reset(new ConfigurationManager(*configuration));

    // 默认创建一个 `SegmentedLog`。
    log = Storage::LogFactory::makeLog(globals.config, storageLayout);

    for (uint64_t index = log->getLogStartIndex();
         index <= log->getLastLogIndex(); ++index) {
        // 如果是集群节点配置修改日志，那么 `configurationManager` 记录一下。
        if (entry.type() == Protocol::Raft::EntryType::CONFIGURATION) {
            configurationManager->add(index, entry.configuration());
        }
    }

    // Restore cluster time epoch from last log entry, if any
    if (log->getLastLogIndex() >= log->getLogStartIndex()) {
        clusterClock.newEpoch(
            log->getEntry(log->getLastLogIndex()).cluster_time());
    }

    if (log->metadata.has_current_term())
        currentTerm = log->metadata.current_term();
    if (log->metadata.has_voted_for())
        votedFor = log->metadata.voted_for();
    updateLogMetadata();

    // Read snapshot after reading log, since readSnapshot() will get rid of
    // conflicting log entries
    readSnapshot();

    // Clean up incomplete snapshots left by prior runs. This could be done
    // earlier, but maybe it's nicer to make sure we can get to this point
    // without PANICing before deleting these files.
    Storage::SnapshotFile::discardPartialSnapshots(storageLayout);

    stepDown(currentTerm);
    if (RaftConsensusInternal::startThreads) {
        
        leaderDiskThread = std::thread(
            &RaftConsensus::leaderDiskThreadMain, this);
        
        timerThread = std::thread(
            &RaftConsensus::timerThreadMain, this);

        stateMachineUpdaterThread = std::thread(
            &RaftConsensus::stateMachineUpdaterThreadMain, this);
        
        stepDownThread = std::thread(
            &RaftConsensus::stepDownThreadMain, this);
    }

    stateChanged.notify_all();
}
```

## 