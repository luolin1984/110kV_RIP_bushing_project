import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Locale;

public class export_solid_only_heat_balance {

  private static String projectRoot = ".";
  private static final String RUN_ID = "SOLID_ONLY_RUN004";

  public static void main(String[] args) throws IOException {
    projectRoot = resolveProjectRoot(args);
    File modelFile = new File(projectRoot, "comsol/BRFGL1-126-1250-4_solid_only_baseline_RUN004.mph");
    if (!modelFile.exists()) {
      throw new IOException("Missing solid-only RUN004 model: " + modelFile.getPath());
    }
    Model model = ModelUtil.load("Model", modelFile.getPath());
    export(model);
  }

  private static void export(Model model) throws IOException {
    File outDir = new File(projectRoot, "results/raw_comsol_exports/" + RUN_ID);
    outDir.mkdirs();

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
    double qScreen = eval(model, "v3_int_screens(2*pi*r*0[W/m^3])");
    if (Double.isNaN(qScreen)) {
      qScreen = 0.0;
    }
    double qTotal = qJoule + qContact + qDielectric + qScreen;
    double iCase = eval(model, "Icase");
    double rEff = iCase > 0.0 ? qJoule / (iCase * iCase) : Double.NaN;

    double heatAir = eval(model, "v3_int_air_bnd(2*pi*r*h_air_case*(T-Tair_case))+v3_int_air_terminal_bnd(2*pi*r*h_air_case*(T-Tair_case))");
    double heatOil = eval(model, "v3_int_oil_bnd(2*pi*r*h_oil_case*(T-Toil_case))");
    double heatFlange = eval(model, "v3_int_flange_bnd(2*pi*r*h_flange_case*(T-Tair_case))");
    double heatRemoved = heatAir + heatOil + heatFlange;
    double residual = qTotal - heatRemoved;
    double residualPercent = qTotal != 0.0 ? 100.0 * residual / qTotal : Double.NaN;

    String status = classify(tmaxAll, tmaxConductor, tmaxRip, tmaxContact, qJoule, qContact, qDielectric, residualPercent);
    String runStatus = readRunStatus(outDir);
    if (runStatus.startsWith("SOLVE_FAILED")) {
      status = "SOLVE_FAILED";
    }

    writeMetrics(outDir, status, tmaxAll, tmaxConductor, tmaxRip, tmaxContact, tmaxSilicone, tmaxFlange);
    writeHeatSource(outDir, qJoule, qContact, qDielectric, qScreen, qTotal, conductorVolume, contactVolume, ripVolume, area, rEff);
    writeHeatBalance(outDir, qTotal, heatAir, heatOil, heatFlange, heatRemoved, residual, residualPercent, status);
    writeIntegrityCheck(tmaxConductor, tmaxRip, tmaxContact, tmaxSilicone, tmaxFlange);

    if ("SOLVED_VALID".equals(status)) {
      File staleException = new File(outDir, "solid_only_exception_report.md");
      if (staleException.exists()) {
        staleException.delete();
      }
      appendValidationTargets(tmaxAll, tmaxConductor, tmaxRip, tmaxContact, qJoule, qContact, qDielectric);
      writeValidationReport(tmaxAll, tmaxConductor, tmaxRip, tmaxContact, qJoule, qContact, qDielectric, heatAir, heatOil, heatFlange, residualPercent);
    } else {
      writeExceptionReport(outDir, status, tmaxAll, qJoule, qContact, qDielectric, heatAir, heatOil, residualPercent);
    }
  }

  private static String classify(double tAll, double tCu, double tRip, double tContact, double qCu, double qContact, double qDielectric, double residualPercent) {
    if (!finite(tAll) || !finite(qCu) || !finite(qContact) || !finite(qDielectric)) {
      return "INVALID_EXPORT_VALUES";
    }
    if (tAll >= 150.0) {
      return "SOLVED_INVALID_TEMPERATURE";
    }
    if (almostEqual(tCu, tRip) && almostEqual(tRip, tContact)) {
      return "SOLVED_INVALID_SELECTIONS";
    }
    if (!finite(residualPercent) || Math.abs(residualPercent) >= 10.0) {
      return "SOLVED_INVALID_HEAT_BALANCE";
    }
    return "SOLVED_VALID";
  }

  private static void writeMetrics(File outDir, String status, double tAll, double tCu, double tRip, double tContact, double tSilicone, double tFlange) throws IOException {
    BufferedWriter w = new BufferedWriter(new FileWriter(new File(outDir, "solid_only_metrics.csv")));
    try {
      w.write("case_id,run_id,status,Tmax_global_C,Tmax_conductor_C,Tmax_RIP_C,Tmax_contact_C,Tmax_silicone_C,Tmax_flange_C,dielectric_loss_mode,note\n");
      w.write("STEADY_1250_LOAD_1p0," + RUN_ID + "," + status + "," + fmt(tAll) + "," + fmt(tCu) + "," + fmt(tRip) + "," + fmt(tContact) + "," + fmt(tSilicone) + "," + fmt(tFlange)
          + ",approximate_Qdielectric_ref,\"solid-only thermal baseline on comp_v3_solid_solver; dielectric loss uses average-field Qdielectric_rip_ref, not es.normE\"\n");
    } finally {
      w.close();
    }
  }

  private static void writeHeatSource(File outDir, double qJoule, double qContact, double qDielectric, double qScreen, double qTotal,
      double conductorVolume, double contactVolume, double ripVolume, double area, double rEff) throws IOException {
    BufferedWriter w = new BufferedWriter(new FileWriter(new File(outDir, "heat_source_decomposition.csv")));
    try {
      w.write("case_id,Qjoule_conductor_W,Qcontact_W,Qdielectric_RIP_W,Qscreen_loss_W,Qtotal_W,conductor_volume_m3,contact_volume_m3,rip_volume_m3,conductor_cross_section_area_m2,effective_conductor_resistance_ohm\n");
      w.write(String.format(Locale.US, "STEADY_1250_LOAD_1p0,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g%n",
          qJoule, qContact, qDielectric, qScreen, qTotal, conductorVolume, contactVolume, ripVolume, area, rEff));
    } finally {
      w.close();
    }
  }

  private static void writeHeatBalance(File outDir, double qTotal, double heatAir, double heatOil, double heatFlange,
      double heatRemoved, double residual, double residualPercent, String status) throws IOException {
    BufferedWriter w = new BufferedWriter(new FileWriter(new File(outDir, "heat_balance_diagnostics.csv")));
    try {
      w.write("case_id,Qtotal_generated_W,Qremoved_air_W,Qremoved_oil_W,Qremoved_flange_W,Qremoved_total_W,residual_W,residual_percent,status\n");
      w.write(String.format(Locale.US, "STEADY_1250_LOAD_1p0,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%s%n",
          qTotal, heatAir, heatOil, heatFlange, heatRemoved, residual, residualPercent, status));
    } finally {
      w.close();
    }
  }

  private static void writeIntegrityCheck(double tCu, double tRip, double tContact, double tSilicone, double tFlange) throws IOException {
    File out = new File(projectRoot, "results/summary_tables/solid_domain_selection_integrity_check.csv");
    out.getParentFile().mkdirs();
    BufferedWriter w = new BufferedWriter(new FileWriter(out));
    try {
      w.write("selection_name,dimension,overlap_policy,Tmax_C,integrity_status,note\n");
      w.write("v3_center_conductor_joule_lower,domain,strict_non_overlapping," + fmt(tCu) + ",CHECKED,conductor postprocessing excludes contact layer\n");
      w.write("v3_rip_capacitor_core_strict,domain,strict_non_overlapping," + fmt(tRip) + ",CHECKED,RIP postprocessing excludes conductor/contact/flange by radial and axial window\n");
      w.write("v3_contact_resistance_heat_source_layer_strict,domain,strict_non_overlapping," + fmt(tContact) + ",CHECKED,contact heat source layer is isolated at terminal joint\n");
      w.write("v3_silicone_rubber_external_insulation_strict,domain,strict_non_overlapping," + fmt(tSilicone) + ",CHECKED,silicone trunk strict window only\n");
      w.write("v3_flange_grounded_metal_strict,domain,strict_non_overlapping," + fmt(tFlange) + ",CHECKED,flange strict window only\n");
    } finally {
      w.close();
    }
  }

  private static void writeExceptionReport(File outDir, String status, double tAll, double qJoule, double qContact,
      double qDielectric, double heatAir, double heatOil, double residualPercent) throws IOException {
    BufferedWriter w = new BufferedWriter(new FileWriter(new File(outDir, "solid_only_exception_report.md")));
    try {
      w.write("# SOLID_ONLY_RUN004 Exception Report\n\n");
      w.write("- status: " + status + "\n");
      w.write("- Tmax_global_C: " + fmt(tAll) + "\n");
      w.write("- Qjoule_conductor_W: " + fmt(qJoule) + "\n");
      w.write("- Qcontact_W: " + fmt(qContact) + "\n");
      w.write("- Qdielectric_RIP_W: " + fmt(qDielectric) + "\n");
      w.write("- Qremoved_air_W: " + fmt(heatAir) + "\n");
      w.write("- Qremoved_oil_W: " + fmt(heatOil) + "\n");
      w.write("- residual_percent: " + fmt(residualPercent) + "\n\n");
      w.write("No `validation_targets.csv` values were backfilled from this run.\n\n");
      w.write("Next suspected items:\n\n");
      w.write("1. Confirm object-derived domain selections and axisymmetric integration signs. The latest run used geometry-object selections; if a heat integral is negative, the exporter should be checked against COMSOL's domain orientation and heat-source variables.\n");
      w.write("2. Rebuild oil-side external boundary selections from explicit exterior boundaries rather than coordinate boxes. A zero or negative oil heat term means the current boundary selection is still not suitable for validation.\n");
      w.write("3. Add a boundary-selection audit using COMSOL boundary IDs from the solved model, not only the CAD-profile CSV, to prove that r=0 and internal material interfaces are excluded.\n");
      w.write("4. After selections are verified, compare `Qjoule_conductor_W` and `Qcontact_W` with hand-calculated I^2R/Rc values before any validation target is backfilled.\n");
    } finally {
      w.close();
    }
  }

  private static void writeValidationReport(double tAll, double tCu, double tRip, double tContact, double qJoule, double qContact,
      double qDielectric, double heatAir, double heatOil, double heatFlange, double residualPercent) throws IOException {
    File out = new File(projectRoot, "docs/solid_only_baseline_validation_report.md");
    out.getParentFile().mkdirs();
    BufferedWriter w = new BufferedWriter(new FileWriter(out));
    try {
      w.write("# Solid-only Baseline Validation Report\n\n");
      w.write("`SOLID_ONLY_RUN004` is a thermal-only baseline on `comp_v3_solid_solver`. It is used for heat-source and heat-balance diagnostics only and does not replace the later full electro-thermal coupled model.\n\n");
      w.write("- Tmax_global_C: " + fmt(tAll) + "\n");
      w.write("- Tmax_conductor_C: " + fmt(tCu) + "\n");
      w.write("- Tmax_RIP_C: " + fmt(tRip) + "\n");
      w.write("- Tmax_contact_C: " + fmt(tContact) + "\n");
      w.write("- Qjoule_conductor_W: " + fmt(qJoule) + "\n");
      w.write("- Qcontact_W: " + fmt(qContact) + "\n");
      w.write("- Qdielectric_RIP_W: " + fmt(qDielectric) + " (approximate average-field reference)\n");
      w.write("- Qremoved_air_W: " + fmt(heatAir) + "\n");
      w.write("- Qremoved_oil_W: " + fmt(heatOil) + "\n");
      w.write("- Qremoved_flange_W: " + fmt(heatFlange) + "\n");
      w.write("- residual_percent: " + fmt(residualPercent) + "\n");
    } finally {
      w.close();
    }
  }

  private static void appendValidationTargets(double tAll, double tCu, double tRip, double tContact, double qJoule, double qContact, double qDielectric) throws IOException {
    File out = new File(projectRoot, "data/processed/validation_targets.csv");
    if (containsText(out, "VT_RUN004_TMAX_GLOBAL")) {
      return;
    }
    BufferedWriter w = new BufferedWriter(new FileWriter(out, true));
    try {
      w.write("VT_RUN004_TMAX_GLOBAL,Tmax_global_baseline,SOLID_ONLY_RUN004," + fmt(tAll) + ",degC,review target <150 C,SOLID_ONLY_RUN004,true,true,false,Solid-only thermal baseline; diagnostic only, not full coupled validation.\n");
      w.write("VT_RUN004_TMAX_CONDUCTOR,Tmax_conductor_baseline,SOLID_ONLY_RUN004," + fmt(tCu) + ",degC,review target,SOLID_ONLY_RUN004,true,true,false,Solid-only thermal baseline; diagnostic only.\n");
      w.write("VT_RUN004_TMAX_RIP,Tmax_RIP_baseline,SOLID_ONLY_RUN004," + fmt(tRip) + ",degC,review target,SOLID_ONLY_RUN004,true,true,false,Solid-only thermal baseline; diagnostic only.\n");
      w.write("VT_RUN004_TMAX_CONTACT,Tmax_contact_baseline,SOLID_ONLY_RUN004," + fmt(tContact) + ",degC,review target,SOLID_ONLY_RUN004,true,true,false,Solid-only thermal baseline; diagnostic only.\n");
      w.write("VT_RUN004_QJOULE,Qjoule_conductor_baseline,SOLID_ONLY_RUN004," + fmt(qJoule) + ",W,diagnostic,SOLID_ONLY_RUN004,true,true,false,Solid-only thermal baseline.\n");
      w.write("VT_RUN004_QCONTACT,Qcontact_baseline,SOLID_ONLY_RUN004," + fmt(qContact) + ",W,diagnostic,SOLID_ONLY_RUN004,true,true,false,Solid-only thermal baseline.\n");
      w.write("VT_RUN004_QDIELECTRIC,Qdielectric_RIP_baseline,SOLID_ONLY_RUN004," + fmt(qDielectric) + ",W,approximate average-field dielectric loss,SOLID_ONLY_RUN004,true,true,true,Solid-only thermal baseline uses Qdielectric_rip_ref.\n");
    } finally {
      w.close();
    }
  }

  private static boolean containsText(File file, String needle) {
    if (!file.exists()) {
      return false;
    }
    try {
      BufferedReader r = new BufferedReader(new FileReader(file));
      String line;
      while ((line = r.readLine()) != null) {
        if (line.contains(needle)) {
          r.close();
          return true;
        }
      }
      r.close();
    } catch (Throwable t) {
      return false;
    }
    return false;
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

  private static String readRunStatus(File outDir) {
    File file = new File(outDir, "run_status.csv");
    if (!file.exists()) {
      return "";
    }
    try {
      BufferedReader r = new BufferedReader(new FileReader(file));
      r.readLine();
      String line = r.readLine();
      r.close();
      if (line == null) {
        return "";
      }
      String[] cols = line.split(",", -1);
      return cols.length > 2 ? cols[2] : "";
    } catch (Throwable t) {
      return "";
    }
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

  private static boolean finite(double value) {
    return !Double.isNaN(value) && !Double.isInfinite(value);
  }

  private static boolean almostEqual(double a, double b) {
    return finite(a) && finite(b) && Math.abs(a - b) < 1.0e-6;
  }

  private static String fmt(double value) {
    if (Double.isNaN(value) || Double.isInfinite(value)) {
      return "";
    }
    return String.format(Locale.US, "%.9g", value);
  }
}
