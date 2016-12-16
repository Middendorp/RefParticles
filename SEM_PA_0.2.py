# -*- coding: utf-8 -*-

# Modules
import numpy as np
from bokeh.io import push_notebook, show, output_notebook, output_file
from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CustomJS, HoverTool


# Import data
file = "G:\\SG160311_01_PA_SE\\sg160311_01_pa_se.csv"
#file = "G:\\SG160311_01_PA_SE\\sg160311_01_pa_se_small.txt"
data = np.loadtxt(file, delimiter=',', skiprows=13)
with open(file) as f:
	for i in range(0, 13):
		line = f.readline()
columns = line.split(',')

# Prepare bokeh
useWebGL = True
output_notebook()
output_file("test.html")
TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select,tap,save,hover"
POINT_SIZE = 3

# Assign source data
source = ColumnDataSource(data=dict(
	d=data[:,13], 
	r=data[:,13]*0.005,
	x=data[:,26], 
	y=data[:,27], 
	A=data[:,18], 
	U=data[:,23], 
	O=data[:,21],
	Si=data[:,22],
	C=data[:,20]
	))


# Initial plots
gDistribution = figure(tools=TOOLS, active_drag="lasso_select", active_scroll="wheel_zoom", title="Particle distribution", x_axis_label='x / mm', y_axis_label='y / mm', webgl=useWebGL)
gDistribution.circle('x', 'y', radius='r', source=source, line_color="#005B82", fill_color="#005B82", fill_alpha=0.5)

gDiamAspe = figure(tools=TOOLS, active_drag="lasso_select", active_scroll="wheel_zoom", title="Morphology", x_axis_label="Diameter", y_axis_label="Aspect ratio", webgl=useWebGL)
gDiamAspe.circle('d', 'A', source=source, size=POINT_SIZE, line_color="#005B82", fill_color="#005B82", fill_alpha=1)

gChem = figure(tools=TOOLS, active_drag="lasso_select", active_scroll="wheel_zoom", title="Chemical composition", x_axis_label="Uranium (wt.%)", y_axis_label="Oxygen (wt.%)", webgl=useWebGL)
gChem.circle('U', 'O', source=source, size=POINT_SIZE, line_color="#005B82", fill_color="#005B82", fill_alpha=1)

hist, edges = np.histogram(data[:,13], density=True, bins=50)
gHist = figure(tools=TOOLS, active_drag="lasso_select", active_scroll="wheel_zoom", title="Particle size distribution", x_axis_label="Diameter / um", y_axis_label="Number of particles", webgl=useWebGL)
gHist.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="#005B82", line_color="#005B82", fill_alpha=0.25)



# Plot selected points
s2 = ColumnDataSource(data=dict(x=[], y=[], r=[], d=[], A=[], U=[], O=[], Si=[], C=[]))
gDistribution.circle('x', 'y', radius='r', source=s2, line_color="#D52D12", fill_color="#D52D12", fill_alpha=0.5)
gDiamAspe.circle('d', 'A', source=s2, size=POINT_SIZE, line_color="#D52D12", fill_color="#D52D12", fill_alpha=1)
gChem.circle('U', 'O', source=s2, size=POINT_SIZE, line_color="#D52D12", fill_color="#D52D12", fill_alpha=1)

# JS
source.callback = CustomJS(args=dict(s2=s2), code="""
        var inds = cb_obj.selected['1d'].indices;
        var d1 = cb_obj.data;
        var d2 = s2.data;
        d2['x'] = []
        d2['y'] = []
        d2['r'] = []
        d2['d'] = []
        d2['A'] = []
        d2['U'] = []
        d2['O'] = []
        d2['Si'] = []
        d2['C'] = []
        for (i = 0; i < inds.length; i++) {
            d2['x'].push(d1['x'][inds[i]])
            d2['y'].push(d1['y'][inds[i]])
            d2['r'].push(d1['r'][inds[i]])
            d2['d'].push(d1['d'][inds[i]])
            d2['A'].push(d1['A'][inds[i]])
            d2['U'].push(d1['U'][inds[i]])
            d2['O'].push(d1['O'][inds[i]])
            d2['Si'].push(d1['Si'][inds[i]])
            d2['C'].push(d1['C'][inds[i]])
        }
        s2.trigger('change');
    """)

# Hoven tooltips
hover = gDistribution.select(dict(type=HoverTool))
hover.tooltips=[
		("Index", "$index"),
		("Position", "$x, $y"),
		("Diameter", "@d"),
  		("Aspect ratio", "@A"),
    		("Composition", "@U U; @O O; @Si Si; @C C")
]

# Show all graphs
p = gridplot([[gDistribution, gHist], [gDiamAspe, gChem]])
t = show(p, notebook_handle=True)
