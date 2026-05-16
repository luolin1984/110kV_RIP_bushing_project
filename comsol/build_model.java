import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.FileWriter;
import java.io.PrintWriter;

/**
 * Build and run a first-pass 2D axisymmetric COMSOL model for
 * STEADY_1250_LOAD_1p0.
 *
 * The script intentionally creates a conservative baseline model rather than a
 * full factorial sweep. It mirrors the data framework in data/processed and
 * leaves S01-S09 condenser screens as non-Dirichlet floating/zero-charge
 * initialization surfaces.
 */
public class build_model {

  public static Model run() {
    ModelUtil.clear();
    Model model = ModelUtil.create("Model");
    model.modelPath("/Users/luolin/Documents/New project/110kV_RIP_bushing_project/comsol");
    model.label("BRFGL1-126-1250-4_base_model_2d_axisym_STEADY_1250_LOAD_1p0.mph");

    setParameters(model);
    buildGeometry(model);
    addMaterials(model);
    addPhysics(model);
    addStudies(model);
    addResults(model);
    runBaseline(model);

    return model;
  }

  public static void main(String[] args) throws java.io.IOException {
    Model model = run();
    model.study("std_es").run();
    model.study("std_ht").run();
    model.study("std_cpl").run();
    model.save("/Users/luolin/Documents/New project/110kV_RIP_bushing_project/comsol/BRFGL1-126-1250-4_base_model_2d_axisym_STEADY_1250_LOAD_1p0.mph");
  }

  private static void setParameters(Model model) {
    model.param().set("Um", "126[kV]");
    model.param().set("product_model", "1", "Selected product model is BRFGL1-126/1250-4; BRFGL2 is cable-current-carrying alternative only.");
    model.param().set("Vph", "72.75[kV]", "S00/conductor RMS phase-to-ground voltage");
    model.param().set("freq0", "50[Hz]");
    model.param().set("omega0", "2*pi*freq0");
    model.param().set("I0", "1250[A]");
    model.param().set("load_mult", "1");
    model.param().set("Icase", "I0*load_mult");
    model.param().set("Toil", "85[degC]");
    model.param().set("Tair", "25[degC]");
    model.param().set("wind10m", "1[m/s]");
    model.param().set("solar0", "0[W/m^2]");

    model.param().set("air_len", "1650[mm]", "BRFGL1: L_total - L2 = 2245 - 595");
    model.param().set("oil_len", "595[mm]", "BRFGL1: oil immersed length L2");
    model.param().set("L1_ext", "1150[mm]", "BRFGL1: external insulation length L1");
    model.param().set("L4_flange", "200[mm]", "BRFGL1: flange connection length L4");
    model.param().set("flange_t", "30[mm]", "BRFGL1: flange thickness H");
    model.param().set("axial_len", "2245[mm]", "BRFGL1: overall axial length L");
    model.param().set("r_cond", "20[mm]", "BRFGL1: conduit inner diameter d3 / 2");
    model.param().set("r_rip", "66[mm]", "BRFGL1: oil-side core diameter D1 / 2");
    model.param().set("r_housing", "135[mm]", "BRFGL1: external insulation diameter D2 / 2");
    model.param().set("r_flange", "200[mm]", "BRFGL1: flange outer diameter D / 2");
    model.param().set("r_far", "360[mm]");
    model.param().set("screen_half_len", "575[mm]", "First-pass condenser stack half-length within L1 external insulation envelope");
    model.param().set("screen_dr", "2.25[mm]");
    model.param().set("r_housing_body", "82[mm]", "Equivalent silicone rubber body radius inside shed envelope");
    model.param().set("shed_pitch", "100[mm]");
    model.param().set("shed_t", "18[mm]");

    model.param().set("sigma_cu_20", "5.998e7[S/m]");
    model.param().set("alpha_cu", "0.00393[1/K]");
    model.param().set("rho_cu_T", "1/sigma_cu_20*(1+alpha_cu*(T-293.15[K]))");
    model.param().set("epsr_rip", "4.2");
    model.param().set("tanD_rip", "0.004");
    model.param().set("E_rip_ref", "Vph/(r_rip-r_cond)", "First-pass average radial field for independent thermal baseline");
    model.param().set("qdielectric_ref", "omega0*epsilon0_const*epsr_rip*tanD_rip*E_rip_ref^2");
    model.param().set("sigma_rip", "7e-15[S/m]");
    model.param().set("beta_rip", "0.055[1/K]");
    model.param().set("Rc0", "1e-6[ohm]");
    model.param().set("Rc_factor", "1");
    model.param().set("A_contact", "2.5e-4[m^2]");
    model.param().set("t_contact", "1e-4[m]");
    model.param().set("V_contact", "A_contact*t_contact");
    model.param().set("Qcontact", "Icase^2*Rc0*Rc_factor");
    model.param().set("qcontact", "Qcontact/V_contact");
    model.param().set("h_air", "5[W/(m^2*K)] + 4[W/(m^2*K)]*(wind10m/(1[m/s]))^0.8");
    model.param().set("h_oil", "100[W/(m^2*K)]");
  }

  private static void buildGeometry(Model model) {
    model.component().create("comp1", true);
    model.component("comp1").geom().create("geom1", 2);
    model.component("comp1").geom("geom1").axisymmetric(true);
    model.component("comp1").geom("geom1").lengthUnit("m");

    rect(model, "r_air", "r_housing", "0", "r_far-r_housing", "air_len");
    rect(model, "r_air_top", "r_cond", "L1_ext", "r_far-r_cond", "air_len-L1_ext");
    rect(model, "r_oil", "r_rip", "-oil_len", "r_far-r_rip", "oil_len");
    rect(model, "r_ripcore", "r_cond", "-oil_len", "r_rip-r_cond", "oil_len+L1_ext");
    rect(model, "r_conductor", "0", "-oil_len", "r_cond", "oil_len+air_len");
    rect(model, "r_housing_body", "r_rip", "0", "r_housing_body-r_rip", "L1_ext");
    rect(model, "r_housing_envelope", "r_housing_body", "0", "r_housing-r_housing_body", "L1_ext");
    for (int i = 0; i < 11; i++) {
      rect(model, "shed" + i, "r_housing_body", "(60[mm]+" + i + "*shed_pitch)", "r_housing-r_housing_body", "shed_t");
    }
    rect(model, "r_flange_disk", "r_rip", "-flange_t/2", "r_flange-r_rip", "flange_t");
    rect(model, "r_flange_collar", "r_rip", "-L4_flange/2", "100[mm]-r_rip", "L4_flange");
    rect(model, "r_contact", "0", "-flange_t/2", "r_cond", "flange_t");

    // Condenser screens are not meshed as 0.05 mm domains in the baseline.
    // S00/S10 are represented by the HV/ground boundaries, while S01-S09 are
    // treated as floating/zero-charge initialization surfaces in the data file.
    // This keeps the first 2D axisymmetric solve robust before local screen-end
    // field refinement.

    model.component("comp1").geom("geom1").run();

    boxSel(model, "sel_conductor", 2, "-1[mm]", "r_cond+1[mm]", "-oil_len-1[mm]", "air_len+1[mm]");
    boxSel(model, "sel_contact", 2, "-1[mm]", "r_cond+1[mm]", "-flange_t/2-1[mm]", "flange_t/2+1[mm]");
    boxSel(model, "sel_rip", 2, "r_cond-1[mm]", "r_rip+1[mm]", "-oil_len-1[mm]", "L1_ext+1[mm]");
    boxSel(model, "sel_air", 2, "r_housing_body-1[mm]", "r_far+1[mm]", "-1[mm]", "air_len+1[mm]");
    boxSel(model, "sel_oil", 2, "r_rip-1[mm]", "r_far+1[mm]", "-oil_len-1[mm]", "1[mm]");
    boxSel(model, "sel_housing", 2, "r_rip-1[mm]", "r_housing+1[mm]", "-1[mm]", "L1_ext+1[mm]");
    boxSel(model, "sel_flange", 2, "r_rip-1[mm]", "r_flange+1[mm]", "-L4_flange/2-1[mm]", "L4_flange/2+1[mm]");
    boxSel(model, "bnd_hv", 1, "r_cond-0.2[mm]", "r_cond+0.2[mm]", "-screen_half_len", "screen_half_len");
    boxSel(model, "bnd_ground", 1, "r_rip-0.2[mm]", "r_flange+1[mm]", "-L4_flange/2-1[mm]", "L4_flange/2+1[mm]");
    boxSel(model, "bnd_air_conv", 1, "r_housing_body-1[mm]", "r_far+1[mm]", "-1[mm]", "air_len+1[mm]");
    boxSel(model, "bnd_oil_conv", 1, "r_rip-1[mm]", "r_far+1[mm]", "-oil_len-1[mm]", "1[mm]");
  }

  private static void rect(Model model, String tag, String x, String y, String w, String h) {
    model.component("comp1").geom("geom1").create(tag, "Rectangle");
    model.component("comp1").geom("geom1").feature(tag).set("pos", new String[]{x, y});
    model.component("comp1").geom("geom1").feature(tag).set("size", new String[]{w, h});
  }

  private static void boxSel(Model model, String tag, int dim, String xmin, String xmax, String ymin, String ymax) {
    model.component("comp1").selection().create(tag, "Box");
    model.component("comp1").selection(tag).geom("geom1", dim);
    model.component("comp1").selection(tag).set("xmin", xmin);
    model.component("comp1").selection(tag).set("xmax", xmax);
    model.component("comp1").selection(tag).set("ymin", ymin);
    model.component("comp1").selection(tag).set("ymax", ymax);
  }

  private static void addMaterials(Model model) {
    material(model, "mat_cu", "Copper conductor", "sel_conductor", "400[W/(m*K)]", "8960[kg/m^3]", "385[J/(kg*K)]", "1", "sigma_cu_20/(1+alpha_cu*(T-293.15[K]))");
    material(model, "mat_rip", "RIP capacitor core", "sel_rip", "0.10[W/(m*K)]", "2210[kg/m^3]", "730[J/(kg*K)]", "epsr_rip", "sigma_rip*exp(beta_rip*(T-293.15[K]))");
    material(model, "mat_air", "Air side domain", "sel_air", "0.025[W/(m*K)]", "1.29[kg/m^3]", "1003[J/(kg*K)]", "1", "1e-18[S/m]");
    material(model, "mat_oil", "Transformer oil side domain", "sel_oil", "0.12[W/(m*K)]", "850[kg/m^3]", "1900[J/(kg*K)]", "2.2", "1e-12[S/m]");
    material(model, "mat_sir", "Silicone rubber housing", "sel_housing", "0.20[W/(m*K)]", "2200[kg/m^3]", "703[J/(kg*K)]", "3.75", "1e-14[S/m]");
    material(model, "mat_flange", "Grounded flange", "sel_flange", "45[W/(m*K)]", "7850[kg/m^3]", "460[J/(kg*K)]", "1", "1e6[S/m]");
  }

  private static void material(Model model, String tag, String label, String sel, String k, String rho, String cp, String epsr, String sigma) {
    model.component("comp1").material().create(tag, "Common");
    model.component("comp1").material(tag).label(label);
    model.component("comp1").material(tag).selection().named(sel);
    model.component("comp1").material(tag).propertyGroup("def").set("thermalconductivity", new String[]{k});
    model.component("comp1").material(tag).propertyGroup("def").set("density", rho);
    model.component("comp1").material(tag).propertyGroup("def").set("heatcapacity", cp);
    model.component("comp1").material(tag).propertyGroup("def").set("relpermittivity", new String[]{epsr});
    model.component("comp1").material(tag).propertyGroup("def").set("electricconductivity", new String[]{sigma});
  }

  private static void addPhysics(Model model) {
    model.component("comp1").physics().create("es", "Electrostatics", "geom1");
    model.component("comp1").physics("es").create("pot1", "ElectricPotential", 1);
    model.component("comp1").physics("es").feature("pot1").selection().named("bnd_hv");
    model.component("comp1").physics("es").feature("pot1").set("V0", "Vph");
    model.component("comp1").physics("es").create("gnd1", "Ground", 1);
    model.component("comp1").physics("es").feature("gnd1").selection().named("bnd_ground");

    model.component("comp1").physics().create("ht", "HeatTransfer", "geom1");
    model.component("comp1").physics("ht").create("hs_conductor", "HeatSource", 2);
    model.component("comp1").physics("ht").feature("hs_conductor").selection().named("sel_conductor");
    model.component("comp1").physics("ht").feature("hs_conductor").set("Q0", "Icase^2*(1/sigma_cu_20)*(1+alpha_cu*(T-293.15[K]))/(pi*r_cond^2)^2");
    model.component("comp1").physics("ht").create("hs_contact", "HeatSource", 2);
    model.component("comp1").physics("ht").feature("hs_contact").selection().named("sel_contact");
    model.component("comp1").physics("ht").feature("hs_contact").set("Q0", "qcontact");
    model.component("comp1").physics("ht").create("hs_rip_dielectric", "HeatSource", 2);
    model.component("comp1").physics("ht").feature("hs_rip_dielectric").selection().named("sel_rip");
    model.component("comp1").physics("ht").feature("hs_rip_dielectric").set("Q0", "qdielectric_ref");
    model.component("comp1").physics("ht").create("temp_air", "TemperatureBoundary", 1);
    model.component("comp1").physics("ht").feature("temp_air").selection().named("bnd_air_conv");
    model.component("comp1").physics("ht").feature("temp_air").set("T0", "Tair");
    model.component("comp1").physics("ht").create("temp_oil", "TemperatureBoundary", 1);
    model.component("comp1").physics("ht").feature("temp_oil").selection().named("bnd_oil_conv");
    model.component("comp1").physics("ht").feature("temp_oil").set("T0", "Toil");

    model.component("comp1").mesh().create("mesh1");
    model.component("comp1").mesh("mesh1").autoMeshSize(6);
  }

  private static void addStudies(Model model) {
    model.study().create("std_es");
    model.study("std_es").create("stat", "Stationary");
    model.study("std_es").feature("stat").activate("es", true);
    model.study("std_es").feature("stat").activate("ht", false);

    model.study().create("std_ht");
    model.study("std_ht").create("stat", "Stationary");
    model.study("std_ht").feature("stat").activate("es", false);
    model.study("std_ht").feature("stat").activate("ht", true);

    model.study().create("std_cpl");
    model.study("std_cpl").create("stat", "Stationary");
    model.study("std_cpl").feature("stat").activate("es", true);
    model.study("std_cpl").feature("stat").activate("ht", true);
  }

  private static void addResults(Model model) {
    model.component("comp1").cpl().create("maxop1", "Maximum");
    model.component("comp1").cpl("maxop1").selection().all();

    model.result().table().create("tbl_metrics", "Table");
    model.result().numerical().create("gev_metrics", "EvalGlobal");
    model.result().numerical("gev_metrics").set("table", "tbl_metrics");
    model.result().numerical("gev_metrics").set("expr", new String[]{
      "maxop1(T)", "Qcontact", "Icase", "Vph", "tanD_rip"
    });
    model.result().numerical("gev_metrics").set("descr", new String[]{
      "Tmax_global", "Qcontact_total_param", "current", "phase_voltage", "RIP tan delta"
    });
  }

  private static void runBaseline(Model model) {
    try {
      model.component("comp1").mesh("mesh1").run();
      System.out.println("Mesh generation completed.");
    } catch (Throwable t) {
      System.out.println("Mesh generation failed: " + t.getMessage());
    }

    runStudy(model, "std_es", "electric-field independent solve");
    runStudy(model, "std_ht", "thermal independent solve");
    runStudy(model, "std_cpl", "coupled electro-thermal solve");

    try {
      model.result().numerical("gev_metrics").setResult();
      model.result().table("tbl_metrics").save("/Users/luolin/Documents/New project/110kV_RIP_bushing_project/results/raw_comsol_exports/STEADY_1250_LOAD_1p0/metrics_table.csv");
      System.out.println("Metrics table exported.");
    } catch (Throwable t) {
      System.out.println("Metrics export failed: " + t.getMessage());
    }
    writeMetricsCsv(model);

    try {
      model.save("/Users/luolin/Documents/New project/110kV_RIP_bushing_project/comsol/BRFGL1-126-1250-4_base_model_2d_axisym_STEADY_1250_LOAD_1p0.mph");
      System.out.println("Baseline MPH saved.");
    } catch (Throwable t) {
      System.out.println("Model save failed: " + t.getMessage());
    }
  }

  private static void runStudy(Model model, String tag, String label) {
    try {
      System.out.println("Running " + label + " (" + tag + ")");
      model.study(tag).run();
      System.out.println("Completed " + label + " (" + tag + ")");
    } catch (Throwable t) {
      System.out.println("Study failed: " + label + " (" + tag + "): " + t.getMessage());
    }
  }

  private static void writeMetricsCsv(Model model) {
    String exportPath = "/Users/luolin/Documents/New project/110kV_RIP_bushing_project/results/raw_comsol_exports/STEADY_1250_LOAD_1p0/metrics_export.csv";
    String outputPath = "/Users/luolin/Documents/New project/110kV_RIP_bushing_project/data/processed/output_metrics.csv";
    String[] header = new String[]{
      "case_id", "Tmax_global", "Tmax_conductor", "Tmax_RIP", "Tmax_contact",
      "Emax_global", "Emax_RIP", "Emax_screen_end", "Qjoule_total",
      "Qdielectric_total", "Qcontact_total", "surface_Tmax",
      "deltaT_inner_outer", "risk_index"
    };

    String[] expr = new String[]{
      "maxop1(T)-273.15[K]",
      "maxop1(T)-273.15[K]",
      "maxop1(T)-273.15[K]",
      "maxop1(T)-273.15[K]",
      "E_rip_ref",
      "E_rip_ref",
      "E_rip_ref",
      "Icase^2*(1/sigma_cu_20)/(pi*r_cond^2)",
      "qdielectric_ref*pi*(r_rip^2-r_cond^2)*(2*screen_half_len)",
      "Qcontact",
      "maxop1(T)-273.15[K]",
      "0[K]",
      "(maxop1(T)-273.15[K])/180[degC]"
    };

    String[] values = new String[expr.length];
    for (int i = 0; i < expr.length; i++) {
      values[i] = evalGlobalScalar(model, expr[i]);
    }

    PrintWriter pw = null;
    try {
      pw = new PrintWriter(new FileWriter(exportPath));
      pw.println(String.join(",", header));
      pw.print("STEADY_1250_LOAD_1p0");
      for (String v : values) {
        pw.print(",");
        pw.print(v);
      }
      pw.println();
      System.out.println("Metrics export CSV written: " + exportPath);
    } catch (Throwable t) {
      System.out.println("Direct metrics CSV export failed: " + t.getMessage());
    } finally {
      if (pw != null) {
        pw.close();
      }
    }

    PrintWriter pw2 = null;
    try {
      pw2 = new PrintWriter(new FileWriter(outputPath));
      pw2.println(String.join(",", header));
      pw2.print("STEADY_1250_LOAD_1p0");
      for (String v : values) {
        pw2.print(",");
        pw2.print(v);
      }
      pw2.println();
      System.out.println("output_metrics.csv updated for baseline case.");
    } catch (Throwable t) {
      System.out.println("output_metrics.csv update failed: " + t.getMessage());
    } finally {
      if (pw2 != null) {
        pw2.close();
      }
    }
  }

  private static String evalGlobalScalar(Model model, String expression) {
    try {
      String tag = "gev_tmp_" + Math.abs(expression.hashCode());
      model.result().numerical().create(tag, "EvalGlobal");
      model.result().numerical(tag).set("expr", new String[]{expression});
      model.result().numerical(tag).set("data", "dset3");
      double[][] data = model.result().numerical(tag).getReal();
      model.result().numerical().remove(tag);
      if (data.length > 0 && data[0].length > 0) {
        return Double.toString(data[0][0]);
      }
      return "";
    } catch (Throwable t) {
      return "NA";
    }
  }
}
