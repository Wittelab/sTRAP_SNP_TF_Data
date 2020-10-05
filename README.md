# sTRAP_SNP_TF_Data
Scripts &amp; Data for Predicting Transcription Factor Binding Sites Modulated by Single Nucleotide Polymorphisms

Sample automation and management is increasingly important as the number and size of population-scale and high-throughput projects grow. This is particularly the case in large-scale population studies where sample size is far outpacing the commonly used 96-well plate format. To facilitate management and transfer of samples in this format, we present Samasy, a web-based application for the construction of a sample database, intuitive display of sample and batch information, and facilitation of automated sample transfer or subset. Samasy is designed with ease-of-use in mind, can be quickly set up, and runs in any web browser. 

Please cite the following publication if these data or scripts are used for new projects:  
[bioRxiv. 2020 Dec;65(6):357-360](https://www.ncbi.nlm.nih.gov/pubmed/30477330)

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