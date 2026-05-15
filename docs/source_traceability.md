# Source Traceability

This traceability file follows `任务说明1-电热耦合仿真数据框架.docx` and `任务说明2-修正仿真数据框架.docx`. Each `source_id` records the source name, URL or literature path, data type, public/assumed status, whether it is suitable for SCI manuscript core citation, and whether it should be used only as a COMSOL initial value.

## Source Register

| source_id | 来源名称 | URL或文献 | 数据类型 | 是否公开 | 是否假设 | SCI正文可引用 | 仅用于COMSOL初值 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK_DOC_1 | 任务说明1-电热耦合仿真数据框架 | `/Users/luolin/Desktop/考虑接触电阻劣化与环境扰动的110 kV RIP变压器套管电热耦合响应及风险边界分析/任务说明/任务说明1-电热耦合仿真数据框架.docx` | 数据框架约束 | 否 | 否 | 否 | 否 | 本次修订依据，包括工况拆分、字段要求和追溯要求。 |
| TASK_DOC_2 | 任务说明2-修正仿真数据框架 | `/Users/luolin/Desktop/考虑接触电阻劣化与环境扰动的110 kV RIP变压器套管电热耦合响应及风险边界分析/任务说明/任务说明2-修正仿真数据框架.docx` | 数据框架修正规则 | 否 | 否 | 否 | 否 | 本次继续修订依据，包括边界条件、材料not_for_core_citation、天气字段和验证目标。 |
| TASK_DOC_5 | 任务说明5-防止混淆 BRFGL1 和 BRFGL2 | `/Users/luolin/Desktop/考虑接触电阻劣化与环境扰动的110 kV RIP变压器套管电热耦合响应及风险边界分析/任务说明/任务说明5-防止混淆 BRFGL1 和 BRFGL2.docx` | 主模型选择与备选模型声明 | 否 | 否 | 否 | 否 | 明确BRFGL1-126/1250-4为直接载流主模型，BRFGL2-126/1250-4仅作为电缆载流备选模型。 |
| IEC60137_2017_WEBSTORE | IEC 60137官方页面 | https://webstore.iec.ch/en/publication/29183 | 标准适用范围 | 是 | 否 | 可引用标准本身；网页仅作检索入口 | 否 | 正式论文应引用购买/可访问的IEC 60137标准文本。 |
| IEC60137_RATED_CURRENT_SERIES | IEC 60137公开预览/额定电流序列 | https://standards.iteh.ai/catalog/standards/iec/6513ae03-63aa-4a6d-8076-03edd09e665a/iec-60137-2003 | 额定电流与热稳定上下文 | 是 | 否 | 谨慎；正式数值应核对标准原文 | 否 | 支撑800 A、1250 A等级和短时热稳定工况上下文。 |
| MGC_DTOI_126_800 | MGC/Duresca 126 kV 800 A公开厂家图样 | https://dnestrenergo.md/wp-content/uploads/2024/10/610.13.0036-DTOI-126kV-800A-E300.pdf | 厂家样本/外形尺寸/额定参数 | 是 | 否 | 可作为公开厂家样本引用 | 否 | 用于126 kV/800 A外形、爬距、试验电压等。 |
| IZOLYATOR_RIP_CATALOG | Izolyator RIP bushing catalogue text | https://www.scribd.com/document/403652984/Transformer-bushings-pdf | 厂家样本/额定参数 | 是 | 否 | 不建议作为SCI核心引用，需替换为厂家正式PDF | 否 | 仅作为126 kV/1250 A参数旁证。 |
| MDPI_2025_126KV | Energies 2025公开论文中的126 kV RIP套管模型 | https://www.mdpi.com/1996-1073/18/13/3239 | 几何、屏长、材料、边界、短时热稳定目标 | 是 | 否 | 不作为SCI正文核心来源；可作为公开初值/对照来源 | 部分字段是初值 | 任务说明2要求避免将MDPI开源论文作为SCI正文核心来源，因此相关材料参数在`materials.csv`中标记`not_for_core_citation=true`。 |
| OPEN_METEO_SHENYANG_2025_FULL_YEAR | Open-Meteo Historical Weather API, Shenyang, 2025 full year | https://open-meteo.com/en/docs/historical-weather-api | 开源逐小时气象边界 | 是 | 站点选择是假设 | 可引用API/数据源，站点选择需说明 | 否 | 完整query保存在 `data/raw_sources/weather_sources/open_meteo_shenyang_2025_query.txt`；`weather_hourly.csv`包含`source_url`和`quality_flag`。 |
| LIT_ZHANG_2009_ATP | Zhang S. Evaluation of thermal transient and overload capability of high-voltage bushings with ATP | 本地PDF `[1] Zhang S...pdf` | 热网络、过载能力、热容 | 否/取决于访问权限 | 否 | 是，按正式文献信息引用 | 否 | 支撑暂态热模型和过载能力分析。 |
| LIT_JYOTHI_2010_RIP_TEMP | Jyothi N S et al. Temperature distribution in RIP insulation for transformer bushings | 本地PDF `[2] Jyothi...pdf` | RIP温度分布、交流电导率 | 否/取决于访问权限 | 否 | 是，按正式文献信息引用 | 否 | 支撑RIP电导率热源。 |
| LIT_ZHANG_2013_EQUAL_MARGIN | Zhang S, Peng Z, Liu P. Inner insulation structure optimization of UHV RIP oil-SF6 bushing | 本地PDF `[3] Zhang S, Peng Z...pdf` | 电热耦合、等裕度、电场约束 | 否/取决于访问权限 | 否 | 是，按正式文献信息引用 | 否 | 支撑电场裕度与电容屏设计。 |
| LIT_ALLAHBAKHSHI_2016_FEM | Allahbakhshi M, Akbari M. Heat analysis of power transformer bushings using FEM | 本地PDF `[4] Allahbakhshi...pdf` | FEM热分析、热点位置 | 否/取决于访问权限 | 否 | 是，按正式文献信息引用 | 否 | 支撑导体热点与边界条件。 |
| LIT_AKBARI_2017_TRANSIENT | Akbari M et al. Heat analysis in transient and steady states considering load variations | 本地PDF `[5] Akbari...pdf` | 稳态/暂态、负荷、油温、气温、风速 | 否/取决于访问权限 | 否 | 是，按正式文献信息引用 | 否 | 支撑steady/transient拆分和时变边界。 |
| LIT_WANG_2014_3D_COUPLED | Wang Q et al. 3-D coupled electromagnetic-fluid-thermal analysis | 本地PDF `[6] Wang Q...pdf` | 三维电磁-流体-热耦合 | 否/取决于访问权限 | 否 | 是 | 否 | 支撑二维模型局限性讨论。 |
| LIT_WANG_2015_REGULARITY | Wang Q et al. Regularity analysis of temperature distribution | 本地PDF `[7] Wang Q, Liao...pdf` | 温度分布规律、多因素分析 | 否/取决于访问权限 | 否 | 是 | 否 | 支撑敏感性分析。 |
| LIT_WANG_2016_HEAT_STRUCTURE | Wang Q et al. Novel dissipating heat structure | 本地PDF `[8] Wang Q, Yang...pdf` | 散热结构、RIP温度风险 | 否/取决于访问权限 | 否 | 是 | 否 | 支撑约120 degC附近RIP热风险边界。 |
| LIT_TIAN_2019_CONTACT | Tian H et al. Contact deterioration process in 500 kV converter transformer RIP bushings | 本地PDF `[9] Tian H...pdf` | 接触电阻劣化、局部过热、外表面温差 | 否/取决于访问权限 | 否 | 是 | 否 | 支撑 `contact_resistance_model.csv` 的倍率和温差预警思路。 |
| LIT_TANG_2021_DEFECTIVE | Tang H et al. Electro-thermal comprehensive analysis method for defective RIP valve-side bushing | 本地PDF `[10] Tang H...pdf` | 接触异常、电容屏悬浮、多频电热分析 | 否/取决于访问权限 | 否 | 是 | 否 | 支撑缺陷类型扩展。 |
| LIT_LIN_2022_CONTACT | Lin M et al. 3-D thermal analysis and current-carrying connection defects | 本地PDF `[11] Lin M...pdf` | 接触缺陷、电流、环境温度、温差反演 | 否/取决于访问权限 | 否 | 是 | 否 | 支撑接触倍率、表面温差和电流耦合。 |
| LIT_ZHENG_2023_DIELECTRIC_LOSS_HST | Zheng H et al. Hot spot temperature based upon dielectric loss | 本地PDF `[13] Zheng H...pdf` | 介损-热点温度反演 | 否/取决于访问权限 | 否 | 是 | 否 | 支撑 `dielectric_loss_nominal` 验证目标。 |
| LIT_WANG_2014_DIELECTRIC | Wang Q et al. Dielectric response and space charge in EIP laminates | 本地PDF `[15] Wang Q, Peng Z...pdf` | RIP介电响应、空间电荷、电导率 | 否/取决于访问权限 | 否 | 是 | 否 | 支撑RIP电导率温度敏感性和tan_delta倍率。 |
| LIT_NING_2015_DIELECTRIC | Ning X et al. Dielectric properties of multi-layer epoxy resin-impregnated crepe paper | 本地PDF `[16] Ning X...pdf` | 多层RIP介电常数、介损、电导率 | 否/取决于访问权限 | 否 | 是 | 否 | 支撑RIP材料参数敏感性。 |
| LIT_WANG_2022_AGING | Wang Y et al. Aging time and electrical treeing in epoxy resin-impregnated paper | 本地PDF `[17] Wang Y...pdf` | 热老化、电树枝、绝缘劣化 | 否/取决于访问权限 | 否 | 是 | 否 | 支撑RIP aging/tan_delta multiplier，但倍率本身仍为敏感性假设。 |
| LIT_SHI_2025_AMBIENT | Shi W et al. Extreme ambient temperatures on electro-thermal fields | 本地PDF `[18] Shi W...pdf` | 极端环境温度、电热场扰动 | 否/取决于访问权限 | 否 | 是 | 否 | 支撑气象扰动工况和典型日选择。 |
| LIT_CHU_2025_POD | Chu Z et al. Fast computation based on POD | 本地PDF `[19] Chu Z...pdf` | 降阶计算、快速扫参 | 否/取决于访问权限 | 否 | 是 | 否 | 后续风险边界快速计算可引用。 |
| SHIN_ETSU_SILICONE_RUBBER | Shin-Etsu silicone rubber public catalogue | https://www.shinetsusilicone-global.com/catalog/pdf/rubber_e.pdf | 硅橡胶参数量级核对 | 是 | 否 | 不建议作为核心SCI材料依据 | 否 | 只作量级核对；SCI正文应优先引用材料手册或论文。 |
| CRC_OR_COPPER_ENGINEERING_REFERENCE | 铜电阻温度系数工程参考 | 待替换为CRC/材料手册正式条目 | 材料温度系数 | 是 | 是 | 需替换后才适合 | 否 | 当前为常用工程值，必须敏感性分析。 |
| SPECIFIC_OIL_DATASHEET_REQUIRED | 变压器油厂家/试验数据待补 | N/A | 变压器油材料参数 | 否 | 是 | 否 | 否 | 当前油参数为占位敏感性参数，不能作为SCI正文数值来源。 |
| SPECIFIC_DATASHEET_REQUIRED | 具体材料数据表待补 | N/A | 材料参数占位 | 否 | 是 | 否 | 否 | 用于铝、铜或油等需最终数据表确认的参数。 |
| SPECIFIC_HEAT_TRANSFER_REFERENCE_REQUIRED | 换热手册/标准待补 | N/A | 空气热物性/换热 | 否 | 是 | 否 | 否 | 需在正式论文中替换为可引用手册或论文。 |
| ENGINEERING_ASSUMPTION | 工程建模假设 | N/A | 倍率、简化几何、初始值、敏感性参数 | 否 | 是 | 否 | 视字段而定 | 所有该来源参数应标记 `sensitivity_required=true`。 |
| ENGINEERING_ASSUMPTION_FROM_MGC_DRAWING | 基于厂家图样读数的几何简化 | MGC图样 | 简化几何 | 是 | 是 | 谨慎 | 否 | 可解释为建模假设，不应作为厂家精确尺寸。 |
| ENGINEERING_ASSUMPTION_FROM_DRAWING | 基于图样读数的厚度估计 | MGC图样 | 简化几何 | 是 | 是 | 谨慎 | 否 | 用于法兰厚度等未明确标注尺寸。 |
| USER_CAD_DWG_DXF_BRFGL1 | 用户提供并转换的BRFGL1-126/1250-4 CAD图 | `/Users/luolin/Desktop/Drawing1.dwg`; `/Users/luolin/Downloads/Drawing1.dxf`; 项目副本 `data/raw_sources/manufacturer_catalogs/cad/BRFGL1-126-1250-4_Drawing1.*` | V2 CAD轮廓驱动几何；空气侧伞裙与油侧过渡外形 | 否 | 否 | 可作为建模图纸来源；正式论文需说明为用户/厂家图纸 | 否 | DXF为单图层，含标注和轮廓混合；脚本按已知BRFGL1尺寸重新标定到真实r-z坐标。 |
| ENGINEERING_ASSUMPTION_FROM_PUBLIC_ALUMINUM_DATA | 铝材公开常识参数占位 | 待替换为材料手册 | 材料参数 | 是 | 是 | 需替换后才适合 | 否 | 需敏感性分析。 |
| USER_REQUIREMENT | 用户课题需求 | 当前对话 | 研究对象与字段需求 | 否 | 否 | 否 | 否 | 定义110/126 kV RIP空气-油电容型变压器套管对象。 |

## COMSOL Initial-Value Rules

`condenser_screens.csv`中的S01-S09 `potential_kV`字段只用于COMSOL求解初值，不得作为固定电位边界。实现时应使用：

1. S00：固定高压电位 `Electric Potential`；
2. S10及法兰：`Ground`；
3. S01-S09：若电容屏作为导体薄层/域建模，用 `Floating Potential` 并约束总电荷为零；若仅作为介质界面边界处理，用 `Zero Charge` 或电绝缘边界，`potential_kV`只作为初始值。

## Generated Data Files

| 文件 | 修订状态 |
| --- | --- |
| `data/processed/operating_cases_steady.csv` | 已按0.6、0.8、1.0、1.2、1.4 p.u. steady负荷倍率生成，不含25 p.u. |
| `data/processed/short_time_transient_cases.csv` | 已单独包含31.25 kA / 2 s短时热稳定工况。 |
| `data/processed/contact_resistance_model.csv` | 已包含Rc_factor 1、2、5、10、20。 |
| `data/processed/materials.csv` | 已增加tan_delta、铜电阻温度系数、RIP温度beta和老化/tan_delta倍率；占位假设均标记`sensitivity_required=true`。 |
| `data/processed/geometry_axisym.csv` | 已区分爬距和轴向总长度，并标记混合800 A外形/1250 A导体半径为`hybrid_parametric_model=true`。 |
| `data/processed/condenser_screens.csv` | 已增加`is_fixed_potential`和COMSOL浮置/零电荷实现说明。 |
| `data/processed/weather_hourly.csv` | 已生成沈阳2025全年8760小时Open-Meteo数据，含降水字段。 |
| `data/processed/weather_typical_days.csv` | 已按`extreme_hot_day`、`extreme_cold_day`、`high_solar_low_wind_day`、`high_humidity_day`、`annual_typical_day`生成5类典型日。 |
| `data/processed/validation_targets.csv` | 已补齐短时131 degC、导体180 degC、72.75 kV基准电压、网格无关性和基准待校准目标。 |
| `data/processed/output_metrics.csv` | 已新增输出指标模板。 |
| `data/processed/selected_model.yml` | 已新增BRFGL1主模型与BRFGL2备选模型防混淆声明。 |
| `data/processed/cad_extract/brfgl1_cad_v2_air_profile.csv` | 已由`Drawing1.dxf`提取并按L1=1150 mm、D2/2=135 mm标定为空气侧V2外轮廓条带。 |
| `data/processed/cad_extract/brfgl1_cad_v2_oil_profile.csv` | 已由`Drawing1.dxf`提取并按L2=595 mm、D1/2=66 mm标定为油侧V2过渡条带。 |
| `comsol/BRFGL1-126-1250-4_geometry_axisym.mph` | 已生成当前几何基准，包含`comp_v1`、`comp_v2`和`comp_v2_cad_solid_preview`三套组件。 |
| `results/paper_figures/brfgl1_geometry_v2_cad_solid_preview.png` | 已生成不含空气/油外部域的CAD实体预览图，用于结构审查和与`Drawing1.dxf`视觉对照。 |
| `results/summary_tables/brfgl1_domain_boundary_selection_mapping.csv` | 已更新至三组件selection映射，`v1_`、`v2_`和`pv_`前缀分别对应快速、仿真和实体预览组件。 |

## Core-Citation Policy

`materials.csv`包含`not_for_core_citation`字段。凡满足以下任一条件的材料参数均标记为`true`：来自工程假设、具体数据表待补、仅作COMSOL初值、或来自任务说明2要求不作为SCI正文核心来源的开放网页/MDPI开源论文。正式论文中应优先用标准文本、厂家正式样本、材料手册、试验数据或同行评议文献替换这些核心数值来源。
