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
and vessel/support loads. The current campaign base constructors do not model
flanges or a complete cone junction; those rows therefore have no verified
working example in this package.

## Examples

`tools.campaign.examples` supplies runnable projects for thickness, MAWP, nozzle
reinforcement, clash, weld validation, hydrotest, pneumatic test, MDMT, leg,
and skirt stress. `tests/campaign/test_examples.py` executes each through
`harness.run_case` and rejects missing, blocked or not-calculated target rows.
The other documented types are supported result contracts discovered in source,
but do not currently have verified examples using the available project base
schema/fixture; they are intentionally identified here rather than presented as
working examples. In particular, the harness horizontal base emits
`saddle_stress` as `BLOCKED MISSING INPUT`: its Zick call does not receive
`saddle_positions_mm`, `vessel_length`, `tangent_start_mm`, `head_depth_mm`,
`head_thickness_mm`, and explicit `zick_K1`, `zick_K2`, `zick_K3`, `zick_K6`,
`zick_K7` data. Wind/seismic cases, a populated flange, connected cone junction,
and MDMT coincident ratio likewise have no passing verified base example.
