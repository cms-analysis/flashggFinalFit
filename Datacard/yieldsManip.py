import pandas, pickle
import glob
import re

tws = ['scaleWeight_4', 'scaleWeight_8', 'alphaSWeight_0', 'alphaSWeight_1', 'pdfWeight_1', 'pdfWeight_2', 'pdfWeight_3', 'pdfWeight_4', 'pdfWeight_5', 'pdfWeight_6', 'pdfWeight_7', 'pdfWeight_8', 'pdfWeight_9', 'pdfWeight_10', 'pdfWeight_11', 'pdfWeight_12', 'pdfWeight_13', 'pdfWeight_14', 'pdfWeight_15', 'pdfWeight_16', 'pdfWeight_17', 'pdfWeight_18', 'pdfWeight_19', 'pdfWeight_20', 'pdfWeight_21', 'pdfWeight_22', 'pdfWeight_23', 'pdfWeight_24', 'pdfWeight_25', 'pdfWeight_26', 'pdfWeight_27', 'pdfWeight_28', 'pdfWeight_29', 'pdfWeight_30', 'pdfWeight_31', 'pdfWeight_32', 'pdfWeight_33', 'pdfWeight_34', 'pdfWeight_35', 'pdfWeight_36', 'pdfWeight_37', 'pdfWeight_38', 'pdfWeight_39', 'pdfWeight_40', 'pdfWeight_41', 'pdfWeight_42', 'pdfWeight_43', 'pdfWeight_44', 'pdfWeight_45', 'pdfWeight_46', 'pdfWeight_47', 'pdfWeight_48', 'pdfWeight_49', 'pdfWeight_50', 'pdfWeight_51', 'pdfWeight_52', 'pdfWeight_53', 'pdfWeight_54', 'pdfWeight_55', 'pdfWeight_56', 'pdfWeight_57', 'pdfWeight_58', 'pdfWeight_59']

yfiles = glob.glob("yields_pass2_nominal/*.pkl")
for yfidx, yf in enumerate(yfiles):
  print " --> Processing: %s (%s)"%(yf,yfidx)

  with open(yf,"r") as fpkl: data = pickle.load(fpkl)

  # First update UL values
  mask = (data['year']=='2017')&(data['type']=='sig')
  for ir,r in data[mask].iterrows():
    p = r['proc']
    #print " Proc: %s"%p
    p_2016 = re.sub("2017","2016",p)
    if len(data[data['proc']==p_2016]) == 0: continue
    y_2016 = data[data['proc']==p_2016].nominal_yield.values[0]
    y_2017 = data[data['proc']==p].nominal_yield.values[0]
    y_COWCorr_2017 = data[data['proc']==p].nominal_yield_COWCorr.values[0]

    # Loop over thw and extract the 2016 scaling factor
    for tw in tws:
      yvar_2016 = data[data['proc']==p_2016]['%s_yield'%tw].values[0]
      yvar_2017 = data[data['proc']==p]['%s_yield'%tw].values[0]
      sf_2016 = yvar_2016/y_2016 if y_2016 != 0. else 1.
      sf_2017 = yvar_2017/y_2017 if y_2017 != 0. else 1.

      # Correct yield
      ycorr_2017 = y_2017*sf_2016
      ycorr_COWCorr_2017 = y_COWCorr_2017*sf_2016

      data.at[ir,'%s_yield'%tw] = ycorr_2017
      data.at[ir,'%s_yield_COWCorr'%tw] = ycorr_COWCorr_2017

  # Then update 2018 ttH pdfWeight vals
  mask = (data['year']=='2018')&(data['type']=='sig')&(data['proc'].str.contains("ttH"))
  for ir,r in data[mask].iterrows():
    p = r['proc']
    #print " Proc: %s"%p
    p_2016 = re.sub("2018","2016",p)
    if len(data[data['proc']==p_2016]) == 0: continue
    y_2016 = data[data['proc']==p_2016].nominal_yield.values[0]
    y_2018 = data[data['proc']==p].nominal_yield.values[0]
    y_COWCorr_2018 = data[data['proc']==p].nominal_yield_COWCorr.values[0]

    # Loop over thw and extract the 2016 scaling factor
    for tw in tws:

      if "pdfWeight" not in tw: continue

      yvar_2016 = data[data['proc']==p_2016]['%s_yield'%tw].values[0]
      sf_2016 = yvar_2016/y_2016 if y_2016 != 0. else 1.

      # Correct yield
      ycorr_2018 = y_2018*sf_2016
      ycorr_COWCorr_2018 = y_COWCorr_2018*sf_2016

      data.at[ir,'%s_yield'%tw] = ycorr_2018
      data.at[ir,'%s_yield_COWCorr'%tw] = ycorr_COWCorr_2018

  # Update name of signal model
  #mask = (data['type']=='sig')
  #for ir,r in data[mask].iterrows():
  #  nmodel = "wsig_13TeV:hggpdfsmrel_%s_13TeV_%s_%s"%(r['year'],r['procOriginal'],r['cat'])
  #  data.at[ir,'model'] = nmodel

  of = re.sub("pass2_nominal","pass2_corrected_lite",yf)
  with open(of,"w") as fopkl: pickle.dump(data,fopkl)
