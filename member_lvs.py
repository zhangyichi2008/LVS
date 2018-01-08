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

class lvs:
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

    def _diffconf(self):
        self.diff_cmd = """ diff -c /etc/keepalived/lvs.conf /etc/keepalived/lvs.conf.%s  """ % (self.user)
        self.diff_pro = subprocess.Popen(self.diff_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if  self.diff_pro.stderr.read():
            print 'please check conf !!!'
            sys.exit()
        else :
            print 'Diff Conf Show: \n'+self.diff_pro.stdout.read()

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
            print "please add Self IP and member_lvs.py -s conf -u user "

    def _addconftmp(self,rsip,port):
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
    def _conf(self):
        rs_ip=self.rsip.split(",")
        if str(os.path.exists('tmp_conf.txt')) == 'True':
            os.remove("tmp_conf.txt")
        os.mknod("tmp_conf.txt")
        for i in  range(0,len(rs_ip)):
            self._addconftmp(rs_ip[i],self.port)

    def _addconf(self):
        self.get_line_cmd = """ grep -n "^virtual_server\s*%s\s*%s\s" /etc/keepalived/lvs.conf.%s |awk -F: '{print $1}'""" % (self.vip,self.port,self.user)
        try:
            self.line_pro = subprocess.Popen(self.get_line_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            self.line_tmp = int(self.line_pro.stdout.read())
            self.line_pro2 = self.line_tmp+5
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
            self.sed_cmd = """ sed -n '%s,%sp' /etc/keepalived/lvs.conf.%s """ % (self.line_tmp,self.line_pro2,self.user)
            self.sed_pro = subprocess.Popen(self.sed_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if  self.sed_pro.stderr.read():
                print 'add conf fail!!!'
                sys.exit()
            else :
                sed_re = re.findall(r'DR',self.sed_pro.stdout.read())
                if sed_re:
                    self._selfipcheck()                
        except Exception,e:
            print Exception,":",e
            print 'vip or port invalid,please check again!  '
            sys.exit()

    def _delconftmp(self,rsip,port):
        fi=open(self.file2,"r")
        content = fi.read()
        fi.close()

        re_tmp = """^virtual_server\s*%s\s*%s\s""" % (self.vip,self.port)
        pattern = re.compile(re_tmp,re.M)
        v = pattern.findall(content)
        if len(v)==1:
            pass
        else :
            print 'vip or port invalid'
            sys.exit()
        pos1 = content.find(v[0])
        if pos1==-1:
            print "Not find vip and port in the lvs conf,please check again!"
            sys.exit()
        v2 = "virtual_server"
        pos2 = content[pos1:].find(v2,2)
        content_v =  content[pos1:][:pos2]

        re_rs_tmp = """^#\s*real_server\s*%s\s*%s\s""" % (rsip,port)
        pattern2 = re.compile(re_rs_tmp,re.M)
        rs = pattern2.findall(content_v)
        if rs:
            print "please check '#'"+rsip+" in che conf "
            sys.exit()

        re_rs_tmp2 = """real_server\s*%s\s*%s\s""" % (rsip,port)
        pattern3 = re.compile(re_rs_tmp2,re.M)
        rs2 = pattern3.findall(content_v)
        if len(rs2)==1:
            pass
        else :
            print "Not find "+rsip+" in the lvs conf,please check again!"
            sys.exit()
        pos3 = content_v.find(rs2[0])
        if pos3==-1:
            print "Not find "+rsip+" in the lvs conf,please check again!"
            sys.exit()
        rs3 = "real_server"
        pos4 = content_v[pos3:].find(rs3,2)
        content_v2 = content_v[:pos3]+content_v[pos3:][pos4:]
        content = content[:pos1]+content_v2+content[pos1:][pos2:]

        fi=open(self.file2,"wb+")
        fi.write(content.replace('\r\r\n', os.linesep))
        fi.close()

    def _delconf(self):
        rs_ip=self.rsip.split(",")
        for i in  range(0,len(rs_ip)):
            self._delconftmp(rs_ip[i],self.port)
        self._diffconf()

    def _useage(self):
        print  "eg: member_lvs.py -c add -v 1.1.1.1 -r 172.16.1.2,172.16.1.3 -p 80 -u yichi or member_lvs.py -s conf -u yichi"
        print  "-c  add or del"
        print  "-v  vip"
        print  "-r  need to add a new rs in the configuration file ,you can -r ip1,ip2,ip3... "
        print  "-p  port "
        print  "-u  user (Your staffMailbox prefix) "
        print  "-s  save (cp lvs.conf.user to lvs.conf and kill -HUP checkers.pid) "

    def _main(self):
        parser = OptionParser()
        parser.add_option("-c","--control",type="string",dest="control")
        parser.add_option("-v","--vip",type="string",dest="vip")
        parser.add_option("-r","--rsip",type="string",dest="rsip")
        parser.add_option("-p","--port",type="int",dest="port")
        parser.add_option("-u","--user",type="string",dest="user")
        parser.add_option("-s","--save",type="string",dest="save")
        (options, agrgs) = parser.parse_args()
        try:
            self.control  = options.control
            self.vip  = options.vip
            self.rsip = options.rsip
            self.port = options.port
            self.user = options.user
            self.save = options.save

            if str(self.save)=='conf' and str(self.control)=='None' and str(self.vip)=='None' and str(self.rsip)=='None' and str(self.port)=='None' and not str(self.user)=='None' :
                self._save()
            elif str(self.save)=='None' and str(self.control)=='add' and not str(self.vip)=='None' and not str(self.rsip)=='None' and not str(self.port)=='None' and not str(self.user)=='None' :
                self._backup()
                self._conf()
                self._addconf()
            elif str(self.save)=='None' and str(self.control)=='del' and not str(self.vip)=='None' and not str(self.rsip)=='None' and not str(self.port)=='None' and not str(self.user)=='None' :
                self._backup()
                self._delconf()
            else :
                self._useage()

        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    test=lvs()
    test._main()
