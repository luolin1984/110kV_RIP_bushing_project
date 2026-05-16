import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;

public class run_physics_diagnostics_brfgl1 {

  private static String projectRoot = ".";
  private static File outDir;

  public static void main(String[] args) throws IOException {
    projectRoot = resolveProjectRoot(args);
    outDir = new File(projectRoot, "results/raw_comsol_exports/PHYSICS_DIAGNOSTICS_RUN003");
    outDir.mkdirs();
    cleanOldExceptions();

    String[][] cases = new String[][]{
      {"ES_FULL", "std_es", "false", "false", "false", "false"},
      {"ES_NO_FLOATING", "std_es", "true", "false", "false", "false"},
      {"HT_FULL", "std_ht", "false", "false", "false", "false"},
      {"HT_NO_DIELECTRIC", "std_ht", "false", "true", "false", "false"},
      {"HT_NO_CONVECTION", "std_ht", "false", "false", "true", "false"},
      {"HT_CONSTANT_CU", "std_ht", "false", "false", "false", "true"},
      {"HT_NO_DIELECTRIC_CONSTANT_CU", "std_ht", "false", "true", "false", "true"},
      {"CPL_FULL", "std_cpl", "false", "false", "false", "false"},
      {"CPL_NO_FLOATING", "std_cpl", "true", "false", "false", "false"},
      {"CPL_NO_DIELECTRIC", "std_cpl", "false", "true", "false", "false"},
      {"CPL_NO_CONVECTION", "std_cpl", "false", "false", "true", "false"},
      {"CPL_CONSTANT_CU", "std_cpl", "false", "false", "false", "true"},
      {"CPL_NO_DIELECTRIC_CONSTANT_CU", "std_cpl", "false", "true", "false", "true"},
      {"CPL_NO_FLOATING_NO_DIELECTRIC_CONSTANT_CU", "std_cpl", "true", "true", "false", "true"},
      {"CPL_ALL_SUSPECTS_OFF", "std_cpl", "true", "true", "true", "true"}
    };

    File csv = new File(outDir, "diagnostic_results.csv");
    BufferedWriter writer = new BufferedWriter(new FileWriter(csv));
    try {
      writer.write("case_id,study,disable_floating,disable_dielectric,disable_convection,constant_copper_loss,status,Tmax_global_C,Emax_global_V_per_m,error_message\n");
      for (int i = 0; i < cases.length; i++) {
        runCase(writer, cases[i]);
      }
    } finally {
      writer.close();
    }
    writeReport(csv);
  }

  private static void runCase(BufferedWriter writer, String[] c) throws IOException {
    String caseId = c[0];
    String study = c[1];
    boolean disableFloating = bool(c[2]);
    boolean disableDielectric = bool(c[3]);
    boolean disableConvection = bool(c[4]);
    boolean constantCopper = bool(c[5]);
    String status = "SOLVED";
    String message = "";
    double tmax = Double.NaN;
    double emax = Double.NaN;

    Model model = null;
    try {
      File physicsModel = new File(projectRoot, "comsol/BRFGL1-126-1250-4_physics_baseline.mph");
      model = ModelUtil.load("Model", physicsModel.getPath());
      applyToggles(model, disableFloating, disableDielectric, disableConvection, constantCopper);
      try {
        model.component("comp_v2").mesh("mesh1").autoMeshSize(7);
      } catch (Throwable ignored) {
      }
      model.component("comp_v2").mesh("mesh1").run();
      model.study(study).run();
      if (study.indexOf("ht") >= 0 || study.indexOf("cpl") >= 0) {
        tmax = eval(model, "maxop_T_all(T)-273.15[K]");
      }
      if (study.indexOf("es") >= 0 || study.indexOf("cpl") >= 0) {
        emax = eval(model, "maxop_E_all(es.normE)");
      }
    } catch (Throwable t) {
      status = "FAILED";
      message = t.getMessage();
      writeStack(caseId, t);
      System.out.println("Diagnostic case failed: " + caseId + " -> " + message);
    }

    writer.write(caseId + "," + study + "," + disableFloating + "," + disableDielectric + ","
        + disableConvection + "," + constantCopper + "," + status + "," + fmt(tmax) + ","
        + fmt(emax) + ",\"" + clean(message) + "\"\n");
    writer.flush();
  }

  private static void applyToggles(Model model, boolean disableFloating, boolean disableDielectric,
      boolean disableConvection, boolean constantCopper) {
    if (disableFloating) {
      for (int i = 1; i <= 9; i++) {
        deactivate(model, "es", "fp_s" + twoDigit(i));
      }
    }
    if (disableDielectric) {
      deactivate(model, "ht", "hs_rip_dielectric");
    }
    if (disableConvection) {
      deactivate(model, "ht", "hf_air");
      deactivate(model, "ht", "hf_oil");
    }
    if (constantCopper) {
      try {
        model.component("comp_v2").physics("ht").feature("hs_cu").set("Q0", "Icase^2*(1/sigma_cu_20)/(pi*(r_conductor_outer^2-r_hollow^2))^2");
      } catch (Throwable ignored) {
      }
      try {
        model.component("comp_v2").material("mat_cu").propertyGroup("def").set("electricconductivity", new String[]{"sigma_cu_20"});
      } catch (Throwable ignored) {
      }
    }
  }

  private static void deactivate(Model model, String physics, String feature) {
    try {
      model.component("comp_v2").physics(physics).feature(feature).active(false);
    } catch (Throwable t) {
      System.out.println("Could not deactivate " + physics + "/" + feature + ": " + t.getMessage());
    }
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
      System.out.println("Metric evaluation failed for " + expr + ": " + t.getMessage());
    }
    return Double.NaN;
  }

  private static void writeStack(String caseId, Throwable t) throws IOException {
    StringWriter sw = new StringWriter();
    PrintWriter pw = new PrintWriter(sw);
    t.printStackTrace(pw);
    pw.close();
    File f = new File(outDir, caseId + "_exception.txt");
    BufferedWriter writer = new BufferedWriter(new FileWriter(f));
    try {
      writer.write(sw.toString());
    } finally {
      writer.close();
    }
  }

  private static void cleanOldExceptions() {
    File[] files = outDir.listFiles();
    if (files == null) {
      return;
    }
    for (int i = 0; i < files.length; i++) {
      if (files[i].getName().endsWith("_exception.txt")) {
        files[i].delete();
      }
    }
  }

  private static void writeReport(File csv) throws IOException {
    File report = new File(outDir, "diagnostic_report.md");
    BufferedWriter writer = new BufferedWriter(new FileWriter(report));
    try {
      writer.write("# Physics Diagnostics RUN003\n\n");
      writer.write("This run separates `std_es`, `std_ht`, and `std_cpl`, then disables one suspect feature group at a time.\n\n");
      writer.write("The machine-readable summary is `diagnostic_results.csv`. Per-case exception stacks are written as `*_exception.txt` when a case fails.\n\n");
      writer.write("Diagnostic toggles:\n\n");
      writer.write("- `disable_floating`: disables S01-S09 floating-potential screen boundaries.\n");
      writer.write("- `disable_dielectric`: disables RIP dielectric heat source using `es.normE`.\n");
      writer.write("- `disable_convection`: disables air and oil convection boundary features.\n");
      writer.write("- `constant_copper_loss`: replaces temperature-dependent copper Joule heat with a constant 20 degC expression.\n\n");
      writer.write("CSV path: " + csv.getPath() + "\n");
    } finally {
      writer.close();
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

  private static boolean bool(String v) {
    return "true".equals(v);
  }

  private static String twoDigit(int i) {
    return (i < 10 ? "0" : "") + i;
  }

  private static String fmt(double value) {
    if (Double.isNaN(value) || Double.isInfinite(value)) {
      return "";
    }
    return String.format(java.util.Locale.US, "%.9g", value);
  }

  private static String clean(String text) {
    if (text == null) {
      return "";
    }
    return text.replace("\"", "'").replace("\n", " ").replace("\r", " ");
  }
}
