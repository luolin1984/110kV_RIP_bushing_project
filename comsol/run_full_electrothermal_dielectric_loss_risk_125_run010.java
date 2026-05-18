import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Locale;

public class run_full_electrothermal_dielectric_loss_risk_125_run010 {

  private static String projectRoot = ".";
  private static final String RUN_ID = "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010";
  private static final String COMP = "comp_v3_solid_solver";
  private static final double RC0 = 1.0e-6;
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
  private static final String[] resultRiskZone = new String[MAX_CASES];
  private static final String[] resultContactRiskZone = new String[MAX_CASES];
  private static final boolean[] resultOverallValid = new boolean[MAX_CASES];
  private static int resultCount = 0;

  public static void main(String[] args) throws IOException {
    Locale.setDefault(Locale.US);
    projectRoot = resolveProjectRoot(args);
    if (!run009Passed()) {
      throw new IOException("RUN009A/B did not pass; RUN010 is blocked.");
    }
    File modelFile = new File(projectRoot, "comsol/BRFGL1-126-1250-4_full_electrothermal_dielectric_loss_RUN009.mph");
    if (!modelFile.exists()) {
      throw new IOException("Missing RUN009 full electrothermal model: " + modelFile.getPath());
    }
    File outDir = new File(projectRoot, "results/raw_comsol_exports/" + RUN_ID);
    outDir.mkdirs();

    Model model = ModelUtil.load("Model", modelFile.getPath());
    model.label("BRFGL1-126-1250-4_full_electrothermal_dielectric_loss_RISK_125_RUN010.mph");
    setFixedParameters(model);
    model.component(COMP).mesh("mesh_run009").run();

    BufferedWriter caseWriter = writer(outDir, "run010_case_matrix.csv");
    BufferedWriter metricsWriter = writer(outDir, "run010_risk_metrics.csv");
    BufferedWriter fieldWriter = writer(outDir, "electric_field_diagnostics_by_case.csv");
    BufferedWriter dielectricWriter = writer(outDir, "dielectric_loss_by_case.csv");
    BufferedWriter sourceWriter = writer(outDir, "heat_source_decomposition_by_case.csv");
    BufferedWriter balanceWriter = writer(outDir, "heat_balance_by_case.csv");
    BufferedWriter validityWriter = writer(outDir, "run010_validity_summary.csv");
    BufferedWriter boundaryWriter = writer(outDir, "run010_risk_boundary_summary.csv");
    try {
      writeHeaders(caseWriter, metricsWriter, fieldWriter, dielectricWriter, sourceWriter, balanceWriter,
          validityWriter, boundaryWriter);
      int idx = 1;
      for (double rc : RC_FACTORS) {
        for (double oil : OIL_TEMPS) {
          for (double load : LOADS) {
            String caseId = String.format(Locale.US, "RUN010_CASE_%03d", idx);
            runCase(model, caseId, load, oil, rc, caseWriter, metricsWriter, fieldWriter, dielectricWriter,
                sourceWriter, balanceWriter, validityWriter);
            flushAll(caseWriter, metricsWriter, fieldWriter, dielectricWriter, sourceWriter, balanceWriter, validityWriter);
            idx++;
          }
        }
      }
      writeRiskBoundarySummary(boundaryWriter);
    } finally {
      caseWriter.close();
      metricsWriter.close();
      fieldWriter.close();
      dielectricWriter.close();
      sourceWriter.close();
      balanceWriter.close();
      validityWriter.close();
      boundaryWriter.close();
    }
  }

  private static boolean run009Passed() throws IOException {
    File baseline = new File(projectRoot, "results/raw_comsol_exports/FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009A_BASELINE/baseline_metrics.csv");
    File validity = new File(projectRoot, "results/raw_comsol_exports/FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009B_27CASE/run009b_validity_summary.csv");
    if (!baseline.exists() || !validity.exists()) {
      return false;
    }
    boolean baselineOk = false;
    BufferedReader reader = new BufferedReader(new FileReader(baseline));
    try {
      reader.readLine();
      String row = reader.readLine();
      baselineOk = row != null && row.contains(",SOLVED_VALID,");
    } finally {
      reader.close();
    }
    int total = 0;
    int valid = 0;
    reader = new BufferedReader(new FileReader(validity));
    try {
      String header = reader.readLine();
      String line;
      while ((line = reader.readLine()) != null) {
        total++;
        if (line.contains(",true,\"\"") || line.contains(",true,\"thermal_warning_only\"")) {
          valid++;
        }
      }
    } finally {
      reader.close();
    }
    return baselineOk && total == 27 && valid == 27;
  }

  private static void setFixedParameters(Model model) {
    model.param().set("voltage_mult", "1.0");
    model.param().set("Tair_case", "25[degC]");
    model.param().set("wind_case", "1.0[m/s]");
    model.param().set("tan_delta_multiplier", "1.0");
  }

  private static void writeHeaders(BufferedWriter caseWriter, BufferedWriter metricsWriter,
      BufferedWriter fieldWriter, BufferedWriter dielectricWriter, BufferedWriter sourceWriter,
      BufferedWriter balanceWriter, BufferedWriter validityWriter, BufferedWriter boundaryWriter) throws IOException {
    caseWriter.write("case_id,run_id,load_multiplier_pu,current_A,oil_temperature_C,air_temperature_C,contact_resistance_multiplier_pu,voltage_multiplier_pu,tan_delta_multiplier_pu,rip_aging_conductivity_multiplier_pu,pollution_multiplier_pu,source_model,notes\n");
    metricsWriter.write("case_id,run_id,status,load_multiplier_pu,current_A,oil_temperature_C,air_temperature_C,contact_resistance_multiplier_pu,Tmax_global_C,Tmax_conductor_C,Tmax_RIP_C,Tmax_contact_C,Tmax_silicone_C,Tmax_flange_C,Emax_global_V_per_m,Emax_RIP_V_per_m,Emax_RIP_probe_excluding_edges_V_per_m,E95_RIP_V_per_m,Qjoule_conductor_W,Qcontact_W,Qdielectric_RIP_field_W,Qdielectric_RIP_ref_W,Qdielectric_ratio_field_to_ref,Qtotal_W,heat_balance_status,heat_balance_residual_percent,field_singularity_flag,dielectric_loss_review_required,thermal_warning,thermal_risk,risk_zone,contact_risk_zone,note\n");
    fieldWriter.write("case_id,Emax_global_V_per_m,Emax_RIP_V_per_m,Emax_RIP_probe_excluding_edges_V_per_m,E95_RIP_V_per_m,Emean_RIP_V_per_m,field_singularity_flag,screen_end_hotspot_flag,notes\n");
    dielectricWriter.write("case_id,Qdielectric_RIP_ref_W,Qdielectric_RIP_field_W,Qdielectric_ratio_field_to_ref,Qdielectric_min_density_W_m3,Qdielectric_mean_density_W_m3,Qdielectric_max_density_W_m3,integration_method,dielectric_loss_review_required,status,notes\n");
    sourceWriter.write("case_id,Qjoule_conductor_W,Qcontact_W,Qdielectric_RIP_field_W,Qscreen_loss_W,Qtotal_W,Qjoule_expected_I2R_W,Qcontact_expected_I2Rc_W,Qjoule_relative_error_pct,Qcontact_relative_error_pct,status,notes\n");
    balanceWriter.write("case_id,Qtotal_generated_W,Qremoved_air_W,Qremoved_oil_W,Qremoved_flange_W,Qremoved_total_W,residual_W,residual_percent_Qgenerated,residual_percent_max_energy_scale,heat_balance_status,notes\n");
    validityWriter.write("case_id,status,valid_temperature,valid_heat_balance,valid_Qjoule,valid_Qcontact,valid_Qdielectric,valid_selection,field_singularity_flag,dielectric_loss_review_required,thermal_warning,thermal_risk,overall_valid,failure_reason\n");
    boundaryWriter.write("oil_temperature_C,contact_resistance_multiplier_pu,max_safe_load_multiplier_pu,first_attention_load_multiplier_pu,first_warning_load_multiplier_pu,first_thermal_risk_load_multiplier_pu,Tmax_at_max_safe_load_C,Tmax_contact_at_max_safe_load_C,risk_zone_transition_note\n");
  }

  private static void runCase(Model model, String caseId, double load, double oil, double rc,
      BufferedWriter caseWriter, BufferedWriter metricsWriter, BufferedWriter fieldWriter,
      BufferedWriter dielectricWriter, BufferedWriter sourceWriter, BufferedWriter balanceWriter,
      BufferedWriter validityWriter) throws IOException {
    model.param().set("load_mult", fmt(load));
    model.param().set("Toil_case", fmt(oil) + "[degC]");
    model.param().set("Rc_factor", fmt(rc));
    String solveStatus = "SOLVED";
    String solveNote = "RUN010 full field-coupled dielectric-loss 125-case risk scan; by-ID selections; RUN006 source normalization; not final SCI result";
    try {
      model.study("std_cpl_field").run();
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

    double eMaxGlobal = eval(model, "v3_max_E_all(es.normE)");
    double eMaxRip = eval(model, "v3_max_E_rip(es.normE)");
    double eProbe = eval(model, "v3_max_E_rip(if(r>0.034[m],if(r<0.064[m],if(z>-0.50[m],if(z<1.05[m],es.normE,0[V/m]),0[V/m]),0[V/m]),0[V/m]))");
    double eMean = eval(model, "v3_int_rip(2*pi*r*es.normE)/v3_int_rip(2*pi*r)");
    double eRms = eval(model, "sqrt(v3_int_rip(2*pi*r*es.normE^2)/v3_int_rip(2*pi*r))");
    double e95 = Double.NaN;
    if (finite(eMean) && finite(eRms)) {
      e95 = Math.min(finite(eMaxRip) ? eMaxRip : Double.POSITIVE_INFINITY,
          eMean + 1.645 * Math.sqrt(Math.max(0.0, eRms * eRms - eMean * eMean)));
    }
    if (!finite(eProbe) || eProbe <= 0.0) {
      eProbe = finite(e95) ? e95 : eMaxRip;
    }
    boolean fieldSingularity = singularityFlag(eMaxGlobal, eMaxRip, eProbe);
    boolean screenHotspot = finite(eMaxRip) && finite(eProbe) && eProbe > 0.0 && eMaxRip / eProbe > 10.0;
    boolean fieldReview = finite(eMaxGlobal) && finite(e95) && e95 > 0.0 && eMaxGlobal / e95 > 10.0;

    double qJoule = eval(model, "v3_int_cu_lower(2*pi*r*q_cu_solid)+v3_int_cu_upper(2*pi*r*q_cu_solid)");
    double qContact = eval(model, "v3_int_contact(2*pi*r*q_contact_solid)");
    double qDielectricField = eval(model, "v3_int_rip(2*pi*r*Qdielectric_rip_field)");
    double qDielectricRef = eval(model, "v3_int_rip(2*pi*r*Qdielectric_rip_ref)");
    double qDielectricRatio = finite(qDielectricField) && finite(qDielectricRef) && qDielectricRef != 0.0
        ? qDielectricField / qDielectricRef : Double.NaN;
    double qDielectricMinDensity = eval(model, "v3_min_rip(Qdielectric_rip_field)");
    double qDielectricMeanDensity = eval(model, "v3_int_rip(2*pi*r*Qdielectric_rip_field)/v3_int_rip(2*pi*r)");
    double qDielectricMaxDensity = eval(model, "v3_max_E_rip(Qdielectric_rip_field)");
    boolean dielectricReview = finite(qDielectricRatio) && (qDielectricRatio < 0.1 || qDielectricRatio > 10.0);
    boolean invalidDielectricLoss = !finite(qDielectricField) || qDielectricField <= 0.0 || qDielectricField > 1000.0;

    double qScreen = 0.0;
    double qTotal = qJoule + qContact + qDielectricField + qScreen;
    double rEff = eval(model, "v3_int_cu_lower(2*pi*r*rho_cu_T/A_conductor^2)+v3_int_cu_upper(2*pi*r*rho_cu_T/A_conductor^2)");
    double qJouleExpected = current * current * rEff;
    double qContactExpected = current * current * RC0 * rc;
    double qJouleErr = relErrPct(qJoule, qJouleExpected);
    double qContactErr = relErrPct(qContact, qContactExpected);

    double qAir = eval(model, "v3_int_air_bnd(2*pi*r*h_air_case*(T-Tair_case))+v3_int_air_terminal_bnd(2*pi*r*h_air_case*(T-Tair_case))");
    double qOil = eval(model, "v3_int_oil_bnd(2*pi*r*h_oil_case*(T-Toil_case))");
    double qFlange = eval(model, "v3_int_flange_bnd(2*pi*r*h_flange_case*(T-Tair_case))");
    double qRemoved = qAir + qOil + qFlange;
    double residual = qTotal - qRemoved;
    double residualPctQ = qTotal != 0.0 ? 100.0 * residual / qTotal : Double.NaN;
    double maxEnergyScale = Math.max(Math.max(Math.abs(qTotal), Math.abs(qAir) + Math.abs(qOil) + Math.abs(qFlange)), 1.0);
    double residualPctMax = 100.0 * residual / maxEnergyScale;
    String hbStatus = heatBalanceStatus(residualPctQ, residual, residualPctMax);

    String riskZone = riskZone(tmaxAll);
    String contactRiskZone = contactRiskZone(tmaxContact);
    boolean validTemperature = finite(tmaxAll) && tmaxAll < 150.0;
    boolean validHeat = "VALID_STRICT".equals(hbStatus) || "VALID_LOW_POWER_RECLASSIFIED".equals(hbStatus);
    boolean validQJoule = finite(qJouleErr) && Math.abs(qJouleErr) < 5.0;
    boolean validQContact = finite(qContactErr) && Math.abs(qContactErr) < 1.0;
    boolean validQDielectric = !invalidDielectricLoss;
    boolean validSelection = !(almostEqual(tmaxConductor, tmaxRip) && almostEqual(tmaxRip, tmaxContact));
    boolean physicsValid = "SOLVED".equals(solveStatus) && validHeat && validQJoule && validQContact
        && validQDielectric && validSelection && !fieldSingularity;
    boolean thermalRisk = physicsValid && finite(tmaxAll) && tmaxAll >= 150.0;
    boolean thermalWarning = physicsValid && finite(tmaxAll) && tmaxAll >= 130.0;
    boolean overallValid = physicsValid && (validTemperature || thermalRisk);
    String status = caseStatus(solveStatus, overallValid, thermalWarning, thermalRisk);
    String failureReason = failureReason(solveStatus, validTemperature, validHeat, validQJoule, validQContact,
        validQDielectric, validSelection, fieldSingularity, thermalRisk);
    String dielectricNote = dielectricReview
        ? "DIELECTRIC_LOSS_REVIEW_REQUIRED: Qdielectric_field/ref outside [0.1,10]; review flag is not model failure"
        : "field-coupled dielectric loss ratio within nominal review interval";
    if (invalidDielectricLoss) {
      dielectricNote = "invalid_dielectric_loss: Qdielectric_field nonpositive or abnormally large";
    }
    String fieldNote = fieldReview ? "field_review_required: Emax_global/E95_RIP > 10" : "field diagnostics stable";

    caseWriter.write(String.format(Locale.US, "%s,%s,%.6f,%.9g,%.6f,25.000000,%.6f,1.000000,1.000000,1.000000,1.000000,field_coupled_Qdielectric,\"full electrostatic field-coupled dielectric loss risk scan; not final SCI result\"%n",
        caseId, RUN_ID, load, current, oil, rc));
    metricsWriter.write(String.format(Locale.US, "%s,%s,%s,%.6f,%.9g,%.6f,25.000000,%.6f,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%s,%.9g,%s,%s,%s,%s,%s,%s,\"%s\"%n",
        caseId, RUN_ID, status, load, current, oil, rc, tmaxAll, tmaxConductor, tmaxRip, tmaxContact,
        tmaxSilicone, tmaxFlange, eMaxGlobal, eMaxRip, eProbe, e95, qJoule, qContact,
        qDielectricField, qDielectricRef, qDielectricRatio, qTotal, hbStatus, residualPctQ,
        bool(fieldSingularity), bool(dielectricReview), bool(thermalWarning), bool(thermalRisk), riskZone,
        contactRiskZone, clean(solveNote + "; " + dielectricNote)));
    fieldWriter.write(String.format(Locale.US, "%s,%.9g,%.9g,%.9g,%.9g,%.9g,%s,%s,\"%s\"%n",
        caseId, eMaxGlobal, eMaxRip, eProbe, e95, eMean, bool(fieldSingularity), bool(screenHotspot), fieldNote));
    dielectricWriter.write(String.format(Locale.US, "%s,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,axisymmetric_2pi_r_RIP_domain_integral,%s,%s,\"%s\"%n",
        caseId, qDielectricRef, qDielectricField, qDielectricRatio, qDielectricMinDensity,
        qDielectricMeanDensity, qDielectricMaxDensity, bool(dielectricReview), status, dielectricNote));
    sourceWriter.write(String.format(Locale.US, "%s,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%s,\"RUN006 source normalization retained; Qcontact=I^2*Rc0*Rc_factor; Qdielectric uses field-coupled es.normE\"%n",
        caseId, qJoule, qContact, qDielectricField, qScreen, qTotal, qJouleExpected, qContactExpected,
        qJouleErr, qContactErr, status));
    balanceWriter.write(String.format(Locale.US, "%s,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%s,\"RUN008B heat-balance classification retained; negative oil term means heat enters solid from hot oil\"%n",
        caseId, qTotal, qAir, qOil, qFlange, qRemoved, residual, residualPctQ, residualPctMax, hbStatus));
    validityWriter.write(String.format(Locale.US, "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\"%s\"%n",
        caseId, status, bool(validTemperature), bool(validHeat), bool(validQJoule), bool(validQContact),
        bool(validQDielectric), bool(validSelection), bool(fieldSingularity), bool(dielectricReview),
        bool(thermalWarning), bool(thermalRisk), bool(overallValid), failureReason));

    storeResult(caseId, load, oil, rc, tmaxAll, tmaxContact, riskZone, contactRiskZone, overallValid);
    System.out.println(caseId + " " + status + " Tmax=" + fmt(tmaxAll) + " Qd=" + fmt(qDielectricField)
        + " hb=" + hbStatus + " risk=" + riskZone);
  }

  private static void storeResult(String caseId, double load, double oil, double rc, double tmaxAll,
      double tmaxContact, String riskZone, String contactRiskZone, boolean overallValid) {
    if (resultCount >= MAX_CASES) {
      return;
    }
    resultCaseId[resultCount] = caseId;
    resultLoad[resultCount] = load;
    resultOilTemp[resultCount] = oil;
    resultRcFactor[resultCount] = rc;
    resultTmaxGlobal[resultCount] = tmaxAll;
    resultTmaxContact[resultCount] = tmaxContact;
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
          if (result < 0 || !resultOverallValid[result]) {
            continue;
          }
          if ("safe".equals(resultRiskZone[result])) {
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
        writer.write(String.format(Locale.US, "%.6f,%.6f,%s,%s,%s,%s,%s,%s,\"%s\"%n",
            oil, rc, loadText(maxSafe), loadText(firstAttention), loadText(firstWarning),
            loadText(firstThermalRisk), tempText(maxSafe < 0 ? Double.NaN : resultTmaxGlobal[maxSafe]),
            tempText(maxSafe < 0 ? Double.NaN : resultTmaxContact[maxSafe]),
            transitionNote(oil, rc, maxSafe, firstAttention, firstWarning, firstThermalRisk)));
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

  private static String contactRiskZone(double tmax) {
    if (!finite(tmax)) {
      return "invalid_case";
    }
    if (tmax < 100.0) {
      return "contact_safe";
    }
    if (tmax < 120.0) {
      return "contact_attention";
    }
    if (tmax < 150.0) {
      return "contact_warning";
    }
    return "contact_risk";
  }

  private static String caseStatus(String solveStatus, boolean overallValid, boolean thermalWarning, boolean thermalRisk) {
    if (!"SOLVED".equals(solveStatus)) {
      return "SOLVE_FAILED";
    }
    if (thermalRisk) {
      return "SOLVED_THERMAL_RISK";
    }
    if (thermalWarning) {
      return "SOLVED_THERMAL_WARNING";
    }
    return overallValid ? "SOLVED_VALID" : "INVALID_CASE";
  }

  private static String failureReason(String solveStatus, boolean temp, boolean heat, boolean qJoule,
      boolean qContact, boolean qDielectric, boolean selection, boolean fieldSingularity, boolean thermalRisk) {
    if (!"SOLVED".equals(solveStatus)) {
      return "solve_failed";
    }
    if (thermalRisk) {
      return "thermal_risk_only";
    }
    StringBuilder sb = new StringBuilder();
    if (!temp) append(sb, "temperature");
    if (!heat) append(sb, "heat_balance");
    if (!qJoule) append(sb, "Qjoule");
    if (!qContact) append(sb, "Qcontact");
    if (!qDielectric) append(sb, "Qdielectric");
    if (!selection) append(sb, "selection");
    if (fieldSingularity) append(sb, "field_singularity");
    return sb.length() == 0 ? "" : sb.toString();
  }

  private static String heatBalanceStatus(double residualPctQ, double residualW, double residualPctMax) {
    if (finite(residualPctQ) && Math.abs(residualPctQ) < 10.0) {
      return "VALID_STRICT";
    }
    if (finite(residualW) && finite(residualPctMax) && Math.abs(residualW) < 3.0 && Math.abs(residualPctMax) < 5.0) {
      return "VALID_LOW_POWER_RECLASSIFIED";
    }
    return "INVALID_HEAT_BALANCE";
  }

  private static boolean singularityFlag(double eGlobal, double eRip, double eProbe) {
    if (!finite(eGlobal) || !finite(eRip) || !finite(eProbe) || eProbe <= 0.0) {
      return true;
    }
    return eGlobal / eProbe > 20.0 || eRip / eProbe > 20.0;
  }

  private static double eval(Model model, String expr) {
    try {
      String tag = "gev_run010_" + Math.abs(expr.hashCode());
      model.result().numerical().create(tag, "EvalGlobal");
      model.result().numerical(tag).set("expr", new String[]{expr});
      try {
        model.result().numerical(tag).set("data", "dset2");
      } catch (Throwable ignored) {
      }
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

  private static BufferedWriter writer(File outDir, String name) throws IOException {
    return new BufferedWriter(new FileWriter(new File(outDir, name)));
  }

  private static void flushAll(BufferedWriter a, BufferedWriter b, BufferedWriter c, BufferedWriter d,
      BufferedWriter e, BufferedWriter f, BufferedWriter g) throws IOException {
    a.flush();
    b.flush();
    c.flush();
    d.flush();
    e.flush();
    f.flush();
    g.flush();
  }

  private static void append(StringBuilder sb, String value) {
    if (sb.length() > 0) {
      sb.append(";");
    }
    sb.append(value);
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

  private static double relErrPct(double value, double expected) {
    if (!finite(value) || !finite(expected) || expected == 0.0) {
      return Double.NaN;
    }
    return 100.0 * (value - expected) / expected;
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
