include <parameters.scad> //text and options are imported from here
//top_text = "eV";
//bottom_text = "7393";
//top_text = "Custom";
//bottom_text = "Text!";
//top_text = "Let's go";
//bottom_text = "eVolts!";
//top_text = "";
//bottom_text = "";

//import(str(dir, "/static/stl_src/skydive_amongus_voron.3mf"));
translate([-60,-60,0])
    import(str(dir, "/static/stl_src/skydive_amongus_eV.stl"));

module my_text(t) {
//    text(t, halign="center", $fn=60, font="Liberation Sans:style=Bold");
//    text(t, halign="center", $fn=60, font="Acknowledge TT BRK:style=Regular");
//    text(t, halign="center", $fn=60, font="Angostura Black:style=Bold");
//    text(t, halign="center", $fn=60, font="Automatica BRK:style=Bold");
//    text(t, halign="center", $fn=60, font="Baltar:style=Regular");
//    text(t, halign="center", $fn=60, font="Blue Highway Condensed:style=Bold");
//    text(t, halign="center", $fn=60, font="Droid:style=Bold");
//    text(t, halign="center", $fn=60, font="Engebrechtre:style=Bold");
//    text(t, halign="center", $fn=60, font="Kenyan Coffee:style=Bold"); //ok
//    text(t, halign="center", $fn=60, font="Kimberley:style=Bold");
//    text(t, halign="center", $fn=60, font="Pakenham:style=Regular"); //good
//    text(t, halign="center", $fn=60, font="Quadrangle:style=Bold");
    text(t, halign="center", $fn=10, font="Roboto Condensed:style=Bold"); //good
//    text(t, halign="center", $fn=60, font="Unispace:style=Bold");
//    text(t, halign="center", $fn=60, font="Upheaval TT BRK:style=Bold");
//    text(t, halign="center", $fn=60, font="Yielding BRK:style=Bold");
}

module my_text_line(t) {
    if (len(t) >= 3) {
        resize(newsize=[14,6])
            my_text(t);
    }
    if (len(t) == 2) {
        resize(newsize=[10,6])
            my_text(t);
    }
    if (len(t) == 1) {
        resize(newsize=[5,6])
            my_text(t);
    }
}

intersection() {
    rotate([90,0,180])
    translate([-0.2,23.5,10])
    linear_extrude(5) {
        if (len(bottom_text) > 0) { //if there are 2 lines of text
            my_text_line(top_text); //top text
            translate([0,-7.75,0]) my_text_line(bottom_text); //bottom text
        }
        
        if (len(bottom_text) == 0) { //if there is only 1 line of text
            if (len(top_text) >= 3) {
                resize(newsize=[14,6.5])
                    translate([0,-7.75,0])
                        my_text(top_text);
            }
            if (len(top_text) == 2) {
                if (top_text[0] == "j") {
                    translate([1,-6,0])
                        resize(newsize=[14,10])
                            my_text(top_text);
                }
                if (top_text[0] != "j") {
                    translate([0,-6,0])
                        resize(newsize=[14,10])
                            my_text(top_text);
                }
                
            }
            if (len(top_text) == 1) {
                translate([0,-6,0])
                    resize(newsize=[10,12])
                        my_text(top_text);
            }
        }
    }

    translate([0,-27.1,-20])
    cylinder(100,40,40, $fn=300);
}

if (shoes) {
    mirror([1,0,0]) translate([16.5,-25,0]) scale(.4) translate([0,0,-5.0605]) rotate(90) import(str(dir, "/static/stl_src/KD8-low-poly.stl"));
    translate([16.5,-25,0]) scale(.4) translate([0,0,-5.0605]) rotate(90) import(str(dir, "/static/stl_src/KD8-low-poly.stl"));
//    scale(1.4) translate([5,-55,0]) import("static/stl_src/converse.stl");
//    intersection() {
//        translate([0,-30,0]) cube([50,50,50]);
//    scale(1.4) translate([5,-55,0]) import("static/stl_src/converse.stl");
//    }
//    mirror([1,0,0]) intersection() {
//        translate([0,-30,0]) cube([50,50,50]);
//    scale(1.4) translate([5,-55,0]) import("static/stl_src/converse.stl");
//    }
//    translate([-7,-10,0]) scale(0.25) rotate(-90) import("static/stl_src/AirMax_1.stl");
//    mirror([1,0,0]) translate([-7,-10,0]) scale(0.25) rotate(-90) import("static/stl_src/AirMax_1.stl");
//    translate([10,8,0]) scale(0.55) rotate(180) import("static/stl_src/NEW_AJ_6_keychain.stl");
//    mirror([1,0,0]) translate([10,8,0]) scale(0.55) rotate(180) import("static/stl_src/NEW_AJ_6_keychain.stl");
}