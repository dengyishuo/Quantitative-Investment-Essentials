# 第29章 量化数据库与数据架构

## 第1节 为什么量化研究需要数据库

量化数据同时具有时间序列、横截面、多频率和多版本特征。行情数据持续追加，财务数据会修订，指数成分会调整，合约会换月，研究特征还需要记录生成时间和使用版本。CSV 适合交换少量数据，却难以独立承担完整的数据平台职责。

数据库和数据文件在量化系统中通常解决以下问题：

- 统一证券、交易日和字段标识；
- 保证增量更新、去重和幂等写入；
- 支持按标的、日期和版本快速查询；
- 管理事务、权限、并发和备份；
- 记录原始数据、清洗数据、特征和模型结果的血缘；
- 为研究、回测、实时信号和监控提供不同延迟的数据服务。

数据库选型不应只比较单机跑分。研究查询、实时服务、事务系统和历史归档对存储的要求不同，成熟系统往往组合使用多种工具。

## 第2节 数据分层与统一模型

建议将量化数据划分为以下层次：

1. **Raw：** 原始文件、接口响应和消息，不覆盖历史版本；
2. **Clean：** 完成字段统一、时区处理、复权、去重和质量检查的数据；
3. **Feature：** 因子、标签、风险暴露及模型输入；
4. **Serving：** 为回测、实盘和监控优化的查询结果、缓存和快照；
5. **Audit：** 数据版本、任务日志、异常记录和变更历史。

核心主键通常由 `instrument_id`、`trade_date` 或 `timestamp`、`source` 和 `version` 组成。日频行情可采用“标的—交易日”复合主键，逐笔数据还需要交易所序号或本地事件序号。财务数据应同时保留报告期、公告日和数据进入系统的时间，以避免未来信息泄漏。

## 第3节 DuckDB：本地分析型数据库

DuckDB 是嵌入式分析型数据库，适合研究员在单机上执行列式扫描、聚合、窗口计算和多表连接。它可以直接查询 Parquet 等文件，不要求先搭建独立数据库服务器。

典型用途包括：

- 查询多年日频行情和因子文件；
- 将分散的 Parquet 分区视为统一数据集；
- 在 Python 或 R 中执行 SQL 分析；
- 将 DataFrame 与文件数据连接；
- 生成回测所需的局部数据快照。

Python 示例：

```python
import duckdb

con = duckdb.connect("research.duckdb")
result = con.execute("""
    SELECT symbol,
           trade_date,
           close,
           avg(close) OVER (
               PARTITION BY symbol
               ORDER BY trade_date
               ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
           ) AS ma20
    FROM read_parquet('data/clean/bars/**/*.parquet')
    WHERE trade_date BETWEEN DATE '2020-01-01' AND DATE '2025-12-31'
""").df()
```

DuckDB 更适合分析型读取而非高并发在线事务。单机研究可以把 DuckDB 与 Parquet 作为默认起点，数据规模、并发和服务要求上升后再引入服务器数据库。

## 第4节 MySQL：结构化数据与事务管理

MySQL 适合保存需要事务、一致性、权限和多用户访问的结构化数据，例如：

- 证券主数据和交易日历；
- 数据源配置与采集任务状态；
- 策略、组合和账户配置；
- 订单、成交和持仓快照；
- 模型注册信息和实验元数据；
- 告警、审批和审计记录。

行情表的设计需要围绕常用查询建立复合索引。例如研究经常按标的和日期范围查询，可以使用：

```sql
CREATE TABLE daily_bar (
    instrument_id BIGINT NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(20, 6),
    high DECIMAL(20, 6),
    low DECIMAL(20, 6),
    close DECIMAL(20, 6),
    volume DECIMAL(30, 6),
    source VARCHAR(32) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (instrument_id, trade_date, source),
    INDEX idx_trade_date (trade_date)
) ENGINE=InnoDB;
```

不要为每只证券建立一张表。通常应按统一字段建表，再根据数据量和查询模式评估日期分区、冷热分层和归档策略。索引越多，写入和维护成本越高；分区也不能替代合理的主键与索引设计。

## 第5节 Redis：缓存、状态和实时消息

Redis 是内存数据存储，适合低延迟读取、缓存和事件驱动场景，不应被当作唯一的历史数据库。量化系统中的常见用途包括：

- 缓存最新行情、净值、风险指标和模型输出；
- 保存带过期时间的临时状态和分布式锁；
- 使用 Hash 保存对象状态；
- 使用 Sorted Set 保存带分数的候选标的或时间排序数据；
- 使用 Stream 传递行情、信号、订单和监控事件；
- 使用发布订阅分发非关键实时通知。

一个简单的键命名约定可以是：

```text
market:last:{symbol}
signal:{strategy}:{symbol}
portfolio:{account}:position
risk:{account}:snapshot
job:{task_id}:status
```

Redis 中的数据必须明确持久化级别、过期时间和恢复来源。订单、成交和正式持仓等关键事实应落入可审计的持久化系统，Redis 主要承担加速与协调职责。

## 第6节 PostgreSQL、TimescaleDB、ClickHouse与SQLite

### PostgreSQL

PostgreSQL 适合复杂 SQL、严格约束、JSON 数据和扩展生态。在需要统一管理研究元数据、业务数据和复杂查询时，它通常是 MySQL 的主要替代选择。

### TimescaleDB

TimescaleDB 建立在 PostgreSQL 之上，面向时间序列数据提供自动分块、时间聚合和保留策略。适合希望保留 PostgreSQL 生态，同时强化时间序列能力的团队。

### ClickHouse

ClickHouse 是列式分析数据库，适合大规模逐笔、订单簿、日志和行为数据的聚合查询。它擅长扫描和分析，但不应直接照搬事务数据库的表设计与更新方式。

### SQLite

SQLite 适合单文件配置、实验元数据、小型应用和可携带数据集。它部署简单，但在高并发写入和大规模分析场景下应谨慎使用。

## 第7节 Parquet、Arrow与对象存储

Parquet 是量化历史数据常用的列式文件格式，支持压缩、列裁剪和谓词下推。建议按查询习惯分区，例如：

```text
data/
  clean/
    daily_bar/
      market=CN/
        year=2025/
          part-000.parquet
```

分区不宜过细。大量微小文件会增加元数据和调度成本。Apache Arrow 提供跨语言的列式内存表示，便于 Python、R、DuckDB 和其他引擎之间减少复制。

对象存储适合保存原始文件、Parquet 数据集、模型文件和不可变快照。数据库保存索引、元数据和状态，对象存储保存大对象与历史版本，是常见的组合方式。

## 第8节 向量数据库与LLM知识库

处理公告、财报、研报和制度文件时，可以将文档切分、元数据和向量表示结合起来。向量检索用于寻找语义相关片段，关键词检索用于精确匹配代码、日期和专有名词，二者结合通常比单一检索更稳健。

量化知识库至少应保留：

- 原始文档与发布日期；
- 文档版本、来源和权限；
- 切分规则与文本位置；
- 嵌入模型和索引版本；
- 检索结果及其引用片段；
- Agent 调用和回答的审计记录。

向量数据库不能替代关系数据库。证券主数据、价格、订单和持仓仍应使用结构化模型；向量检索主要服务非结构化知识。

## 第9节 选型矩阵

| 需求 | 优先考虑 | 说明 |
|---|---|---|
| 单机研究、Parquet分析 | DuckDB | 部署简单，适合分析查询 |
| 小型配置和单文件应用 | SQLite | 易分发，适合轻量状态 |
| 事务、权限、多用户业务 | MySQL或PostgreSQL | 适合主数据、配置和交易记录 |
| 时间序列与PostgreSQL生态 | TimescaleDB | 强化时间分块与聚合 |
| 大规模列式分析 | ClickHouse | 适合逐笔、日志和宽表聚合 |
| 缓存、实时状态、消息流 | Redis | 低延迟，但需持久化事实来源 |
| 历史归档和跨引擎共享 | Parquet与对象存储 | 低成本、开放格式 |
| 文档语义检索 | 向量索引加关键词检索 | 必须保留来源和版本 |

## 第10节 推荐的量化数据架构

个人研究可以采用：

> 数据接口 → Raw 文件 → Parquet → DuckDB → Python/R → 回测结果

小型团队可以采用：

> 对象存储保存历史数据 + MySQL/PostgreSQL保存主数据和任务状态 + DuckDB执行研究查询 + Redis提供缓存和任务协调

高频或大规模平台可以进一步增加消息队列、ClickHouse、流处理和独立特征服务，但复杂度必须由实际需求驱动。

无论规模大小，都应落实以下原则：

- 原始数据不可覆盖；
- 时间和时区定义统一；
- 写入任务可重复执行且不产生重复数据；
- 研究数据能够按版本重建；
- 生产访问遵循最小权限；
- 密钥不写入代码仓库；
- 定期执行备份恢复演练；
- 关键数据具备质量规则、告警和审计记录。

## 第11节 官方资料

- [DuckDB Documentation](https://duckdb.org/docs/)
- [MySQL Reference Manual](https://dev.mysql.com/doc/)
- [Redis Documentation](https://redis.io/docs/latest/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [ClickHouse Documentation](https://clickhouse.com/docs/)
- [Apache Arrow Documentation](https://arrow.apache.org/docs/)

