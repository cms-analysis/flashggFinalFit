theory_systematics = [
                 # 9 NP scheme
                 {'name':'THU_ggH_Mu','title':'THU_ggH_Mu','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_Res','title':'THU_ggH_Res','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_Mig01','title':'THU_ggH_Mig01','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_Mig12','title':'THU_ggH_Mig12','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_VBF2j','title':'THU_ggH_VBF2j','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_VBF3j','title':'THU_ggH_VBF3j','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_PT60','title':'THU_ggH_PT60','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_PT120','title':'THU_ggH_PT120','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_qmtop','title':'THU_ggH_qmtop','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                # Scale weights are grouped: [1,2], [3,6], [4,8]
                #{'name':'scaleWeight_0','title':'CMS_hgg_scaleWeight_0','type':'factory','prior':'lnN','correlateAcrossYears':1}, # nominal weight
                {'name':'scaleWeight_1','title':'CMS_hgg_scaleWeight_1','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
                {'name':'scaleWeight_2','title':'CMS_hgg_scaleWeight_2','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
                {'name':'scaleWeight_3','title':'CMS_hgg_scaleWeight_3','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
                {'name':'scaleWeight_4','title':'CMS_hgg_scaleWeight_4','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
                #{'name':'scaleWeight_5','title':'CMS_hgg_scaleWeight_5','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['norm','shape']}, #Unphysical
                {'name':'scaleWeight_6','title':'CMS_hgg_scaleWeight_6','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
                #{'name':'scaleWeight_7','title':'CMS_hgg_scaleWeight_7','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['norm','shape']}, #Unphysical
                {'name':'scaleWeight_8','title':'CMS_hgg_scaleWeight_8','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']}
              ]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# EXPERIMENTAL SYSTEMATICS
# correlateAcrossYears = 0 : no correlation
# correlateAcrossYears = 1 : fully correlated
# correlateAcrossYears = -1 : partially correlated

experimental_systematics = []

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Shape nuisances: effect encoded in signal model
signal_shape_systematics = []
