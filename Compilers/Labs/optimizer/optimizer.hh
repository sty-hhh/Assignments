#pragma once
#ifndef __SYSU_OPTIMIZER_PLUGIN_HH_
#define __SYSU_OPTIMIZER_PLUGIN_HH_

#include <llvm/ADT/MapVector.h>
#include <llvm/IR/AbstractCallSite.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/PassManager.h>
#include <llvm/Pass.h>
#include <llvm/Passes/PassPlugin.h>
#include <llvm/Support/raw_ostream.h>

namespace sysu {

class StaticCallCounter : public llvm::AnalysisInfoMixin<StaticCallCounter> {
public:
  using Result = llvm::MapVector<const llvm::Function *, unsigned>;
  Result run(llvm::Module &M, llvm::ModuleAnalysisManager &);

private:
  // A special type used by analysis passes to provide an address that
  // identifies that particular analysis pass type.
  static llvm::AnalysisKey Key;
  friend struct llvm::AnalysisInfoMixin<StaticCallCounter>;
};

class StaticCallCounterPrinter
    : public llvm::PassInfoMixin<StaticCallCounterPrinter> {
public:
  explicit StaticCallCounterPrinter(llvm::raw_ostream &OutS) : OS(OutS) {}
  llvm::PreservedAnalyses run(llvm::Module &M,
                              llvm::ModuleAnalysisManager &MAM);

private:
  llvm::raw_ostream &OS;
};

// 预处理
class PreProcess : public llvm::PassInfoMixin<PreProcess> {
 public:
  llvm::PreservedAnalyses run(llvm::Module &M, llvm::ModuleAnalysisManager &);
};

// 通用子表达式删除
class CSE : public llvm::PassInfoMixin<CSE> {
 public:
  llvm::PreservedAnalyses run(llvm::Module &M, llvm::ModuleAnalysisManager &);
};

// 死代码消除
class DCE : public llvm::PassInfoMixin<DCE> {
 public:
  llvm::PreservedAnalyses run(llvm::Module &M, llvm::ModuleAnalysisManager &);
};

// 循环不变量
class LoopInvarient : public llvm::PassInfoMixin<LoopInvarient> {
 public:
  llvm::PreservedAnalyses run(llvm::Module &M, llvm::ModuleAnalysisManager &);
};

class delLS : public llvm::PassInfoMixin<delLS> {
 public:
  llvm::PreservedAnalyses run(llvm::Module &M, llvm::ModuleAnalysisManager &);
};

} // namespace sysu

extern "C" {
llvm::PassPluginLibraryInfo LLVM_ATTRIBUTE_WEAK llvmGetPassPluginInfo();
}

#endif