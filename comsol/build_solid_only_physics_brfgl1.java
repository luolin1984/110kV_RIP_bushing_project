import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.File;
import java.io.IOException;

public class build_solid_only_physics_brfgl1 {

  private static String projectRoot = ".";
  private static final String COMP = "comp_v3_solid_solver";
  private static final String GEOM = "geom_v3";

  public static void main(String[] args) throws IOException {
    projectRoot = resolveProjectRoot(args);
    File geometryModel = new File(projectRoot, "comsol/BRFGL1-126-1250-4_geometry_axisym.mph");
    if (!geometryModel.exists()) {
      throw new IOException("Missing geometry model: " + geometryModel.getPath());
    }
    Model model = ModelUtil.load("Model", geometryModel.getPath());
    model.label("BRFGL1-126-1250-4_solid_only_physics.mph");
    setCaseParameters(model);
    addExplicitIdSelections(model);
    addMaterials(model);
    addHeatTransfer(model);
    addOperators(model);
    addMesh(model);
    model.save(path("comsol/BRFGL1-126-1250-4_solid_only_physics.mph"));
  }

  private static void setCaseParameters(Model model) {
    model.param().set("freq0", "50[Hz]");
    model.param().set("omega0", "2*pi*freq0");
    model.param().set("load_mult", "1");
    model.param().set("Icase", "I0*load_mult");
    model.param().set("voltage_mult", "1");
    model.param().set("Vcase", "Vph_rms*voltage_mult");
    model.param().set("Tair_case", "25[degC]");
    model.param().set("Toil_case", "85[degC]");
    model.param().set("wind_case", "1[m/s]");
    model.param().set("h_air_case", "20[W/(m^2*K)]");
    model.param().set("h_oil_case", "300[W/(m^2*K)]");
    model.param().set("h_flange_case", "20[W/(m^2*K)]");
    model.param().set("sigma_cu_20", "5.998e7[S/m]");
    model.param().set("rho_cu_20", "1/sigma_cu_20");
    model.param().set("alpha_cu", "0.00393[1/K]");
    model.param().set("epsr_rip", "4.2");
    model.param().set("tan_delta_rip", "0.004");
    model.param().set("tan_delta_multiplier", "1");
    model.param().set("sigma_rip", "7e-15[S/m]");
    model.param().set("eps0_solid_const", "8.854187817e-12[F/m]");
    model.param().set("A_conductor", "pi*(r_conductor_outer^2-r_hollow^2)");
  }

  private static void addMaterials(Model model) {
    materialAll(model, "mat_v3_default_solid", "Default solid fallback for unclassified small domains", "0.20[W/(m*K)]", "2200[kg/m^3]", "800[J/(kg*K)]", "1", "1e-15[S/m]");
    material(model, "mat_v3_hollow", "Internal hollow/conduit placeholder", "id_dom_hollow", "0.05[W/(m*K)]", "1.2[kg/m^3]", "1005[J/(kg*K)]", "1", "1e-15[S/m]");
    material(model, "mat_v3_cu_lower", "Copper conductor lower/active path", "id_dom_conductor_lower", "400[W/(m*K)]", "8960[kg/m^3]", "385[J/(kg*K)]", "1", "sigma_cu_20/(1+alpha_cu*(T-293.15[K]))");
    material(model, "mat_v3_cu_upper", "Copper conductor upper/active path", "id_dom_conductor_upper", "400[W/(m*K)]", "8960[kg/m^3]", "385[J/(kg*K)]", "1", "sigma_cu_20/(1+alpha_cu*(T-293.15[K]))");
    material(model, "mat_v3_contact", "Copper contact heat-source layer", "id_dom_contact", "400[W/(m*K)]", "8960[kg/m^3]", "385[J/(kg*K)]", "1", "sigma_cu_20/(1+alpha_cu*(T-293.15[K]))");
    material(model, "mat_v3_terminal", "Copper terminal connector", "id_dom_terminal", "400[W/(m*K)]", "8960[kg/m^3]", "385[J/(kg*K)]", "1", "sigma_cu_20/(1+alpha_cu*(T-293.15[K]))");
    material(model, "mat_v3_rip", "RIP capacitor core", "id_dom_rip_core", "0.20[W/(m*K)]", "2210[kg/m^3]", "730[J/(kg*K)]", "epsr_rip", "sigma_rip");
    material(model, "mat_v3_screen", "Aluminum condenser screens", "id_dom_screens", "205[W/(m*K)]", "2700[kg/m^3]", "900[J/(kg*K)]", "1", "3.5e7[S/m]");
    material(model, "mat_v3_silicone", "Silicone rubber housing and CAD sheds", "id_dom_silicone", "0.20[W/(m*K)]", "2200[kg/m^3]", "703[J/(kg*K)]", "3.75", "1e-14[S/m]");
    material(model, "mat_v3_flange", "Grounded flange metal", "id_dom_flange", "45[W/(m*K)]", "7850[kg/m^3]", "460[J/(kg*K)]", "1", "1e6[S/m]");
  }

  private static void addHeatTransfer(Model model) {
    addVariables(model);
    model.component(COMP).physics().create("ht_solid", "HeatTransfer", GEOM);
    model.component(COMP).physics("ht_solid").selection().all();
    heatSource(model, "hs_cu_lower", "id_dom_conductor_lower", "q_cu_solid");
    heatSource(model, "hs_cu_upper", "id_dom_conductor_upper", "q_cu_solid");
    heatSource(model, "hs_contact", "id_dom_contact", "q_contact_solid");
    heatSource(model, "hs_rip_dielectric_ref", "id_dom_rip_core", "Qdielectric_rip_ref");
    convectiveFlux(model, "hf_air", "id_bnd_air_external", "h_air_case", "Tair_case");
    convectiveFlux(model, "hf_oil", "id_bnd_oil_external", "h_oil_case", "Toil_case");
    convectiveFlux(model, "hf_flange", "id_bnd_flange_external", "h_flange_case", "Tair_case");

    model.study().create("std_solid_ht");
    model.study("std_solid_ht").create("stat", "Stationary");
    model.study("std_solid_ht").feature("stat").activate("ht_solid", true);
  }

  private static void addVariables(Model model) {
    model.component(COMP).variable().create("var_solid_heat");
    model.component(COMP).variable("var_solid_heat").set("rho_cu_T", "rho_cu_20*(1+alpha_cu*(T-293.15[K]))");
    model.component(COMP).variable("var_solid_heat").set("q_cu_solid", "Icase^2*rho_cu_T/A_conductor^2");
    model.component(COMP).variable("var_solid_heat").set("q_contact_solid", "Icase^2*Rc0*Rc_factor/V_contact");
    model.component(COMP).variable("var_solid_heat").set("Qdielectric_rip_ref", "omega0*eps0_solid_const*epsr_rip*tan_delta_rip*tan_delta_multiplier*(Vcase/(r_rip-r_conductor_outer))^2");
  }

  private static void addOperators(Model model) {
    maxop(model, "v3_max_T_all", "all");
    maxop(model, "v3_max_T_conductor", "id_dom_conductor_lower");
    maxop(model, "v3_max_T_rip", "id_dom_rip_core");
    maxop(model, "v3_max_T_contact", "id_dom_contact");
    maxop(model, "v3_max_T_silicone", "id_dom_silicone");
    maxop(model, "v3_max_T_flange", "id_dom_flange");
    intop(model, "v3_int_cu_lower", "id_dom_conductor_lower");
    intop(model, "v3_int_cu_upper", "id_dom_conductor_upper");
    intop(model, "v3_int_contact", "id_dom_contact");
    intop(model, "v3_int_rip", "id_dom_rip_core");
    intop(model, "v3_int_screens", "id_dom_screens");
    intop(model, "v3_int_air_bnd", "id_bnd_air_external");
    intop(model, "v3_int_air_terminal_bnd", "id_bnd_empty");
    intop(model, "v3_int_oil_bnd", "id_bnd_oil_external");
    intop(model, "v3_int_flange_bnd", "id_bnd_flange_external");
  }

  private static void addExplicitIdSelections(Model model) {
    explicit(model, "id_dom_hollow", 2, new int[]{1});
    explicit(model, "id_dom_conductor_lower", 2, new int[]{2});
    explicit(model, "id_dom_contact", 2, new int[]{3});
    explicit(model, "id_dom_conductor_upper", 2, new int[]{4});
    explicit(model, "id_dom_rip_core", 2, new int[]{5});
    explicit(model, "id_dom_terminal", 2, new int[]{6});
    explicit(model, "id_dom_screens", 2, new int[]{7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17});
    explicit(model, "id_dom_flange", 2, new int[]{18, 19, 20, 82});
    explicit(model, "id_dom_silicone", 2, range(21, 81));
    explicit(model, "id_bnd_air_external", 1, airBoundaryIds());
    explicit(model, "id_bnd_oil_external", 1, new int[]{63});
    explicit(model, "id_bnd_flange_external", 1, new int[]{231, 233, 318});
    explicit(model, "id_bnd_empty", 1, new int[]{});
  }

  private static void addMesh(Model model) {
    model.component(COMP).mesh().create("mesh_solid");
    model.component(COMP).mesh("mesh_solid").autoMeshSize(8);
  }

  private static void material(Model model, String tag, String label, String sel, String k, String rho, String cp, String epsr, String sigma) {
    model.component(COMP).material().create(tag, "Common");
    model.component(COMP).material(tag).label(label);
    model.component(COMP).material(tag).selection().named(sel);
    model.component(COMP).material(tag).propertyGroup("def").set("thermalconductivity", new String[]{k});
    model.component(COMP).material(tag).propertyGroup("def").set("density", rho);
    model.component(COMP).material(tag).propertyGroup("def").set("heatcapacity", cp);
    model.component(COMP).material(tag).propertyGroup("def").set("relpermittivity", new String[]{epsr});
    model.component(COMP).material(tag).propertyGroup("def").set("electricconductivity", new String[]{sigma});
  }

  private static void explicit(Model model, String tag, int dim, int[] ids) {
    model.component(COMP).selection().create(tag, "Explicit");
    model.component(COMP).selection(tag).geom(GEOM, dim);
    model.component(COMP).selection(tag).set(ids);
  }

  private static int[] range(int a, int b) {
    int[] ids = new int[b - a + 1];
    for (int i = 0; i < ids.length; i++) {
      ids[i] = a + i;
    }
    return ids;
  }

  private static int[] airBoundaryIds() {
    int[] high = range(206, 318);
    int[] tmp = new int[high.length + 3];
    tmp[0] = 14;
    tmp[1] = 16;
    tmp[2] = 28;
    for (int i = 0; i < high.length; i++) {
      tmp[i + 3] = high[i];
    }
    int keep = 0;
    for (int id : tmp) {
      if (id == 229 || id == 230 || id == 231 || id == 232 || id == 233 || id == 318) {
        continue;
      }
      keep++;
    }
    int[] ids = new int[keep];
    int j = 0;
    for (int id : tmp) {
      if (id == 229 || id == 230 || id == 231 || id == 232 || id == 233 || id == 318) {
        continue;
      }
      ids[j++] = id;
    }
    return ids;
  }

  private static void materialAll(Model model, String tag, String label, String k, String rho, String cp, String epsr, String sigma) {
    model.component(COMP).material().create(tag, "Common");
    model.component(COMP).material(tag).label(label);
    model.component(COMP).material(tag).selection().all();
    model.component(COMP).material(tag).propertyGroup("def").set("thermalconductivity", new String[]{k});
    model.component(COMP).material(tag).propertyGroup("def").set("density", rho);
    model.component(COMP).material(tag).propertyGroup("def").set("heatcapacity", cp);
    model.component(COMP).material(tag).propertyGroup("def").set("relpermittivity", new String[]{epsr});
    model.component(COMP).material(tag).propertyGroup("def").set("electricconductivity", new String[]{sigma});
  }

  private static void heatSource(Model model, String tag, String sel, String q0) {
    model.component(COMP).physics("ht_solid").create(tag, "HeatSource", 2);
    model.component(COMP).physics("ht_solid").feature(tag).selection().named(sel);
    model.component(COMP).physics("ht_solid").feature(tag).set("Q0", q0);
  }

  private static void convectiveFlux(Model model, String tag, String sel, String h, String text) {
    model.component(COMP).physics("ht_solid").create(tag, "HeatFluxBoundary", 1);
    model.component(COMP).physics("ht_solid").feature(tag).selection().named(sel);
    model.component(COMP).physics("ht_solid").feature(tag).set("HeatFluxType", "ConvectiveHeatFlux");
    model.component(COMP).physics("ht_solid").feature(tag).set("h", h);
    model.component(COMP).physics("ht_solid").feature(tag).set("Text", text);
  }

  private static void maxop(Model model, String tag, String sel) {
    model.component(COMP).cpl().create(tag, "Maximum");
    if ("all".equals(sel)) {
      model.component(COMP).cpl(tag).selection().all();
    } else {
      model.component(COMP).cpl(tag).selection().named(sel);
    }
  }

  private static void intop(Model model, String tag, String sel) {
    model.component(COMP).cpl().create(tag, "Integration");
    model.component(COMP).cpl(tag).selection().named(sel);
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
}
