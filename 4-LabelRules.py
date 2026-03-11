"""
Manually defined classification rules for MM-Dermis subset.

包含两部分：
1. 前 10 个主要类别（In-distribution, ID），每类有中文名、英文名和英文简称。
2. OOD（Out-of-distribution）集合，将若干诊断并入一个统一的 OOD 类。

此外，本文件还提供一个工具函数与命令行入口：
- 对 `classification_clean_20260311_233813.xlsx` 进行标签整理，
  为每一条记录生成数值标签和英文简称等字段，并保存带标签的新表。
"""

import os

from dataclasses import dataclass
from typing import List, Dict

import pandas as pd


@dataclass(frozen=True)
class LabelDef:
    """单个标签定义。"""

    index: int          # 数值标签，用于训练（0-9 为主类，10 为 OOD）
    name_zh: str        # 中文名
    name_en: str        # 英文全称
    name_en_short: str  # 英文简称（短标签，如 ECZ, PSO 等）
    group: str          # 'ID' 主类 或 'OOD'


# === 1. 前 10 个主要类别（ID 类） ===
MAIN_LABELS: List[LabelDef] = [
    LabelDef(
        index=0,
        name_zh="湿疹",
        name_en="Eczema",
        name_en_short="ECZ",
        group="ID",
    ),
    LabelDef(
        index=1,
        name_zh="银屑病",
        name_en="Psoriasis",
        name_en_short="PSO",
        group="ID",
    ),
    LabelDef(
        index=2,
        name_zh="白癜风",
        name_en="Vitiligo",
        name_en_short="VIT",
        group="ID",
    ),
    LabelDef(
        index=3,
        name_zh="特应性皮炎",
        name_en="Atopic dermatitis",
        name_en_short="AD",
        group="ID",
    ),
    LabelDef(
        index=4,
        name_zh="掌跖脓疱病",
        name_en="Palmoplantar pustulosis",
        name_en_short="PPP",
        group="ID",
    ),
    LabelDef(
        index=5,
        name_zh="大疱性类天疱疮",
        name_en="Bullous pemphigoid",
        name_en_short="BP",
        group="ID",
    ),
    LabelDef(
        index=6,
        name_zh="扁平苔藓",
        name_en="Lichen planus",
        name_en_short="LP",
        group="ID",
    ),
    LabelDef(
        index=7,
        name_zh="荨麻疹",
        name_en="Urticaria",
        name_en_short="URT",
        group="ID",
    ),
    LabelDef(
        index=8,
        name_zh="药物性皮炎",
        name_en="Drug eruption",
        name_en_short="DE",
        group="ID",
    ),
    LabelDef(
        index=9,
        name_zh="痤疮",
        name_en="Acne",
        name_en_short="ACN",
        group="ID",
    ),
]


# === 2. OOD 规则 ===

# 统一的 OOD 标签定义（index=10）
OOD_LABEL = LabelDef(
    index=10,
    name_zh="OOD",
    name_en="Out-of-distribution",
    name_en_short="OOD",
    group="OOD",
)

# 收入 OOD 的具体诊断条目（原始中文诊断 → OOD）
OOD_DIAGNOSES: List[Dict[str, str]] = [
    {
        "name_zh": "过敏性紫癜",
        "name_en": "Allergic purpura",
        "name_en_short": "AP",
    },
    {
        "name_zh": "玫瑰糠疹",
        "name_en": "Pityriasis rosea",
        "name_en_short": "PR",
    },
    {
        "name_zh": "结节性痒疹",
        "name_en": "Prurigo nodularis",
        "name_en_short": "PN",
    },
    {
        "name_zh": "血管炎",
        "name_en": "Vasculitis",
        "name_en_short": "VASC",
    },
    {
        "name_zh": "丘疹性荨麻疹",
        "name_en": "Papular urticaria",
        "name_en_short": "PU",
    },
]


# === 3. 便捷映射（可在训练/推理脚本中直接使用） ===

ALL_LABELS: List[LabelDef] = MAIN_LABELS + [OOD_LABEL]

# 中文诊断名 → 数值标签 index
ZH_TO_INDEX: Dict[str, int] = {
    # 主类
    **{lbl.name_zh: lbl.index for lbl in MAIN_LABELS},
    # OOD 子诊断全部映射到 OOD index
    **{item["name_zh"]: OOD_LABEL.index for item in OOD_DIAGNOSES},
}

# 数值标签 index → 中文名
INDEX_TO_ZH: Dict[int, str] = {lbl.index: lbl.name_zh for lbl in ALL_LABELS}


def apply_label_rules_to_clean_file() -> None:
    """
    读取指定的 classification_clean_20260311_233813.xlsx，
    按照上面的规则为每一条记录生成标签，并保存新文件。

    - 只保留在 ZH_TO_INDEX 中有定义的诊断（前 10 个主类 + OOD 集合）。
    - 新增字段：
        - label_index: 整数标签（0-9 为主类，10 为 OOD）
        - label_zh: 标签中文名（主类中文名或 "OOD"）
        - label_en_short: 英文简称（主类简称或 "OOD"）
        - label_group: "ID" 或 "OOD"
    """
    # 1. 读取原始清洗索引
    clean_file = r"d:\VscFiles\MM-DermisDatasetProcess\classification_clean_20260311_233813.xlsx"
    print(f"正在读取清洗后的索引文件: {clean_file}")
    df = pd.read_excel(clean_file)
    print(f"原始记录数: {len(df)}")

    if "diagnosis" not in df.columns:
        raise ValueError("输入表格中缺少 'diagnosis' 列，无法根据诊断进行标签映射。")

    # 2. 只保留我们在规则中明确列出的诊断
    known_diags = set(ZH_TO_INDEX.keys())
    mask_known = df["diagnosis"].isin(known_diags)
    df_known = df[mask_known].copy().reset_index(drop=True)

    dropped = len(df) - len(df_known)
    print(f"根据规则保留的记录数: {len(df_known)}")
    print(f"被丢弃（未在当前规则中定义诊断）的记录数: {dropped}")

    # 3. 为每条记录生成标签相关字段
    def _map_row(row):
        diag_zh = row["diagnosis"]
        idx = ZH_TO_INDEX[diag_zh]
        row["label_index"] = idx

        # 主类或 OOD 定义
        if idx == OOD_LABEL.index:
            lbl = OOD_LABEL
        else:
            # 从 MAIN_LABELS 中查找对应 index
            lbl = next(l for l in MAIN_LABELS if l.index == idx)

        row["label_zh"] = lbl.name_zh
        row["label_en_short"] = lbl.name_en_short
        row["label_group"] = lbl.group
        return row

    df_labeled = df_known.apply(_map_row, axis=1)

    # 4. 保存新的带标签索引文件
    base, ext = os.path.splitext(clean_file)
    out_file = base + "_labeled" + ext
    df_labeled.to_excel(out_file, index=False)

    print(f"\n带标签的索引文件已保存到: {out_file}")
    print("字段包括: 原始字段 + label_index, label_zh, label_en_short, label_group")


if __name__ == "__main__":
    apply_label_rules_to_clean_file()
