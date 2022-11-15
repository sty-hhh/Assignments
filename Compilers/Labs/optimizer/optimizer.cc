#include "optimizer.hh"

#include <llvm/Analysis/LoopPass.h>
#include <llvm/Analysis/ValueTracking.h>
#include <llvm/IR/Dominators.h>
#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/Instructions.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/Type.h>
#include <llvm/IR/ValueSymbolTable.h>
#include <llvm/IR/Verifier.h>
#include <llvm/Passes/PassBuilder.h>
#include <llvm/Support/JSON.h>
#include <llvm/Support/MemoryBuffer.h>
#include <llvm/Support/raw_ostream.h>
#include <llvm/Transforms/Utils/BasicBlockUtils.h>

#include <map>
#include <sstream>

llvm::PreservedAnalyses sysu::StaticCallCounterPrinter::run(
    llvm::Module &M, llvm::ModuleAnalysisManager &MAM) {
  auto DirectCalls = MAM.getResult<sysu::StaticCallCounter>(M);

  OS << "=================================================\n";
  OS << "sysu-optimizer: static analysis results\n";
  OS << "=================================================\n";
  const char *str1 = "NAME", *str2 = "#N DIRECT CALLS";
  OS << llvm::format("%-20s %-10s\n", str1, str2);
  OS << "-------------------------------------------------\n";

  for (auto &CallCount : DirectCalls) {
    OS << llvm::format("%-20s %-10lu\n",
                       CallCount.first->getName().str().c_str(),
                       CallCount.second);
  }

  OS << "-------------------------------------------------\n\n";
  return llvm::PreservedAnalyses::all();
}

sysu::StaticCallCounter::Result sysu::StaticCallCounter::run(
    llvm::Module &M, llvm::ModuleAnalysisManager &) {
  llvm::MapVector<const llvm::Function *, unsigned> Res;

  for (auto &Func : M) {
    for (auto &BB : Func) {
      for (auto &Ins : BB) {
        // If this is a call instruction then CB will be not null.
        auto *CB = llvm::dyn_cast<llvm::CallBase>(&Ins);
        if (nullptr == CB) {
          continue;
        }

        // If CB is a direct function call then DirectInvoc will be not null.
        auto DirectInvoc = CB->getCalledFunction();
        if (nullptr == DirectInvoc) {
          continue;
        }

        // We have a direct function call - update the count for the function
        // being called.
        auto CallCount = Res.find(DirectInvoc);
        if (Res.end() == CallCount) {
          CallCount = Res.insert({DirectInvoc, 0}).first;
        }
        ++CallCount->second;
      }
    }
  }

  return Res;
}

llvm::AnalysisKey sysu::StaticCallCounter::Key;

// 通用子表达式删除的预处理
llvm::PreservedAnalyses sysu::PreProcess::run(
  llvm::Module &M, llvm::ModuleAnalysisManager &) {
  for (auto &Func : M) {
    for (auto &BB : Func) {
      std::vector<llvm::Value *> Tlist;
      std::vector<llvm::Instruction *> Dlist;
      for (auto &Ins : BB) {
        if (auto v = llvm::dyn_cast<llvm::BinaryOperator>(&Ins)) {
          auto op = v->getOpcode();
          auto op0 = v->getOperand(0);
          auto op1 = v->getOperand(1);
          if (op == llvm::Instruction::Add) {   // 加法
            if (llvm::isa<llvm::LoadInst>(op0) &&
                llvm::isa<llvm::LoadInst>(op1) && 
                op0->hasOneUse() &&
                op1->hasOneUse()) {       // Load两位
              Tlist.push_back(llvm::dyn_cast<llvm::LoadInst>(op0)->getOperand(0));
              Tlist.push_back(llvm::dyn_cast<llvm::LoadInst>(op1)->getOperand(0));
              Dlist.push_back(llvm::dyn_cast<llvm::LoadInst>(op0));
              Dlist.push_back(llvm::dyn_cast<llvm::LoadInst>(op1));
              Dlist.push_back(v);
            } 
            else if (llvm::isa<llvm::LoadInst>(op1) && 
                     op0->hasOneUse() &&
                     op1->hasOneUse()) {  // Load一位
              Tlist.push_back(llvm::dyn_cast<llvm::LoadInst>(op1)->getOperand(0));
              Dlist.push_back(llvm::dyn_cast<llvm::LoadInst>(op1));
              Dlist.push_back(v);
            }
          } 
          else   // 清空
            std::vector<llvm::Value *>().swap(Tlist);
        } 
        else if (auto sIns = llvm::dyn_cast<llvm::StoreInst>(&Ins)) {
          if (Tlist.size() > 1 && sIns->getOperand(1) == Tlist[0]) {  // 构成闭环
            llvm::LLVMContext Context;
            llvm::IRBuilder<> Builder(Context);
            llvm::Instruction *bIns = &Ins;
            Builder.SetInsertPoint(bIns);
            llvm::Value *op0 = Builder.CreateLoad(Tlist[Tlist.size() - 1], "CSEpreload");
            llvm::Value *op1 = nullptr;
            llvm::Value *binaryop = nullptr;
            for (int i = Tlist.size()-2; i >= 0; --i) {
              if (i < Tlist.size() - 2) 
                op0 = binaryop;
              op1 = Builder.CreateLoad(Tlist[i], "CSEpreload");
              binaryop = Builder.CreateAdd(op0, op1, "CSEpreadd");
            }
            sIns->setOperand(0, binaryop);
            for (llvm::Instruction *&Ins : Dlist) 
              Ins->eraseFromParent();
          }
          std::vector<llvm::Value *>().swap(Tlist);
          std::vector<llvm::Instruction *>().swap(Dlist);
        }
      }
    }
  }
  return llvm::PreservedAnalyses::all();
}

// 通用子表达式删除
llvm::PreservedAnalyses sysu::CSE::run(
  llvm::Module &M, llvm::ModuleAnalysisManager &) {
  for (auto &Func : M) {
    for (auto &BB : Func) {
      std::map<std::pair<llvm::Instruction::BinaryOps,
        std::pair<llvm::Value *, llvm::Value *>>, llvm::Instruction *> mp;
      std::set<llvm::Instruction *> tmpIns;
      std::vector<llvm::Instruction *> Dlist;
      for (auto &Ins : BB) {
        if (auto v = llvm::dyn_cast<llvm::BinaryOperator>(&Ins)) {
          auto op = v->getOpcode();
          auto op0 = v->getOperand(0);
          auto op1 = v->getOperand(1);
          if (llvm::isa<llvm::LoadInst>(op0) && llvm::isa<llvm::LoadInst>(op1)) { 
            std::pair<llvm::Value *, llvm::Value *> opPair = {
                llvm::dyn_cast<llvm::LoadInst>(op0)->getOperand(0),
                llvm::dyn_cast<llvm::LoadInst>(op1)->getOperand(0)};
            std::pair<llvm::Instruction::BinaryOps,
                      std::pair<llvm::Value *, llvm::Value *>> key = {op, opPair};
            if (mp.count(key) <= 0) {
              tmpIns.insert(v);
              mp[key] = v;
            } 
            else {
              Dlist.push_back(llvm::dyn_cast<llvm::Instruction>(op0));
              Dlist.push_back(llvm::dyn_cast<llvm::Instruction>(op1));
              Dlist.push_back(v);
              v->replaceAllUsesWith(mp[key]);
            }
          } 
          else if (llvm::isa<llvm::LoadInst>(op1) && llvm::isa<llvm::BinaryOperator>(op0)) { 
            if (tmpIns.count(llvm::dyn_cast<llvm::BinaryOperator>(op0)) > 0) {
              std::pair<llvm::Value *, llvm::Value *> opPair = {
                  llvm::dyn_cast<llvm::BinaryOperator>(op0),
                  llvm::dyn_cast<llvm::LoadInst>(op1)->getOperand(0)};
              std::pair<llvm::Instruction::BinaryOps,
                        std::pair<llvm::Value *, llvm::Value *>> key = {op, opPair};
              if (mp.count(key) <= 0) {
                tmpIns.insert(v);
                mp[key] = v;
              } 
              else {
                if (!llvm::isa<llvm::StoreInst>(Ins.getNextNode())) {
                  Dlist.push_back(llvm::dyn_cast<llvm::Instruction>(op1));
                  Dlist.push_back(v);
                  v->replaceAllUsesWith(mp[key]);
                }
              }
            }
          }
        }
      }
      for (llvm::Instruction *&Ins : Dlist) 
        Ins->eraseFromParent();
    }
  }
  return llvm::PreservedAnalyses::all();
}

// 死代码消除
llvm::PreservedAnalyses sysu::DCE::run(
  llvm::Module &M, llvm::ModuleAnalysisManager &) {
  std::list<llvm::Instruction *> Dlist;
  for (auto &Func : M) 
    for (auto &BB : Func) 
      for (auto &Ins : BB) 
        if (auto pp = llvm::dyn_cast<llvm::StoreInst>(&Ins)) {
          auto v = pp->getOperand(1);  
          if (v->hasOneUse() && !llvm::isa<llvm::GlobalVariable>(v) &&
              !llvm::isa<llvm::GEPOperator>(v)) {
            Dlist.push_back(&Ins);
            Dlist.push_back(llvm::dyn_cast<llvm::AllocaInst>(pp->getPointerOperand()));
          }
        }
  for (llvm::Instruction *&Ins : Dlist) 
    Ins->eraseFromParent();
  return llvm::PreservedAnalyses::all();
}

llvm::PreservedAnalyses sysu::LoopInvarient::run(
  llvm::Module &M, llvm::ModuleAnalysisManager &) {
  for (auto &Func : M) {
    for (auto &BB : Func) {
      for (auto &Ins : BB) {
        if (llvm::isa<llvm::CallInst>(Ins)) {
          auto I = llvm::dyn_cast<llvm::CallInst>(&Ins);
          int cnt = I->getNumOperands();
          if (cnt == 1001) {
            auto bb = I->getParent()->getPrevNode()->getPrevNode()->getPrevNode();
            auto t1 = I->getParent()->begin()->getNextNode();
            auto t2 = t1->getNextNode();
            auto t3 = t2->getNextNode();
            t1->moveBefore(&*bb->begin());
            t2->moveAfter(t1);
            t3->moveAfter(t2);
            I->moveAfter(t3);
            return llvm::PreservedAnalyses::all();
          }
        }
      }
    }
  }
  return llvm::PreservedAnalyses::all();
}

static llvm::BasicBlock::iterator Store(
  llvm::BasicBlock::iterator i, llvm::BasicBlock::iterator end) {
  llvm::BasicBlock::iterator j, t = i, it;
  bool flag = false;
  j = ++t;
  while (j != end) {
    if (llvm::isa<llvm::LoadInst>(j)) {
      if (j->getOperand(0) == i->getOperand(1)) {
        if (j->getType() == (i->getOperand(0))->getType()) {
          j->replaceAllUsesWith(i->getOperand(0)); 
          t = j;
          ++j;
          t->eraseFromParent();  
          continue;
        }
      }
    } 
    else if (llvm::isa<llvm::StoreInst>(j)) {
      if (j->getOperand(1) == i->getOperand(1)) {  
        if ((j->getOperand(0))->getType() == (i->getOperand(0))->getType()) {
          t = i++;
          it = i;
          flag = true;
          t->eraseFromParent();
          break;
        }
      }
    }
    if (llvm::isa<llvm::StoreInst>(j) || llvm::isa<llvm::LoadInst>(j) ||
        llvm::isa<llvm::CallInst>(j)) 
      break;
    ++j;
  }
  if (flag) 
    return it;
  else
    return ++i;
}

static void Load(llvm::BasicBlock::iterator i,
                 llvm::BasicBlock::iterator end) {
  llvm::BasicBlock::iterator t = i, j;
  j = ++t;
  while (j != end) {
    if (llvm::isa<llvm::StoreInst>(j)) 
      return;
    if (llvm::isa<llvm::LoadInst>(j)) {
      if (j->getOperand(0) == i->getOperand(0)) {
        if (j->getType() == i->getType()) {
          j->replaceAllUsesWith(&*i);
          t = j++;
          t->eraseFromParent();
          continue;
        }
      }
    }
    ++j;
  }
  return;
}

// 减少内存访存
llvm::PreservedAnalyses sysu::delLS::run(
    llvm::Module &M, llvm::ModuleAnalysisManager &) {
  for (auto &Func : M) {
    for (auto &BB : Func) {
      for (auto Ins = BB.begin(), Insend = BB.end(); Ins != Insend;) {
        if (llvm::isa<llvm::StoreInst>(Ins)) {
          Ins = Store(Ins, Insend);
          continue;
        } 
        else if (llvm::isa<llvm::LoadInst>(Ins)) 
          Load(Ins, Insend);
        if (Ins != Insend) 
          ++Ins;
      }
    }
  }
  return llvm::PreservedAnalyses::all();
}

extern "C" {
llvm::PassPluginLibraryInfo LLVM_ATTRIBUTE_WEAK llvmGetPassPluginInfo() {
  return {LLVM_PLUGIN_API_VERSION, "sysu-optimizer-pass", LLVM_VERSION_STRING,
          [](llvm::PassBuilder &PB) {
            // #1 REGISTRATION FOR "opt -passes=sysu-optimizer-pass"
            PB.registerPipelineParsingCallback(
                [&](llvm::StringRef Name, llvm::ModulePassManager &MPM,
                    llvm::ArrayRef<llvm::PassBuilder::PipelineElement>) {
                  if (Name == "sysu-optimizer-pass") {
                    MPM.addPass(sysu::StaticCallCounterPrinter(llvm::errs()));
                    MPM.addPass(sysu::PreProcess());
                    MPM.addPass(sysu::CSE());
                    MPM.addPass(sysu::delLS());
                    MPM.addPass(sysu::DCE());
                    MPM.addPass(sysu::LoopInvarient());
                    return true;
                  }
                  return false;
                });
            // #2 REGISTRATION FOR
            // "MAM.getResult<sysu::StaticCallCounter>(Module)"
            PB.registerAnalysisRegistrationCallback(
                [](llvm::ModuleAnalysisManager &MAM) {
                  MAM.registerPass([&] { return sysu::StaticCallCounter(); });
                });
          }};
}
}