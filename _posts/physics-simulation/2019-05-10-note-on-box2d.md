---
layout: post
mathjax: true
title: "Note on Box2D"
categories: physics-simulation
date: 2019-05-10 00:00:00
---

﻿Box2D 是一个开源的 2D 物理引擎，有一些成功的商业项目应用（《愤怒小鸟》等），相对可靠，代码相对简单，值得一读。本文是 Box2D 源代码的简单手记，如需补充物理模拟算法请参考以下书籍/论文，本人均已亲测，证实无雷，可放心阅读。

- *Game Developer Physics, 2nd edition*
- *Game Physics Engine Development*
- *Game Physics, 2nd edition* (not strongly recommened though)
- *Real-time Collision Detection*
- *Physically based Modelling: Principals and Practice*
- *Analytical Methods for Dynamic Simulation of Non-Penetrating Rigid Bodies*
- *Fast Contact Force Computation for Nonpenetrating Rigid Bodies*
- *Iterative Dynamics with Temporal Coherence*

文中代码片段经过简化处理（如错误处理或特殊处理），此外，过于细节的代码会用 `// ......` 表示省略。


## Interface and Data Structure

Box2D 的接口比较经典。`World` 是物理模拟器的最上层接口，每个 `World` 包含多个 `Body`，每个 `Body` 包含多个 `Fixture`。每个 `Fixture` 包含一个 `Shape`，根据 `Shape` 的不同（`Polygon`，`Circle` 和 `Chain` 等），拥有一定数量的 subshape（通常是 1）的 `FixtureProxy`。。一个简化的代码例子如下所示。

```c++
int main()
	// 创建模拟器。
	b2World world;

	// 创建刚体。
	b2BodyDef bodyDef;
	bodyDef.type = b2_dynamicBody;
	b2Body* body = world.CreateBody(&bodyDef);

	// 创建刚体形状和固点。
	b2PolygonShape dynamicBox;
	dynamicBox.SetAsBox(1.0f, 1.0f);
	b2FixtureDef fixtureDef;
	fixtureDef.shape = &dynamicBox;
	body->CreateFixture(&fixtureDef);

	// 模拟器循环。
	while (1) {
		world.Step();
	}
	return 0;
}
```

## Create Body and Fixture

`World` 创建 `Body`，`Body` 创建 `Fixture`, `Fixture` 通过 `CreateProxies`创建 `Proxy`。值得注意的是，`b2FixtureDef.userdata` 用于填充玩法相关的数据，与引擎自身关系不大；而 `b2BroadPhase::CreateProxy` 中 `DynamicTree::CreateProxy` 传递的是 `b2FixtureProxy`，存储在 `b2DynamicTree` 中。

```c++
// `b2FixtureDef.userdata` 用于填充玩法相关的数据。
b2Fixture* b2Body::CreateFixture(const b2FixtureDef* def) {
	b2Fixture* fixture = new b2Fixture;
	fixture.Create();
	fixture.CreateProxies(m_world.m_contactManager.m_broadPhase, m_xf);

	// 将 `fixture` 插入 `m_fixtureList`。
	// ......
	
	ResetMassData();
	m_world.flags |= newFixture;
}

void b2Fixture::CreateProxies(b2BroadPhase* broadPhase, const b2Transform& xf)
{
	m_proxyCount = m_shape->GetChildCount();
	for (int32 i = 0; i < m_proxyCount; ++i)
	{
		// 计算 subshape 的 AABB，简单的比如 Circle 的 AABB 就是中心点减去半径。
		b2FixtureProxy* proxy = m_proxies + i;
		m_shape->ComputeAABB(&proxy->aabb, xf, i);
		proxy->proxyId = broadPhase->CreateProxy(proxy->aabb, proxy);
		
		// 设置 subshape 的索引等属性。
		// ......
	}
}

// 此处 `userdata` 是 `b2FixtureProxy`。
int32 b2BroadPhase::CreateProxy(const b2AABB& aabb, void* userData)
{
	// 插入 DynamicTree，用于管理粗略地空间碰撞。
	int32 proxyId = m_tree.CreateProxy(aabb, userData);
	++m_proxyCount;
	
	// 记录 `proxyId`。
	m_moveBuffer[m_moveCount] = proxyId;
	++m_moveCount;
	return proxyId;
}
```

## Find New Contacts

在创建刚体之后，模拟器开始迭代模拟。首先，模拟器会检查是否有增加新的 `Fixture`，如果是，那么则尝试检查新碰撞。`World` 包含一个 `ContactManager` 用于管理碰撞检测，`ContactManager` 包含一个 `BroadPhase` 用于进行碰撞宽检测。

```c++
void b2World::Step(float32 dt, int32 velocityIterations, int32 positionIterations) {
	if (m_flags & e_newFixture) {
		m_contactManager.FindNewContacts();
		m_flags &= ~e_newFixture;
	}
	// ......
}

void b2ContactManager::FindNewContacts() {
	m_broadPhase.UpdatePairs(this);
}

template <typename T>
void b2BroadPhase::UpdatePairs(T* callback)
{
	m_pairCount = 0;
	for (int32 i = 0; i < m_moveCount; ++i)
	{
		// 检视新加入的 proxy id，并在 `m_tree` 查找潜在的碰撞 Fixture。
		m_queryProxyId = m_moveBuffer[i];
		const b2AABB& fatAABB = m_tree.GetFatAABB(m_queryProxyId);
		m_tree.Query(this, fatAABB);
	}
	m_moveCount = 0;

	// 排序以暴露重复。
	std::sort(m_pairBuffer, m_pairBuffer + m_pairCount, b2PairLessThan);

	int32 i = 0;
	while (i < m_pairCount){
		// 取出两个相撞的 subshape 的 `FixtureProxy` 并回传。
		b2Pair* primaryPair = m_pairBuffer + i;
		void* userDataA = m_tree.GetUserData(primaryPair->proxyIdA);
		void* userDataB = m_tree.GetUserData(primaryPair->proxyIdB);
		callback->AddPair(userDataA, userDataB);
		++i;

		// 跳过重复的对。
		// ......
	}
}
```

`DynamicTree::Query` 查找潜在碰撞的具体算法并不太复杂，暂时忽略，该函数会通过 `BroadPhase::QueryCallback` 回传潜在碰撞的 `FixtureProxy`，而后`BroadPhase` 通过 `ContactManager::AddPair` 进一步回传到 `ContactManager`。

```c++
bool b2BroadPhase::QueryCallback(int32 proxyId){
	// 检查。
	// ......
	
	// 记录潜在碰撞对象的 `proxyId`。
	m_pairBuffer[m_pairCount].proxyIdA = b2Min(proxyId, m_queryProxyId);
	m_pairBuffer[m_pairCount].proxyIdB = b2Max(proxyId, m_queryProxyId);
	++m_pairCount;
	return true;
}

void b2ContactManager::AddPair(void* proxyUserDataA, void* proxyUserDataB)
{
	// 取出 proxyA，proxyB，fixtureA，fixtureB，indexA，indexB，bodyA 和 bodyB。
	// .....
	
	// 遍历检查是否有来自相同的 subshape 的碰撞，如果有则略过。理论上，一个 subshape 可能有多个碰撞点，这
	// 里应该一种简化了。
	b2ContactEdge* edge = bodyB->GetContactList();
	while (edge) {
		// ......
		edge = edge->next;
	}

	// 一些细节检查，如是否都是静态刚体等，是否为联结，玩法过滤器等。
	// .....
	
	// 碰撞工厂产生（潜在的）碰撞对象。
	b2Contact* c = b2Contact::Create(fixtureA, indexA, fixtureB, indexB, m_allocator);
	// 从·`c` 中取出 fixtureA，fixtureB，indexA，indexB，bodyA 和 bodyB。
	// ......

	// 将 `c` 插入 `ContactManager.m_contactList`(`Contact` 列表)。
	// ......

	// `c->m_nodeA` 是 `ContactEdge`，表征两个碰撞的边。
	c->m_nodeA.contact = c;
	c->m_nodeA.other = bodyB;
	// 将 `c->m_nodeA` 插入 `bodyA->m_contactList`（`ContactEdge` 列表）。对 `c->m_nodeB` 也做类似的事情。
	// ......

	// 唤醒两个 `Body`。
	bodyA->SetAwake(true);
	bodyB->SetAwake(true);

	++m_contactCount;
}
```

`b2Contact::Create` 负责根据具体 `Fixture` 的 shape 找到对应的碰撞类型，产生 `Contact`。注意此时尚未进行严格检测，从代码上虽然产生了 `Contact` 类型的对象，然而这个 `Contact` 还没有被严格验证，可能实际上并没有碰撞。
```c++
b2Contact* b2Contact::Create(
	b2Fixture* fixtureA, int32 indexA,
	b2Fixture* fixtureB, int32 indexB,
	b2BlockAllocator* allocator)
{
	// 注册检测函数。
	// ......

	// 形状
	b2Shape::Type type1 = fixtureA->GetType();
	b2Shape::Type type2 = fixtureB->GetType();
	// 找到具体形状的碰撞检测函数。
	b2ContactCreateFcn* createFcn = s_registers[type1][type2].createFcn;
	return createFcn(fixtureA, indexA, fixtureB, indexB, allocator);
}
```

`createFcn` 的一个典型的例子就是 `Circle`，其他 shape 也是类似的。
```c++
b2Contact* b2CircleContact::Create(
	b2Fixture* fixtureA, int32,
	b2Fixture* fixtureB, int32, b2BlockAllocator* allocator)
{
	void* mem = allocator->Allocate(sizeof(b2CircleContact));
	return new (mem) b2CircleContact(fixtureA, fixtureB);
}
```

## Collide

在 `FindNewContacts` 之后，`World` 会对潜在碰撞列表中 `m_contactList` 中的 `Contact` 进行严格检查。

```c++
void b2ContactManager::Collide() {
	b2Contact* c = m_contactList;
	while (c) {
		// 取出 proxyIdA, proxyIdB, fixtureA，fixtureB，indexA，indexB，bodyA 和 bodyB。
		// ......
		// 检查对象是否出于激活状态。
		// ......

		// 宽检查。
		bool overlap = m_broadPhase.TestOverlap(proxyIdA, proxyIdB);
		// 如果检查不通过，则删除节点。
		// ......

		// 严格检查，产生包括碰撞点等细节。
		c->Update(m_contactListener);
		c = c->GetNext();
	}
}

void b2Contact::Update(b2ContactListener* listener) {
	b2Manifold oldManifold = m_manifold;
	m_flags |= e_enabledFlag;

	bool touching = false;
	// 上一帧的碰撞状态。
	bool wasTouching = (m_flags & e_touchingFlag) == e_touchingFlag;

	// 提取 bodyA，bodyB，transform xfA, 和 xfB。
	// ......
	// 省略掉一些 `Fixture.IsSensor` 作为感知器，不参与碰撞的细节。
	// ......

	// 严格碰撞检测。
	Evaluate(&m_manifold, xfA, xfB);
	// 如果通过了严格碰撞检测，那么流形的点计数 > 0，否则说明没有通过严格碰撞检测。
	touching = m_manifold.pointCount > 0;

	for (int32 i = 0; i < m_manifold.pointCount; ++i) {
		b2ManifoldPoint* mp2 = m_manifold.points + i;
		// 初始值，待求解。
		mp2->normalImpulse = 0.0f;
		mp2->tangentImpulse = 0.0f;

		// 在之前的碰撞中查找相同的碰撞流形，如果有则复用信息（详见论文算法）。		
		for (int32 j = 0; j < oldManifold.pointCount; ++j) {
			// ......
		}
	}

	// 如果碰撞状态发生了变化，那么唤醒 bodyA 和 bodyB。
	// ......
	// 设置或者取消 `m_flags` 的 `e_touchingFlag` 标志。
	// ......
	// 回调 `m_listener` 的 3 个回调：`BeginContact`，`EndContact`，和 `PreSolve`。
	// ......
}
```

`Contact::Evaluate` 是一个虚方法，根据实际碰撞类型而不同。最简单的例子是 `Circle` 的碰撞。由于性能关系，使用泛用的凸多边形碰撞检测算法可能不切实际，所以实际上只能通过 hard code type matching 的方式调用不同的算法检测碰撞。
```c++
void b2CircleContact::Evaluate(b2Manifold* manifold, const b2Transform& xfA, const b2Transform& xfB) {
	b2CollideCircles(manifold,
		(b2CircleShape*)m_fixtureA->GetShape(), xfA,
		(b2CircleShape*)m_fixtureB->GetShape(), xfB);
}
```

Box2D 使用 `Manifold` 和 `ManifoldPoint` 来记录碰撞面和点的相关信息。
```c++
void b2CollideCircles(
	b2Manifold* manifold,
	const b2CircleShape* circleA, const b2Transform& xfA,
	const b2CircleShape* circleB, const b2Transform& xfB)
{
	manifold->pointCount = 0;
	// 非常直观的半径比较，如果没有碰撞就直接返回，`manifold` 的 `pointCount` 保留为 0。
	// ......
	
	// 设置碰撞流体信息。
	manifold->type = b2Manifold::e_circles;
	manifold->localPoint = circleA->m_p; // 提示：`Circle.m_p` 是刚体坐标系的坐标。
	// ......
}
```

## Solve

```c++
void b2World::Solve(const b2TimeStep& step) {
	// 孤立岛，孤立无关的刚体，减小计算量。
	b2Island island(m_bodyCount,
		m_contactManager.m_contactCount,
		m_jointCount,
		&m_stackAllocator,
		m_contactManager.m_contactListener);

	// 从 `m_bodyList`，`m_contactManager.m_contactList` 和 `m_jointList` 清除所有的 `e_islangFlag`。
	// ......
	
	// 利用栈进行 DFS 搜索，建立一个刚体孤岛。
	int32 stackSize = m_bodyCount;
	b2Body** stack = (b2Body**)m_stackAllocator.Allocate(stackSize * sizeof(b2Body*));
	
	for (b2Body* seed = m_bodyList; seed; seed = seed->m_next) {
		// 过滤一些情况。
		// ......
		island.Clear();
		int32 stackCount = 0;
		stack[stackCount++] = seed;
		seed->m_flags |= b2Body::e_islandFlag;

		while (stackCount > 0)
		{
			b2Body* b = stack[--stackCount];
			// 孤岛添加刚体。
			island.Add(b);
			b->m_flags |= b2Body::e_awakeFlag;

			// 过滤静态刚体。
			// ......
			
			// DFS 搜索所有有关的刚体。
			for (b2ContactEdge* ce = b->m_contactList; ce; ce = ce->next)
			{
				b2Contact* contact = ce->contact;
				// 过滤。
				// ......
				// 孤岛添加碰撞。
				island.Add(contact);
				contact->m_flags |= b2Contact::e_islandFlag;
				
				// DFS 搜索。
				b2Body* other = ce->other;
				// 过滤。
				// ......
				stack[stackCount++] = other;
				other->m_flags |= b2Body::e_islandFlag;
			}
			
			// 搜索连接，暂时略过。
			// ......
		}

		island.Solve(&profile, step, m_gravity, m_allowSleep);

		// 再次将静态刚体清理 `e_islandFlag`。因为刚刚没有加入 island DFS，相当于图被分割了。
		// ......
	}
	m_stackAllocator.Free(stack);

	// Synchronize fixtures, check for out of range bodies.
	for (b2Body* b = m_bodyList; b; b = b->GetNext()) {
		// 过滤。
		// ......
		b->SynchronizeFixtures();
	}
	// 查找新的潜在碰撞对。
	m_contactManager.FindNewContacts();
}
```

`b2Island::Solve` 的过程比较复杂，涉及非常多的算法，而这其中的求解速度约束 `ContactSolver.SolveVelocityConstraints` 和位置约束 `ContactSolver.SolvePositionConstraints` 是重点，但其具体的算法我们稍后再做讨论。容易看到，力学反馈的过程是这样的：

1. 根据牛顿第二定律计算加速度和阻尼器；
2. 求解速度约束，求出速度；
3. 根据求解出的速度，使用欧拉积分器求解出位置；
4. 求解位置约束，求出最终位置。

```c++
void b2Island::Solve(b2Profile* profile, const b2TimeStep& step, const b2Vec2& gravity, bool allowSleep) {
	float32 h = step.dt;

	// 计算速度，施加阻尼。
	for (int32 i = 0; i < m_bodyCount; ++i)
	{
		// 从 body 取出位置 c，旋转 a，线性速度 v，和角速度 w。
		// ......
		// 存储上一帧的位置和旋转（用于连续碰撞检测）。
		b->m_sweep.c0 = b->m_sweep.c;
		b->m_sweep.a0 = b->m_sweep.a;

		if (b->m_type == b2_dynamicBody) {
			// 牛顿第二定律
			v += h * (b->m_gravityScale * gravity + b->m_invMass * b->m_force);
			w += h * b->m_invI * b->m_torque;

			// 阻尼器用于防止浮点数误差导致抖动的方法。
			v *= 1.0f / (1.0f + h * b->m_linearDamping);
			w *= 1.0f / (1.0f + h * b->m_angularDamping);
		}
		// 将 c / a / v / w 存储在 `m_positions` / `m_velocities`。
		// ......
	}

	// 创建 Solver。
	b2SolverData solverData;
	solverData.positions = m_positions;
	// ......
	b2ContactSolverDef contactSolverDef;
	contactSolverDef.step = step;
	contactSolverDef.contacts = m_contacts;
	// ......
	b2ContactSolver contactSolver(&contactSolverDef);
	contactSolver.InitializeVelocityConstraints();
	
	// 使用之前的计算结果做初始化。
	if (step.warmStarting)
		contactSolver.WarmStart();
	
	// 初始化连结的速度约束，暂时略过。
	// ......

	// 求解速度约束，通过 `step.velocityIterations` 次迭代寻找解。
	for (int32 i = 0; i < step.velocityIterations; ++i) {
		// 求解连结的速度约束，暂时略过。
		// ......
		contactSolver.SolveVelocityConstraints();
	}

	// 缓存冲量（详见论文算法）。
	contactSolver.StoreImpulses();

	// 积分位置和角度。经过 `contactSolver.SolveVelocityConstraints()`，速度和角
	// 速度（一定程度上）满足速度约束。
	for (int32 i = 0; i < m_bodyCount; ++i) {
		// 取出位置 c，旋转 a，线性速度 v，和角速度 w。
		// ......
		// 限制最大线性速度和角速度。
		// ......

		// 欧拉积分法。
		c += h * v;
		a += h * w;

		// 存储积分结果。
		// ......
	}

	// 求解位置约束，通过 `step.positionIterations` 次迭代寻找解。
	for (int32 i = 0; i < step.positionIterations; ++i) {
		bool contactsOkay = contactSolver.SolvePositionConstraints();
		// 求解连结的位置约束，暂时略过。
		// ......
	}

	// 将位置 c，旋转 a，线性速度 v，和角速度 w 存储到 `Body`。
	for (int32 i = 0; i < m_bodyCount; ++i) {
		// ......
	}

	// 如果允许刚体自行睡眠，检查速度是否都低于某个阈值，如果是，那么将这个孤岛所有的刚体睡眠。
	if (allowSleep) {
		// ......
	}
}
```

