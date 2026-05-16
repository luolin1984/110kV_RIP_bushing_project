import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

public class build_physics_brfgl1 {

  public static String projectRoot = ".";

  public static void main(String[] args) throws IOException {
    Model model = build(args);
    model.save(path("comsol/BRFGL1-126-1250-4_physics_baseline.mph"));
  }

  public static Model build(String[] args) throws IOException {
    projectRoot = resolveProjectRoot(args);
    File geometryModel = new File(projectRoot, "comsol/BRFGL1-126-1250-4_geometry_axisym.mph");
    if (!geometryModel.exists()) {
      throw new IOException("Missing geometry model: " + geometryModel.getPath()
          + ". Run comsol/run_build_geometry_brfgl1.sh first.");
    }
    Model model = ModelUtil.load("Model", geometryModel.getPath());
    model.label("BRFGL1-126-1250-4_physics_baseline.mph");
    setCaseParameters(model);
    addMaterials(model);
    addElectrostatics(model);
    addHeatTransfer(model);
    addStudies(model);
    addOperators(model);
    addMesh(model);
    return model;
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
    model.param().set("h_air_case", "12[W/(m^2*K)] + 8[W/(m^2*K)]*(wind_case/(1[m/s]))^0.8");
    model.param().set("h_oil_case", "300[W/(m^2*K)]");
    model.param().set("sigma_cu_20", "5.998e7[S/m]");
    model.param().set("alpha_cu", "0.00393[1/K]");
    model.param().set("epsr_rip", "4.2");
    model.param().set("tan_delta_rip", "0.004");
    model.param().set("sigma_rip", "7e-15[S/m]");
    model.param().set("Qjoule_cu_ref", "Icase^2*(1/sigma_cu_20)/(pi*(r_conductor_outer^2-r_hollow^2))^2");
    model.param().set("Qdielectric_rip_ref", "omega0*epsilon0_const*epsr_rip*tan_delta_rip*(Vcase/(r_rip-r_conductor_outer))^2");
  }

  private static void addMaterials(Model model) {
    materialAll(model, "mat_default", "Default numerical background", "0.20[W/(m*K)]", "1200[kg/m^3]", "1000[J/(kg*K)]", "1", "1e-15[S/m]");
    material(model, "mat_cu", "Copper conductor", "v2_center_conductor", "400[W/(m*K)]", "8960[kg/m^3]", "385[J/(kg*K)]", "1", "sigma_cu_20/(1+alpha_cu*(T-293.15[K]))");
    material(model, "mat_rip", "RIP capacitor core", "v2_rip_capacitor_core", "0.20[W/(m*K)]", "2210[kg/m^3]", "730[J/(kg*K)]", "epsr_rip", "sigma_rip");
    material(model, "mat_sir", "Silicone rubber housing", "v2_silicone_rubber_external_insulation", "0.20[W/(m*K)]", "2200[kg/m^3]", "703[J/(kg*K)]", "3.75", "1e-14[S/m]");
    material(model, "mat_flange", "Grounded metal/flange", "v2_flange_grounded_metal", "45[W/(m*K)]", "7850[kg/m^3]", "460[J/(kg*K)]", "1", "1e6[S/m]");
    material(model, "mat_air_main", "Surrounding air main", "v2_surrounding_air_main_domain", "0.026[W/(m*K)]", "1.2[kg/m^3]", "1005[J/(kg*K)]", "1", "1e-15[S/m]");
    material(model, "mat_air_terminal", "Surrounding air above terminal", "v2_surrounding_air_terminal_domain", "0.026[W/(m*K)]", "1.2[kg/m^3]", "1005[J/(kg*K)]", "1", "1e-15[S/m]");
    material(model, "mat_oil_main", "Transformer oil main", "v2_surrounding_oil_main_domain", "0.12[W/(m*K)]", "850[kg/m^3]", "1900[J/(kg*K)]", "2.2", "1e-12[S/m]");
    material(model, "mat_oil_near_flange", "Transformer oil near flange", "v2_surrounding_oil_near_flange_domain", "0.12[W/(m*K)]", "850[kg/m^3]", "1900[J/(kg*K)]", "2.2", "1e-12[S/m]");
    material(model, "mat_screen", "Aluminum condenser screens", "v2_condenser_screens", "205[W/(m*K)]", "2700[kg/m^3]", "900[J/(kg*K)]", "1", "3.5e7[S/m]");
  }

  private static void addElectrostatics(Model model) {
    model.component("comp_v2").physics().create("es", "Electrostatics", "geom_v2");
    model.component("comp_v2").physics("es").create("pot_s00", "ElectricPotential", 1);
    model.component("comp_v2").physics("es").feature("pot_s00").selection().named("v2_bnd_S00_fixed_72p75kV_rms");
    model.component("comp_v2").physics("es").feature("pot_s00").set("V0", "Vcase");
    model.component("comp_v2").physics("es").create("gnd_s10", "Ground", 1);
    model.component("comp_v2").physics("es").feature("gnd_s10").selection().named("v2_bnd_S10_ground_0V");
    model.component("comp_v2").physics("es").create("gnd_flange", "Ground", 1);
    model.component("comp_v2").physics("es").feature("gnd_flange").selection().named("v2_bnd_flange_ground");
    for (int i = 1; i <= 9; i++) {
      String tag = "fp_s" + twoDigit(i);
      try {
        model.component("comp_v2").physics("es").create(tag, "FloatingPotential", 1);
        model.component("comp_v2").physics("es").feature(tag).selection().named("v2_bnd_screen_S" + twoDigit(i) + "_floating");
        model.component("comp_v2").physics("es").feature(tag).set("Q0", "0[C]");
      } catch (Throwable t) {
        System.out.println("Floating potential creation failed for S" + twoDigit(i) + ": " + t.getMessage());
      }
    }
  }

  private static void addHeatTransfer(Model model) {
    model.component("comp_v2").physics().create("ht", "HeatTransfer", "geom_v2");
    model.component("comp_v2").physics("ht").selection().named("v2_thermal_solid_domains");
    heatSource(model, "hs_cu_lower", "v2_center_conductor_joule_lower", "Icase^2*(1/sigma_cu_20)*(1+alpha_cu*(T-293.15[K]))/(pi*(r_conductor_outer^2-r_hollow^2))^2");
    heatSource(model, "hs_cu_upper", "v2_center_conductor_joule_upper", "Icase^2*(1/sigma_cu_20)*(1+alpha_cu*(T-293.15[K]))/(pi*(r_conductor_outer^2-r_hollow^2))^2");
    heatSource(model, "hs_contact", "v2_contact_resistance_heat_source_layer_strict", "Q_contact_vol");
    heatSource(model, "hs_rip_dielectric", "v2_rip_capacitor_core_strict", "omega0*epsilon0_const*epsr_rip*tan_delta_rip*es.normE^2");
    convectiveFlux(model, "hf_air", "v2_bnd_air_external_convection_explicit", "h_air_case", "Tair_case");
    convectiveFlux(model, "hf_oil", "v2_bnd_oil_immersed_surface_explicit", "h_oil_case", "Toil_case");
  }

  private static void addStudies(Model model) {
    model.study().create("std_es");
    model.study("std_es").create("stat", "Stationary");
    model.study("std_es").feature("stat").activate("es", true);
    model.study("std_es").feature("stat").activate("ht", false);
    model.study("std_es").feature("stat").set("solnum", "auto");

    model.study().create("std_ht");
    model.study("std_ht").create("stat", "Stationary");
    model.study("std_ht").feature("stat").activate("es", false);
    model.study("std_ht").feature("stat").activate("ht", true);

    model.study().create("std_cpl");
    model.study("std_cpl").create("stat", "Stationary");
    model.study("std_cpl").feature("stat").activate("es", true);
    model.study("std_cpl").feature("stat").activate("ht", true);
  }

  private static void addOperators(Model model) {
    maxop(model, "maxop_T_all", "geom_v2", "all");
    maxop(model, "maxop_T_conductor", "geom_v2", "v2_center_conductor_joule_lower");
    maxop(model, "maxop_T_rip", "geom_v2", "v2_rip_capacitor_core_strict");
    maxop(model, "maxop_T_contact", "geom_v2", "v2_contact_resistance_heat_source_layer_strict");
    maxop(model, "maxop_T_flange", "geom_v2", "v2_flange_grounded_metal_strict");
    maxop(model, "maxop_T_silicone", "geom_v2", "v2_silicone_rubber_external_insulation_strict");
    maxop(model, "maxop_E_all", "geom_v2", "all");
    maxop(model, "maxop_E_rip", "geom_v2", "v2_rip_capacitor_core_strict");
    maxop(model, "maxop_E_screen_probe", "geom_v2", "v2_condenser_screens");
  }

  private static void addMesh(Model model) {
    model.component("comp_v2").mesh().create("mesh1");
    model.component("comp_v2").mesh("mesh1").autoMeshSize(9);
  }

  private static void material(Model model, String tag, String label, String sel, String k, String rho, String cp, String epsr, String sigma) {
    model.component("comp_v2").material().create(tag, "Common");
    model.component("comp_v2").material(tag).label(label);
    model.component("comp_v2").material(tag).selection().named(sel);
    model.component("comp_v2").material(tag).propertyGroup("def").set("thermalconductivity", new String[]{k});
    model.component("comp_v2").material(tag).propertyGroup("def").set("density", rho);
    model.component("comp_v2").material(tag).propertyGroup("def").set("heatcapacity", cp);
    model.component("comp_v2").material(tag).propertyGroup("def").set("relpermittivity", new String[]{epsr});
    model.component("comp_v2").material(tag).propertyGroup("def").set("electricconductivity", new String[]{sigma});
  }

  private static void materialAll(Model model, String tag, String label, String k, String rho, String cp, String epsr, String sigma) {
    model.component("comp_v2").material().create(tag, "Common");
    model.component("comp_v2").material(tag).label(label);
    model.component("comp_v2").material(tag).selection().all();
    model.component("comp_v2").material(tag).propertyGroup("def").set("thermalconductivity", new String[]{k});
    model.component("comp_v2").material(tag).propertyGroup("def").set("density", rho);
    model.component("comp_v2").material(tag).propertyGroup("def").set("heatcapacity", cp);
    model.component("comp_v2").material(tag).propertyGroup("def").set("relpermittivity", new String[]{epsr});
    model.component("comp_v2").material(tag).propertyGroup("def").set("electricconductivity", new String[]{sigma});
  }

  private static void heatSource(Model model, String tag, String sel, String q0) {
    model.component("comp_v2").physics("ht").create(tag, "HeatSource", 2);
    model.component("comp_v2").physics("ht").feature(tag).selection().named(sel);
    model.component("comp_v2").physics("ht").feature(tag).set("Q0", q0);
  }

  private static void convectiveFlux(Model model, String tag, String sel, String h, String text) {
    try {
      model.component("comp_v2").physics("ht").create(tag, "HeatFluxBoundary", 1);
      model.component("comp_v2").physics("ht").feature(tag).selection().named(sel);
      model.component("comp_v2").physics("ht").feature(tag).set("HeatFluxType", "ConvectiveHeatFlux");
      model.component("comp_v2").physics("ht").feature(tag).set("h", h);
      model.component("comp_v2").physics("ht").feature(tag).set("Text", text);
    } catch (Throwable t) {
      System.out.println("Convective heat-flux feature failed for " + tag + ": " + t.getMessage());
    }
  }

  private static void addCadConvectiveFluxes(Model model, String featurePrefix, String selectionPrefix,
      String csvPath, String h, String text, double minZ, double maxZ) {
    BufferedReader reader = null;
    try {
      reader = new BufferedReader(new FileReader(csvPath));
      String line = reader.readLine();
      int idx = 0;
      while ((line = reader.readLine()) != null) {
        if (line.trim().isEmpty()) {
          continue;
        }
        String[] cols = line.split(",", -1);
        double z0 = Math.max(Double.parseDouble(cols[1]), minZ);
        double z1 = Math.min(Double.parseDouble(cols[2]), maxZ);
        if (z1 <= z0) {
          continue;
        }
        convectiveFlux(model, featurePrefix + threeDigit(idx), selectionPrefix + threeDigit(idx), h, text);
        idx++;
      }
    } catch (Throwable t) {
      System.out.println("CAD convective heat-flux setup failed for " + featurePrefix + ": " + t.getMessage());
    } finally {
      if (reader != null) {
        try {
          reader.close();
        } catch (Throwable ignored) {
        }
      }
    }
  }

  private static void temperatureBoundary(Model model, String tag, String sel, String temperature) {
    try {
      model.component("comp_v2").physics("ht").create(tag, "TemperatureBoundary", 1);
      model.component("comp_v2").physics("ht").feature(tag).selection().named(sel);
      model.component("comp_v2").physics("ht").feature(tag).set("T0", temperature);
    } catch (Throwable t) {
      System.out.println("Temperature boundary feature failed for " + tag + ": " + t.getMessage());
    }
  }

  private static void maxop(Model model, String tag, String geom, String sel) {
    model.component("comp_v2").cpl().create(tag, "Maximum");
    if (!"all".equals(sel)) {
      model.component("comp_v2").cpl(tag).selection().named(sel);
    } else {
      model.component("comp_v2").cpl(tag).selection().all();
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

  private static String twoDigit(int i) {
    return (i < 10 ? "0" : "") + i;
  }

  private static String threeDigit(int i) {
    if (i < 10) {
      return "00" + i;
    }
    if (i < 100) {
      return "0" + i;
    }
    return "" + i;
  }
}
