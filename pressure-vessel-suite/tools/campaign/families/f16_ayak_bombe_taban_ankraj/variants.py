from tools.campaign.bases import vertical_leg_tank


def variants():
    # One record models the complete leg set.
    grid = [
        (250,200,12,250,10,4,20,0,0),(250,200,16,250,10,4,20,0,0),
        (300,250,20,345,15,4,24,0,0),(200,200,10,250,8,4,16,0,0),
        (300,200,16,250,10,6,20,5e6,5e3),(300,250,20,345,15,8,24,1e7,1e4),
        (250,200,16,250,10,4,20,2e7,2e4),(350,300,25,345,20,8,30,5e7,5e4),
        (200,150,12,250,5,2,16,5e6,0),(400,300,30,345,25,12,30,1e8,1e5),
        (250,250,16,250,10,4,20,1e7,1e4),(300,200,20,345,12,6,24,2e7,2e4),
        (225,175,14,250,7,4,18,8e6,8e3),(350,250,22,345,18,8,27,3e7,3e4),
        (275,225,18,250,10,6,22,1.5e7,1.5e4),(325,275,24,345,16,8,26,4e7,4e4),
        (250,180,15,250,9,4,20,6e6,6e3),(300,300,20,345,20,8,24,2.5e7,2.5e4),
        (180,180,10,250,6,4,16,4e6,4e3),(400,250,25,345,18,10,30,6e7,6e4),
        (240,210,14,250,10,4,20,9e6,9e3),(330,240,21,345,14,8,25,3.5e7,3.5e4),
        (260,190,17,250,8,6,22,1.2e7,1.2e4),(360,280,26,345,22,10,28,7e7,7e4),
        (210,160,11,250,6,2,18,3e6,3e3),(380,320,28,345,25,12,32,9e7,9e4),
        (290,230,19,250,12,6,24,1.8e7,1.8e4),(340,260,23,345,16,8,26,4.5e7,4.5e4),
        (230,190,13,250,8,4,18,7e6,7e3),(370,290,27,345,20,10,30,8e7,8e4),
    ]
    rows = []
    for i, (L,W,t,Fy,fc,n,db,M,V) in enumerate(grid, 1):
        p = vertical_leg_tank()
        p["supports"][0].update(
            leg_attachment="bottom_head", leg_section_type="pipe",
            leg_profile_height_mm=100, leg_profile_width_mm=100, leg_web_thickness_mm=8,
            leg_unbraced_length_mm=600, leg_effective_length_factor_K=1,
            base_plate_length_mm=L, base_plate_width_mm=W, base_plate_thickness_mm=t,
            base_plate_yield_MPa=Fy, foundation_bearing_allowable_MPa=fc,
            anchor_bolt_count=n, anchor_bolt_diameter_mm=db,
            anchor_tension_allowable_N=50000, anchor_shear_allowable_N=25000,
            overturning_moment_Nmm=M, lateral_load_N=V)
        rows.append((f"GRID-{i:02d}", p))
    p = vertical_leg_tank(); p["supports"][0].update(leg_attachment="bottom_head", leg_section_type="pipe", leg_profile_height_mm=100, leg_profile_width_mm=100, leg_web_thickness_mm=8, leg_unbraced_length_mm=600, leg_effective_length_factor_K=1, anchor_bolt_count=0)
    rows.append(("INVALID-ANCHORS", p))
    p = vertical_leg_tank(); p["supports"][0].update(leg_attachment="bottom_head", leg_section_type="pipe", leg_profile_height_mm=100, leg_profile_width_mm=100, leg_web_thickness_mm=8, leg_unbraced_length_mm=600, leg_effective_length_factor_K=1)
    rows.append(("MISSING-PLATE", p))
    return rows
