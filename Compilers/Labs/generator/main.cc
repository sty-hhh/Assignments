#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/Type.h>
#include <llvm/IR/ValueSymbolTable.h>
#include <llvm/IR/Verifier.h>
#include <llvm/Support/JSON.h>
#include <llvm/Support/MemoryBuffer.h>
#include <llvm/Support/raw_ostream.h>
#include <llvm/IR/DerivedTypes.h>
#include <map>
#include <vector>
#include <string>
#include <regex>
#include <algorithm>

namespace {
llvm::LLVMContext TheContext;
llvm::Module TheModule("-", TheContext);
std::vector<llvm::BasicBlock *> BreakStack, ContinueStack, IfThenStack, IfElseStack, WhileBodyStack, WhileEndStack, OtherLabelStack;
std::vector<int> IfOrWhile, Flag;
llvm::BasicBlock *CurBlock = nullptr;
enum StdType {BinaryOp, IfStmt, WhileStmt, ReturnStmt, BreakStmt, 
              DeclStmt, CallExpr, ContinueStmt, CompoundStmt, Default};
enum ShortCircuit {Left, Right};

// 函数声明
llvm::Value *getArray(const llvm::json::Object *O,llvm::IRBuilder<> *Builder, llvm::Function *f);
llvm::Value *BuildImplicitCastExpr(const llvm::json::Object *O, llvm::IRBuilder<> *Builder, llvm::Function *f);
llvm::Value *GetValue(const llvm::json::Object *O, llvm::IRBuilder<> *Builder, llvm::Function *f);
std::vector<int> Array2Vec(const std::string &TypeStr);
void InitArray(const llvm::json::Object *O, llvm::Value *BasePtr, std::vector<int> &dim, llvm::IRBuilder<> *Builder, int deep, std::string &name, llvm::Function *f);
void BuildIfStmt(const llvm::json::Object *O, llvm::IRBuilder<> *OutBuilder, llvm::Function *f);
bool BuildCompoundStmt(const llvm::json::Object *O, llvm::IRBuilder<> *Builder, llvm::Function *f);
int BuildInstruction(const llvm::json::Object *O, llvm::IRBuilder<> *Builder, llvm::Function *f);

// 符号表
class SymbolTable {
private:
  std::map<std::string, std::vector<std::pair<llvm::Value *, int>>> *TableList;
  int level;
public:
  SymbolTable() : level(-1),
                  TableList(new std::map<std::string, std::vector<std::pair<llvm::Value *, int>>>()) {}
  llvm::Value *lookup(std::string name) {
    if (this->TableList->find(name) != this->TableList->end())
      return (*(this->TableList))[name].back().first;
    else 
      return nullptr;
  }
  void ALevel() { 
    this->level++; 
  }
  void SLevel() {
    for (auto &it : (*(this->TableList))) {
      if (it.second.back().second == this->level) 
        it.second.pop_back();
      if (it.second.size() == 0) 
        it.second.clear();
    }
    --this->level;
  }
  int GetLevel() { 
    return level; 
  }
  void AddSymbol(std::string name, llvm::Value *value) {
    (*(this->TableList))[name].push_back({value, this->level});
  }
};

SymbolTable st;

llvm::Value *BuildBinaryOp(const llvm::json::Object *O,
                            llvm::IRBuilder<> *Builder, 
                            llvm::Function *f) {
  std::string kind = O->getString("kind")->str();
  if (kind != "BinaryOperator") {
    auto value = GetValue(O, Builder, f);
    if (value->getType()->isPointerTy()) 
      value = Builder->CreateLoad(value, "rval");
    return value;
  }
  auto innerArray = O->getArray("inner");
  std::string opcode = O->getString("opcode")->str();
  if (opcode == "&&" || opcode == "||") {  // 短路
    int tag;
    std::string blockname;
    if (opcode == "||") {
      blockname = "lor.lhs.false";
      tag = 0;
    } else {
      blockname = "land.lhs.true";
      tag = 1;
    }
    std::vector<llvm::BasicBlock *> Label(2, nullptr);
    int CType;
    if (!IfOrWhile.empty()) 
      CType = IfOrWhile.back();  
    if (CType == StdType::IfStmt) {
      Label[0] = IfThenStack.back();
      Label[1] = IfElseStack.back();
      if (!Flag.empty()) {
        if (Flag.back() == ShortCircuit::Left) 
          Label[(tag + 1) % 2] = OtherLabelStack.back();
        else 
          Label[1] = OtherLabelStack.back();
        OtherLabelStack.pop_back();
        Flag.pop_back();
      }
    } else if (CType == StdType::WhileStmt) {
      Label[0] = WhileBodyStack.back();
      Label[1] = WhileEndStack.back();
      blockname = "land.lhs.true";
      if (!Flag.empty()) {
        if (Flag.back() == ShortCircuit::Left) 
          Label[(tag + 1) % 2] = OtherLabelStack.back();
        else 
          Label[1] = OtherLabelStack.back();
        OtherLabelStack.pop_back();
        Flag.pop_back();
      }
    } 
    int k = 0;
    for (k = 0; k < 2; ++k) {
      if (!(*innerArray)[k].getAsObject()->get("opcode")) 
        break;
      else {
        std::string op = (*innerArray)[k].getAsObject()->getString("opcode")->str();
        if (op != "&&" && op != "||") 
            break;
      }
    }
    if (k == 0) {
      llvm::Value *expr = BuildBinaryOp((*innerArray)[0].getAsObject(), Builder, f);
      llvm::BasicBlock *block = llvm::BasicBlock::Create(TheContext, blockname, f);
      llvm::Value *cond = nullptr;
      if (expr->getType() == llvm::Type::getInt32Ty(TheContext)) 
        cond = Builder->CreateICmpNE(expr, Builder->getInt32(false), "booltmp");
      else 
        cond = Builder->CreateICmpNE(expr, Builder->getInt1(false), "booltmp");
      if (opcode == "&&") 
        Builder->CreateCondBr(cond, block, Label[1]);
      else 
        Builder->CreateCondBr(cond, Label[0], block);
      llvm::IRBuilder<> builder(block);
      auto nextOp = (*innerArray)[1].getAsObject()->get("opcode");
      if (nextOp == nullptr || nextOp->getAsString()->str() != "&&" && nextOp->getAsString()->str() != "||") {  // 终止条件
        llvm::Value *expr = BuildBinaryOp((*innerArray)[1].getAsObject(), &builder, f);
        llvm::Value *cond = nullptr;
        if (expr->getType() == llvm::Type::getInt32Ty(TheContext)) 
          cond = builder.CreateICmpNE(expr, builder.getInt32(false), "booltmp");
        else 
          cond = builder.CreateICmpNE(expr, builder.getInt1(false), "booltmp");
        builder.CreateCondBr(cond, Label[0], Label[1]);
      } 
      else 
        BuildBinaryOp((*innerArray)[1].getAsObject(), &builder, f);  // 递归
      return nullptr;
    } else if (k == 1) {  
      llvm::BasicBlock *block = llvm::BasicBlock::Create(TheContext, "bottom", f);
      llvm::IRBuilder<> BuilderBottom(block);
      llvm::Value *expr = BuildBinaryOp((*innerArray)[1].getAsObject(), &BuilderBottom, f);
      llvm::Value *cond = nullptr;
      if (expr->getType() == llvm::Type::getInt32Ty(TheContext)) 
        cond = BuilderBottom.CreateICmpNE(expr, BuilderBottom.getInt32(false), "booltmp");
      else 
        cond = BuilderBottom.CreateICmpNE(expr, BuilderBottom.getInt1(false), "booltmp");
      BuilderBottom.CreateCondBr(cond, Label[0], Label[1]);
      OtherLabelStack.push_back(block);
      if (opcode == "&&") 
        Flag.push_back(ShortCircuit::Left);
      else 
        Flag.push_back(ShortCircuit::Right);
      BuildBinaryOp((*innerArray)[0].getAsObject(), Builder, f);  // 递归
      return nullptr;
    }
    else if (k == 2) {  
      llvm::BasicBlock *block = llvm::BasicBlock::Create(TheContext, blockname, f);
      llvm::IRBuilder<> builder(block);
      BuildBinaryOp((*innerArray)[1].getAsObject(), &builder, f);
      OtherLabelStack.push_back(block);
      if (opcode == "&&") 
        Flag.push_back(ShortCircuit::Left);
      else 
        Flag.push_back(ShortCircuit::Right);
      BuildBinaryOp((*innerArray)[0].getAsObject(), Builder, f);  // 递归
      return nullptr;
    }
  }

  // 一般情况
  llvm::Value *lhs = BuildBinaryOp((*innerArray)[0].getAsObject(), Builder, f);
  llvm::Value *rhs = BuildBinaryOp((*innerArray)[1].getAsObject(), Builder, f);
  if (lhs == nullptr || rhs == nullptr) 
    return nullptr;
  if (opcode == "+") 
    return Builder->CreateAdd(lhs, rhs, "addtmp");
  else if (opcode == "-") 
    return Builder->CreateSub(lhs, rhs, "subtmp");
  else if (opcode == "*") 
    return Builder->CreateMul(lhs, rhs, "multmp");
  else if (opcode == "/") 
    return Builder->CreateSDiv(lhs, rhs, "multmp");
  else if (opcode == "%") 
    return Builder->CreateSRem(lhs, rhs, "remtmp");
  else if (opcode == "<") 
    return Builder->CreateICmpSLT(lhs, rhs, "lesstmp");
  else if (opcode == "<=") 
    return Builder->CreateICmpSLE(lhs, rhs, "lessequaltmp");
  else if (opcode == ">") 
    return Builder->CreateICmpSGT(lhs, rhs, "greatertmp");
  else if (opcode == ">=") 
    return Builder->CreateICmpSGE(lhs, rhs, "greaterequaltmp");
  else if (opcode == "!=") 
    return Builder->CreateICmpNE(lhs, rhs, "equalexlaimtmp");
  else if (opcode == "==") {
    if (lhs->getType() != rhs->getType()) 
      lhs = Builder->CreateIntCast(lhs, rhs->getType(), true, "cast");
    return Builder->CreateICmpEQ(lhs, rhs, "equalequaltmp");
  } 
  return nullptr;
}

llvm::Value *BuildCallExpr(const llvm::json::Object *O,
                           llvm::IRBuilder<> *Builder, 
                           llvm::Function *f) {
  auto innerArray = O->getArray("inner");
  std::string FName = (*innerArray)[0].getAsObject()->getArray("inner")->begin()->getAsObject()
                          ->getObject("referencedDecl")->getString("name")->str();
  auto Func = TheModule.getFunction(FName);
  std::vector<llvm::Value *> FuncArgArray;
  for (int i = 1; i < innerArray->size(); ++i) {
    auto value = GetValue((*innerArray)[i].getAsObject(), Builder, f);
    FuncArgArray.push_back(value);
  }
  return Builder->CreateCall(Func, FuncArgArray);
}

llvm::Value *GetValue(const llvm::json::Object *O, 
                    llvm::IRBuilder<> *Builder,
                    llvm::Function *f) {
  if (O == nullptr) 
    return nullptr;
  std::string kind = O->getString("kind")->str();
  if (kind == "IntegerLiteral") {
    std::string type = O->getObject("type")->getString("qualType")->str();
    if (type == "int") {
      int num = stoi(O->getString("value")->str());
      return Builder->getInt32(num);
    } else if (type == "long") {
      long num = stol(O->getString("value")->str());
      return Builder->getInt64(num);
    } else if (type == "unsigned int") {
      long num = stol(O->getString("value")->str());
      return Builder->getInt64(num);
    } else if (type == "long long") {
      long num = stol(O->getString("value")->str());
      return Builder->getInt64(num);
    } 
  } else if (kind == "StringLiteral") {
    std::string TypeStr = O->getObject("type")->getString("qualType")->str();
    std::vector<int> dim = Array2Vec(TypeStr);
    std::vector<llvm::Value *> IdList;
    IdList.push_back(Builder->getInt32(0));
    int num = 1;
    for (int i = 0; i < dim.size(); ++i) 
      num *= dim[i];
    std::string str1 = O->getString("value")->str();
    str1 = str1.substr(1, str1.length() - 2);
    std::string str2(num - 1, '\0');
    int j = 0;
    for (int i = 0; i < str1.length(); ++i) {
      if (str1[i] == '\\') {
        if (str1[i + 1] == '\\')
          str2[j++] = '\\';
        else if (str1[i + 1] == 'n')
          str2[j++] = '\n';
        else if (str1[i + 1] == '\"')
          str2[j++] = '\"';
        ++i;
      } 
      else 
        str2[j++] = str1[i];
    }
    llvm::Constant *ConstStr = llvm::ConstantDataArray::getString(TheContext, str2);
    llvm::GlobalVariable *Gval = new llvm::GlobalVariable(TheModule,
        llvm::ArrayType::get(llvm::Type::getInt8Ty(TheContext), num), false,
        llvm::GlobalValue::ExternalLinkage, 0, "conststr");
    Gval->setInitializer(ConstStr);
    Gval->setConstant(true);
    Gval->setAlignment(llvm::MaybeAlign(1));
    return Gval;
  } else if (kind == "UnaryOperator") {
    auto value = GetValue((*O->getArray("inner"))[0].getAsObject(), Builder, f);
    std::string opcode = O->getString("opcode")->str();
    if (opcode == "+") 
      return value;
    else if (opcode == "-") {
      auto ret = Builder->CreateNeg(value);
      ret->setName("neg");
      return ret;
    } 
    else if (opcode == "!") {
      if (value->getType() == llvm::Type::getInt32Ty(TheContext)) 
        value = Builder->CreateICmpNE(value, llvm::ConstantInt::get(TheContext, llvm::APInt(32, "0", 10)),"tobool");
      auto ret = Builder->CreateNot(value);
      ret->setName("not");
      return ret;
    } 
  } else if (kind == "DeclRefExpr") {
    std::string name = O->getObject("referencedDecl")->getString("name")->str();
    if (name.length() > 20) 
      name = name.substr(0, 20);
    llvm::Value *ptr = st.lookup(name);
    return ptr;
  } else if (kind == "BinaryOperator") 
    return BuildBinaryOp(O, Builder, f);
  else if (kind == "CallExpr") 
    return BuildCallExpr(O, Builder, f);
  else if (kind == "ArraySubscriptExpr") {
    auto ptr = getArray(O, Builder, f);
    return ptr;
  } else if (kind == "ImplicitCastExpr") {
    if (O->get("castKind")) 
      return BuildImplicitCastExpr(O, Builder, f);
  } 

  // 其他情况
  auto innerArray = O->getArray("inner");
  if (innerArray == nullptr) 
    return nullptr;
  return GetValue((*innerArray)[0].getAsObject(), Builder, f);
}

llvm::Value *getArray(const llvm::json::Object *O,
                      llvm::IRBuilder<> *Builder, 
                      llvm::Function *f) {
  const llvm::json::Object *cur = O;
  std::vector<llvm::Value *> IdList;
  std::string name;
  std::string TypeStr;

  while (1) {
    std::string kind = cur->getString("kind")->str();
    if (kind == "DeclRefExpr") {  
      name = cur->getObject("referencedDecl")->getString("name")->str();
      TypeStr = cur->getObject("type")->getString("qualType")->str();
      break;
    } else if (kind == "ArraySubscriptExpr") {
      auto innerPtr = cur->getArray("inner");
      auto Idx = GetValue((*innerPtr)[1].getAsObject(), Builder, f);
      if (Idx->getType()->isPointerTy()) 
        Idx = Builder->CreateLoad(Idx, "rval");
      IdList.push_back(Idx);
      cur = (*innerPtr)[0].getAsObject();
    } else { 
      auto innerPtr = cur->getArray("inner");
      cur = (*innerPtr)[0].getAsObject();
    }
  }
  std::reverse(IdList.begin(), IdList.end());
  if (name.length() > 20) 
    name = name.substr(0, 20);
  auto BasePtr = st.lookup(name);
  bool flag = false;
  if (!BasePtr->getType()->isArrayTy() && !BasePtr->getType()->getPointerElementType()->isArrayTy()) {
    BasePtr = Builder->CreateLoad(BasePtr, "deref");
    flag = true;
  }
  for (int i = 0; i < IdList.size(); ++i) {
    if (((IdList.size() > 1) && (i == IdList.size() - 1)) || !flag) {
      BasePtr = Builder->CreateInBoundsGEP(
          BasePtr,
          {llvm::ConstantInt::get(TheContext, llvm::APInt(32, 0)), IdList[i]},
          name);
    } 
    else 
      BasePtr = Builder->CreateInBoundsGEP(BasePtr, {IdList[i]}, name);
  }
  return BasePtr;
}

void setFuncArgs(llvm::Function *Func, 
                 std::vector<std::string> &FuncArgs,
                 llvm::IRBuilder<> *Builder) {
  int Idx = 0;
  llvm::Function::arg_iterator AB, AE;
  for (AB = Func->arg_begin(), AE = Func->arg_end(); AB != AE; ++AB, ++Idx) {
    AB->setName("arg_" + FuncArgs[Idx]);
    if (AB->getType()->isIntegerTy()) {
      llvm::Value *Lval = Builder->CreateAlloca(llvm::Type::getInt32Ty(TheContext), nullptr, FuncArgs[Idx]);
      st.AddSymbol(FuncArgs[Idx], Lval);
      Builder->CreateStore(AB, Lval);
    } else if (AB->getType()->isPointerTy()) {
      llvm::Value *Lval = Builder->CreateAlloca(AB->getType(), nullptr, FuncArgs[Idx]);
      st.AddSymbol(FuncArgs[Idx], Lval);
      Builder->CreateStore(AB, Lval);
    }
  }
}

void BuildIfStmt(const llvm::json::Object *O, 
                 llvm::IRBuilder<> *OutBuilder,
                 llvm::Function *f) {
  auto innerArrayPtr = O->getArray("inner");
  llvm::BasicBlock *if_then = llvm::BasicBlock::Create(TheContext, "if.then", f);
  llvm::BasicBlock *if_else = nullptr;
  llvm::BasicBlock *if_end = llvm::BasicBlock::Create(TheContext, "if.end", f);
  if (innerArrayPtr->size() >= 3) 
    if_else = llvm::BasicBlock::Create(TheContext, "if.else", f);
  
  IfOrWhile.push_back(StdType::IfStmt); 
  IfThenStack.push_back(if_then);            
  if (innerArrayPtr->size() >= 3) 
    IfElseStack.push_back(if_else);
  else
    IfElseStack.push_back(if_end);

  auto opcode = (*innerArrayPtr)[0].getAsObject()->get("opcode");
  if (opcode == nullptr || opcode->getAsString()->str() != "&&" && opcode->getAsString()->str() != "||") {
    llvm::Value *cmp = BuildBinaryOp((*innerArrayPtr)[0].getAsObject(), OutBuilder, f);
    llvm::Value *cond = nullptr;
    if (cmp->getType() == llvm::Type::getInt32Ty(TheContext)) 
      cond = OutBuilder->CreateICmpNE(cmp, OutBuilder->getInt32(false), "booltmp");
    else if (cmp->getType() == llvm::Type::getInt8Ty(TheContext)) 
      cond = OutBuilder->CreateICmpNE(cmp, OutBuilder->getInt8(false), "booltmp");
    else 
      cond = OutBuilder->CreateICmpNE(cmp, OutBuilder->getInt1(false), "booltmp");
    OutBuilder->CreateCondBr(cond, if_then, IfElseStack.back());
  } 
  else 
    BuildBinaryOp((*innerArrayPtr)[0].getAsObject(), OutBuilder, f);
  
  llvm::IRBuilder<> builder_then(if_then);
  st.ALevel();
  bool t1 = BuildCompoundStmt((*innerArrayPtr)[1].getAsObject(), &builder_then, f);
  if (!t1) 
    builder_then.CreateBr(if_end);
  st.SLevel();
  if (innerArrayPtr->size() >= 3) {
    llvm::IRBuilder<> builder_else(if_else);
    st.ALevel();
    bool t2 = BuildCompoundStmt((*innerArrayPtr)[2].getAsObject(), &builder_else, f);
    if (!t2) 
        builder_else.CreateBr(if_end);
    st.SLevel();
  }
  OutBuilder->SetInsertPoint(if_end);
  IfThenStack.pop_back();
  IfElseStack.pop_back();
  IfOrWhile.pop_back();
  return;
}

void BuildWhileStmt(const llvm::json::Object *O,
                    llvm::IRBuilder<> *OutBuilder, 
                    llvm::Function *f) {
  auto innerArrayPtr = O->getArray("inner");
  llvm::BasicBlock *while_cond = llvm::BasicBlock::Create(TheContext, "while.cond", f);
  llvm::BasicBlock *while_body = llvm::BasicBlock::Create(TheContext, "while.body", f);
  llvm::BasicBlock *while_end = llvm::BasicBlock::Create(TheContext, "while.end", f);

  WhileBodyStack.push_back(while_body);
  WhileEndStack.push_back(while_end);
  IfOrWhile.push_back(StdType::WhileStmt); 
  OutBuilder->CreateBr(while_cond);

  auto opcode = (*innerArrayPtr)[0].getAsObject()->get("opcode");
  llvm::IRBuilder<> builder_cond(while_cond);
  if (opcode == nullptr || opcode->getAsString()->str() != "&&" && opcode->getAsString()->str() != "||") {
    llvm::Value *cmp = BuildBinaryOp((*innerArrayPtr)[0].getAsObject(), &builder_cond, f);
    llvm::Value *cond = nullptr;
    if (cmp->getType() == llvm::Type::getInt32Ty(TheContext)) 
      cond = builder_cond.CreateICmpNE(cmp, OutBuilder->getInt32(false), "booltmp");
    else 
      cond = builder_cond.CreateICmpNE(cmp, OutBuilder->getInt1(false), "booltmp");
    builder_cond.CreateCondBr(cond, while_body, while_end);
  } 
  else
    BuildBinaryOp((*innerArrayPtr)[0].getAsObject(), &builder_cond, f);

  llvm::IRBuilder<> builder_body(while_body);
  BreakStack.push_back(while_end);
  ContinueStack.push_back(while_cond);
  st.ALevel();
  bool t = BuildCompoundStmt((*innerArrayPtr)[1].getAsObject(), &builder_body, f);
  if (!t) 
    builder_body.CreateBr(while_cond);
  st.SLevel();
  ContinueStack.pop_back();
  BreakStack.pop_back();

  OutBuilder->SetInsertPoint(while_end);
  WhileBodyStack.pop_back();
  WhileEndStack.pop_back();
  IfOrWhile.pop_back();
  return;
}

void BuildDoStmt(const llvm::json::Object *O, 
                 llvm::IRBuilder<> *OutBuilder,
                 llvm::Function *f) {
  auto innerArrayPtr = O->getArray("inner");
  llvm::BasicBlock *do_cond = llvm::BasicBlock::Create(TheContext, "do.cond", f);
  llvm::BasicBlock *do_body = llvm::BasicBlock::Create(TheContext, "do.body", f);
  llvm::BasicBlock *do_end = llvm::BasicBlock::Create(TheContext, "do.end", f);
  OutBuilder->CreateBr(do_body);

  llvm::IRBuilder<> builder_body(do_body);
  st.ALevel();
  bool t = BuildCompoundStmt((*innerArrayPtr)[0].getAsObject(), &builder_body, f);
  if (!t) 
    builder_body.CreateBr(do_cond);
  st.SLevel();
  auto opcode = (*innerArrayPtr)[1].getAsObject()->get("opcode");
  llvm::IRBuilder<> builder_cond(do_cond);
  if (opcode == nullptr || opcode->getAsString()->str() != "&&" && opcode->getAsString()->str() != "||") {
    llvm::Value *cmp = BuildBinaryOp((*innerArrayPtr)[1].getAsObject(), &builder_cond, f);
    llvm::Value *cond = nullptr;
    if (cmp->getType() == llvm::Type::getInt32Ty(TheContext)) 
      cond = builder_cond.CreateICmpNE(cmp, builder_cond.getInt32(false), "booltmp");
    else if (cmp->getType() == llvm::Type::getInt8Ty(TheContext)) 
      cond = builder_cond.CreateICmpNE(cmp, builder_cond.getInt8(false), "booltmp");
    else
      cond = builder_cond.CreateICmpNE(cmp, builder_cond.getInt1(false), "booltmp");
    builder_cond.CreateCondBr(cond, do_body, do_end);
  } 
  OutBuilder->SetInsertPoint(do_end);
  return;
}

bool BuildCompoundStmt(const llvm::json::Object *O, 
                       llvm::IRBuilder<> *Builder,
                       llvm::Function *f) {
  std::string kind = O->getString("kind")->str();
  if (kind != "CompoundStmt") {
    int type = BuildInstruction(O, Builder, f);
    if (type == StdType::ReturnStmt || type == StdType::BreakStmt || type == StdType::ContinueStmt) 
      return true;
    return false;
  }
  auto ptr = O->getArray("inner");
  if (ptr == nullptr) 
    return false;
  for (int i = 0; i < ptr->size(); ++i) {
    int type = BuildInstruction((*ptr)[i].getAsObject(), Builder, f);
    if (type == StdType::ReturnStmt || type == StdType::BreakStmt || type == StdType::ContinueStmt) 
      return true;
  }
  return false;
}

int BuildInstruction(const llvm::json::Object *O,
                     llvm::IRBuilder<> *Builder, 
                     llvm::Function *f) {
  std::string kind = O->getString("kind")->str();
  if (kind == "ReturnStmt") {  
    auto ptr = GetValue(O, Builder, f);
    if (ptr == nullptr) {  
      Builder->CreateBr(CurBlock);
      return StdType::ReturnStmt;
    }
    auto RetVal = st.lookup("retval");
    auto Type = ptr->getType();
    if (Type->getTypeID() == llvm::Type::IntegerTyID) {  
      Builder->CreateStore(ptr, RetVal);
      Builder->CreateBr(CurBlock);
      return StdType::ReturnStmt;
    }
    auto Rval = Builder->CreateLoad(llvm::Type::getInt32Ty(TheContext), ptr);
    Builder->CreateStore(Rval, RetVal);
    Builder->CreateBr(CurBlock);
    return StdType::ReturnStmt;
  } else if (kind == "BinaryOperator" && (O->getString("opcode")->str() == "=")) {  
    auto innerArray = O->getArray("inner");
    auto Rval = GetValue((*innerArray)[1].getAsObject(), Builder, f);
    if (Rval->getType()->isPointerTy()) 
      Rval = Builder->CreateLoad(Rval, "rval");
    auto Lval = GetValue((*innerArray)[0].getAsObject(), Builder, f);
    Builder->CreateStore(Rval, Lval);
    return StdType::BinaryOp;
  } else if (kind == "DeclStmt") {  
    auto TFunc = Builder->GetInsertBlock()->getParent();
    llvm::IRBuilder<> TmpBB(&TFunc->getEntryBlock(), TFunc->getEntryBlock().begin());
    auto innerArray = O->getArray("inner");
    for (int i = 0; i < innerArray->size(); ++i) {
      std::string name = (*innerArray)[i].getAsObject()->getString("name")->str();
      if (name.length() > 20) 
        name = name.substr(0, 20);
      std::string TypeStr = (*innerArray)[i].getAsObject()->getObject("type")->getString("qualType")->str();
      llvm::Value *Lval = nullptr;
      if (TypeStr == "int" || TypeStr == "const int" || TypeStr == "long") 
        Lval = TmpBB.CreateAlloca(llvm::Type::getInt32Ty(TheContext), nullptr, name);
      else if (std::regex_search(TypeStr.begin(), TypeStr.end(), std::regex("[[0-9]*]")) &&
                 TypeStr.find("char") == std::string::npos) {  // 整数数组
        std::vector<int> dim = Array2Vec(TypeStr);
        llvm::Type *AType = Builder->getInt32Ty();
        for (int i = 0; i < dim.size(); ++i) 
          AType = llvm::ArrayType::get(AType, dim[dim.size() - i - 1]);
        Lval = TmpBB.CreateAlloca(AType, nullptr, name);
      } else if (TypeStr == "long long") 
        Lval = TmpBB.CreateAlloca(llvm::Type::getInt64Ty(TheContext), nullptr, name);
      else if (std::regex_search(TypeStr.begin(), TypeStr.end(), std::regex("[[0-9]*]")) &&
                 TypeStr.find("char") != std::string::npos) {  // 字符数组
        std::vector<int> dim = Array2Vec(TypeStr);
        llvm::Type *AType = Builder->getInt8Ty();
        for (int i = 0; i < dim.size(); i++) 
          AType = llvm::ArrayType::get(AType, dim[dim.size() - i - 1]);
        Lval = TmpBB.CreateAlloca(AType, nullptr, name);
      } 
      st.AddSymbol(name, Lval);  
      if ((*innerArray)[i].getAsObject()->getArray("inner") == nullptr) 
        continue;
      llvm::Value *result = nullptr;
      auto innerArray2 = (*innerArray)[i].getAsObject()->getArray("inner");
      std::string kind = (*innerArray2)[0].getAsObject()->getString("kind")->str();

      if (kind == "BinaryOperator") 
        result = BuildBinaryOp((*innerArray2)[0].getAsObject(), Builder, f);
      else if (kind == "InitListExpr") {  // 局部数组
        std::vector<int> dim = Array2Vec(TypeStr);
        std::vector<llvm::Value *> IdList;
        IdList.push_back(Builder->getInt32(0));
        auto BasePtr = st.lookup(name);
        int num = 1;
        for (int i = 0; i < dim.size(); ++i) 
          num *= dim[i];
        Builder->CreateMemSet(
            BasePtr, llvm::ConstantInt::get(TheContext, llvm::APInt(8, 0)),
            llvm::ConstantInt::get(TheContext, llvm::APInt(32, num * 4)),
            llvm::MaybeAlign(4));
        InitArray((*innerArray2)[0].getAsObject(), 
                    Builder->CreateInBoundsGEP(BasePtr, IdList, name), 
                    dim, Builder, 0, name, f);
        continue;
      } else if (kind == "StringLiteral") {  // 字符串数组
        std::vector<int> dim = Array2Vec(TypeStr);
        std::vector<llvm::Value *> IdList;
        IdList.push_back(Builder->getInt32(0));
        auto BasePtr = st.lookup(name);
        int num = 1;
        for (int i = 0; i < dim.size(); ++i) 
          num *= dim[i];
        Builder->CreateMemSet(
            BasePtr, llvm::ConstantInt::get(TheContext, llvm::APInt(8, 0)),
            llvm::ConstantInt::get(TheContext, llvm::APInt(32, num)),
            llvm::MaybeAlign(1));  
        std::string str1 = (*innerArray2)[0].getAsObject()->getString("value")->str();
        str1 = str1.substr(1, str1.length() - 2);
        std::string str2(num - 1, '\0');
        int j = 0;
        for (int i = 0; i < str1.length(); ++i) {
          if (str1[i] == '\\') {
            if (str1[i + 1] == '\\')
              str2[j++] = '\\';
            else if (str1[i + 1] == 'n')
              str2[j++] = '\n';
            else if (str1[i + 1] == '\"')
              str2[j++] = '\"';
            ++i;
          } 
          else 
            str2[j++] = str1[i];
        }
        llvm::Constant *ConstStr = llvm::ConstantDataArray::getString(TheContext, str2);
        llvm::GlobalVariable *Gval = new llvm::GlobalVariable(
            TheModule, llvm::ArrayType::get(llvm::Type::getInt8Ty(TheContext), num),
            false, llvm::GlobalValue::ExternalLinkage, 0, "conststr");
        Gval->setInitializer(ConstStr);
        Gval->setConstant(true);
        Gval->setAlignment(llvm::MaybeAlign(1));
        Builder->CreateMemCpy(BasePtr, llvm::MaybeAlign(1), Gval, llvm::MaybeAlign(1), num);
        continue;
      } else {  
        result = GetValue((*innerArray2)[0].getAsObject(), Builder, f);
        if (result->getType()->isPointerTy()) 
          result = Builder->CreateLoad(llvm::Type::getInt32Ty(TheContext), result, "rval");
      }
      Builder->CreateStore(result, Lval);
    }
    return StdType::DeclStmt;
  } else if (kind == "IfStmt") {
    BuildIfStmt(O, Builder, f);
    return StdType::IfStmt;
  } else if (kind == "CallExpr") {
    BuildCallExpr(O, Builder, f);
    return StdType::CallExpr;
  } else if (kind == "WhileStmt") {
    BuildWhileStmt(O, Builder, f);
    return StdType::WhileStmt;
  } else if (kind == "BreakStmt") {
    Builder->CreateBr(BreakStack.back());
    return StdType::BreakStmt;
  } else if (kind == "ContinueStmt") {
    Builder->CreateBr(ContinueStack.back());
    return StdType::ContinueStmt;
  } else if (kind == "CompoundStmt") {
    st.ALevel();
    BuildCompoundStmt(O, Builder, f);
    st.SLevel();
    return StdType::CompoundStmt;
  } else if (kind == "DoStmt") {
    BuildDoStmt(O, Builder, f);
  }
  return StdType::Default;
}

llvm::Function *BuildFunctionDecl(const llvm::json::Object *O) {
  if (O->get("storageClass") != nullptr) 
    return nullptr;
  std::string name = O->getString("name")->str();
  llvm::Function *TFunc = TheModule.getFunction(name);
  std::string TypeStr = O->getObject("type")->getString("qualType")->str();
  TypeStr = TypeStr.substr(0, TypeStr.find_first_of('(') - 1);
  llvm::Type *RetType = nullptr;
  if (TypeStr == "int") 
    RetType = llvm::Type::getInt32Ty(TheContext);
  else if (TypeStr == "void") 
    RetType = llvm::Type::getVoidTy(TheContext);
  else if (TypeStr == "long") 
    RetType = llvm::Type::getInt32Ty(TheContext);
  else if (TypeStr == "long long") 
    RetType = llvm::Type::getInt64Ty(TheContext);

  auto innerArray = O->getArray("inner");
  if (innerArray == nullptr) {
    TFunc = llvm::Function::Create(
        llvm::FunctionType::get(RetType, {}, false),
        llvm::Function::ExternalLinkage, name, &TheModule);
    return TFunc;
  }
  int k = 0;
  std::vector<llvm::Type *> FuncArgs;
  std::vector<std::string> FuncArgsNames;
  while (k < (*innerArray).size()) {
    std::string kind = (*innerArray)[k].getAsObject()->getString("kind")->str();
    if (kind != "ParmVarDecl") 
      break;
    std::string name = (*innerArray)[k].getAsObject()->getString("name")->str();
    FuncArgsNames.push_back(name);
    std::string type = (*innerArray)[k].getAsObject()->getObject("type")->getString("qualType")->str();
    if (type == "int") 
      FuncArgs.push_back(llvm::Type::getInt32Ty(TheContext));
    else if (type == "int *") 
      FuncArgs.push_back(llvm::Type::getInt32PtrTy(TheContext));
    else if (type.find("(*)") != std::string::npos) {  
      std::vector<int> dim = Array2Vec(type);
      llvm::Type *AType = llvm::Type::getInt32Ty(TheContext);
      for (int i = dim.size() - 1; i >= 0; --i) 
        AType = llvm::ArrayType::get(AType, dim[i]);
      FuncArgs.push_back(llvm::PointerType::get(AType, 0));
    } 
    else if (type == "const char *") 
      FuncArgs.push_back(llvm::Type::getInt8PtrTy(TheContext));
    ++k;
  }
  if (!TFunc)
    TFunc = llvm::Function::Create(
        llvm::FunctionType::get(RetType, FuncArgs, false),
        llvm::Function::ExternalLinkage, name, &TheModule);
  if (!TFunc) 
    return nullptr;
  if (k >= (*innerArray).size()) 
    return TFunc;
  auto BB = llvm::BasicBlock::Create(TheContext, "entry", TFunc);
  llvm::IRBuilder<> Builder(BB);

  st.ALevel(); 
  setFuncArgs(TFunc, FuncArgsNames, &Builder); 
  llvm::Value *RetVal = nullptr;
  if (TypeStr == "int") {
    RetVal = Builder.CreateAlloca(llvm::Type::getInt32Ty(TheContext), nullptr, "retval");
    Builder.CreateStore(Builder.getInt32(0), RetVal);
  } else if (TypeStr == "long") {
    RetVal = Builder.CreateAlloca(llvm::Type::getInt32Ty(TheContext), nullptr, "retval");
    Builder.CreateStore(Builder.getInt32(0), RetVal);
  } else if (TypeStr == "long long") {
    RetVal = Builder.CreateAlloca(llvm::Type::getInt64Ty(TheContext), nullptr, "retval");
    Builder.CreateStore(Builder.getInt64(0), RetVal);
  }
  if (TypeStr != "void") 
    st.AddSymbol("retval", RetVal);
  auto ReturnBlock = llvm::BasicBlock::Create(TheContext, "return", TFunc);
  CurBlock = ReturnBlock;
  bool t = BuildCompoundStmt((*innerArray)[k].getAsObject(), &Builder, TFunc);
  if (!t) 
    Builder.CreateBr(ReturnBlock); 
  Builder.SetInsertPoint(ReturnBlock);
  if (TypeStr == "int" || TypeStr == "long" || TypeStr == "long long") {
    auto Rval = Builder.CreateLoad(RetVal, "constretval");
    Builder.CreateRet(Rval);
  } else if (TypeStr == "void") 
    Builder.CreateRetVoid();
  st.SLevel(); 
  llvm::verifyFunction(*TFunc);
  return TFunc;
  TFunc->eraseFromParent();
  return nullptr;
}

llvm::Constant *GetConstInitList(const llvm::json::Object *O,
                                 std::vector<int> &dim,
                                 llvm::IRBuilder<> *Builder, 
                                 int depth,
                                 llvm::Function *f) {
  if (depth > dim.size()) 
    return nullptr;
  if (depth == dim.size()) {  
    auto ptr = GetValue(O, Builder, f);
    if (ptr == nullptr) 
      ptr = Builder->getInt32(0);
    else if (ptr->getType()->isPointerTy()) 
      ptr = Builder->CreateLoad(ptr, "rval");
    return llvm::dyn_cast<llvm::Constant>(ptr);
  }
  std::vector<llvm::Constant *> elems;
  bool array_filler = false;
  const llvm::json::Array *innerArrayPtr = nullptr;
  if (O != nullptr) {
    innerArrayPtr = O->getArray("inner");
    if (innerArrayPtr == nullptr) {
      innerArrayPtr = O->getArray("array_filler");
      array_filler = true;
    }
  }
  llvm::Type *SubAType = Builder->getInt32Ty();
  for (int i = dim.size() - 1; i > depth; --i) 
    SubAType = llvm::ArrayType::get(SubAType, dim[i]);
  int j = 0;
  if (array_filler) 
    ++j;
  for (int i = 0; i < dim[depth]; ++i) {
    llvm::Constant *subarray = nullptr;
    if (innerArrayPtr != nullptr && j < innerArrayPtr->size()) 
      subarray = GetConstInitList((*innerArrayPtr)[j].getAsObject(), dim, Builder, depth + 1, f);
    else {
      if (depth == dim.size() - 1)  // 一维数组的情况
        subarray = Builder->getInt32(0);
      else
        subarray = llvm::ConstantArray::get(llvm::dyn_cast<llvm::ArrayType>(SubAType), {}); 
    }
    elems.push_back(subarray);
    ++j;
  }
  llvm::Type *AType = Builder->getInt32Ty();
  for (int i = dim.size() - 1; i >= depth; --i) 
    AType = llvm::ArrayType::get(AType, dim[i]);
  llvm::Constant *const_array = llvm::ConstantArray::get(
      llvm::dyn_cast<llvm::ArrayType>(AType), elems);  //数组常量
  return const_array;
}

void InitArray(const llvm::json::Object *O, 
                llvm::Value *BasePtr,
                std::vector<int> &dim, 
                llvm::IRBuilder<> *Builder, 
                int depth,
                std::string &array_name, 
                llvm::Function *f) {
  if (depth > dim.size()) 
    return;
  if (depth == dim.size()) {  
    auto Rval = GetValue(O, Builder, f);
    if (Rval == nullptr) 
      Rval = Builder->getInt32(0);
    else if (Rval->getType()->isPointerTy()) 
      Rval = Builder->CreateLoad(llvm::Type::getInt32Ty(TheContext), Rval, "getint");
    Builder->CreateStore(Rval, BasePtr);
  }
  std::vector<llvm::Value *> IdList;
  IdList.push_back(Builder->getInt32(0));
  if (array_name.length() > 20) 
    array_name = array_name.substr(0, 20);
  bool array_filler = false;
  const llvm::json::Array *innerArrayPtr = nullptr;
  if (O != nullptr) {
    innerArrayPtr = O->getArray("inner");
    if (innerArrayPtr == nullptr) {
      innerArrayPtr = O->getArray("array_filler");
      array_filler = true;
    }
  }
  int j = 0;
  if (array_filler) 
    ++j;
  for (int i = 0; i < dim[depth]; ++i) {
    IdList.push_back(Builder->getInt32(i));
    llvm::Value *NextPtr = Builder->CreateInBoundsGEP(BasePtr, IdList, array_name);
    if (innerArrayPtr != nullptr && j < innerArrayPtr->size()) 
      InitArray((*innerArrayPtr)[j].getAsObject(), NextPtr, dim, Builder, depth + 1, array_name, f);
    else 
      return;
    IdList.pop_back();
    ++j;
  }
}

std::vector<int> Array2Vec(const std::string &TypeStr) {
  std::vector<int> dim;
  for (int i = 0; i < TypeStr.size(); ++i) {
    if (TypeStr[i] == '[') {
      int num = 0;
      int j = i + 1;
      while (TypeStr[j] != ']') {
        num = 10 * num + TypeStr[j] - '0';
        ++j;
      }
      dim.push_back(num);
      i = j;
    }
  }
  return dim;
}

llvm::Value *BuildImplicitCastExpr(const llvm::json::Object *O,
                                   llvm::IRBuilder<> *Builder,
                                   llvm::Function *f) {
  auto value = GetValue((*O->getArray("inner"))[0].getAsObject(), Builder, f);
  std::string castKind = O->getString("castKind")->str();
  std::string castType = O->getObject("type")->getString("qualType")->str();
  if (castKind == "ArrayToPointerDecay") {
    std::string type = O->getObject("type")->getString("qualType")->str();
    if (type.find("int") != std::string::npos) {
      auto ptr = Builder->CreateInBoundsGEP(
          value, {llvm::ConstantInt::get(TheContext, llvm::APInt(32, 0)),
                  llvm::ConstantInt::get(TheContext, llvm::APInt(32, 0))});
      ptr->setName("Arr2Ptr");
      return ptr;
    } else if (type == "char *") {
      auto ptr = Builder->CreateInBoundsGEP(
          value, {llvm::ConstantInt::get(TheContext, llvm::APInt(32, 0)),
                  llvm::ConstantInt::get(TheContext, llvm::APInt(32, 0))});
      ptr->setName("Arr2Ptr");
      return ptr;
    } 
  } else if (castKind == "IntegralCast") { 
    if (castType == "int") {
      if (value->getType()->isPointerTy()) 
        value = Builder->CreateLoad(value, "rval");
      value = Builder->CreateIntCast(value, llvm::Type::getInt32Ty(TheContext), true, "IntegralCast");
    } else if (castType == "long") 
      value = Builder->CreateIntCast(value, llvm::Type::getInt32Ty(TheContext), true, "IntegralCast");
    else if (castType == "long long") 
      value = Builder->CreateIntCast(value, llvm::Type::getInt64Ty(TheContext), true, "IntegralCast");
    else if (castType == "unsigned int") 
      value = Builder->CreateIntCast(value, llvm::Type::getInt64Ty(TheContext), true, "IntegralCast");
    return value;
  } else if (castKind == "LValueToRValue") 
    return Builder->CreateLoad(value, "lval2rval");
  else 
    return value;
  return nullptr;
}

llvm::GlobalVariable *BuildGlobalVarDecl(const llvm::json::Object *O) {
  auto name = O->getString("name")->str();
  auto TypeStr = O->getObject("type")->getString("qualType")->str();
  if (TypeStr == "int") {
    llvm::GlobalVariable *Gval = new llvm::GlobalVariable(TheModule,
        llvm::Type::getInt32Ty(TheContext), false,
        llvm::GlobalValue::ExternalLinkage, 0, name);
    st.AddSymbol(name, Gval);
  } else if (TypeStr == "const int") {
    llvm::GlobalVariable *Gval = new llvm::GlobalVariable(TheModule,
        llvm::Type::getInt32Ty(TheContext), true,
        llvm::GlobalValue::ExternalLinkage, 0, name);
    st.AddSymbol(name, Gval);
  } else if (std::regex_search(TypeStr.begin(), TypeStr.end(), std::regex("[[0-9]*]"))) { 
    std::vector<int> dim = Array2Vec(TypeStr);
    auto Builder = std::make_unique<llvm::IRBuilder<>>(TheContext);
    llvm::Type *array_type = Builder->getInt32Ty();
    for (int i = 0; i < dim.size(); i++) 
      array_type = llvm::ArrayType::get(array_type, dim[dim.size() - i - 1]);
    llvm::GlobalVariable *garray = new llvm::GlobalVariable(TheModule,
        array_type, false, llvm::GlobalValue::ExternalLinkage, 0, name);
    st.AddSymbol(name, garray);
    if (TypeStr.find("const") != std::string::npos)
      garray->setConstant(true); 
    if (O->getArray("inner") != nullptr) {
      llvm::Constant *const_array = GetConstInitList(O->getArray("inner")->begin()->getAsObject(), dim,
                                    Builder.get(), 0, nullptr);
      garray->setInitializer(const_array);
    }
    else {
      garray->setInitializer(llvm::ConstantAggregateZero::get(Builder->getInt32Ty()));
      garray->setAlignment(llvm::MaybeAlign(16));
    }
    return garray;
  }
  llvm::GlobalVariable *GlobalVar = TheModule.getNamedGlobal(name);
  auto innerArrayPtr = O->getArray("inner");
  if (innerArrayPtr == nullptr) {
    auto Builder = std::make_unique<llvm::IRBuilder<>>(TheContext);
    GlobalVar->setInitializer(Builder->getInt32(0));
  } else {
    auto Builder = std::make_unique<llvm::IRBuilder<>>(TheContext);
    auto innerArray = *innerArrayPtr;
    auto rval = GetValue(innerArray[0].getAsObject(), Builder.get(), nullptr);
    GlobalVar->setInitializer(llvm::dyn_cast<llvm::Constant>(rval));
  }
  return GlobalVar;
}

void buildTranslationUnitDecl(const llvm::json::Object *O) {
  if (O == nullptr) 
    return;
  if (auto kind = O->get("kind")->getAsString()) 
    assert(*kind == "TranslationUnitDecl");
  else 
    assert(0);
  st.ALevel();
  if (auto inner = O->getArray("inner"))
    for (const auto &it : *inner)
      if (auto inner = it.getAsObject())
        if (auto kind = inner->get("kind")->getAsString()) {
          if (*kind == "FunctionDecl")
            BuildFunctionDecl(inner);
          else if (*kind == "VarDecl")
            BuildGlobalVarDecl(inner);
        }
  st.SLevel();
}

}  // namespace

int main() {
  auto llvmin = llvm::MemoryBuffer::getFileOrSTDIN("-");
  auto json = llvm::json::parse(llvmin.get()->getBuffer());
  buildTranslationUnitDecl(json->getAsObject());
  TheModule.print(llvm::outs(), nullptr);
}