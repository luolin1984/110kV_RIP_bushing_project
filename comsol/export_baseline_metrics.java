import com.comsol.model.*;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;

public class export_baseline_metrics {

  public static void export(Model model, String projectRoot, String status, String note) {
    File outDir = new File(projectRoot, "results/raw_comsol_exports/STEADY_1250_LOAD_1p0_RUN002");
    outDir.mkdirs();
    File metrics = new File(outDir, "baseline_metrics.csv");
    File exception = new File(outDir, "baseline_exception_report.md");

    String[] header = new String[]{
      "case_id", "run_id", "status", "Tmax_global_C", "Tmax_conductor_C", "Tmax_RIP_C",
      "Tmax_contact_C", "Emax_global_V_per_m", "Emax_RIP_V_per_m", "Emax_screen_end_probe_V_per_m",
      "Qcontact_W", "note"
    };
    String[] expr = new String[]{
      "maxop_T_all(T)-273.15[K]",
      "maxop_T_conductor(T)-273.15[K]",
      "maxop_T_rip(T)-273.15[K]",
      "maxop_T_contact(T)-273.15[K]",
      "maxop_E_all(es.normE)",
      "maxop_E_rip(es.normE)",
      "maxop_E_screen_probe(es.normE)",
      "Icase^2*Rc0*Rc_factor"
    };
    String[] values = new String[expr.length];
    for (int i = 0; i < expr.length; i++) {
      values[i] = evalGlobalScalar(model, expr[i], "dset_cpl");
      if ("NA".equals(values[i]) && i >= 4) {
        values[i] = evalGlobalScalar(model, expr[i], "dset_es");
      }
    }

    boolean physical = "SOLVED".equals(status);
    double tmax = parse(values[0]);
    if (Double.isNaN(tmax) || tmax < -60.0 || tmax > 250.0) {
      physical = false;
      status = "INVALID_TEMPERATURE_RANGE";
      note = note + "; Tmax outside physical acceptance range [-60, 250] degC";
    }

    PrintWriter pw = null;
    try {
      pw = new PrintWriter(new FileWriter(metrics));
      pw.println(String.join(",", header));
      pw.print("STEADY_1250_LOAD_1p0,RUN002," + status);
      for (String v : values) {
        pw.print(",");
        pw.print(v);
      }
      pw.print(",");
      pw.println(csv(note));
    } catch (Throwable t) {
      System.out.println("Metrics export failed: " + t.getMessage());
    } finally {
      if (pw != null) {
        pw.close();
      }
    }

    if (!physical) {
      PrintWriter epw = null;
      try {
        epw = new PrintWriter(new FileWriter(exception));
        epw.println("# Baseline Exception Report");
        epw.println();
        epw.println("- case_id: STEADY_1250_LOAD_1p0");
        epw.println("- run_id: RUN002");
        epw.println("- status: " + status);
        epw.println("- note: " + note);
        epw.println("- Tmax_global_C: " + values[0]);
        epw.println();
        epw.println("This run must not be backfilled as a valid validation target.");
      } catch (Throwable t) {
        System.out.println("Exception report export failed: " + t.getMessage());
      } finally {
        if (epw != null) {
          epw.close();
        }
      }
    }
  }

  private static String evalGlobalScalar(Model model, String expression, String dataset) {
    try {
      String tag = "gev_tmp_" + Math.abs((expression + dataset).hashCode());
      model.result().numerical().create(tag, "EvalGlobal");
      model.result().numerical(tag).set("expr", new String[]{expression});
      model.result().numerical(tag).set("data", dataset);
      double[][] data = model.result().numerical(tag).getReal();
      model.result().numerical().remove(tag);
      if (data.length > 0 && data[0].length > 0) {
        return Double.toString(data[0][0]);
      }
      return "NA";
    } catch (Throwable t) {
      return "NA";
    }
  }

  private static double parse(String v) {
    try {
      return Double.parseDouble(v);
    } catch (Throwable t) {
      return Double.NaN;
    }
  }

  private static String csv(String value) {
    return "\"" + value.replace("\"", "\"\"") + "\"";
  }
}
