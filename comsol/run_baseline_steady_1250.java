import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class run_baseline_steady_1250 {

  public static void main(String[] args) throws java.io.IOException {
    String root = resolveProjectRoot(args);
    File physicsModel = new File(root, "comsol/BRFGL1-126-1250-4_physics_baseline.mph");
    if (!physicsModel.exists()) {
      throw new IOException("Missing physics model: " + physicsModel.getPath()
          + ". Run build_physics_brfgl1.java first.");
    }
    Model model = ModelUtil.load("Model", physicsModel.getPath());
    String status = "SOLVED";
    String note = "RUN004 solid-domain thermal baseline with segmented CAD convection";
    try {
      model.component("comp_v2").mesh("mesh1").run();
      model.study("std_es").run();
      // RUN004 keeps the standalone heat study defined for diagnostics, but
      // does not execute it in the baseline path because it stalls in COMSOL
      // 6.0 on the CAD-strip mesh. The coupled study below still solves the
      // thermal field with the electrostatic solution active.
      model.study("std_cpl").run();
    } catch (Throwable t) {
      status = "SOLVE_FAILED";
      note = t.getMessage();
      System.out.println("Baseline solve failed: " + t.getMessage());
    }
    export(model, root, status, note);
    model.save(new File(root, "comsol/BRFGL1-126-1250-4_baseline_STEADY_1250_LOAD_1p0_RUN004.mph").getPath());
  }

  private static void export(Model model, String root, String status, String note) throws IOException {
    File outDir = new File(root, "results/raw_comsol_exports/STEADY_1250_LOAD_1p0_RUN004");
    outDir.mkdirs();
    File csv = new File(outDir, "baseline_metrics.csv");
    double tmaxAll = eval(model, "maxop_T_all(T)-273.15[K]", "dset3");
    double tmaxConductor = eval(model, "maxop_T_conductor(T)-273.15[K]", "dset3");
    double tmaxRip = eval(model, "maxop_T_rip(T)-273.15[K]", "dset3");
    double tmaxContact = eval(model, "maxop_T_contact(T)-273.15[K]", "dset3");
    double emaxAll = eval(model, "maxop_E_all(es.normE)", "dset3");
    double emaxRip = eval(model, "maxop_E_rip(es.normE)", "dset3");
    double emaxScreenProbe = eval(model, "maxop_E_screen_probe(es.normE)", "dset3");
    double qContact = eval(model, "Icase^2*Rc0*Rc_factor", "dset3");

    if ("SOLVED".equals(status)) {
      status = "SOLVED_VALID";
    }
    if (!Double.isNaN(tmaxAll) && tmaxAll >= 150.0) {
      status = "INVALID_TEMPERATURE_RANGE";
      note = note + "; Tmax_global_C does not satisfy RUN004 acceptance criterion < 150 C";
    }
    if (!Double.isNaN(tmaxConductor) && !Double.isNaN(tmaxRip) && !Double.isNaN(tmaxContact)
        && almostEqual(tmaxConductor, tmaxRip) && almostEqual(tmaxRip, tmaxContact)) {
      status = "INVALID_SELECTION_OVERLAP";
      note = note + "; conductor/RIP/contact Tmax are numerically identical";
    }

    BufferedWriter writer = new BufferedWriter(new FileWriter(csv));
    try {
      writer.write("case_id,run_id,status,Tmax_global_C,Tmax_conductor_C,Tmax_RIP_C,Tmax_contact_C,Emax_global_V_per_m,Emax_RIP_V_per_m,Emax_screen_end_probe_V_per_m,Qcontact_W,note\n");
      writer.write("STEADY_1250_LOAD_1p0,RUN004," + status + ","
          + fmt(tmaxAll) + "," + fmt(tmaxConductor) + "," + fmt(tmaxRip) + "," + fmt(tmaxContact) + ","
          + fmt(emaxAll) + "," + fmt(emaxRip) + "," + fmt(emaxScreenProbe) + "," + fmt(qContact) + ",\""
          + note.replace("\"", "'") + "\"\n");
    } finally {
      writer.close();
    }

    if (!"SOLVED_VALID".equals(status)) {
      File report = new File(outDir, "baseline_exception_report.md");
      BufferedWriter reportWriter = new BufferedWriter(new FileWriter(report));
      try {
        reportWriter.write("# STEADY_1250_LOAD_1p0 RUN004 exception report\n\n");
        reportWriter.write("- status: " + status + "\n");
        reportWriter.write("- note: " + note + "\n");
        reportWriter.write("- action: do not backfill validation targets as valid baseline values.\n");
      } finally {
        reportWriter.close();
      }
    }
  }

  private static double eval(Model model, String expr, String dataSetTag) {
    try {
      String tag = "gev_" + Math.abs(expr.hashCode());
      model.result().numerical().create(tag, "EvalGlobal");
      try {
        if (dataSetTag != null && dataSetTag.length() > 0) {
        model.result().numerical(tag).set("data", dataSetTag);
        }
      } catch (Throwable ignored) {
      }
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

  private static String fmt(double value) {
    if (Double.isNaN(value) || Double.isInfinite(value)) {
      return "";
    }
    return String.format(java.util.Locale.US, "%.9g", value);
  }

  private static boolean almostEqual(double a, double b) {
    return Math.abs(a - b) < 1.0e-6;
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
