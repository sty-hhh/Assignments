%{
#include "parser.hh"
#include <llvm/Support/JSON.h>
#include <llvm/Support/MemoryBuffer.h>
#include <llvm/Support/raw_ostream.h>

#include<queue>

#define yyerror(x)                                                             \
  do {                                                                         \
    llvm::errs() << (x);                                                       \
  } while (0)

namespace {
auto llvmin = llvm::MemoryBuffer::getFileOrSTDIN("-");
auto input = llvmin.get() -> getBuffer();
auto end = input.end(), it = input.begin();
bool flag = false;

auto wk_getline(char endline = '\n') {
  auto beg = it;
  while (it != end && *it != endline)
    ++it;
  auto len = it - beg;
  if (it != end && *it == endline)
    ++it;
  return llvm::StringRef(beg, len);
}

std::queue<llvm::json::Object> queue;
void preProcess() {
  while (it != end) {
    auto tk = wk_getline();
    auto b = tk.find("'") + 1, e = tk.rfind("'");
    auto s = tk.substr(b, e - b), t = tk.substr(0, tk.find(" "));
    if (t == "numeric_constant") {
      auto v = std::stoll(s.str(),0,0);
      auto tmp = std::to_string(v);
      if (v > 2147483647) {
        queue.push(llvm::json::Object{
          {"kind", "IntegerLiteral"}, 
          {"long", "true"}, 
          {"value", tmp}
        });  
      }
      else {
        queue.push(llvm::json::Object{
          {"kind", "IntegerLiteral"}, 
          {"long", "false"}, 
          {"value", tmp}
        });  
      }
    }
    if (t == "identifier") {
      queue.push(llvm::json::Object{
        {"value", s}
      });  
    }
    if (t == "string_literal") {
      queue.push(llvm::json::Object{
        {"kind", "StringLiteral"},
        {"value", s}
      });  
    }
  }
  it = input.begin();
}

llvm::json::Array stak;

} // namespace

auto yylex() {
  auto tk = wk_getline();
  auto b = tk.find("'") + 1, e = tk.rfind("'");
  auto s = tk.substr(b, e - b), t = tk.substr(0, tk.find(" "));
  if (t == "numeric_constant") 
    return T_NUMERIC_CONSTANT;
  if (t == "identifier") 
    return T_IDENTIFIER;
  if (t == "int")
    return T_INT;
  if (t == "return")
    return T_RETURN;
  if (t == "semi")
    return T_SEMI;
  if (t == "l_paren")
    return T_L_PAREN;
  if (t == "r_paren")
    return T_R_PAREN;
  if (t == "l_brace")
    return T_L_BRACE;
  if (t == "r_brace")
    return T_R_BRACE;
  if (t == "equal")
    return T_EQUAL;
  if (t == "exclaim")
    return T_EXCLAIM;
  if (t == "plus")
    return T_PLUS;
  if (t == "minus")
    return T_MINUS;
  if (t == "star")
    return T_STAR;
  if (t == "slash")
    return T_SLASH;
  if (t == "percent")
    return T_PERCENT;
  if (t == "less")
    return T_LESS;
  if (t == "greater")
    return T_GREATER;
  if (t == "lessequal")
    return T_LESSEQUAL;
  if (t == "greaterequal")
    return T_GREATEREQUAL;
  if (t == "equalequal")
    return T_EQUALEQUAL;
  if (t == "exclaimequal")
    return T_EXCLAIMEQUAL;
  if (t == "ampamp")
    return T_AMPAMP;
  if (t == "pipepipe")
    return T_PIPEPIPE;
  if (t == "comma")
    return T_COMMA;
  if (t == "const")
    return T_CONST;
  if (t == "if")
    return T_IF;
  if (t == "else")
    return T_ELSE;
  if (t == "do")
    return T_DO;
  if (t == "while")
    return T_WHILE;
  if (t == "break")
    return T_BREAK;
  if (t == "continue")
    return T_CONTINUE;
  if (t == "void")
    return T_VOID;
  if (t == "l_square")
    return T_L_SQUARE;
  if (t == "r_square")
    return T_R_SQUARE;
  if (t == "char")
    return T_CHAR;
  if (t == "string_literal")
    return T_STRING;
  return YYEOF;
}

int main() {
  preProcess();
  yyparse();
  llvm::outs() << stak.back() << "\n";
}
%}
%glr-parser
%token T_NUMERIC_CONSTANT
%token T_IDENTIFIER
%token T_INT
%token T_RETURN
%token T_SEMI
%token T_L_PAREN
%token T_R_PAREN
%token T_L_BRACE
%token T_R_BRACE
%token T_EQUAL
%token T_EXCLAIM
%token T_PLUS
%token T_MINUS
%token T_STAR
%token T_SLASH
%token T_PERCENT
%token T_LESS
%token T_GREATER
%token T_LESSEQUAL
%token T_GREATEREQUAL
%token T_EQUALEQUAL
%token T_EXCLAIMEQUAL
%token T_AMPAMP
%token T_PIPEPIPE
%token T_COMMA
%token T_CONST
%token T_IF
%token T_ELSE
%token T_DO
%token T_WHILE
%token T_BREAK
%token T_CONTINUE
%token T_VOID
%token T_L_SQUARE
%token T_R_SQUARE
%token T_CHAR
%token T_STRING
//
%start CompUnit
%%

CompUnit: 
  Decl {
    auto decl = stak.back().getAsObject();
    assert(decl != nullptr);
    assert(decl->get("kind") != nullptr);
    *(decl->get("kind")) = "TranslationUnitDecl";
  }
  | FuncDef {
    auto inner = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "TranslationUnitDecl"},
      {"inner", llvm::json::Array{inner}}
    });
  }
  | CompUnit FuncDef {
    auto inner = stak.back();
    stak.pop_back();

    auto unit = stak.back();
    auto _unit = unit.getAsObject();
    assert(_unit != nullptr);
    assert(_unit->get("inner") != nullptr);

    auto arr = _unit->get("inner")->getAsArray();
    assert(arr != nullptr);
    stak.pop_back();

    arr->push_back(inner);
    stak.push_back(unit);
  }
  | CompUnit Decl {
    auto inner = stak.back();
    auto _inner = inner.getAsObject();
    assert(_inner != nullptr);
    assert(_inner->get("inner") != nullptr);
    auto inner_arr = _inner->get("inner")->getAsArray();
    stak.pop_back();

    auto unit = stak.back();
    auto _unit = unit.getAsObject();
    assert(_unit != nullptr);
    assert(_unit->get("inner") != nullptr);

    auto unit_arr = _unit->get("inner")->getAsArray();
    assert(unit_arr != nullptr);
    stak.pop_back();

    for (auto it=inner_arr->begin(); it != inner_arr->end(); it++) 
      unit_arr->push_back(*it);
    stak.push_back(unit);    
  }

Decl:
  ConstDecl{} | VarDecl {}

ConstDecl:
  T_CONST BType MultiConstDef T_SEMI {}

MultiConstDef:
  ConstDef {
    auto inner = stak.back();
    assert(inner != nullptr);
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "MultiDef"},
      {"inner", llvm::json::Array{inner}}
    });
  }
  | MultiConstDef T_COMMA ConstDef {
    auto inner = stak.back();
    assert(inner != nullptr);
    stak.pop_back();

    auto multi = stak.back().getAsObject();
    assert(multi != nullptr);
    assert(multi->get("inner") != nullptr);
    auto arr = multi->get("inner")->getAsArray();
    arr->push_back(inner);
  }

ConstDef:
  Ident MultiSquare T_EQUAL ConstInitVal{
    auto inner = stak.back();
    stak.pop_back();
    auto constExp = stak.back();
    stak.pop_back();

    auto ident = stak.back().getAsObject();
    assert(ident != nullptr);
    assert(ident->get("value") != nullptr);
    stak.pop_back();

    stak.push_back(llvm::json::Object{
      {"kind", "VarDecl"},
      {"name", *(ident->get("value"))},
      {"inner", llvm::json::Array{inner}}}
    );
  }
  | Ident T_EQUAL ConstInitVal {
    auto inner = stak.back();
    auto _inner = inner.getAsObject();
    assert(_inner != nullptr);
    assert(_inner->get("kind") != nullptr);
    stak.pop_back();
    auto ident = stak.back().getAsObject();
    assert(ident != nullptr);
    assert(ident->get("value") != nullptr);
    stak.pop_back();

    if (_inner->get("long") != nullptr && *(_inner->get("long")) == "true") {
      stak.push_back(llvm::json::Object{
        {"kind", "VarDecl"},
        {"name", *(ident->get("value"))},
        {"inner", llvm::json::Array{llvm::json::Object{
                                    {"kind", "ImplicitCastExpr"},
                                    {"inner", llvm::json::Array{inner}}}}}
      });
    }
    else {
      stak.push_back(llvm::json::Object{
        {"kind", "VarDecl"},
        {"name", *(ident->get("value"))},
        {"inner", llvm::json::Array{inner}}
      });
    }
  }

MultiSquare:
  T_L_SQUARE ConstExp T_R_SQUARE{}
  | MultiSquare T_L_SQUARE ConstExp T_R_SQUARE{
    stak.pop_back();
  }

ConstInitValList:
  ConstInitVal {
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "InitListExpr"},
      {"inner", llvm::json::Array{}}
    });
  }
  | ConstInitValList T_COMMA ConstInitVal {
    stak.pop_back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "InitListExpr"},
      {"inner", llvm::json::Array{}}
    });
  }

ConstInitVal:
  ConstExp{}
  | T_L_BRACE T_R_BRACE {
    stak.push_back(llvm::json::Object{
      {"kind", "InitListExpr"},
      {"inner", llvm::json::Array{}}
    });
  }
  | T_L_BRACE ConstInitValList T_R_BRACE {
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "InitListExpr"},
      {"inner", llvm::json::Array{}}
    });
  }

VarDecl: 
  BType MultiVarDef T_SEMI {
    auto varDef = stak.back().getAsObject();
    assert(varDef != nullptr);
    varDef->insert({"kind", "VarDecl"});
  }

MultiVarDef:
  VarDef {
    auto inner = stak.back();
    assert(inner != nullptr);
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "MultiDef"},
      {"inner", llvm::json::Array{inner}}
    });
  }
  | MultiVarDef T_COMMA VarDef{
    auto inner = stak.back();
    assert(inner != nullptr);
    stak.pop_back();

    auto multi = stak.back().getAsObject();
    assert(multi != nullptr);
    assert(multi->get("inner") != nullptr);
    auto arr = multi->get("inner")->getAsArray();
    arr->push_back(inner);
  }

VarDef:
  Ident MultiSquare T_EQUAL InitVal{
    auto initVal = stak.back();
    stak.pop_back();
    auto constExp = stak.back();
    stak.pop_back();

    auto ident = stak.back().getAsObject();
    assert(ident != nullptr);
    assert(ident->get("value") != nullptr);
    stak.pop_back();

    stak.push_back(llvm::json::Object{
      {"kind", "VarDecl"},
      {"name", *(ident->get("value"))},
      {"inner", llvm::json::Array{initVal}}}
    );
  }
  | Ident T_EQUAL InitVal {
    auto inner = stak.back();
    assert(inner != nullptr);
    stak.pop_back();
    auto ident = stak.back().getAsObject();
    assert(ident != nullptr);
    assert(ident->get("value") != nullptr);
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "VarDecl"},
      {"name", *(ident->get("value"))},
      {"inner", llvm::json::Array{inner}}
    });
  }
  | Ident MultiSquare {
    auto constExp = stak.back();
    stak.pop_back();

    auto ident = stak.back().getAsObject();
    assert(ident != nullptr);
    assert(ident->get("value") != nullptr);
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "VarDecl"},
      {"name", *(ident->get("value"))}
    });
  }
  | Ident {
    auto ident = stak.back().getAsObject();
    assert(ident != nullptr);
    assert(ident->get("value") != nullptr);
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "VarDecl"},
      {"name", *(ident->get("value"))}
    });
  }

InitValList:
  InitVal {
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "InitListExpr"},
      {"inner", llvm::json::Array{}}
    });
  }
  | InitValList T_COMMA InitVal {
    stak.pop_back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "InitListExpr"},
      {"inner", llvm::json::Array{}}
    });
  }

InitVal:
  Exp {}
  | T_L_BRACE T_R_BRACE {
    stak.push_back(llvm::json::Object{
      {"kind", "InitListExpr"},
      {"inner", llvm::json::Array{}}
    });
  }
  | T_L_BRACE InitValList T_R_BRACE {
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "InitListExpr"},
      {"inner", llvm::json::Array{}}
    });
  }

// 函数声明
FuncDecl:
  FuncType Ident T_L_PAREN FuncFParams T_R_PAREN T_SEMI {
    auto funcfparams = stak.back();
    stak.pop_back();
    auto _funcfparams = funcfparams.getAsObject();
    auto ident = stak.back().getAsObject();
    stak.pop_back();
    *(_funcfparams->get("kind")) = "FunctionDecl";
    _funcfparams->insert({"name", *(ident->get("value"))});
    stak.push_back(funcfparams);
  }
  | FuncType Ident T_L_PAREN T_R_PAREN T_SEMI {
    auto name = stak.back().getAsObject();
    assert(name != nullptr);
    assert(name->get("value") != nullptr);
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "FunctionDecl"},
      {"name", *(name->get("value"))}
    });
  }

// 函数定义的解析
FuncDef:
  FuncType Ident T_L_PAREN FuncFParams T_R_PAREN Block {
    auto block = stak.back();
    stak.pop_back();
    auto funcfparams = stak.back();
    stak.pop_back();
    auto _funcfparams = funcfparams.getAsObject();
    auto ident = stak.back().getAsObject();
    stak.pop_back();
    *(_funcfparams->get("kind")) = "FunctionDecl";
    _funcfparams->insert({"name", *(ident->get("value"))});
    auto arr = _funcfparams->get("inner")->getAsArray();
    arr->push_back(block);
    stak.push_back(funcfparams);
  }
  | FuncType Ident T_L_PAREN T_R_PAREN Block {
    auto inner = stak.back();
    stak.pop_back();
    auto name = stak.back().getAsObject();
    assert(name != nullptr);
    assert(name->get("value") != nullptr);
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "FunctionDecl"},
      {"name", *(name->get("value"))},
      {"inner", llvm::json::Array{inner}}
    });
  }
  | FuncDecl {}

FuncType: T_VOID | T_INT | T_CHAR {}

FuncFParams:
  FuncFParam{
    auto tmp = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "FuncFParams"},
      {"inner", llvm::json::Array{tmp}}
    });
  }
  | FuncFParams T_COMMA FuncFParam {
    auto param = stak.back();
    stak.pop_back();
    auto params = stak.back().getAsObject();
    assert(params->get("kind") != nullptr);
    assert(params->get("inner") != nullptr);
    auto arr = params->get("inner")->getAsArray();
    arr->push_back(param);
  }

FuncFParam:
  BType Ident ArrParam {
    auto ident = stak.back().getAsObject();
    stak.pop_back();
    assert(ident->get("value") != nullptr);
    stak.push_back(llvm::json::Object{
      {"kind", "ParmVarDecl"},
      {"name", *(ident->get("value"))}
    });
  }
  | T_CONST BType Ident ArrParam {
    auto ident = stak.back().getAsObject();
    stak.pop_back();
    assert(ident->get("value") != nullptr);
    stak.push_back(llvm::json::Object{
      {"kind", "ParmVarDecl"},
      {"name", *(ident->get("value"))}
    });
  }
  | BType Ident {
    auto ident = stak.back().getAsObject();
    stak.pop_back();
    assert(ident->get("value") != nullptr);
    stak.push_back(llvm::json::Object{
      {"kind", "ParmVarDecl"},
      {"name", *(ident->get("value"))}
    });
  }

ArrParam:
  T_L_SQUARE T_R_SQUARE MultiArrParam {}
  | T_L_SQUARE T_R_SQUARE {}

MultiArrParam:
  T_L_SQUARE ConstExp T_R_SQUARE {
    stak.pop_back();
  }
  | MultiArrParam T_L_SQUARE ConstExp T_R_SQUARE {
    stak.pop_back();
  }

BType: 
  T_INT {}
  | T_CHAR {
    flag = true;
  }

Ident: T_IDENTIFIER {
  auto curNode = queue.front();
  queue.pop();
  stak.push_back(llvm::json::Object{curNode});
}

Block: 
  T_L_BRACE TmpBlock T_R_BRACE {}

TmpBlock:
  %empty {
    stak.push_back(llvm::json::Object{
      {"kind", "CompoundStmt"}
    });
  }
  | BlockItem {}

BlockItem:
  Stmt {
    auto inner = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "CompoundStmt"},
      {"inner", llvm::json::Array{inner}}
    });
  }
  | Decl {
    auto inner = stak.back();
    auto _inner = inner.getAsObject();
    assert(_inner != nullptr);
    assert(_inner->get("kind") != nullptr);
    *(_inner->get("kind")) = "DeclStmt";
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "CompoundStmt"},
      {"inner", llvm::json::Array{inner}}
    });
  }
  | BlockItem Stmt{
    auto inner = stak.back();
    stak.pop_back();
    auto unit = stak.back();
    auto _unit = unit.getAsObject();
    assert(_unit != nullptr);
    assert(_unit->get("inner") != nullptr);
    auto unit_arr = _unit->get("inner")->getAsArray();
    assert(unit_arr != nullptr);
    stak.pop_back();
    unit_arr->push_back(inner);
    stak.push_back(unit);
  }
  | BlockItem Decl {
    auto inner = stak.back();
    auto _inner = inner.getAsObject();
    assert(_inner != nullptr);
    assert(_inner->get("kind") != nullptr);
    *(_inner->get("kind")) = "DeclStmt";
    stak.pop_back();

    auto unit = stak.back();
    auto _unit = unit.getAsObject();
    assert(_unit != nullptr);
    assert(_unit->get("inner") != nullptr);
    auto unit_arr = _unit->get("inner")->getAsArray();
    assert(unit_arr != nullptr);
    stak.pop_back();
    unit_arr->push_back(inner);
    stak.push_back(unit);
  }

Stmt: OpenStmt{} | ClosedStmt{}

OpenStmt:
  T_IF T_L_PAREN Exp T_R_PAREN Stmt {
    auto if_stmt = stak.back();
    assert(if_stmt != nullptr);
    stak.pop_back();
    auto exp = stak.back();
    assert(exp != nullptr);
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "IfStmt"},
      {"inner", llvm::json::Array{exp, if_stmt}}
    });
  }
  | T_IF T_L_PAREN Exp T_R_PAREN ClosedStmt T_ELSE OpenStmt {
    auto else_stmt = stak.back();
    stak.pop_back();
    auto if_stmt = stak.back();
    stak.pop_back();
    auto exp = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "IfStmt"},
      {"hasElse", "true"},
      {"inner", llvm::json::Array{exp, if_stmt, else_stmt}}
    });
  }

ClosedStmt:
  NonIfStmt {}
  | T_IF T_L_PAREN Exp T_R_PAREN ClosedStmt T_ELSE ClosedStmt {
    auto else_stmt = stak.back();
    stak.pop_back();
    auto if_stmt = stak.back();
    stak.pop_back();
    auto exp = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "IfStmt"},
      {"hasElse", "true"},
      {"inner", llvm::json::Array{exp, if_stmt, else_stmt}}
    });
  }

NonIfStmt:
  LVal T_EQUAL Exp T_SEMI {
    auto inner2 = stak.back();
    stak.pop_back();
    auto inner1 = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"opcode", "="},
      {"kind", "BinaryOperator"},
      {"inner", llvm::json::Array{inner1, inner2}}
    });
  }
  | Exp T_SEMI{}
  | T_SEMI {
    stak.push_back(llvm::json::Object{
      {"kind", "NullStmt"}
    });
  }
  | T_WHILE T_L_PAREN Exp T_R_PAREN Stmt {
    auto while_stmt = stak.back();
    stak.pop_back();
    auto exp = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "WhileStmt"},
      {"inner", llvm::json::Array{exp, while_stmt}}
    });
  }
  | T_DO Stmt T_WHILE T_L_PAREN Exp T_R_PAREN T_SEMI {
    auto exp = stak.back();
    stak.pop_back();
    auto while_stmt = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "DoStmt"},
      {"inner", llvm::json::Array{while_stmt, exp}}
    });
  }
  | Block {}
  | T_BREAK T_SEMI {
    stak.push_back(llvm::json::Object{
      {"kind", "BreakStmt"}
    });
  }
  | T_CONTINUE T_SEMI {
    stak.push_back(llvm::json::Object{
      {"kind", "ContinueStmt"}
    });
  }
  | T_RETURN Exp T_SEMI {
    auto inner = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "ReturnStmt"},
      {"inner", llvm::json::Array{inner}}
    });
  }
  | T_RETURN T_SEMI {
    stak.push_back(llvm::json::Object{
      {"kind", "ReturnStmt"}
    });
  }

Exp:
  LOrExp {}

LVal:
  MultiLVal {}
  | Ident {
    auto inner = stak.back();
    assert(inner != nullptr);
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "DeclRefExpr"},
      {"referenceDecl", inner}
    });
  }

MultiLVal:
  SingleLVal {}
  | MultiLVal T_L_SQUARE Exp T_R_SQUARE {
    auto exp = stak.back();
    stak.pop_back();
    auto multi = stak.back();
    stak.pop_back();
    auto tmp = llvm::json::Object{
      {"kind", "ImplicitCastExpr"},
      {"inner", llvm::json::Array{multi}}
    };
    stak.push_back(llvm::json::Object{
      {"kind", "ArraySubscriptExpr"},
      {"inner", llvm::json::Array{llvm::json::Object{tmp},exp}}
    });
  }

SingleLVal:
  Ident T_L_SQUARE Exp T_R_SQUARE {
    auto exp = stak.back();
    assert(exp != nullptr);
    stak.pop_back();
    auto ident = stak.back();
    stak.pop_back();
    auto in_inner1 = llvm::json::Object{
      {"kind", "DeclRefExpr"},
      {"referenceDecl", ident}
    };
    auto inner1 = llvm::json::Object{
      {"kind", "ImplicitCastExpr"},
      {"inner", llvm::json::Array{llvm::json::Object{in_inner1}}}
    };
    stak.push_back(llvm::json::Object{
      {"kind", "ArraySubscriptExpr"},
      {"inner", llvm::json::Array{llvm::json::Object{inner1},exp}}
    });
  }

PrimaryExp:
  T_L_PAREN Exp T_R_PAREN {
    auto exp = stak.back();
    auto _exp = exp.getAsObject();
    assert(_exp != nullptr);
    assert(_exp->get("kind") != nullptr);
    stak.pop_back();

    if (_exp->get("LVal") != nullptr && *(_exp->get("LVal")) == "true") {
      auto arr = _exp->get("inner")->getAsArray();
      auto inner = arr->back();
      stak.push_back(llvm::json::Object{
        {"kind", "ParenExpr"},
        {"inner", llvm::json::Array{inner}}
      });
      auto inner1 = stak.back();
      stak.pop_back();
      stak.push_back(llvm::json::Object{
        {"kind", "ImplicitCastExpr"},
        {"inner", llvm::json::Array{inner1}}
      });
    }
    else{
      stak.push_back(llvm::json::Object{
        {"kind", "ParenExpr"},
        {"inner", llvm::json::Array{exp}}
      });
    }
  }
  | Number {}
  | String {}
  | LVal {
    auto inner = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "ImplicitCastExpr"},
      {"LVal", "true"},
      {"inner", llvm::json::Array{inner}}
    });
  }

Number: 
  T_NUMERIC_CONSTANT {
    auto curNode = queue.front();
    queue.pop();
    stak.push_back(llvm::json::Object{curNode});
  }

Str:
  Str String{
    auto inner1 = stak.back();
    auto _inner1 = inner1.getAsObject();
    assert(_inner1 != nullptr);
    assert(_inner1->get("kind") != nullptr);
    stak.pop_back();

    auto inner2 = stak.back();
    auto _inner2 = inner2.getAsObject();
    assert(_inner2 != nullptr);
    assert(_inner2->get("kind") != nullptr);
    stak.pop_back();

    auto a = _inner2->get("inner")->getAsArray();
    auto b = a->back();
    auto _b = b.getAsObject();
    assert(a != nullptr);
    assert(_b != nullptr);

    std::string t1 = _inner1->getString("value").getValue().str();
    std::string t2 = _b->getString("value").getValue().str();
    std::string t = t2.substr(0, t2.length()-1) + t1.substr(1, t1.length());

    stak.push_back(llvm::json::Object{
      {"kind", "StringLiteral"},
      {"value", t}
    });
    auto inner = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "ImplicitCastExpr"},
      {"inner", llvm::json::Array{inner}}
    });
  }
  | String {
    auto inner = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "ImplicitCastExpr"},
      {"inner", llvm::json::Array{inner}}
    });
  }

String: T_STRING {
  auto curNode = queue.front();
  queue.pop();
  stak.push_back(llvm::json::Object{curNode});
}

UnaryExp:
  PrimaryExp {} | FuncCall {}
  | UnaryOp UnaryExp {
    auto exp = stak.back();
    auto _exp = exp.getAsObject();
    assert(_exp != nullptr);
    assert(_exp->get("kind") != nullptr);
    stak.pop_back();

    if (_exp->get("long") != nullptr && *(_exp->get("long")) == "true") {
      stak.push_back(llvm::json::Object{
        {"kind", "UnaryOperator"},
        {"long", "true"},
        {"inner", llvm::json::Array{exp}}
      });
    }
    else {
      stak.push_back(llvm::json::Object{
        {"kind", "UnaryOperator"},
        {"long", "false"},
        {"inner", llvm::json::Array{exp}}
      });
    }
  }

UnaryOp: T_PLUS | T_MINUS | T_EXCLAIM {}

FuncRParams:
  Str { 
    auto exp = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "ImplicitCastExpr"},
      {"inner", llvm::json::Array{exp}}
    });
    auto inner = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "FuncRParams"},
      {"inner", llvm::json::Array{inner}} 
    });
  }
  | Exp {
    auto exp = stak.back();
    auto _exp = exp.getAsObject();
    assert(_exp != nullptr);
    assert(_exp->get("kind") != nullptr);
    stak.pop_back();

    if (_exp->get("inner") == nullptr || flag == false) {
      stak.push_back(llvm::json::Object{
        {"kind", "FuncRParams"},
        {"inner", llvm::json::Array{exp}}
      });
    }
    else {
      stak.push_back(llvm::json::Object{
        {"kind", "ImplicitCastExpr"},
        {"inner", llvm::json::Array{exp}}
      });
      auto inner = stak.back();
      stak.pop_back();
      stak.push_back(llvm::json::Object{
        {"kind", "FuncRParams"},
        {"inner", llvm::json::Array{inner}}
      });
    }
  }
  | FuncRParams T_COMMA Exp {
    auto exp = stak.back();
    stak.pop_back();
    auto funcRparams = stak.back();
    stak.pop_back();
    auto _funcRparams = funcRparams.getAsObject();
    auto arr = _funcRparams->get("inner")->getAsArray();
    arr->push_back(exp);
    stak.push_back(funcRparams);
  }

// 函数调用
FuncCall:
  RVal T_L_PAREN T_R_PAREN {
    auto inner = stak.back();
    stak.pop_back();
    auto it = stak.back();
    auto _it = it.getAsObject();
    stak.push_back(llvm::json::Object{
      {"kind", "CallExpr"},
      {"inner", llvm::json::Array{inner}}
    });
  }
  | RVal T_L_PAREN FuncRParams T_R_PAREN {
    auto funcRparams = stak.back();
    auto _funcRparams = funcRparams.getAsObject();
    stak.pop_back();
    auto rVal = stak.back();
    stak.pop_back();
    *(_funcRparams->get("kind")) = "CallExpr";
    auto arr = _funcRparams->get("inner")->getAsArray();
    arr->insert(arr->begin(), rVal);
    stak.push_back(funcRparams);
  }
 
RVal: Ident {
  auto name = stak.back();
  stak.pop_back();
  stak.push_back(llvm::json::Object{
    {"kind", "ImplicitCastExpr"},
    {"inner", llvm::json::Array{llvm::json::Object{{"kind", "DeclRefExpr"}}}}
  });
}

AddExp:
  MulExp {}
  | AddExp AddOp MulExp {
    auto inner2 = stak.back();
    stak.pop_back();
    auto inner1 = stak.back();
    stak.pop_back();
    
    auto _inner2 = inner2.getAsObject();
    auto _inner1 = inner1.getAsObject();
    assert(_inner2 != nullptr);
    assert(_inner1 != nullptr);
    assert(_inner2->get("kind") != nullptr);
    assert(_inner1->get("kind") != nullptr);

    if (_inner2->get("long") != nullptr && _inner1->get("long") != nullptr && *(_inner2->get("long")) != *(_inner1->get("long"))) {
      if (*(_inner2->get("long")) == "false") {
        *(_inner2->get("long")) = "true";
        stak.push_back(llvm::json::Object{
          {"kind", "ImplicitCastExpr"},
          {"inner", llvm::json::Array{inner2}}
        });
        auto tmp = stak.back();
        stak.pop_back();
        stak.push_back(llvm::json::Object{
          {"kind", "BinaryOperator"},
          {"long", "true"},
          {"inner", llvm::json::Array{inner1, tmp}}
        });
      }
      else {
        *(_inner1->get("long")) = "true";
        stak.push_back(llvm::json::Object{
          {"kind", "ImplicitCastExpr"},
          {"inner", llvm::json::Array{inner1}}
        });
        auto tmp = stak.back();
        stak.pop_back();
        stak.push_back(llvm::json::Object{
          {"kind", "BinaryOperator"},
          {"long", "true"},
          {"inner", llvm::json::Array{tmp, inner2}}
        });
      }
    }
    else {
      stak.push_back(llvm::json::Object{
        {"kind", "BinaryOperator"},
        {"inner", llvm::json::Array{inner1, inner2}}
      });
    }
  }

MulOp: T_STAR | T_SLASH | T_PERCENT {}

AddOp: T_PLUS | T_MINUS {}

MulExp:
  UnaryExp {}
  | MulExp MulOp UnaryExp {
    auto inner2 = stak.back();
    stak.pop_back();
    auto inner1 = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "BinaryOperator"},
      {"inner", llvm::json::Array{inner1, inner2}}
    });
  }

CompareOp: T_LESS | T_GREATER | T_LESSEQUAL | T_GREATEREQUAL {}

RelExp:
  AddExp {}
  | RelExp CompareOp AddExp {
    auto inner2 = stak.back();
    stak.pop_back();
    auto inner1 = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "BinaryOperator"},
      {"inner", llvm::json::Array{inner1, inner2}}
    });
  }

EqualOp: T_EQUALEQUAL | T_EXCLAIMEQUAL {}

EqExp:
  RelExp {}
  | EqExp EqualOp RelExp {
    auto inner2 = stak.back();
    stak.pop_back();
    auto inner1 = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "BinaryOperator"},
      {"inner", llvm::json::Array{inner1, inner2}}
    });
  }

LAndExp:
  EqExp {}
  | LAndExp T_AMPAMP EqExp {
    auto inner2 = stak.back();
    stak.pop_back();
    auto inner1 = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "BinaryOperator"},
      {"inner", llvm::json::Array{inner1, inner2}}
    });
  }

LOrExp:
  LAndExp {}
  | LOrExp T_PIPEPIPE LAndExp {
    auto inner2 = stak.back();
    stak.pop_back();
    auto inner1 = stak.back();
    stak.pop_back();
    stak.push_back(llvm::json::Object{
      {"kind", "BinaryOperator"},
      {"inner", llvm::json::Array{inner1, inner2}}
    });
  }
  
ConstExp: Exp {}
%%