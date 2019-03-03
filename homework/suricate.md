Suricata

1. 规则配置
	默认规则配置文件 /etc/suricata/suricata.yaml
	默认规则目录位置 /etc/suricata/rules
	设置HOME_NET与EXTERNAL_NET 推荐HOME_NET填写内网网段
	通过配置文件的default-rule-path设置规则目录,rule-files来选择启用那些规则

2. Suricata规则
	规则行为 协议 源IP 源端口 流量方向 目标IP 目标端口 规则体
	alert  tcp $EXTERNAL_NET $FILE_DATA_PORTS -> $HOME_NET any

	规则行为 根据优先级排列:
		- pass 如果匹配到规则后 suricata会停止扫描数据包 并跳到所有规则的末尾
		- drop ips模式使用 如果匹配到之后则立即阻断数据包不会发送任何信息
		- reject 对数据包主动拒绝 接受者与发送中都会收到一个拒绝包
		- alert 记录所有匹配的规则并记录与匹配规则相关的数据包
	源IP 目标IP
		支持单个IP CIDR IP组[96.30.87.36,96.32.45.57] 所有主机any 以及规则文件中配置的ip变量 $HOME_NET(受保护的ip段)与$EXTERNAL_NET(其他所有ip)
	源端口/目标端口
		支持设置单个端口80 端口组[80,8080] 端口范围[1024:65535] 以及any任意端口 还可以在配置文件中添加端口组 port-groups 通过!号可以进行排除
	流量方向
		-> 单向流量 从源ip到目标ip的单项流量
		<> 双向流量 2个ip往返之间的流量
	规则体
		(msg:"INDICATOR-SHELLCODE heapspray characters detected - ASCII"; flow:to_client,established; file_data; content:"0d0d0d0d";  fast_pattern:only; metadata:service ftp-data, service http, service imap, service pop3; reference:url, sf-freedom.blogspot.com/2006/07/heap-spraying-internet-exploiter.html;  classtype:attempted-user; sid:33339; rev:1;)

		- msg:规则名称 规则中的第一个字段 ids告警上显示的信息
		- 特征标示符sid:用于唯一性规则标识 sid不能重复 0-10000000 VRT保留 20000000-29999999 Emerging保留 30000000+:公用
		- 修订rev:规则版本号 每次修改规则rev则递增1
		- 引用reference:连接外部信息来源 补充描述
		- 优先级 priority: 手动设置规则优先级别 范围1-255 1最高 一般都是1-4 suricata会首先检查优先级较高的规则
		- 类别 classtype:根据规则检测到的活动类型为规则分类  
		- 元数据 Metadata suricata会忽略元数据背后的语句 用于添加备注
		- 内容匹配 content:检测数据包中是否存在此内容
```
如果有多个匹配项可以使用 content:"evilliveshere";content:"here";这种写法,如果没有用内容修饰的话 不会按照先后顺序去匹配的 只会在内容中匹配是否包含这2个值,必须用内容修饰来调整先后顺序 用distance 0来让第二个匹配项在第一个匹配项匹配位置之后匹配。并且如果有多个content他们的关系是and关系必须都匹配到才告警;
使用感叹号！对匹配项的否定:content:!"evilliveshere";
将字符串的十六进制用管道符(|)进行包围:content:"|FF D8|"; 字符串与十六进制混合使用:content:"FF |SMB|25 05 00 00 80";  
匹配内容区分大小写,保留字符(; \ "|)须进行转义或十六进制转码;

内容修饰能够更加精准匹配
	不区分大小写 nocase:content:"root";nocase;#修饰符直接在';'号后面添加;
	
	偏移位置 offset:content:"xss";offset 100;#代表了从数据包开始位置0往后偏移100位字节后进行匹配;
	
	结束位置 depth:content:"xss";offset 100;depth 200;#代表了匹配数据包结束的位置,如果没有offset则是从开始位置计算,有offset则是从offset开始,此次则是从100字节开始匹配到200字节内的内容;
	
	在xx范围外 distance:本次匹配必须在上一次匹配结束位置到distance设置的偏移位置区间之外,例如content:"msg1";content:"msg2";distance 25;如果msg1在第100行找到,那么就会在100+25后匹配msg2; 
	
	在xx范围内 within:本次匹配必须在上一次匹配结束位置之内,如果上次结束是100,within 15;那么第二次匹配必须在100到115之内开始匹配。如果within与distance同时出现,content:"evilliveshere";  content:"here";distance:1;within:7; 则匹配here在  evilliveshere位置结束1-7内匹配;
	
	有效载荷大小 dsize:dsize: >64   用来匹配payload大小,可以用来检测异常包大小;

	pcre正则 pcre:content:"xss"; pcre:"xss\w"   先匹配content内容后才进行匹配pcre正则,这样的话减少系统开销;

	http修饰符:更多详细内容查看:http://suricata.readthedocs.io/en/suricata-4.0.4/rules/http-keywords.html
		alert  tcp any any -> any 80(msg:"Evil Doamin www.appliednsm.com";  "content:"GET"
		httpmethod;   content:"www.appliednsm.com";http_uri; sid:5445555; rev:1;)
		http_client_body    HTTP客户端请求的主体内容
    	http_cookie         HTTP头字段的“Cookie”内容
    	http_header         HTTP请求或响应头的任何内容
    	http_method         客户端使用的HTTP方法（GET,POST等）
    	http_uri            HTTP客户端请求的URI内容
    	http_stat_code      服务器响应的HTTP状态字段内容
    	http_stat_message   服务器响应的HTTP状态消息内容
    	http_encode         在HTTP传输过程中所使用的编码类型
		url_len             url长度

	快速匹配模式:fast_pattern;如果suricata规则中有多个匹配项目,快速匹配的目的是设置优先级最高的匹配项,如果设置了快速匹配模式没有命中则跳过这条规则;
```
		- flow流匹配：
```
flow是特定时间内具有相同数据的数据包（5元组信息）同属于一个流，suricata会将这些流量保存在内存中;
flowbits set, name      设置条件
flowbits isset, name    选择条件
一旦设置flowbits之后，第一条规则没有命中那么第二条规则即使命中了也不会显示出来，例如一些攻击行为的响应信息，现在请求中设置条件，然后在响应中选择条件


to_client/from_server    服务器到客户端
to_server/from_client    客户端到服务器
established       匹配已经建立连接的（tcp则是经过3次握手之后，udp则是有双向流量）
no_established     匹配不属于建立连接的
only_stream    匹配由流引擎重新组装的数据包
no_stream    不匹配流引擎重新组装的数据包
```

