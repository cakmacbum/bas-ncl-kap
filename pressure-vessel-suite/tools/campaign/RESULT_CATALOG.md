# Campaign calculation result catalog

This is an I/O contract only; it intentionally contains no equations. Inputs are
project JSON keys (SI unless stated). A field marked * is required for the row
to be evaluated. `BLOCKED MISSING INPUT` means required project data is absent;
`BLOCKED CODE DATA` means the selected code/material dataset cannot supply it.
`NOT CALCULATED` means no calculation was run. `PASS`/`FAIL` are limit checks;
`REVIEW REQUIRED` needs engineering review; `OUT OF SCOPE` is informational.
Result rows carry `component_id`, `component_type`, `calculation_type`,
`clause_reference`, `status`, `intermediate_values` (name/value/unit), and
`final_result` (scalar or named object). Intermediate field lists below describe
common keys; optional keys vary by code and component. `final_result` expresses
the named check/quantity, in the unit shown by the corresponding value.

## Calculation types

| Type | Trigger and minimum useful inputs (units) | Row / output contract |
|---|---|---|
| `thickness` | Shell/head with `inside_diameter` (mm), `nominal_thickness` (mm), `material_id`; `design_conditions.design_pressure` (MPa), `design_temperature` (°C); material allowable stress (MPa), weld joint efficiency (ratio), corrosion allowance (mm). | `shell` or `head`; code clause; required thickness (mm), allowable pressure (MPa), governing inputs; final required thickness / acceptance. |
| `mawp` | Pressure component plus geometry, nominal thickness, material allowable stress, weld efficiency and corrosion allowance as above. | `shell`/`head`; MAWP clause; thickness/allowable pressure intermediates (mm, MPa); final MAWP (MPa). |
| `nozzle_reinforcement` | `nozzles[]`: host id, `outside_diameter`/`inside_diameter`/`neck_thickness` (mm), `axial_position` (mm), `material_id`; host geometry/thickness and material/pressure data; pad dimensions when `reinforcement_pad=true`. | `nozzle`; area/reinforcement terms (mm², mm); final required/provided area check. |
| `clash_check` | Nozzle geometry/position and host plus other nozzle/component geometry; dimensions and positions in mm. | nozzle or project; clash clause; clearance/distance (mm); final clash/review state. |
| `weld_validation` | `welds[]`: `joint_id`, `joint_type`, category, `joint_efficiency` (ratio), NDE method/extent; associated component/material and design conditions. | `weld`; clause; joint efficiency and NDE metadata; final validity/review status. |
| `hydrotest` | Design pressure (MPa), test temperature (°C where required), material allowable stresses at design/test temperatures (MPa), component MAWP. | project; test clause; pressure/stress values (MPa); final test pressure (MPa) and status. |
| `pneumatic_test` | Design pressure (MPa), material allowable stress at design/test temperatures (MPa), test conditions. | project; test clause; pressure/stress (MPa); final test pressure (MPa). |
| `mdmt_check` | Minimum design temperature (°C), component material/thickness (mm), impact exemption data; coincident load ratio when ratio method is selected (dimensionless). | shell/head/governing row; clause; exemption inputs and coincident ratio; final allowable MDMT (°C) / status. Missing ratio blocks ratio method. |
| `external_pressure` | External design pressure/vacuum (MPa), shell/head diameter and thickness (mm), unsupported length (mm), material modulus/allowables at design temperature. | shell/head; external pressure clause; geometry/coefficient keys (mm, MPa, dimensionless); final allowable external pressure (MPa). |
| `external_pressure_check` | Same external pressure project data and applied pressure (MPa). | component; clause; applied/allowable pressure (MPa); final adequacy status. |
| `vacuum_stability` | Vacuum pressure (MPa), shell geometry/thickness and unsupported length (mm), elastic modulus/allowable stress (MPa), stiffener data if present. | shell; vacuum clause; stability terms (mixed mm/MPa); final stability check. |
| `flange_stress` | Flange geometry and gasket/bolt data: `Y`,`T`,`U`,`Z`,`F`,`V`,`f` (dimensionless factors), flange dimensions (mm), bolt area (mm²), bolt/gasket loads (N), pressure (MPa). | flange; clause; moment/stress terms (N·mm, MPa); final stress/adequacy result. |
| `flange` | EN flange geometry, material, gasket/bolt data and design pressure/temperature. | flange; EN clause; component stress values (MPa); final flange verification. |
| `saddle_stress` | Horizontal vessel; two `supports[]` type saddle with `location_mm`, `width_mm`, `height_mm`, host shell dimensions/thickness and material; pressure plus weight/load data. | support; Zick clause; K1–K7 and stress terms (dimensionless, MPa); final stress/acceptance. K1–K7 require saddle geometry and vessel/support load inputs. |
| `skirt_stress` | Vertical vessel; skirt `diameter_mm`, `thickness_mm`, `height_mm`, material; wind/seismic and operating/test load cases. | support; clause; membrane/bending stresses (MPa); final status. |
| `leg_stress` | Vertical vessel leg: count, diameter/thickness, location, material, base load; vessel weight/pressure and wind/seismic load cases. | support; clause; axial/bending stresses (MPa); final stress result. |
| `leg_section_check` | Leg section dimensions (`leg_diameter_mm`, `leg_thickness_mm`, count), material allowable stress (MPa), loads (N). | support; clause; section properties and demand (mm², mm³, N); final capacity check. |
| `leg_weld_check` | `leg_weld_size_mm` (mm), leg/support material, weld length (mm), support reaction (N). | support; clause; weld area/stress (mm², MPa); final weld check. |
| `base_plate_check` | Plate length/width/thickness (mm), anchor count/diameter/circle (mm), material allowable stresses (MPa), support reaction (N). | support; clause; bearing/anchor demand (MPa, N); final plate/anchor check. |
| `wrc_local_stress` | Vessel shell geometry/thickness (mm), nozzle/attachment dimensions and load components (N, N·mm), material allowable stress (MPa). | shell/attachment; WRC clause; local stresses (MPa); final status. |
| `junction_check` | `junctions[]` with connected component ids/types, diameters/thicknesses (mm), cone angle (degrees), material, pressure and weld geometry. | junction; clause; junction geometry/stress terms (mm, degrees, MPa); final reinforcement/adequacy status. |
| `global_load_case` | Named load case with pressure (MPa), temperature (°C), weight/forces (N), moments (N·mm), wind/seismic components and support/component geometry. | project/load case; load clause; per-case result values with physical units; final case status. |
| `global_load_combination` | At least two defined load cases and combination factors (dimensionless); each case must define applicable loads. | project; combination clause; case ids/factors and combined force/moment values (N, N·mm); final governing combination. |
| `load_combination` | EN project with defined load cases, factors, pressure and structural loads (MPa, N, N·mm). | project; EN clause; combined load values; final combined verification. |
| `pressure_consistency` | Design, operating and maximum allowable pressures in `design_conditions` (MPa). | project; consistency clause; pressure fields (MPa); final consistency status. |
| `material_check` | `materials[]` designation, product form, temperature (°C), allowable/yield/tensile strengths (MPa), density (kg/m³), code source/revision. | material; material clause; property/source values (units per field); final data validity. |
| `fatigue` | EN fatigue assessment inputs: cycles, stress ranges (MPa), material fatigue data and detail category. | component; fatigue clause; cycle/damage terms (cycles, dimensionless); final fatigue status. |
| `pressure_relief` | Relief device set pressure and capacity, fluid/service properties and design/relieving conditions. | relief system; relief clause; set/capacity values (MPa, kg/s or stated basis); final sizing status. |
| `fea_analysis` | FEA model/mesh, material properties and boundary/load definitions. | analysis; solver clause; displacement/stress values (mm, MPa); final solver/acceptance status. | 
| `fea_material_data_check` | FEA material assignment with elastic modulus (MPa), Poisson ratio, density (kg/m³) and temperature. | material; FEA data clause; material properties; final data validity. |

`weld_validation` may emit one row per joint. `clash_check` may emit both
component and project summary rows. `mdmt_check` may emit component rows and
`MDMT-GOVERNING`. Wind/seismic loads are represented by project load cases or
support wind/seismic inputs; a pressure-only base is insufficient to establish
those checks. Cone results need explicit cone/junction connectivity. Flange
factor fields are dimensionless and must be provided with flange geometry and
bolt/gasket data; the standard vessel fixture has no flange. Zick K1–K7 cannot
be demonstrated unless the solver receives complete saddle location, dimensions
and vessel/support loads. The examples below provide complete saddle geometry,
flange factors and connected cone topology where the calculation route supports
them.

## Deep input/output contracts

| Type / case | Required trigger fields (units) | Common intermediate_values (units) and limit |
|---|---|---|
| `saddle_stress` | `orientation="horizontal"`; exactly two saddle supports on one shell; `location_mm`, `width_mm`, `contact_angle_deg`, `saddle_stiffened`; table values `zick_K1`, `zick_K2`, `zick_K6`, `zick_K7` (-) when not internally fixed; shell `tangent_length`, thickness and material; design pressure; two heads and positive vessel mass. | `D_i_mm`, `R_m_mm`, `t_corroded_mm`, `L_mm`, `H_mm`, `A_mm`, `b_mm` (mm); `theta_deg`, applicable K1..K7 (-); `W_total_N`, `Q_left_N`, `Q_right_N` (N); stresses (MPa). Missing required geometry/load/table input blocks. |
| `leg_section_check` | Leg support with `leg_section_type="pipe"`, positive `leg_diameter_mm`, `leg_thickness_mm`, `leg_count`, shell host/material and resolved vessel/test weight. | `n_legs` (-), `N_max`, `N_min`, `H_per_leg` (N), section area/modulus (mm2/mm3), stresses/capacity (MPa/N); final status. |
| `leg_weld_check` | Above plus `leg_to_pad_weld_leg_mm`, `pad_to_shell_weld_leg_mm`, `leg_to_base_plate_weld_leg_mm`, `weld_electrode_strength_MPa`, pad dimensions and positive weld sizes. | Weld group area (mm2), reactions (N), demand/allowable (MPa), final utilization/status. |
| `base_plate_check` | Above plus exact solver fields `base_plate_length_mm`, `base_plate_width_mm`, `base_plate_thickness_mm`, `base_plate_yield_MPa` (mm/MPa). `leg_base_plate_*` fixture-style names are not read by this check. | Plate dimensions (mm), reaction (N), bearing pressure (MPa), required/provided thickness (mm), final status. |
| `wrc_local_stress` | Leg attached to shell (`leg_attachment="shell"`); shell geometry/material and loads; `wrc_coefficients` for needed point/load pairs A/B/C/D x P/ML/MC/VL/VC with explicit `Nx`, `Ny`, `Mx`, `My` (-). Values are user-read from the licensed bulletin. | Coefficients (-), membrane/bending/local stress (MPa), final status. Missing is not treated as zero. |
| `flange_stress` | ASME integral flange: `inside_diameter`, `outside_diameter`, flange/hub dimensions (mm), material; positive `bolt_load_W_N` (N), `moment_M_Nmm` (N-mm), and `flange_factor_Y/f/F/V/T/U` (-). | `A`, `B`, `t`, `g0`, `g1`, `h0` (mm); `K`, `Z`, `L`, factors (-); `W` (N), `M` (N-mm), `S_H`, `S_R`, `S_T`, `S_f` (MPa); Appendix 2 stress status. |
| `junction_check` | `cones[]` and `junctions[]` connecting cone and shell/head; valid ordered `component_sequence` ending in heads; `cone_end`, resolvable `weld_joint_id`, `weld_efficiency`, end diameters (mm). | Resolved component ids/types, junction/weld metadata (-), diameters/thickness (mm), apex angle (deg). Current result is topology/input review, not numeric adequacy. |
| `global_load_case` | `load_cases[]` with unique id/name and wind (`wind_speed_m_s`, m/s) or seismic (`seismic_zone_factor`, -); optional external forces (N), moments (N-mm), component and elevation (mm). | `axial_force`, `resultant_shear` (N), `overturning_moment`, `torsional_moment` (N-mm), source snapshot; `REVIEW REQUIRED`. |
| `global_load_combination` | Two or more known case ids and matching `load_factors` (-); concurrent cases. Wind and seismic cannot be combined by current domain validation. | Case ids/factors (-), axial/shear (N), overturning/torsional moments (N-mm); `REVIEW REQUIRED`. |
| `load_combination` (EN) | EN project, known load cases and combination ids/factors; optional standard and edition. | Intended combined forces/moments (N/N-mm); EN route is unsupported and returns `NOT CALCULATED`. |
| `external_pressure` | ASME shell/head; external pressure >0 MPa or vacuum; positive component `ug28_strain_factor_a` (-) and `ug28_allowable_stress_b` (MPa), geometry/material. | `D_mm`, `L_mm`, `t_mm`, `P_external_MPa`, A (-), B (MPa); preliminary allowable/status, `REVIEW REQUIRED`. |
| `external_pressure_check`, `vacuum_stability` | Vacuum route needs `vacuum_condition=true`, shell geometry and A/B data; delegated shell pressure is 0.101325 MPa. | Wrapper returns shell calculation as `external_pressure`; `external_pressure_check` appears only in missing-module fallback. Normal connected route cannot emit these requested type names. |
| MDMT coincident ratio | Existing UCS-66 inputs: minimum design temperature, component material/thickness and optional `impact_test_temperature_C`. No coincident load-ratio field exists in domain/project models or the ASME MDMT input assembly. | MDMT rows include thickness (mm), curve group (-), impact temperature and allowable MDMT (degC); ratio is not consumed/emitted. |
| Static liquid head | `design_conditions.fluid_density_kg_m3` (kg/m3), load-case `fluid_density_kg_m3` and `fluid_level_mm` (mm); component reference elevation must be positive for MAWP correction. | `static_head_delta_P`, `MAWP_corrected` (MPa). Fixture elevations default to zero, so the campaign example can verify input fields but not a corrected value. |
| `pressure_consistency` | `operating_pressure` > `design_pressure` (MPa) triggers review. | Pressure fields (MPa), review status; consistent inputs produce no row. |
| `material_check` | Emitted only when a component material id is absent from `materials[]`. | Missing material/component identity; implementation marks the result `NOT CALCULATED`, so no qualifying example is possible. |
| `fatigue` | EN `design_cycles` (cycles), `material_fatigue_data`, component/detail stress ranges and category. | Input snapshot includes cycles/material data; current implementation returns `NOT CALCULATED` because fatigue curves and cycle assessment are unimplemented. |

## Examples

`tools.campaign.examples` supplies verified projects for every connected route
that can produce a result other than `BLOCKED` / `NOT CALCULATED`, including
saddle, leg details, flange stress, junction input review, global loads, external
pressure, and pressure consistency. Tests execute every example with
`harness.run_case`. No example is claimed for `flange` and `load_combination`
(EN methods return unsupported `NOT CALCULATED`), `external_pressure_check`
(normal wrapper emits `external_pressure`), `vacuum_stability` (delegation
returns the shell row type), `material_check` (the only trigger is
`NOT CALCULATED`), or `fatigue` (unsupported even with inputs). `junction_check`
is triggerable as an input/topology review only, not numerical adequacy. The
coincident MDMT ratio is absent from the model and solver input contract.

**TETİKLENEMEZ evidence (source lines):** `flange` and EN `load_combination`
are explicitly returned as unsupported in
`packages/code-en-13445/src/code_en_13445/design_code.py:737-769`;
`external_pressure_check` exists only in the import-failure branch at
`packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py:2029-2041`, while
the connected solver produces `external_pressure` at
`packages/external-pressure/src/external_pressure/ext_pressure.py:47-73`;
vacuum delegates to the shell external-pressure solver at
`packages/external-pressure/src/external_pressure/ext_pressure.py:325-358`;
`material_check` is created only for an unresolved material and set
`NOT CALCULATED` at `packages/calc-core/src/calc_core/orchestrator.py:490-507`;
fatigue remains unsupported with populated inputs at
`packages/code-en-13445/src/code_en_13445/design_code.py:749-769`. MDMT
assembles only component, conditions, materials, curve group, thickness and
impact temperature at `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py:1320-1340`;
no coincident-ratio field is modeled. The global-load validator rejects
wind+seismic concurrency at `packages/domain/src/domain/load_cases.py:351-369`.
