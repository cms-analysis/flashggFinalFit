import uproot
from scipy.stats import chi2
from optparse import OptionParser


def get_options():
    parser = OptionParser()
    parser.add_option("--filename", dest="filename", default='', help="File to be considered.")
    parser.add_option("--nBins", dest="nBins", default=8, type='int', help="Number of generator-level bins.")
    return parser.parse_args()
(opt,args) = get_options()


def main():
    nll = uproot.open(opt.filename)["limit"].arrays()
    nll = nll['deltaNLL'][1]
    
    chi2pdf = chi2(opt.nBins)
    pval = 1 - (chi2pdf.cdf(2*nll))
    
    print(pval)


if __name__ == "__main__":
    main()