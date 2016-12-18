# -*- coding: utf-8 -*-

# Modules
import numpy as np
import jinja2
#from bokeh.io import show, output_file
from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CustomJS, HoverTool, TapTool, BoxSelectTool, LassoSelectTool
from bokeh.models.widgets import Select,TextInput
from bokeh.models.layouts import HBox, VBox
from bokeh.resources import CDN
from bokeh.embed import file_html
import tkinter as tk
from tkinter import filedialog
from os import listdir
from datetime import date

sampleName="Test"

# Ask for directory and search for csv file
root = tk.Tk()
directory = filedialog.askdirectory(title="Select the folder containing the particle analysis:", mustexist=True)
root.destroy()

if directory=='':
    print("Directory selection closed, using default location.")
    directory="F:\\SupportData"

for i in listdir(directory):
    if i.endswith(".csv"):
        file = directory+"\\"+i

# Import file
with open(file) as f:
    for i in range(0, 20):
        line = f.readline().replace("\n", "").split(',')
        if(line[0].strip()=="Part#"):
            columns = line
            skip=i
        elif(line[0].strip()=="Date"):
            datum = date(int(line[3]), int(line[1]), int(line[2]))
        elif(line[0].strip()=="Acc."):
            voltage = float(line[2])
        elif(line[0].strip()=="Magn:"):
            magnification = int(line[1])
        elif(line[0].strip()=="Preset"):
            MeasTime = float(line[2])
data = np.loadtxt(file, delimiter=',', skiprows=skip+1)

# Link data to columns
columns_def = ["Part#", "Aspe", "AvgDiam", "StgX", "StgY", "CK", "OK", "SiK", "UM", "ClK", "X_stage", "Y_stage", "Xferet", "Yferet", "Orient", "Field#", "CeL"]
columns_val = [0,       1,      2,         3,      4,      5,    6,    7,     8,    9,     10,        11,        12,       13,       14,       15,       16]
columns_fnd = np.zeros(len(columns_def))

for i in range(0,len(columns)):
    temp = columns[i].strip()
    for col in range(0,len(columns_def)):
        if(temp==columns_def[col]):
            columns_val[col]=data[:,i]
            columns_fnd[col]=1
            #print(temp)
    
for col in range(0,len(columns_def)):
    if(columns_fnd[col]==0):
        columns_val[col]=np.zeros(len(data[:,1]))

# Get field data
temp = listdir(directory+"\\stub01\\") 
numFields = 0

for i in range(0,len(temp)):       
    if(temp[i][:3]=="fld"):
        numFields+=1
        #print(int(temp[i][-4:]))

Fields = np.zeros((numFields, 3))
for i in range(0,len(data[:,0])):
    temp = int(columns_val[15][i]-10000-1)
    Fields[temp, 0] = columns_val[10][i]/1000
    Fields[temp, 1] = columns_val[11][i]/1000

for i in range(0,len(Fields[:,0])):
    if(Fields[i,0]==0 and Fields[i,1]==0):
        print("No particles found on field "+str(i))
        
# Find field size
with open(directory+"\\stub01\\Stub Summary.txt") as f:
    for i in range(0,20):
        line = f.readline().replace("\n", "").split(':')
        if(line[0].strip()=="Field size (mm)"):
            temp = line[1].split("x")
            FieldX = float(temp[0])
            FieldY = float(temp[1])
	
# Prepare bokeh
useWebGL = False
TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select,tap,save,hover"
POINT_SIZE = 3
cBLUE = "#005B82"
cRED = "#D52D12"
cGray = "#CDCDCD"

# Assign source data
source = ColumnDataSource(data=dict(
	ID=columns_val[0], 
	d=columns_val[2], 
	r=columns_val[2]*0.005,
	x=columns_val[3], 
	y=columns_val[4], 
	A=columns_val[1], 
	U=columns_val[8], 
	O=columns_val[6],
	Si=columns_val[7],
	C=columns_val[5],
	Cl=columns_val[9],
	Ce=columns_val[16],
	Field=columns_val[15],
	XX=columns_val[2],
 	YY=columns_val[1],
	))
s2 = ColumnDataSource(data=dict(x=[], y=[], r=[], d=[], A=[], U=[], O=[], Si=[], C=[], Field=[], ID=[], Ce=[], Cl=[], XX=[], YY=[]))
hist, edges = np.histogram(columns_val[2], density=True, bins=50)
ChartAxes = ["d", "A", "U", "C", "O", "Cl", "Ce"]

# Particle distribution
gDistribution = figure(tools=TOOLS, active_drag="lasso_select", active_scroll="wheel_zoom", title="Particle distribution", x_axis_label='x / mm', y_axis_label='y / mm', webgl=useWebGL)
gDistribution.rect(x=Fields[:,0], y=Fields[:,1], width=FieldX, height=FieldY, angle=0, line_color=cGray, fill_color=cGray, line_alpha=0.5, fill_alpha=0.25)
gDistribution.circle('x', 'y', radius='r', source=source, line_color=cBLUE, fill_color=cBLUE, fill_alpha=0.5)
gDistribution.circle('x', 'y', radius='r', source=s2, line_color=cRED, fill_color=cRED, fill_alpha=0.5)
gDistribution.select(BoxSelectTool).select_every_mousemove = False
gDistribution.select(LassoSelectTool).select_every_mousemove = False

# Histogram
gHist = figure(tools="save", title="Histogram", x_axis_label="d / um", y_axis_label="N", webgl=useWebGL)
gHist.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color=cBLUE, line_color=cBLUE, fill_alpha=0.25)

# Graph with variable axis
gChart = figure(tools=TOOLS, active_drag="lasso_select", active_scroll="wheel_zoom", title="", x_axis_label="x-axis", y_axis_label="y-axis", webgl=useWebGL)
gChart.circle('XX', 'YY', source=source, size=POINT_SIZE, line_color=cBLUE, fill_color=cBLUE, fill_alpha=1)
gChart.circle('XX', 'YY', source=s2, size=POINT_SIZE, line_color=cRED, fill_color=cRED, fill_alpha=0.5)

# JS callback, after change of selection
source.callback = CustomJS(args=dict(s2=s2), code="""
        var inds = cb_obj.selected['1d'].indices;
        var d1 = cb_obj.data;
        var d2 = s2.data;
        var dSum = 0;
                
        d2['ID'] = []
        d2['x'] = []
        d2['y'] = []
        d2['r'] = []
        d2['d'] = []
        d2['A'] = []
        d2['U'] = []
        d2['O'] = []
        d2['Si'] = []
        d2['C'] = []
        d2['Ce'] = []
        d2['Ce'] = []
        d2['Cl'] = []
        d2['XX'] = []
        d2['YY'] = []
               
        // Loop through all selected items
        for (i = 0; i < inds.length; i++) {
            d2['ID'].push(d1['ID'][inds[i]])
            d2['x'].push(d1['x'][inds[i]])
            d2['y'].push(d1['y'][inds[i]])
            d2['r'].push(d1['r'][inds[i]])
            d2['d'].push(d1['d'][inds[i]])
            d2['A'].push(d1['A'][inds[i]])
            d2['U'].push(d1['U'][inds[i]])
            d2['O'].push(d1['O'][inds[i]])
            d2['Si'].push(d1['Si'][inds[i]])
            d2['C'].push(d1['C'][inds[i]])
            d2['Ce'].push(d1['Ce'][inds[i]])
            d2['Cl'].push(d1['Cl'][inds[i]])
            d2['Field'].push(d1['Field'][inds[i]])
            d2['XX'].push(d1['XX'][inds[i]])
            d2['YY'].push(d1['YY'][inds[i]])
            
            dSum += d1['d'][inds[i]];
        }
                        
        document.getElementById('statNsel').innerHTML=inds.length.toString();
        document.getElementById('statdMeanSel').innerHTML=(dSum/inds.length).toString();
        document.getElementById('statdMedianSel').innerHTML="-";
        
        s2.trigger('change');
    """)

# JC callback after selection of particle (change image)
callTab = CustomJS(args=dict(s2=s2), code="""
    var inds = cb_obj.selected['1d'].indices;
    var d1 = cb_obj.data;
    var field = d1['Field'][inds[0]];
    
    field = field-10000;
    field="00000"+field.toString()
    field = field.substr(field.length-4);
    
    document.getElementById('pImgParticle').innerHTML=field;    
    document.getElementById('imgParticle').src="./stub01/fld"+field+"/search.png";
    document.getElementById('aImgParticle').href='./stub01/fld'+field+'/search.png';
""")

# Apply callbacks to graphs
tDistribution = gDistribution.select(type=TapTool)
tDistribution.callback = callTab
tChart = gChart.select(type=TapTool)
tChart.callback = callTab

# Function to change axis
code="""
        var data = source.get('data');
        var r = data[cb_obj.get('value')];
        var {var} = data[cb_obj.get('value')];
        //window.alert( "{var} " + cb_obj.get('value') + {var}  );
        for (i = 0; i < r.length; i++) {{
            {var}[i] = r[i] ;
            data['{var}'][i] = r[i];
        }}
        source.trigger('change');
    """
    
callbackx = CustomJS(args=dict(source=source), code=code.format(var="XX"))
callbacky = CustomJS(args=dict(source=source), code=code.format(var="YY"))

selectX = Select(title="X axis:", value="d", options=ChartAxes, callback=callbackx)
selectY = Select(title="Y axis:", value="A", options=ChartAxes, callback=callbacky)


# Hover tooltips (for distribution)
hover = gDistribution.select(dict(type=HoverTool))
hover.tooltips=[
    ("ID", "@ID"),
    ("Field", "@Field"),
    ("Position", "@x, @y"),
    ("Diameter", "@d"),
    ("Aspect ratio", "@A"),
    ("Composition", ""),
    ("U", "@U"),
    ("O", "@O"),
    ("C", "@C"),
    ("Si", "@Si"),
    ("Cl", "@Cl"),
]

# Show all graphs
controls = VBox(selectX, selectY)
p = gridplot([[gDistribution, controls], [gHist, gChart]])
#t = show(p, notebook_handle=True)

# HTML template to embed graphs
template = jinja2.Template("""
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{{ title if title else "Bokeh Plot" }}</title>
        {{ bokeh_css }}
        {{ bokeh_js }}
        <style>
          html {
            width: 100%;
            height: 100%;
          }
          body {
            width: 90%;
            height: 100%;
            margin: auto;
          }
          table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
          }
        </style>
    </head>
    <body>
        <h1>"""+sampleName+"""</h1>
        <hr>
        
        <h2>Information</h2>
        <div>
            Date: """+datum.strftime("%A %d. %B %Y")+"""<br>
            Magnification: """+str(magnification)+"""x<br>
            Voltage: """+str(voltage)+""" kV<br>
            EDX measurement time: """+str(MeasTime)+""" s<br>
        </div>
        
        <h2>Statistics</h2>
        <table>
            <tr>
                <th></th>
                <th>All</th> 
                <th>Selected</th>
            </tr>
            <tr>
                <td>Number</td>
                <td id='statNall'>"""+str(len(columns_val[0]))+"""</td> 
                <td id='statNsel'>0</td>
            </tr>
            <tr>
                <td>Average diameter</td>
                <td id='statdMeanAll'>"""+str(np.mean(columns_val[2]))+"""</td> 
                <td id='statdMeanSel'>-</td>
            </tr>
            <tr>
                <td>Median diameter</td>
                <td id='statdMedianAll'>"""+str(np.median(columns_val[2]))+"""</td> 
                <td id='statdMedianSel'>-</td>
            </tr>
        </table> 
        
        <h2>Micrographs</h2>
        <div>
            <a id="aImgParticle" href="./stub01/fld0001/search.png" target="_blank"><img id="imgParticle" src="./stub01/fld0001/search.png" alt="" width="500px">
            <p id="pImgParticle">Field 1</p></a>
        </div>
        
        <h2>Graphs</h2>        
        {{ plot_div|indent(8) }}
        {{ plot_script|indent(8) }}
    </body>
</html>
""")

# Export html file
html = file_html(p, CDN, title="SEM PA Analysis", template=template)
with open(directory+"\\report.html", "w") as f:
    f.write(html)
    
print("===== finished =====")
