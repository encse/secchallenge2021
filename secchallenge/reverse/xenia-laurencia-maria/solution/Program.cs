using System;
using System.Text.RegularExpressions;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace reverse {

    class Trampoline {
        public string cell;
        public Trampoline(string cell) {
            this.cell = cell;
        }
    }

    class Program {

        Regex rxShortcut = new Regex(@"^OR\(IF\(EEHVX=0.*,([$A-Za-z0-9]+)\(\)\)\),([$A-Za-z0-9]+)\(\)\)$");
        Regex rxVar = new Regex(@"^[A-Za-z][A-Za-z0-9]*$");
        Regex rxNum = new Regex(@"^-?[1-9][0-9]*$");
        Regex rxEq = new Regex(@"^([A-Za-z0-9]*)=([A-Za-z0-9]*)$");
        Regex rxGt = new Regex(@"^([A-Za-z0-9]*)&gt;([A-Za-z0-9]*)$");
        Regex rxLt = new Regex(@"^([A-Za-z0-9]*)&lt;([A-Za-z0-9]*)$");
        Regex rxGte = new Regex(@"^([A-Za-z0-9]*)&gt;=([A-Za-z0-9]*)$");
        Regex rxLte = new Regex(@"^([A-Za-z0-9]*)&lt;=([A-Za-z0-9]*)$");
        Regex rxAdd = new Regex(@"^([A-Za-z0-9]*)\+([A-Za-z0-9]*)$");
        Regex rxSub = new Regex(@"^([A-Za-z0-9]*)-([A-Za-z0-9]*)$");
        Regex rxCell = new Regex(@"^[$A-Za-z0-9]+\(\)$");
        Regex rxFun = new Regex(@"^[A-Za-z].*\(.*\)$");
        Regex rxString = new Regex("^\"[^\"]*\"$");

        Dictionary<string, string> cells = new Dictionary<string, string>();
        Dictionary<string, object> values = new Dictionary<string, object>();

        object evalExpr(string expr) {
            var m = rxShortcut.Match(expr);

            if (m.Success) {
                return new Trampoline(m.Groups[1].Value);
            }

            if (expr == "0") {
                return 0;
            }

            if (rxNum.Match(expr).Success) {
                return int.Parse(expr);
            }

            m = rxVar.Match(expr);

            if (m.Success) {
                var v = expr;
                if (!values.ContainsKey(v))
                    return 0;
                return values[v];
            }

            if (rxString.Match(expr).Success) {
                return expr.Substring(1, expr.Length - 2);
            }

            m = rxEq.Match(expr);
            if (m.Success) {
                var a = evalExpr(m.Groups[1].Value);
                var b = evalExpr(m.Groups[2].Value);
                return a == b;
            }

            m = rxLt.Match(expr);
            if (m.Success) {
                var a = evalExpr(m.Groups[1].Value);
                var b = evalExpr(m.Groups[2].Value);
                return (int)a < (int)b;
            }

            m = rxGt.Match(expr);
            if (m.Success) {
                var a = evalExpr(m.Groups[1].Value);
                var b = evalExpr(m.Groups[2].Value);
                return (int)a > (int)b;
            }

            m = rxAdd.Match(expr);
            if (m.Success) {
                var a = evalExpr(m.Groups[1].Value);
                var b = evalExpr(m.Groups[2].Value);
                return (int)a + (int)b;
            }
            m = rxSub.Match(expr);
            if (m.Success) {
                var a = evalExpr(m.Groups[1].Value);
                var b = evalExpr(m.Groups[2].Value);
                return (int)a - (int)b;
            }
            if (rxCell.Match(expr).Success) {
                return new Trampoline(expr.Substring(0, expr.Length - 2));
            }
            if (rxFun.Match(expr).Success) {

                var i = 0;
                while (expr[i] != '(')
                    i = i + 1;

                var function_name = expr.Substring(0, i);
                var args = new List<string>();

                i = i + 1;
                var j = i;

                bool accept_ch(char ch) {
                    if (expr[i] == ch) {
                        i = i + 1;
                        return true;
                    }
                    return false;
                };

                bool accept_string() {
                    if (accept_ch('"')) {
                        while (!accept_ch('"'))
                            i = i + 1;
                        return true;
                    }
                    return false;
                }

                while (expr[i] != ')') {
                    if (accept_string()) {
                        ;
                    } else if (accept_ch('(')) {
                        var p = 1;
                        while (p != 0) {
                            if (accept_string()) {
                                ;
                            } else if (accept_ch('(')) {
                                p = p + 1;
                            } else if (accept_ch(')')) {
                                p = p - 1;
                            } else {
                                i = i + 1;
                            }
                        }
                    } else if (accept_ch(',')) {
                        args.Add(expr.Substring(j, i - 1 - j));
                        j = i;
                    } else {
                        i = i + 1;
                    }
                }

                if (j != i)
                    args.Add(expr.Substring(j, i - j));

                if (function_name == "OR") {
                    var v = false;
                    foreach (var arg in args) {
                        var e = evalExpr(arg);
                        if (e is bool) {
                            v |= (bool)e;
                        } else if (e is int) {
                            v |= ((int)e) != 0;
                        } else if (e is Trampoline){
                            return e;
                        }
                    }
                    return v;

                } else if (function_name == "IF") {
                    if ((bool)evalExpr(args[0])) {
                        return evalExpr(args[1]);
                    } else
                        return evalExpr(args[2]);
                } else if (function_name == "SET.NAME" || function_name == "DEFINE.NAME") {
                    values[evalExpr(args[0]) as string] = evalExpr(args[1]);
                    return true;
                } else if (function_name == "FORMULA.FILL") {
                    var cell = args[1].Replace("$", "");
                    var value = (evalExpr(args[0]) as string).Substring(1);
                    cells[cell] = value;
                    return true;
                } else if (
                    function_name == "WAIT" ||
                    function_name == "WINDOW.SIZE" ||
                    function_name == "WINDOW.MOVE" ||
                    function_name == "WINDOW.RESTORE"
                ) {
                    return true;
                } else if (function_name == "CHAR") {
                    return (char)(int)evalExpr(args[0]);
                } else if (function_name == "ALERT") {
                    if (args.Count == 1 && args[0].Contains("&amp;")) {
                        var st = "";
                        foreach (var ch in args[0].Split("&amp;")) {
                            st += evalExpr(ch);
                        }
                        Console.ForegroundColor = ConsoleColor.Green;
                        Console.WriteLine();
                        Console.WriteLine(st);
                        Console.ResetColor();
                    }
                    return true;
                } else {
                    Console.WriteLine("=== " + function_name);
                    return true;
                    //throw new Exception("function name");
                }
            }

            Console.WriteLine(expr);
            throw new Exception("parse");

        }

        void LoadCells(string filn) {
            var rxCell = new Regex(@"^\s*<c r=""([^""]+)""");
            var rxValue = new Regex(@"^\s*<f>(.*)</f>");

            Console.WriteLine("Loading " + filn);

            var file = new StreamReader(filn);
            string line;
            string cell = null;
            while ((line = file.ReadLine()) != null) {
                var m = rxCell.Match(line);
                if (m.Success)
                    cell = m.Groups[1].Value;

                m = rxValue.Match(line);
                if (m.Success)
                    cells[cell] = m.Groups[1].Value;
            }

            Console.WriteLine("Loaded");
        }

        void Run(string filn) {
            LoadCells(filn);

            Console.WriteLine("Finding entry point:");
            var rxCellCall = new Regex(@"\$[A-Za-z]+\$[0-9]+\(\)");
            var notCalledCells = cells.Keys.ToHashSet();
            foreach (var kvp in cells) {
                foreach (Match m in rxCellCall.Matches(kvp.Value)) {
                    var c = m.Value.Replace("$", "");
                    c = c.Substring(0, c.Length - 2);
                    if (c != kvp.Key) {
                        notCalledCells.Remove(c);
                    }
                }
            }

            foreach (var notCalledCell in notCalledCells) {
                Console.WriteLine("   not referred cell: " + notCalledCell);
            }

            var cell = notCalledCells.Single(x => x != "A1");
            Console.WriteLine("Starting from: " + cell);
            var i = 0;
            while (cell != null && cell != "HALT") {
                if (i  % 10000 == 0) {
                    Console.Write("\rremaining cells: " + (cells.Count - i) + " " + cell + "                  ");
                }
                i++;

                cell = cell.Replace("$", "");
                var value = cells[cell];
                
                var t = evalExpr(value);

                if(!(t is Trampoline)){
                    break;
                }
                cell = (t as Trampoline).cell;
            }
        }

        static void Main(string[] args) {
            Console.WriteLine(@"################################################################################################");
            Console.WriteLine(@"#                                                                                              #");
            Console.WriteLine(@"#      ___                                __   ___       __                        __          #");
            Console.WriteLine(@"# \_/ |__  |\ | |  /\     |     /\  |  | |__) |__  |\ | /  ` |  /\      |\/|  /\  |__) |  /\   #");
            Console.WriteLine(@"# / \ |___ | \| | /~~\    |___ /~~\ \__/ |  \ |___ | \| \__, | /~~\     |  | /~~\ |  \ | /~~\  #");
            Console.WriteLine(@"#                                                                                              #");
            Console.WriteLine(@"#    Solver for the 'Xenia Laurencia Maria' challenge                                          #");
            Console.WriteLine(@"#    https://secchallenge.crysys.hu/challenges#Xenia%20Laurencia%20Maria-8                     #");
            Console.WriteLine(@"#                                                                                              #");
            Console.WriteLine(@"################################################################################################");
            Console.WriteLine();

            if (args.Length == 0) {
                Console.WriteLine(@"Usage: dotnet run <sheet.xml>");
                Console.WriteLine(" - sheet.xml: macro sheet file, find it in the unzipped xlsm.");
            } else {
                new Program().Run(args[0]);
            }
        }
    }
}
