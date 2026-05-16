import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Locale;

public class export_v3_boundary_geometry {

  private static String projectRoot = ".";
  private static final String COMP = "comp_v3_solid_solver";
  private static final String GEOM = "geom_v3";

  public static void main(String[] args) throws IOException {
    projectRoot = resolveProjectRoot(args);
    File modelFile = new File(projectRoot, "comsol/BRFGL1-126-1250-4_geometry_axisym.mph");
    if (!modelFile.exists()) {
      throw new IOException("Missing geometry model: " + modelFile.getPath());
    }
    Model model = ModelUtil.load("Model", modelFile.getPath());
    File out = new File(projectRoot, "results/summary_tables/v3_boundary_geometry.csv");
    out.getParentFile().mkdirs();
    BufferedWriter w = new BufferedWriter(new FileWriter(out));
    try {
      w.write("boundary_id,length_m,r_mean_m,z_mean_m,r_mean_mm,z_mean_mm,status\n");
      for (int id = 1; id <= 360; id++) {
        String sel = "tmp_bnd_" + id;
        String op = "tmp_int_" + id;
        try {
          model.component(COMP).selection().create(sel, "Explicit");
          model.component(COMP).selection(sel).geom(GEOM, 1);
          model.component(COMP).selection(sel).set(new int[]{id});
          model.component(COMP).cpl().create(op, "Integration");
          model.component(COMP).cpl(op).selection().named(sel);
          double len = eval(model, op + "(1)");
          double rInt = eval(model, op + "(r)");
          double zInt = eval(model, op + "(z)");
          double rMean = len != 0.0 ? rInt / len : Double.NaN;
          double zMean = len != 0.0 ? zInt / len : Double.NaN;
          if (!Double.isNaN(len) && len > 0.0) {
            w.write(String.format(Locale.US, "%d,%.9g,%.9g,%.9g,%.9g,%.9g,OK%n",
                id, len, rMean, zMean, rMean * 1000.0, zMean * 1000.0));
          }
        } catch (Throwable t) {
          // Invalid boundary ids are silently ignored.
        } finally {
          try {
            model.component(COMP).cpl().remove(op);
          } catch (Throwable t) {
          }
          try {
            model.component(COMP).selection().remove(sel);
          } catch (Throwable t) {
          }
        }
      }
    } finally {
      w.close();
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
      return Double.NaN;
    }
    return Double.NaN;
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
