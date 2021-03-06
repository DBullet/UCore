## 启动、中断、异常和系统调用-思考题

## 3.1 BIOS
-  BIOS从磁盘读入的第一个扇区是是什么内容？为什么没有直接读入操作系统内核映像？

BIOS从硬盘读取的第一个扇区是主引导记录(MBR)，因为BIOS在完成硬件初始化和POST之后，文件系统尚未建立，BIOS不知道要从哪一个磁盘读入操作系统。

- 比较UEFI和BIOS的区别。

UEFI，全称Unified Extensible Firmware Interface，即“统一的可扩展固件接口”, 是适用于电脑的标准固件接口，旨在代替BIOS（基本输入/输出系统）。此标准由UEFI联盟中的140多个技术公司共同创建，其中包括微软公司。UEFI旨在提高软件互操作性和解决BIOS的局限性。

UEFI启动对比BIOS启动的优势有三点：

* 安全性更强：UEFI启动需要一个独立的分区，它将系统启动文件和操作系统本身隔离，可以更好的保护系统的启动。
* 启动配置更灵活：EFI启动和GRUB启动类似，在启动的时候可以调用EFIShell，在此可以加载指定硬件驱动，选择启动文件。比如默认启动失败，在EFIShell加载U盘上的启动文件继续启动系统。
* 支持容量更大:传统的BIOS启动由于MBR的限制，默认是无法引导超过2TB以上的硬盘的。随着硬盘价格的不断走低，2TB以上的硬盘会逐渐普及，因此UEFI启动也是今后主流的启动方式。


## 3.2 系统启动流程

- 分区引导扇区的结束标志是什么？

		最后两个字节为0x55AA。

- 在UEFI中的可信启动有什么作用？

		通过启动前的数字签名检查来保证启动介质的安全性。

## 3.3 中断、异常和系统调用比较
1. 什么是中断、异常和系统调用？

* 中断：外部意外的响应
* 异常：指令执行意外的响应
* 系统调用：系统调用指令的响应；

2.  中断、异常和系统调用的处理流程有什么异同？
* 源头：中断：外设，异常：应用程序中意想不到的行为，系统调用：应用程序请求操作系统服务
* 响应方式：中断：异步，异常：同步，系统调用：同步或异步
* 处理机制：中断：持续，对用户是透明的；异常：杀死进程或重新执行应用程序指令；系统调用：等待和持续；

3. 以ucore lab8的answer为例，uCore的系统调用有哪些？大致的功能分类有哪些？
ucore lab8的answer中共有22个系统调用，大致分为如下几类 {%s%}

* 进程管理：包括 fork/exit/wait/exec/yield/kill/getpid/sleep
* 文件操作：包括 open/close/read/write/seek/fstat/fsync/getcwd/getdirentry/dup
* 内存管理：pgdir命令
* 外设输出：putc命令

## 3.4 linux系统调用分析
-  通过分析[lab1_ex0](https://github.com/chyyuu/ucore_lab/blob/master/related_info/lab1/lab1-ex0.md)了解Linux应用的系统调用编写和含义。(仅实践，不用回答)
- 通过调试[lab1_ex1](https://github.com/chyyuu/ucore_lab/blob/master/related_info/lab1/lab1-ex1.md)了解Linux应用的系统调用执行过程。(仅实践，不用回答)


## 3.5 ucore系统调用分析 （扩展练习，可选）
-  基于实验八的代码分析ucore的系统调用实现，说明指定系统调用的参数和返回值的传递方式和存放位置信息，以及内核中的系统调用功能实现函数。

	在 ucore 中，执行系统调用前，需要将系统调用的参数出存在寄存器中。eax 表示系统调用类型，其余参数依次存在 edx, ecx, ebx, edi, esi 中。


 
## 3.6 请分析函数调用和系统调用的区别
1. 系统调用与函数调用的区别是什么？

* 指令不同
* 特权级不同
* 堆栈切换

2. 通过分析`int`、`iret`、`call`和`ret`的指令准确功能和调用代码，比较函数调用与系统调用的堆栈操作有什么不同？

	执行int指令时，需要保存应用程序现场，即ss和esp压栈，并在执行iret执行返回时将ss和esp弹出，恢复程序执行现场。而函数调用则是执行push %ebp和mov %esp, %ebp两条指令来保存调用者的基地址并保存被调用者的基地址。