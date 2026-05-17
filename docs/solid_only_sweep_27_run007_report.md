# SOLID_ONLY_SWEEP_27_RUN007 阶段报告

## 1. 本轮任务目标

本轮目标是基于 RUN006 已通过的 source-fixed、explicit by-ID、solid-only 热诊断模型，执行 3 x 3 x 3 共 27 组小规模稳态热扫参，检查热源归一化、显式 domain/boundary selection、热量收支和温度响应趋势。本轮没有执行 125 组风险边界扫描，也没有构建完整电热耦合主模型。

## 2. 扫参矩阵

load_multiplier_pu = [0.8, 1.0, 1.2]；oil_temperature_C = [75, 85, 95]；contact_resistance_multiplier_pu = [1, 5, 20]。固定条件为 voltage_multiplier_pu=1.0、air_temperature_C=25、wind_speed_m_s=1.0、tan_delta_multiplier_pu=1.0。

实际输出工况矩阵见 `results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007/sweep_case_matrix.csv`，共 27 组。

## 3. 使用的基准模型

本轮沿用 RUN006 的 source-fixed、by-ID、solid-only thermal diagnostic model。RIP 介质损耗仍采用 approximate_Qdielectric_ref，用于热诊断扫参，不能等同于完整电热耦合模型的真实电场耦合介质损耗。

正式热边界沿用显式 boundary ID selection；导体、RIP、接触层、硅橡胶和法兰等后处理区域沿用显式 domain ID selection。未回退到 Box selection。

## 4. RUN006 基准依据

RUN006 已通过基准热诊断，关键依据为 Tmax_global_C 约 88.42 degC，Qjoule_conductor_W 约 34.01 W，Qcontact_W = 1.5625 W，Qdielectric_RIP_W 约 2.55 W，热量收支 residual_percent 约 -3.25%。RUN007 在此基础上保持热源归一化方式，并按工况更新电流、油温和接触电阻倍率。

## 5. 27 组工况有效性统计

- 求解状态：{'SOLVED_VALID': 27}
- overall_valid：27/27
- valid_temperature：27/27
- valid_heat_balance：27/27
- valid_Qjoule：27/27
- valid_Qcontact：27/27
- valid_selection：27/27
- thermal_warning：0/27

Tmax_global_C 范围为 77.815 至 105.270 degC，Tmax_contact_C 最大值为 101.850 degC。最大热量收支残差绝对值为 7.946%，最大 Qjoule 相对误差绝对值为 7.785e-13%，最大 Qcontact 相对误差绝对值为 8.527e-14%。

## 6. 是否存在无效工况

无效工况数量为 0。无无效工况。

## 7. 热源分解趋势

Qjoule_conductor_W 范围为 21.172 至 53.415 W，并随电流平方增大。Qcontact_W 范围为 1.000 至 45.000 W，满足 Icase^2 * Rc0 * Rc_factor 的缩放关系。Qdielectric_RIP_W 在本轮为 approximate_Qdielectric_ref，数值为 2.545 W。Qjoule 对 I^2 的线性拟合为 Q = 23.401 * (I^2/1e6) - 1.797，R2 = 0.99389。

## 8. 热量收支趋势

27 组工况均满足 abs(residual_percent) < 10%。油侧热通量在部分工况为负，表示 75-95 degC 热油向固体域输入热量；这与当前 solid-only 热诊断边界定义一致。空气侧和法兰侧整体承担散热，热量收支未出现失衡型异常。

## 9. 是否可以进入下一步 125 组风险边界扫描

满足进入 125 组核心风险边界扫描的前置诊断条件；本脚本未执行 125 组扫描，下一阶段仍建议在用户确认后单独启动。

趋势检查结果：

- Tmax 随 oil_temperature_C 升高而升高：True
- Qjoule 随 I^2 增长：True
- Qcontact 随 I^2 * Rc_factor 增长：True
- 高 Rc_factor 下 Tmax_contact 有响应：True

## 10. 若不能进入，需要修正的问题

无需要修正的无效工况；仅需注意本轮是 solid-only 诊断结果。

## 输出文件

- `results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007/sweep_case_matrix.csv`
- `results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007/sweep_metrics.csv`
- `results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007/heat_source_decomposition_by_case.csv`
- `results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007/heat_balance_by_case.csv`
- `results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007/sweep_validity_summary.csv`
- `results/paper_figures/solid_only_sweep_27_run007/fig01_Tmax_vs_load_by_oil_temp.png`
- `results/paper_figures/solid_only_sweep_27_run007/fig02_Tmax_contact_vs_Rc_factor.png`
- `results/paper_figures/solid_only_sweep_27_run007/fig03_heat_source_decomposition_by_load.png`
- `results/paper_figures/solid_only_sweep_27_run007/fig04_heat_balance_residual_by_case.png`
- `results/paper_figures/solid_only_sweep_27_run007/fig05_validity_matrix.png`
- `results/paper_figures/solid_only_sweep_27_run007/fig06_Qcontact_validation.png`
- `results/paper_figures/solid_only_sweep_27_run007/fig07_Qjoule_I2_scaling.png`
