import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Arrays;

public class export_v3_entity_ids {

  private static String projectRoot = ".";
  private static final String COMP = "comp_v3_solid_solver";

  public static void main(String[] args) throws IOException {
    projectRoot = resolveProjectRoot(args);
    File modelFile = new File(projectRoot, "comsol/BRFGL1-126-1250-4_geometry_axisym.mph");
    if (!modelFile.exists()) {
      throw new IOException("Missing geometry model: " + modelFile.getPath());
    }
    Model model = ModelUtil.load("Model", modelFile.getPath());
    File outDir = new File(projectRoot, "results/summary_tables");
    outDir.mkdirs();
    writeDomainSelectionEntities(model, new File(outDir, "v3_domain_selection_entities.csv"));
    writeBoundarySelectionEntities(model, new File(outDir, "v3_boundary_selection_entities.csv"));
    writeSelectionCatalog(model, new File(outDir, "v3_selection_catalog.csv"));
  }

  private static void writeDomainSelectionEntities(Model model, File file) throws IOException {
    String[][] rows = new String[][]{
        {"center_conductor_main", "geom_v3_g_center_conductor_main_dom", "center conductor lower/main tube"},
        {"center_conductor_upper", "geom_v3_g_center_conductor_upper_dom", "center conductor upper tube"},
        {"contact_resistance_heat_source_layer", "geom_v3_g_contact_resistance_heat_source_layer_dom", "terminal-conductor contact heat-source layer"},
        {"terminal_connector_region", "geom_v3_g_terminal_connector_region_dom", "terminal connector region"},
        {"rip_capacitor_core", "geom_v3_g_rip_capacitor_core_dom", "RIP capacitor core"},
        {"silicone_rubber_external_insulation", "geom_v3_g_silicone_rubber_external_insulation_dom", "silicone rubber trunk"},
        {"flange_grounded_metal_disk", "geom_v3_g_flange_grounded_metal_disk_dom", "grounded flange disk"},
        {"flange_grounded_metal_neck", "geom_v3_g_flange_grounded_metal_neck_dom", "grounded flange neck"},
        {"condenser_screens", "v3_condenser_screens", "all explicit condenser screen domains"},
        {"air_side_sheds_or_equivalent_envelope", "v3_air_side_sheds_or_equivalent_envelope", "CAD air-side shed/envelope domains"},
        {"inner_conduit_or_hollow_region", "v3_inner_conduit_or_hollow_region", "inner hollow/conduit placeholder"}
    };
    BufferedWriter w = new BufferedWriter(new FileWriter(file));
    try {
      w.write("physical_region,selection_name,dimension,entity_ids,entity_count,physical_meaning\n");
      for (String[] row : rows) {
        int[] ids = entities(model, row[1], 2);
        w.write(row[0] + "," + row[1] + ",domain,\"" + join(ids) + "\"," + ids.length + ",\"" + row[2] + "\"\n");
      }
    } finally {
      w.close();
    }
  }

  private static void writeBoundarySelectionEntities(Model model, File file) throws IOException {
    String[][] rows = new String[][]{
        {"air_shed_external_candidate", "v3_bnd_air_external_convection_explicit", "CAD air-side shed external surface candidate"},
        {"air_terminal_external_candidate", "v3_bnd_external_terminal_convection", "terminal outer surface candidate"},
        {"oil_external_candidate", "v3_bnd_oil_immersed_surface_explicit", "oil-immersed outer surface candidate"},
        {"flange_external_candidate", "v3_bnd_flange_external_convection", "flange external surface candidate"},
        {"axisymmetry", "v3_bnd_axisymmetry", "r=0 axisymmetry boundary; must not be convective"}
    };
    BufferedWriter w = new BufferedWriter(new FileWriter(file));
    try {
      w.write("physical_region,selection_name,dimension,entity_ids,entity_count,physical_meaning\n");
      for (String[] row : rows) {
        int[] ids = entities(model, row[1], 1);
        w.write(row[0] + "," + row[1] + ",boundary,\"" + join(ids) + "\"," + ids.length + ",\"" + row[2] + "\"\n");
      }
    } finally {
      w.close();
    }
  }

  private static void writeSelectionCatalog(Model model, File file) throws IOException {
    BufferedWriter w = new BufferedWriter(new FileWriter(file));
    try {
      w.write("selection_name,domain_ids,boundary_ids\n");
      String[] tags = model.component(COMP).selection().tags();
      Arrays.sort(tags);
      for (String tag : tags) {
        w.write(tag + ",\"" + join(entities(model, tag, 2)) + "\",\"" + join(entities(model, tag, 1)) + "\"\n");
      }
    } finally {
      w.close();
    }
  }

  private static int[] entities(Model model, String selectionName, int dim) {
    try {
      return model.component(COMP).selection(selectionName).entities(dim);
    } catch (Throwable t1) {
      try {
        return model.component(COMP).selection(selectionName).entities();
      } catch (Throwable t2) {
        System.out.println("Could not read entities for " + selectionName + " dim " + dim + ": " + t1.getMessage());
        return new int[0];
      }
    }
  }

  private static String join(int[] ids) {
    if (ids == null || ids.length == 0) {
      return "";
    }
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < ids.length; i++) {
      if (i > 0) {
        sb.append(" ");
      }
      sb.append(ids[i]);
    }
    return sb.toString();
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
