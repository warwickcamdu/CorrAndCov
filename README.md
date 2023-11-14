# CorrAndCov

Based on code originally written by Kabir & Darius to calculate time-crosscorrelation of actin and HYE

Adapted to Python by Laura190, camdu@warwick.ac.uk

Download the bundled version from the latest release. \
Windows 10: https://github.com/warwickcamdu/CorrAndCov/releases/download/v0.0.1/CorrAndCov-0.0.1.zip \
Unzip the folder, navigate into the dist folder and run CorrAndCov.exe.

### What the code does
1. Coarse-grains the images
2. Calculates time Autocorrelation function for each box in Act channel using different time lags (Offset)
3. and Crosscorrelation between Act and the Binder chnls
4. Calculates 2d Coefficient-of-variation (CoV) Maps of Act, B1 and B2
6. Plots CoV of Actin vs CC of Act-B1 Act-B2 and B1-B2 (at different time lags)

### Run from source
```bash
cd CorrAndCov
conda env create -n myenv --file environment.yaml
conda activate myenv
python CorrAndCov.py
```
This code uses https://github.com/fatheral/matlab_imresize

### Documentation
https://warwickcamdu.github.io/CorrAndCov/
