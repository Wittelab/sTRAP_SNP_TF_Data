# sTRAP_SNP_TF_Data
Scripts &amp; Data for Predicting Transcription Factor Binding Sites Modulated by Single Nucleotide Polymorphisms

Please cite the following publication if these data or scripts are used for new projects:  
[Emami N.C., Cavazo T.B., et al. Large-Scale Association Study Detects Novel Rare Variants, Risk Genes Functional Elements, and Polygenic Architecture of Prostate Cancer Susceptibility. Cancer Research 2020)

## Getting Started 
### Installing Selenium

Selenium is a tool for automating control of your web browser, and for interfacing with web tools and webservers. We implement a python script for automatically running transcription factor binding prediction, using the sTRAP webserver, and using the Selenium Webdriver.

Dependencies: Python v2.7, Google Chrome

Step 1: Install Selenium Python Package
```bash
pip install selenium
```

Step 2: Download Selenium WebDriver Application
(see https://selenium-python.readthedocs.io/installation.html#drivers)

Step 3: Move the WebDriver Application to your `Applications` folder

## Example Usage

The program is run from the commany line using Python v2.7, and passing (a) a .txt file where each line lists a dbSNP rsid, and (b) the path to an existing directory to place the output files in.

```bash
python SNP_TFBS_Affinity.py --rsid_file input_rsids.txt --output_dir ./PrCa_GWAS_Lead_SNP_sTRAP_Results/
```

That's it!
