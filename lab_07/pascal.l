%{
#include <stdio.h>
%}

%%
"program"      { printf("KEYWORD: program\n"); }
"var"          { printf("KEYWORD: var\n"); }
"begin"        { printf("KEYWORD: begin\n"); }
"end"          { printf("KEYWORD: end\n"); }
"integer"      { printf("KEYWORD: integer\n"); }
"real"         { printf("KEYWORD: real\n"); }
"if"           { printf("KEYWORD: if\n"); }
"then"         { printf("KEYWORD: then\n"); }
"else"         { printf("KEYWORD: else\n"); }
"while"        { printf("KEYWORD: while\n"); }
"do"           { printf("KEYWORD: do\n"); }
"for"          { printf("KEYWORD: for\n"); }
"to"           { printf("KEYWORD: to\n"); }
":="           { printf("ASSIGN\n"); }
";"            { printf("SEMICOLON\n"); }
","            { printf("COMMA\n"); }
"("            { printf("LPAREN\n"); }
")"            { printf("RPAREN\n"); }
":"            { printf("COLON\n"); }
"="            { printf("EQUAL\n"); }
"<="           { printf("LE\n"); }
">="           { printf("GE\n"); }
"<>"           { printf("NE\n"); }
"<"            { printf("LT\n"); }
">"            { printf("GT\n"); }
"."            { printf("DOT\n"); }
"+"            { printf("PLUS\n"); }
"-"            { printf("MINUS\n"); }
"*"            { printf("MUL\n"); }
"/"            { printf("DIV\n"); }
[0-9]+\.[0-9]+ { printf("REAL: %s\n", yytext); }
[0-9]+         { printf("INTEGER: %s\n", yytext); }
[a-zA-Z][a-zA-Z0-9]* { printf("IDENTIFIER: %s\n", yytext); }
[ \t\n\r]+       { /* skip whitespace */ }
.              { printf("UNKNOWN: %s\n", yytext); }
%%

int main(void) {
    yylex();
    return 0;
}

int yywrap() { return 1; }
