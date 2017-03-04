# Jupyter notebook SEM particle analysis
A number of notebooks to analyze the data obtained from a SEM particle analysis, the following notebooks are available, all of which can be executed individually, but are combined in the *Particle-analysis* notebook:

- ***[Particle-analysis](Particle-analysis.ipynb)*** - Combined all notebooks into a single output file
- *[ImportData](ImportData.ipynb)* - Imports the measured data into a dataframe
- *[ImageStitching](#ImageStitching)* - Takes snapshots of each discovered particle and combines it into a single image compilation
- *[EDXProcess](#EDXProcess)* - Import the collected EDX spectra (spc files)
- *[ParticleClassification](#ParticleClassification)* - Classifies the particles into various groups
- *[InterparticleDistance](#InterparticleDistance)* - Calculates the distance to the nearest neighbor for each particle
- *[Bokehgraphs](#Bokehgraphs)* - Creates interactive Bokeh graphs to visualize the data
