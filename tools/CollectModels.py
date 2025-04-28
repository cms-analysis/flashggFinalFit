# ******************************************************************************
# *                                                                            *
# * Title:      CollectModels.py                                               *
# * Author:     Benjamin Lawrence-Sanderson                                    *
# *             Northwestern University                                        *
# * Created:    2025-04-25                                                     *
# * Description:                                                               *
# *             Collects the output mgg and mbb workspaces and merges the      *
# *             two 1D models into a single 2D model using RooProdPdf.         *
# *                                                                            *
# ******************************************************************************

# from CollectModels import collect_models
# collect_models(
#     json_file="path/to/json/file.json",
#     output_file="output_file.root",
#     log_level="INFO"

import glob
import os
import sys
import json
import logging
import ROOT
import re

import commonObjects as co
import commonTools as ct

# Set up a basic logger at module level that will be configured properly later
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(handler)

def _group_models_by_category(models: dict) -> dict:
    grouped = {}    # { 
                    #   cat0: {modelA0: pathA0, modelB0: pathB0}, 
                    #   cat1: {modelC1: pathC1, modelD1: pathD1}, 
                    #   ... 
                    # }
    for model_name, model_path in models.items():
        # Extract category from model name
        cat = model_name.split("_")[-2] # Require cat name contains no underscores
        if cat not in grouped:
            grouped[cat] = {}
        grouped[cat][model_name] = model_path

    # Check the sub-dicts are all the same length
    lengths = [len(grouped[cat]) for cat in grouped]
    if len(set(lengths)) != 1:
        logger.warning("Not all categories have the same number of models.")

    return grouped

        

def _parse_json(json_file: str) -> dict:
    """Parse the JSON file to get the model names and paths."""
    # model_name: path/to/model.root
    # {
    #   "mgg_GGHH_2022+2023_cat0_13TeV": "path/to/CMS-HGG_sigfit_bbgg_2022+2023_GGHH_2022+2023_cat0.root",
    #   "mjj_GGHH_2022+2023_cat0_13TeV": "path/to/CMS-HBB_sigfit_bbgg_2022+2023_GGHH_2022+2023_cat0.root",
    # }
    # obs_proc_year_cat_sqrts
    
    if not os.path.exists(json_file):
        logger.error(f"JSON file {json_file} does not exist.")
        sys.exit(1)

    with open(json_file, "r", encoding="utf-8") as f:
        ungrouped_models = json.load(f)

    if len(ungrouped_models) == 0:
        logger.error(f"JSON file {json_file} is empty.")
        sys.exit(1)

    # TODO: Group by category AND YEAR (for separate year fits)
    models = _group_models_by_category(ungrouped_models) # depth-2 dict
    # { cat0: {modelA0: pathA0, modelB0: pathB0}, cat1: {modelC1: pathC1, modelD1: pathD1}, ... }

    return models


def _rooiter(x):
    iter = x.iterator()
    ret = iter.Next()
    while ret:
        yield ret
        ret = iter.Next()


def _name_to_cat(name: str) -> str:
    """Extract the category from the model name."""
    # e.g. mgg_GGHH_2022+2023_cat0_13TeV -> cat0
    return name.split("_")[-2]  # Require cat name contains no underscores


def _name_to_year(name: str) -> str:
    """Extract the year from the model name."""
    # e.g. mgg_GGHH_2022+2023_cat0_13TeV -> 2022+2023
    # n.b. We are indexing from the end since proc name may contain underscores,
    #   kappa samples for example
    return name.split("_")[-3]  # Require cat name contains no underscores


def _name_to_proc(name: str) -> str:
    """Extract the process from the model name."""
    # e.g. mgg_GGHH_2022+2023_cat0_13TeV -> GGHH
    # n.b. We are indexing from the end since proc name may contain underscores,
    #   kappa samples for example
    split_name = name.split("_")
    
    return "_".join(split_name[1:-3])


def _name_to_obs(name: str) -> str:
    """Extract the observable from the model name."""
    # e.g. mgg_GGHH_2022+2023_cat0_13TeV -> mgg
    # e.g. mjj_GGHH_2022+2023_cat0_13TeV -> mjj
    return name.split("_")[0]





def _get_PDF_name(
    ws_type: str,
    proc: str,
    obs: str,
    year: str,
    cat: str,
) -> str:
    """Get PDF name based on workspace type and process

    Args:
        ws_type (str): Type of workspace (signal, bkg-res, bkg-nonres)
        proc (str): Process name (i.e. ggh, vbf, tth, vh, gghh).
            For background non-resonant (data), use gghh.
        obs (str): Observable (mgg or mjj)
        year (str): Year

    Returns:
        str: PDF name
    """
    # General process:
    # 1) List all PDFs in workspace
    # 2) Loose match to that PDF name
    # 3) Return that PDF name
    # 4) If not found, throw error and exit

    if year not in co.years_to_process:
        logger.error("Year not listed in 'years to process' (see commonObjects.py): %s", year)
        sys.exit(1)
    if "," in cat:
        logger.error("_get_PDF_name requires single category, multiple given: %s", cat)
        sys.exit(1)
    if "," in year:
        logger.error("_get_PDF_name requires single year, multiple given: %s", year)
        sys.exit(1)
    if obs not in ["mgg", "mjj"]:
        logger.error("Unknown observable: %s", obs)
        sys.exit(1)

    proc_name = ct.dataToProc(proc)  # ggh -> GG2H

    pdf_name = ""
    # Signal
    if ws_type == "signal":
        if obs == "mgg":
            # e.g. hggpdfsmrel_GGHH_all2022_cat0_13TeV
            pdf_name = f"{co.outputMggWSObjectTitle__}_mgg_{proc_name}_{year}_{cat}_{co.sqrts__}"
        elif obs == "mjj":
            # e.g. hbbpdfsmrel_GGHH_all2022_cat0_13TeV
            pdf_name = f"{co.outputMbbWSObjectTitle__}_mjj_{proc_name}_{year}_{cat}_{co.sqrts__}"
        else:
            logger.error(f"Unknown observable: {obs}")
            sys.exit(1)

    elif ws_type == "bkg-res":
        if obs == "mgg":
            # e.g. hggpdfsmrel_mgg_TTH_all2022_cat0_13TeV
            pdf_name = f"{co.outputMggWSObjectTitle__}_mgg_{proc_name}_{year}_{cat}_{co.sqrts__}"
        elif obs == "mjj":
            # e.g. hbbpdfsmrel_mjj_TTH_all2022_cat0_13TeV
            pdf_name = f"{co.outputMbbWSObjectTitle__}_mjj_{proc_name}_{year}_{cat}_{co.sqrts__}"
        else:
            logger.error(f"Unknown observable: {obs}")
            sys.exit(1)

    elif ws_type == "bkg-nonres":
        if obs == "mgg":
            # e.g. CMS_hgg_cat1_13TeV_bkgshape
            pdf_name = f"CMS_hgg_{cat}_{co.sqrts__}_bkgshape"
        elif obs == "mjj":
            # e.g. hbbpdfsmrel_mjj_GGHH_all2022_cat1_13TeV
            # pdf_name = f"{co.outputMbbWSObjectTitle__}_mjj_{proc_name}_{year}_{cat}_{co.sqrts__}"
            # e.g. CMS_hbb_cat0_13TeV_bkgshape
            pdf_name = f"CMS_hbb_{cat}_{co.sqrts__}_bkgshape"
        else:
            logger.error(f"Unknown observable: {obs}")
            sys.exit(1)
    else:
        logger.error(f"Unknown workspace type: {ws_type}")
        sys.exit(1)

    return pdf_name


def _get_dataset_name(
    ws_type: str,
    obs: str,
    year: str,
    cat: str,
) -> str:
    """Get dataset name in nonresonant background workspace

    Args:
        obs (str): Observable (mgg or mjj)
        year (str): Year
        cat (str): Category

    Returns:
        str: Dataset name
    """
    if obs not in ["mgg", "mjj"]:
        logger.error("Unknown observable: %s", obs)
        sys.exit(1)
    if year not in co.years_to_process:
        logger.error("Year not listed in 'years to process' (see commonObjects.py): %s", year)
        sys.exit(1)
    if "," in cat:
        logger.error("_get_dataset_name requires single category, multiple given: %s", cat)
        sys.exit(1)
    if "," in year:
        logger.error("_get_dataset_name requires single year, multiple given: %s", year)
        sys.exit(1)

    dataset_name = ""
    if ws_type == "bkg-nonres":
        if obs == "mgg":
            # e.g. roohist_data_mass_cat1
            dataset_name = f"roohist_data_mass_{cat}"
        elif obs == "mjj":
            # e.g. roohist_data_mass_cat1
            dataset_name = f"roohist_data_mass_{cat}"
    elif ws_type == "signal":
        logger.warning("Signal workspace does not have relevant datasets")
    elif ws_type == "bkg-res":
        logger.warning("Background resonant workspace does not have relevant datasets")
    else:
        logger.error(f"Unknown workspace type: {ws_type}")
        sys.exit(1)

    return dataset_name


def _build_output_name(
    output_name: str, 
    proc: str,
    year: str,
    cat: str,
) -> str:
    """Build the output name for the combined model.

    Args:
        output_name (str): Output name template
        ws_type (str): Type of workspace (signal, bkg-res, bkg-nonres)
        proc (str): Process name (i.e. ggh, vbf, tth, vh, gghh).
            For background non-resonant (data), use gghh.
        year (str): Year
        cat (str): Category

    Returns:
        str: Output name
    """
    name = output_name.replace("%YEAR", year)
    name = name.replace("%PROC", proc)
    name = name.replace("%CAT", cat)
    return name


def _get_ws_name(
        obs: str,
        ws_type: str,
) -> str:
    """Get the workspace name based on the observable and workspace type.
    
    Args:
        obs (str): Observable (mgg or mjj)
        ws_type (str): Type of workspace (signal, bkg-res, bkg-nonres)

    Returns:
        str: Workspace name
    """
    if ws_type == "signal" and obs == "mgg":
        return f"{co.outputWSName__}_{co.sqrts__}"
    elif ws_type == "signal" and obs == "mjj":
        return f"{co.outputWSName__}_{co.sqrts__}"
    elif ws_type == "bkg-res" and obs == "mgg":
        return co.bkgWSName__
    elif ws_type == "bkg-res" and obs == "mjj":
        return co.bkgWSName__
    elif ws_type == "bkg-nonres" and obs == "mgg":
        return co.bkgWSName__
    elif ws_type == "bkg-nonres" and obs == "mjj":
        return co.bkgWSName__
    else:
        logger.error(f"Unknown workspace type: {ws_type}")
        sys.exit(1)


def _build_2d_pdf_name(
        ws_type: str,
        proc: str,
        year: str,
        cat: str,
) -> str:
    """Build the 2D PDF name for the combined model.

    Args:
        ws_type (str): Type of workspace (signal, bkg-res, bkg-nonres)
        proc (str): Process name (i.e. ggh, vbf, tth, vh, gghh).
            For background non-resonant (data), use gghh.
        year (str): Year
        cat (str): Category

    Returns:
        str: 2D PDF name
    """
    if ws_type == "bkg-nonres":
        return f"CMS-2D_{cat}_bkgshape"
    elif ws_type == "bkg-res":
        proc_name = ct.dataToProc(proc)
        return f"{co.output2DWSObjectTitle__}_2D_{proc_name}_{year}_{cat}_{co.sqrts__}"
    elif ws_type == "signal":
        proc_name = ct.dataToProc(proc)
        return f"{co.output2DWSObjectTitle__}_2D_{proc_name}_{year}_{cat}_{co.sqrts__}"
    else:
        logger.error(f"Unknown workspace type: {ws_type}")
        sys.exit(1)


def _build_prod_pdf(
        mgg_pdf: ROOT.RooAbsPdf,
        mjj_pdf: ROOT.RooAbsPdf,
        prod_pdf_name: str,
        ws_type: str,
        proc: str,
        cat: str,
) -> ROOT.RooProdPdf:
    # n.b. descriptions assume:
    #   - single signal proc
    #   - single nonres bkg proc
    #   - multiple res bkg procs
    if ws_type == "bkg-nonres":
        return ROOT.RooProdPdf(
            prod_pdf_name,
            f"2D nonresonant PDF for {cat}",
            ROOT.RooArgList(mgg_pdf, mjj_pdf),
        )
    elif ws_type == "bkg-res":
        return ROOT.RooProdPdf(
            prod_pdf_name,
            f"2D resonant PDF for {proc} {cat}",
            ROOT.RooArgList(mgg_pdf, mjj_pdf),
        )
    elif ws_type == "signal":
        return ROOT.RooProdPdf(
            prod_pdf_name,
            f"2D signal PDF for {cat}",
            ROOT.RooArgList(mgg_pdf, mjj_pdf),
        )
    else:
        logger.error(f"Unknown workspace type: {ws_type}")
        sys.exit(1)


def _clear_2d_ws_directory(ws_type: str) -> None:
    """Clear the 2D workspace directory in the datacard directory.
    
    Args:
        ws_type (str): Type of workspace (signal, bkg-res, bkg-nonres)
    """
    # Clear the outdir_2D directory in the datacard directory
    # e.g. /path/to/outdir_2D/bkg-res/
    outdir = co.dwd__ + "/outdir_2D/" + f"/{ws_type}/"
    if os.path.exists(outdir):
        os.system(f"rm -rf {outdir}")
        logger.debug(f"Cleared outdir_2D/{ws_type}/ directory")
    else:
        logger.debug("No outdir_2D directory to clear")


def _move_workspace(path: str, ws_type: str) -> str:
    """Move the workspace to outdir_2D in Datacard directory.
    Args:
        path (str): Path to the workspace
        ws_type (str): Type of workspace (signal, bkg-res, bkg-nonres)
        
    Returns:
        str: Path to the moved workspace
    """
    # Move the workspace to outdir_2D in Datacard directory
    # e.g. /path/to/workspace.root -> /path/to/outdir_2D/bkg-res/workspace.root
    outdir = co.dwd__ + "/outdir_2D" + f"/{ws_type}/" 
    if not os.path.exists(outdir):
        os.system(f"mkdir -p {outdir}")
    outdir = os.path.abspath(outdir)

    filename = os.path.basename(path)
    outpath = os.path.join(outdir, filename)
    if os.path.exists(outpath):
        logger.warning("Overwriting %s", outpath.split("/")[-1])
    
    os.system(f"mv {path} {outpath}")
    return outpath




def collect_models(
    json_file: str, 
    output_file: str, 
    mgg_var_name: str = "mass",
    mjj_var_name: str = "dijet_mass",
    log_level: str = "INFO",
    ws_type: str = None,
    no_clear: bool = False,
    **kwargs
) -> None:
    """Main function to collect models."""
    # Set up logging - reconfigure the global logger
    global logger
    
    import os
    import logManager
    from customLogger import CustomFormatter, FileFormatter
    
    LOG_FILE_NAME = "logfile.log"
    if not os.environ.get("LOGLEVEL", False):
        os.environ["LOGLEVEL"] = log_level.upper()
    
    logManager.manage(LOG_FILE_NAME, recreate=True)
    
    # Remove any existing handlers to avoid duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add new handlers with proper formatting
    file_handler = logging.FileHandler(LOG_FILE_NAME)
    file_handler.setLevel(logging.getLevelName(log_level.upper()))
    file_handler.setFormatter(FileFormatter())
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.getLevelName(log_level.upper()))
    console_handler.setFormatter(CustomFormatter())
    
    logger.setLevel(logging.getLevelName(log_level.upper()))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Continue with the existing implementation but use function parameters instead of args
    if ws_type not in ["signal", "bkg-res", "bkg-nonres", None]:
        logger.error("Unknown workspace type: %s. Allowed workspace types: signal, bkg-res, bkg-nonres.", ws_type)
        sys.exit(1)

    if not no_clear:
        _clear_2d_ws_directory(ws_type)

    models = _parse_json(json_file)
    
    # Loop over the models
    for cat, model_dict in models.items():
        obs_info = {}
        for model_name, model_path in model_dict.items():
            year = _name_to_year(model_name)
            proc = _name_to_proc(model_name)
            obs = _name_to_obs(model_name)

            # PDF name
            pdf_name = _get_PDF_name(
                ws_type=ws_type,
                proc=proc,
                obs=obs,
                year=year,
                cat=cat,
            )
            logger.debug("PDF name: %s", pdf_name)

            # Dataset name
            dataset_name = _get_dataset_name(
                ws_type=ws_type,
                obs=obs,
                year=year,
                cat=cat,
            )
            logger.debug("Dataset name: %s", dataset_name)

            obs_info[obs] = {
                "pdf_name": pdf_name,
                "dataset_name": dataset_name,
                "model_path": model_path,
                "year": year,
                "cat": cat,
                "proc": proc,
            }

        mgg_path = obs_info["mgg"]["model_path"]
        mjj_path = obs_info["mjj"]["model_path"]

        # Open files
        mgg_file = ROOT.TFile.Open(mgg_path)
        mjj_file = ROOT.TFile.Open(mjj_path)
        if not mgg_file or not mjj_file:
            logger.error("Could not open workspace files: %s, %s", mgg_path, mjj_path)
            mgg_file.Close()
            mjj_file.Close()
            sys.exit(1)
        
        # Get workspaces
        mgg_ws = mgg_file.Get(_get_ws_name(obs="mgg", ws_type=ws_type))
        mjj_ws = mjj_file.Get(_get_ws_name(obs="mjj", ws_type=ws_type))
        if not mgg_ws or not mjj_ws:
            logger.error(
                "Failed to get workspaces from input files (mgg: %s, mjj: %s)",
                mgg_path is True,
                mjj_path is True,
            )
            mgg_file.Close()
            mjj_file.Close()
            sys.exit(1)
        else:
            logger.debug("Loaded workspaces")

        # Create output workspace
        out_ws = ROOT.RooWorkspace("multipdf", "multipdf")

        # Get mgg and mjj variables
        mgg = mgg_ws.var(mgg_var_name)
        mjj = mjj_ws.var(mjj_var_name)
        if not mgg or not mjj:
            logger.error("Failed to get mass variables from workspaces")
            mgg_file.Close()
            mjj_file.Close()
            continue
        else:
            logger.debug("Got mass variables")

        # Get mgg and mjj PDFs
        mgg_pdf = mgg_ws.pdf(obs_info["mgg"]["pdf_name"])
        mjj_pdf = mjj_ws.pdf(obs_info["mjj"]["pdf_name"])
        if not mgg_pdf or not mjj_pdf:
            logger.error(
                "Failed to get PDFs or category indices for background nonresonant (Bad: %s)",
                ", ".join(
                    [
                        str(k)
                        for k, v in {
                            "mgg_pdf": mgg_pdf,
                            "mjj_pdf": mjj_pdf,
                        }.items()
                        if not bool(v)
                    ]
                ),
            )
            mgg_file.Close()
            mjj_file.Close()
            sys.exit(1)

        prod_pdf_name = _build_2d_pdf_name(
            ws_type=ws_type,
            proc=obs_info["mgg"]["proc"],
            year=obs_info["mgg"]["year"],
            cat=obs_info["mgg"]["cat"],
        )
        logger.debug("Output PDF name: %s", prod_pdf_name)

        # Create 2D PDF
        prod_pdf = _build_prod_pdf(
            mgg_pdf=mgg_pdf,
            mjj_pdf=mjj_pdf,
            prod_pdf_name=prod_pdf_name,
            ws_type=ws_type,
            proc=obs_info["mgg"]["proc"],
            cat=obs_info["mgg"]["cat"],
        )
        prod_pdf_norm = ROOT.RooRealVar(
            prod_pdf_name + "_norm",
            "2D pdf normalization based on mgg pdf norm",
            mgg_ws.obj(obs_info["mgg"]["pdf_name"] + "_norm").getVal(),
            0,
            3 * mgg_ws.obj(obs_info["mgg"]["pdf_name"] + "_norm").getVal(),
        )
        prod_pdf_norm.setConstant(True)

        out_ws.imp = getattr(out_ws, "import")

        allVars, allFunctions, allPdfs = {}, {}, {}
        for _var in _rooiter(mgg_ws.allVars()):
            allVars[_var.GetName()] = _var
        for _var in _rooiter(mjj_ws.allVars()):
            allVars[_var.GetName()] = _var
        for _func in _rooiter(mgg_ws.allFunctions()):
            allFunctions[_func.GetName()] = _func
        for _func in _rooiter(mjj_ws.allFunctions()):
            allFunctions[_func.GetName()] = _func
        for _pdf in _rooiter(mgg_ws.allPdfs()):
            allPdfs[_pdf.GetName()] = _pdf
        for _pdf in _rooiter(mjj_ws.allPdfs()):
            allPdfs[_pdf.GetName()] = _pdf
        allData_mgg = mgg_ws.allData()
        allData_mjj = mjj_ws.allData()

        # Import objects into output workspace
        logger.debug(f"({ws_type}) Importing variables...")
        for _varName, _var in allVars.items():
            logger.debug("  --> Importing %s", _varName)
            _var.setConstant(True)
            out_ws.imp(_var, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence())
        logger.debug(f"({ws_type}) Importing functions...")
        for _funcName, _func in allFunctions.items():
            logger.debug("  --> Importing %s", _funcName)
            out_ws.imp(_func, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence())
        logger.debug(f"({ws_type}) Importing PDFs...")
        for _pdfName, _pdf in allPdfs.items():
            logger.debug("  --> Importing %s", _pdfName)
            out_ws.imp(_pdf, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence())
        logger.debug(f"({ws_type}) Importing datasets...")
        for _data in allData_mgg:
            logger.debug("  --> Importing %s", _data.GetName())
            out_ws.imp(_data, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence())
        for _data in allData_mjj:
            logger.debug("  --> Importing %s", _data.GetName())
            out_ws.imp(_data, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence())
        out_ws.imp(prod_pdf, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence())
        out_ws.imp(prod_pdf_norm)

        # Output workspace name (full file path)
        full_output_name = _build_output_name(
            output_name=output_file,
            proc=proc,
            year=year,
            cat=cat,
        )
        logger.debug("Full output name: %s", full_output_name)
        out_file = ROOT.TFile.Open(full_output_name, "RECREATE")
        out_ws.Write()
        out_file.Close()

        # Close input files
        mgg_file.Close()
        mjj_file.Close()

        logger.info("Created 2D workspace: %s", full_output_name)

        # Move the workspace to outdir_2D in Datacard directory
        outpath = _move_workspace(
            path=full_output_name,
            ws_type=ws_type,
        )
        logger.info("Moved workspace to: %s", outpath)
    

def create_empty_json(path: str) -> None:
    """Create an empty JSON file at the given path

    Args:
        path (str): Path to the JSON file
    """

    if os.path.exists(path):
        logger.debug("JSON file already exists: %s", path)
        return

    with open(path, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4)
    logger.info("Created empty JSON file: %s", path)


def remove_obs_from_json(
    json_file: str,
    obs: str,
) -> None:
    """Remove the given observable from the JSON file

    Args:
        json_file (str): Path to the JSON file
        obs (str): Observable to remove (e.g. mgg, mjj)
    """
    if not os.path.exists(json_file):
        logger.error("JSON file does not exist: %s", json_file)
        return

    with open(json_file, "r", encoding="utf-8") as f:
        models = json.load(f)

    for cat in models:
        models[cat] = {k: v for k, v in models[cat].items() if obs not in k.split("_")[0]}

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(models, f, indent=4)


if __name__ == "__main__":
    # Only parse arguments when run as a script
    import argparse
    
    def _parse_args():
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description="Collect models from fit outputs")
        parser.add_argument(
            "--json",
            dest="json",
            help="Input json file listing model names and paths.",
        )
        parser.add_argument(
            "--output",
            dest="output",
            help="Output file name for the combined model.",
        )
        parser.add_argument(
            "--mggVarName",
            dest="mggVarName",
            default="mass",
            help="Variable name for mgg workspace (default: mass)",
        )
        parser.add_argument(
            "--mjjVarName",
            dest="mjjVarName",
            default="dijet_mass",
            help="Variable name for mjj workspace (default: dijet_mass)",
        )
        parser.add_argument(
            "--wsType",
            dest="ws_type",
            default=None,
            help="Workspace type (signal, bkg-res, bkg-nonres) (default: None)",
        )
        parser.add_argument(
            "--noClear",
            dest="noClear",
            default=False,
            action="store_true",
            help="Do not clear the outdir_2D directory before running",
        )
        parser.add_argument(
            "--logLevel",
            dest="logLevel",
            default="INFO",
            help="Log level (default: INFO) (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        )
        return parser.parse_args()
    
    args = _parse_args()
    
    collect_models(
        json_file=args.json,
        output_file=args.output,
        mgg_var_name=args.mggVarName,
        mjj_var_name=args.mjjVarName,
        ws_type=args.ws_type,
        no_clear=args.noClear,
        log_level=args.logLevel,
    )
