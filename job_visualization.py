"""
大数据招聘岗位：可视化方案（教学版）
技术栈：pandas + matplotlib
输入：jobs_clean.csv（清洗层产出）；若不存在则自动生成演示数据用于预览
输出：4 张图表 PNG -> charts/ 目录
  1) city_salary.png  城市需求与薪资（双轴组合图）
  2) edu_salary.png   学历 vs 平均薪资（柱状图）
  3) exp_salary.png   经验 vs 平均薪资（折线图）
  4) skill_freq.png   高频技能 Top15（水平条形图）

运行：python job_visualization.py
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # 无界面环境也能保存图片
import matplotlib.pyplot as plt

# ========== 0. 中文字体设置（关键：避免中文乱码/方框） ==========
# Windows 常用 "Microsoft YaHei"(微软雅黑) / "SimHei"(黑体)；macOS 用 "PingFang SC"
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "PingFang SC", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False   # 正常显示负号
plt.rcParams["figure.dpi"] = 120             # 提高清晰度，适合网页展示

CLEAN_FILE = "jobs_clean.csv"
OUT_DIR = "charts"
os.makedirs(OUT_DIR, exist_ok=True)


# ========== 1. 数据加载（含演示数据兜底） ==========
def load_data():
    """读取清洗结果；若文件不存在，生成结构一致的演示数据以便预览。"""
    if os.path.exists(CLEAN_FILE):
        df = pd.read_csv(CLEAN_FILE, encoding="utf-8-sig")
        print(f"[读取] {CLEAN_FILE}，{df.shape[0]} 行")
        return df
    print("[提示] 未找到 jobs_clean.csv，使用演示数据生成示例图（请替换为真实数据）。")
    return make_demo_data()


def make_demo_data():
    rng = np.random.default_rng(42)
    cities = ["北京", "上海", "深圳", "杭州", "广州", "成都", "南京", "武汉", "西安", "苏州"]
    skills_pool = ["Python", "SQL", "Hadoop", "Spark", "Hive", "Flink", "Kafka",
                   "Java", "Linux", "数据仓库", "Tableau", "机器学习", "Docker", "Scala"]
    n = 1500
    return pd.DataFrame({
        "city_clean": rng.choice(cities, n),
        "salary_avg": np.clip(rng.normal(18, 6, n), 6, 60),
        "edu_level": rng.integers(0, 6, n),
        "exp_min": rng.choice([0, 1, 2, 3, 5, 5, 8], n),
        "skills": [",".join(rng.choice(skills_pool, rng.integers(3, 8))) for _ in range(n)],
    })


# ========== 2. 图表1：城市需求与薪资（双轴组合图） ==========
def chart_city_salary(df):
    g = df.groupby("city_clean")["salary_avg"].agg(["count", "mean"]).reset_index()
    g = g[g["count"] >= 20].sort_values("count", ascending=False).head(12)
    fig, ax1 = plt.subplots(figsize=(11, 5.5))
    ax1.bar(g["city_clean"], g["count"], color="#4C8BF5", alpha=.85, label="岗位数量")
    ax1.set_ylabel("岗位数量", color="#4C8BF5", fontsize=12)
    ax1.tick_params(axis="y", labelcolor="#4C8BF5")
    ax2 = ax1.twinx()  # 右轴：平均薪资
    ax2.plot(g["city_clean"], g["mean"], color="#E8743B", marker="o",
             linewidth=2.2, label="平均薪资(K)")
    ax2.set_ylabel("平均薪资 (K/月)", color="#E8743B", fontsize=12)
    ax2.tick_params(axis="y", labelcolor="#E8743B")
    ax1.set_title("各城市岗位需求量与平均薪资（双轴）", fontsize=14, fontweight="bold")
    ax1.set_xlabel("城市")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "city_salary.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[保存] {path}")
    return path


# ========== 3. 图表2：学历 vs 平均薪资（柱状图） ==========
def chart_edu_salary(df):
    labels = {0: "学历不限", 1: "中专/中技", 2: "大专", 3: "本科", 4: "硕士", 5: "博士"}
    g = df.groupby("edu_level")["salary_avg"].mean().reindex(range(6)).dropna()
    xs = [labels[i] for i in g.index]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(xs, g.values, color="#0F9D8A")
    ax.set_title("不同学历的平均薪资", fontsize=14, fontweight="bold")
    ax.set_xlabel("学历要求")
    ax.set_ylabel("平均薪资 (K/月)")
    for b in bars:  # 柱顶标注数值
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3,
                f"{b.get_height():.1f}", ha="center", fontsize=10)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "edu_salary.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[保存] {path}")
    return path


# ========== 4. 图表3：经验 vs 平均薪资（折线图） ==========
def chart_exp_salary(df):
    g = df.groupby("exp_min")["salary_avg"].mean().sort_index()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(g.index, g.values, marker="o", color="#7B5EA7", linewidth=2.4)
    ax.set_title("工作经验与平均薪资关系", fontsize=14, fontweight="bold")
    ax.set_xlabel("最低经验要求（年）")
    ax.set_ylabel("平均薪资 (K/月)")
    ax.grid(alpha=.3)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "exp_salary.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[保存] {path}")
    return path


# ========== 5. 图表4：高频技能 Top15（水平条形图） ==========
def chart_skill_freq(df):
    ser = df["skills"].dropna().astype(str).str.split(r"[,，、/]").explode().str.strip()
    ser = ser[ser != ""]
    top = ser.value_counts().head(15).sort_values()
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.barh(top.index, top.values, color="#4C8BF5")
    ax.set_title("招聘岗位高频技能 Top15", fontsize=14, fontweight="bold")
    ax.set_xlabel("出现频次")
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "skill_freq.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[保存] {path}")
    return path


if __name__ == "__main__":
    df = load_data()
    chart_city_salary(df)
    chart_edu_salary(df)
    chart_exp_salary(df)
    chart_skill_freq(df)
    print("[完成] 4 张图表已生成至 charts/ 目录。")
