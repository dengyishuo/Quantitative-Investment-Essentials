# 第31章 R、Python与量化软件包

本章只介绍 R 和 Python 在量化研究中的定位、安装、环境管理及常用软件包。语法、算法实现和通用软件工程不在本章展开。

## 第1节 R与Python的定位

R 在统计分析、计量经济学、时间序列和可视化方面具有成熟生态；Python 在数据工程、机器学习、深度学习、服务部署和 LLM 应用方面覆盖更广。实际团队不必二选一：研究可以由 R 或 Python 主导，数据通过数据库、Parquet 和 Arrow 共享。

选择语言时应优先考虑：

- 团队已有代码和能力；
- 数据源和交易接口支持；
- 所需统计或机器学习软件包；
- 部署、监控和维护方式；
- 可复现环境与长期升级成本。

## 第2节 R的安装与环境

### 安装R

从 [CRAN](https://cran.r-project.org/) 选择对应操作系统的安装程序。需要交互式开发环境时，可以使用 RStudio 或支持 R 的编辑器。

安装软件包：

```r
install.packages(c(
  "data.table",
  "dplyr",
  "ggplot2",
  "quantmod",
  "PerformanceAnalytics"
))
```

### 使用renv管理项目环境

```r
install.packages("renv")
renv::init()
renv::snapshot()
```

`renv.lock` 应进入版本控制；软件包缓存和临时文件通常不进入仓库。新机器可以使用 `renv::restore()` 恢复依赖。

## 第3节 Python的安装与环境

从 [Python 官方网站](https://www.python.org/downloads/) 或团队认可的发行方式安装 Python。每个项目应使用独立虚拟环境。

使用标准库 `venv`：

```bash
python -m venv .venv
```

激活后安装软件包：

```bash
python -m pip install --upgrade pip
python -m pip install numpy pandas scipy statsmodels scikit-learn
```

项目应锁定依赖版本，并记录 Python 版本。不要把 API 密钥、数据库密码或交易凭证写入源码和依赖文件。

## 第4节 R量化软件包

### 数据处理与时间

- `data.table`：高性能表格处理；
- `dplyr`、`tidyr`：数据转换和整形；
- `lubridate`：日期时间处理；
- `arrow`：Arrow与Parquet；
- `DBI`、`dbplyr`：数据库接口和远程表查询；
- `duckdb`、`RMySQL`、`RPostgres`：连接常用数据库。

### 行情、收益与组合分析

- `quantmod`：金融数据、图表和常用研究接口；
- `xts`、`zoo`：时间序列容器；
- `TTR`：技术指标；
- `PerformanceAnalytics`：收益和风险评价；
- `PortfolioAnalytics`：组合约束与优化；
- `FinancialInstrument`：金融工具和头寸描述。

### 统计与计量

- `forecast`、`fable`：时间序列预测；
- `rugarch`：GARCH类模型；
- `urca`、`tseries`：单位根、协整和时间序列检验；
- `vars`：VAR模型；
- `glmnet`：Lasso、Ridge和Elastic Net；
- `fixest`：高维固定效应模型。

### 机器学习与深度学习

- `tidymodels`、`mlr3`：统一建模工作流；
- `ranger`：随机森林；
- `xgboost`、`lightgbm`：梯度提升树；
- `torch`、`keras3`：深度学习。

### 优化与并行

- `quadprog`、`ROI`：二次规划和统一优化接口；
- `nloptr`：非线性优化；
- `future`、`parallel`：并行任务。

## 第5节 Python量化软件包

### 数据与计算

- `numpy`：数组和数值计算；
- `pandas`：表格与时间序列；
- `polars`：列式DataFrame；
- `scipy`：科学计算与优化；
- `pyarrow`：Arrow与Parquet；
- `duckdb`：嵌入式SQL分析。

### 统计、计量与时间序列

- `statsmodels`：统计模型、回归和时间序列；
- `arch`：波动率模型；
- `linearmodels`：面板数据和资产定价模型；
- `pmdarima`：ARIMA工作流；
- `sktime`：时间序列学习接口。

### 机器学习与深度学习

- `scikit-learn`：预处理、模型、交叉验证和评估；
- `xgboost`、`lightgbm`、`catboost`：梯度提升树；
- `pytorch`、`tensorflow`：深度学习；
- `optuna`：超参数优化；
- `shap`：模型解释。

### 投资组合与风险

- `cvxpy`：凸优化建模；
- `PyPortfolioOpt`：常见组合优化方法；
- `riskfolio-lib`：组合和风险预算；
- `quantstats`、`empyrical`：绩效与风险指标。

### 回测与交易研究

- `vectorbt`：向量化研究与参数扫描；
- `backtrader`：事件驱动回测框架；
- `zipline-reloaded`：资产回测研究；
- `exchange_calendars`：交易所日历。

框架只负责实现，不保证研究正确。交易日历、复权、停牌、涨跌停、合约换月、撮合规则和成本模型仍需根据目标市场自行验证。

### 数据库与服务

- `sqlalchemy`：数据库访问抽象；
- `pymysql`、`mysqlclient`：MySQL客户端；
- `psycopg`：PostgreSQL客户端；
- `redis`：Redis客户端；
- `fastapi`：研究结果和模型服务接口。

### LLM与Agent

- 模型厂商官方SDK：调用语言模型和多模态模型；
- `pydantic`：结构化输入输出与校验；
- `transformers`：开源预训练模型；
- Agent与工作流框架：用于工具调用、状态管理和流程编排。

LLM生态变化较快，优先选择模型厂商官方SDK和最少依赖的实现，再按需要引入更高层框架。

## 第6节 R与Python协作

两种语言可以通过以下方式协作：

- 使用 Parquet、Arrow 和数据库共享数据；
- 使用命令行或任务调度器拆分研究步骤；
- R通过`reticulate`调用Python；
- Python通过`rpy2`调用R；
- 将稳定模型封装为HTTP或批处理服务。

跨语言调用会增加环境和部署复杂度。若文件或数据库接口已经足够，不必为了“无缝调用”强行嵌入另一种运行时。

## 第7节 推荐的最小环境

个人研究的最小组合可以是：

- Python或R任选其一；
- Git进行版本控制；
- Parquet保存历史数据；
- DuckDB执行本地查询；
- Jupyter、Quarto或普通脚本记录研究；
- 独立虚拟环境与锁定文件；
- 自动化测试和可重复运行的回测入口。

当出现多人协作、实时任务和交易状态后，再增加 MySQL/PostgreSQL、Redis、任务调度、对象存储和监控系统。

## 第8节 官方入口

- [R Project](https://www.r-project.org/)
- [CRAN](https://cran.r-project.org/)
- [Python Documentation](https://docs.python.org/)
- [PyPI](https://pypi.org/)
- [renv Documentation](https://rstudio.github.io/renv/)

