# 得到15分钟内的系统负载
#load_15=`uptime | awk '{print $NF}'`
#`echo $load_15

# 把user、system的使用率相加
a=(`cat /proc/stat | grep -E "cpu\b" | awk -v total=0 '{$1="";for(i=2;i<=NF;i++){total+=$i};used=$2+$3 }END{print total,used}'`)
sleep 3
#b=(`cat /proc/stat | grep -E "cpu\b" | awk -v total=0 '{$1="";for(i=2;i<=NF;i++){total+=$i};used=$2+$3 }END{print total,used}'`)
#cpu_usage=$(((${b[1]}-${a[1]})*10/(${b[0]}-${a[0]})))
echo ${a[0]}
echo ${a[1]}

# 读取/proc/meminfo文件，MemTotal – MemFree得到MEM使用率
mem_use_rate=`awk '/MemTotal/{total=$2}/MemFree/{free=$2}END{print (total-free)/total}'  /proc/meminfo`
echo $mem_use_rate

#获得硬盘总的大小与剩余空间大小
all_disk_space=`df -hl | grep /dev | awk '{print $2}'`
free_disk_space=`df -hl | grep /dev | awk '{print $5}'`
echo $all_disk_space
echo $free_disk_space

# 读取/proc/meminfo文件，MemTotal – MemFree得到MEM使用總量(MB)
awk '/MemTotal/{total=$2}/MemFree/{free=$2}END{print (total)/1024}'  /proc/meminfo

# 读取/proc/net/dev文件，得到每秒的平均流量 (B/S)
traffic_be=(`awk -F'[: ]+' 'BEGIN{ORS=" "}/'$1'/{print $3,$10}' /proc/net/dev`)
sleep 3
traffic_af=(`awk -F'[: ]+' 'BEGIN{ORS=" "}/'$1'/{print $3,$10}' /proc/net/dev`)
eth0_in=$(((${traffic_af[0]}-${traffic_be[0]})/3))
eth0_out=$(((${traffic_af[1]}-${traffic_be[1]})/3))
echo $eth0_in
echo $eth0_out

# 读取/proc/meminfo文件，(MemTotal – MemFree – Buffers – Cached)/1024得到应用程序使用内存数
# awk '/MemTotal/{total=$2}/MemFree/{free=$2}/Buffers/{buffers=$2}/^Cached/{cached=$2}END{print (total-free-buffers-cached)/1024}'  /proc/meminfo

# 通过/proc/meminfo文件，SwapTotal – SwapFree得到SWAP使用大小(MB)
# awk '/SwapTotal/{total=$2}/SwapFree/{free=$2}END{print (total-free)/1024}'  /proc/meminfo

# 平均每秒把数据从硬盘读到物理内存的数据量
a=`awk '/pgpgin/{print $2}' /proc/vmstat`
sleep 3
b=`awk '/pgpgin/{print $2}' /proc/vmstat`
ioin=$(((b-a)/3))
echo $ioin

# 平均每秒把数据从物理内存写到硬盘的数据量
a=`awk '/pgpgout/{print $2}' /proc/vmstat`
sleep 3
b=`awk '/pgpgout/{print $2}' /proc/vmstat`
ioout=$(((b-a)/3))
echo $ioout

