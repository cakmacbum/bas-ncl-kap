# V09 - F09 nozzle reinforcement independent confirmation

## Group and verdict

All 30 SAPMA rows compare `A_required`. Each discrepancy comes from the same root cause: the independent oracle calculates the host required thickness with a non-UG-27 equation. The published K2-02 example has a larger percentage difference, but the same cause.

| Group | Cases | Verdict | Direction | Difference |
|---|---:|---|---|---:|
| G1 - oracle host thickness equation | 30 | ORACLE_HATASI | Oracle understates required area; suite is correct | 1.278% for 29; K2-02: 2.158% |

The oracle uses `P*D/(2*S*E + 0.8*P)` at `oracle.py:5-7`. ASME VIII-1 UG-27(c)(1), circumferential stress, is `t=P*R/(S*E-0.6*P)`. For inside diameter `D_i`, the corroded inside radius is `R=D_i/2+CA`. The suite reuses host thickness calculation at `design_code.py:1066-1088, 1144-1159`; its UG-27 formula is independently implemented at `formulas.py:55-61`. Required area is `A=d*t_req` for these equal-stress radial cases (`reinforcement.py:269`, with `F=1` and `fr1=1`).

CA increases the inside radius. Mill tolerance is not subtracted from pressure-required thickness; it reduces available nominal metal. The cases below also show net available thickness and shell MAWP from `MAWP=S*E*t/(R+0.6*t)`. UG-40 limits eligible reinforcement area; UG-45 checks nozzle-neck minimum thickness. Neither substitutes for `t_req` in this `A_required` comparison.

## Hand checks

Common inputs: `P=1.2 MPa`, `S=138 MPa`, `E=1`. The longitudinal UG-27 thickness is lower than the circumferential value in both examples.

### ratio-0.05-pad-0

Inputs: `D_i=1000 mm`, shell nominal `12 mm`, `CA=2 mm`, `d=25 mm`, neck `8 mm`. Thus `R=1000/2+2=502 mm`. `t_req=1.2*502/(138-0.6*1.2)=602.4/137.28=4.388112 mm`; `A_req=25*4.388112=109.7028 mm2`, exactly matching suite output. Oracle gives `t=1.2*1000/(276+0.96)=4.332756 mm`, `A=108.3189 mm2`, exactly matching reference. Difference is 1.2776%, oracle low. Available net shell thickness is `12*(1-0.125)-2=8.5 mm`; shell `MAWP=138*8.5/(502+0.6*8.5)=2.312 MPa`.

### PUB-K2-02-PVE-S5

Inputs: `D_i=314.198 mm`, nominal `4.775 mm`, `CA=2 mm`, `d=47.498 mm`. `R=314.198/2+2=159.099 mm`. `t_req=1.2*159.099/137.28=1.390726 mm`; `A_req=47.498*1.390726=66.0567 mm2`, matching suite. Oracle gives `t=1.2*314.198/(276+0.96)=1.36135 mm`; `A=64.6611 mm2`, matching reference. Difference is 2.158%. Net available thickness is `4.775*(1-0.125)-2=2.1781 mm`; shell `MAWP=138*2.1781/(159.099+0.6*2.1781)=1.862 MPa`.

## Correction recommendation

Do not change suite code. Update the oracle to calculate host required thickness with UG-27(c)(1), corroded inside radius, and applicable joint efficiency; compare the resulting `t_req` and `A_required` consistently. This is a recommendation only and has not been applied.

HUKUM: suite_hatasi=0 (emniyetsiz=0) ? oracle_hatasi=1 ? formulasyon=0
