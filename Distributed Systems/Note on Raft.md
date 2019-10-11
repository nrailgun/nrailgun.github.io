# In Search of an Understandable Consensus Algorithm

本文是一致性算法 Raft 的论文 *In Search of an Understandable Consensus Algorithm* 的笔记，仅仅记录了算法本身和简要思想，方法的推理过程请查看论文。

## Introduction

**Raft** is a consensus algorithm for managing a replicated log. It produces a result equivalent to (multi-)Paxos (**strong consistency** and **partition tolerance**), but it's more understandable. It has several novel features: 

1. **strong leader**, 
2. **leader election**,
3. and **membership changes**.

## The Raft Consensus Algorithm

简单而言：

- 通过 leader 来代理所有的 log 同步，当 log 被*足够数量*的 follower 接收时，commit 这个 log 并执行。
- 后续Election 过程就是一个 lamport clock 的变种，请先阅读 lamport clock 的论文理解其思想。

注意足够数量（quorum）并不一定是过半数（majority）。下面是算法的 summary。

### State

Updated on stable storage before responding to RPCs.

| Persistent state on all servers: |                                                              |
| -------------------------------- | ------------------------------------------------------------ |
| **currentTerm**                  | latest term server has seen (initialized to $0$ on first boot, increases monotonically). |
| **votedFor**                     | candidateId that received vote in current term (or null if none) |
| **log[]**                        | log entries; each entry contains command for state machine, and term when entry was received by leader (first index is $1$) |

| Volatile state on all servers: |                                                              |
| ------------------------------ | ------------------------------------------------------------ |
| **commitIndex**                | index of highest log entry known to be committed (initialized to $0$, increases monotonically) |
| **lastApplied**                | index of highest log entry applied to state machine (initialized to $0$, increases monotonically) |

| Volatile state on leaders: | (Reinitialized after election)                               |
| -------------------------- | ------------------------------------------------------------ |
| **nextIndex[]**            | for each server, index of the next log entry to send to that server (initialized to leader last log index + 1) |
| **matchIndex[]**           | for each server, index of highest log entry known to be replicated on server (initialized to 0, increases monotonically) |

### AppendEntries RPC

Invoked by leader to replicate log entries; also used as heartbeat.

| Arguments:       |                                                              |
| ---------------- | ------------------------------------------------------------ |
| **term**         | leader’s term                                                |
| **leaderId**     | so follower can redirect clients                             |
| **prevLogIndex** | index of log entry immediately preceding new ones            |
| **prevLogTerm**  | term of prevLogIndex entry                                   |
| **entries[]**    | log entries to store (empty for heartbeat; may send more than one for efficiency) |
| **leaderCommit** | leader’s commitIndex                                         |

| Results:    |                                                              |
| ----------- | ------------------------------------------------------------ |
| **term**    | currentTerm, for leader to update itself                     |
| **success** | true if follower contained entry matching prevLogIndex and prevLogTerm |

 Receiver implementation:
1. Reply false if term $\lt$ currentTerm
2. Reply false if log doesn’t contain an entry at prevLogIndex whose term matches prevLogTerm
3. If an existing entry conflicts with a new one (same index but different terms), delete the existing entry and all that follow it
4. Append any new entries not already in the log
5. If leaderCommit > commitIndex, set commitIndex $=$ min(leaderCommit, index of last new entry)

### RequestVote RPC

Invoked by candidates to gather votes.

| Arguments:       |                                     |
| ---------------- | ----------------------------------- |
| **term**         | candidate’s term                    |
| **candidateId**  | candidate requesting vote           |
| **lastLogIndex** | index of candidate’s last log entry |
| **lastLogTerm**  | term of candidate’s last log entry  |

| Results:        |                                             |
| --------------- | ------------------------------------------- |
| **term**        | currentTerm, for candidate to update itself |
| **voteGranted** | true means candidate received vote          |

Receiver implementation: 

1. Reply false if term < currentTerm
2. If votedFor is null or candidateId, and candidate’s log is at least as up-to-date as receiver’s log, grant vote

### Rules for Servers

- All Servers:
  - If commitIndex $\gt$ lastApplied: increment lastApplied, apply log[lastApplied] to state machine
  - If RPC request or response contains term T $\gt$ currentTerm: set currentTerm = T, convert to follower
- Followers:
  - Respond to RPCs from candidates and leaders
  - If election timeout elapses without receiving AppendEntries RPC from current leader or granting vote to candidate: convert to candidate
- Candidates:
  - On conversion to candidate, start election:
    - Increment currentTerm
    - Vote for self
    - Reset election timer
    - Send RequestVote RPCs to all other servers
  - If votes received from majority of servers: become leader
  - If AppendEntries RPC received from new leader: convert to follower
  - If election timeout elapses: start new election
- Leaders:
  - Upon election: send initial empty AppendEntries RPCs (heartbeat) to each server; repeat during idle periods to prevent election timeouts
  - If command received from client: append entry to local log, respond after entry applied to state machine
  - If last log index ≥ nextIndex for a follower: send AppendEntries RPC with log entries starting at nextIndex
    - If successful: update nextIndex and matchIndex for follower
    - If AppendEntries fails because of log inconsistency: decrement nextIndex and retry
  - If there exists an N such that N > commitIndex, a majority of matchIndex[i] ≥ N, and log[N].term == currentTerm: set commitIndex = N.

## Cluster Membership Changes

上文假定集群成员固定，实际上可能发生变化。最简单的方法是一个 2PC 过程，先暂停所有节点的服务并更新集群配置，随后再重启所有节点。Raft 认为这种方法可用性较低。

Raft 将新配置同步到 follower 节点，leader 所有的决议需要同时获得旧和新两个配置的半数节点统一才认为被 commit。一旦新配置被 commit，新 leader 可以保证不丢失新配置，此时添加新 log 去掉旧配置并等待其被提交。

# LogCabin

LogCabin 是 Raft 算法论文提供的最小实现。即使是最小实现，也大约有 4w+ 行代码，可见分布式系统实现之难。

## 客户端

和 Etcd 类似，连接集群进行键值对读写。**客户端是受信的**，不能将客户端放在公网。

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

客户端根据集群列表试图去联系集群并找到 leader。随机找 1 个节点询问是否为 leader，如果不是 leader，根据节点所知的 leader hint 或者继续查找。如果没有 leader，那么说明暂时服务不可用（多数节点宕机）。

实际上，一个节点认为自己是 leader，集群节点不一定认同，可能实际上已经有了另一个 leader。虽然两个节点都认为自己是 leader，但是集群多数节点承认的只有一个。自以为是的 leader 在发布 log 的时候会被拒绝，客户端切一个节点继续即可。

客户端的节点列表里，要至少有一个节点还在集群里，还在就还可以更新列表，都不在就没办法了。极端例子是，一开始有 3 个节点，客户端知道 3 个，然后加了 6 个新节点，然后 3 个旧的挂了，集群依旧工作，不过客户端就连接不上（3 个旧节点）了。使用 DNS 一类的方案可以缓解这个问题，不过按理这种情况在管理员正常履行职责的前提下出现概率较低。

## 启动

`Global` 是初始化顺序受控的全局变量集合。其初始化过程包含：

- 初始化 RPC，以及3 个 RPC 服务：`controlService`、`raftService`，和 `ClientService`。分别转发集群成员操作，日志同步，和键值对操作，实现较为简单。

- 初始化 Raft 实例。
- 初始化 `StateMachine` 实例。

初始化后，LogCabin 开始 IO 复用循环，响应 RPC 请求。

## 日志

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

## 节点初始化

最初集群中只有一个节点，管理员通过 `ClientImpl` 发起请求 `SetConfiguration`，要求为集群增加（改变）成员。`ClientImpl` 包含了一个 `LeaderRPC` 用于与集群 Leader 通信，`SetConfiguration`  的请求通过 `LeaderRPC` 送出。

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

    // 如果日志不为空，根据时间戳估计集群时间。
    if (log->getLastLogIndex() >= log->getLogStartIndex()) {
        clusterClock.newEpoch(
            log->getEntry(log->getLastLogIndex()).cluster_time());
    }

    // update metadata
    if (log->metadata.has_current_term())
        currentTerm = log->metadata.current_term();
    if (log->metadata.has_voted_for())
        votedFor = log->metadata.voted_for();
    // 交替写，避免损坏 metadata 文件。
    updateLogMetadata();

    // 读 snapshot，删除上次 crash 没做完的 snapshot。
    readSnapshot();
    Storage::SnapshotFile::discardPartialSnapshots(storageLayout);

    stepDown(currentTerm);
    if (RaftConsensusInternal::startThreads) {
        
        // 不断将需要提交的日志写入可靠存储。
        leaderDiskThread = std::thread(
            &RaftConsensus::leaderDiskThreadMain, this);
        
        // 如果 follower 有一段时间没有接收到 append entries，发起选举。
        timerThread = std::thread(
            &RaftConsensus::timerThreadMain, this);

        // 状态机线程
        stateMachineUpdaterThread = std::thread(
            &RaftConsensus::stateMachineUpdaterThreadMain, this);
        
        stepDownThread = std::thread(
            &RaftConsensus::stepDownThreadMain, this);
    }

    stateChanged.notify_all();
}
```

## 竞选

在 `RaftConsensus::bootstrap` metadata 中的 term 会被从 0 设置到 1。节点 1 运行时 `RaftConsensus::init` 会通过 `RaftConsensus::stepDown` 设置 `startElectionAt`。

在单节点的情况下，由于没有 *AppendEntities* 的 RPC 请求，很快 `startElectionAt` 就会超时，`timerThreadMain` 就会通过 `RaftConsensus::startNewEletion` 发起选举。由于仅有单个节点，显然会选择自己。

```c++
void RaftConsensus::startNewElection()
{
    // `commitIndex` 实际上是 configuration log commit 时候的 log index。
    if (commitIndex >= configuration->id &&
        !configuration->hasVote(configuration->localServer)) {
        setElectionTimer();
        return;
    }

    // 要求投票
    ++currentTerm;
    state = State::CANDIDATE;
    leaderId = 0;
    votedFor = serverId;
    printElectionState();
    setElectionTimer();
    configuration->forEach(&Server::beginRequestVote);
    // ...

    // 写 metadata，取消 rpc。
    updateLogMetadata();
    interruptAll();

    // 特殊处理只有一个自身节点的情况，程序设计需要，无关算法，忽略。
    if (configuration->quorumAll(&Server::haveVote))
        becomeLeader();
}

// 请求 peer（另外节点）投票
void RaftConsensus::requestVote(std::unique_lock<Mutex>& lockGuard, Peer& peer)
{
    Protocol::Raft::RequestVote::Request request;
    request.set_term(currentTerm);
    // ... 填 request

    // call rpc
    Protocol::Raft::RequestVote::Response response;
    TimePoint start = Clock::now();
    uint64_t epoch = currentEpoch;
    Peer::CallStatus status = peer.callRPC(
    	Protocol::Raft::OpCode::REQUEST_VOTE, request, response, lockGuard);
    switch (status) {
        case Peer::CallStatus::OK:
            break;
        // ... 处理错误
    }

    // 如果不是本轮竞选的投票，或者自己已经不再是 candidate。
    if (currentTerm != request.term() || state != State::CANDIDATE ||
        peer.exiting) {
        return;
    }

    if (response.term() > currentTerm) {
        // 有人跟我抢，抢回去，看谁 term 大谁 nb。
        stepDown(response.term());
    } else {
        peer.requestVoteDone = true;
        peer.lastAckEpoch = epoch;
        stateChanged.notify_all();

        if (response.granted()) {
            // 收到本票
            peer.haveVote_ = true;
            if (configuration->quorumAll(&Server::haveVote))
                // 竞选成功
                becomeLeader();
        }
    }
}

void RaftConsensus::becomeLeader()
{
    state = State::LEADER;
    leaderId = serverId;
    startElectionAt = TimePoint::max();
    withholdVotesUntil = TimePoint::max();

    // 忽略掉选举的时间。集群时间属于物理时间，raft 不依赖物理时间。
    clusterClock.newEpoch(clusterClock.clusterTimeAtEpoch);
    
    // 设置几个标志位。Raft 是非拜占庭式的，不需要告知 follower 竞选结果，反正
    // AppendEntries rpc 发过去对面就信了。
    configuration->forEach(&Server::beginLeadership);

    // 加一个 log，顺路把 leader 上之前没有 commit 的一起 commit 了，免得非要等
    // append entries rpc 才 commit。
    Log::Entry entry;
    // ...
    append({&entry});
    
    interruptAll();
}
```

其他节点收到 *RequestVote* rpc 检查下是否投赞成票。

```c++
void
RaftConsensus::handleRequestVote(
                    const Protocol::Raft::RequestVote::Request& request,
                    Protocol::Raft::RequestVote::Response& response)
{
    std::lock_guard<Mutex> lockGuard(mutex);

    // 要做我 leader，你的 log 必须比我更“灵通”。
    uint64_t lastLogIndex = log->getLastLogIndex();
    uint64_t lastLogTerm = getLastLogTerm();
    bool logIsOk = (request.last_log_term() > lastLogTerm ||
                    (request.last_log_term() == lastLogTerm &&
                     request.last_log_index() >= lastLogIndex));
    
    if (withholdVotesUntil > Clock::now()) {
        // leader 没死吧？你自己网络断了？
        response.set_term(currentTerm);
        response.set_granted(false);
        response.set_log_ok(logIsOk);
        return;
    }

    if (request.term() > currentTerm) {
        // 投票
        stepDown(request.term());
    }

    // 同时竞选，如果对方 log 比自己“灵通”，投票。
    if (request.term() == currentTerm) {
        if (logIsOk && votedFor == 0) {
            stepDown(currentTerm);
            setElectionTimer();
            votedFor = request.server_id();
            updateLogMetadata();
        }
    }

    response.set_term(currentTerm);
    response.set_granted(request.term() == currentTerm &&
                         votedFor == request.server_id());
    response.set_log_ok(logIsOk);
}
```

## 日志的添加与提交

客户端通过 `ClientService` 将请求转发给 `RaftConsensus`。如果 log 被提交（超过半数同意），那么状态机执行这个命令。

```c++
void ClientService::stateMachineCommand(RPC::ServerRPC rpc)
{
    PRELUDE(StateMachineCommand);
    Core::Buffer cmdBuffer;
    rpc.getRequest(cmdBuffer);
    std::pair<Result, uint64_t> result = globals.raft->replicate(cmdBuffer);
    if (result.first == Result::RETRY || result.first == Result::NOT_LEADER) {
        // ...
    }
    // 状态机执行
    uint64_t logIndex = result.second;
    if (!globals.stateMachine->waitForResponse(logIndex, request, response)) {
        // ...
    }
    rpc.reply(response);
}

std::pair<RaftConsensus::ClientResult, uint64_t>
RaftConsensus::replicate(const Core::Buffer& operation)
{
    std::unique_lock<Mutex> lockGuard(mutex);
    Log::Entry entry;
    // ...
    return replicateEntry(entry, lockGuard);
}

std::pair<RaftConsensus::ClientResult, uint64_t>
RaftConsensus::replicateEntry(Log::Entry& entry,
	std::unique_lock<Mutex>& lockGuard)
{
    if (state == State::LEADER) {
        // ...
        append({&entry});
        while (!exiting && currentTerm == entry.term()) {
            // 等待提交成功，返回给客户端。
            if (commitIndex >= index) {
                return {ClientResult::SUCCESS, index};
            }
            stateChanged.wait(lockGuard);
        }
    }
    return {ClientResult::NOT_LEADER, 0};
}

void RaftConsensus::append(const std::vector<const Log::Entry*>& entries)
{
    std::pair<uint64_t, uint64_t> range = log->append(entries);
    if (state == State::LEADER) {
        // leader 稍后同步，交给 `RaftConsensus::leaderDiskThreadMain` 处理。
        logSyncQueued = true;
    } else {
        // follower 立刻同步日志
        std::unique_ptr<Log::Sync> sync = log->takeSync();
        sync->wait();
        log->syncComplete(std::move(sync));
    }
    
    // 处理 configuration
    uint64_t index = range.first;
    for (auto it = entries.begin(); it != entries.end(); ++it) {
        const Log::Entry& entry = **it;
        if (entry.type() == Protocol::Raft::EntryType::CONFIGURATION)
            configurationManager->add(index, entry.configuration());
        ++index;
    }
    stateChanged.notify_all();
}
```

在 leader 的 `peerThreadMain` 中，定期会发送一下 *AppendEntries* RPC 给 follower 节点。通过 `RaftService` 将请求转发给 `RaftConsensus`。

```c++
void RaftConsensus::peerThreadMain(std::shared_ptr<Peer> peer) {
    // ...
    while (!peer->exiting) {
        // ...
        if (peer->backoffUntil > now) {
            waitUntil = peer->backoffUntil;
        } else {
            switch (state) {
                // ...
                case State::LEADER:
                    if (peer->getMatchIndex() < log->getLastLogIndex() ||
                        peer->nextHeartbeatTime < now) {
                        // 有其他还没 match 的 log，就调用 `appendEntries`。
                        appendEntries(lockGuard, *peer);
                    }
	// ...
}

// follower 收到 rpc 请求，调用 `handleAppendEntries`。
void RaftService::appendEntries(RPC::ServerRPC rpc)
{
    PRELUDE(AppendEntries);
    globals.raft->handleAppendEntries(request, response);
    rpc.reply(response);
}
```

`appendEntries` 之后会检查看看能不能前移 `commitIndex`。`RaftConsensus::advanceCommitIndex` 会通过 `QuorumMin` 检查是否半数都完成 log replication。`QuorumMin` 只是一个类似 python `map` / `reduce` 的检查 `matchIndex` 的普通函数，没有什么特殊的。

```c++
void RaftConsensus::appendEntries(std::unique_lock<Mutex>& lockGuard,
                             Peer& peer)
{
    uint64_t lastLogIndex = log->getLastLogIndex();
    uint64_t prevLogIndex = peer.nextIndex - 1;

    // 不在 log 里，那么 *InstallSnapshot*。
    if (peer.nextIndex < log->getLogStartIndex()) {
        installSnapshot(lockGuard, peer);
        return;
    }
    uint64_t prevLogTerm;
    if (prevLogIndex >= log->getLogStartIndex()) {
        prevLogTerm = log->getEntry(prevLogIndex).term();
    }
    // ... 其他情况，可能需要 *InstallSnapshot*。

    // 造 request
    Protocol::Raft::AppendEntries::Request request;
    request.set_server_id(serverId);
    request.set_term(currentTerm);
    // ...

    // RPC
    Protocol::Raft::AppendEntries::Response response;
    // ...
    Peer::CallStatus status = peer.callRPC(
                Protocol::Raft::OpCode::APPEND_ENTRIES,
                request, response, lockGuard);
    // ... 一些异常
    
    if (response.term() > currentTerm) {
        // leader 换了
        stepDown(response.term());
    } else {
        peer.lastAckEpoch = epoch;
        stateChanged.notify_all();
        peer.nextHeartbeatTime = start + HEARTBEAT_PERIOD;
        if (response.success()) {
            peer.matchIndex = prevLogIndex + numEntries;
            // 看下能不能把 commit index 向前推。
            advanceCommitIndex();
            peer.nextIndex = peer.matchIndex + 1;
            // ...
        } else {
            // 太超前就矫正一下，稍后补发。
            if (peer.nextIndex > 1)
                --peer.nextIndex;
            if (response.has_last_log_index() &&
                peer.nextIndex > response.last_log_index() + 1) {
                peer.nextIndex = response.last_log_index() + 1;
            }
        }
    }
    // ...
}

void RaftConsensus::advanceCommitIndex()
{
    // 看看半数以上的 peer 的 match index 大于什么，然后 commitIndex 移动过去。
    uint64_t newCommitIndex =
        configuration->quorumMin(&Server::getMatchIndex);

    if (commitIndex >= newCommitIndex)
        return;
    if (log->getEntry(newCommitIndex).term() != currentTerm)
        return;
    commitIndex = newCommitIndex;
    // ...
}

// `appendEntries` 接收方
void RaftConsensus::handleAppendEntries(
                    const Protocol::Raft::AppendEntries::Request& request,
                    Protocol::Raft::AppendEntries::Response& response)
{
    // ...
    response.set_term(currentTerm);
    response.set_success(false);
    response.set_last_log_index(log->getLastLogIndex());
	// ... 论文里的各种检查条件，实在没有必要重复描述了。
    response.set_success(true);

    uint64_t index = request.prev_log_index();
    for (auto it = request.entries().begin();
         it != request.entries().end(); ++it) {
        ++index;
        
        const Protocol::Raft::Entry& entry = *it;
        if (entry.has_index()) {
            // 修 #160: "Packing entries into AppendEntries requests is
            // broken (critical)"。可见实现一个正确的分布式系统在工程上极为
            // **Complicated and Difficult**，自己实现可谓危险重重。
            assert(entry.index() == index);
        }
        
        if (index < log->getLogStartIndex()) {
            // snapshoted
            continue;
        }
        if (log->getLastLogIndex() >= index) {
            // 新 leader 不明就里，重新 replicate 之前的 logs（见 paper），导致
            // 错误的 truncate。
            if (log->getEntry(index).term() == entry.term())
                continue;
            // 旧 leader 半路死了，这些没 commit 的 log 新 leader 没有，要丢掉了。
            uint64_t lastIndexKept = index - 1;
            uint64_t numTruncating = log->getLastLogIndex() - lastIndexKept;
            numEntriesTruncated += numTruncating;
            log->truncateSuffix(lastIndexKept);
            configurationManager->truncateSuffix(lastIndexKept);
        }

        std::vector<const Protocol::Raft::Entry*> entries;
        do {
            const Protocol::Raft::Entry& entry = *it;
            entries.push_back(&entry);
            ++it;
            ++index;
        } while (it != request.entries().end());
        append(entries);
        clusterClock.newEpoch(entries.back()->cluster_time());
        break;
    }
    response.set_last_log_index(log->getLastLogIndex());

    // 直接根据 rpc 的 `commit_index` 设置 commit index，实际上会落后一些，稍后
    // 的 heart beat 中才能跟上 `commit_index`。理论上 `commitIndex` 并不会减
    // 少，不过似乎由于一些实现上的原因导致了减少（却不影响正确性），然而过不去不变式
    // 检查，所以这里有个 if。
    if (commitIndex < request.commit_index()) {
        commitIndex = request.commit_index();
        stateChanged.notify_all();
    }
}
```

## 变更成员

```c++
RaftConsensus::ClientResult RaftConsensus::setConfiguration(
        const Protocol::Client::SetConfiguration::Request& request,
        Protocol::Client::SetConfiguration::Response& response)
{
	// ...
    // 配置已经变化，这个配置可能不合适了。
    if (configuration->id != request.old_id()) {
        return ClientResult::FAIL;
    }
    // 不能同时改两个不同配置。
    if (configuration->state != Configuration::State::STABLE) {
        return ClientResult::FAIL;
    }

    // 最初的 `state` 是 BLANK，有节点配置的情况下是 STABLE，现在进入 STAGING（临时）状态。
    // 把新的节点信息写到 `newServers` 里。
    Protocol::Raft::SimpleConfiguration nextConfiguration;
    for (auto it = request.new_servers().begin(); it != request.new_servers().end(); ++it) {
        Protocol::Raft::Server* s = nextConfiguration.add_servers();
        s->set_server_id(it->server_id());
        s->set_addresses(it->addresses());
    }
    configuration->setStagingServers(nextConfiguration);
    stateChanged.notify_all();

    // 新节点如果没有 catch up，稍后 commit 的时候会有很多需要同步的前置 log，会导致集群响应缓慢，
    // 在开始更改配置之前，先容他们先 catch up 一下。
    uint64_t term = currentTerm;
    ++currentEpoch;
    uint64_t epoch = currentEpoch;
    TimePoint checkProgressAt = Clock::now() + ELECTION_TIMEOUT;
    while (true) {
        if (exiting || term != currentTerm) {
            // lost leadership
            return ClientResult::NOT_LEADER;
        }
        if (configuration->stagingAll(&Server::isCaughtUp)) {
            // 都 catch up 了，开始更换配置。
            break;
        }
        if (Clock::now() >= checkProgressAt) {
            using RaftConsensusInternal::StagingProgressing;
            StagingProgressing progressing(epoch, response);
            if (!configuration->stagingAll(progressing)) {
                // 有部分节点很久没 ack 了，没救，失败。
                configuration->resetStagingServers();
                stateChanged.notify_all();
                return ClientResult::FAIL;
            } else {
                // 虽然有节点还没 catch up，但是有收到他们的（某些）ack，再给个机会。
                ++currentEpoch;
                epoch = currentEpoch;
                checkProgressAt = Clock::now() + ELECTION_TIMEOUT;
            }
        }
        stateChanged.wait_until(lockGuard, checkProgressAt);
    }

    // 变更节点配置也是一个 log。
    Protocol::Raft::Configuration newConfiguration;
    // ...
    // 传播这个 configuration log。
    std::pair<ClientResult, uint64_t> result = replicateEntry(entry, lockGuard);
    if (result.first != ClientResult::SUCCESS) {
        // ... 失败
        return result.first;
    }
    uint64_t transitionalId = result.second;

    // 等待 stable configuration 被提交，这个判断条件非常 hack。
    while (true) {
        if (configuration->id > transitionalId && commitIndex >= configuration->id) {
            // 提交 ok。
            response.mutable_ok();
            return ClientResult::SUCCESS;
        }
        if (exiting || term != currentTerm) {
			// lost leadership
            return ClientResult::NOT_LEADER;
        }
        stateChanged.wait(lockGuard);
    }
}
```

注意 replicate log 过程中，configuration log 的 append 是特殊处理的，不会被状态机执行，不等 commit 会被直接取出设置。如果失败，和普通的 log 一样，稍后会被删除掉，`restoreInvariants` 会再次把集群节点设置改回来。

```c++
void RaftConsensus::append(const std::vector<const Log::Entry*>& entries)
{
    // ...
    uint64_t index = range.first;
    for (auto it = entries.begin(); it != entries.end(); ++it) {
        const Log::Entry& entry = **it;
        if (entry.type() == Protocol::Raft::EntryType::CONFIGURATION)
            configurationManager->add(index, entry.configuration());
        ++index;
    }
    stateChanged.notify_all();
}

void RaftConsensus::advanceCommitIndex()
{
	// ...
    // commit 1 个 transitional 的 config 后，就可以 append stable 的 config 了。
    if (configuration->state == Configuration::State::TRANSITIONAL) {
        Log::Entry entry;
        entry.set_type(Protocol::Raft::EntryType::CONFIGURATION);
        // ...
        *entry.mutable_configuration()->mutable_prev_configuration() =
            configuration->description.next_configuration();
        append({&entry});
        return;
    }
}

void ConfigurationManager::add(
    uint64_t index,
    const Protocol::Raft::Configuration& description)
{
    descriptions[index] = description;
    restoreInvariants();
}

// 虽然名字是 invariant，但是实际上却是在实现算法，而不是 model checking，有些误导性。
void ConfigurationManager::restoreInvariants()
{
    // ...
    auto it = descriptions.rbegin();
    if (configuration.id != it->first)
        configuration.setConfiguration(it->first, it->second);
}

void Configuration::setConfiguration(
        uint64_t newId,
        const Protocol::Raft::Configuration& newDescription)
{
    if (newDescription.next_configuration().servers().size() == 0)
        state = State::STABLE;
    else
        state = State::TRANSITIONAL; // append 之后就从 STAGING 变成 TRANSITIONAL 了。

    id = newId;
    description = newDescription;
    oldServers.servers.clear();
    newServers.servers.clear();
    // ...
}
```

