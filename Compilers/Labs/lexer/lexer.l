%{
#include <cstdio>
#include <string>
using namespace std;
#define YYEOF (0)
#define ENTER (1)   
#define SPACE (2)    
int yylex();

string LOC = "<stdin>";             /*文件位置*/
string SOL = "", LS = "";           /*换行和空白符*/
bool Sflag = true, Lflag = false;   /*判断换行和空白符*/

int main() {
  yyout = stderr;
  int flag = 1;
  do {  
    if (Sflag) SOL = "[StartOfLine] ";
    else SOL = "";
    if (Lflag) LS = "[LeadingSpace] ";
    else LS = "";
    flag = yylex();
    if (flag != SPACE) {             
      Lflag = false;
      if (flag != ENTER)
        Sflag = false;
    }
  } while (flag != YYEOF);
}

int yyrow = 1, yycolumn = 1, yycolpre = 1;
#define YY_USER_ACTION                                                         \
  do {                                                                         \
    yycolumn += yyleng;                                                        \
  } while (0);
%}
%option noyywrap
%%

int {
  std::fprintf(yyout, "int '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

char {
  std::fprintf(yyout, "char '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

void {
  std::fprintf(yyout, "void '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

struct {
  std::fprintf(yyout, "struct '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

long {
  std::fprintf(yyout, "long '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

short {
  std::fprintf(yyout, "short '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

signed {
  std::fprintf(yyout, "signed '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

unsigned {
  std::fprintf(yyout, "unsigned '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

float {
  std::fprintf(yyout, "float '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

double {
  std::fprintf(yyout, "double '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

union {
  std::fprintf(yyout, "union '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

enum {
  std::fprintf(yyout, "enum '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

auto {
  std::fprintf(yyout, "auto '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

register {
  std::fprintf(yyout, "register '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

static {
  std::fprintf(yyout, "static '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

extern {
  std::fprintf(yyout, "extern '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

typedef {
  std::fprintf(yyout, "typedef '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

return {
  std::fprintf(yyout, "return '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

const {
  std::fprintf(yyout, "const '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

if {
  std::fprintf(yyout, "if '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

else {
  std::fprintf(yyout, "else '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

do {
  std::fprintf(yyout, "do '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

while {
  std::fprintf(yyout, "while '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

continue {
  std::fprintf(yyout, "continue '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

break {
  std::fprintf(yyout, "break '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

switch {
  std::fprintf(yyout, "switch '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

case {
  std::fprintf(yyout, "case '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

default {
  std::fprintf(yyout, "default '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

for {
  std::fprintf(yyout, "for '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

sizeof {
  std::fprintf(yyout, "sizeof '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

goto {
  std::fprintf(yyout, "goto '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\( {
  std::fprintf(yyout, "l_paren '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\) {
  std::fprintf(yyout, "r_paren '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\{ {
  std::fprintf(yyout, "l_brace '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\} {
  std::fprintf(yyout, "r_brace '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\[ {
  std::fprintf(yyout, "l_square '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\] {
  std::fprintf(yyout, "r_square '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\? {
  std::fprintf(yyout, "question '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

: {
  std::fprintf(yyout, "colon '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

; {
  std::fprintf(yyout, "semi '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

, {
  std::fprintf(yyout, "comma '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

!= {
  std::fprintf(yyout, "exclaimequal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

! {
  std::fprintf(yyout, "exclaim '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

= {
  std::fprintf(yyout, "equal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

== {
  std::fprintf(yyout, "equalequal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\<= {
  std::fprintf(yyout, "lessequal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

>= {
  std::fprintf(yyout, "greaterequal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\< {
  std::fprintf(yyout, "less '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

> {
  std::fprintf(yyout, "greater '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\+ {
  std::fprintf(yyout, "plus '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\+\+ {
  std::fprintf(yyout, "plusplus '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\+= {
  std::fprintf(yyout, "plusequal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

- {
  std::fprintf(yyout, "minus '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

-- {
  std::fprintf(yyout, "minusminus '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

-= {
  std::fprintf(yyout, "minusequal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\* {
  std::fprintf(yyout, "star '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\*= {
  std::fprintf(yyout, "starequal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\/ {
  std::fprintf(yyout, "slash '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\/= {
  std::fprintf(yyout, "slashequal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

% {
  std::fprintf(yyout, "percent '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

%= {
  std::fprintf(yyout, "percentequal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

& {
  std::fprintf(yyout, "amp '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

&= {
  std::fprintf(yyout, "ampequal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\| {
  std::fprintf(yyout, "pipe '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\|= {
  std::fprintf(yyout, "pipeequal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\^ {
  std::fprintf(yyout, "caret '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\^= {
  std::fprintf(yyout, "caretequal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\<\< {
  std::fprintf(yyout, "lessless '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

>> {
  std::fprintf(yyout, "greatergreater '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

~ {
  std::fprintf(yyout, "tilde '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

&& {
  std::fprintf(yyout, "ampamp '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\|\| {
  std::fprintf(yyout, "pipepipe '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\'.\' {
  std::fprintf(yyout, "char_constant '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

[0-9]+ {
  std::fprintf(yyout, "numeric_constant '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

0[xX][0-9a-fA-F]+ {
  std::fprintf(yyout, "numeric_constant '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

[a-zA-Z_][a-zA-Z_0-9]* {
  std::fprintf(yyout, "identifier '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

\"(\\.|[^"\\])*\" {
  std::fprintf(yyout, "string_literal '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

<<EOF>> {
  std::fprintf(yyout, "eof ''\t\tLoc=<%s:%d:%d>\n", LOC.c_str(),
               yyrow > 1 ? yyrow - 1 : yyrow, yycolpre - yyleng);
  return YYEOF;
}

#.* {
  string str = yytext;
  int l = str.find('\"');
  int r = str.rfind('\"');
  LOC = str.substr(l + 1, r - l - 1);
  int index = 0, tmp = 0;
  for (int i = 0; i < str.size(); ++i) {
    if (str[i] >= '0' && str[i] <= '9') {
      index = i;
      break;
    }
  }
  while (str[index] >= '0' && str[index] <= '9') {
    tmp *= 10;
    tmp += str[index] - '0';
    ++index;
  }
  yyrow = tmp - 1;  
}

\n {
  ++yyrow;
  yycolpre = yycolumn;
  yycolumn = 1;
  Sflag = true;
  return ENTER;
}

[\f\r\t\v ] {
  Lflag = true;
  return SPACE;
}

. {
  std::fprintf(yyout, "unknown '%s'\t\t%s%sLoc=<%s:%d:%d>\n", 
              yytext, SOL.c_str(), LS.c_str(), LOC.c_str(),
              yyrow, yycolumn - yyleng);
  return ~YYEOF;
}

%%
