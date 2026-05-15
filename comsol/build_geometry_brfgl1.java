import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

/**
 * Geometry-only COMSOL model for BRFGL1-126/1250-4 RIP dry condenser
 * transformer bushing.
 *
 * Coordinate convention:
 *   r axis: COMSOL x coordinate, in m
 *   z axis: COMSOL y coordinate, in m
 *   z = 0: flange center/mid-plane
 *   z > 0: air side
 *   z < 0: oil side
 *
 * The file builds three components:
 *   comp_v1: equivalent stepped-envelope geometry for fast electro-thermal work
 *   comp_v2: CAD-driven geometry with surrounding air/oil domains for simulation
 *   comp_v2_cad_solid_preview: CAD-driven bushing solids only for visual checking
 */
public class build_geometry_brfgl1 {

  public static void main(String[] args) throws java.io.IOException {
    ModelUtil.clear();
    Model model = ModelUtil.create("Model");
    model.modelPath("/Users/luolin/Documents/New project/110kV_RIP_bushing_project/comsol");
    model.label("BRFGL1-126-1250-4_geometry_axisym.mph");

    setParameters(model);
    buildGeometry(model, "comp_v1", "geom_v1", false);
    buildGeometry(model, "comp_v2", "geom_v2", true);
    buildSolidPreviewGeometry(model, "comp_v2_cad_solid_preview", "geom_preview");

    model.save("/Users/luolin/Documents/New project/110kV_RIP_bushing_project/comsol/BRFGL1-126-1250-4_geometry_axisym.mph");
  }

  private static void setParameters(Model model) {
    model.param().set("Um", "126[kV]", "Highest voltage for equipment");
    model.param().set("I0", "1250[A]", "Rated current");
    model.param().set("Vph_rms", "72.75[kV]", "S00 high-voltage screen RMS phase-to-ground voltage");
    model.param().set("product_model", "1", "Selected model: BRFGL1-126/1250-4. BRFGL2 is not used for this geometry.");

    model.param().set("L_total", "2245[mm]", "BRFGL1 overall axial length L");
    model.param().set("L1_ext", "1150[mm]", "External insulation length L1");
    model.param().set("oil_len", "595[mm]", "Oil immersed length L2");
    model.param().set("air_len", "1650[mm]", "Air-side equivalent length L_total - oil_len");
    model.param().set("L3_ct", "200[mm]", "CT length L3, stored as geometry metadata");
    model.param().set("L4_flange", "200[mm]", "Flange connection length L4");
    model.param().set("flange_t", "30[mm]", "Flange thickness H");
    model.param().set("terminal_a1", "40[mm]", "Air-side terminal connector dimension a1");
    model.param().set("creepage_check", "3906[mm]", "Nominal creepage distance; check only, not axial length");
    model.param().set("bolt_circle_D0", "350[mm]", "Flange bolt circle D0; not explicitly modeled in 2D axisymmetry");

    model.param().set("r_hollow", "20[mm]", "Conduit inner radius d3/2");
    model.param().set("r_conductor_outer", "32[mm]", "Assumed conductor tube outer radius; keeps S00 at the conductor/RIP interface");
    model.param().set("r_screen_start", "35[mm]", "S00 screen radius");
    model.param().set("r_rip", "66[mm]", "Oil-side core radius D1/2; maximum condenser-screen radius limit");
    model.param().set("r_body", "82[mm]", "Equivalent silicone rubber trunk radius");
    model.param().set("r_housing", "135[mm]", "External insulation maximum radius D2/2");
    model.param().set("r_terminal", "40[mm]", "Equivalent air-side terminal connector radius from a1");
    model.param().set("r_oil_tip", "45[mm]", "Equivalent tapered oil-side shield tip radius");
    model.param().set("r_flange", "200[mm]", "Flange outer radius D/2");
    model.param().set("r_flange_neck", "100[mm]", "Equivalent grounded flange neck radius");
    model.param().set("r_far", "360[mm]", "Surrounding air/oil far-field radius");

    model.param().set("screen_th", "0.25[mm]", "Numerical thickness for explicit condenser-screen domains");
    model.param().set("shed_pitch", "92[mm]", "Parametric V2 shed pitch");
    model.param().set("shed_t", "16[mm]", "Parametric V2 shed axial thickness");
    model.param().set("shed_start", "55[mm]", "First V2 shed start");
    model.param().set("Rc0", "1e-6[ohm]", "Nominal contact resistance");
    model.param().set("Rc_factor", "1", "Contact resistance deterioration multiplier");
    model.param().set("V_contact", "pi*(r_conductor_outer^2-r_hollow^2)*terminal_a1", "Contact heat-source volume");
    model.param().set("Q_contact_vol", "I0^2*Rc0*Rc_factor/V_contact", "Volumetric heat source Q_contact = I^2*Rc0*Rc_factor/V_contact");
  }

  private static void buildGeometry(Model model, String comp, String geom, boolean cadDrivenV2) throws IOException {
    model.component().create(comp, true);
    model.component(comp).geom().create(geom, 2);
    model.component(comp).geom(geom).axisymmetric(true);
    model.component(comp).geom(geom).lengthUnit("m");

    // Surrounding media.
    rect(model, comp, geom, "g_surrounding_air_domain", "r_housing", "0", "r_far-r_housing", "air_len");
    rect(model, comp, geom, "g_air_above_terminal", "r_terminal", "L1_ext", "r_far-r_terminal", "air_len-L1_ext");
    rect(model, comp, geom, "g_surrounding_oil_domain", "r_rip", "-oil_len", "r_far-r_rip", "oil_len");

    // Current-carrying tube, inner hollow, terminal, and contact heat layer.
    rect(model, comp, geom, "g_inner_conduit_or_hollow_region", "0", "-oil_len", "r_hollow", "oil_len+air_len");
    rect(model, comp, geom, "g_center_conductor", "r_hollow", "-oil_len", "r_conductor_outer-r_hollow", "oil_len+air_len");
    rect(model, comp, geom, "g_terminal_connector_region", "0", "L1_ext", "r_terminal", "terminal_a1");
    rect(model, comp, geom, "g_contact_resistance_heat_source_layer", "r_hollow", "L1_ext", "r_conductor_outer-r_hollow", "terminal_a1");

    // RIP core and explicit thin condenser-screen domains.
    rect(model, comp, geom, "g_rip_capacitor_core", "r_conductor_outer", "-oil_len", "r_rip-r_conductor_outer", "oil_len+L1_ext");
    screen(model, comp, geom, 0, 35.00, 1150.0);
    screen(model, comp, geom, 1, 37.25, 1150.0);
    screen(model, comp, geom, 2, 39.50, 1150.0);
    screen(model, comp, geom, 3, 41.75, 1150.0);
    screen(model, comp, geom, 4, 44.00, 1150.0);
    screen(model, comp, geom, 5, 46.25, 1100.0);
    screen(model, comp, geom, 6, 48.50, 1010.0);
    screen(model, comp, geom, 7, 50.75, 920.0);
    screen(model, comp, geom, 8, 53.00, 830.0);
    screen(model, comp, geom, 9, 55.25, 740.0);
    screen(model, comp, geom, 10, 57.50, 650.0);

    // Air-side external insulation.
    rect(model, comp, geom, "g_silicone_rubber_external_insulation", "r_rip", "0", "r_body-r_rip", "L1_ext");
    if (cadDrivenV2) {
      addCadProfileStrips(
          model,
          comp,
          geom,
          "/Users/luolin/Documents/New project/110kV_RIP_bushing_project/data/processed/cad_extract/brfgl1_cad_v2_air_profile.csv",
          "g_cad_air_side_profile");
    } else {
      rect(model, comp, geom, "g_air_side_sheds_or_equivalent_envelope", "r_body", "0", "r_housing-r_body", "L1_ext");
      rect(model, comp, geom, "g_air_side_step_lower", "95[mm]", "0", "r_housing-95[mm]", "280[mm]");
      rect(model, comp, geom, "g_air_side_step_upper", "95[mm]", "870[mm]", "r_housing-95[mm]", "280[mm]");
    }

    // Grounded flange and oil-side stepped/tapered approximation.
    rect(model, comp, geom, "g_flange_grounded_metal_disk", "r_rip", "-flange_t/2", "r_flange-r_rip", "flange_t");
    rect(model, comp, geom, "g_flange_grounded_metal_neck", "r_rip", "-L4_flange/2", "r_flange_neck-r_rip", "L4_flange");
    rect(model, comp, geom, "g_oil_side_core", "r_conductor_outer", "-oil_len", "r_rip-r_conductor_outer", "oil_len");
    if (cadDrivenV2) {
      addCadProfileStrips(
          model,
          comp,
          geom,
          "/Users/luolin/Documents/New project/110kV_RIP_bushing_project/data/processed/cad_extract/brfgl1_cad_v2_oil_profile.csv",
          "g_cad_oil_side_profile");
    } else {
      rect(model, comp, geom, "g_oil_side_shield_or_tapered_region_1", "r_oil_tip", "-oil_len", "r_rip-r_oil_tip", "180[mm]");
      rect(model, comp, geom, "g_oil_side_shield_or_tapered_region_2", "52[mm]", "-415[mm]", "r_rip-52[mm]", "170[mm]");
      rect(model, comp, geom, "g_oil_side_shield_or_tapered_region_3", "58[mm]", "-245[mm]", "r_rip-58[mm]", "145[mm]");
    }

    model.component(comp).geom(geom).run();

    createSelections(model, comp, geom);
  }

  private static void buildSolidPreviewGeometry(Model model, String comp, String geom) throws IOException {
    model.component().create(comp, true);
    model.component(comp).geom().create(geom, 2);
    model.component(comp).geom(geom).axisymmetric(true);
    model.component(comp).geom(geom).lengthUnit("m");

    // No surrounding air/oil domains are created in this component. It is only
    // for checking the bushing body against the CAD drawing.
    rect(model, comp, geom, "g_inner_conduit_or_hollow_region", "0", "-oil_len", "r_hollow", "oil_len+air_len");
    rect(model, comp, geom, "g_center_conductor", "r_hollow", "-oil_len", "r_conductor_outer-r_hollow", "oil_len+air_len");
    rect(model, comp, geom, "g_terminal_connector_region", "0", "L1_ext", "r_terminal", "terminal_a1");
    rect(model, comp, geom, "g_contact_resistance_heat_source_layer", "r_hollow", "L1_ext", "r_conductor_outer-r_hollow", "terminal_a1");

    rect(model, comp, geom, "g_rip_capacitor_core", "r_conductor_outer", "-oil_len", "r_rip-r_conductor_outer", "oil_len+L1_ext");
    screen(model, comp, geom, 0, 35.00, 1150.0);
    screen(model, comp, geom, 1, 37.25, 1150.0);
    screen(model, comp, geom, 2, 39.50, 1150.0);
    screen(model, comp, geom, 3, 41.75, 1150.0);
    screen(model, comp, geom, 4, 44.00, 1150.0);
    screen(model, comp, geom, 5, 46.25, 1100.0);
    screen(model, comp, geom, 6, 48.50, 1010.0);
    screen(model, comp, geom, 7, 50.75, 920.0);
    screen(model, comp, geom, 8, 53.00, 830.0);
    screen(model, comp, geom, 9, 55.25, 740.0);
    screen(model, comp, geom, 10, 57.50, 650.0);

    rect(model, comp, geom, "g_silicone_rubber_external_insulation", "r_rip", "0", "r_body-r_rip", "L1_ext");
    addCadProfileStrips(
        model,
        comp,
        geom,
        "/Users/luolin/Documents/New project/110kV_RIP_bushing_project/data/processed/cad_extract/brfgl1_cad_v2_air_profile.csv",
        "g_cad_air_side_profile");

    rect(model, comp, geom, "g_flange_grounded_metal_disk", "r_rip", "-flange_t/2", "r_flange-r_rip", "flange_t");
    rect(model, comp, geom, "g_flange_grounded_metal_neck", "r_rip", "-L4_flange/2", "r_flange_neck-r_rip", "L4_flange");
    rect(model, comp, geom, "g_oil_side_core", "r_conductor_outer", "-oil_len", "r_rip-r_conductor_outer", "oil_len");
    addCadProfileStrips(
        model,
        comp,
        geom,
        "/Users/luolin/Documents/New project/110kV_RIP_bushing_project/data/processed/cad_extract/brfgl1_cad_v2_oil_profile.csv",
        "g_cad_oil_side_profile");

    model.component(comp).geom(geom).run();

    createPreviewSelections(model, comp, geom);
  }

  private static void createSelections(Model model, String comp, String geom) {
    String p = comp.equals("comp_v1") ? "v1_" : "v2_";
    boxSel(model, comp, geom, p + "center_conductor", 2, "r_hollow-0.2[mm]", "r_conductor_outer+0.2[mm]", "-oil_len-1[mm]", "air_len+1[mm]");
    boxSel(model, comp, geom, p + "inner_conduit_or_hollow_region", 2, "-0.2[mm]", "r_hollow+0.2[mm]", "-oil_len-1[mm]", "air_len+1[mm]");
    boxSel(model, comp, geom, p + "rip_capacitor_core", 2, "r_conductor_outer-0.2[mm]", "r_rip+0.2[mm]", "-oil_len-1[mm]", "L1_ext+1[mm]");
    boxSel(model, comp, geom, p + "condenser_screens", 2, "r_screen_start-1[mm]", "58[mm]", "-576[mm]", "576[mm]");
    boxSel(model, comp, geom, p + "silicone_rubber_external_insulation", 2, "r_rip-0.2[mm]", "r_body+0.2[mm]", "-1[mm]", "L1_ext+1[mm]");
    boxSel(model, comp, geom, p + "air_side_sheds_or_equivalent_envelope", 2, "r_body-0.2[mm]", "r_housing+0.2[mm]", "-1[mm]", "L1_ext+1[mm]");
    boxSel(model, comp, geom, p + "flange_grounded_metal", 2, "r_rip-0.2[mm]", "r_flange+0.2[mm]", "-L4_flange/2-1[mm]", "L4_flange/2+1[mm]");
    boxSel(model, comp, geom, p + "oil_side_core", 2, "r_conductor_outer-0.2[mm]", "r_rip+0.2[mm]", "-oil_len-1[mm]", "1[mm]");
    boxSel(model, comp, geom, p + "oil_side_shield_or_tapered_region", 2, "r_oil_tip-0.2[mm]", "r_rip+0.2[mm]", "-oil_len-1[mm]", "-100[mm]");
    boxSel(model, comp, geom, p + "terminal_connector_region", 2, "-0.2[mm]", "r_terminal+0.2[mm]", "L1_ext-1[mm]", "L1_ext+terminal_a1+1[mm]");
    boxSel(model, comp, geom, p + "contact_resistance_heat_source_layer", 2, "r_hollow-0.2[mm]", "r_conductor_outer+0.2[mm]", "L1_ext-1[mm]", "L1_ext+terminal_a1+1[mm]");
    boxSel(model, comp, geom, p + "surrounding_air_domain", 2, "r_terminal-1[mm]", "r_far+1[mm]", "-1[mm]", "air_len+1[mm]");
    boxSel(model, comp, geom, p + "surrounding_oil_domain", 2, "r_rip-1[mm]", "r_far+1[mm]", "-oil_len-1[mm]", "1[mm]");

    for (int i = 0; i <= 10; i++) {
      double radius = 35.0 + 2.25 * i;
      double length = screenLength(i);
      String tag = p + "screen_S" + twoDigit(i);
      boxSel(model, comp, geom, tag, 2,
          (radius - 0.3) + "[mm]",
          (radius + 0.3) + "[mm]",
          (-length / 2.0 - 1.0) + "[mm]",
          (length / 2.0 + 1.0) + "[mm]");
    }

    boxSel(model, comp, geom, p + "bnd_axisymmetry", 1, "-0.1[mm]", "0.1[mm]", "-oil_len-1[mm]", "air_len+1[mm]");
    boxSel(model, comp, geom, p + "bnd_S00_fixed_72p75kV_rms", 1, "34.8[mm]", "35.2[mm]", "-575[mm]", "575[mm]");
    boxSel(model, comp, geom, p + "bnd_S10_ground_0V", 1, "57.3[mm]", "57.7[mm]", "-326[mm]", "326[mm]");
    boxSel(model, comp, geom, p + "bnd_flange_ground", 1, "r_rip-0.2[mm]", "r_flange+0.2[mm]", "-L4_flange/2-1[mm]", "L4_flange/2+1[mm]");
    boxSel(model, comp, geom, p + "bnd_air_external_convection", 1, "r_body-1[mm]", "r_housing+1[mm]", "-1[mm]", "L1_ext+1[mm]");
    boxSel(model, comp, geom, p + "bnd_surrounding_air_outer", 1, "r_far-0.2[mm]", "r_far+0.2[mm]", "-1[mm]", "air_len+1[mm]");
    boxSel(model, comp, geom, p + "bnd_surrounding_oil_outer", 1, "r_far-0.2[mm]", "r_far+0.2[mm]", "-oil_len-1[mm]", "1[mm]");
    boxSel(model, comp, geom, p + "bnd_oil_immersed_surface", 1, "r_oil_tip-1[mm]", "r_rip+1[mm]", "-oil_len-1[mm]", "1[mm]");
  }

  private static void createPreviewSelections(Model model, String comp, String geom) {
    String p = "pv_";
    boxSel(model, comp, geom, p + "center_conductor", 2, "r_hollow-0.2[mm]", "r_conductor_outer+0.2[mm]", "-oil_len-1[mm]", "air_len+1[mm]");
    boxSel(model, comp, geom, p + "inner_conduit_or_hollow_region", 2, "-0.2[mm]", "r_hollow+0.2[mm]", "-oil_len-1[mm]", "air_len+1[mm]");
    boxSel(model, comp, geom, p + "rip_capacitor_core", 2, "r_conductor_outer-0.2[mm]", "r_rip+0.2[mm]", "-oil_len-1[mm]", "L1_ext+1[mm]");
    boxSel(model, comp, geom, p + "condenser_screens", 2, "r_screen_start-1[mm]", "58[mm]", "-576[mm]", "576[mm]");
    boxSel(model, comp, geom, p + "silicone_rubber_external_insulation", 2, "r_rip-0.2[mm]", "r_body+0.2[mm]", "-1[mm]", "L1_ext+1[mm]");
    boxSel(model, comp, geom, p + "air_side_sheds_or_equivalent_envelope", 2, "r_body-0.2[mm]", "r_housing+0.2[mm]", "-1[mm]", "L1_ext+1[mm]");
    boxSel(model, comp, geom, p + "flange_grounded_metal", 2, "r_rip-0.2[mm]", "r_flange+0.2[mm]", "-L4_flange/2-1[mm]", "L4_flange/2+1[mm]");
    boxSel(model, comp, geom, p + "oil_side_core", 2, "r_conductor_outer-0.2[mm]", "r_rip+0.2[mm]", "-oil_len-1[mm]", "1[mm]");
    boxSel(model, comp, geom, p + "oil_side_shield_or_tapered_region", 2, "r_hollow-0.2[mm]", "r_rip+0.2[mm]", "-oil_len-1[mm]", "1[mm]");
    boxSel(model, comp, geom, p + "terminal_connector_region", 2, "-0.2[mm]", "r_terminal+0.2[mm]", "L1_ext-1[mm]", "L1_ext+terminal_a1+1[mm]");
    boxSel(model, comp, geom, p + "contact_resistance_heat_source_layer", 2, "r_hollow-0.2[mm]", "r_conductor_outer+0.2[mm]", "L1_ext-1[mm]", "L1_ext+terminal_a1+1[mm]");

    for (int i = 0; i <= 10; i++) {
      double radius = 35.0 + 2.25 * i;
      double length = screenLength(i);
      boxSel(model, comp, geom, p + "screen_S" + twoDigit(i), 2,
          (radius - 0.3) + "[mm]",
          (radius + 0.3) + "[mm]",
          (-length / 2.0 - 1.0) + "[mm]",
          (length / 2.0 + 1.0) + "[mm]");
    }

    boxSel(model, comp, geom, p + "bnd_axisymmetry", 1, "-0.1[mm]", "0.1[mm]", "-oil_len-1[mm]", "air_len+1[mm]");
    boxSel(model, comp, geom, p + "bnd_S00_fixed_72p75kV_rms", 1, "34.8[mm]", "35.2[mm]", "-575[mm]", "575[mm]");
    boxSel(model, comp, geom, p + "bnd_S10_ground_0V", 1, "57.3[mm]", "57.7[mm]", "-326[mm]", "326[mm]");
    boxSel(model, comp, geom, p + "bnd_flange_ground", 1, "r_rip-0.2[mm]", "r_flange+0.2[mm]", "-L4_flange/2-1[mm]", "L4_flange/2+1[mm]");
    boxSel(model, comp, geom, p + "bnd_external_solid_surface", 1, "r_body-1[mm]", "r_housing+1[mm]", "-oil_len-1[mm]", "L1_ext+1[mm]");
  }

  private static void rect(Model model, String comp, String geom, String tag, String x, String y, String w, String h) {
    model.component(comp).geom(geom).create(tag, "Rectangle");
    model.component(comp).geom(geom).feature(tag).set("pos", new String[]{x, y});
    model.component(comp).geom(geom).feature(tag).set("size", new String[]{w, h});
  }

  private static void addCadProfileStrips(Model model, String comp, String geom, String csvPath, String tagPrefix) throws IOException {
    BufferedReader reader = new BufferedReader(new FileReader(csvPath));
    String line = reader.readLine();
    int idx = 0;
    while ((line = reader.readLine()) != null) {
      if (line.trim().isEmpty()) {
        continue;
      }
      String[] cols = line.split(",", -1);
      double z0 = Double.parseDouble(cols[1]);
      double z1 = Double.parseDouble(cols[2]);
      double r0 = Double.parseDouble(cols[3]);
      double r1 = Double.parseDouble(cols[4]);
      if (r1 <= r0 || z1 <= z0) {
        continue;
      }
      rect(
          model,
          comp,
          geom,
          tagPrefix + "_" + threeDigit(idx),
          r0 + "[mm]",
          z0 + "[mm]",
          (r1 - r0) + "[mm]",
          (z1 - z0) + "[mm]");
      idx++;
    }
    reader.close();
  }

  private static void screen(Model model, String comp, String geom, int i, double radiusMm, double lengthMm) {
    double z0 = -lengthMm / 2.0;
    rect(model, comp, geom, "g_screen_S" + twoDigit(i),
        radiusMm + "[mm]", z0 + "[mm]", "screen_th", lengthMm + "[mm]");
  }

  private static void boxSel(Model model, String comp, String geom, String tag, int dim, String xmin, String xmax, String ymin, String ymax) {
    model.component(comp).selection().create(tag, "Box");
    model.component(comp).selection(tag).geom(geom, dim);
    model.component(comp).selection(tag).set("xmin", xmin);
    model.component(comp).selection(tag).set("xmax", xmax);
    model.component(comp).selection(tag).set("ymin", ymin);
    model.component(comp).selection(tag).set("ymax", ymax);
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

  private static double screenLength(int i) {
    double[] lengths = {1150.0, 1150.0, 1150.0, 1150.0, 1150.0, 1100.0, 1010.0, 920.0, 830.0, 740.0, 650.0};
    return lengths[i];
  }
}
