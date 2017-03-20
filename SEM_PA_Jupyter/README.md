# Jupyter notebook SEM particle analysis
A number of notebooks to analyze the data obtained from a SEM particle analysis, the following notebooks are available, all of which can be executed individually, but are combined in the *Particle-analysis* notebook:

- ***[Particle-analysis](Particle-analysis.ipynb)*** - Combined all notebooks into a single output file
- *[ImportData](ImportData.ipynb)* - Imports the measured data into a dataframe
- *[ImageStitching](ImageStitching.ipynb)* - Takes snapshots of each discovered particle and combines it into a single image compilation
- *[EDXProcess](EDXProcess.ipynb)* - Import the collected EDX spectra (spc files)
- *[ParticleClassification](ParticleClassification.ipynb)* - Classifies the particles into various groups
- *[InterparticleDistance](InterparticleDistance.ipynb)* - Calculates the distance to the nearest neighbor for each particle
- *[Bokehgraphs](Bokehgraphs.ipynb)* - Creates interactive Bokeh graphs to visualize the data

Be carefull, when a large dataset has been loaded, the *ImageStitching*, *BokehGraphs* and especially *EDXProcess* take a very long time to execute.
