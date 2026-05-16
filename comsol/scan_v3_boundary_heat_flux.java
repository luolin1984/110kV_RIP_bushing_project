import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.LinkedHashSet;
import java.util.Locale;
import java.util.Set;

public class scan_v3_boundary_heat_flux {

  private static String projectRoot = ".";
  private static final String COMP = "comp_v3_solid_solver";
  private static final String GEOM = "geom_v3";

  public static void main(String[] args) throws IOException {
    projectRoot = resolveProjectRoot(args);
    File modelFile = new File(projectRoot, "comsol/BRFGL1-126-1250-4_solid_only_baseline_RUN004.mph");
    if (!modelFile.exists()) {
      throw new IOException("Missing solved solid-only model: " + modelFile.getPath());
    }
    Model model = ModelUtil.load("Model", modelFile.getPath());
    Set<Integer> candidates = new LinkedHashSet<Integer>();
    add(candidates, entities(model, "geom_v3_g_rip_capacitor_core_bnd", 1));
    add(candidates, entities(model, "geom_v3_g_silicone_rubber_external_insulation_bnd", 1));
    add(candidates, entities(model, "geom_v3_g_terminal_connector_region_bnd", 1));
    add(candidates, entities(model, "geom_v3_g_flange_grounded_metal_disk_bnd", 1));
    add(candidates, entities(model, "geom_v3_g_flange_grounded_metal_neck_bnd", 1));
    for (int i = 0; i < 60; i++) {
      add(candidates, entities(model, "geom_v3_g_cad_air_side_profile_" + threeDigit(i) + "_bnd", 1));
    }
    File out = new File(projectRoot, "results/summary_tables/v3_boundary_heat_flux_scan.csv");
    out.getParentFile().mkdirs();
    BufferedWriter w = new BufferedWriter(new FileWriter(out));
    try {
      w.write("boundary_id,length_eval,Tmean_C,Qair_W,Qoil_W,Qflange_W\n");
      for (Integer id : candidates) {
        double[] m = metrics(model, id.intValue());
        w.write(String.format(Locale.US, "%d,%.9g,%.9g,%.9g,%.9g,%.9g%n",
            id.intValue(), m[0], m[1], m[2], m[3], m[4]));
      }
    } finally {
      w.close();
    }
  }

  private static double[] metrics(Model model, int id) {
    String sel = "scan_bnd_" + id;
    String op = "scan_int_" + id;
    double[] m = new double[]{Double.NaN, Double.NaN, Double.NaN, Double.NaN, Double.NaN};
    try {
      model.component(COMP).selection().create(sel, "Explicit");
      model.component(COMP).selection(sel).geom(GEOM, 1);
      model.component(COMP).selection(sel).set(new int[]{id});
      model.component(COMP).cpl().create(op, "Integration");
      model.component(COMP).cpl(op).selection().named(sel);
      m[0] = eval(model, op + "(1)");
      double tint = eval(model, op + "(T)");
      m[1] = m[0] != 0.0 ? tint / m[0] - 273.15 : Double.NaN;
      m[2] = eval(model, op + "(h_air_case*(T-Tair_case))");
      m[3] = eval(model, op + "(h_oil_case*(T-Toil_case))");
      m[4] = eval(model, op + "(h_flange_case*(T-Tair_case))");
    } catch (Throwable t) {
      m[0] = Double.NaN;
      m[1] = Double.NaN;
      m[2] = Double.NaN;
      m[3] = Double.NaN;
      m[4] = Double.NaN;
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
    return m;
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

  private static int[] entities(Model model, String selectionName, int dim) {
    try {
      return model.component(COMP).selection(selectionName).entities(dim);
    } catch (Throwable t1) {
      return new int[0];
    }
  }

  private static void add(Set<Integer> set, int[] ids) {
    for (int id : ids) {
      set.add(Integer.valueOf(id));
    }
  }

  private static String threeDigit(int i) {
    if (i < 10) return "00" + i;
    if (i < 100) return "0" + i;
    return "" + i;
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
