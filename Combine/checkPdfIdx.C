#include <TFile.h>
#include <TTree.h>

void print_first_entry(const char* filename, const char* treename) {
    // Open the ROOT file
    TFile *file = TFile::Open(filename);
    if (!file || file->IsZombie()) {
        std::cerr << "Error: Unable to open file " << filename << std::endl;
        return;
    }

    // Get the TTree
    TTree *tree = dynamic_cast<TTree*>(file->Get(treename));
    if (!tree) {
        std::cerr << "Error: Unable to retrieve tree " << treename << " from file" << std::endl;
        file->Close();
        return;
    }

    // Get the list of branches in the tree
    TObjArray *branches = tree->GetListOfBranches();

    // Loop over branches
    std::cout << "X"; // This is introduced only for the later step to split the output of this macro
    for (Int_t i = 0; i < branches->GetEntries(); ++i) {
        TBranch *branch = dynamic_cast<TBranch*>(branches->At(i));
        if (!branch) continue;

        // Get the branch name
        const char *branchName = branch->GetName();

        if (strncmp(branchName, "pdfindex", strlen("pdfindex")) != 0)
        continue;  // Skip branches that don't match the condition

        // Get the branch address
        void *branchAddress = nullptr;
        tree->SetBranchAddress(branchName, &branchAddress);

        // Load the first entry of the branch
        branch->GetEntry(0);

        // Get the leaf associated with the branch
       TLeaf *leaf = branch->GetLeaf(branchName);
       if (!leaf) continue;

       // Print the value
       std::cout << branchName << "=";
       if (leaf->GetNdata() > 0) {
         std::cout << leaf->GetValue(0) << ",";
       }
    }

    // Close the file
    file->Close();
}

void checkPdfIdx(const char* filename) {
  print_first_entry(filename, "limit");
}
