import ROOT
import argparse

import glob

parser=argparse.ArgumentParser()

parser.add_argument('--path')
parser.add_argument('--comparepath',default=None)
parser.add_argument('--checkall',action='store_true')
args=parser.parse_args()

if not args.checkall:
    proc = args.path.split('/')[-1].split('_M125')[0].replace('output_','')
    era = args.path.split('/')[-2]

    file=ROOT.TFile(args.path).Get('tagsDumper/cms_hgg_13TeV')

    all_datasets = [k.GetName() for k in file.allData()]

    wsum=0
    counter=0
    for i in all_datasets:
        
        Data=file.data(i)
        if Data and Data.ClassName() == "RooDataSet":
            for j in range(Data.numEntries()):
                entry=Data.get(j)
                w=Data.weight()
                wsum+=w
            counter+=1

    print(f'{proc} and {era}: '+str(wsum))

    print(str(counter)+'datasets used')

    if args.comparepath!=None:
        proc = args.comparepath.split('/')[-1].split('_M125')[0].replace('output_','')
        era = args.comparepath.split('/')[-2]

        file=ROOT.TFile(args.comparepath).Get('tagsDumper/cms_hgg_13TeV')

        all_datasets = [k.GetName() for k in file.allData()]

        wsum_ref=0
        counter_ref=0
        for i in all_datasets:
            
            Data=file.data(i)
            if Data and Data.ClassName() == "RooDataSet":
                for j in range(Data.numEntries()):
                    entry=Data.get(j)
                    w=Data.weight()
                    wsum_ref+=w
                counter_ref+=1
        print(f'comparison file: '+str(wsum_ref))
        print(f'input / ref = {wsum/wsum_ref}')


if args.checkall:
    globalsum=0
    gloabalsum_ref=0
    listf=glob.glob(args.path+'/*')
    for f in listf:
        proc=f.split('/')[-1].split('_M125')[0].replace('output_','')
        era = f.split('/')[-2]

        file=ROOT.TFile(f).Get('tagsDumper/cms_hgg_13TeV')

        all_datasets = [k.GetName() for k in file.allData()]
        
        wsum=0

        counter=0
        for i in all_datasets:
            
            Data=file.data(i)
            if Data and Data.ClassName() == "RooDataSet":
                for j in range(Data.numEntries()):
                    entry=Data.get(j)
                    w=Data.weight()
                    wsum+=w
                counter+=1
        globalsum+=wsum
        listf_ref=glob.glob(args.comparepath+'/*')
        for fref in listf_ref:
            if proc in fref:
                
                file=ROOT.TFile(fref).Get('tagsDumper/cms_hgg_13TeV')

                all_datasets = [k.GetName() for k in file.allData()]

                wsumref=0
                counterref=0
                for i in all_datasets:
                    
                    Data=file.data(i)
                    if Data and Data.ClassName() == "RooDataSet":
                        for j in range(Data.numEntries()):
                            entry=Data.get(j)
                            w=Data.weight()
                            wsumref+=w
                        counterref+=1
                print('f/fref='+str(wsum/wsumref)+'   '+proc)
                gloabalsum_ref+=wsumref
                continue
    # print(globalsum/gloabalsum_ref *(1+4/120))