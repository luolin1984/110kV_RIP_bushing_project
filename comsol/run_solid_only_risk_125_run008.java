import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Locale;

public class run_solid_only_risk_125_run008 {

  private static String projectRoot = ".";
  private static final String RUN_ID = "SOLID_ONLY_RISK_125_RUN008";
  private static final String COMP = "comp_v3_solid_solver";

  private static final double[] LOADS = new double[]{0.6, 0.8, 1.0, 1.2, 1.4};
  private static final double[] OIL_TEMPS = new double[]{65.0, 75.0, 85.0, 95.0, 105.0};
  private static final double[] RC_FACTORS = new double[]{1.0, 2.0, 5.0, 10.0, 20.0};
  private static final int MAX_CASES = 125;
  private static final String[] resultCaseId = new String[MAX_CASES];
  private static final double[] resultLoad = new double[MAX_CASES];
  private static final double[] resultOilTemp = new double[MAX_CASES];
  private static final double[] resultRcFactor = new double[MAX_CASES];
  private static final double[] resultTmaxGlobal = new double[MAX_CASES];
  private static final double[] resultTmaxContact = new double[MAX_CASES];
  private static final String[] resultStatus = new String[MAX_CASES];
  private static final String[] resultRiskZone = new String[MAX_CASES];
  private static final String[] resultContactRiskZone = new String[MAX_CASES];
  private static final boolean[] resultOverallValid = new boolean[MAX_CASES];
  private static int resultCount = 0;

  public static void main(String[] args) throws IOException {
    projectRoot = resolveProjectRoot(args);
    File physicsModel = new File(projectRoot, "comsol/BRFGL1-126-1250-4_solid_only_physics.mph");
    if (!physicsModel.exists()) {
      throw new IOException("Missing solid-only physics model: " + physicsModel.getPath());
    }
    File outDir = new File(projectRoot, "results/raw_comsol_exports/" + RUN_ID);
    outDir.mkdirs();

    Model model = ModelUtil.load("Model", physicsModel.getPath());
    model.label("BRFGL1-126-1250-4_solid_only_risk_125_RUN008.mph");
    setFixedParameters(model);
    model.component(COMP).mesh("mesh_solid").run();

    BufferedWriter caseWriter = writer(outDir, "risk_case_matrix.csv");
    BufferedWriter metricsWriter = writer(outDir, "risk_metrics.csv");
    BufferedWriter sourceWriter = writer(outDir, "heat_source_decomposition_by_case.csv");
    BufferedWriter balanceWriter = writer(outDir, "heat_balance_by_case.csv");
    BufferedWriter validityWriter = writer(outDir, "risk_validity_summary.csv");
    BufferedWriter boundaryWriter = writer(outDir, "risk_boundary_summary.csv");
    try {
      writeHeaders(caseWriter, metricsWriter, sourceWriter, balanceWriter, validityWriter, boundaryWriter);
      int idx = 1;
      for (double rc : RC_FACTORS) {
        for (double oil : OIL_TEMPS) {
          for (double load : LOADS) {
            String caseId = String.format(Locale.US, "RUN008_CASE_%03d", idx);
            runCase(model, caseId, load, oil, rc, caseWriter, metricsWriter, sourceWriter, balanceWriter, validityWriter);
            idx++;
          }
        }
      }
      writeRiskBoundarySummary(boundaryWriter);
    } finally {
      caseWriter.close();
      metricsWriter.close();
      sourceWriter.close();
      balanceWriter.close();
      validityWriter.close();
      boundaryWriter.close();
    }
  }

  private static BufferedWriter writer(File outDir, String name) throws IOException {
    return new BufferedWriter(new FileWriter(new File(outDir, name)));
  }

  private static void writeHeaders(BufferedWriter caseWriter, BufferedWriter metricsWriter, BufferedWriter sourceWriter,
      BufferedWriter balanceWriter, BufferedWriter validityWriter, BufferedWriter boundaryWriter) throws IOException {
    caseWriter.write("case_id,run_id,load_multiplier_pu,current_A,oil_temperature_C,air_temperature_C,contact_resistance_multiplier_pu,voltage_multiplier_pu,tan_delta_multiplier_pu,rip_aging_conductivity_multiplier_pu,pollution_multiplier_pu,source_model,notes\n");
    metricsWriter.write("case_id,run_id,status,load_multiplier_pu,current_A,oil_temperature_C,air_temperature_C,contact_resistance_multiplier_pu,Tmax_global_C,Tmax_conductor_C,Tmax_RIP_C,Tmax_contact_C,Tmax_silicone_C,Tmax_flange_C,thermal_warning,thermal_risk,risk_zone,contact_risk_zone,note\n");
    sourceWriter.write("case_id,run_id,Qjoule_conductor_W,Qcontact_W,Qdielectric_RIP_W,Qscreen_loss_W,Qtotal_W,conductor_volume_m3,contact_volume_m3,rip_volume_m3,conductor_cross_section_area_m2,effective_conductor_resistance_ohm,Qjoule_expected_I2R_W,Qcontact_expected_I2Rc_W,Qjoule_relative_error_pct,Qcontact_relative_error_pct,status,notes\n");
    balanceWriter.write("case_id,run_id,Qtotal_generated_W,Qremoved_air_W,Qremoved_oil_W,Qremoved_flange_W,Qremoved_total_W,residual_W,residual_percent,status,notes\n");
    validityWriter.write("case_id,status,valid_temperature,valid_heat_balance,valid_Qjoule,valid_Qcontact,valid_selection,overall_valid,thermal_warning,thermal_risk,failure_reason\n");
    boundaryWriter.write("oil_temperature_C,contact_resistance_multiplier_pu,max_safe_load_multiplier_pu,first_attention_load_multiplier_pu,first_warning_load_multiplier_pu,first_thermal_risk_load_multiplier_pu,Tmax_at_max_safe_load_C,Tmax_contact_at_max_safe_load_C,risk_zone_transition_note\n");
  }

  private static void setFixedParameters(Model model) {
    model.param().set("voltage_mult", "1.0");
    model.param().set("Tair_case", "25[degC]");
    model.param().set("wind_case", "1.0[m/s]");
    model.param().set("tan_delta_multiplier", "1.0");
  }

  private static void runCase(Model model, String caseId, double load, double oilTemp, double rcFactor,
      BufferedWriter caseWriter, BufferedWriter metricsWriter, BufferedWriter sourceWriter,
      BufferedWriter balanceWriter, BufferedWriter validityWriter) throws IOException {
    model.param().set("load_mult", fmt(load));
    model.param().set("Toil_case", fmt(oilTemp) + "[degC]");
    model.param().set("Rc_factor", fmt(rcFactor));
    String solveStatus = "SOLVED";
    String solveNote = "solid-only thermal diagnostic risk scan; by-ID selections; approximate_Qdielectric_ref; not full electro-thermal coupling";
    try {
      model.study("std_solid_ht").run();
    } catch (Throwable t) {
      solveStatus = "SOLVE_FAILED";
      solveNote = clean(t.toString() + " " + t.getMessage());
      System.out.println(caseId + " failed: " + solveNote);
    }

    double current = eval(model, "Icase");
    double tmaxAll = eval(model, "v3_max_T_all(T)-273.15[K]");
    double tmaxConductor = eval(model, "v3_max_T_conductor(T)-273.15[K]");
    double tmaxRip = eval(model, "v3_max_T_rip(T)-273.15[K]");
    double tmaxContact = eval(model, "v3_max_T_contact(T)-273.15[K]");
    double tmaxSilicone = eval(model, "v3_max_T_silicone(T)-273.15[K]");
    double tmaxFlange = eval(model, "v3_max_T_flange(T)-273.15[K]");

    double area = eval(model, "A_conductor");
    double conductorVolume = eval(model, "v3_int_cu_lower(2*pi*r)+v3_int_cu_upper(2*pi*r)");
    double contactVolume = eval(model, "v3_int_contact(2*pi*r)");
    double ripVolume = eval(model, "v3_int_rip(2*pi*r)");
    double qJoule = eval(model, "v3_int_cu_lower(2*pi*r*q_cu_solid)+v3_int_cu_upper(2*pi*r*q_cu_solid)");
    double qContact = eval(model, "v3_int_contact(2*pi*r*q_contact_solid)");
    double qDielectric = eval(model, "v3_int_rip(2*pi*r*Qdielectric_rip_ref)");
    double qScreen = 0.0;
    double qTotal = qJoule + qContact + qDielectric + qScreen;
    double rEff = eval(model, "v3_int_cu_lower(2*pi*r*rho_cu_T/A_conductor^2)+v3_int_cu_upper(2*pi*r*rho_cu_T/A_conductor^2)");
    double qJouleExpected = current * current * rEff;
    double qContactExpected = eval(model, "Icase^2*Rc0*Rc_factor");
    double qJouleErr = relErrPct(qJoule, qJouleExpected);
    double qContactErr = relErrPct(qContact, qContactExpected);

    double heatAir = eval(model, "v3_int_air_bnd(2*pi*r*h_air_case*(T-Tair_case))+v3_int_air_terminal_bnd(2*pi*r*h_air_case*(T-Tair_case))");
    double heatOil = eval(model, "v3_int_oil_bnd(2*pi*r*h_oil_case*(T-Toil_case))");
    double heatFlange = eval(model, "v3_int_flange_bnd(2*pi*r*h_flange_case*(T-Tair_case))");
    double heatRemoved = heatAir + heatOil + heatFlange;
    double residual = qTotal - heatRemoved;
    double residualPct = qTotal != 0.0 ? 100.0 * residual / qTotal : Double.NaN;

    String riskZone = riskZone(tmaxAll);
    String contactRiskZone = contactRiskZone(tmaxContact);
    boolean validTemperature = finite(tmaxAll) && tmaxAll < 150.0;
    boolean validHeatBalance = finite(residualPct) && Math.abs(residualPct) < 10.0;
    boolean validQJoule = finite(qJouleErr) && Math.abs(qJouleErr) < 5.0;
    boolean validQContact = finite(qContactErr) && Math.abs(qContactErr) < 1.0;
    boolean validSelection = !(almostEqual(tmaxConductor, tmaxRip) && almostEqual(tmaxRip, tmaxContact));
    boolean physicsValid = "SOLVED".equals(solveStatus) && validHeatBalance && validQJoule && validQContact && validSelection;
    boolean thermalRisk = physicsValid && finite(tmaxAll) && tmaxAll >= 150.0;
    boolean thermalWarning = physicsValid && finite(tmaxAll) && tmaxAll >= 130.0;
    boolean overallValid = physicsValid && (validTemperature || thermalRisk);
    String status = status(solveStatus, validHeatBalance, validQJoule, validQContact, validSelection, thermalRisk, overallValid);
    String failureReason = failureReason(solveStatus, validTemperature, validHeatBalance, validQJoule, validQContact, validSelection, thermalRisk);
    String heatBalanceNote = heatOil < 0.0
        ? "negative oil heat flux means heat entering from hot oil boundary; 2*pi*r axisymmetric heat-flux weighting"
        : "positive oil heat flux means heat removed to oil boundary; 2*pi*r axisymmetric heat-flux weighting";

    caseWriter.write(String.format(Locale.US, "%s,%s,%.6f,%.9g,%.6f,25.000000,%.6f,1.000000,1.000000,1.000000,1.000000,approximate_Qdielectric_ref,\"source-fixed by-ID solid-only thermal diagnostic risk scan; not full electro-thermal coupling\"%n",
        caseId, RUN_ID, load, current, oilTemp, rcFactor));
    metricsWriter.write(String.format(Locale.US, "%s,%s,%s,%.6f,%.9g,%.6f,25.000000,%.6f,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%s,%s,%s,%s,\"%s\"%n",
        caseId, RUN_ID, status, load, current, oilTemp, rcFactor, tmaxAll, tmaxConductor, tmaxRip,
        tmaxContact, tmaxSilicone, tmaxFlange, bool(thermalWarning), bool(thermalRisk), riskZone,
        contactRiskZone, clean(solveNote)));
    sourceWriter.write(String.format(Locale.US, "%s,%s,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%s,\"2*pi*r source normalization; Qdielectric_RIP_W uses approximate_Qdielectric_ref; contact expected=I^2*Rc0*Rc_factor\"%n",
        caseId, RUN_ID, qJoule, qContact, qDielectric, qScreen, qTotal, conductorVolume, contactVolume,
        ripVolume, area, rEff, qJouleExpected, qContactExpected, qJouleErr, qContactErr, status));
    balanceWriter.write(String.format(Locale.US, "%s,%s,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%s,\"%s\"%n",
        caseId, RUN_ID, qTotal, heatAir, heatOil, heatFlange, heatRemoved, residual, residualPct, status, heatBalanceNote));
    validityWriter.write(String.format(Locale.US, "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\"%s\"%n",
        caseId, status, bool(validTemperature), bool(validHeatBalance), bool(validQJoule), bool(validQContact),
        bool(validSelection), bool(overallValid), bool(thermalWarning), bool(thermalRisk), failureReason));

    storeResult(caseId, load, oilTemp, rcFactor, tmaxAll, tmaxContact, status, riskZone, contactRiskZone, overallValid);
  }

  private static void storeResult(String caseId, double load, double oilTemp, double rcFactor, double tmaxAll,
      double tmaxContact, String status, String riskZone, String contactRiskZone, boolean overallValid) {
    if (resultCount >= MAX_CASES) {
      return;
    }
    resultCaseId[resultCount] = caseId;
    resultLoad[resultCount] = load;
    resultOilTemp[resultCount] = oilTemp;
    resultRcFactor[resultCount] = rcFactor;
    resultTmaxGlobal[resultCount] = tmaxAll;
    resultTmaxContact[resultCount] = tmaxContact;
    resultStatus[resultCount] = status;
    resultRiskZone[resultCount] = riskZone;
    resultContactRiskZone[resultCount] = contactRiskZone;
    resultOverallValid[resultCount] = overallValid;
    resultCount++;
  }

  private static void writeRiskBoundarySummary(BufferedWriter writer) throws IOException {
    for (double oil : OIL_TEMPS) {
      for (double rc : RC_FACTORS) {
        int maxSafe = -1;
        int firstAttention = -1;
        int firstWarning = -1;
        int firstThermalRisk = -1;
        for (double load : LOADS) {
          int result = find(load, oil, rc);
          if (result < 0) {
            continue;
          }
          if ("safe".equals(resultRiskZone[result]) && resultOverallValid[result]) {
            maxSafe = result;
          }
          if (firstAttention < 0 && "attention".equals(resultRiskZone[result])) {
            firstAttention = result;
          }
          if (firstWarning < 0 && "warning".equals(resultRiskZone[result])) {
            firstWarning = result;
          }
          if (firstThermalRisk < 0 && "thermal_risk".equals(resultRiskZone[result])) {
            firstThermalRisk = result;
          }
        }
        String note = transitionNote(oil, rc, maxSafe, firstAttention, firstWarning, firstThermalRisk);
        writer.write(String.format(Locale.US, "%.6f,%.6f,%s,%s,%s,%s,%s,%s,\"%s\"%n",
            oil, rc, loadText(maxSafe), loadText(firstAttention), loadText(firstWarning), loadText(firstThermalRisk),
            tempText(maxSafe < 0 ? Double.NaN : resultTmaxGlobal[maxSafe]),
            tempText(maxSafe < 0 ? Double.NaN : resultTmaxContact[maxSafe]),
            note));
      }
    }
  }

  private static int find(double load, double oil, double rc) {
    for (int i = 0; i < resultCount; i++) {
      if (almostEqual(resultLoad[i], load) && almostEqual(resultOilTemp[i], oil) && almostEqual(resultRcFactor[i], rc)) {
        return i;
      }
    }
    return -1;
  }

  private static String transitionNote(double oil, double rc, int maxSafe, int firstAttention,
      int firstWarning, int firstThermalRisk) {
    StringBuilder sb = new StringBuilder();
    sb.append(String.format(Locale.US, "oil=%.0f C, Rc=%.0f: ", oil, rc));
    if (maxSafe >= 0) {
      sb.append(String.format(Locale.US, "safe up to load %.1f", resultLoad[maxSafe]));
    } else {
      sb.append("no safe load in scanned grid");
    }
    if (firstAttention >= 0) {
      sb.append(String.format(Locale.US, "; first attention %.1f", resultLoad[firstAttention]));
    }
    if (firstWarning >= 0) {
      sb.append(String.format(Locale.US, "; first warning %.1f", resultLoad[firstWarning]));
    }
    if (firstThermalRisk >= 0) {
      sb.append(String.format(Locale.US, "; first thermal_risk %.1f", resultLoad[firstThermalRisk]));
    }
    return sb.toString();
  }

  private static String loadText(int result) {
    if (result < 0) {
      return "NA";
    }
    return String.format(Locale.US, "%.6f", resultLoad[result]);
  }

  private static String tempText(double value) {
    if (!finite(value)) {
      return "NA";
    }
    return String.format(Locale.US, "%.9g", value);
  }

  private static String riskZone(double tmax) {
    if (!finite(tmax)) {
      return "invalid_case";
    }
    if (tmax < 110.0) {
      return "safe";
    }
    if (tmax < 130.0) {
      return "attention";
    }
    if (tmax < 150.0) {
      return "warning";
    }
    return "thermal_risk";
  }

  private static String contactRiskZone(double tmaxContact) {
    if (!finite(tmaxContact)) {
      return "invalid_case";
    }
    if (tmaxContact < 100.0) {
      return "contact_safe";
    }
    if (tmaxContact < 120.0) {
      return "contact_attention";
    }
    if (tmaxContact < 150.0) {
      return "contact_warning";
    }
    return "contact_risk";
  }

  private static String status(String solveStatus, boolean heat, boolean qJoule, boolean qContact, boolean selection,
      boolean thermalRisk, boolean overallValid) {
    if (!"SOLVED".equals(solveStatus)) {
      return "SOLVE_FAILED";
    }
    if (!heat || !qJoule || !qContact || !selection) {
      return "INVALID_CASE";
    }
    if (thermalRisk) {
      return "SOLVED_THERMAL_RISK";
    }
    if (overallValid) {
      return "SOLVED_VALID";
    }
    return "INVALID_CASE";
  }

  private static String failureReason(String solveStatus, boolean temp, boolean heat, boolean qJoule, boolean qContact,
      boolean selection, boolean thermalRisk) {
    if (!"SOLVED".equals(solveStatus)) {
      return "solve_failed";
    }
    StringBuilder sb = new StringBuilder();
    if (!temp && !thermalRisk) append(sb, "temperature");
    if (!heat) append(sb, "heat_balance");
    if (!qJoule) append(sb, "Qjoule");
    if (!qContact) append(sb, "Qcontact");
    if (!selection) append(sb, "selection");
    if (thermalRisk) append(sb, "thermal_risk_not_model_error");
    if (sb.length() == 0) {
      return "";
    }
    return sb.toString();
  }

  private static void append(StringBuilder sb, String value) {
    if (sb.length() > 0) {
      sb.append(";");
    }
    sb.append(value);
  }

  private static double relErrPct(double value, double expected) {
    if (!finite(value) || !finite(expected) || expected == 0.0) {
      return Double.NaN;
    }
    return 100.0 * (value - expected) / expected;
  }

  private static double eval(Model model, String expr) {
    try {
      String tag = "gev_" + Math.abs(expr.hashCode());
      model.result().numerical().create(tag, "EvalGlobal");
      model.result().numerical(tag).set("expr", new String[]{expr});
      double[][] value = model.result().numerical(tag).getReal();
      model.result().numerical().remove(tag);
      if (value.length > 0 && value[0].length > 0) {
        return value[0][0];
      }
    } catch (Throwable t) {
      System.out.println("Eval failed for " + expr + ": " + t.getMessage());
    }
    return Double.NaN;
  }

  private static boolean finite(double value) {
    return !Double.isNaN(value) && !Double.isInfinite(value);
  }

  private static boolean almostEqual(double a, double b) {
    return finite(a) && finite(b) && Math.abs(a - b) < 1.0e-6;
  }

  private static String bool(boolean value) {
    return value ? "true" : "false";
  }

  private static String fmt(double value) {
    return String.format(Locale.US, "%.9g", value);
  }

  private static String clean(String text) {
    if (text == null) {
      return "";
    }
    return text.replace("\"", "'").replace("\n", " ").replace("\r", " ");
  }

  private static String resolveProjectRoot(String[] args) {
    if (args != null && args.length > 0 && args[0] != null && args[0].length() > 0) {
      return new File(args[0]).getAbsolutePath();
    }
    String envRoot = System.getenv("BRFGL1_PROJECT_ROOT");
    if (envRoot != null && envRoot.length() > 0) {
      return new File(envRoot).getAbsolutePath();
    }
    File cwd = new File(System.getProperty("user.dir"));
    if (new File(cwd, "data/processed").exists()) {
      return cwd.getAbsolutePath();
    }
    File candidate = new File(cwd, "110kV_RIP_bushing_project");
    if (new File(candidate, "data/processed").exists()) {
      return candidate.getAbsolutePath();
    }
    return cwd.getAbsolutePath();
  }

}
