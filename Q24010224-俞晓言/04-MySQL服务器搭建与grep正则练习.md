# 实验 04：MySQL 服务器搭建与 grep 正则练习

## 实验信息

- 学生：俞晓言
- 学号：Q24010224
- 完成日期：2026 年 9 月 23 日
- 客户端：macOS 终端，通过 SSH 操作 Ubuntu
- 实验环境：UTM 中的 Ubuntu 24.04.4 LTS ARM64（主机名 `merlin-ubuntu`，用户 `merlin`）
- 软件版本：MySQL 8.0.46、DBeaver Community 26.2.1

## 实验目标

1. 安装并验证 MySQL 服务。
2. 创建数据库 `mydb` 和仅供本机连接的普通数据库用户 `myuser`，验证其权限。
3. 安装适合 ARM64 的 DBeaver 图形客户端，并理解本机连接与跨机器连接的差别。
4. 使用 `grep` 练习行首、行尾、字符集合、转义和通配符等基本正则表达式。

## 一、MySQL 服务器

### 1. 安装并检查服务

本次在 SSH 登录后的 Ubuntu Shell 中执行命令；没有进入持续的 root Shell。`sudo` 只对需要管理员权限的命令生效：

```bash
sudo apt update
sudo apt install mysql-server
systemctl is-active mysql
systemctl is-enabled mysql
mysql --version
```

安装后得到：

```text
active
enabled
mysql  Ver 8.0.46-0ubuntu0.24.04.4 for Linux on aarch64 ((Ubuntu))
```

`active` 表示服务正在运行，`enabled` 表示开机自动启动。课件中的 `sudo su root` 也能完成安装，但本实验不需要让后续所有命令一直以 root 身份运行。

### 2. 创建数据库和用户

Ubuntu 默认安装的 MySQL 可通过 `sudo mysql` 以系统管理员身份进入 MySQL 命令行。随后执行：

```sql
CREATE DATABASE IF NOT EXISTS mydb
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'myuser'@'localhost'
  IDENTIFIED BY '<实验密码>';

GRANT ALL PRIVILEGES ON mydb.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;

SHOW DATABASES;
SHOW GRANTS FOR 'myuser'@'localhost';
EXIT;
```

这里的 `<实验密码>` 是报告中的占位符，执行时使用课件给出的练习密码；仓库不记录真实密码。`utf8mb4` 能存储完整的 Unicode 字符，`utf8mb4_unicode_ci` 是该数据库的排序规则。`mydb.*` 将授权范围限制为 `mydb` 中的对象，而非整个 MySQL 实例。

管理员执行 `SHOW DATABASES;` 时，结果包含 `mydb`。`SHOW GRANTS` 显示 `myuser@localhost` 对 `mydb.*` 拥有 `ALL PRIVILEGES`。

### 3. 以普通用户验证连接

分别测试本地 Unix Socket 和 TCP 连接，密码由 `-p` 提示交互输入，不写在命令行中：

```bash
mysql -u myuser -p mydb
mysql --protocol=TCP -h 127.0.0.1 -P 3306 -u myuser -p mydb
```

两种方式均成功连接。在 MySQL 中执行 `SELECT CURRENT_USER(), DATABASE();`，结果为 `myuser@localhost` 和 `mydb`。普通用户执行 `SHOW DATABASES;` 可看到 `mydb`，但看不到管理员的 `mysql`、`sys` 等数据库。这比仅检查 `mysql.service` 的状态更能证明数据库与权限配置已生效。

`localhost` / `127.0.0.1` 指 Ubuntu 虚拟机本身。`'myuser'@'localhost'` **不是**允许 Mac 直接访问的远程用户；本实验没有修改 MySQL 的监听地址、防火墙或开放 3306 端口，因为课件要求的本地连接不需要这些操作。

## 二、DBeaver 安装与架构排查

课件建议在 Ubuntu 中执行 `sudo snap install dbeaver-ce --classic`。本次按此方法安装后，启动报错：

```text
cannot snap-exec: cannot exec ".../dbeaver": exec format error
```

检查发现 Ubuntu 为 `aarch64`，而所装 Snap 中的 `dbeaver` 可执行文件却是 `x86-64`。因此问题不是 MySQL 服务或密码，而是应用程序与 CPU 架构不匹配。

随后从 [DBeaver 官方 26.2.1 下载目录](https://dbeaver.io/files/26.2.1/)取得 `dbeaver-ce-26.2.1-linux-aarch64.deb`，核对官方 SHA-256 校验值后，在 Ubuntu 中安装：

```bash
sudo apt install ./dbeaver-ce-26.2.1-linux-aarch64.deb
file /usr/share/dbeaver-ce/dbeaver
```

文件检查结果为 `ARM aarch64`。DBeaver 的进程和图形界面组件已正常启动；错误架构的 Snap 安装已移除。由于本次未可靠地完成 DBeaver 界面里的“测试连接”，**不能把图形客户端连接成功写成已验证结果**。已验证的是 MySQL 命令行经 `127.0.0.1:3306` 成功连接。

后续在 Ubuntu 的 DBeaver 中新建 MySQL 连接时，应填写：主机 `127.0.0.1`、端口 `3306`、数据库 `mydb`、用户 `myuser`，并在应用中手动输入实验密码。如果选择“保存密码”，应先考虑共享电脑或截图泄露的风险。课件的示例密码强度很低，仅适合隔离的课堂练习环境；之后应更换，不应复用于其他账号。

## 三、`grep` 正则表达式练习

课件以 `textfile` 为输入文件，但没有提供原文件内容。为使结果可复现，本次在 Ubuntu 的 `/home/merlin/textfile` 创建了如下测试数据：

```text
name
normal 5.a
web 12.00
yellow 5.b
misc 5.a
price 5.00
alpha 12.00
other
```

在该文件所在目录依次执行：

```bash
grep '^n' textfile
grep '\.00$' textfile
grep '5\..' textfile
grep '^[wy]' textfile
```

| 表达式 | 含义 | 本次匹配结果 |
| --- | --- | --- |
| `^n` | `^` 锚定行首，匹配以 `n` 开头的行 | `name`；`normal 5.a` |
| `\.00$` | `\.` 匹配字面上的点，`$` 锚定行尾 | `web 12.00`；`price 5.00`；`alpha 12.00` |
| `5\..` | 数字 `5` 后跟字面点，再跟任意一个字符 | `normal 5.a`；`yellow 5.b`；`misc 5.a`；`price 5.00` |
| `^[wy]` | 行首是 `w` 或 `y` | `web 12.00`；`yellow 5.b` |

这里使用单引号保护正则表达式，避免 Shell 提前解释特殊字符。第三个表达式中的最后一个 `.` 是“任意单个字符”，因此 `5.00` 中的 `5.0` 也会匹配；它没有要求整行必须在此处结束。第二个表达式则用 `\.` 避免把点号误当成任意字符，并用 `$` 确保 `.00` 位于行尾。

## 实验结论

MySQL 服务已安装、运行并设置为开机启动，`mydb` 与 `myuser@localhost` 已创建；普通用户通过 Socket 和本机 TCP 两种方式均能登录并访问目标数据库。四条 `grep` 命令均在自建的 `textfile` 上得到预期输出。

DBeaver 的 Snap 包因内含 x86-64 可执行文件，无法在 ARM64 虚拟机上运行；已改装官方 ARM64 `.deb` 并确认程序启动。图形界面的数据库连接测试尚未完成，因此该部分保留为后续验证项。整个实验未将 MySQL 暴露给虚拟机外部网络，也未在仓库中记录数据库密码。
