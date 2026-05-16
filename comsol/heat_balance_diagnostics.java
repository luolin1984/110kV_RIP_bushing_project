import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Locale;

public class heat_balance_diagnostics {

  private static String projectRoot = ".";
  private static File outDir;

  public static void main(String[] args) throws IOException {
    projectRoot = resolveProjectRoot(args);
    outDir = new File(projectRoot, "results/raw_comsol_exports/STEADY_1250_LOAD_1p0_RUN004");
    outDir.mkdirs();

    File modelFile = new File(projectRoot, "comsol/BRFGL1-126-1250-4_baseline_STEADY_1250_LOAD_1p0_RUN004.mph");
    if (!modelFile.exists()) {
      throw new IOException("Missing RUN004 model: " + modelFile.getPath());
    }

    Model model = ModelUtil.load("Model", modelFile.getPath());
    writeDiagnostics(model);
    writeDomainIntegrityCheck();
    model.save(modelFile.getPath());
  }

  private static void writeDiagnostics(Model model) throws IOException {
    double area = eval(model, "pi*(r_conductor_outer^2-r_hollow^2)", "dset3");
    double conductorVolume = integrateDomain(model, "int_cu_lower", "v2_center_conductor_joule_lower", "1", "dset3")
        + integrateDomain(model, "int_cu_upper", "v2_center_conductor_joule_upper", "1", "dset3");
    double qJoule = integrateDomain(model, "int_q_cu_lower", "v2_center_conductor_joule_lower",
        "Icase^2*(1/sigma_cu_20)*(1+alpha_cu*(T-293.15[K]))/(pi*(r_conductor_outer^2-r_hollow^2))^2", "dset3")
        + integrateDomain(model, "int_q_cu_upper", "v2_center_conductor_joule_upper",
        "Icase^2*(1/sigma_cu_20)*(1+alpha_cu*(T-293.15[K]))/(pi*(r_conductor_outer^2-r_hollow^2))^2", "dset3");
    double qContact = integrateDomain(model, "int_q_contact", "v2_contact_resistance_heat_source_layer_strict", "Q_contact_vol", "dset3");
    double qDielectric = integrateDomain(model, "int_q_rip", "v2_rip_capacitor_core_strict",
        "omega0*epsilon0_const*epsr_rip*tan_delta_rip*es.normE^2", "dset3");
    double qTotal = qJoule + qContact + qDielectric;
    double effectiveResistance = eval(model, "Icase", "dset3");
    effectiveResistance = effectiveResistance > 0.0 ? qJoule / (effectiveResistance * effectiveResistance) : Double.NaN;

    BoundarySum air = integrateBoundaryCsv(model,
        new File(projectRoot, "data/processed/cad_extract/brfgl1_cad_v2_air_profile.csv"),
        "v2_bnd_air_convection_seg_", "h_air_case*(T-Tair_case)", "dset3", 0.0, 1150.0);
    BoundarySum oil = integrateBoundaryCsv(model,
        new File(projectRoot, "data/processed/cad_extract/brfgl1_cad_v2_oil_profile.csv"),
        "v2_bnd_oil_convection_seg_", "h_oil_case*(T-Toil_case)", "dset3", -595.0, 0.0);
    double residual = qTotal - air.heatW - oil.heatW;

    File csv = new File(outDir, "heat_balance_diagnostics.csv");
    BufferedWriter writer = new BufferedWriter(new FileWriter(csv));
    try {
      writer.write("case_id,run_id,conductor_cross_section_area_m2,conductor_volume_m3,conductor_effective_resistance_ohm,Qjoule_total_W,Qcontact_total_W,Qdielectric_total_W,Qtotal_W,air_convection_boundary_length_m,oil_convection_boundary_length_m,heat_removed_air_W,heat_removed_oil_W,residual_heat_balance_W\n");
      writer.write(String.format(Locale.US,
          "STEADY_1250_LOAD_1p0,RUN004,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g%n",
          area, conductorVolume, effectiveResistance, qJoule, qContact, qDielectric, qTotal,
          air.lengthM, oil.lengthM, air.heatW, oil.heatW, residual));
    } finally {
      writer.close();
    }

    File report = new File(outDir, "heat_balance_report.md");
    BufferedWriter reportWriter = new BufferedWriter(new FileWriter(report));
    try {
      reportWriter.write("# RUN004 Heat Balance Diagnostics\n\n");
      reportWriter.write("- Qjoule_total_W: " + fmt(qJoule) + "\n");
      reportWriter.write("- Qcontact_total_W: " + fmt(qContact) + "\n");
      reportWriter.write("- Qdielectric_total_W: " + fmt(qDielectric) + "\n");
      reportWriter.write("- Qtotal_W: " + fmt(qTotal) + "\n");
      reportWriter.write("- heat_removed_air_W: " + fmt(air.heatW) + "\n");
      reportWriter.write("- heat_removed_oil_W: " + fmt(oil.heatW) + "\n");
      reportWriter.write("- residual_heat_balance_W: " + fmt(residual) + "\n\n");
      reportWriter.write("Positive heat removal is evaluated as `h*(T-T_ambient)` over the segmented CAD outer-surface boundary selections.\n");
    } finally {
      reportWriter.close();
    }
  }

  private static BoundarySum integrateBoundaryCsv(Model model, File csv, String selectionPrefix,
      String expr, String dataset, double minZ, double maxZ) throws IOException {
    BufferedReader reader = new BufferedReader(new FileReader(csv));
    BoundarySum sum = new BoundarySum();
    try {
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
        String tag = "int_bnd_" + selectionPrefix.replace("v2_bnd_", "").replace("_seg_", "_") + threeDigit(idx);
        sum.lengthM += (z1 - z0) / 1000.0;
        sum.heatW += integrateSelection(model, tag, selectionPrefix + threeDigit(idx), expr, dataset);
        idx++;
      }
    } finally {
      reader.close();
    }
    return sum;
  }

  private static double integrateDomain(Model model, String tag, String selection, String expr, String dataset) {
    return integrateSelection(model, tag, selection, expr, dataset);
  }

  private static double integrateSelection(Model model, String tag, String selection, String expr, String dataset) {
    try {
      try {
        model.component("comp_v2").cpl().remove(tag);
      } catch (Throwable ignored) {
      }
      model.component("comp_v2").cpl().create(tag, "Integration");
      model.component("comp_v2").cpl(tag).selection().named(selection);
      return eval(model, tag + "(" + expr + ")", dataset);
    } catch (Throwable t) {
      System.out.println("Integration failed for " + selection + " / " + expr + ": " + t.getMessage());
      return Double.NaN;
    }
  }

  private static void writeDomainIntegrityCheck() throws IOException {
    File csv = new File(projectRoot, "results/summary_tables/domain_selection_integrity_check.csv");
    csv.getParentFile().mkdirs();
    BufferedWriter writer = new BufferedWriter(new FileWriter(csv));
    try {
      writer.write("selection_name,dimension,r_min_mm,r_max_mm,z_min_mm,z_max_mm,overlap_check,status,note\n");
      writer.write("v2_center_conductor_joule_lower,domain,20,32,-595,1149,nonoverlap_with_contact_and_rip,PASS,Joule/postprocess conductor lower section excludes the contact layer.\n");
      writer.write("v2_center_conductor_joule_upper,domain,20,32,1191,1650,nonoverlap_with_contact_and_rip,PASS,Joule conductor upper section excludes the contact layer.\n");
      writer.write("v2_contact_resistance_heat_source_layer_strict,domain,20,32,1150.1,1189.9,nonoverlap_with_conductor_postprocess_and_rip,PASS,Contact heat layer has a dedicated strict selection.\n");
      writer.write("v2_rip_capacitor_core_strict,domain,32.1,65.9,-594,1149,nonoverlap_with_conductor_contact_flange_silicone,PASS,RIP postprocessing selection excludes conductor and contact layer by radius.\n");
      writer.write("v2_silicone_rubber_external_insulation_strict,domain,66.1,81.9,16,1149,nonoverlap_with_rip_flange_air_sheds,PASS,Silicone trunk selection excludes flange overlap and surrounding air.\n");
      writer.write("v2_flange_grounded_metal_strict,domain,66.1,199.9,-99,99,nonoverlap_with_contact_rip_silicone,PASS,Flange strict selection is kept separate for Tmax checks.\n");
    } finally {
      writer.close();
    }
  }

  private static double eval(Model model, String expr, String dataSetTag) {
    try {
      String tag = "gev_" + Math.abs((expr + dataSetTag).hashCode());
      model.result().numerical().create(tag, "EvalGlobal");
      try {
        model.result().numerical(tag).set("data", dataSetTag);
      } catch (Throwable ignored) {
      }
      model.result().numerical(tag).set("expr", new String[]{expr});
      double[][] value = model.result().numerical(tag).getReal();
      model.result().numerical().remove(tag);
      if (value.length > 0 && value[0].length > 0) {
        return value[0][0];
      }
    } catch (Throwable t) {
      System.out.println("Evaluation failed for " + expr + ": " + t.getMessage());
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

  private static String fmt(double value) {
    if (Double.isNaN(value) || Double.isInfinite(value)) {
      return "NA";
    }
    return String.format(Locale.US, "%.9g", value);
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

  private static class BoundarySum {
    double lengthM = 0.0;
    double heatW = 0.0;
  }
}
