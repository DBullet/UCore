### 6.1	非连续内存分配的需求背景
 1. 为什么要设计非连续内存分配机制？

提高分配的灵活性和利用效率，方便共享，充分利用内存空间

 2. 非连续内存分配中内存分块大小有哪些可能的选择？大小与大小是否可变?

即可以采用段机制按需求分配不定长的内存块，页可采采用页机制分配一定数量的定长的小内存块。对于较大的内存块，便于操作系统管理，而小的内存块更便于灵活地满足应用程序对内存的需求，减少内部碎片的产生。

 3. 为什么在大块时要设计大小可变，而在小块时要设计成固定大小？小块时的固定大小可以提供多种选择吗？

 大小可变的内存块能更加灵活地满足内存需求，减少内部碎片的产生。固定大小的内存块则更便于管理。小块的固定大小可以提供多种选择，但为了方便管理通常有地址对齐的要求。

### 6.2	段式存储管理
 1. 什么是段、段基址和段内偏移？

段表示访问方式和存储数据等属性相同的一段地址空间。段基址是一个段的起始地址。段内偏移是段中某数据的地址偏移段基址的距离。

 2. 段式存储管理机制的地址转换流程是什么？为什么在段式存储管理中，各段的存储位置可以不连续？这种做法有什么好处和麻烦？

段式存储管理中，地址转换是段基址（段号）加段内偏移。段反映了程序的存储逻辑结构，程序不会从一个段的基址去访问另一个段，于是不同的段可以不连续。好处是可以不连续，方便内存管理，而且对不同进程的段能够给予保护。麻烦是地址转换较复杂。


### 6.3	页式存储管理
 1. 什么是页（page）、帧（frame）、页表（page table）、存储管理单元（MMU）、快表（TLB, Translation Lookaside Buffer）和高速缓存（cache）？

页是虚拟内存分配的最小单位。帧是物理内存中的一页。页表是将虚拟地址转换为物理地址的映射表，其一项为虚拟页号所对应的物理页号，以及相应的属性信息。存储管理单元是硬件中完成虚拟地址到物理地址转换的结构。快表是硬件上为了加速地址转换而将一部分页表装入的高速缓存。高速缓存是为了加快访问速度而在CPU和主存之间设立的一种存储结构，其内保存了程序近期访问到的部分内存。


 2. 页式存储管理机制的地址转换流程是什么？为什么在页式存储管理中，各页的存储位置可以不连续？这种做法有什么好处和麻烦？

页式存储管理中，地址转换是页号加页内偏移。CPU使用连续的逻辑地址，存储访问时，逻辑地址先分成逻辑页号和页内偏移，然后通过页表定义的对应关系，把逻辑页面转换成物理页号，最后再把物理页号加页内偏移得到物理地址，所以不同的段可以不连续。

这种做法的好处是内存分配可以不连续，方便内存管理中的存储分配和回收，麻烦是地址转换比较复杂（页表项访问开销和页表存储开销），并且频繁进行（每次存储访问会变成两次或更多）。


### 6.4	页表概述
 1. 每个页表项有些什么内容？有哪些标志位？它们起什么作用？

页表项有虚拟页号，对应的物理页号以及一系列标志位。标志位有有效位，访问位，修改位，权限位。有效位用来指示对应页是否缓存在内存中，访问位和修改位可以作为页面置换算法选择换出页面的依据，权限位则对存储给予了保护，避免进程越权访问。

 2. 页表大小受哪些因素影响？

页大小、地址空间大小、进程数目。

### 6.5	快表和多级页表
 1. 快表（TLB）与高速缓存（cache）有什么不同？

快表是对页表的缓存，而高速缓存是对进程运行的内存进行缓存。

 2. 为什么快表中查找物理地址的速度非常快？它是如何实现的？为什么它的的容量很小？

因为块表的硬件是基于SRAM的cache，存储介质访问速度更快。快表通过将最近访问到的一部分页表内容从主存中加载到cache中，使得在需要访问这些已经被缓存的页表项时不需要访问主存而可以直接在cache中获得需要的页表项。快表的容量限制主要是来自于对功耗和价格的考虑。

 3. 什么是多级页表？多级页表中的地址转换流程是什么？多级页表有什么好处和麻烦？

 多级页表是对一级列表进一步分块索引存储，形成更多层次的物理地址查询结构。多级页表的地址转换首先根据虚拟地址的较高位页索引在高级页表查找到对应下一级页表的物理地址，再到下一级页表中依据虚拟地址中的索引查找，直到确定最终的物理页的物理地址。多级页表减少了存储页表所需要的存储空间，但是增加了地址转换的复杂度。 


### 6.6	反置页表
 1. 页寄存器机制的地址转换流程是什么？

逻辑地址进行hash，然后查相应页寄存器。

 2. 反置页表机制的地址转换流程是什么？

逻辑地址和进程号共同进行hash，然后查相应页寄存器。

 3. 反置页表项有些什么内容？

 PID、逻辑页号、标志位。

### 6.7	段页式存储管理
 1. 段页式存储管理机制的地址转换流程是什么？这种做法有什么好处和麻烦？

对于给出的逻辑地址，根据段寄存器中的内容选择到GDT或LDT中对应的段表中查询虚拟地址所对应的段的基址。查询过程中需要进行地址是否越界的检查。根据段基址和逻辑地址中的段内偏移对段进行访问。这种做法增强了对内存的保护，防止越权访问以及进程对不属于自身的存储空间访问。麻烦是增加了地址转换的复杂度。

 2. 如何实现基于段式存储管理的内存共享？

可以通过对代码的动态链接，实现多道程序以段为单位共享同一代码库。

 3. 如何实现基于页式存储管理的内存共享？

 可以将不同的虚拟地址映射到同一物理地址，采用换出的方式来实现内存的共享。