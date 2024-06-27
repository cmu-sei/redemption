
// <legal>
// 'Redemption' Automated Code Repair Tool
//
// Copyright 2023, 2024 Carnegie Mellon University.
//
// NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING
// INSTITUTE MATERIAL IS FURNISHED ON AN 'AS-IS' BASIS. CARNEGIE MELLON
// UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
// AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR
// PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF
// THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY
// KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT
// INFRINGEMENT.
//
// Licensed under a MIT (SEI)-style license, please see License.txt or
// contact permission@sei.cmu.edu for full terms.
//
// [DISTRIBUTION STATEMENT A] This material has been approved for public
// release and unlimited distribution.  Please see Copyright notice for
// non-US Government use and distribution.
//
// This Software includes and/or makes use of Third-Party Software each
// subject to its own license.
//
// DM23-2165
// </legal>

#include <map>
#include <utility>
#include <optional>

#include <llvm/Pass.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/LegacyPassManager.h>
#include <llvm/Transforms/IPO/PassManagerBuilder.h>

#include "llvm/IR/InstrTypes.h"
#include <llvm/IR/DerivedTypes.h>
#include <llvm/IR/Type.h>
#include <llvm/Support/raw_ostream.h>
#include <llvm/ADT/Hashing.h>
#include <llvm/Support/Debug.h>
#include "llvm/IR/Operator.h"
#include "llvm/IR/IntrinsicInst.h"
#include "llvm/IR/DebugLoc.h"
#include "llvm/IR/DebugInfoMetadata.h"

#include <llvm/IR/Dominators.h>
#include <llvm/Analysis/DominanceFrontier.h>

#include <stdlib.h>
#include <iostream>
#include <string>
#include <vector>
#include <sstream>

using namespace llvm;
using namespace std;


/*******************************************************************************
 *  To indicate that GivenPtrDeref is dominated by null-checks and other
 *  dereferences of the same pointer value, the following syntax is used:
 *
 *    [GivenPtrDeref, {
 *      "derefs": [OtherDeref_1, ..., OtherDeref_n],
 *      "null_checks": [check_1, ..., check_n],
 *    }]
 *
 *  where GivenPtrDeref is identified as [filename, [line, col]], and
 *  OtherDeref_i and check_i are identified as [line, col].
 *******************************************************************************/


class NullDomPass : public llvm::FunctionPass
{
public:
  static char ID;

  NullDomPass() : llvm::FunctionPass(ID) { }
  ~NullDomPass(){ }

  virtual void getAnalysisUsage(AnalysisUsage &AU) const override {
    AU.addRequired<DominatorTreeWrapperPass>();
    AU.setPreservesCFG();
  }

  bool doInitialization(llvm::Module &M) override {
    outs() << "[\n";
    return false;
  }

  bool doFinalization(llvm::Module &M) override {
    outs() << "]\n";
    return false;
  }

  std::optional<pair<Value*, BasicBlock*>> getNullCheck(BranchInst* BI) {
    // If BI is of the form "if (cond) {goto BT;} else {goto BF;}", and
    // cond is of the form "p != NULL", then return the pair (p, BT).
    // Also handle slight variations.

    if (!BI->isConditional()) {
      return {};
    }
    Value* cond = BI->getCondition();
    CmpInst* cmp = dyn_cast<CmpInst>(cond);
    if (!cmp) {
      return {};
    }

    // Check whether the comparison operator is equality ("==") or disequality ("!=").
    // If neither, then return empty-handed.
    bool is_neq;
    switch (cmp->getPredicate()) {
      case llvm::CmpInst::ICMP_EQ: is_neq = false; break;
      case llvm::CmpInst::ICMP_NE: is_neq = true; break;
      default:
        return {};
    }

    // Check that the pointer is being compared to NULL, and grab the pointer.
    // Handle both "p == NULL" and "NULL == p".
    Value* operands[] = {
      cmp->getOperand(0),
      cmp->getOperand(1)
    };
    Value* retPtr = nullptr;
    if (dyn_cast<ConstantPointerNull>(operands[0])) {
      retPtr = operands[1];
    }
    if (dyn_cast<ConstantPointerNull>(operands[1])) {
      retPtr = operands[0];
    }
    if (retPtr == nullptr) {
      return {};
    }

    // Get the basic block that is jumped to if the pointer is not NULL.
    BasicBlock* retBB = BI->getSuccessor(is_neq ? 0: 1);
    return {{retPtr,retBB}};
  }

  void write_line_col(Instruction* inst) {
    llvm::DebugLoc dl = inst->getDebugLoc();
    if (dl) {
      outs() << "[" << dl.getLine() << ", " << dl.getCol() << "]";
    } else {
      outs() << "[-1, -1]";
    }
  }

  void write_file_line_col(Instruction* inst) {
    llvm::DebugLoc dl = inst->getDebugLoc();
    if (dl) {
      // TODO: Escape any quotation marks in the filename.
      outs() << "[\"" << dl.get()->getDirectory() << '/'
             << dl.get()->getFilename() << "\", ";
      outs() << "[" << dl.getLine() << ", " << dl.getCol() << "]";
      outs() << "]";
    } else {
      outs() << "[\"???\", [-1, -1]]";
    }
  }

  Value* get_base_of_GEP(Value* p) {
    /* We are only concerned with null-pointer checks, 
       so we conflate {p, p->foo, p[2], etc.}. */
    if (auto* gep = dyn_cast<GetElementPtrInst>(p)) {
      return gep->getPointerOperand();
    } else {
      return p;
    }
  }

  bool
  runOnFunction(llvm::Function &F) override
  {
    outs() << "################## \n";
    outs() << "# Function: " << F.getName() << "\n";
    auto *DT = &getAnalysis<DominatorTreeWrapperPass>().getDomTree();
    std::map<Value*, vector<Instruction*>> ptrDerefs;
    std::map<Value*, vector<pair<Instruction*, BasicBlock*>>> null_checks;
    for(llvm::Function::iterator BB = F.begin(), E = F.end(); BB != E; ++BB) {
      for(llvm::BasicBlock::iterator BI = BB->begin(), BE = BB->end(); BI != BE; ++BI) {
        llvm::Instruction* I = &(*BI);
        Value* ptr = nullptr;
        if (LoadInst* LI = dyn_cast<LoadInst>(I)) {
          ptr = get_base_of_GEP(LI->getPointerOperand());
        } else if (StoreInst* SI = dyn_cast<StoreInst>(I)) {
          ptr = get_base_of_GEP(SI->getPointerOperand());
        }
        if (ptr) {
          llvm::DebugLoc dl = I->getDebugLoc();
          ptrDerefs[ptr].push_back(I);
          continue;
        }
        if (BranchInst* br = dyn_cast<BranchInst>(I)) {
          auto info = getNullCheck(br);
          if (info.has_value()) {
            Value* checkedPtr = info.value().first;
            BasicBlock* succ = info.value().second;
            null_checks[checkedPtr].push_back({br, succ});
          }
        }
      }
    }

    for (auto const& [curPtr, derefs] : ptrDerefs) {
      outs() << "################## \n";
      for (Instruction* curDeref : derefs) {
        vector<Instruction*> domByDerefs;
        vector<pair<Instruction*, BasicBlock*>> domByChecks;
        for (Instruction* otherDeref : derefs) {
          if (DT->dominates(dyn_cast<Value>(otherDeref), curDeref)) {
            domByDerefs.push_back(otherDeref);
          }
        }
        for (auto nullCheckPair : null_checks[curPtr]) {
          auto [br, target] = nullCheckPair;
          BasicBlockEdge edge = BasicBlockEdge(br->getParent(), target);
          if (DT->dominates(edge, curDeref->getParent())) {
            domByChecks.push_back(nullCheckPair);
          }
        }
        outs() << "[\n";
        outs() << "  "; write_file_line_col(curDeref); outs() << ", {\n";
        outs() << "    \"derefs\": [\n";
        for (Instruction* dominatingDeref : domByDerefs) {
          outs() << "      "; write_line_col(dominatingDeref); outs() << ",\n";
        }
        outs() << "    ],\n    \"null_checks\": [\n";
        for (auto const& [br, target]: domByChecks) {
          outs() << "      "; write_line_col(br); outs() <<",\n";
        }
        outs() << "    ]\n";
        outs() << "  }\n";
        outs() << "],\n";
      }
    }
    return false;
  }

};

char NullDomPass::ID = 0;

static llvm::RegisterPass<NullDomPass> X(
              "nulldom",
              "NullDom: Identify whether pointer dereferences are dominated by null checks",
              false, true
);


////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////


class AddNoReturnPass : public llvm::FunctionPass
{
public:
  static char ID;

  AddNoReturnPass() : llvm::FunctionPass(ID) { }
  ~AddNoReturnPass(){ }

  std::vector<std::string> splitString(const std::string &str, char delimiter) {
    std::vector<std::string> result;
    std::stringstream ss(str);
    std::string item;

    while (getline(ss, item, delimiter)) {
        result.push_back(item);
    }

    return result;
  }

  bool doInitialization(llvm::Module &M) override {
    char* no_ret_env = getenv("NORETURN_FUNCTIONS");
    if (!no_ret_env) {
      return false;
    }
    std::string no_ret_str = std::string(no_ret_env);
    // Remove all spaces
    no_ret_str.erase(std::remove(no_ret_str.begin(), no_ret_str.end(), ' '),
                     no_ret_str.end());
    // Split by commas
    vector<string> noret_names = splitString(no_ret_str, ',');
    // Add 'noreturn' attribute to each specified function
    for (int i=0; i < noret_names.size(); i++) {
      llvm::Function* func = M.getFunction(noret_names[i]);
      //errs() << noret_names[i] << ": " << func << "\n";
      if (func) {
        func->addFnAttr(Attribute::NoReturn);
      }
    }
    return false;
  }

  virtual void getAnalysisUsage(AnalysisUsage &AU) const override {
    AU.setPreservesCFG();
  }

  bool runOnFunction(llvm::Function &F) override
  {
    return false;
  }

};

char AddNoReturnPass::ID = 0;

static llvm::RegisterPass<AddNoReturnPass> Y(
              "add-no-return",
              "AddNoReturn",
              false, true
);

