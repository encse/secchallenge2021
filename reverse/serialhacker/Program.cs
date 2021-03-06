using System;

namespace rev
{
    class Program
    {
        Random r = new Random();

        string Take(string st, int n){
            var res = "";
            while(res.Length < n){
                res += st[r.Next(st.Length)];
            }
            return res;
        }

        void Run(){
            var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
            var checks = new Func<string,bool>[]{ok1, ok2, ok3, ok4}; 
            foreach(var check in checks){
                while (true) {
                    var part = Take(alphabet, 5);
                    if (check(part)) {
                        Console.WriteLine(part);
                        break;
                    }
                }
            }
        }

        bool ok1(string st){
            int num = 0;
            foreach (char ch in st)
                num += (int) ch;
            return num == 385;
        }

        bool ok2(string st){
            long num = 1;
            foreach (char ch in st)
                num *= (long) ch;
            return num % 512L == 420L;
        }


        bool ok3(string i) =>  (int) i[0] == (int) i[4] && ((int) i[1] == (int) i[3] && i[2] == 'E');

        bool ok4(string j) => (int) j[0] == (int) j[1] - 1 && ((int) j[1] == (int) j[2] - 1 && (int) j[2] == (int) j[3] - 2) && (int) j[3] == (int) j[4] - 3;


        static void Main(string[] args)
        {
            new Program().Run();
        }
    }
}
