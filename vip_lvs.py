#!/usr/bin/env  python 
#encoding=utf8
#By yichi
import os
import re
import sys
import time
import subprocess
import datetime
from optparse import OptionParser

class lvsadd:
    def __init__(self):
        self.today = time.strftime("%Y%m%d%H%M%S",time.localtime(time.time()))

    def _backup(self):
        self.file1 = "/etc/keepalived/lvs.conf.%s" %self.today
        self.file2 = "/etc/keepalived/lvs.conf.%s" %self.user 
        self.cp_cmd = """ cp /etc/keepalived/lvs.conf  %s ; cp -a /etc/keepalived/lvs.conf  %s """ % (self.file1,self.file2)
        self.bak_pro = subprocess.Popen(self.cp_cmd,shell=True,stderr=subprocess.PIPE)
        if  self.bak_pro.stderr.read():
            print 'lvs conf backup fail!!!'
            sys.exit()
        else :
            print 'lvs conf backup sucess!!!'
        return self.file2

    def _selfipcheck(self):
        rs_ip=self.rsip.split(",")
        a=0
        for i in  range(0,len(rs_ip)):
            net='.'.join(rs_ip[i].split(".")[:3])
            net_cmd = """ ip a |grep "inet" """
            net_pro = subprocess.Popen(net_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if  net_pro.stderr.read():
                print 'ip a show fail!!!'
                sys.exit()
            else :
                net_re=re.findall(net,net_pro.stdout.read())
                if not net_re:
                    print "not have Self IP\t"+net+".0"
                    a=a+1
        if a>0:
            print "please add Self IP and vip_lvs.py -s conf -u user "

    def _conftmp1_fnat(self):
        fi=open("tmp_conf.txt","a+")
        h="#RT"+self.num+"\n"
        i="virtual_server "+self.vip+" "+str(self.port)+" {\n"
        j="\tdelay_loop 5\n"
        k="\tlb_algo wrr\n"
        l="\tlb_kind FNAT\n"
        m="\tprotocol TCP\n"
        n="\n"
        o="\tladdr_group_name laddr_g1\n"
        fi.write(h)
        fi.write(i)
        fi.write(j)
        fi.write(k)
        fi.write(l)
        fi.write(m)
        fi.write(n)
        fi.write(o)
        fi.close()

    def _conftmp1_dr(self):
        fi=open("tmp_conf.txt","a+")
        h="#RT"+self.num+"\n"
        i="virtual_server "+self.vip+" "+str(self.port)+" {\n"
        j="\tdelay_loop 5\n"
        k="\tlb_algo wrr\n"
        l="\tlb_kind DR\n"
        m="\tprotocol TCP\n"
        n="\n"
        fi.write(h)
        fi.write(i)
        fi.write(j)
        fi.write(k)
        fi.write(l)
        fi.write(m)
        fi.write(n)
        fi.close()
    def _conftmp2(self,rsip,port):
        fi=open("tmp_conf.txt","a+")
        a="\treal_server "+rsip+" "+str(port)+" {\n"
        b="\t\tweight 5000\n"
        c="\t\tTCP_CHECK {\n"
        d="\t\t\tconnect_port "+str(port)+"\n"
        e="\t\t\tconnect_timeout 10\n"
        f="\t\t}\n"
        g="\t}\n"
        fi.write(a)
        fi.write(b)
        fi.write(c)
        fi.write(d)
        fi.write(e)
        fi.write(f)
        fi.write(g)
        fi.close()
    def _conftmp3(self):
        fi=open("tmp_conf.txt","a+")
        p="}\n"
        fi.write(p)
        fi.close()

    def _conf_fnat(self):
        rs_ip=self.rsip.split(",")
        if str(os.path.exists('tmp_conf.txt')) == 'True':
            os.remove("tmp_conf.txt")
        os.mknod("tmp_conf.txt")
        self._conftmp1_fnat()
        for i in  range(0,len(rs_ip)):
            self._conftmp2(rs_ip[i],self.port)
        self._conftmp3()

    def _conf_dr(self):
        rs_ip=self.rsip.split(",")
        if str(os.path.exists('tmp_conf.txt')) == 'True':
            os.remove("tmp_conf.txt")
        os.mknod("tmp_conf.txt")
        self._conftmp1_dr()
        for i in  range(0,len(rs_ip)):
            self._conftmp2(rs_ip[i],self.port)
        self._conftmp3()

    def _addconf(self):
        self.get_line_cmd = """ wc -l /etc/keepalived/lvs.conf.%s |awk '{print $1}' """ % (self.user)
        try:
            self.line_pro = subprocess.Popen(self.get_line_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            self.line_pro2 = int(self.line_pro.stdout.read())+2
            lines=[]
            fi2=open(self.file2,'r')
            fi3=open("tmp_conf.txt",'r')
            fi4=fi3.read()
            for line in fi2:
                lines.append(line)
            fi2.close()
            lines.insert(self.line_pro2,fi4)
            s=''.join(lines)
            fi2=open(self.file2,'w+')
            fi2.write(s)
            fi2.close()
            self._diffconf()
        except Exception,e:
           print Exception,":",e
           print ' invalid user,please check again!  '
           sys.exit()

    def _diffconf(self):
        self.diff_cmd = """ diff -c /etc/keepalived/lvs.conf /etc/keepalived/lvs.conf.%s |grep "^+" """ % (self.user)
        self.diff_pro = subprocess.Popen(self.diff_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if  self.diff_pro.stderr.read():
            print 'please check conf !!!'
            sys.exit()
        else :
            print 'Add Conf Show: \n'+self.diff_pro.stdout.read()

    def _save(self):
        self.save_cmd = """ cp -a /etc/keepalived/lvs.conf.%s /etc/keepalived/lvs.conf """ % (self.user)
        self.kill_cmd = """ kill -HUP `cat /var/run/checkers.pid` """ 
        self.save_pro = subprocess.Popen(self.save_cmd,shell=True,stderr=subprocess.PIPE)
        if  self.save_pro.stderr.read():
            print 'lvs conf save fail!!!'
            sys.exit()
        else :
            print 'lvs conf save sucess!!!'
            self.kill_pro = subprocess.Popen(self.kill_cmd,shell=True,stderr=subprocess.PIPE)
            if  self.kill_pro.stderr.read():
                print 'lvs kill checkers.pid fail!!!'
                sys.exit()
            else :
                print 'kill -HUP checkers.pid sucess !'

    def _useage(self):
        print  "eg: vip_lvs.py -v 1.1.1.1 -r 172.16.1.2,172.16.1.3 -p 80 -u yichi -m dr -n 922203  eg: vip_lvs.py -s conf -u yichi"
        print  "-v  Vip"
        print  "-r  Need to add a new IP in the configuration file ,you can -r ip1,ip2,ip3... "
        print  "-p  Port "
        print  "-u  Your name "
        print  "-n  RT number "
        print  "-m  Mode: dr or fnat "
        print  "-s  cp lvs.conf.user to lvs.conf and kill -HUP checkers.pid "

    def _main(self):
        parser = OptionParser()
        parser.add_option("-v","--vip",type="string",dest="vip")
        parser.add_option("-r","--rsip",type="string",dest="rsip")
        parser.add_option("-p","--port",type="int",dest="port")
        parser.add_option("-u","--user",type="string",dest="user")
        parser.add_option("-n","--num",type="string",dest="num")
        parser.add_option("-m","--mode",type="string",dest="mode")
        parser.add_option("-s","--save",type="string",dest="save")
        (options, agrgs) = parser.parse_args()
        try:
            self.vip  = options.vip
            self.rsip = options.rsip
            self.port = options.port
            self.user = options.user
            self.num = options.num
            self.mode = options.mode
            self.save = options.save

            if str(self.save)=='conf' and str(self.vip)=='None' and str(self.rsip)=='None' and str(self.port)=='None' and str(self.num)=='None' and str(self.mode)=='None' and not str(self.user)=='None' :
                self._save()
            elif str(self.vip)=='None' or str(self.rsip)=='None'  or  str(self.port)=='None' or  str(self.user)=='None' or str(self.num)=='None' or str(self.mode)=='None' :
                self._useage()
            else :
                if str(self.mode)=='fnat' :
                    self._backup()
                    self._conf_fnat()
                    self._addconf()
                elif str(self.mode)=='dr' :
                    self._backup()
                    self._conf_dr()
                    self._addconf()
                    self._selfipcheck()
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    test=lvsadd()
    test._main()
