import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Locale;
import java.util.Properties;

public class run_material_and_mesh_sensitivity_run011 {

  private static String projectRoot = ".";
  private static final String RUN_ID = "MATERIAL_AND_MESH_SENSITIVITY_RUN011";
  private static final String RUN011A = "RUN011A_MESH_INDEPENDENCE";
  private static final String RUN011B = "RUN011B_MATERIAL_BOUNDARY_SENSITIVITY";
  private static final String COMP = "comp_v3_solid_solver";
  private static final String MESH = "mesh_run009";
  private static final double RC0 = 1.0e-6;
  private static int evalCounter = 0;

  private static final String[] MESH_LEVELS = new String[]{"coarse", "medium", "fine"};
  private static final int[] MESH_AUTO_SIZES = new int[]{9, 8, 6};
  private static final String[] MESH_CASES = new String[]{"CASE_A_BASELINE", "CASE_B_HIGH_CONTACT", "CASE_C_HIGHEST_PRESSURE"};
  private static final double[] MESH_LOADS = new double[]{1.0, 1.2, 1.4};
  private static final double[] MESH_OILS = new double[]{85.0, 95.0, 105.0};
  private static final double[] MESH_RCS = new double[]{1.0, 20.0, 20.0};

  private static final String[] SENS_BASE_CASES = new String[]{"SENS_BASELINE", "SENS_HIGH_RISK"};
  private static final double[] SENS_LOADS = new double[]{1.0, 1.4};
  private static final double[] SENS_OILS = new double[]{85.0, 105.0};
  private static final double[] SENS_RCS = new double[]{1.0, 20.0};

  public static void main(String[] args) throws IOException {
    Locale.setDefault(Locale.US);
    projectRoot = resolveProjectRoot(args);
    if (!run010Passed()) {
      throw new IOException("RUN010 did not pass; RUN011 is blocked.");
    }
    File modelFile = new File(projectRoot, "comsol/BRFGL1-126-1250-4_full_electrothermal_dielectric_loss_RUN009.mph");
    if (!modelFile.exists()) {
      throw new IOException("Missing RUN009 field-coupled model: " + modelFile.getPath());
    }

    File outA = new File(projectRoot, "results/raw_comsol_exports/" + RUN_ID + "/" + RUN011A);
    File outB = new File(projectRoot, "results/raw_comsol_exports/" + RUN_ID + "/" + RUN011B);
    outA.mkdirs();
    outB.mkdirs();

    Model model = ModelUtil.load("Model", modelFile.getPath());
    model.label("BRFGL1-126-1250-4_material_and_mesh_sensitivity_RUN011.mph");
    prepareRun011Model(model);

    runMeshIndependence(model, outA);
    runSensitivity(model, outB);

    model.save(path("comsol/BRFGL1-126-1250-4_material_and_mesh_sensitivity_RUN011.mph"));
  }

  private static boolean run010Passed() throws IOException {
    File validity = new File(projectRoot,
        "results/raw_comsol_exports/FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010/run010_validity_summary.csv");
    if (!validity.exists()) {
      return false;
    }
    BufferedReader reader = new BufferedReader(new FileReader(validity));
    int total = 0;
    int valid = 0;
    try {
      String header = reader.readLine();
      String line;
      while ((line = reader.readLine()) != null) {
        total++;
        String[] parts = line.split(",", -1);
        if (parts.length >= 13 && "true".equalsIgnoreCase(parts[12])) {
          valid++;
        }
      }
    } finally {
      reader.close();
    }
    return total == 125 && valid == 125;
  }

  private static void prepareRun011Model(Model model) {
    setCommonDefaults(model);
    model.param().set("k_RIP_multiplier", "1");
    model.param().set("Rc0_multiplier", "1");
    try {
      model.component(COMP).material("mat_v3_rip").propertyGroup("def")
          .set("thermalconductivity", new String[]{"0.20[W/(m*K)]*k_RIP_multiplier"});
    } catch (Throwable t) {
      System.out.println("Could not set RIP thermal-conductivity multiplier: " + t.getMessage());
    }
    try {
      model.component(COMP).variable("var_run009_heat")
          .set("q_contact_solid", "Icase^2*Rc0*Rc0_multiplier*Rc_factor/V_contact");
    } catch (Throwable t) {
      System.out.println("Could not set Rc0 multiplier in contact heat source: " + t.getMessage());
    }
  }

  private static void setCommonDefaults(Model model) {
    model.param().set("voltage_mult", "1.0");
    model.param().set("Tair_case", "25[degC]");
    model.param().set("wind_case", "1.0[m/s]");
    model.param().set("tan_delta_multiplier", "1.0");
    model.param().set("epsr_rip", "4.2");
    model.param().set("k_RIP_multiplier", "1.0");
    model.param().set("Rc0_multiplier", "1.0");
    model.param().set("h_air_case", "20[W/(m^2*K)]");
    model.param().set("h_oil_case", "300[W/(m^2*K)]");
    model.param().set("h_flange_case", "20[W/(m^2*K)]");
  }

  private static void runMeshIndependence(Model model, File outDir) throws IOException {
    BufferedWriter caseWriter = writer(outDir, "mesh_case_matrix.csv");
    BufferedWriter metricsWriter = writer(outDir, "mesh_metrics.csv");
    try {
      caseWriter.write("case_id,mesh_level,auto_mesh_size,load_multiplier_pu,current_A,oil_temperature_C,air_temperature_C,contact_resistance_multiplier_pu,voltage_multiplier_pu,tan_delta_multiplier_pu,source_model,notes\n");
      metricsWriter.write("case_id,mesh_level,element_count,vertex_count,dof_count,min_element_quality,Tmax_global_C,Tmax_conductor_C,Tmax_RIP_C,Tmax_contact_C,Emax_RIP_probe_excluding_edges_V_per_m,E95_RIP_V_per_m,Qjoule_conductor_W,Qcontact_W,Qdielectric_RIP_field_W,Qtotal_W,heat_balance_residual_percent,heat_balance_status,field_singularity_flag,status\n");
      for (int mi = 0; mi < MESH_LEVELS.length; mi++) {
        String meshLevel = MESH_LEVELS[mi];
        int autoSize = MESH_AUTO_SIZES[mi];
        model.component(COMP).mesh(MESH).autoMeshSize(autoSize);
        model.component(COMP).mesh(MESH).run();
        for (int ci = 0; ci < MESH_CASES.length; ci++) {
          setCommonDefaults(model);
          model.param().set("load_mult", fmt(MESH_LOADS[ci]));
          model.param().set("Toil_case", fmt(MESH_OILS[ci]) + "[degC]");
          model.param().set("Rc_factor", fmt(MESH_RCS[ci]));
          String caseId = MESH_CASES[ci];
          Properties m = solveAndMeasure(model, caseId, "RUN011A mesh independence; autoMeshSize=" + autoSize);
          int elemCount = meshElementCount(model);
          int vertexCount = meshVertexCount(model);
          int dofCount = dofCount(model);
          double minQuality = meshMinQuality(model);
          caseWriter.write(String.format(Locale.US, "%s,%s,%d,%.6f,%.9g,%.6f,25.000000,%.6f,1.000000,1.000000,field_coupled_Qdielectric,\"RUN011A mesh independence; medium autoMeshSize=8 follows RUN010\"%n",
              caseId, meshLevel, autoSize, MESH_LOADS[ci], d(m, "current"), MESH_OILS[ci], MESH_RCS[ci]));
          metricsWriter.write(String.format(Locale.US, "%s,%s,%d,%d,%d,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%s,%s,%s%n",
              caseId, meshLevel, elemCount, vertexCount, dofCount, minQuality, d(m, "tmaxAll"), d(m, "tmaxConductor"),
              d(m, "tmaxRip"), d(m, "tmaxContact"), d(m, "eProbe"), d(m, "e95"), d(m, "qJoule"), d(m, "qContact"), d(m, "qDielectricField"),
              d(m, "qTotal"), d(m, "residualPctQ"), s(m, "heatBalanceStatus"), bool(b(m, "fieldSingularity")), s(m, "status")));
          caseWriter.flush();
          metricsWriter.flush();
          System.out.println("RUN011A " + caseId + " " + meshLevel + " " + s(m, "status")
              + " Tmax=" + fmt(d(m, "tmaxAll")) + " Qd=" + fmt(d(m, "qDielectricField")));
        }
      }
    } finally {
      caseWriter.close();
      metricsWriter.close();
    }
  }

  private static void runSensitivity(Model model, File outDir) throws IOException {
    model.component(COMP).mesh(MESH).autoMeshSize(8);
    model.component(COMP).mesh(MESH).run();

    BufferedWriter caseWriter = writer(outDir, "sensitivity_case_matrix.csv");
    BufferedWriter metricsWriter = writer(outDir, "sensitivity_metrics.csv");
    try {
      caseWriter.write("sensitivity_case_id,base_case,parameter_name,parameter_value,parameter_multiplier,load_multiplier_pu,current_A,oil_temperature_C,air_temperature_C,contact_resistance_multiplier_pu,voltage_multiplier_pu,source_model,notes\n");
      metricsWriter.write("sensitivity_case_id,base_case,parameter_name,parameter_value,parameter_multiplier,Tmax_global_C,Tmax_conductor_C,Tmax_RIP_C,Tmax_contact_C,E95_RIP_V_per_m,Qjoule_conductor_W,Qcontact_W,Qdielectric_RIP_field_W,Qtotal_W,risk_zone,contact_risk_zone,heat_balance_status,field_singularity_flag,dielectric_loss_review_required,status\n");
      int idx = 1;
      for (int base = 0; base < SENS_BASE_CASES.length; base++) {
        idx = runSensitivityFamily(model, caseWriter, metricsWriter, idx, base, "k_RIP_multiplier", new double[]{0.8, 1.0, 1.2}, 1.0, "multiplier");
        idx = runSensitivityFamily(model, caseWriter, metricsWriter, idx, base, "tan_delta_multiplier", new double[]{0.5, 1.0, 2.0, 5.0}, 1.0, "multiplier");
        idx = runSensitivityFamily(model, caseWriter, metricsWriter, idx, base, "epsr_RIP", new double[]{3.5, 4.2, 4.5}, 4.2, "absolute");
        idx = runSensitivityFamily(model, caseWriter, metricsWriter, idx, base, "h_oil", new double[]{100.0, 300.0, 500.0}, 300.0, "absolute_W_m2K");
        idx = runSensitivityFamily(model, caseWriter, metricsWriter, idx, base, "h_air", new double[]{5.0, 10.0, 20.0}, 20.0, "absolute_W_m2K");
        idx = runSensitivityFamily(model, caseWriter, metricsWriter, idx, base, "Rc0_multiplier", new double[]{0.5, 1.0, 2.0}, 1.0, "multiplier");
      }
    } finally {
      caseWriter.close();
      metricsWriter.close();
    }
  }

  private static int runSensitivityFamily(Model model, BufferedWriter caseWriter, BufferedWriter metricsWriter,
      int idx, int baseIndex, String parameterName, double[] values, double baselineValue, String valueMode)
      throws IOException {
    for (int i = 0; i < values.length; i++) {
      String sensitivityCaseId = String.format(Locale.US, "RUN011B_CASE_%03d", idx);
      setSensitivityBase(model, baseIndex);
      applySensitivityParameter(model, parameterName, values[i]);
      Properties m = solveAndMeasure(model, sensitivityCaseId,
          "RUN011B OFAT sensitivity; parameter=" + parameterName);
      double multiplier = values[i] / baselineValue;
      caseWriter.write(String.format(Locale.US, "%s,%s,%s,%.9g,%.9g,%.6f,%.9g,%.6f,25.000000,%.6f,1.000000,field_coupled_Qdielectric,\"%s; one-factor-at-a-time; not final SCI result\"%n",
          sensitivityCaseId, SENS_BASE_CASES[baseIndex], parameterName, values[i], multiplier,
          SENS_LOADS[baseIndex], d(m, "current"), SENS_OILS[baseIndex], SENS_RCS[baseIndex], valueMode));
      metricsWriter.write(String.format(Locale.US, "%s,%s,%s,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%s,%s,%s,%s,%s,%s%n",
          sensitivityCaseId, SENS_BASE_CASES[baseIndex], parameterName, values[i], multiplier,
          d(m, "tmaxAll"), d(m, "tmaxConductor"), d(m, "tmaxRip"), d(m, "tmaxContact"), d(m, "e95"), d(m, "qJoule"), d(m, "qContact"),
          d(m, "qDielectricField"), d(m, "qTotal"), riskZone(d(m, "tmaxAll")), contactRiskZone(d(m, "tmaxContact")),
          s(m, "heatBalanceStatus"), bool(b(m, "fieldSingularity")), bool(b(m, "dielectricReviewRequired")), s(m, "status")));
      caseWriter.flush();
      metricsWriter.flush();
      System.out.println("RUN011B " + sensitivityCaseId + " " + SENS_BASE_CASES[baseIndex] + " "
          + parameterName + "=" + fmt(values[i]) + " " + s(m, "status") + " Tmax=" + fmt(d(m, "tmaxAll")));
      idx++;
    }
    return idx;
  }

  private static void setSensitivityBase(Model model, int baseIndex) {
    setCommonDefaults(model);
    model.param().set("load_mult", fmt(SENS_LOADS[baseIndex]));
    model.param().set("Toil_case", fmt(SENS_OILS[baseIndex]) + "[degC]");
    model.param().set("Rc_factor", fmt(SENS_RCS[baseIndex]));
  }

  private static void applySensitivityParameter(Model model, String parameterName, double value) {
    if ("k_RIP_multiplier".equals(parameterName)) {
      model.param().set("k_RIP_multiplier", fmt(value));
    } else if ("tan_delta_multiplier".equals(parameterName)) {
      model.param().set("tan_delta_multiplier", fmt(value));
    } else if ("epsr_RIP".equals(parameterName)) {
      model.param().set("epsr_rip", fmt(value));
    } else if ("h_oil".equals(parameterName)) {
      model.param().set("h_oil_case", fmt(value) + "[W/(m^2*K)]");
    } else if ("h_air".equals(parameterName)) {
      model.param().set("h_air_case", fmt(value) + "[W/(m^2*K)]");
    } else if ("Rc0_multiplier".equals(parameterName)) {
      model.param().set("Rc0_multiplier", fmt(value));
    }
  }

  private static Properties solveAndMeasure(Model model, String caseId, String note) {
    Properties m = new Properties();
    m.setProperty("solveStatus", "SOLVED");
    try {
      model.study("std_cpl_field").run();
    } catch (Throwable t) {
      m.setProperty("solveStatus", "SOLVE_FAILED");
      m.setProperty("note", clean(t.toString() + " " + t.getMessage()));
      System.out.println(caseId + " solve failed: " + s(m, "note"));
    }

    setD(m, "current", eval(model, "Icase"));
    setD(m, "tmaxAll", eval(model, "v3_max_T_all(T)-273.15[K]"));
    setD(m, "tmaxConductor", eval(model, "v3_max_T_conductor(T)-273.15[K]"));
    setD(m, "tmaxRip", eval(model, "v3_max_T_rip(T)-273.15[K]"));
    setD(m, "tmaxContact", eval(model, "v3_max_T_contact(T)-273.15[K]"));
    setD(m, "eMaxGlobal", eval(model, "v3_max_E_all(es.normE)"));
    setD(m, "eMaxRip", eval(model, "v3_max_E_rip(es.normE)"));
    setD(m, "eProbe", eval(model, "v3_max_E_rip(if(r>0.034[m],if(r<0.064[m],if(z>-0.50[m],if(z<1.05[m],es.normE,0[V/m]),0[V/m]),0[V/m]),0[V/m]))"));
    setD(m, "eMean", eval(model, "v3_int_rip(2*pi*r*es.normE)/v3_int_rip(2*pi*r)"));
    double eRms = eval(model, "sqrt(v3_int_rip(2*pi*r*es.normE^2)/v3_int_rip(2*pi*r))");
    if (finite(d(m, "eMean")) && finite(eRms)) {
      setD(m, "e95", Math.min(finite(d(m, "eMaxRip")) ? d(m, "eMaxRip") : Double.POSITIVE_INFINITY,
          d(m, "eMean") + 1.645 * Math.sqrt(Math.max(0.0, eRms * eRms - d(m, "eMean") * d(m, "eMean")))));
    }
    if (!finite(d(m, "eProbe")) || d(m, "eProbe") <= 0.0) {
      setD(m, "eProbe", finite(d(m, "e95")) ? d(m, "e95") : d(m, "eMaxRip"));
    }

    setD(m, "qJoule", eval(model, "v3_int_cu_lower(2*pi*r*q_cu_solid)+v3_int_cu_upper(2*pi*r*q_cu_solid)"));
    setD(m, "qContact", eval(model, "v3_int_contact(2*pi*r*q_contact_solid)"));
    setD(m, "qDielectricField", eval(model, "v3_int_rip(2*pi*r*Qdielectric_rip_field)"));
    setD(m, "qDielectricRef", eval(model, "v3_int_rip(2*pi*r*Qdielectric_rip_ref)"));
    setD(m, "qDielectricRatio", finite(d(m, "qDielectricField")) && finite(d(m, "qDielectricRef")) && d(m, "qDielectricRef") != 0.0
        ? d(m, "qDielectricField") / d(m, "qDielectricRef") : Double.NaN);
    setD(m, "qTotal", d(m, "qJoule") + d(m, "qContact") + d(m, "qDielectricField"));
    double rEff = eval(model, "v3_int_cu_lower(2*pi*r*rho_cu_T/A_conductor^2)+v3_int_cu_upper(2*pi*r*rho_cu_T/A_conductor^2)");
    double qJouleExpected = d(m, "current") * d(m, "current") * rEff;
    double qContactExpected = eval(model, "Icase^2*Rc0*Rc0_multiplier*Rc_factor");
    setD(m, "qJouleErrorPct", relErrPct(d(m, "qJoule"), qJouleExpected));
    setD(m, "qContactErrorPct", relErrPct(d(m, "qContact"), qContactExpected));
    double qAir = eval(model, "v3_int_air_bnd(2*pi*r*h_air_case*(T-Tair_case))+v3_int_air_terminal_bnd(2*pi*r*h_air_case*(T-Tair_case))");
    double qOil = eval(model, "v3_int_oil_bnd(2*pi*r*h_oil_case*(T-Toil_case))");
    double qFlange = eval(model, "v3_int_flange_bnd(2*pi*r*h_flange_case*(T-Tair_case))");
    double qRemoved = qAir + qOil + qFlange;
    double residual = d(m, "qTotal") - qRemoved;
    setD(m, "residualPctQ", d(m, "qTotal") != 0.0 ? 100.0 * residual / d(m, "qTotal") : Double.NaN);
    double maxEnergyScale = Math.max(Math.max(Math.abs(d(m, "qTotal")), Math.abs(qAir) + Math.abs(qOil) + Math.abs(qFlange)), 1.0);
    double residualPctMax = 100.0 * residual / maxEnergyScale;
    m.setProperty("heatBalanceStatus", heatBalanceStatus(d(m, "residualPctQ"), residual, residualPctMax));
    setB(m, "fieldSingularity", singularityFlag(d(m, "eMaxGlobal"), d(m, "eMaxRip"), d(m, "eProbe")));
    setB(m, "dielectricReviewRequired", finite(d(m, "qDielectricRatio")) && (d(m, "qDielectricRatio") < 0.1 || d(m, "qDielectricRatio") > 10.0));

    boolean validTemperature = finite(d(m, "tmaxAll")) && d(m, "tmaxAll") < 150.0;
    boolean validHeat = "VALID_STRICT".equals(s(m, "heatBalanceStatus")) || "VALID_LOW_POWER_RECLASSIFIED".equals(s(m, "heatBalanceStatus"));
    boolean validQJoule = finite(d(m, "qJouleErrorPct")) && Math.abs(d(m, "qJouleErrorPct")) < 5.0;
    boolean validQContact = finite(d(m, "qContactErrorPct")) && Math.abs(d(m, "qContactErrorPct")) < 1.0;
    boolean validQDielectric = finite(d(m, "qDielectricField")) && d(m, "qDielectricField") > 0.0 && d(m, "qDielectricField") < 1000.0;
    boolean validSelection = !(almostEqual(d(m, "tmaxConductor"), d(m, "tmaxRip")) && almostEqual(d(m, "tmaxRip"), d(m, "tmaxContact")));
    boolean physicsValid = "SOLVED".equals(s(m, "solveStatus")) && validHeat && validQJoule && validQContact
        && validQDielectric && validSelection && !b(m, "fieldSingularity");
    boolean thermalRisk = physicsValid && finite(d(m, "tmaxAll")) && d(m, "tmaxAll") >= 150.0;
    boolean thermalWarning = physicsValid && finite(d(m, "tmaxAll")) && d(m, "tmaxAll") >= 130.0;
    boolean overallValid = physicsValid && (validTemperature || thermalRisk);
    if (!"SOLVED".equals(s(m, "solveStatus"))) {
      m.setProperty("status", "SOLVE_FAILED");
    } else if (thermalRisk) {
      m.setProperty("status", "SOLVED_THERMAL_RISK");
    } else if (thermalWarning) {
      m.setProperty("status", "SOLVED_THERMAL_WARNING");
    } else {
      m.setProperty("status", overallValid ? "SOLVED_VALID" : "INVALID_CASE");
    }
    if (s(m, "note").length() == 0) {
      m.setProperty("note", note);
    }
    return m;
  }

  private static int meshElementCount(Model model) {
    try {
      return model.component(COMP).mesh(MESH).getNumElem();
    } catch (Throwable t) {
      return -1;
    }
  }

  private static int meshVertexCount(Model model) {
    try {
      return model.component(COMP).mesh(MESH).getNumVertex();
    } catch (Throwable t) {
      return -1;
    }
  }

  private static double meshMinQuality(Model model) {
    try {
      return model.component(COMP).mesh(MESH).getMinQuality();
    } catch (Throwable t) {
      return Double.NaN;
    }
  }

  private static int dofCount(Model model) {
    try {
      int[] size = model.sol("sol1").getSize();
      int best = 0;
      for (int v : size) {
        if (v > best) {
          best = v;
        }
      }
      return best;
    } catch (Throwable t) {
      return -1;
    }
  }

  private static double eval(Model model, String expr) {
    double value = evalWithData(model, expr, "dset2");
    if (finite(value)) {
      return value;
    }
    return evalWithData(model, expr, null);
  }

  private static double evalWithData(Model model, String expr, String dataSet) {
    String tag = "gev_run011_" + (++evalCounter);
    try {
      model.result().numerical().create(tag, "EvalGlobal");
      model.result().numerical(tag).set("expr", new String[]{expr});
      if (dataSet != null) {
        model.result().numerical(tag).set("data", dataSet);
      }
      double[][] value = model.result().numerical(tag).getReal();
      if (value.length > 0 && value[0].length > 0) {
        return value[0][0];
      }
    } catch (Throwable t) {
    } finally {
      try {
        model.result().numerical().remove(tag);
      } catch (Throwable ignored) {
      }
    }
    return Double.NaN;
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

  private static void setD(Properties props, String key, double value) {
    props.setProperty(key, fmt(value));
  }

  private static double d(Properties props, String key) {
    String value = props.getProperty(key);
    if (value == null || value.length() == 0) {
      return Double.NaN;
    }
    try {
      return Double.parseDouble(value);
    } catch (Throwable t) {
      return Double.NaN;
    }
  }

  private static void setB(Properties props, String key, boolean value) {
    props.setProperty(key, bool(value));
  }

  private static boolean b(Properties props, String key) {
    return "true".equalsIgnoreCase(props.getProperty(key, "false"));
  }

  private static String s(Properties props, String key) {
    return props.getProperty(key, "");
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

  private static BufferedWriter writer(File outDir, String name) throws IOException {
    return new BufferedWriter(new FileWriter(new File(outDir, name)));
  }

  private static String path(String relative) {
    return new File(projectRoot, relative).getPath();
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
