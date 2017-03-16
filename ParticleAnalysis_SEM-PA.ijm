directory = "F:\\PA_suspension\\PA_SG170216_02\\stub01\\";
I_min = 21;
N = 576;
	
function analyze(id) {
	open(directory+id+"/search.png");
	rename(id);
	
	open(directory+id+"/search.png");
	rename("test");
	
	selectWindow("test");
	run("8-bit");
	run("Set Scale...", "distance=1 known=1 pixel=1 unit=px");
	setThreshold(I_min, 255);
	run("Convert to Mask");

	run("Set Measurements...", "area mean standard modal min centroid perimeter fit shape display redirect="+id+" decimal=3");
	run("Analyze Particles...", "size=4-Infinity display exclude include record");

	selectWindow("test");
	close();
	selectWindow(id);
	close();
}

run("Clear Results");
for (i = 1; i < N+1; i++) {
	if(i<10) {
		analyze("fld000"+i);
	} else if(i<100) {
		analyze("fld00"+i);
	} else if(i<1000) {
		analyze("fld0"+i);
	} else {
		analyze("fld"+i);
	}
}