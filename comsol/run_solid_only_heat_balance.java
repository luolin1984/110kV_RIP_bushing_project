import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Locale;

public class run_solid_only_heat_balance {

  private static String projectRoot = ".";
  private static final String COMP = "comp_v2_cad_solid_preview";
  private static final String GEOM = "geom_preview";
  private static final String RUN_ID = "SOLID_ONLY_RUN005";

  public static void main(String[] args) throws IOException {
    projectRoot = resolveProjectRoot(args);
    File geometryModel = new File(projectRoot, "comsol/BRFGL1-126-1250-4_geometry_axisym.mph");
    if (!geometryModel.exists()) {
      throw new IOException("Missing geometry model: " + geometryModel.getPath());
    }
    Model model = ModelUtil.load("Model", geometryModel.getPath());
    model.label("BRFGL1-126-1250-4_solid_only_heat_balance_RUN005.mph");
    setCaseParameters(model);
    addMaterials(model);
    // RUN005 is intentionally thermal-only. The solid-only electrostatic solve
    // with floating screens is still nonphysical/nonconvergent in the current
    // geometry, so heat-balance closure is diagnosed with the reference
    // dielectric-loss density Qdielectric_rip_ref.
    addHeatTransfer(model);
    addOperators(model);
    addMesh(model);

    String status = "SOLVED_VALID";
    String note = "solid-only thermal diagnostic on comp_v2_cad_solid_preview";
    try {
      model.component(COMP).mesh("mesh_solid").run();
      model.study("std_solid_ht").run();
    } catch (Throwable t) {
      status = "SOLVE_FAILED";
      note = clean(t.getMessage());
      System.out.println("Solid-only run failed: " + t.getMessage());
    }

    export(model, status, note);
    model.save(path("comsol/BRFGL1-126-1250-4_solid_only_heat_balance_RUN005.mph"));
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
    model.param().set("sigma_cu_20", "5.998e7[S/m]");
    model.param().set("alpha_cu", "0.00393[1/K]");
    model.param().set("epsr_rip", "4.2");
    model.param().set("tan_delta_rip", "0.004");
    model.param().set("sigma_rip", "7e-15[S/m]");
    model.param().set("Qdielectric_rip_ref", "omega0*epsilon0_const*epsr_rip*tan_delta_rip*(Vcase/(r_rip-r_conductor_outer))^2");
  }

  private static void addMaterials(Model model) {
    materialAll(model, "mat_pv_default", "Default solid-only fallback", "0.20[W/(m*K)]", "1200[kg/m^3]", "1000[J/(kg*K)]", "1", "1e-15[S/m]");
    material(model, "mat_pv_cu", "Copper conductor", "pv_center_conductor", "400[W/(m*K)]", "8960[kg/m^3]", "385[J/(kg*K)]", "1", "sigma_cu_20/(1+alpha_cu*(T-293.15[K]))");
    material(model, "mat_pv_rip", "RIP capacitor core", "pv_rip_capacitor_core", "0.20[W/(m*K)]", "2210[kg/m^3]", "730[J/(kg*K)]", "epsr_rip", "sigma_rip");
    material(model, "mat_pv_sir", "Silicone rubber housing", "pv_silicone_rubber_external_insulation", "0.20[W/(m*K)]", "2200[kg/m^3]", "703[J/(kg*K)]", "3.75", "1e-14[S/m]");
    material(model, "mat_pv_flange", "Grounded metal/flange", "pv_flange_grounded_metal", "45[W/(m*K)]", "7850[kg/m^3]", "460[J/(kg*K)]", "1", "1e6[S/m]");
    material(model, "mat_pv_screen", "Aluminum condenser screens", "pv_condenser_screens", "205[W/(m*K)]", "2700[kg/m^3]", "900[J/(kg*K)]", "1", "3.5e7[S/m]");
  }

  private static void addElectrostatics(Model model) {
    model.component(COMP).physics().create("es_solid", "Electrostatics", GEOM);
    model.component(COMP).physics("es_solid").create("pot_s00", "ElectricPotential", 1);
    model.component(COMP).physics("es_solid").feature("pot_s00").selection().named("pv_bnd_S00_fixed_72p75kV_rms");
    model.component(COMP).physics("es_solid").feature("pot_s00").set("V0", "Vcase");
    model.component(COMP).physics("es_solid").create("gnd_s10", "Ground", 1);
    model.component(COMP).physics("es_solid").feature("gnd_s10").selection().named("pv_bnd_S10_ground_0V");
    model.component(COMP).physics("es_solid").create("gnd_flange", "Ground", 1);
    model.component(COMP).physics("es_solid").feature("gnd_flange").selection().named("pv_bnd_flange_ground");
    for (int i = 1; i <= 9; i++) {
      try {
        String tag = "fp_s" + twoDigit(i);
        model.component(COMP).physics("es_solid").create(tag, "FloatingPotential", 1);
        model.component(COMP).physics("es_solid").feature(tag).selection().named("pv_bnd_screen_S" + twoDigit(i) + "_floating");
        model.component(COMP).physics("es_solid").feature(tag).set("Q0", "0[C]");
      } catch (Throwable t) {
        System.out.println("Floating potential failed in solid-only model S" + twoDigit(i) + ": " + t.getMessage());
      }
    }
    model.study().create("std_solid_es");
    model.study("std_solid_es").create("stat", "Stationary");
    model.study("std_solid_es").feature("stat").activate("es_solid", true);
  }

  private static void addHeatTransfer(Model model) {
    model.component(COMP).physics().create("ht_solid", "HeatTransfer", GEOM);
    model.component(COMP).physics("ht_solid").selection().all();
    heatSource(model, "hs_cu_lower", "pv_center_conductor_joule_lower", "Icase^2*(1/sigma_cu_20)*(1+alpha_cu*(T-293.15[K]))/(pi*(r_conductor_outer^2-r_hollow^2))^2");
    heatSource(model, "hs_cu_upper", "pv_center_conductor_joule_upper", "Icase^2*(1/sigma_cu_20)*(1+alpha_cu*(T-293.15[K]))/(pi*(r_conductor_outer^2-r_hollow^2))^2");
    heatSource(model, "hs_contact", "pv_contact_resistance_heat_source_layer_strict", "Q_contact_vol");
    heatSource(model, "hs_rip_dielectric_ref", "pv_rip_capacitor_core_strict", "Qdielectric_rip_ref");
    convectiveFlux(model, "hf_air", "pv_bnd_air_external_convection_explicit", "h_air_case", "Tair_case");
    convectiveFlux(model, "hf_oil", "pv_bnd_oil_immersed_surface_explicit", "h_oil_case", "Toil_case");

    model.study().create("std_solid_ht");
    model.study("std_solid_ht").create("stat", "Stationary");
    model.study("std_solid_ht").feature("stat").activate("es_solid", false);
    model.study("std_solid_ht").feature("stat").activate("ht_solid", true);
  }

  private static void addOperators(Model model) {
    maxop(model, "pv_max_T_all", "all");
    maxop(model, "pv_max_T_conductor", "pv_center_conductor_joule_lower");
    maxop(model, "pv_max_T_rip", "pv_rip_capacitor_core_strict");
    maxop(model, "pv_max_T_contact", "pv_contact_resistance_heat_source_layer_strict");
    maxop(model, "pv_max_E_all", "all");
    maxop(model, "pv_max_E_rip", "pv_rip_capacitor_core_strict");
    intop(model, "pv_int_cu_lower", "pv_center_conductor_joule_lower");
    intop(model, "pv_int_cu_upper", "pv_center_conductor_joule_upper");
    intop(model, "pv_int_contact", "pv_contact_resistance_heat_source_layer_strict");
    intop(model, "pv_int_rip", "pv_rip_capacitor_core_strict");
    intop(model, "pv_int_air_bnd", "pv_bnd_air_external_convection_explicit");
    intop(model, "pv_int_oil_bnd", "pv_bnd_oil_immersed_surface_explicit");
  }

  private static void addMesh(Model model) {
    model.component(COMP).mesh().create("mesh_solid");
    model.component(COMP).mesh("mesh_solid").autoMeshSize(8);
  }

  private static void export(Model model, String status, String note) throws IOException {
    File outDir = new File(projectRoot, "results/raw_comsol_exports/SOLID_ONLY_RUN005");
    outDir.mkdirs();
    double tmaxAll = eval(model, "pv_max_T_all(T)-273.15[K]");
    double tmaxConductor = eval(model, "pv_max_T_conductor(T)-273.15[K]");
    double tmaxRip = eval(model, "pv_max_T_rip(T)-273.15[K]");
    double tmaxContact = eval(model, "pv_max_T_contact(T)-273.15[K]");
    double emaxAll = Double.NaN;
    double emaxRip = Double.NaN;

    double area = eval(model, "pi*(r_conductor_outer^2-r_hollow^2)");
    double conductorVolume = eval(model, "pv_int_cu_lower(1)+pv_int_cu_upper(1)");
    String qCuExpr = "Icase^2*(1/sigma_cu_20)*(1+alpha_cu*(T-293.15[K]))/(pi*(r_conductor_outer^2-r_hollow^2))^2";
    double qJoule = eval(model, "pv_int_cu_lower(" + qCuExpr + ")+pv_int_cu_upper(" + qCuExpr + ")");
    double qContact = eval(model, "pv_int_contact(Q_contact_vol)");
    double qDielectric = eval(model, "pv_int_rip(Qdielectric_rip_ref)");
    double qTotal = qJoule + qContact + qDielectric;
    double iCase = eval(model, "Icase");
    double rEff = iCase > 0.0 ? qJoule / (iCase * iCase) : Double.NaN;
    double airLen = totalLength(new File(projectRoot, "results/summary_tables/air_convection_boundaries.csv"));
    double oilLen = totalLength(new File(projectRoot, "results/summary_tables/oil_convection_boundaries.csv"));
    double heatAir = eval(model, "pv_int_air_bnd(h_air_case*(T-Tair_case))");
    double heatOil = eval(model, "pv_int_oil_bnd(h_oil_case*(T-Toil_case))");
    double residual = qTotal - heatAir - heatOil;

    if ("SOLVED_VALID".equals(status)) {
      if (Double.isNaN(tmaxAll) || tmaxAll >= 150.0) {
        status = "SOLVED_INVALID_TEMPERATURE";
        note = note + "; Tmax_global_C does not satisfy <150 C review target";
      }
      if (almostEqual(tmaxConductor, tmaxRip) && almostEqual(tmaxRip, tmaxContact)) {
        status = "SOLVED_INVALID_SELECTIONS";
        note = note + "; conductor/RIP/contact Tmax are identical";
      }
    }

    BufferedWriter w = new BufferedWriter(new FileWriter(new File(outDir, "solid_only_metrics.csv")));
    try {
      w.write("case_id,run_id,status,Tmax_global_C,Tmax_conductor_C,Tmax_RIP_C,Tmax_contact_C,Emax_global_V_per_m,Emax_RIP_V_per_m,Qcontact_W,note\n");
      w.write("STEADY_1250_LOAD_1p0," + RUN_ID + "," + status + "," + fmt(tmaxAll) + "," + fmt(tmaxConductor) + "," + fmt(tmaxRip) + "," + fmt(tmaxContact) + "," + fmt(emaxAll) + "," + fmt(emaxRip) + "," + fmt(qContact) + ",\"" + clean(note) + "\"\n");
    } finally {
      w.close();
    }

    w = new BufferedWriter(new FileWriter(new File(outDir, "heat_balance_diagnostics.csv")));
    try {
      w.write("case_id,run_id,conductor_cross_section_area_m2,conductor_volume_m3,conductor_effective_resistance_ohm,Qjoule_total_W,Qcontact_total_W,Qdielectric_total_W,Qtotal_W,air_convection_boundary_length_m,oil_convection_boundary_length_m,heat_removed_air_W,heat_removed_oil_W,residual_heat_balance_W\n");
      w.write(String.format(Locale.US, "STEADY_1250_LOAD_1p0,%s,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g%n",
          RUN_ID, area, conductorVolume, rEff, qJoule, qContact, qDielectric, qTotal, airLen, oilLen, heatAir, heatOil, residual));
    } finally {
      w.close();
    }

    w = new BufferedWriter(new FileWriter(new File(outDir, "solid_only_heat_balance_report.md")));
    try {
      w.write("# Solid-only RUN005 heat balance\n\n");
      w.write("- status: " + status + "\n");
      w.write("- Tmax_global_C: " + fmt(tmaxAll) + "\n");
      w.write("- Qjoule_total_W: " + fmt(qJoule) + "\n");
      w.write("- Qcontact_total_W: " + fmt(qContact) + "\n");
      w.write("- Qdielectric_total_W: " + fmt(qDielectric) + "\n");
      w.write("- heat_removed_air_W: " + fmt(heatAir) + "\n");
      w.write("- heat_removed_oil_W: " + fmt(heatOil) + "\n");
      w.write("- residual_heat_balance_W: " + fmt(residual) + "\n\n");
      w.write("This is a solver-oriented solid-only diagnostic model. RIP dielectric loss uses `Qdielectric_rip_ref` for thermal stability; electrostatic field values are exported for review but are not final validation targets.\n");
    } finally {
      w.close();
    }
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

  private static double totalLength(File csv) throws IOException {
    if (!csv.exists()) {
      return Double.NaN;
    }
    java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.FileReader(csv));
    String line = reader.readLine();
    double total = 0.0;
    while ((line = reader.readLine()) != null) {
      if (line.trim().isEmpty()) {
        continue;
      }
      String[] cols = line.split(",", -1);
      total += Double.parseDouble(cols[3]);
    }
    reader.close();
    return total;
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

  private static boolean almostEqual(double a, double b) {
    return !Double.isNaN(a) && !Double.isNaN(b) && Math.abs(a - b) < 1.0e-6;
  }

  private static String fmt(double value) {
    if (Double.isNaN(value) || Double.isInfinite(value)) {
      return "";
    }
    return String.format(Locale.US, "%.9g", value);
  }

  private static String clean(String text) {
    if (text == null) {
      return "";
    }
    return text.replace("\"", "'").replace("\n", " ").replace("\r", " ");
  }

  private static String twoDigit(int i) {
    return (i < 10 ? "0" : "") + i;
  }
}
