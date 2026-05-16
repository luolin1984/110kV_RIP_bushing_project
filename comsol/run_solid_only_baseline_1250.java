import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class run_solid_only_baseline_1250 {

  private static String projectRoot = ".";

  public static void main(String[] args) throws IOException {
    projectRoot = resolveProjectRoot(args);
    File physicsModel = new File(projectRoot, "comsol/BRFGL1-126-1250-4_solid_only_physics.mph");
    if (!physicsModel.exists()) {
      throw new IOException("Missing solid-only physics model: " + physicsModel.getPath());
    }
    File outDir = new File(projectRoot, "results/raw_comsol_exports/SOLID_ONLY_RUN004");
    outDir.mkdirs();
    Model model = ModelUtil.load("Model", physicsModel.getPath());
    model.label("BRFGL1-126-1250-4_solid_only_baseline_RUN004.mph");
    String status = "SOLVED";
    String note = "STEADY_1250_LOAD_1p0 solid-only thermal run on comp_v3_solid_solver";
    try {
      model.component("comp_v3_solid_solver").mesh("mesh_solid").run();
      model.study("std_solid_ht").run();
    } catch (Throwable t) {
      status = "SOLVE_FAILED";
      note = clean(t.toString() + " " + t.getMessage());
      System.out.println("Solid-only RUN004 failed: " + t.toString());
      t.printStackTrace();
    }
    writeStatus(outDir, status, note);
    model.save(path("comsol/BRFGL1-126-1250-4_solid_only_baseline_RUN004.mph"));
  }

  private static void writeStatus(File outDir, String status, String note) throws IOException {
    BufferedWriter writer = new BufferedWriter(new FileWriter(new File(outDir, "run_status.csv")));
    try {
      writer.write("case_id,run_id,status,note\n");
      writer.write("STEADY_1250_LOAD_1p0,SOLID_ONLY_RUN004," + status + ",\"" + clean(note) + "\"\n");
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

  private static String path(String relativePath) {
    return new File(projectRoot, relativePath).getPath();
  }

  private static String clean(String text) {
    if (text == null) {
      return "";
    }
    return text.replace("\"", "'").replace("\n", " ").replace("\r", " ");
  }
}
