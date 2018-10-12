import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import time, datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
_user = "邮箱地址"
_pwd = "邮箱认证密码"
_to  = ["summer@x.com","4768@163.com","arrow@x.com"]




# zabbix数据库信息

zdbhost = '1.1.1.1'
zdbuser = 'xxxx'
zdbpass = 'xxxx'
zdbport = 3306
zdbname = 'xxxx'

d = datetime.datetime.now()
day = datetime.date.today()
keys = {
    'trends_uint': [
        'net.if.in[eth0]',
        'net.if.out[eth0]',
        'vfs.fs.size[/,free]',
        'vm.memory.size[available]',
    ],
    'trends': [
        'system.cpu.load[percpu,avg5]',
        'system.cpu.util[,idle]',
    ],
}





class ReportForm:

    def __init__(self):
        self.conn = pymysql.connect(host=zdbhost, user=zdbuser, passwd=zdbpass, port=zdbport, db=zdbname)
        self.cursor = self.conn.cursor()
        self.groupname = "all"
        self.IpInfoList = self.__getHostList()

    def __getHostList(self):
        sql = '''select groupid from groups where name = '%s' ''' % self.groupname
        self.cursor.execute(sql)
        groupid = self.cursor.fetchone()[0]

        sql = '''select hostid from hosts_groups where groupid = %s''' % groupid
        self.cursor.execute(sql)
        hostlist = self.cursor.fetchall()

        IpInfoList = {}
        for i in hostlist:
            hostid = i[0]
            sql = '''select host from hosts where status = 0 and hostid = %s''' % hostid
            ret = self.cursor.execute(sql)
            if ret:
                IpInfoList[self.cursor.fetchone()[0]] = {'hostid': hostid}
        return IpInfoList

    def __getItemid(self, hostid, itemname):
        sql = '''select itemid from items where hostid = %s and key_ = "%s" ''' % (hostid, itemname)
        if self.cursor.execute(sql):
            itemid = self.cursor.fetchone()[0]
        else:
            itemid = None
        return itemid
        print(itemid)

    def getTrendsValue(self, itemid, start_time, stop_time):
        resultlist = {}
        for type in ['min', 'max', 'avg']:
            sql = '''select %s(value_%s) as result from trends where itemid = %s
            and clock >= %s and clock <= %s''' % (type, type, itemid, start_time, stop_time)
            self.cursor.execute(sql)
            result = self.cursor.fetchone()[0]
            if result == None:
                result = 0
            resultlist[type] = result
        return resultlist

    def getTrends_uintValue(self, itemid, start_time, stop_time):
        resultlist = {}
        for type in ['min', 'max', 'avg']:
            sql = '''select %s(value_%s) as result from trends_uint where itemid = %s
            and clock >= %s and clock <= %s''' % (type, type, itemid, start_time, stop_time)
            self.cursor.execute(sql)
            result = self.cursor.fetchone()[0]
            if result:
                resultlist[type] = int(result)
            else:
                resultlist[type] = 0
        return resultlist



    def get_week(self, d):
       # dayscount = datetime.timedelta(days=d.isoweekday())
       # dayto = d - dayscount
        dayto=d
        sixdays = datetime.timedelta(days=6)
        dayfrom = dayto - sixdays
        date_from = datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0)
        date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59)
        ts_first = int(time.mktime(datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0).timetuple()))
        ts_last = int(time.mktime(datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59).timetuple()))
        return ts_first, ts_last

    def getLastMonthData(self, hostid, table, itemname):
        ts_first = self.get_week(d)[0]
        ts_last = self.get_week(d)[1]
        itemid = self.__getItemid(hostid, itemname)
        # function = getattr(self, 'get %s Value' % table.capitalize())
        function = getattr(self, 'get%sValue' % table.capitalize())
        return function(itemid, ts_first, ts_last)

    def getinfo(self):
        for ip, resultdict in zabbix.IpInfoList.items():
            print("正在查询 IP:%-15s hostid:%5d 的信息！" % (ip, resultdict['hostid']))
            for table, keylists in keys.items():
                for key in keylists:
                    print("\t正在统计 key_:%s" % key)
                    data = zabbix.getLastMonthData(resultdict['hostid'], table, key)
                    zabbix.IpInfoList[ip][key] = data

    def writeToXls(self):
       # dayscount = datetime.timedelta(days=d.isoweekday())
       # dayto = d - dayscount
        dayto = d
        sixdays = datetime.timedelta(days=6)
        dayfrom = dayto - sixdays
        date_from = datetime.date(dayfrom.year, dayfrom.month, dayfrom.day)
        date_to = datetime.date(dayto.year, dayto.month, dayto.day)
        '''生成xls文件'''
        try:
            import xlsxwriter
            # 创建文件
            workbook = xlsxwriter.Workbook('/usr/monitor/week/weekreport.xlsx')
            # 创建工作薄
            worksheet = workbook.add_worksheet()
            top=workbook.add_format({'align':'center','bg_color':'#008000','font_size':10,'bold':True})
            # 写标题（第一行）
            i = 0
            for value in ["主机", "CPU avg空闲值", "CPU min空闲值", "可用avg内存(单位M)", "可用min内存(单位M)", "磁盘剩余量(单位G)","CPU5分钟负载", "Incoming max流量（单位Mbps）",
                          "Incoming avg流量（单位Mbps）", "Outgoing max流量（单位Mbps）", "Outgoing avg流量（单位Mbps）"]:
                worksheet.write(0, i, value,top)
                i = i + 1
            # 写入内容：
            j = 1
            for ip, value in self.IpInfoList.items():
                worksheet.write(j, 0, ip)
                worksheet.write(j, 1, '%.2f' % value['system.cpu.util[,idle]']['avg'])
                worksheet.write(j, 2, '%.2f' % value['system.cpu.util[,idle]']['min'])
                worksheet.write(j, 3, '%dM' % int(value['vm.memory.size[available]']['avg'] / 1024 / 1024))
                worksheet.write(j, 4, '%dM' % int(value['vm.memory.size[available]']['min'] / 1024 / 1024))
                worksheet.write(j, 5, '%dG' % int(value['vfs.fs.size[/,free]']['avg'] / 1024 / 1024 / 1024))
                worksheet.write(j, 6, '%.2f' % value['system.cpu.load[percpu,avg5]']['avg'])
                worksheet.write(j, 7, value['net.if.in[eth0]']['max'] / 1000 / 1000)
                worksheet.write(j, 8, value['net.if.in[eth0]']['avg'] / 1000 / 1000)
                worksheet.write(j, 9, value['net.if.out[eth0]']['max'] / 1000 / 1000)
                worksheet.write(j, 10, value['net.if.out[eth0]']['avg'] / 1000 / 1000)
                j = j + 1
            workbook.close()
        except Exception as e:
            print(e)
    def __del__(self):
        '''关闭数据库连接'''
        self.cursor.close()
        self.conn.close()



    def S_mail(self):
        msg = MIMEMultipart()
        msg["Subject"] = "懒猪行服务器巡检周报"
        msg["From"]  = _user
        msg["To"]   = ",".join(_to)


        #---这是附件部分---
        #xlsx类型附件
        part = MIMEApplication(open('/usr/monitor/week/weekreport.xlsx','rb').read())
        part.add_header('Content-Disposition', 'attachment', filename="weekreport.xlsx")
        msg.attach(part)

        s = smtplib.SMTP("smtp.263.net",587)#连接smtp邮件服务器,端口默认是25
        s.login(_user, _pwd)#登陆服务器
        s.sendmail(_user, _to, msg.as_string())#发送邮件
        s.close()    





if __name__ == "__main__":
    zabbix = ReportForm()
    zabbix.getinfo()
    zabbix.writeToXls()
    zabbix.S_mail()
