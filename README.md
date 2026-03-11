# MM-Dermis 数据集预处理与检查流程

本项目用于对 MM-Dermis 数据集的标注索引进行展开、图片完整性检查，以及在四模态（普通、Amber、Pola、Wood）全部存在的前提下，生成干净索引并统计类别分布。

---

## 1. `1-DataProcess.py`：原始索引展开与标准化

- **输入**
  - 原始 Excel：`F:\MM-Dermis\annotations\classification.xlsx`

- **主要功能**
  - 处理 `SID` 字段：
    - 支持形如 `01-05` 的范围写法，将其展开为多行：01、02、03、04、05。
    - 保留单个 `SID` 不变。
  - 标准化字段格式：
    - `CID` 统一为 4 位字符串（如 `0001`）。
    - `SID` 统一为 2 位字符串（如 `01`）。
  - 将展开后的记录保存为新的 DataFrame。

- **输出**
  - 在 `F:\MM-Dermis\annotations\` 下生成带时间戳的索引文件，例如：  
    `classification_processed_YYYYMMDD_HHMMSS.xlsx`
  - 使用 `openpyxl` 写入，并将 `CID`、`SID` 列设置为文本格式，防止 Excel 去掉前导零。

---

## 2. `2-ImageCheck.py`：图片四模态完整性检查

- **输入**
  - 展开的索引文件：`classification_processed_*.xlsx`
  - 图片根目录：`F:\MM-Dermis\images`

- **目录与文件命名约定**
  - 目录结构：`F:\MM-Dermis\images\CID-{CID}\{SID}\`
  - 每个样本预期存在 4 个模态图片：
    - `CID_{cid}_{sid}.jpg`
    - `CID_{cid}_{sid}_Amber.jpg`
    - `CID_{cid}_{sid}_Pola.jpg`
    - `CID_{cid}_{sid}_Wood.jpg`

- **主要功能**
  - 遍历索引中每一条记录，构建对应图片目录并检查：
    - 目录是否存在；
    - 四个模态文件是否全部存在。
  - 统计：
    - 完整记录数；
    - 不完整记录数（缺少任一模态）；
    - 目录不存在的记录数。

- **输出**
  - 文本报告：
    - 保存到当前脚本所在目录：`image_check_report.txt`
    - 内容包括：检查时间、索引文件路径、图片根目录、整体统计信息、问题记录的详细列表（缺失文件、目录路径等）。
  - 缺失清单 CSV：
    - 当存在缺失或目录不存在时，在 `d:\VscFiles\Dermatoses\` 下生成：`missing_images.csv`
    - 列出所有有问题的记录，便于后续排查或补数据。
  - 控制台输出：
    - 打印总记录数、完整/不完整/目录不存在的数量及比例。

---

## 3. `3-IndexCleanAndStats.py`：根据四模态完整性清洗索引并统计类别分布

- **输入**
  - 展开的索引文件：`classification_processed_*.xlsx`
  - 图片根目录：`F:\MM-Dermis\images`

- **主要功能**
  - 对索引中每一行检查是否满足：
    - 对应 `CID-{CID}\{SID}\` 目录存在；
    - 四个模态图片（普通、Amber、Pola、Wood）全部存在。
  - 过滤掉任意模态缺失或目录不存在的记录，得到“干净索引”。
  - 对清洗后的索引按 `diagnosis` 字段统计类别样本数量。
  - 使用 `matplotlib` 绘制中文支持的横向条形图，展示各诊断类别的样本数量分布。

- **输出**
  - 清洗后的索引 Excel：
    - 保存在当前脚本目录：`classification_clean_YYYYMMDD_HHMMSS.xlsx`
    - 仅包含四模态全部存在的样本。
  - 类别分布图：
    - 保存到当前目录下的 `results\` 文件夹：  
      `class_distribution_YYYYMMDD_HHMMSS.png`
    - 图像为横向条形图（`barh`），支持中文标签。
  - 控制台输出：
    - 清洗前后的条目数量、剔除条数；
    - 各诊断类别的样本数量。

---

## 4. `4-LabelRules.py`：手工指定的分类规则与 OOD 定义

- **主要功能**
  - 定义前 10 个主要类别（In-distribution, ID），每类包含：
    - 中文名称；
    - 英文全称；
    - 英文简称（短标签）。
  - 定义一个统一的 OOD（Out-of-distribution）类别：
    - 标签索引统一为 `10`；
    - 所有指定的 OOD 诊断都映射到该标签。
  - 提供便捷映射：
    - `MAIN_LABELS`：前 10 个主类的详细定义；
    - `OOD_LABEL`：统一的 OOD 标签定义；
    - `OOD_DIAGNOSES`：映射到 OOD 的具体诊断列表；
    - `ALL_LABELS`：主类 + OOD 的完整标签列表；
    - `ZH_TO_INDEX`：中文诊断名 → 整数标签；
    - `INDEX_TO_ZH`：整数标签 → 中文名（主类 + OOD）。

- **前 10 个主类（ID）示意**
  - `0`：湿疹 — *Eczema*（`ECZ`）
  - `1`：银屑病 — *Psoriasis*（`PSO`）
  - `2`：白癜风 — *Vitiligo*（`VIT`）
  - `3`：特应性皮炎 — *Atopic dermatitis*（`AD`）
  - `4`：掌跖脓疱病 — *Palmoplantar pustulosis*（`PPP`）
  - `5`：大疱性类天疱疮 — *Bullous pemphigoid*（`BP`）
  - `6`：扁平苔藓 — *Lichen planus*（`LP`）
  - `7`：荨麻疹 — *Urticaria*（`URT`）
  - `8`：药物性皮炎 — *Drug eruption*（`DE`）
  - `9`：痤疮 — *Acne*（`ACN`）

- **OOD 诊断集合**
  - 统一映射到标签索引 `10`（OOD），包括：
    - 过敏性紫癜 — *Allergic purpura*（`AP`）
    - 玫瑰糠疹 — *Pityriasis rosea*（`PR`）
    - 结节性痒疹 — *Prurigo nodularis*（`PN`）
    - 血管炎 — *Vasculitis*（`VASC`）
    - 丘疹性荨麻疹 — *Papular urticaria*（`PU`）

---

## 推荐使用流程

1. 运行 `1-DataProcess.py`  
   - 从原始标注文件生成标准化、展开后的索引：`classification_processed_*.xlsx`。
2. 运行 `2-ImageCheck.py`  
   - 对当前索引进行图片完整性检查，确认哪些样本存在缺失或目录问题。
3. 运行 `3-IndexCleanAndStats.py`  
   - 在保证四模态图片全部存在的前提下，生成干净索引，并输出类别分布统计及可视化图像。
4. 结合 `4-LabelRules.py`  
   - 在后续建模阶段，将清洗后的索引（`classification_clean_*.xlsx`）中的 `diagnosis` 字段，通过 `ZH_TO_INDEX` 等映射转换为最终训练使用的标签体系（10 个 ID 类 + 1 个 OOD 类）。

通过以上步骤，可以构建一个**多模态均完整且标注规范**的 MM-Dermis 子集，用于后续建模与分析。 

