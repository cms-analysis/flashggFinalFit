# Takes the ggbbres summary file and makes a nice table for the given mass points' central value

with open("../limits_for_AN.txt") as f:
#with open("summary_combine_results_ggbbres.txt") as f:
#with open("/home/users/evourlio/CMSSW_10_2_13/src/flashggFinalFit/Combine/limitSummaries_massDecorSRs_fullSetOfWeights_CatOptim0p05_defaultSys_DY_231219/summary_combine_results_ggbbres.txt") as f:
#with open("dummy.txt") as f:
    summary = f.read().splitlines()

my="90"

limits = {}
for line in summary:
    limit = line.split(" ")
    if limit[1] != "50.0%:":
        continue
    limit[0] = limit[0].replace("Combine/combine_results_ggbbres_","")
    limit[0] = limit[0].replace("mh{}.txt:Expected".format(my),"")
    if limit[0][0:2] == "mx":
        limits[limit[0]] = {}
    if "pdfIn" in limit[0]:
        continue
    elif "no_dy_bkg" in limit[0]:
        limit[0] = limit[0].replace("no_dy_bkg_","")
        limits[limit[0]]["No DY bkg"] = limit[4]
    elif "no_res_bkg" in limit[0]:
        limit[0] = limit[0].replace("no_res_bkg_","")
        limits[limit[0]]["No Res bkg"] = limit[4]
    elif "no_sys" in limit[0]:
        limit[0] = limit[0].replace("no_sys_","")
        limits[limit[0]]["No Systs"] = limit[4]
    else:
        limits[limit[0]]["Full"] = limit[4]

mx = [240, 280, 320, 360, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]

print("\centering")
print("\\begin{tabular}{c c c c}")
print("\tMass & DY Limit & No DY Limit & Hit (\%)\\\\")
for mass in mx:
    point = "mx{}my{}".format(str(mass),my)
    full = float(limits[point]["Full"])
    nody = float(limits[point]["No DY bkg"])
    ratio = (full-nody)/nody*100
    print("\t{} & {} & {} & {:.1f}\\\\".format(point,full,nody,ratio))

print("\end{tabular}")
