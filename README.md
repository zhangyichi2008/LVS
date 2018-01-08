# LVS
lvs自动化（member_lvs.py  用来增加和删除member，vip_lvs.py 用来新增加vip的部分配置）

eg: member_lvs.py -c add -v 1.1.1.1 -r 172.16.1.2,172.16.1.3 -p 80 -u yichi or member_lvs.py -s conf -u yichi

-c  add or del
-v  vip
-r  need to add a new rs in the configuration file ,you can -r ip1,ip2,ip3... 
-p  port 
-u  user (Your staffMailbox prefix) 
-s  save (cp lvs.conf.user to lvs.conf and kill -HUP checkers.pid) 


vip_lvs.py -v vip  -r rsip  -p port  -u user -m mode -n RTnumber or vip_lvs.py -s conf -u user

-v  Vip
-r  Need to add a new IP in the configuration file ,you can -r ip1,ip2,ip3... 
-p  Port 
-u  Your name 
-n  RT number 
-m  Mode: dr or fnat 
-s  cp lvs.conf.user to lvs.conf and kill -HUP checkers.pid 
