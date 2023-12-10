#!/usr/bin/python
import argparse
import os
import sys

from detect_mass_points import detect_mass_points


def get_mX(mass):
  return int(mass.split('x')[1].split('m')[0])


def get_mY(mass):
  return int(mass.split('y')[1])


def get_mH(config, mass):
  if args.config == 'Ybb':
    return 125
  if args.config == 'Ygg_low' or args.config == 'Ygg_high':
    return get_mY(mass)


def tree2ws(nonResYears, masses, nonResBkgTrees, procTemplate, mggl, mggh):
  print('Starting step 1: Make workspaces from pNN root files')
  print()

  for year in nonResYears:
    for m in masses:
      os.system('bash get_limit_hadd_tree2ws.sh'+' '+str(nonResBkgTrees)+' '+str(procTemplate)+' '+str(year)+' '+str(m)+' '+str(mggl)+' '+str(mggh))

  print('Finished step 1: Make workspaces from pNN root files')
  print()


def modelNonResBkg(doFailedFits, nonResYears, masses, nonResBkgTrees, procTemplate, config, nCats):
  print('Starting step 2: Model the non-resonant background')
  print()

  if not doFailedFits:
    for year in nonResYears:
      command = ''
      for m in masses:
        proc = procTemplate+m
        os.system('cp Background/config_'+procTemplate+'.py Background/config_'+procTemplate+'_batch_'+year+'_'+m+'.py')
        os.system('sed -i "s;<trees/year/m/ws/signal_year>;'+nonResBkgTrees+'/'+year+'/'+m+'/ws/data_'+year+';g" Background/config_'+procTemplate+'_batch_'+year+'_'+m+'.py')
        os.system('sed -i "s;<proc_template>_<signal_year>_<m>;'+procTemplate+'_'+year+'_'+m+';g" Background/config_'+procTemplate+'_batch_'+year+'_'+m+'.py')
        os.system('sed -i "s;<signal_year>_<m>;'+year+'_'+m+';g" Background/config_'+procTemplate+'_batch_'+year+'_'+m+'.py')
        os.system('sed -i "s;<signal_year>;'+year+';g" Background/config_'+procTemplate+'_batch_'+year+'_'+m+'.py')
        os.system('sed -i "s;<m>;'+m+';g" Background/config_'+procTemplate+'_batch_'+year+'_'+m+'.py')

        mh = get_mH(config, m)
        print(mh)
        low_bound=None; high_bound=None
        if mh < 83:
          low_bound = 68 # Low mass exception
        else:
          low_bound = mh-10*mh/125
        high_bound = mh+10*mh/125

        command = command+' sleep 0.5; python Background/RunBackgroundScripts_lite.py --inputConfig Background/config_'+procTemplate+'_batch_'+year+'_'+m+'.py --mode fTest --modeOpts "--blindingRegion '+str(low_bound)+','+str(high_bound)+' --gofCriteria 0.01" > /dev/null &'
    os.system(command+' wait')

  else:
    print('Looking for failed fits...')
    failed_jobs=">> Failed job list\n"

    # Check jobs successful
    for year in nonResYears:
      for m in masses:
        for i in range(int(nCats[m])):

          proc = procTemplate+m
          if not os.path.exists('Background/outdir_'+procTemplate+'_'+year+'_'+m+'/fTest/output/CMS-HGG_multipdf_'+proc+'cat'+str(i)+'.root') and not os.path.exists('Background/outdir_'+procTemplate+'_'+year+'_'+m+'/fTest/output/CMS-HGG_multipdf_'+proc+'cat'+str(i)+'_combined.root'):
            failed_jobs=failed_jobs+year+' '+m+' cat'+str(i)+' 0.01 -> 0.005 \n'
            print(year+' '+m+' cat'+str(i))
            os.system('sed -i "s/--gofCriteria 0.01/--gofCriteria 0.005/g" Background/outdir_'+procTemplate+'_'+year+'_'+m+'/fTest/jobs/sub_fTest_'+procTemplate+'_'+year+'_'+m+'_'+proc+'cat'+str(i)+'.sh')
            os.system('set +e; bash Background/outdir_'+procTemplate+'_'+year+'_'+m+'/fTest/jobs/sub_fTest_'+procTemplate+'_'+year+'_'+m+'_'+proc+'cat'+str(i)+'.sh >> rerunning_background.log 2>&1; set -e')

          proc = procTemplate+m
          if not os.path.exists('Background/outdir_'+procTemplate+'_'+year+'_'+m+'/fTest/output/CMS-HGG_multipdf_'+proc+'cat'+str(i)+'.root') and not os.path.exists('Background/outdir_'+procTemplate+'_'+year+'_'+m+'/fTest/output/CMS-HGG_multipdf_'+proc+'cat'+str(i)+'_combined.root'):
            failed_jobs=failed_jobs+year+' '+m+' cat'+str(i)+' 0.005 -> 0.001 \n'
            print(year+' '+m+' cat'+str(i))
            os.system('sed -i "s/--gofCriteria 0.005/--gofCriteria 0.001/g" Background/outdir_'+procTemplate+'_'+year+'_'+m+'/fTest/jobs/sub_fTest_'+procTemplate+'_'+year+'_'+m+'_'+proc+'cat'+str(i)+'.sh')
            os.system('set +e; bash Background/outdir_'+procTemplate+'_'+year+'_'+m+'/fTest/jobs/sub_fTest_'+procTemplate+'_'+year+'_'+m+'_'+proc+'cat'+str(i)+'.sh >> rerunning_background.log 2>&1; set -e')

          proc = procTemplate+m
          if not os.path.exists('Background/outdir_'+procTemplate+'_'+year+'_'+m+'/fTest/output/CMS-HGG_multipdf_'+proc+'cat'+str(i)+'.root') and not os.path.exists('Background/outdir_'+procTemplate+'_'+year+'_'+m+'/fTest/output/CMS-HGG_multipdf_'+proc+'cat'+str(i)+'_combined.root'):
            failed_jobs=failed_jobs+year+' '+m+' cat'+str(i)+' 0.001 -> 0.0 \n'
            print(year+' '+m+' cat'+str(i))
            os.system('sed -i "s/--gofCriteria 0.001/--gofCriteria 0.0/g" Background/outdir_'+procTemplate+'_'+year+'_'+m+'/fTest/jobs/sub_fTest_'+procTemplate+'_'+year+'_'+m+'_'+proc+'cat'+str(i)+'.sh')
            os.system('set +e; bash Background/outdir_'+procTemplate+'_'+year+'_'+m+'/fTest/jobs/sub_fTest_'+procTemplate+'_'+year+'_'+m+'_'+proc+'cat'+str(i)+'.sh >> rerunning_background.log 2>&1; set -e')

    print(failed_jobs)

    for year in nonResYears:
      os.system('for f in $(ls Background/outdir_'+procTemplate+'_'+year+'_*/fTest/output/*.root | grep "'+year+'.root" -v); do rename .root _'+year+'.root $f; done')

  print('Finished step 2: Model the non-resonant background')
  print()


def modelSignalAndResBkg(sigModels, resHBkgModels, mggl, mggh):
  print('Starting step 3: Get the models for signal and resonant background')
  print()

  os.system('python SignalModelInterpolation/create_signal_ws_new_cat_2d.py -i '+sigModels+' -o SignalModelInterpolation/outdir --mgg-range '+str(mggl)+' '+str(mggh))
  os.system('python SignalModelInterpolation/create_signal_ws_new_cat_2d_res_bkg.py -i '+resHBkgModels+' -o SignalModelInterpolation/res_bkg_outdir --mgg-range '+str(mggl)+' '+str(mggh))

  print('Finished step 3: Get the models for signal and resonant background')
  print()


def makeDatacards(masses, sigModels, resHBkgModels, resDYBkgModels, config, procTemplate, indir):
  print('Starting step 4: Make datacards')
  print()

  for m in masses:
    mH = str(get_mH(config, m))
    mX = str(get_mX(m))
    mY = str(get_mY(m))
    if resDYBkgModels is not None:
      os.system('bash get_limit_datacard.sh '+sigModels+' '+resHBkgModels+' '+m+' '+mH+' '+mX+' '+mY+' 1 '+procTemplate+' '+indir)
    else:
      os.system('bash get_limit_datacard.sh '+sigModels+' '+resHBkgModels+' '+m+' '+mH+' '+mX+' '+mY+' 0 '+procTemplate+' '+indir)

  print('Finished step 4: Make datacards')
  print()


def makeWorkspaces(resDYBkgModels, procTemplate, masses, config, mggl, mggh):
  print('Starting step 5: Make workspaces')
  print()

  os.system('mkdir -p Combine/Models; ' + \
            'mkdir -p Combine/Models/signal; ' + \
            'mkdir -p Combine/Models/res_bkg; '+ \
           ('mkdir -p Combine/Models/dy_bkg; ' if resDYBkgModels is not None else '') + \
            'mkdir -p Combine/Models/background; ' + \
            'cp SignalModelInterpolation/outdir/* Combine/Models/signal/.; ' + \
            'cp SignalModelInterpolation/res_bkg_outdir/* Combine/Models/res_bkg/.; ' + \
           ('cp SignalModelInterpolation/dy_bkg_outdir/* Combine/Models/dy_bkg/.; ' if resDYBkgModels is not None else '') + \
            'cp Background/outdir_'+procTemplate+'_*/fTest/output/CMS-HGG*.root Combine/Models/background/.; ' + \
            'cp Datacard/Datacard_'+procTemplate+'*.txt Combine/.; ' \
  )

  for m in masses:
    mH = str(get_mH(config, m))
    mX = str(get_mX(m))
    mY = str(get_mY(m))
    os.system('bash get_limit_workspace.sh '+str(mggl)+' '+str(mggh)+' '+mX+' '+mY+' '+mH+' '+procTemplate)

  print('Finished step 5: Make workspaces')
  print()


def getLimit(masses, config, mggl, mggh, procTemplate):
  print('Starting step 6: Get limit')
  print()

  for m in masses:
    mH = str(get_mH(config, m))
    mX = str(get_mX(m))
    mY = str(get_mY(m))
    os.system('bash get_limit_combine.sh '+str(mggl)+' '+str(mggh)+' '+mX+' '+mY+' '+mH+' '+procTemplate)

  os.system('grep "r <" Combine/combine_results_'+procTemplate+'_mx*.txt > Combine/summary_combine_results_'+procTemplate+'.txt')

  os.system('mkdir -p Outputs/CollectedPlots_'+procTemplate+'; ' + \
            'cp -r Background/plots Outputs/CollectedPlots_'+procTemplate+'/Background/; ' + \
            'mkdir -p Outputs/CollectedPlots_'+procTemplate+'/Combine; ' + \
            'mkdir -p Outputs/CollectedPlots_'+procTemplate+'/Combine/Datacard; ' + \
            'cp Combine/Datacard* Outputs/CollectedPlots_'+procTemplate+'/Combine/Datacard; ' + \
            'mkdir -p Outputs/CollectedPlots_'+procTemplate+'/Combine/Results; ' + \
            'cp Combine/*combine_results_'+procTemplate+'_* Outputs/CollectedPlots_'+procTemplate+'/Combine/Results; ' + \
            'cp -r Combine/Models Outputs/CollectedPlots_'+procTemplate+'/Combine/Models; ' + \
            'mkdir -p Outputs/CollectedPlots_'+procTemplate+'/Combine/Impacts; ' + \
            'cp Combine/impacts* Outputs/CollectedPlots_'+procTemplate+'/Combine/Impacts/; ' + \
            'mkdir -p Outputs/CollectedPlots_'+procTemplate+'/Combine/NLL_Scans; ' + \
            'cp Combine/NLL_Scan* Outputs/CollectedPlots_'+procTemplate+'/Combine/NLL_Scans; ' + \
            'mkdir -p Outputs/CollectedPlots_'+procTemplate+'/Background/DY; ' + \
            'cp Combine/'+procTemplate+'*cr*.png Outputs/CollectedPlots_'+procTemplate+'/Background/DY; ' \
  )

  print('Finished step 6: Get limit')
  print()


def main(args):
  print()
  print('Starting FlashGG Workflow')
  print('Running steps: '+args.steps)
  print('Running configuration: '+args.config)
  print()
  if args.doFailedFits and '2' not in args.steps:
    print('WARNING: The "doFailedFits" flag only works with step 2! It will do nothing for this run.')

  resYears = ['2016','2017','2018']
  nonResYears = ['combined']

  # Configuration based on final state - choices limited at the argument level
  mggl=None; mggh=None; plot_blinding_region=None; do_dy_bkg=None; lumiMap=None
  if args.config == 'Ybb':
    mggl=100
    mggh=180
    plot_blinding_region='115,135'
    lumiMap='lumiMap = {\'2016\':36.31, \'2017\':41.48, \'2018\':59.83, \'combined\':137.65, \'merged\':137.65}'
  if args.config == 'Ygg_low':
    mggl=65
    mggh=1000
    plot_blinding_region='68,135'
    do_dy_bkg=(args.resDYBkgModels is not None)
    lumiMap='lumiMap = {\'2016\':36.31, \'2017\':41.48, \'2018\':54.67, \'combined\':132.46, \'merged\':132.46}'
  if args.config == 'Ygg_high':
    mggl=100
    mggh=1000
    plot_blinding_region='115,900'
    lumiMap='lumiMap = {\'2016\':36.31, \'2017\':41.48, \'2018\':59.83, \'combined\':137.65, \'merged\':137.65}'

  os.system('sed -i "/lumiMap/s/.*/'+lumiMap+'/" tools/commonObjects.py')
  nCats={}; nCRs={}
  for year in nonResYears:
    treePerYearDir = args.nonResBkgTrees+'/'+year
    masses=[m for m in detect_mass_points(treePerYearDir) if args.masses in m]
    print('Year = '+year)
    print('Detected mass points,\tSRs,\tCRs:')
    for m in masses:
      nCats[m]=os.popen('ls '+treePerYearDir+'/Data*'+m+'cat* | wc -w').read()
      nCRs[m]=0 # FIXME: No CRs for now, when we have them, switch to: os.system('ls '+treePerYearDir+'/Data*'+m+'*cr_* | wc -w')
      print(m+'\t\t'+str(int(nCats[m])-int(nCRs[m]))+'\t'+str(nCRs[m]))
    print()
  print()

  if '1' in args.steps:
    tree2ws(nonResYears, masses, args.nonResBkgTrees, args.procTemplate, mggl, mggh)
  if '2' in args.steps:
    modelNonResBkg(args.doFailedFits, nonResYears, masses, args.nonResBkgTrees, args.procTemplate, args.config, nCats)
  if '3' in args.steps:
    modelSignalAndResBkg(args.sigModels, args.resHBkgModels, mggl, mggh)
  if '4' in args.steps:
    makeDatacards(masses, args.sigModels, args.resHBkgModels, args.resDYBkgModels, args.config, args.procTemplate, args.nonResBkgTrees)
  if '5' in args.steps:
    makeWorkspaces(args.resDYBkgModels, args.procTemplate, masses, args.config, mggl, mggh)
  if '6' in args.steps:
    getLimit(masses, args.config, mggl, mggh, args.procTemplate)


if __name__=="__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--nonResBkgTrees', '-inrb', type=str, required=True)
  parser.add_argument('--sigModels', '-is', type=str, required=True)
  parser.add_argument('--resHBkgModels', '-nhrb', type=str, required=True)
  parser.add_argument('--resDYBkgModels', '-idyrb', type=str, default=None)
  parser.add_argument('--masses', '-m', type=str, default='mx') # masses format mxXmyY so 'mx' as default means that all masses are run 
  parser.add_argument('--steps', '-s', type=str, default='123456')
  parser.add_argument('--config', '-c', type=str, choices=['Ybb','Ygg_low','Ygg_high'], default='Ygg_low')
  parser.add_argument('--procTemplate', '-p', type=str, default='ggbbres')
  parser.add_argument('--doFailedFits', action="store_true", default=False)
  args = parser.parse_args()

  main(args)
