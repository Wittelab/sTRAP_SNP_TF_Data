from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import re, argparse, os, shutil, copy

def main(rsid_file, output_directory):
  # Initalize Variables
  rsid_list = []
  rsid_alleles = {}
  rsid_flanking_seq = {}
  unsuccessful = []
  
  # Fire up Chrome
  driver = webdriver.Chrome()

  # Parse the input rsids
  with open(rsid_file,"r") as infh:
    for line in infh:
      rsid = line.strip()
      rsid_list.append(rsid)

  # For each SNP, get major / minor alleles
  for rsid in rsid_list:
    print "Processing %s" % (rsid,)
    alleles = get_snp_alleles(driver, rsid, output_directory)
    if alleles == "indel":
      unsuccessful.append(rsid)
      continue
    elif not alleles:
      unsuccessful.append(rsid)
      continue
    else:
      rsid_alleles[rsid] = alleles

  rsid_list = [rsid for rsid in rsid_list if rsid not in unsuccessful]
  # Batch retreive flanking sequences from UCSC Table Browser
  rsid_flanking_seq = get_SNP_Flanking_Sequences(driver, rsid_list, rsid_alleles, rsid_flanking_seq, output_directory)

  # Get affinity diffs
  for rsid in rsid_list:
    get_SNP_affinities(driver, rsid, rsid_alleles[rsid], rsid_flanking_seq[rsid], output_directory)

# Split up FASTA files into chunks
def chunk(input_array, chunk_size):
  """Yield successive n-sized chunks from l."""
  for index in range(0, len(input_array), chunk_size):
      yield input_array[index:index + chunk_size]

# Reverse complement flanking sequences
def revComp(input_sequence):
  complement_dict = {"A":"T","T":"A","C":"G","G":"C","-":"-"}
  return "".join([complement_dict[input_sequence[base_index].upper()] for base_index in range(len(input_sequence)-1,-1,-1)])

# Get major / minor allele for an rsid from dbSNP
def get_snp_alleles(driver, rsid, output_directory, recurse=0):
  if not recurse:
    driver.get("https://www.ncbi.nlm.nih.gov/snp/%s" % (rsid,))
  else:
    driver.switch_to.window(driver.window_handles[-1])
  try:
    dbsnp_header = driver.find_element_by_xpath('//*[@id="main_content"]/main/div[4]/dl[1]/dd[3]')
    alleles = dbsnp_header.text.split("/")[0].split(">")
    variation_type = driver.find_element_by_xpath('//*[@id="main_content"]/main/div[4]/dl[1]/dd[4]')
    is_snv = "SNV" in variation_type.text
    if not is_snv:
      with open("%s/unsuccessful.txt" % (output_directory,),"a") as outfh:
        outfh.write("\t".join([rsid, str(variation_type.text)])+"\n")
      return "indel"
    else:
      return alleles
  except Exception as e:
    status = driver.find_element_by_xpath('//*[@id="main_content"]/main/div[4]/div[2]')
    if "was merged into" in status.text:
      merged_url = driver.find_element_by_xpath('//*[@id="main_content"]/main/div[4]/div[2]/dd/a')
      merged_url.click()
      return get_snp_alleles(driver, rsid, output_directory, 1)
    else:
      with open("%s/unsuccessful.txt" % (output_directory),"a") as outfh:
        outfh.write("\t".join([rsid, "Error", "Could not parse dbSNP for %s" % (rsid,)])+"\n")
      return 0

# Get flanking sequences for each input SNP from the UCSC Table Browser
def get_SNP_Flanking_Sequences(driver, rsid_list, rsid_alleles, rsid_flanking_seq, output_directory):
  # driver.get("http://genome.ucsc.edu/cgi-bin/hgTables?hgta_doMainPage=1&db=hg19&hgta_group=varRep&hgta_track=snp150Common&hgta_table=snp150Common")
  driver.get("http://genome.ucsc.edu/cgi-bin/hgTables?hgta_doMainPage=1&db=hg19&hgta_group=varRep&hgta_track=snp150&hgta_table=snp150")
  driver.find_element_by_xpath('//*[@id="hgta_doPasteIdentifiers"]').click()
  
  driver.find_element_by_xpath('//*[@id="hgta_doClearPasteIdentifierText"]').click()
  driver.find_element_by_xpath('//*[@id="firstSection"]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/td[2]/form/textarea').send_keys("\n".join(rsid_list))
  driver.find_element_by_xpath('//*[@id="hgta_doPastedIdentiers"]').click()
  
  try:
    # select = Select(driver.find_element_by_xpath('//*[@id="firstSection"]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/td[2]/form[1]/table/tbody/tr[9]/td/select'))
    select = Select(driver.find_element_by_xpath('//*[@id="outputTypeDropdown"]'))
    select.select_by_visible_text("sequence")
    driver.find_element_by_xpath('//*[@id="hgta_doTopSubmit"]').click()
    
    driver.find_element_by_xpath('//*[@id="hgSeq.padding5"]').clear()
    driver.find_element_by_xpath('//*[@id="hgSeq.padding5"]').send_keys("25")
    driver.find_element_by_xpath('//*[@id="hgSeq.padding3"]').clear()
    driver.find_element_by_xpath('//*[@id="hgSeq.padding3"]').send_keys("25")
    
    driver.find_element_by_xpath('//*[@id="hgta_doGenomicDna"]').click()
    
    snplines = driver.find_element_by_xpath('/html/body/pre').text.split("\n")
    for fasta_chunk in chunk(snplines, 3):
      header = fasta_chunk[0]
      rsid_match = re.search("rs[\d]+",header)
      rsid = rsid_match.group(0)
      if rsid not in rsid_alleles:
        continue
      strand_match = re.search("strand=([-|+])",header)
      strand = strand_match.group(1)
      flanking_sequence = fasta_chunk[1].strip() + fasta_chunk[2].strip()
      if strand == "-":
        flanking_sequence = revComp(flanking_sequence)
      if flanking_sequence[25] not in rsid_alleles[rsid] and revComp(flanking_sequence)[25] in rsid_alleles[rsid]:
        flanking_sequence = revComp(flanking_sequence)
        print "%s alleles %s evidently match opposite strand, reference position allele %s flipped twice" % (rsid, str(rsid_alleles[rsid]), flanking_sequence[25],)
      rsid_flanking_seq[rsid] = flanking_sequence

    return rsid_flanking_seq

  except Exception as e:
    warnlist = driver.find_element_by_xpath('//*[@id="warnList"]/li/a[1]')
    warnlist.click()
    warnsnps = driver.find_element_by_xpath('/html/body/pre').text.split("\n")
    for warnsnp in warnsnps:
      with open("%s/unsuccessful.txt" % (output_directory),"a") as outfh:
        outfh.write("\t".join([warnsnp, "In WarnSNPs; %s not in dbSNP build 150?" % (warnsnp,)])+"\n")
      rsid_list.remove(warnsnp)
    return get_SNP_Flanking_Sequences(driver, rsid_list, rsid_alleles, rsid_flanking_seq, output_directory)

# Submit a variant to the sTRAP TFBS affinity server
def get_SNP_affinities(driver, rsid, alleles, flanking_sequence, output_directory):
  driver.get("http://trap.molgen.mpg.de/cgi-bin/trap_two_seq_form.cgi")
  alleles_copy = copy.deepcopy(alleles)
  wt_allele = alleles_copy.pop(alleles_copy.index(flanking_sequence[25]))
  alt_allele = alleles_copy.pop(0)
  flanking_altseq = flanking_sequence[:25] + alt_allele + flanking_sequence[26:]
  fasta_string  = "> %s-%s\n" % (rsid, wt_allele)
  fasta_string += "%s\n" % (flanking_sequence)
  fasta_string += "> %s-%s\n" % (rsid, alt_allele); 
  fasta_string += "%s\n" % (flanking_altseq)
  with open(output_directory+"/%s.ref_alt.fasta" % (rsid),"a") as outfh:
    outfh.write(fasta_string)

  driver.find_element_by_xpath('//*[@id="content"]/form[2]/textarea').send_keys(fasta_string)
    
  # Use transfac_2010.1 vertebrates for TFBS affinities
  select = Select(driver.find_element_by_xpath('//*[@id="content"]/form[2]/select[1]'))
  select.select_by_visible_text("transfac_2010.1 vertebrates")

  # User human_promoters as the background
  select = Select(driver.find_element_by_xpath('//*[@id="content"]/form[2]/select[2]'))
  select.select_by_visible_text("human_promoters")

  driver.find_element_by_xpath('//*[@id="content"]/form[2]/p[5]/input').click()
  
  driver.find_element_by_xpath('//*[@id="content"]/p[2]/a').click()

  snplines = driver.find_element_by_xpath('/html/body/pre').text.split("\n")
  with open(output_directory+"/%s.sTRAP_TFBS_Affinity.txt" % (rsid),"a") as outfh:
    for snpline in snplines:
      outfh.write(snpline+"\n")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description = \
    'TFBS Affinity Automatic Parsing')
  parser.add_argument('--rsid_file', type = str, required = True, help = \
    'File of input rsids.')
  parser.add_argument('--output_dir', type = str, required = True, help = \
    'Name or path of output directory.')
  args = parser.parse_args()
  rsid_file = args.rsid_file
  output_directory = args.output_dir
  main(rsid_file, output_directory)
