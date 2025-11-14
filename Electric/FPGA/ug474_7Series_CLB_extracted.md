--- Page 1 ---
7 Series FPGAs 
Configurable Logic Block
User Guide
UG474 (v1.7) November 17, 2014

--- Page 2 ---
7 Series FPGAs CLB User Guide www.xilinx.com UG474 (v1.7) November 17, 2014DISCLAIMER
The information disclosed to you hereunder (the “Materials”) is provided solely for the selection and use of Xilinx products. T o the maximum 
extent permitted by applicable law: (1) Materials are made avai lable "AS IS" and with all faults, Xilinx hereby DISCLAIMS ALL W ARRANTIES 
AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and (2) Xilinx shall not be liable (whether in contract or tort, including  
negligence, or under any other theory of liability) for any loss or  damage of any kind or nature related to, arising under, or in connection with, 
the Materials (including your use of the Materials), including for any direct, indirect, special, incidental, or consequential loss or damage 
(including loss of data, profits, goodwill, or any type of loss or damage suffered as a result of any action brought by a third  party) even if such 
damage or loss was reasonably foreseeable or Xilinx had been ad vised of the possibility of the same. Xilinx assumes no obligati on to correct 
any errors contained in the Materials or to notify you of updates to the Materials or to product specifications. You may not re produce, 
modify, distribute, or publicly display the Materials without prior written consent. Certain products are subject to the terms and conditions 
of Xilinx’s limited warranty, please refer to Xilinx’s Terms of Sale which can be viewed at http://www.xilinx.com/legal.htm#tos ; IP cores may be 
subject to warranty and support terms contained in a license issued to you by Xilinx. Xilinx products are not designed or inten ded to be fail-
safe or for use in any application requiring fail-safe performanc e; you assume sole risk and liability for use of Xilinx produc ts in such critical 
applications, please refer to Xilinx’s Te rms of Sale which can be viewed at http://www.xilinx.com/legal.htm#tos .
Automotive Applications Disclaimer
XILINX PRODUCTS ARE NOT DESIGNED OR INTENDED TO BE FAIL-SAFE, OR FOR USE IN ANY APPLICATION REQUIRING FAIL-SAFE PERFORMANCE, SUCH AS APPLICATIONS RELATED TO: (I) THE DEPLOYME NT OF AIRBAGS, (II) CONTROL OF A VEHICLE, UNLESS THERE IS A 
FAIL-SAFE OR REDUNDANCY FEATURE (WHICH DOES NOT INCLUDE USE OF SOFTWARE IN THE XILINX DEVICE TO IMPLEMENT THE 
REDUNDANCY) AND A WARNING SIGNAL UPON FAILURE TO THE OPERATOR, OR (III) USES THAT COULD LEAD TO DEATH OR PERSONAL 
INJURY. CUSTOMER ASSUMES THE SOLE RISK AND LIABILITY OF ANY USE OF XILINX PRODUCTS IN SUCH APPLICATIONS. 
© Copyright 2011–2014 Xilinx, Inc. Xilinx, the Xilinx logo, Artix, ISE, Kintex, Spartan, Virtex, Vivado, Zynq, and other design ated brands 
included herein are trademarks of Xilinx in the United States an d other countries. All other trademarks are the property of the ir respective 
owners.
Revision History
The following table shows the revision history for this document.
Date Version Revision
03/01/2011 1.0 Xilinx Initial release.
03/28/2011 1.1 Added devices XC7K355T, XC7K420T, and XC7K480T to Table 1-2 . Portions of the text 
have been revised for clarity.
09/30/2011 1.2 Added last sentence under 7 Series CLB Features . Added Table 1-2  and Table 1-3 . 
Updated CLB features in Table 1-2 . Added first sentence under CLB Arrangement , 
added ASMBL Architecture  section, and CLB Slices  heading. Added last paragraph 
under Carry Logic . Added lasts sentence under Using Carry Logic . Added second 
sentence under Slice Multiplexer Timing Parameters . Modified Table 5-2 , Table 5-4 , and 
Table 5-5  for clarity. Added Devices Using Stacked Silicon Interconnect (SSI) Technology  
section.
01/30/2012 1.3 Revised Table 1-1 . Added fifth paragraph under Distributed RAM (Available in SLICEM 
Only) . Clarified last paragraph under Global Controls GSR and GTS .
11/05/2012 1.4 Changed “uniformity” to  “optimized” in last bullet under 7 Series CLB Features . 
Changed “unified” to “scalable ” in first sentence under Device Resources . Deleted 
7A350T device from Table 1-1 . Deleted 7V1500T and 7VH290T devices from Table 1-3 . 
Added reference to 7 Series FPGA Libraries Guide to Distributed RAM (Available in 
SLICEM Only) , Shift Registers (Available in SLICEM Only) , and Flip-Flop Primitives . 
Changed “TCEO” to “TCECK ” in Figure 5-2  and first bullet under General Timing 
Characteristics .

--- Page 3 ---
UG474 (v1.7) November 17, 2014 www.xilinx.com 7 Series FPGAs CLB User Guide08/6/2013 1.5 Added Artix®-7 devices. Update d references to implementation tools.
08/11/2014 1.6 Revised footnotes in Table 1-1  through Table 1-3 . Revised polarity from independent  to 
programmable  in Control Signals, page 22 . Added Primitive column to Table 2-3  and 
removed footnotes. Renamed or made minor revisions to Figure 2-6  through Figure 2-14 . 
Revised sections Clock – WCLK, page 49 , Clock – CLK, page 50 , and Clock - C, page 51 .
11/17/2014 1.7 Updated Table 1-1  for new Artix 7A15T device.Date Version Revision

--- Page 4 ---
7 Series FPGAs CLB User Guide www.xilinx.com UG474 (v1.7) November 17, 2014

--- Page 5 ---
7 Series FPGAs CLB User Guide www.xilinx.com 5
UG474 (v1.7) November 17, 2014Revision History  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  2
Preface:  About This Guide
Guide Contents  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  7
Additional Support Resources . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  8
Chapter 1:  Overview
CLB Overview  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  9
7 Series CLB Features  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  10
Device Resources  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  10
Recommended Design Flow . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  12
Pinout Planning . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  12
Chapter 2:  Functional Details
CLB Arrangement . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  15
Slice Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  18
Look-Up Table (LUT)  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  21
Storage Elements . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  21
Distributed RAM (Available in SLICEM Only)  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  23
Shift Registers (Available in SLICEM Only) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  34
Multiplexers  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3 9
Carry Logic  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  43
Chapter 3:  Design Entry
Design Checklist . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  45
Using the CLB Resources . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  46
Primitives . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  . . .  46
Chapter 4:  Applications
Distributed RAM Applications . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  53
Shift Register Applications . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  53
Carry Logic Applications . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  55
Chapter 5:  Timing
CLB General Slice Timing Model and Parameters . . . . . . . . . . . . . . . . . . . . . . . . . . . .  58
CLB Slice Multiplexer Timing Model and Parameters . . . . . . . . . . . . . . . . . . . . . . . .  60
CLB Slice Carry-Chain Timing Model and Parameters  . . . . . . . . . . . . . . . . . . . . . . .  61Table of Contents
Send Feedback

--- Page 6 ---
6 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014CLB Slice Distributed RAM Timing Model and Parameters 
(Available in SLICEM Only)  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  63
CLB Slice SRL Shift Register Timing Model and Parameters 
(Available in SLICEM Only)  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  66
Chapter 6:  Advanced Topics
Using the Latch Function as Logic  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  71
Interconnect Resources . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  72
Devices Using Stacked Silicon Interconnect (SSI) Technology  . . . . . . . . . . . . . . .  73
Send Feedback

--- Page 7 ---
7 Series FPGAs CLB User Guide www.xilinx.com 7
UG474 (v1.7) November 17, 2014Preface
About This Guide
Xilinx® 7 series FPGAs include three FPGA families that are all designed for lowest power 
to enable a common design to scale across fa milies for optimal powe r, performance, and 
cost. The Artix®-7 family is optimized for lo west cost and absolute power for the highest 
volume applications. The Virtex®-7 family is  optimized for highest system performance 
and capacity. The Kintex®-7 fami ly is an innovative class of FPGAs optimized for the best 
price-performance. This guide serves as a tec hnical reference describing the 7 series FPGAs 
configurable logic blocks (CLBs).
Usually, logic synthesis assigns the CLB resources without system designer intervention. It 
can be advantageous for the designer to understand certain CLB details, including the varying capabilities of the look-up tables (LUTs), the physical direction of the carry 
propagation, the number and distribution of th e available flip-flops, and the availability of 
the very efficient shift registers. This guide describes these and other features of the CLB in detail.
This 7 Series FPGAs Configurable Logic Block User Guide , part of an overall set of 
documentation on the 7 series FPGAs, is available on the Xilinx 
7 Series documentation 
website .
Guide Contents
This manual contains these chapters:
Chapter 1, Overview , provides basic information needed for the majority of users, 
including:
CLB Overview  is targeted at the new user.
7 Series CLB Features  discusses what is new compared with the Spartan®-6 and 
Virtex®-6 FPGA families for the experienced user and provides design migration considerations.
Device Resources  indicates the number of resources per device, and unity 
between different 7 series families.
Recommended Design Flow  provides the basics of using CLB resources and lists 
key aspects to consider.
Pinout Planning  discusses aspects of CLBs that might affect pin placement for a 
design.
Chapter 2, Functional Details , lists architectural specifics for each CLB feature.
Chapter 3, Design Entry , provides design entry guidelines and primitives for 
instantiation.
Chapter 4, Applications , provides examples that use the CLB resources in larger 
applications.
Send Feedback

--- Page 8 ---
8 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Preface: About This Guide
Chapter 5, Timing , contains timing models and de fines CLB timing specifications 
from the respective 7 series FPGA data sheet.
Chapter 6, Advanced Topics , discusses advanced features of the 7 series CLB.
Additional Support Resources
To find additional documentatio n, see the Xilinx website at:
www.xilinx.com/support/documentation/inde x
To search the Answer Database of silicon, software, and IP questions and answers, or to 
create a technical support WebCase, see the Xilinx website at:
www.xilinx.com/suppor t
Send Feedback

--- Page 9 ---
7 Series FPGAs CLB User Guide www.xilinx.com 9
UG474 (v1.7) November 17, 2014Chapter 1
Overview
CLB Overview
The 7 series configurable logic block (CLB) provides advanced, high-performance FPGA 
logic:
 Real 6-input look-up table (LUT) technology
 Dual LUT5 (5-input LUT) option
 Distributed Memory and Shift Register Logic capability
 Dedicated high-speed carry logic for arithmetic functions Wide multiplexers for efficient utilization
CLBs are the main logic resources for implementing sequential as well as combinatorial 
circuits. Each CLB element is co nnected to a switch matrix for access to the general routing 
matrix (shown in Figure 1-1 ). A CLB element contains a pair of slices.
The LUTs in 7 series FPGAs can be configured as either a 6-input LUT with one output, or 
as two 5-input LUTs with separate outputs but common addresses or logic inputs. Each 
5-input LUT output can optionally be registered in a flip-flop. Four such 6-input LUTs and their eight flip-flops as well as multiplexers and arithmetic carry logic form a slice, and two 
slices form a CLB. Four flip-flops per slice (o ne per LUT) can optionally be configured as 
latches. In that case, the remaining four flip-flops in that slice must remain unused.X-Ref Target - Figure 1-1
Figure 1-1: Arrangement of Slices within the CLBSwitch
MatrixSlice(1)COUT COUT
CIN CINSlice(0)CLB
UG474_c1_01_071910
Send Feedback

--- Page 10 ---
10 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 1: Overview
Approximately two-thirds of the slices are SLICEL logic slices and the rest are SLICEM, 
which can also use their LUTs as distributed 64 -bit RAM or as 32-bit shift registers (SRL32) 
or as two SRL16s. Modern synthesis tools take  advantage of these highly efficient logic, 
arithmetic, and memory features. Expert  designers can also instantiate them.
7 Series CLB Features
The 7 series CLB is identical to that in the Virtex®-6 FPGA family. The CLB is very similar 
to that of the Spartan®-6 FPGA family with these differences:
 Columnar architecture 
 Scales easily to higher densities
 More routing between CLBs
 SLICEL and SLICEM only (no Spartan-6 FPGA SLICEX)
 All slices support carry logic
 More optimized
The common features in the CLB structure simp lify design migration from the Spartan-6 
and Virtex-6 families to the 7 series devices. The unique floorplan means that location constraints should be removed before implementing designs originally targeted to earlier FPGAs. The interconnect routing resources are increased in size, quantity, and flexibility relative to the Virtex-6 FPGA family, improv ing the quality of automatic place and route 
results.
Device Resources
The CLB resources are scalable across all the 7 series families, providing a common architecture that improves efficiency, IP implementation, and design migration. The 
number of CLBs and the ratio between CLBs an d other device resources differentiates the 
7 series families. Migration between the 7 series families does not require any design changes for the CLBs.
Device capacity is often measured in terms of logic cells, which are the logical equivalent of 
a classic four-input LUT and a flip-flop. The 7 series FPGA CLB six-input LUT, abundant 
flip-flops and latches, carry logic, and the ability to create distributed RAM or shift 
registers in the SLICEM, increase the effectiv e capacity. The ratio between the number of 
logic cells and 6-input LUTs is 1.6:1. 
7Series FPGA CLB Resources
Table 1-1  through Table 1-3  show the available CLB resource s for the Artix®-7, Kintex®-7, 
and Virtex®-7 FPGAs. Refer to DS180 , 7 Series FPGAs Overview  for the most up-to-date 
information.
Table 1-1: Artix-7 FPGA CLB Resources
Device Slices(1)SLICEL SLICEM6-input 
LUTsDistributed RAM 
(Kb)Shift 
Register 
(Kb)Flip-Flops
7A15T 2,600(2)1,800 800 10,400 200 100 20,800
7A35T 5,200(2)3,600 1,600 20,800 400 200 41,600
Send Feedback

--- Page 11 ---
7 Series FPGAs CLB User Guide www.xilinx.com 11
UG474 (v1.7) November 17, 2014Device Resources
7A50T 8,150 5,750 2,400 32,600 600 300 65,200
7A75T 11,800(2)8,232 3,568 47,200 892 446 94,400
7A100T 15,850 11,100 4,750 63,400 1,188 594 126,800
7A200T 33,650 22,100 11,550 134,600 2,888 1,444 269,200
Notes: 
1. Each 7 series FPGA slice contains four LUTs and eight flip-flop s; only SLICEMs can use their LUTs as distributed RAM or SRLs.
2. Number of slices correspondin g to the number of LUTs and fl ip-flops supported in the device.Table 1-1: Artix-7 FPGA CLB Resources (Cont’d)
Device Slices(1)SLICEL SLICEM6-input 
LUTsDistributed RAM 
(Kb)Shift 
Register 
(Kb)Flip-Flops
Table 1-2: Kintex-7 FPGA CLB Resources
Device Slices(1)SLICEL SLICEM6-input 
LUTsDistributed RAM 
(Kb)Shift 
Register 
(Kb)Flip-Flops
7K70T 10,250 6,900 3,350 41,000 838 419 82,000
7K160T 25,350 16,600 8,750 101,400 2,188 1,094 202,800
7K325T 50,950 34,950 16,000 203,800 4,000 2,000 407,600
7K355T 55,650 35,300 20,350 222,600 5,088 2,544 445,200
7K410T 63,550 40,900 22,650 254,200 5,663 2,831 508,4007K420T 65,150
(2)41,400 23,750 260,600 5,938 2,969 521,200
7K480T 74,650 47,500 27,150 298,600 6,788 3,394 597,200
Notes: 
1. Each 7 series FPGA slice contains four LUTs and eight flip-flop s; only SLICEMs can use their LUTs as distributed RAM or SRLs.
2. Number of slices correspondin g to the number of LUTs and fl ip-flops supported in the device.
Table 1-3: Virtex-7 FPGA CLB Resources
Device Slices(1)SLICEL SLICEM6-input 
LUTsDistributed RAM 
(Kb)Shift 
Register 
(Kb)Flip-Flops
7V585T 91,050 63,300 27,750 364,200 6,938 3,469 728,400
7V2000T 305,400 219,200 86,200 1,221,600 21,550 10,775 2,443,200
7VX330T 51,000 33,450 17,550 204,000 4,388 2,194 408,000
7VX415T 64,400 38,300 26,100 257,600 6,525 3,263 515,2007VX485T 75,900 43,200 32,700 303,600 8,175 4,088 607,200
7VX550T 86,600
(2)51,700 34,900 346,400 8,725 4,363 692,800
7VX690T 108,300 64,750 43,550 433,200 10,888 5,444 866,4007VX980T 153,000 97,650 55,350 612,000 13,838 6,919 1,224,000
7VX1140T 178,000 107,200 70,800 712,000 17,700 8,850 1,424,000
Send Feedback

--- Page 12 ---
12 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 1: Overview
Recommended Design Flow
CLB resources are inferred for generic design logic and do not require instantiation. Good 
HDL design is sufficient. A few items to note:
 CLB flip-flops have either a set or a reset. The designer must not use both set and 
reset.
 Flip-flops are abundant. Pipe lining should be considered to improve performance. 
 Control inputs are shared across a slice or CLB. The number of unique control inputs 
required for a design should be minimized. Control inputs include clock, clock enable, set/reset, and write enable.
 A 6-input LUT can be used as a 32-bit sh ift register for effi cient implementation. 
 A 6-input LUT can be used as a 64 x 1 memory for small storage requirements.
 Dedicated carry logic implements arithmetic functions effectively.
These steps indicate the recommended design flow:1. Implement the design using preferred methodologies (HDL, IP , etc.).
2. Evaluate utilization reports to determine resources used.
Check to make sure arithmetic logic, distributed RAM, and SRL are used, when 
helpful.
3. Consider flip-flop usage.
a. Pipeline for performanceb. Use dedicated flip-flops at the outputs of dedicated resources (block RAM, DSP)
c. Allow shift registers to use SRL (avoid set/resets)
4. Minimize the use of set/resets.
Pinout Planning
Although the use of most resources affects the resulting device pinout, CLB usage has little 
effect on pinouts because they are distri buted throughout the device. The ASMBL™ 
architecture provides maximum flexibility with CLBs on both sides of most I/Os. 
The best approach is to let the tools ch oose the I/O locations based on the FPGA 
requirements. Results can be adjusted if ne cessary for board layout considerations. The 
timing constraints should be set so that the tools can choose optimal placement for the 
design requirements.7VH580T 90,700 55,300 35,400 362,800 8,850 4,425 725,600
7VH870T 136,900 83,750 53,150 547,600 13,275 6,638 1,095,200
Notes: 
1. Each 7 series FPGA slice contains four LUTs and eight flip-flop s; only SLICEMs can use their LUTs as distributed RAM or SRLs.
2. Number of slices correspondin g to the number of LUTs and fl ip-flops supported in the device.Table 1-3: Virtex-7 FPGA CLB Resources (Cont’d)
Device Slices(1)SLICEL SLICEM6-input 
LUTsDistributed RAM 
(Kb)Shift 
Register 
(Kb)Flip-Flops
Send Feedback

--- Page 13 ---
7 Series FPGAs CLB User Guide www.xilinx.com 13
UG474 (v1.7) November 17, 2014Pinout Planning
Carry logic cascades vertically up a column , so wide arithmetic buses might drive a 
vertical orientation to other logic, including I/O.
While most 7 series devices are av ailable in flip-chip packages, taking full advantage of the 
distributed I/O in the ASMBL architecture, th e smaller devices are available in wire-bond 
packages at a lower cost. In these packages, so me pins are naturally closer to the I/Os and 
special resources than others, so pin placement should be done after the internal logic is defined.
Send Feedback

--- Page 14 ---
14 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 1: Overview
Send Feedback

--- Page 15 ---
7 Series FPGAs CLB User Guide www.xilinx.com 15
UG474 (v1.7) November 17, 2014Chapter 2
Functional Details
This chapter provides a detailed view of the 7 series FPGAs CLB architecture. These details 
can be useful for design optimi zation and verification, but are not necessary for initiating 
a design. This chapter includes:
CLB Arrangement
Overview of slice locations and features within the CLB
Slice Description
Complete details of SLICEM and SLICEL
Look-Up Table (LUT)
Description of the logical function generators
Storage Elements
Description and controls for the latches and flip-flops
Distributed RAM (Available in SLICEM Only)
SLICEM ability to use LUTs as writable memory
Shift Registers (Available in SLICEM Only)
SLICEM ability to use LUTs as shift registers
Multiplexers
Dedicated gates for combining LUTs into wide functions
Carry Logic
Dedicated gates and cascading to impl ement efficient arithmetic functions
CLB Arrangement
The CLBs are arranged in columns in the 7 series FPGAs. The 7 series is the fourth 
generation to be based on the unique co lumnar approach provided by the ASMBL™ 
architecture.
ASMBL Architecture
Xilinx created the Advanced Silicon Modular Block (ASMBL) architecture to enable FPGA 
platforms with varying feature mixes opti mized for different application domains. 
Through this innovation Xilinx offers a greate r selection of devices, enabling customers to 
select the FPGA with the right mix of features  and capabilities for their specific design. 
Figure 2-1  provides a high-level description of  the different types of column-based 
resources.
Send Feedback

--- Page 16 ---
16 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
The ASMBL architecture breaks through traditional design barriers by:
 Eliminating geometric layout constraints such as dependencies between I/O count 
and array size.
 Enhancing on-chip power and ground distribu tion by allowing power and ground to 
be placed anywhere on the chip.
 Allowing disparate integrated IP blocks to  be scaled independent of each other and 
surrounding resources.
SSI Technology
The 7 series FPGAs extend integration even higher by using the unique stacked silicon 
interconnect (SSI) technology. SSI technology enables multiple super logic regions (SLRs) 
to be combined on a passive interposer layer, to create a single FPGA with more than ten thousand inter-SLR connections. See Chapter 6, Advanced Topics  for additional 
information.
CLB Slices
A CLB element contains a pair of slices, and ea ch slice is composed of four 6-input LUTs 
and eight storage elements.
 SLICE(0) – slice at the bottom of the CLB and in the left column
 SLICE(1) – slice at the top of the CLB and in the right column
These two slices do not have direct connections to each other, and each slice is organized as 
a column. Each slice in a column has an independent carry chain. X-Ref Target - Figure 2-1
Figure 2-1: ASMBL ArchitectureColumn
Based
ASMBL
Architect ureFeature Option s
Domain A Dom ain B Dom ain C
UG474_c2_24_071014Applic ations Applic ations Applic ationsLogic (SLICEL)
Logic (SLICEM)
DSP
MemoryClock M anagement TileGlobal Clock
High-perform ance I/O
High-r ange I/O
Integr ated IP
Mixed Sign al
Transceiver s
Send Feedback

--- Page 17 ---
7 Series FPGAs CLB User Guide www.xilinx.com 17
UG474 (v1.7) November 17, 2014CLB Arrangement
The Xilinx tools designate slices with these definitions:
 An “X” followed by a number identifies the position of each slice in a pair as well as 
the column position of the slice. The “X” number counts slices starting from the 
bottom in sequence 0, 1 (the  first CLB column); 2, 3 (the  second CLB column); etc. 
 A “Y” followed by a number identifies a row of slices. The number remains the same 
within a CLB, but counts up in sequence  from one CLB row to the next CLB row, 
starting from the bottom. 
Figure 2-2  shows four CLBs located in th e bottom-left corner of the die.
CLB/ Slice Configurations
Table 2-1  summarizes the logic resources in one C LB. Each SLICEM LUT can be configured 
as a look-up table, distribute d RAM, or a shift register.X-Ref Target - Figure 2-2
Figure 2-2: Row and Column Relationship  between CLBs and SlicesSlice1
X1Y1COUT COUT
CIN CINSlice0
X0Y1CLB
UG474_c2_01_092210Slice1
X1Y0COUT COUT
Slice0
X0Y0CLBSlice1
X3Y1COUT COUT
CIN CINSlice0
X2Y1CLB
Slice1
X3Y0COUT COUT
Slice0
X2Y0CLB
Table 2-1: Logic Resources in One CLB
Slices LUTs Flip-FlopsArithmetic and 
Carry ChainsDistributed RAM(1)Shift Registers(1)
2 8 16 2 256 bits 128 bits
Notes: 
1. SLICEM only, SLICEL does not have distributed RAM or shift registers.
Send Feedback

--- Page 18 ---
18 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
Slice Description
Every slice contains:
 Four logic-function genera tors (or look-up tables)
 Eight storage elements
 Wide-function multiplexers
 Carry logic
These elements are used by all slices to prov ide logic, arithmetic, and ROM functions. In 
addition, some slices support two additional  functions: storing data using distributed 
RAM and shifting data with 32-bit registers. Slices that support these additional functions are called SLICEM; others are called SLICEL. SLICEM (shown in Figure 2-3 ) represents a 
superset of elements and connections found in all slices. SLICEL is shown in Figure 2-4 . 
Each CLB can contain two SLICEL or a SLICEL and a SLICEM.
Send Feedback

--- Page 19 ---
7 Series FPGAs CLB User Guide www.xilinx.com 19
UG474 (v1.7) November 17, 2014Slice Description
X-Ref Target - Figure 2- 3
Figure 2-3: Diagram of SLICEMA6:A1D
COUT
D
DX
C
CX
B
BX
A
AXO6DI2
O5
DI1
MC31 WENCK
DI1
MC31 WENCK
DI1
MC31 WENCK
DI1
MC31 WENCK
UG474_c2_02_110510DXDMUX
D
DQ
C
CQCMUX
B
BQBMUX
A
AQAMUXReset Type
DFF/LAT
INIT1INIT0SRHISRLO
SRCE
CK
FF/LAT
INIT1INIT0SRHISRLO
FF/LAT
INIT1INIT0SRHISRLO
FF/LAT
INIT1INIT0SRHISRLOD
SRCE
CK
D
SRCE
CK
D
SRQ
CE
CK
CIN0/1
WENWECKSync/A sync
FF/LAT
A6:A1
O6
O5C6:1CXD6:1
DI
A6:A1
O6
O5B6:1BX
A6:A1
W6:W1W6:W1W6:W1W6:W1
O6
O5A6:1AX
SR
CE
CLKCEQ
CKSR
QQQSRHI
SRLOINIT1INIT0
D
CEQ
CKSRSRHI
SRLOINIT1INIT0
D
CE Q
CKSRSRHI
SRLOINIT1INIT0
D
CE Q
CKSRSRHI
SRLOINIT1INIT0DI2
DI2
DI2CI
BI
AI
Send Feedback

--- Page 20 ---
20 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
X-Ref Target - Figure 2-4
Figure 2-4: Diagram of SLICELA6:A1DCOUT
D
DX
C
CX
B
BX
A
AXO6
O5
UG474_c2_03_101210DXDMUX
D
DQ
C
CQCMUX
B
BQBMUX
A
AQAMUXReset Type
DFF/LAT
INIT1INIT0SRHISRLO
SRCE
CK
FF/LAT
INIT1INIT0SRHISRLO
FF/LAT
INIT1INIT0SRHISRLO
FF/LAT
INIT1INIT0SRHISRLOD
SRCE
CK
D
SRCE
CK
D
SRQ
CE
CK
CIN0/1Sync/A sync
FF/LAT
A6:A1
O6
O5C6:1CXD6:1
A6:A1
O6
O5B6:1BX
A6:A1
O6
O5A6:1AX
SR
CE
CLKCEQ
CKSR
QQQSRHI
SRLOINIT1INIT0
D
CEQ
CKSRSRHI
SRLOINIT1INIT0
D
CE Q
CKSRSRHI
SRLOINIT1INIT0
D
CE Q
CKSRSRHI
SRLOINIT1INIT0
Send Feedback

--- Page 21 ---
7 Series FPGAs CLB User Guide www.xilinx.com 21
UG474 (v1.7) November 17, 2014Look-Up Table (LUT)
Look-Up Table (LUT)
The function generators in 7 series FPGAs ar e implemented as six-input look-up tables 
(LUTs). There are six independent inputs (A inputs - A1 to A6) and two independent outputs (O5 and O6) for each of the four function generators in a slice (A, B, C, and D). The function generators can implement:
 Any arbitrarily defined six-input Boolean function
 Two arbitrarily defined five-i nput Boolean functions, as long as these two functions 
share common inputs
 Two arbitrarily defined Boolean fu nctions of 3 and 2 inputs or less
A six-input function uses:A 1 - A 6  i n p u t s
O 6  o u t p u t
Two five-input or less functions use:A 1 – A 5  i n p u t s
A 6  d r i v e n  H i g h
 O5 and O6 outputs
The propagation delay through a LUT is in dependent of the function implemented. 
Signals from the function generators can:
 Exit the slice (through A, B, C, D ou tput for O6 or AMUX, BMUX, CMUX, DMUX 
output for O5)
 Enter the XOR dedicated gate from an O6 output  Enter the carry-logic chain from an O5 output
 Enter the select line of the carry-logic multiplexer from O6 output
 Feed the D input of the storage element Go to F7AMUX/F7BMUX wide multiplexers from O6 output
In addition to the basic LUTs, slices cont ain three multiplexers (F7AMUX, F7BMUX, and 
F8MUX). These multiplexers are used to combine up to four function generators to provide any function of seven or eight inputs in a slice. 
 F7AMUX: Used to generate seven input functions from LUTs A and B
 F7BMUX: Used to generate seven input functions from LUTs C and D
 F8MUX: Used to combine all LUTs to generate eight input functions.
Functions with more than eight inputs can be  implemented using multiple slices. There are 
no direct connections between slices to form function generators greater than eight inputs 
within a CLB.
Storage Elements
There are eight storage elements per slice. Four  can be configured as either edge-triggered 
D-type flip-flops or level-sensitive latches. The D input can be driven directly by a LUT output via AFFMUX, BFFMUX, CFFMUX, or DF FMUX, or by the BYPASS slice inputs 
bypassing the function generators via AX, BX, CX, or DX input. When configured as a latch, the latch is transparent when the CLK is Low.
Send Feedback

--- Page 22 ---
22 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
There are four additional storage elements that  can only be configured as edge-triggered 
D-type flip-flops. The D input can be driven by the O5 output of the LUT or the BYPASS 
slice inputs via AX, BX, CX, or DX input. When the original four storage elements are configured as latches, these four addi tional storage elements cannot be used.
Figure 2-5  shows both the register only and the register/latch configuration in a slice.
Control Signals
The control signals clock (CLK), clock enable  (CE), and set/reset (SR) are common to all 
storage elements in one slice. When one flip-flop in a slice has SR or CE enabled, the other flip-flops used in the slice also have SR or CE enabled by the common signal. Only the CLK signal has programmable polarity . Any inverter placed on the clock signal is automatically 
absorbed. The CE and SR signals are active-High.
These initialization options are available for storage elements:
 SRLOW: Synchronous or asynchronous Reset when CLB SR signal is asserted
 SRHIGH: Synchronous or asynchronous Set when CLB SR signal is assertedX-Ref Target - Figure 2-5
Figure 2-5: Two Versions of Configuration in a Slice: 4 Registers Only and 4 Register/LatchUG474_c2_04_101210DX
CX
BX
CE
AXDQ
CQ
BQ
AQDFF
LATCHINIT1INIT0SRHIGHSRLOW
SRDFF/LATCHLUT D O utput
LUT C O utputCE
CK
DFF
LATCHINIT1INIT0SRHIGHSRLOW
SRCE
CK
DFF
LATCHINIT1INIT0SRHIGHSRLOW
SRCE
CK
DFF
LATCHINIT1INIT0SRHIGHSRLOW
SRQ
CE
CKQQQ
SR
LUT B O utput
LUT A O utputAFF/LATCHBFF/LATCHCFF/LATCH
CLKReset Type
Sync
AsyncDX
CX
BX
CE
AXDQ
CQ
BQ
AQD
SRDFFLUT D O5 O utput
LUT C O5 O utputCE
CKINIT1
INIT0SRHIGHSRLOW
INIT1INIT0SRHIGHSRLOW
INIT1
INIT0SRHIGHSRLOW
INIT1
INIT0SRHIGHSRLOWD
SRCE
CK
D
SRCE
CK
D
SRQ
CE
CKQQQ
SR
LUT B O5 O utput
LUT A O5 O utputAFFBFFCFF
CLKReset Type
Sync
Async
Send Feedback

--- Page 23 ---
7 Series FPGAs CLB User Guide www.xilinx.com 23
UG474 (v1.7) November 17, 2014Distributed RAM (Available in SLICEM Only)
 INIT0: Asynchronous Reset on power-up or global Set/Reset (see Global Controls 
GSR and GTS, page 72 )
 INIT1: Asynchronous Set on power-up or global Set/Reset
The SR signal forces the storage element into  the state specified by the SRHIGH or SRLOW 
attribute. SRHIGH forces a logic High at the storage element output when SR is asserted, 
while SRLOW forces a logic Low at the storage element output (see Table 2-2 ).
SRHIGH and SRLOW can be set individually for each storage element in a slice. The choice 
of synchronous (SYNC) or asynchronous (ASYNC) set/reset (SRTYPE) cannot be set 
individually for each st orage element in a slice.
The initial state after configuration or global initial state is define d by separate INIT0 and 
INIT1 attributes. By default, setting the SRLOW attribute sets INIT0, and setting the 
SRHIGH attribute sets INIT1. 7 series devi ces can set INIT0 and INIT1 independent of 
SRHIGH and SRLOW.
The configuration options for the set and reset fu nctionality of a register  or the four storage 
elements capable of functioning as a latch are:
 No set or reset
S y n c h r o n o u s  s e t
 Synchronous reset
 Asynchronous set (preset) Asynchronous reset (clear)
Distributed RAM (Available in SLICEM Only)
The function generators (LUTs) in SLICEM s can be implemented as a synchronous RAM 
resource called a dist ributed RAM element. Multiple LUTs in a SLICEM can be combined 
in various ways to store larger amount of data. RAM elements are configurable within a 
SLICEM to implement these configurations:
 Single-Port 32 x 1-bit RAM
 Dual-Port 32 x 1-bit RAM
 Quad-Port 32 x 2-bit RAM
 Simple Dual-Port 32 x 6-bit RAM Single-Port 64 x 1-bit RAM
 Dual-Port 64 x 1-bit RAM
 Quad-Port 64 x 1-bit RAM Simple Dual-Port 64 x 3-bit RAM
 Single-Port 128 x 1-bit RAM
 Dual-Port 128 x 1-bit RAMTable 2-2: Truth Table when using SRLOW and SRHIGH
SR SRVAL Function
0 SRLOW (default) No Logic Change
1S R L O W  ( d e f a u l t )00 SRHIGH No Logic Change
1S R H I G H1
Send Feedback

--- Page 24 ---
24 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
 Single-Port 256 x 1-bit RAM
Distributed RAM modules are synchronous (wri te) resources. A synchronous read can be 
implemented with a flip-flop in the same slice. By using this flip-flop, the distributed RAM performance is improved by decreasing the delay into the clock-to-out value of the 
flip-flop. However, an additional clock latency is added. The distributed elements share the same clock input. For a write operation, th e Write Enable (WE) input, driven by either 
the CE or WE pin of a SLICEM, must be set High.
Table 2-3  shows the number of LUTs (four per sl ice) occupied by each distributed RAM 
configuration. See UG953
, Vivado Design Suite 7 Series FPGA and Zynq-7000 All 
Programmable SoC Libraries Guide  for details of available distributed RAM primitives.
Distributed RAM configurations include:
S i n g l e  p o r t
 Common address port for synchronous writes and asynchronous reads
-Read and write addresses share the same address bus
D u a l  p o r t
 One port for synchronous writes and asynchronous reads
-One function generator is connected with the shared read and write port 
address
 One port for asynchronous reads
-Second function generator has the A in puts connected to a second read-only 
port address, and the WA inputs are sh ared with the first read/write port 
addressTable 2-3: Distributed RAM Configuration
RAM Description Primitive Number of LUTs
32 x 1S Single port RAM32X1S 1
32 x 1D  Dual port RAM32X1D 2
32 x 2Q  Quad port RAM32M 4
32 x 6SDP  Simple dual port RAM32M 4
64 x 1S  Single port RAM64X1S 1
64 x 1D  Dual port RAM64X1D 2
64 x 1Q  Quad port RAM64M 4
64 x 3SDP  Simple dual port RAM64M 4
128 x 1S  Single port RAM128X1S 2
128 x 1D  Dual port RAM128X1D 4
256 x 1S  Single port RAM256X1S 4
Send Feedback

--- Page 25 ---
7 Series FPGAs CLB User Guide www.xilinx.com 25
UG474 (v1.7) November 17, 2014Distributed RAM (Available in SLICEM Only)
 Simple dual port
 One port for synchronous writes (no da ta out/read port from the write port)
 One port for asynchronous reads
Q u a d  p o r t
 One port for synchronous writes and asynchronous reads
 Three ports for asynchronous reads
As shown in Figure 2-3 , the common write port W6:W1 (WA[6:1] in the following figures) 
is always physically driven by the inputs to the D LUT using D[6:1]. The read ports are independent for each of the four LUTs. Th erefore the D LUT is always effectively 
single port, even if DPRAM64 is selected as the LUT configuration. The other three LUTs 
are always effectively dual port, although SPRAM32 can be selected when the read and 
write addresses are connected together. 
Figure 2-6  through Figure 2-14  illustrate various example di stributed RAM configurations 
occupying one SLICEM.
When using x2 configurations (as in 32 X 2 Quad Port in Figure 2-6 ), A6 and WA6 are 
driven High by the software to  keep O5 and O6 independent.
Send Feedback

--- Page 26 ---
26 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
X-Ref Target - Figure 2-6
Figure 2-6: 32 X 2 Quad Port Distributed RAM (RAM32M)UG474_c2_06_070914DI1 DOD[0]
DOC[0]DOD[1]
DOC[1]
DOB[0]
DOB[1]
DOA[0]
DOA[1]DI2DID[1]
DID[0]
ADDRD[4:0]
ADDRC[4:0]
ADDRB[4:0]
ADDRA[4:0]WCLK
WED(CLK)
(WE)
5
5DPRAM32RAM32M
A[6:1]
WA[6:1]CLK
WEO6
O5
DI1
DI2
5
5DPRAM32
A[6:1]
WA[6:1]CLKWEO6
DI1
DI2
DI2B[5:1]C[5:1]D[5:1](AX/BX/CX/DX)(DI)
A[5:1]5
5DPRAM32
A[6:1]
WA[6:1]CLKWEO6
DI1
5
5DPRAM32
A[6:1]
WA[6:1]CLKWEO6O5
O5
O5
Send Feedback

--- Page 27 ---
7 Series FPGAs CLB User Guide www.xilinx.com 27
UG474 (v1.7) November 17, 2014Distributed RAM (Available in SLICEM Only)
X-Ref Target - Figure 2-7
Figure 2-7: 32 X 6 Simple Dual Port Distributed RAM (RAM32M)UG474_c2_06_070914DI1
O[2]
O[1]
O[4]
O[3]
O[6]
O[5]DI2unused
unused
WADDR[5:1]
WADDR[6] = 1
RADDR[5:1]
RADDR[6] = 1DATA[1]
DATA[2]
DATA[3]
DATA[4]
DATA[5]
DATA[6]WCLK
WED(CLK)
(WE)5
5DPRAM32RAM32M
A[6:1]
WA[6:1]CLK
WE
DI1
DI2
5
5DPRAM32
A[6:1]
WA[6:1]CLKWEO6
DI1
DI2
DI2B[5:1]C[5:1]D[5:1]
A[5:1]5
5DPRAM32
A[6:1]
WA[6:1]CLKWEO6
DI1
5
5DPRAM32
A[6:1]
WA[6:1]CLKWEO6O5
O5
O5
Send Feedback

--- Page 28 ---
28 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
If four single-port 64 x 1-bit modu les are each built as shown in Figure 2-8 , the four 
RAM64X1S primitives can occupy a SLICEM, as long as they share the same clock, write 
enable, and shared read and write port addr ess inputs. This configuration equates to a 
64 x 4-bit single-port distributed RAM.
If two dual-port 64 x 1-bit modu les are each built as shown in Figure 2-9 , the two 
RAM64X1D primitives can occupy a SLICEM, as long as they share the same clock, write 
enable, and shared read and write port addr ess inputs. This configuration equates to a 
64 x 2-bit dual-port distributed RAM.X-Ref Target - Figure 2-8
Figure 2-8: 64 X 1 Single Port Distributed RAM (RAM64X1S)
X-Ref Target - Figure 2-9
Figure 2-9: 64 X 1 Dual Port Distributed RAM (RAM64X1D)UG474_c2_07_101210Output
Registered
Output
(Option al)DI1
DQ(DI)D
A[5:0]
WCLK
WE(D[6:1])
(CLK)
(WE/CE)6SPRAM64RAM64X1S
A[6:1]
WA[6:1]CLKWEO6O
6
UG474_c2_0 8_101210DI1(DI)D
A[5:0]
WCLK
WE(D[6:1])
(CLK)
(WE/CE)6
6DPRAM64RAM64X1D
A[6:1]
WA[6:1]CLKWEO6
DI1
DPRA[5:0](C[6:1]) 6
6DPRAM64
A[6:1]
WA[6:1]CLKWEO6Registered
Output
(Option al)DQSPO
Registered
Output
(Option al)DQDPO
Send Feedback

--- Page 29 ---
7 Series FPGAs CLB User Guide www.xilinx.com 29
UG474 (v1.7) November 17, 2014Distributed RAM (Available in SLICEM Only)
X-Ref Target - Figure 2-10
Figure 2-10: 64 X 1 Quad Port Distributed RAM (RAM64M)UG474_c2_09_070914DI1 DID
ADDRD
ADDRC
ADDRB
ADDRAWCLK
WE(CLK)
(WE)DPRAM64
RAM64M
A[6:1]
WA[6:1]CLK
WEO6
DI1DPRAM64
A[6:1]
WA[6:1]CLKWEO6
DI1
(B[6:1])(C[6:1])(D[6:1])(DI)
(A[6:1])DPRAM64
A[6:1]
WA[6:1]CLKWEO6
DI1DPRAM64
A[6:1]
WA[6:1]CLKWEO6Registered
OutputDOD
DOC
DOB
DOA(Option al)DQ
Registered
Output
(Option al)DQ
Registered
Output
(Option al)DQ
Registered
Output
(Option al)DQ
Send Feedback

--- Page 30 ---
30 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
Implementation of distributed RAM configuratio ns with depth greater than 64 requires the 
usage of wide-function multiplexers (F7AMUX, F7BMUX, and F8MUX), as shown in Figure 2-12  through Figure 2-14 .
If two single-port 128 x 1-bit modu les are each built as shown in Figure 2-12 , the two 
RAM128X1S primitives can occupy a SLICEM, as long as they share the same clock, write 
enable, and shared read and write port addre ss inputs. This configuration equates to 128 x 
2-bit single-port distributed RAM.X-Ref Target - Figure 2-11
Figure 2-11: 64 X 3 Simple Dual Port Distributed RAM (RAM64M)UG474_c2_10_070914DI1
O[1]
O[2]
O[3]DI2unused
unused
WADDR[6:1]
RADDR[6:1]DATA[1]
DATA[2]
DATA[3]WCLK
WED(CLK)
(WE)6
6DPRAM64RAM64M
A[6:1]
WA[6:1]CLK
WE
DI1
DI2
6
6DPRAM64
A[6:1]
WA[6:1]CLKWEO6
DI1
DI2
DI2B[6:1]C[6:1]D[6:1]
A[6:1]6
6DPRAM64
A[6:1]
WA[6:1]CLKWEO6
DI1
6
6DPRAM64
A[6:1]
WA[6:1]CLKWEO6O5
O5
O5
Send Feedback

--- Page 31 ---
7 Series FPGAs CLB User Guide www.xilinx.com 31
UG474 (v1.7) November 17, 2014Distributed RAM (Available in SLICEM Only)
X-Ref Target - Figure 2-12
Figure 2-12: 128 X 1 Single Port Distributed RAM (RAM128X1S)UG474_c2_11_101210DI1(DI)A6 (CX)
D
A[6:0]
WCLK
WE(CLK)
(WE/CE)[5:0]
[5:0]7SPRAM64RAM12 8X1S
A[6:1]
WA[7:1]CLKWEO6
DI1
7SPRAM64
A[6:1]
WA[7:1]CLKWEO6Registered
OutputOutput
F7BMUX
(Option al)DQ0
Send Feedback

--- Page 32 ---
32 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
X-Ref Target - Figure 2-1 3
Figure 2-13: 128 X 1 Dual Port Distributed RAM (RAM128X1D)UG474_c2_12_101210DI1 DDI
AXA[6:0]
WCLK
DPRA[6:0]WE(CLK)
(WE)7DPRAM64RAM12 8X1D
A[6:1]
WA[7:1]CLKWEO6
DI1
6
7DPRAM64
A[6:1]
WA[7:1]CLKWEO6Registered
OutputF7BMUX
(Option al)DQSPO
DI1
6
7DPRAM64
A[6:1]
WA[7:1]CLKWEO6
DI1
6
7DPRAM64
A[6:1]
WA[7:1]CLKWEO6Registered
OutputF7AMUX
(Option al)DQDPOA6 (CX)
6
Send Feedback

--- Page 33 ---
7 Series FPGAs CLB User Guide www.xilinx.com 33
UG474 (v1.7) November 17, 2014Distributed RAM (Available in SLICEM Only)
Distributed RAM configurations greater than the provided examples require more than 
one SLICEM. There are no direct connections between slices to form larger distributed 
RAM configurations within a CLB or between slices.X-Ref Target - Figure 2-14
Figure 2-14: 256 X 1 Single Port Distributed RAM (RAM256X1S)UG474_c2_13_101210DI1 D
A[7:0]
WCLK
WE(CLK)
(WE/CE)6
8SPRAM64RAM256X1S
A[6:1]
WA[8:1]
CLKWEO6
DI1
6
8SPRAM64
A[6:1]
WA[8:1]
CLKWEO6F7BMUX
F8MUXRegistered
OutputOutput
(Option al)DQO
DI1
6
8SPRAM64
A[6:1]
WA[8:1]
CLKWEO6
DI1
6
8SPRAM64
A[6:1]
WA[8:1]
CLKWEO6F7AMUXA6 (CX)
A6 (AX)A7 (BX)
Send Feedback

--- Page 34 ---
34 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
Distributed RAM Data Flow
Synchronous Write Operation
The synchronous write operation is a single clock-edge operation with an active-High 
write-enable (WE) feature. When WE is High, the input (D) is loaded into the memory location at address A.
Asynchronous Read Operation
The output is determined by the address A for the single-port mode output SPO of 
dual-port mode, or address DPRA for the DPO output of dual-port mode. Each time a new address is applied to the address pins, the da ta value in the memory location of that 
address is available on the output after the ti me delay to access the LUT. This operation is 
asynchronous and independent of the clock signal.
Distributed RAM Summary
Here is a summary of distributed RAM features:
 Single-port and dual-port modes are available in SLICEMs
 A write operation requires one clock edge
 Read operations are asynchronous (Q output) The data input has a setup-to-clock timing specification
Read Only Memory (ROM)
Each function generator in both SLICEMs and SLICELs can implement a 64 x 1-bit ROM. 
Three configurations are available: ROM64X 1, ROM128X1, and ROM256X1. ROM contents 
are loaded at each de vice configuration. Table 2-4  shows the number of LUTs occupied by 
each ROM configuration size.
Shift Registers (Available in SLICEM Only)
A SLICEM function generator can also be config ured as a 32-bit shift register without using 
the flip-flops available in a slice. Used in this way, each LUT can delay serial data from 1 to 32 clock cycles. The shiftin D (DI1 LUT pin) an d shiftout Q31 (MC31 LUT pin) lines cascade 
LUTs to form larger shift registers. The fo ur LUTs in a SLICEM are thus cascaded to 
produce delays up to 128 clock cycles. It is also possible to combine shift registers across more than one SLICEM. There are no direct connections between slices to form longer shift registers, nor is the MC31 output at LUT B/C/D available. The resulting programmable 
delays can be used to balance the timing of data pipelines.Table 2-4: ROM Configuration
ROM Number of LUTs
64 x 1 1
128 x 1 2
256 x 1 4
Send Feedback

--- Page 35 ---
7 Series FPGAs CLB User Guide www.xilinx.com 35
UG474 (v1.7) November 17, 2014Shift Registers (Available in SLICEM Only)
Applications for shift registers include:
 Delay or latency compensation 
 Synchronous FIFO and content addressable memory (CAM)
Shift register functions include: Write operation
 Synchronous with a clock input (CLK ) and an optional clock enable (CE)
 Fixed read access to Q31 Dynamic read access
 Performed through the 5-bit address bus, A[4:0]
-The LSB of the LUT address is unused and the software automatically ties it 
to a logic High.
 Any of the 32 bits can be read out asynchronously (at the O6 LUT outputs, 
referred to as Q on the primitive) by varying the address
 This capability is useful in creating smaller shift registers (less than 32 bits).
-For example, when building a 13-bit shif t register, set the address to the 13th 
bit.
 A storage element or flip-flop is ava ilable to implement a synchronous read.
-The clock-to-out of the flip-flop determines the overall delay and improves 
performance.
-However, one additional cycl e of clock latency is added.
 Set or reset of the shift register is not supported.
Figure 2-15  is a logic block diagram of a 32-bit shift register.
X-Ref Target - Figure 2-15
Figure 2-15: 32-Bit Shift Register ConfigurationUG474_c2_14_110510Output (Q)
Registered
Output
(Option al)(AQ)DI1
DQ(AI)SHIFTIN (MC31 of Previo us LUT)
SHIFTIN (D)
A[4:0]
CLK
CE(A[6:2])
(CLK)
(WE/CE)SRL32SRLC32E
A[6:2]
CLK
CEO6MC31SHIFTOUT (Q31)
5
Send Feedback

--- Page 36 ---
36 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
Figure 2-16  illustrates an example shift register configuration occupying one function 
generator.
Figure 2-17  shows two 16-bit shift registers. The example shown can be implemented in a 
single LUT. For more information on the SRLC32E and SRL16E primitives, see UG953 , 
Vivado Design Suite 7 Series FPGA and Zynq -7000 All Programmable SoC Libraries Guide .
As mentioned earlier, the MC31 output and a dedicated connection between shift registers 
allows connecting the last bit of one shift regist er to the first bit of the next, without using 
the LUT O6 output. Longer shift registers can be  built with dynamic access to any bit in the 
chain. The shift register chaining and the F7AMUX, F7BMUX, and F8MUX multiplexers allow up to a 128-bit shift register with addressable access to be implemented in one 
SLICEM. Figure 2-18  through Figure 2-20  illustrate various example shift register 
configurations that ca n occupy one SLICEM.X-Ref Target - Figure 2-16
Figure 2-16: Representation of a Shift Register
X-Ref Target - Figure 2-17
Figure 2-17: Dual 16-Bit Shift Register ConfigurationUG474_c2_15_101210SHIFTIN (D)
SHIFTOUT(Q31) WE
CLK
Addre ss (A[4:0])32-bit Shift Regi ster
MUX
Q5
UG474_c2_16_101210DI1 SHIFTIN1 (AI)
SHIFTIN2 (AX)A[3:0]
CLK
CE4SRL16
A[5:2]
CLK
WEO5
MC31DI2
4SRL16
A[5:2]
CLKWEO6
Send Feedback

--- Page 37 ---
7 Series FPGAs CLB User Guide www.xilinx.com 37
UG474 (v1.7) November 17, 2014Shift Registers (Available in SLICEM Only)
X-Ref Target - Figure 2-18
Figure 2-18: 64-Bit Shift Register ConfigurationUG474_c2_17_101210DI1 SHIFTIN (D)
A[5:0]
CLK
WE(CLK)
(WE/CE)5SRL32
A[6:2]
CLK
WEO6
MC31
MC31DI1
5SRL32
A[6:2]
CLKWEO6Registered
OutputOutput (Q)
F7AMUX
(Option al)DQ A5 (AX)
(AQ)
SHIFTOUT (Q63)(MC31)
X-Ref Target - Figure 2-19
Figure 2-19: 96-Bit Shift Register ConfigurationUG474_c2_1 8_101210DI1 SHIFTIN (D)
A[6:0]
CLK
WE
AX (A5)(CLK)
(WE/CE)5SRL32
A[6:2]
CLK
WEO6
MC31
MC31DI1
5SRL32
A[6:2]
CLK
WEO6F7BMUX
Not U sedF8MUXRegistered
OutputOutput (Q)
(Option al)DQ(BQ)(BMUX)
DI1
5SRL32
A[6:2]
CLK
WEO6
F7AMUXCX (A5)
BX (A6)
Send Feedback

--- Page 38 ---
38 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
It is possible to create shift registers longer  than 128 bits across more than one SLICEM. 
However, there are no direct connections between slices to form these shift registers.
Shift Register Data Flow
Shift Operation
Figure 5-7  shows a timing diagram of the shift operation. The shift operation has these 
characteristics:
 Operates on a single clock edge
 Enabled by an active-High clock enable The input (D) is loaded into th e first bit of the shift register
 Each bit is also shifted to the next highest bit positionX-Ref Target - Figure 2-20
Figure 2-20: 128-Bit Shift Register ConfigurationUG474_c2_19_101210DI1 SHIFTIN (D)
A[6:0]
CLK
WE(CLK)
(WE/CE)5SRL32
A[6:2]
CLK
WEO6
MC31
MC31
MC31
MC31DI1SRL32
A[6:2]
CLK
WEO6F7BMUX
F8MUXCX (A5)
BX (A6)
Registered
OutputOutput (Q)
(Option al)DQ(BMUX)
SHIFTOUT (Q127)(MC31)(BQ)
DI1SRL32
A[6:2]
CLK
WEO6
DI1SRL32
A[6:2]
CLK
WEO6F7AMUXAX (A5)
Send Feedback

--- Page 39 ---
7 Series FPGAs CLB User Guide www.xilinx.com 39
UG474 (v1.7) November 17, 2014Multiplexers
 In a cascadable shift register configuration, the last bit is shifted out on the MC31 
output
 The bit selected by the 5-bit address port (A[4:0]) appears on the Q output
Dynamic Read Operation
In a dynamic read operation:
 The Q output is determined by the 5-bit address
 Each time a new address is applied to the 5-input addres s pins, the new bit position 
value is available on the Q output after the time delay to access the LUT
 This operation is asynchronous and independ ent of the clock and clock-enable signals
Static Read Operation
In a static read operation:
 If the 5-bit address is fixed, the Q ou tput always uses the same bit position
 This mode implements any shift-register length from 1 to 32 bits in one LUT
 The shift register length is (N + 1),  where N is the input address (0–31)
 The Q output changes synchronou sly with each shift operation
 The previous bit is shifted to the ne xt position and appears on the Q output
Shift Register Summary
Here is a summary of the shift registers:
 A shift operation requires one clock edge
 Dynamic-length read operations to th e Q output of the LUT are asynchronous
 Static-length read operations to the Q output of the LUT are synchronous The data input has a setup-to-clock timing specification
 In a cascadable configuration, the Q31 ou tput always contains the last bit value
 The Q31 output changes synchron ously after each shift operation
Multiplexers
Function generators and associated multiplexers in 7 series FPGAs can implement these 
functions:
 4:1 multiplexers using one LUT
 Four 4:1 MUXes per slice
 8:1 multiplexers using two LUTs
 Two 8:1 MUXes per slice
 16:1 multiplexers using four LUTs
 One 16:1 MUX per slice
Send Feedback

--- Page 40 ---
40 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
These wide input multiplexers are implemente d in one level of logic (or LUT) using the 
dedicated F7AMUX, F7BMUX, and F8MUX multiplexers. These multiplexers allow LUT combinations of up to four LUTs in a slice. The wide multiplexers can also be used to create general-purpose functions of up to 13 inputs in  two LUTs or 27 inputs in four LUTs (one 
slice). Although the multiplexer outputs are co mbinatorial, they can be registered in the 
CLB storage elements.
Designing Large Multiplexers
4:1 Multiplexer
Each LUT can be configured into a 4:1 MUX. The 4:1 MUX can be implemented with a 
flip-flop in the same slice. Up to four 4:1 MUXes can be implemented in a slice, as shown in Figure 2-21 .
X-Ref Target - Figure 2-21
Figure 2-21: Four 4:1 Multiplexers in a SliceUG474_c2_20_101210(D[6:1])
(C[6:1])
(B[6:1])
(A[6:1])
(CLK)
CLK6SLICE
LUT
LUT
LUT
LUTA[6:1]O6
6A[6:1]O6Registered
Output4:1 MUX O utput
(Option al)DQ(D)
(DQ)
Registered
Output4:1 MUX O utput
(Option al)DQ(C)
(CQ)
Registered
Output4:1 MUX O utput
(Option al)DQ(B)
(BQ)
Registered
Output4:1 MUX O utput
(Option al)DQ(A)
(AQ)6A[6:1]O6
6A[6:1]O6SEL D [1:0], DATA D [3:0]
Input
SEL C [1:0], DATA C [3:0]
Input
SEL B [1:0], DATA B [3:0]
Input 
SEL A [1:0], DATA A [3:0]
Input
Send Feedback

--- Page 41 ---
7 Series FPGAs CLB User Guide www.xilinx.com 41
UG474 (v1.7) November 17, 2014Multiplexers
8:1 Multiplexer
Each slice has an F7AMUX and an F7BMUX. These two MUXes combine the output of two 
LUTs to form a combinatorial function up to  13 inputs (or an 8:1 MUX). Up to two 8:1 
MUXes can be implemented in a slice, as shown in Figure 2-22 .
X-Ref Target - Figure 2-22
Figure 2-22: Two 8:1 Multiplexers in a SliceUG474_c2_21_101210(D[6:1])
(C[6:1])
(CX)
(B[6:1])
(A[6:1])
(AX)SELF7(1)
(CLK)CLK
SELF7(2)SEL D [1:0], DATA D [3:0]
Input (1)
SEL C [1:0], DATA C [3:0]
Input (1)
SEL B [1:0], DATA B [3:0]
Input (2)
SEL A [1:0], DATA A [3:0]
Input (2)6SLICE
LUT
LUT
LUT
LUTA[6:1]O6
6A[6:1]O6Registered
Output8:1 MUX
Output (1)
(Option al)DQ(CMUX)
(CQ)
Registered
Output8:1 MUX
Output (2)
(Option al)DQ(AMUX)
(AQ)6A[6:1]O6
6A[6:1]O6F7BMUX
F7AMUX
Send Feedback

--- Page 42 ---
42 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
16:1 Multiplexer
Each slice has an F8MUX. F8 MUX combines the outputs of F7AMUX and F7BMUX to form 
a combinatorial function up to 27 inputs (or a 16:1 MUX). Only one 16:1 MUX can be implemented in a slice, as shown in Figure 2-23 .
It is possible to create multiplexers wider than 16:1 across more than one SLICEM. 
However, there are no direct connections between slices to form these wide multiplexers.X-Ref Target - Figure 2-2 3
Figure 2-23: 16:1 Multiplexer in a SliceUG474_c2_22_101210(D[6:1])
(C[6:1])
(CX)
(B[6:1])
(A[6:1])
(AX)
(BX)
(CLK)SELF7
SELF7
SELF 8
CLK6SLICE
LUT
LUT
LUT
LUTA[6:1]O6
6A[6:1]O6
Registered
Output16:1 MUX
Output
(Option al)DQ(BMUX)
(B)
6A[6:1]O6
6A[6:1]O6F7BMUX
F8MUX
F7AMUXSEL D [1:0], DATA D [3:0]
Input
SEL C [1:0], DATA C [3:0]
Input
SEL B [1:0], DATA B [3:0]
Input
SEL A [1:0], DATA A [3:0]
Input
Send Feedback

--- Page 43 ---
7 Series FPGAs CLB User Guide www.xilinx.com 43
UG474 (v1.7) November 17, 2014Carry Logic
Carry Logic
In addition to function gene rators, dedicated fast lookahead carry logic is provided to 
perform fast arithmetic addition and subtract ion in a slice. A 7 series FPGA CLB has two 
separate carry chains, as shown in Figure 1-1 . The carry chains are cascadable to form 
wider add/subtract logic, as shown in Figure 2-2 .
The carry chain runs upward and has a height of four bits per slice. For each bit, there is a 
carry multiplexer (MUXCY) and a dedicate d XOR gate for adding/subtracting the 
operands with a selected carry bits. The dedicated carry path and carry multiplexer (MUXCY) can also be used to cascade function generators for implementing wide logic functions.
Figure 2-24  illustrates the carry chain with  associated logic in a slice.
X-Ref Target - Figure 2-24
Figure 2-24: Fast Carry Logic Path and Associated ElementsUG474_c2_23_071 813O6 From LUTDDMUX/DQ*
DMUX
DQO5 From LUTD
DXS3MUXCY
DI3CO3
O3COUT (To Next Slice)
Carry Ch ain Block
(CARRY4)
(Option al)DQ
O6 From LUTCCMUX/CQ*
CMUX
CQO5 From LUTC
CXS2MUXCY
DI2CO2
CO1
CO0O2
(Option al)DQ
O6 From LUTBBMUX/BQ*
BMUX
BQO5 From LUTB
BXS1MUXCY
DI1O1
(Option al)DQ
O6 From LUTAAMUX/AQ*
AMUX
AQO5 From LUTA
AXS0MUXCY
DI0
CIN
CIN (From Previo us Slice)*Can be used if
unregi stered/regi stered
outputs are free.CYINIT
10O0
(Option al)DQ
Send Feedback

--- Page 44 ---
44 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 2: Functional Details
The carry chains use carry look ahead logic along with the function generators. There are 
10 independent inputs and 8 independent outputs:
I n p u t s
 S inputs - S0 to S3
-The “propagate” signals of the carry lookahead logic
-Sourced from the O6 output of a function generator
 DI inputs - DI1 to DI4
-The “generate” signals of the carry lookahead logic
-Sourced from either the O5 output of a function generator
- To create a multiplier 
-Or the BYPASS input (AX, BX, CX, or DX) of a slice
- To create an adder/accumulator
C Y I N I T
-CIN of the first bit in a carry chain
- 0 for add
- 1 for subtract- AX input for the dynamic first carry bit
C I N
-Cascade slices to form a longer carry chain
O u t p u t s
 O outputs - O0 to O3
-Contain the sum of the addition/subtraction
 CO outputs - CO0 to CO3
-Compute the carry out for each bit
-CO3 is connected to COUT output of a slice to form a longer carry chain by 
cascading multiple slices
The propagation delay for an adder increases linearly with the number of bits in the 
operand, as more carry chains are cascaded . The carry chain can be implemented with a 
storage element or a flip-flop in the same slice.
Carry logic cascading is limited only by the height of the column of slices. Carry logic 
cannot be cascaded across super logic regions (SLRs) in devices using stacked silicon interconnect (SSI) technology. See Devices Using Stacked Silicon Interconnect (SSI) 
Technology in Chapter 6 .
Send Feedback

--- Page 45 ---
7 Series FPGAs CLB User Guide www.xilinx.com 45
UG474 (v1.7) November 17, 2014Chapter 3
Design Entry
CLB resources are used automatically and effi ciently by FPGA synthesis tools without any 
special FPGA-specific coding required. Some HDL coding suggestions and techniques can 
help optimize designs for maximum efficiency.
Design Checklist
These guidelines are provided as a quick checkl ist of design suggestions for effective use of 
the 7 series CLBs:
 Resource Utilization
 Use generic HDL code and allow the sy nthesis and mapping tools to choose the 
specific FPGA CLB resources.
 Consider instantiation of specific resour ces only when necessary to meet density 
or performance requirements.
 Compare the results to an estimated slice count to verify design efficiency. If a design is running out of resource s in the target device, examine which 
resource is the limiting factor and consid er using alternative resources, such as 
moving registers to SRLs or distributed RAM, or distributed RAM to block RAM, or carry logic to DSP slices.
 When migrating a design from another architecture, remove resource 
instantiation and any mapping and fl oorplanning constraints (refer to UG429
, 
7 Series FPGAs Migration Methodology Guide ).
Refer to www.xilinx.com  for good HDL coding techniques for FPGAs, such as in UG687 , 
XST User Guide for Virtex-6, Spartan-6, and 7 Series Devices .
 Pipelining
 The designer should use sequential desi gn techniques and pipelining to take 
advantage of abundant flip-flops for performance.
 Control Signals
 Use control signals only as necessary.
 Avoid using a routed global reset signal  and minimize use of local resets to 
maximize opportunity to use FPGA resources.
 Use active-High control signals. Avoid having both set and reset on the same flip-flop.
 Avoid control signals on small shift registers and storage arrays in order to use 
LUTs instead of flip-flops, to maxi mize utilization and minimize power.
Send Feedback

--- Page 46 ---
46 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 3: Design Entry
 Software Options
 To improve performance automatically, use timing constrai nts and trade off 
longer implementation run times through software options.
Using the CLB Resources
Xilinx recommends using generic HDL code and allowing the tools to infer the usage of CLB resources. Using IP solutions designed for 7 series FPGAs can help make full use of the CLB resources. Although any feature in th e CLB can be instantiated directly, including 
the LUTs, carry logic, and sequential elements , instantiation should be reserved primarily 
for specifying when resources outside the CLB should be used, such as the DSP slice. Instantiation might also be need ed if the synthesis tool does not infer a desired special CLB 
resource, such as the wide multiplexers, distributed RAM, or SRL feature.
Primitives
This section provides an overview of the most commonly used CLB primitives. For instantiation examples and for information on other CLB primitives, see UG953
, Vivado 
Design Suite 7 Series FPGA and Zynq-7000 All Programmable SoC Libraries Guide .
Multiplexer Primitives
The multiplexer primitives provide direct instantiation of the dedicated multiplexers in 
each slice, allowing wider multiplexers to be built. Table 3-1  describes the two primitives.
The port signals are the same for both multiplexer primitives. Figure 3-1  shows MUXF7.Table 3-1: Multiplexer Primitives
Primitive Inputs Resource Output Function
MUXF7LUT outputs 
(4:1 multiplexer)F7AMUX or F7BMUX 8:1 multiplexer
MUXF8F7AMUX and F7BMUX outputs 
(8:1 multiplexer)F8MUX 16:1 multiplexer
X-Ref Target - Figure 3-1
Figure 3-1: MUXF7 PrimitiveOI0MUXF7
UG474_c3_01_101210I1
S
Send Feedback

--- Page 47 ---
7 Series FPGAs CLB User Guide www.xilinx.co m 47
UG474 (v1.7) November 17, 2014Primitives
Port Signals
Data In - I0, I1
The data input provides the data to be  selected by the select signal (S).
Control In - S
The select input signal determines the data in put signal to be connected to the output O. 
Logic 0 selects the I0 input, while logic 1 selects the I1 input.
Data Out - O
The data output O provides the data value (one bit) selected by the control inputs.
Carry Chain Primitive
The CARRY4 primitive instantiates the fast carry logic available in each slice. This 
primitive works in conjunction with LUTs to build adders and multipliers. Figure 3-2  
shows the CARRY4 primitive. Synthesis tools generally infer this logic from arithmetic 
HDL code, automatically connect ing this function properly. 
Port Signals
Sum Outputs - O[ 3:0]
The sum outputs provide the final result of th e addition/subtraction. They connect to the 
slice AMUX/BMUX/CMUX/DMUX outputs.
Carry Outputs - CO[ 3:0]
The carry outputs provide the carry out for each bit. CO[3] is equivalent to COUT. A longer 
carry chain can be created if CO[3] is connect ed through COUT to the CI input of another 
CARRY4 primitive, and dedicated routing conne cts the carry chain up a column of slices. 
The carry outputs also optionally connect to the slice AMUX/BMUX/CMUX/DMUX outputs.X-Ref Target - Figure 3-2
Figure 3-2: CARRY4 PrimitiveCARRY4
CYINIT CIDI[3:0]
S[3:0]O[3:0]
UG474_c3_02_101210CO[3:0]
Send Feedback

--- Page 48 ---
48 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 3: Design Entry
Carry In - CI
The carry in input, also called CIN, is used to cascade slices to form longer carry chains. 
Data Inputs - DI[ 3:0]
The data inputs are used as “generate” signal s to the carry lookahead logic. The “generate” 
signals are sourced from LUT outputs.
Select Inputs - S[3:0]
The select inputs are used as “propagate” signals to the carry lookahead logic. The 
“propagate” signals are sourced from LUT outputs.
Carry Initialize - CYINIT
The carry initialize input is used to select the first bit in a carry chain. The value for this pin is either 0 (for add), 1 (for  subtract), or AX input (for  the dynamic first carry bit).
SLICEM Distributed RAM Primitives
Eight primitives are shown in Table 3-2 . Three primitives are single-port RAM, three 
primitives are dual-port RAM, and two primitives are quad-port RAM. 
The input and output data are one bit wide (with the exception of the quad-port RAM).
Figure 3-3  shows generic single-port, dual-p ort, and quad-port distributed RAM 
primitives. The A, ADDR, and DPRA signals are address buses.Table 3-2: Single-Port, Dual-Port, and Quad-Port Distributed RAM
Primitive RAM Size Type Address Inputs
RAM32X1S 32-bit Single-po rt A[4:0] (read/write)
RAM32M 32-bit Quad-port ADDRA[4:0] (read)
ADDRB[4:0] (read)
ADDRC[4:0] (read)ADDRD[4:0] (read/write)
RAM64X1S 64-bit Single-po rt A[5:0] (read/write)
RAM64X1D 64-bit Dual-port A[5:0] (read/write)
DPRA[5:0] (read)
RAM64M 64-bit Quad-port ADDRA[5:0] (read)
ADDRB[5:0] (read)ADDRC[5:0] (read)
ADDRD[5:0] (read/write)
RAM128X1S 128-bit Single-port A[6:0] (read/write)
RAM128X1D 128-bit Dual-port A[6:0], (read/write) 
DPRA[6:0] (read)
RAM256X1S 256-bit Single-port A[7:0] (read/write)
Send Feedback

--- Page 49 ---
7 Series FPGAs CLB User Guide www.xilinx.co m 49
UG474 (v1.7) November 17, 2014Primitives
Instantiating several distributed RAM primitives can be used to implement wide memory 
blocks.
Port Signals
Each distributed RAM port operates independen tly of the other while reading the same set 
of memory cells.
Clock – WCLK
The clock is used for the synchronous write. The data and the address input pins have setup times referenced to the WCLK pin.
The clock pin (WCLK) has an inversion option at the slice level. The clock signal can be 
active at the negative edge of the clock or th e positive edge of the clock without requiring 
other logic resources. The default is at the positive clock edge.
Enable – WE/WED
The enable pin affects the write functionality of  the port. An inactive write enable prevents 
any writing to memory cells. An active write enable causes the clock edge to write the data input signal to the memory location  pointed to by the address inputs.
Address – A[#:0], DPRA[#:0], and ADDRA[#:0] – ADDRD[#:0]
The address inputs A[#:0] (for single-port and dual-port), DPRA[#:0] (for dual-port), and 
ADDRA[#:0] – ADDRD[#:0] (for quad-port) select the memory cells for read or write. The 
width of the port determines the required a ddress inputs. Some of the address inputs are 
not buses in VHDL or Verilog instantiations. Table 3-2  summarizes the function of each 
address pin.
Data In – D, DID[#:0]
The data input D (for single-port and dual-por t) and DID[#:0] (for quad-port) provide the 
new data value to be written into the RAM.X-Ref Target - Figure 3-3
Figure 3-3: Single-Port, Dual-Port, and Quad -Port Distributed RAM PrimitivesRAM#X1S
UG474_c3_03_101210DO
WE
WCLK
A[#:0]SPO DOD[#:0]RAM#X1D
D
DPOR/W Port
Read PortWE
WCLK
A[#:0]
DPRA[#:0]RAM#M
DI[A:D][#:0]
DOC[#:0]R/W Port
Read Port
Read Port
Read PortWE
WCLK
ADDRD[#:0]
ADDRC[#:0]
DOB[#:0] ADDRB[#:0]
DOA[#:0] ADDRA[#:0]
Send Feedback

--- Page 50 ---
50 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 3: Design Entry
Data Out – O, SPO, DPO and DOA[#:0] – DOD[#:0]
The data out O (single-port or SPO), DP O (dual-port), and DO A[#:0] – DOD[#:0] 
(quad-port) reflects the contents of the memory cells referenced by the address inputs. Following an active write clock edge, the data out (O, SPO, or DOD[#:0]) reflects the newly written data. 
SLICEM SRL Shift Register Primitive
One primitive is available for the 32-bit shift register (SRLC32E), which uses one LUT in a 
SLICEM. Figure 3-4  shows the 32-bit shift register primitive.
Port Signals
Clock – CLK
Either the rising edge or the falling edge of the clock is used for the synchronous shift 
operation. The data and clock enable input pins  have setup times referenced to the chosen 
edge of CLK.
The clock pin (CLK) has an inversion option at the slice level. The clock signal can be active 
at the negative or positive edge without re quiring other logic resources. The default is 
positive clock edge.
Data In – D
The data input provides new data (one bit) to be shifted into the shift register.
Clock Enable – CE
The clock enable pin affects shift functionality.  An inactive clock enable pin does not shift 
data into the shift register and does not writ e new data. Activating the clock enable allows 
the data in (D) to be written to the first locati on and all data to be shifted by one location. 
When available, new data appears on output pins (Q) and the cascadable output pin (Q31).
Address – A[4:0]
The address input selects the bit (range 0 to 31)  to be read. The nth bit is available on the 
output pin (Q). Address inputs have no effect  on the cascadable output pin (Q31). Q31 is 
always the last bit of the shift register (bit 31).
Data Out – Q
The data output Q provides the data value (1 bit) selected by the address inputs.X-Ref Target - Figure 3-4
Figure 3-4: 32-Bit Shift RegisterSRLC32E
UG474_c3_04_102910DQA[4:0]5
CE
CLKQ31
Send Feedback

--- Page 51 ---
7 Series FPGAs CLB User Guide www.xilinx.co m 51
UG474 (v1.7) November 17, 2014Primitives
Data Out – Q 31
The data output Q31 provides the last bit value of the 32-bit shift register. New data 
becomes available after each shift-in operation.
Flip-Flop Primitives
There are several primitives for the CLB stor age elements, including both flip-flops and 
latches, with different combinations of control signals available. The FDRE primitive is shown in Figure 3-5  for an example. For more information on the flip-flop and latch 
primitives, see UG953
, Vivado Design Suite 7 Series FP GA and Zynq-7000 All Programmable 
SoC Libraries Guide .
Port Signals
Data In - D
The data input provides new data (one bit) to be clocked into the flip-flop.
Data Out - Q
Q is the one-bit registered data output from the flip-flop.
Clock - C
Either the rising edge or the falling edge of th e clock is used to capture data and toggle the 
output. The data and clock enable input pins have setup times referenced to the chosen 
edge of the clock. The clock pin (C) has an inversion option at the slice level. The clock signal can be active at the negative or posi tive edge of the clock without requiring other 
logic resources. The default is the positive clock edge. All flip-flops in a slice must use the same clock and same clock polarity.
Clock Enable - CE
When CE is Low, clock transitions are ignored with respect to the D input. The set and reset inputs have priority over the clock enable.
Synchronous Reset - R
When R is High, all other inputs are overridden and the data output (Q) is driven Low on 
the active clock transition. This signal is available in the FDRE component. The FDRE flip-flop is also cleared by default on power-up.X-Ref Target - Figure 3-5
Figure 3-5: FDRE PrimitiveFDRE
UG474_c3_05_102910DQ
CE
C
R
Send Feedback

--- Page 52 ---
52 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 3: Design Entry
Synchronous Set - S
When S is High, all other inputs are overridden and the data output (Q) is driven High on 
the active clock transition. This signal is available in the FDSE component. The FDSE flip-flop is also preset by default on power-up.
Asynchronous Clear - CLR
When CLR is High, all other inputs are overridden and the data output (Q) is driven Low. This signal is available in the FDCE component. The FDCE flip-flop is also cleared by default on power-up. 
Asynchronous Preset - PRE
When PRE is High, all other inputs are overridden and the data output (Q) is driven High. This signal is available in the FDPE component. The FDPE flip-flop is also preset by default on power-up.
Note:
Using both asynchronous clear and preset on the same flip-flop requires additional resources 
and timing paths.
Send Feedback

--- Page 53 ---
7 Series FPGAs CLB User Guide www.xilinx.com 53
UG474 (v1.7) November 17, 2014Chapter 4
Applications
This chapter provides guidance regarding us ing the CLB resources as parts of larger 
functions. Trade-offs are described between alternative methods of implementing these 
functions.
Distributed RAM Applications
Distributed RAM provides a trade-off between  using storage elements for very small 
arrays and block RAM for larg er arrays. It is recommended to infer memory where 
possible to provide the greatest flexibility.  Distributed RAM can also be targeted by 
instantiation or through the use of Xilinx LogiCORE™ IP .
In general, distributed RAM should be used for all memories that consist of 64 bits or less, 
unless there is a shortage of SLICEM or logi c resources for the target device. Distributed 
RAM is more efficient in terms of resources, performance, and power.
For depths greater than 64 bits but less than or  equal to 128 bits, the decision on the best 
resource to use depends on these factors:
1. The availability of extra block RAMs. If not available, distributed RAM should be 
used.
2. The latency requirements. If asynchronous read capability is needed, distributed 
RAMs must be used.
3. The data width. Widths greater than 16 bits should use block RAM, if available.
4. The necessary performance requirements. Registered distributed RAMs generally 
have shorter clock-to-out timing and fewe r placement restrictions than block RAMs.
Shift Register Applications
Synchronous Shift Registers
The shift-register primitive does not use the register available in the same slice. To 
implement a fully synchronous read and write shift register, output pin Q must be connected to a flip-flop. Both the shift regist er and the flip-flop share the same clock, as 
shown in Figure 4-1 .
Send Feedback

--- Page 54 ---
54 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 4: Applications
This configuration provides a better timing solution and simplifies the design. Because the 
flip-flop must be considered to be the last regi ster in the shift-register chain, the static or 
dynamic address should point to the desired length minus one. If needed, the cascadable output can also be registered in a flip-flop.
Static-Length Shift Registers
The cascadable 32-bit shift register implements any static length mode shift register 
without the dedicated multiplexers (F7AMUX, F7BMUX, and F8MUX). Figure 4-2  
illustrates a 72-bit shift register. Only the last SRLC32E primitive needs to have its address inputs tied to 0b00111 . Alternatively, shift register length can be limited to 71 bits 
(address tied to 0b00110 ) and a flip-flop can be used as the last register. (In an SRLC32E 
primitive, the shift register length is the address input + 1).X-Ref Target - Figure 4-1
Figure 4-1: Synchronous Shift RegisterSynchrono us
OutputDQ DQ
Addre ss
CLK(Write En able) CESRLC32E FF
Q31
UG474_c4_01_101210
X-Ref Target - Figure 4-2
Figure 4-2: Example Static-Length Shift RegisterLUT
SRLC32ED
Q31
LUT
SRLC32ED
Q31
LUT
SRLC32ED OUT
(72-bit SRL)A[4:0]
Q31Q
500111D
UG474_c4_02_101210LUT
SRLC32ED
Q31
LUT
SRLC32ED
Q31
LUT
SRLC32ED OUT
(72-bit SRL)A[4:0]
Q31QFF
D Q
500110D
Send Feedback

--- Page 55 ---
7 Series FPGAs CLB User Guide www.xilinx.com 55
UG474 (v1.7) November 17, 2014Carry Logic Applications
Carry Logic Applications
Dedicated carry logic in the CLB improves the performance of arithmetic functions such as 
adders, counters, and comparators. Designs that include simple counters or adder/
subtractors automatically infer the carry logic. More complex functions including 
multipliers can be implemented using the separate DSP48E1 slice.
The DSP48E1 slices in every device suppo rt many independent functions including 
multiply, multiply accumulate, multiply add, three-input add, barrel shift, wide-bus multiplexing, magnitude comparator, bitwise lo gic functions, pattern detection, and wide 
counter. The architecture also supports cascading multiple DSP48E1 slices to form wide math functions, DSP filters, and complex arithm etic. For more details on the DSP48E1 slice, 
see UG479
, 7 Series DSP48E1 Slice User Guide .
The choice between using CLB carry logic and the DSP48E1 slice depends on the 
application. A small arithmetic function can be faster and lower power using the CLB carry 
logic rather than using an entire DSP48E1 slic e. When the DSP48E1 slices are fully utilized, 
the CLB slices and carry logic pr ovide an efficient alternative. 
Using Carry Logic
Carry logic can be inferred or instantiated. Using macros designed for the 7 series FPGA 
can provide the most flexibility and efficien cy, especially for more complex functions.
Unimacros include adders, counters, comp arators, multipliers, and multiplier/
accumulators. The unimacros use the DSP48E1 slice.
The Xilinx IP includes a similar set of functi ons. When defining these functions, the user 
can specify whether the implementation should be in the CLB carry logic or in the DSP48E1 slice.
The carry logic runs vertically up every othe r column of slices (SLICEL and SLICEM). The 
Xilinx tools automatically place logic in a column when the carry logic is used. When floorplanning, carry logic based functions should always be specified as a group to avoid unnecessary breaks in the carry chain. Carry  logic cannot be cascaded across super logic 
regions (SLRs) in devices using stacked silicon interconnect (SSI) technology.
Send Feedback

--- Page 56 ---
56 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 4: Applications
Send Feedback

--- Page 57 ---
7 Series FPGAs CLB User Guide www.xilinx.com 57
UG474 (v1.7) November 17, 2014Chapter 5
Timing
Although it is not necessary to understand the various timing parameters to implement 
most designs using Xilinx software, a thorough timing model can assist advanced users in analyzing critical paths or planning speed-sensi tive designs, especially in the larger and 
more complex 7 series FPGAs.
The user is recommended to use the models in this chapter in conjunction with both the 
Xilinx® Timing Analyzer and the section on switching characteristics in the respective 7 series FPGAs data sheet. All pin names, para meter names, and paths are consistent with 
the Timing Analyzer reports. Most of the CL B timing parameters found in the data sheet 
section on switching characteristics are described in this chapter.
Five categories of functions are described in this chapter:CLB General Slice Timing Model and Parameters, page 58
CLB Slice Multiplexer Timing Model and Parameters, page 60
CLB Slice Carry-Chain Timing Model and Parameters, page 61
CLB Slice Distributed RAM Timing Model and Parameters (Available in SLICEM 
Only), page 63
CLB Slice SRL Shift Register Timing Model and Parameters (Available in SLICEM 
Only), page 66
For each category, three timing  model sections are described:
 Functional element diagram - basic archit ectural schematic illustrating pins and 
connections
 Timing parameters - definitions of the respective 7 series FPGAs data sheet timing 
parameters
 Timing diagram - illustrates functional element timing parameters relative to each 
other
The general form of a timing parameter name is T subscripted with a combination of the 
starting pin and the ending pin. For example, T
CECK  is the setup time from CE to the clock, 
and TCKCE  is the hold time from the clock to CE being removed. In some cases, a single 
parameter name can apply to multiple paths through the slice, and can have different 
values for each path.
Send Feedback

--- Page 58 ---
58 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 5: Timing
CLB General Slice Timing Model and Parameters
A simplified 7 series FPGA slice is shown in Figure 5-1 . Only the elements relevant to the 
timing paths described in this section are shown.
X-Ref Target - Figure 5-1
Figure 5-1: Simplified 7 Series FPGA SliceUG474_c5_01_101210LUT
O6
O56D
FF/LAT
D
CECLK
SRQ
F7BMUX
F8MUXDMUX
DQD 
Inputs
LUT
O6
O56C
FF/LAT
D
CECLK
SRQ
CQCMUXC 
InputsDX
CX
LUT
O6
O56B
FF/LAT
D
CECLK
SRQ
BQBMUXB 
Inputs
BX
FF/LAT
D
CECLK
SRQ
AQF7AMUX LUT
O6
O56A
AMUXA 
Inputs
AX
CE
CLK
SRD
CEQ
CK
SR
D
CEQ
CK
SR
D
CEQ
CK
SR
D
CEQ
CK
SR
Send Feedback

--- Page 59 ---
7 Series FPGAs CLB User Guide www.xilinx.com 59
UG474 (v1.7) November 17, 2014CLB General Slice Timing Model and Parameters
General Timing Parameters
Table 5-1  shows the general slice timing parame ters for a majority of the paths in 
Figure 5-1 . 
Table 5-1: General Slice Timing Parameters
Parameter Function Description
Combinatorial Delays
TILO(1)A/B/C/D inputs to A/B/C/D 
outputsPropagation delay from the A/B/C/D LUT inputs of the slice, 
through the look-up tables (LUTs), to the A/B/C/D outputs of the 
slice.
TITO A/B/C/D inputs through 
transparent latch to AQ/BQ/
CQ/DQ outputsPropagation delay from the A/B/C/D LUT inputs of the slice, 
through the LUTs to the AQ/BQ/CQ/DQ outputs of the slice 
sequential elements (configured as a latch).
Sequential Delays
TCKO FF Clock (CLK) to AQ/BQ/
CQ/DQ outputsTime after the clock that data  is stable at the AQ/BQ/CQ/DQ 
outputs of the slice sequential elements (configured as a flip-flop).
TCKLO Latch Clock (CLK) to AQ/BQ/
CQ/DQ outputsTime after the clock that data  is stable at the AQ/BQ/CQ/DQ 
outputs of the slice sequential elements (configured as a latch).
TSHCKO FF Clock (CLK) to AMUX/
BMUX/CMUX/DMUX 
outputsTime after the clock that data is stable at the AMUX/BMUX/
CMUX/DMUX outputs (through  the slice flip-flops).
Setup and Hold Times for Slice Sequential Elements(2)
TAS/TAH A/B/C/D inputs Time before/after the CLK that data from the A/B/C/D LUT 
inputs of the slice must be stable.
TDICK /TCKDI AX/BX/CX/DX inputs Time before/after the CLK that data from the AX/BX/CX/DX 
inputs of the slice must be stable.
TCECK /TCKCE CE input Time before/after the CLK that  the CE input of the slice must be 
stable.
TSRCK /TCKSR SR input Time before/after the CLK that the SR (Set/Reset) input of the 
slice must be stable.
Set/Reset
TRPW (TSRMIN ) SR input Minimum pulse width for the SR (Set/Reset).
TRQ SR input Propagation delay for an asynchronous Set/Reset of the slice 
sequential elements. 
Miscellaneous
TCEO CE input Propagation delay from CE enable to latch output at AQ/BQ/
CQ/DQ outputs.
FTOG CLK input Toggle Frequency – Maximum frequency that a slice flip-flop can 
be clocked. For export control.
Notes: 
1. This parameter includes a LUT configured as two five-input functions.
2. TXXCK  = Setup Time (before clock edge), and TCKXX  = Hold Time (after clock edge).
Send Feedback

--- Page 60 ---
60 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 5: Timing
General Timing Characteristics
Figure 5-2  illustrates the general timing characteristics of a 7 series FPGA slice.
 At time TCECK  before clock event (1), the clock-enable signal becomes valid-High at 
the CE input of the slice register.
 At time TDICK  before clock event (1), data from  either AX, BX, CX, or DX inputs 
become valid-High at the D input of the slic e register and is reflected on either the 
AQ, BQ, CQ, or DQ pin at time TCKO after clock event (1).
 At time TSRCK  before clock event (3), the SR sign al (configured as synchronous reset) 
becomes valid-High, resetting the slice register. This is reflected on the AQ, BQ, CQ, or DQ pin at time T
CKO after clock event (3).
CLB Slice Multiplexer Timing Model and Parameters
Figure 2-22, page 41  and Figure 2-23, page 42  illustrate the wide multiplexers in a 7 series 
FPGA slice.
Slice Multiplexer Timing Parameters
Table 5-2  shows the slice multiplexer timing para meters for a majority of the paths in 
Figure 2-22  and Figure 2-23 . Note that many of these parameter names are also used for 
paths that do not include the wide multiplexers.X-Ref Target - Figure 5-2
Figure 5-2: General Slice Timing CharacteristicsUG474_c5_02_102310TCECK123
CLK
CE
AX/BX/CX/DX
(DATA)
SR (RESET)
AQ/BQ/CQ/DQ
(OUT)TDICK
TCKOTSRCK
TCKO
Table 5-2: Slice Multiplexer Timing Parameters
Parameter Function Description
Propagation Delays for Slice Using the Wide Multiplexers
TAXA/TAXB/
TBXB/
TCXB/TCXCAX/BX/CX inputs to AMUX/
BMUX/CMUX outputsPropagation delay from the 
AX/BX/CX inputs of the 
slice through the select inputs of the multiplexers to the 
AMUX/BMUX/CMUX 
outputs of the slice.
Send Feedback

--- Page 61 ---
7 Series FPGAs CLB User Guide www.xilinx.com 61
UG474 (v1.7) November 17, 2014CLB Slice Carry-Chain Timing Model and Parameters
CLB Slice Carry-Chain Timing Model and Parameters
Figure 2-24, page 43  illustrates a carry chain in a 7 series FPGA slice. 
Slice Carry-Chain Timing Parameters
Table 5-3  shows the slice carry-chain timing para meters for a majority of the paths in 
Figure 2-24 .TOPAB /
TOPBA /TOPBB /
TOPCB /
TOPDB / TOPDCA/B/C/D inputs to AMUX/
BMUX/CMUX outputsPropagation delay from the 
A/B/C/D LUT inputs of the 
slice through the multiplexers to the AMUX/
BMUX/CMUX outputs of 
the slice.
T
ILO_2 A/C inputs to AMUX/CMUX 
outputsPropagation delay from the A 
LUT inputs of the slice through the F7AMUX 
multiplexer to the AMUX 
output of the slice, or propagation delay from the C 
LUT inputs of the slice 
through the F7BMUX multiplexer to the CMUX 
output of the slice.Table 5-2: Slice Multiplexer Timing Parameters (Cont’d)
Parameter Function Description
Table 5-3: Slice Carry-Chain Timing Parameters
Parameter Function Description
Propagation Delays for Slice Configured as a Carry Chain
TAXA/TAXB/TAXC/TAXD/ 
TBXB/TBXC/TBXD/
TCXC/TCXD/
TDXDAX/BX/CX/DX inputs to 
AMUX/BMUX/ CMUX/DMUX outputsPropagation delay from the 
AX/BX/CX/DX inputs of the slice through the carry 
logic to the AMUX/BMUX/
CMUX/DMUX outputs of the slice.
T
AXCY /TBXCY /TCXCY /TDXCY AX/BX/CX/DX inputs to 
COUT outputPropagation delay from the 
AX/BX/CX/DX inputs of 
the slice to the COUT output 
of the slice.
TBYP CIN input to COUT output Propagation delay from the 
CIN input of the slice to the COUT output of the slice.
T
OPCYA /TOPCYB /TOPCYC / 
TOPCYDA/B/C/D inputs to COUT outputPropagation delay from the 
A/B/C/D LUT inputs of the 
slice to the COUT output of 
the slice.
Send Feedback

--- Page 62 ---
62 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 5: Timing
Slice Carry-Chain Timing Characteristics
Figure 5-3  illustrates the timing characteristics of a slice carry chain implemented in a 
7 series FPGA slice.
Note relevant to Figure 5-3 :
 At time TCINCK  before clock event 1, data from the CIN input becomes valid-High at 
the Data input of the slice register. This  is reflected on any of the AQ/BQ/CQ/DQ 
pins at time TCKO after clock event 1.TCINA /TCINB /TCINC /TCIND CIN input to AMUX/
BMUX/ CMUX/DMUX 
outputsPropagation delay from the 
CIN input of the slice to 
AMUX/BMUX/CMUX/DMUX outputs of the slice 
using XOR (sum).
Setup and Hold Times for a Slice Configured as a Carry Chain
(1)
TCINCK /TCKCIN CIN input Time before/after the CLK 
that the CIN input of the slice 
must be stable.
Notes: 
1. TXXCK  = Setup Time (before clock edge), and TCKXX  = Hold Time (after clock edge).Table 5-3: Slice Carry-Chain Timing Parameters (Cont’d)
Parameter Function Description
X-Ref Target - Figure 5- 3
Figure 5-3: Slice Carry-Chain Timing CharacteristicsUG474_c5_03_110110TCINCK1
CLK
CIN
(DATA)
AQ/BQ/CQ/DQ
(OUT)TCKO
Send Feedback

--- Page 63 ---
7 Series FPGAs CLB User Guide www.xilinx.com 63
UG474 (v1.7) November 17, 2014CLB Slice Distributed RAM Timing Model and Parameters (Available in SLICEM Only)
CLB Slice Distributed RAM Ti ming Model and Parameters 
(Available in SLICEM Only)
Figure 5-4  illustrates the details of distributed RA M implemented in a 7 series FPGA slice. 
Some elements of the slice are omitted for clarit y. Only the elements relevant to the timing 
paths described in this section are shown.
X-Ref Target - Figure 5-4
Figure 5-4: Simplified 7 Series FPGA SLICEM Distributed RAMUG474_c5_04_1101106DDI
DX
D inp ut
CI
CX
C inp ut
BI
BX
B inp ut
AI
AX
A inp utCLK
WEWA[6:0]RAM
CLK
WEDI1
DI2A[6:0] O6
DMUX O5
6C
WA[6:0]RAM
CLK
WEDI1
DI2A[6:0]O6
CMUX O5
6B
WA[6:0]RAM
CLK
WEDI1
DI2A[6:0]O6
BMUX O5
6A
WA[6:0]RAM
CLK
WEDI1
DI2A[6:0]O6
AMUX O5
Send Feedback

--- Page 64 ---
64 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 5: Timing
Distributed RAM Timing Parameters
Table 5-4  shows the timing parameters for the di stributed RAM in SLIC EM for a majority 
of the paths in Figure 5-4 .
Table 5-4: Distributed RAM Timing Parameters
Parameter Function Description
Sequential Delays for a Slice LUT Configured as RAM (Distributed RAM)
TSHCKO CLK to A/B/C/D outputsTime after the CLK of a write operation that the 
data written to the distributed RAM is stable on 
the A/B/C/D outputs of the slice.
TSHCKO  (TSHCKO_1 )CLK to AMUX/BMUX/CMUX/DMUX 
outputsTime after the CLK of a write operation that the 
data written to the distributed RAM is stable on 
the AMUX/BMUX/CMUX/DMUX outputs of 
the slice.
Setup and Hold Times for a Slice LUT Configured as RAM (Distributed RAM)(1)
TDS/TDH
(TDS_LRAM /TDH_LRAM )AI/BI/CI/DI configured as data inputs 
(DI1)(2)Time before/after the clock that data must be stable at the AI/BI/CI/DI inputs of the slice 
(configured as RAM).
T
AS/TAH
(TAS_LRAM /TAH_LRAM )A/B/C/D address inputsTime before/after the clock that address signals 
must be stable at the A/B/C/D LUT inputs of 
the slice (configured as RAM).
TWS/TWH
(TWS_LRAM /TWH_LRAM )WE inputTime before/after the clock that the write 
enable signal must be st able at the WE input of 
the slice (configured as RAM).
Clock CLK
TMPW
(TMPW_LRAM )Minimum clock pulse width for distributed 
RAM.
TMCPMinimum clock period to meet address write 
cycle time.
Notes: 
1. TXS = Setup Time (before clock edge), and TXH = Hold Time (after clock edge).
2. Parameter includes AX/BX/CX/DX configured as a data input (DI2).
Send Feedback

--- Page 65 ---
7 Series FPGAs CLB User Guide www.xilinx.com 65
UG474 (v1.7) November 17, 2014CLB Slice Distributed RAM Timing Model and Parameters (Available in SLICEM Only)
Distributed RAM Timing Characteristics
The timing characteristics of a distribute d RAM implemented in a 7 series FPGA slice 
(LUT configured as RAM) are shown in Figure 5-5 .
Clock Event 1: Write Operation
During a Write operation, the contents of the memory at the address on the ADDR inputs 
are changed. The data written to this memo ry location is reflected on the A/B/C/D 
outputs synchronously.
 At time TWS before clock event 1, the write-enab le signal (WE) be comes valid-High, 
enabling the RAM for a Write operation.
 At time TAS before clock event 1, the address (2) becomes valid at the A/B/C/D 
inputs of the RAM.
 At time TDS before clock event 1, the DATA becomes valid (1) at the DI input of the 
RAM and is reflected on the A/B/C/D outputs at time TSHCKO  after clock event 1. 
This is also applicable to the AMUX, BMUX, CMUX, DMUX, and COUT outputs at time T
SHCKO  after clock event 1.
Clock Event 2: Read Operation
All Read operations are asynchronous in dist ributed RAM. As long as WE is Low, the 
address bus can be asserted at any time. The contents of the RAM on the address bus are reflected on the A/B/C/D outputs after a delay of length T
ILO (propagation delay through 
a LUT). The address (F) is asse rted after clock event 2, and the contents of the RAM at 
address (F) are reflected at the output after a delay of length TILO.X-Ref Target - Figure 5-5
Figure 5-5: Slice Distributed RAM Timing CharacteristicsUG474_c5_05_110110TMPWTMPWTMCP1234567
CLK
WE
DATA_OUT
A/B/C/D
OutputA/B/C/D
(ADDR)
AI/BI/CI/DI
(DI)TAS
2
1
10 0 1 MEM(F)
WRITE WRITE WRITE WRITE READ READMEM(E)XX 00 1F3 4 5 E
TDS
TWS TILO TILO
TSHCKO
Send Feedback

--- Page 66 ---
66 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 5: Timing
CLB Slice SRL Shift Register Timing Model and Parameters 
(Available in SLICEM Only)
Figure 5-6  illustrates shift register implementation in a 7 series FPGA slice. Some elements 
of the slice have been omitted for clarity. On ly the elements relevant to the timing paths 
described in this section are shown.
X-Ref Target - Figure 5-6
Figure 5-6: Simplified 7 Series FPGA Slice SRLUG474_c5_06_1101106DDI
CI
BI
AID addressSRL
CLK WEDI1
AO6
MC31
WCLK
6C
C addressSRL
CLK WEDI1
AO6
MC31
6B
B addressSRL
CLK WEDI1
AO6
MC31
6A
A addressSRL
CLK WEDI1
AO6
DMUX MC31
Send Feedback

--- Page 67 ---
7 Series FPGAs CLB User Guide www.xilinx.com 67
UG474 (v1.7) November 17, 2014CLB Slice SRL Shift Register Timing Model and Parameters (Available in SLICEM Only)
Slice SRL Timing Parameters
Table 5-5  shows the SLICEM SRL timing paramete rs for a majority of the paths in 
Figure 5-6 .
Table 5-5: Slice SRL Timing Parameters
Parameter Function Description
Sequential Delays for a Slice LUT Configured as an SRL
TREG(1)CLK to A/B/C/D outputsTime after the CLK of a write operation that the 
data written to the SRL is stable on the A/B/C/
D outputs of the slice.
TREG (TREG_MUX )(1)CLK to AMUX - DMUX outputsTime after the CLK of a write operation that the 
data written to the SRL is stable on the AMUX/
BMUX/CMUX/DMUX outputs of the slice.
TREG (TREG_M31 )CLK to DMUX output via MC31 
outputTime after the CLK of a write operation that the 
data written to the SRL is stable on the DMUX output via MC31 output.
Setup and Hold Times for a S lice LUT Configured as an SRL
(2)
TCECK /TCKCE
(TCECK_SHFREG /TCKCESHFREG )CE input (CE)Time before/after the clock that the 
clock-enable signal must  be stable at the CE 
input of the slice LUT (configured as an SRL).
TWS/TWH
(TWS_SHFREG /TWH_SHFREG )CE input (WE)Time before/after the clock that the 
write-enable signal must be stable at the WE input of the slice LUT (configured as an SRL).
T
DS/TDH(3)
(TDS_SHFREG /TDH_SHFREG )AI/BI/CI/DI configured as data 
inputs (DI)Time before/after the clock that the data must 
be stable at the AI/BI/CI/DI inputs of the slice 
(configured as an SRL).
Clock CLK
TMPWMinimum clock pulse wi dth for distributed 
RAM.
Notes: 
1. This parameter includes a LUT configured as a two-bit shift register.
2. TXS = Setup Time (before clock edge), and TXH = Hold Time (after clock edge).
3. Parameter includes AX/BX/CX/DX configured as a data input (DI2) or two bits with a common shift.
Send Feedback

--- Page 68 ---
68 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 5: Timing
Slice SRL Timing Characteristics
Figure 5-7  illustrates the timing characteristics of a shift register implemented in a 7 series 
FPGA slice (a LUT configured as an SRL).
Clock Event 1: Shift In
During a write (Shift In) operation, the single -bit content of the register at the address on 
the A/B/C/D inputs is changed, as data is shifted through the SRL. The data written to 
this register is reflected on the A/B/C/D outputs synchronously, if the address is 
unchanged during the clock event. If the A/B/C/D inputs are changed during a clock 
event, the value of the data at the addres sable output (A/B/C/D outputs) is invalid.
 At time TWS before clock event 1, the write-enab le signal (WE) be comes valid-High, 
enabling the SRL for the Write operation that follows.
 At time TDS before clock event 1, the data becomes valid (0) at the DI input of the SRL 
and is reflected on the A/B/C/D output after a delay of length TREG after clock 
event 1. Because address 0 is specified at clock event 1, the data on the DI input is reflected at A/B/C/D output, becaus e it is written to register 0.
Clock Event 2: Shift In
 At time TDS before clock event 2, the data becomes valid (1) at the DI input of the SRL 
and is reflected on the A/B/C/D output after a delay of length TREG after clock 
event 2. Because address 0 is still specified at clock event 2, the data on the DI input is 
reflected at the D output, because it is written to register 0.
Clock Event 3: Shift In/Addressable (Asynchronous) Read
All Read operations are asynchronous to the CLK signal. If the address is changed 
(between clock events), the contents of the re gister at that address are reflected at the 
addressable output (A/B/C/D outp uts) after a delay of length TILO (propagation delay 
through a LUT).
 At time TDS before clock event 3, the data becomes valid (1) at the DI input of the SRL 
and is reflected on the A/B/C/D output TREG time after clock event 3.X-Ref Target - Figure 5-7
Figure 5-7: Slice SRL Timing CharacteristicsUG474_c5_07_110110123456 3 2
CLK
Write En able
(WE)
Shift_In (DI)
Addre ss
(A/B/C/D)
Data Out
(A/B/C/D)
MSB
(MC31/DMUX)TDS
TILO TILO0110 1 0
2 0
X
XXXXXX X 001 1 1 1 1 00TREG
TREGTWS
1
Send Feedback

--- Page 69 ---
7 Series FPGAs CLB User Guide www.xilinx.com 69
UG474 (v1.7) November 17, 2014CLB Slice SRL Shift Register Timing Model and Parameters (Available in SLICEM Only)
 The address is changed (from 0 to 2). The valu e stored in register 2 at this time is a 0 
(in this example, this was the first data shif ted in), and it is reflected on the A/B/C/D 
output after a delay of length TILO.
Clock Event 32: MSB (Most Significant Bit) Changes
 At time TREG after clock event 32, the first bit shifted into the SRL becomes valid 
(logical 0 in this case) on the DMUX output  of the slice via the MC31 output of LUT A 
(SRL). This is also applicable to the AMUX, BMUX, CMUX, DMUX, and COUT outputs at time T
REG after clock event 1.
Send Feedback

--- Page 70 ---
70 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 5: Timing
Send Feedback

--- Page 71 ---
7 Series FPGAs CLB User Guide www.xilinx.com 71
UG474 (v1.7) November 17, 2014Chapter 6
Advanced Topics
Using the Latch Function as Logic
Because the latch function is level-sensitive, it can be used as the equivalent of a logic gate. 
The primitives to specify this function are AND2B1L (a 2-input AND gate with one input inverted) and OR2L (a 2-input OR gate), as shown in Figure 6-1 .
As shown in Figure 6-2 , the data and SR inputs and Q output of the latch are used when the 
AND2B1L and OR2L primitives are instantiated , and the CK gate and CE gate enables are 
held active-High. The AND2B1L combines the la tch data input (the inverted input on the 
gate, DI) with the asynchronous clear input (S RI). The OR2L combines the latch data input 
with an asynchronous preset. Generally, the latch data input comes from the output of a 
LUT within the same slice, extending the lo gic capability to anot her external input. 
Because there is only one SR input per slice, using more than one AND2B1L or OR2L per slice requires a shared common external input.
The device model shows these functions as AND2L and OR2L configurations of the 
storage element. X-Ref Target - Figure 6-1
Figure 6-1: AND2B1L and OR2L Components
X-Ref Target - Figure 6-2
Figure 6-2: Implementation of OR2L (Q = D or SRI)UG474_c6_01_110210AND2B1L OR2L
UG474_c6_02_110310LUT6 DQ
CEVCC
CKSRIN[6:1] O6 Q
SRI
Send Feedback

--- Page 72 ---
72 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 6: Advanced Topics
The AND2B1L and OR2L two-input gates save  LUT resources and are initialized to a 
known state on power-up and on GSR assertion (Global Set/Reset). Using these primitives can reduce logic levels and increase logic density of the device by trading register/latch resources for logic. However, due to the static inputs required on the clock and clock enable inputs, specifying one or more AND2 B1L or OR2L primitives can cause register 
packing and density issues in a slice disallowing the use of the remaining registers and latches.
Interconnect Resources
Interconnect is the programmable network of  signal pathways between the inputs and 
outputs of functional elements  within the FPGA, such as IOBs, CLBs, DSP slices, and block 
RAM. Interconnect, also called routing, is segmented for optimal connectivity. The Xilinx placement and routing tools exploit the rich in terconnect array to deliver optimal system 
performance and the fastest compile times.
The 7 series CLBs are arranged in a regular array inside the FPGA. Each connects to a 
switch matrix for access to the general-ro uting resources, which run vertically and 
horizontally between the CLB rows and column s. A similar switch matrix connects other 
resources, such as the DSP slices and block RAM resources.
Most of the interconnect features are transp arent to FPGA designers. Knowledge of the 
interconnect details can be used to guide design techniques but is not necessary for 
efficient FPGA design. Only selected types of interconnect are under user control. These include the clock routing resources, which are selected by using clock buffers and discussed in more detail in UG472
, 7 Series FPGAs Clocking Resources User Guide . Two 
global control signals, GSR and GTS, are selected by using the STARTUPE2 primitive.
Global Controls G SR and GT S
In addition to the general- purpose interconnect, 7 series FPGAs have two global logic 
control signals, as described in Table 6-1 .
If a common initialization signal is needed fo r every flip-flop in the design, use the GSR 
control in a design instead of a separate routed global reset signal to make CLB inputs available, which results in a smaller more ef ficient design. The GSR signal must always 
re-initialize every flip-flop. Using GSR and GTS does not use any general-purpose routing resources. The GSR signal is asserted au tomatically during the FPGA configuration 
process, guaranteeing that the FPGA starts up  in a known state. At configuration, because 
flip-flops are enabled by the configuration clock and then clocked by a user clock, it is recommended to enable key flip-flops or key clock signals on the user clock after configuration.Table 6-1: Global Logic Control Signals
Global Control Input Description
GSR Global Set/Reset: When High, asynchronously places all registers 
and flip-flops in their initial state. 
GTS Global 3-State: When High, asynchronously forces all I/O pins to a 
high-impedance state (High-Z, 3-state).
Send Feedback

--- Page 73 ---
7 Series FPGAs CLB User Guide www.xilinx.com 73
UG474 (v1.7) November 17, 2014Devices Using Stacked Silicon Interconnect (SSI) Technology
STARTUPE2 Primitive
The GSR and GTS signal sources are defined and connected using the STARTUPE2 
primitive. This primitive allows the user to define the source of these dedicated nets. GSR and GTS are always active during configurat ion, and connecting signals to them on the 
STARTUPE2 primitive defines how they are cont rolled after configuration. By default, 
they are disabled after configuration on a se lected clock cycle of the start-up phase, 
enabling the flip-flops and I/Os in the de vice. The STARTUPE2 primitive also includes 
other signals used specifically during config uration. For more information, refer to the 
UG470
, 7 Series FPGAs Configuration User Guide .
Interconnect Optimization
Interconnect delays vary according to the spec ific implementation and loading in a design. 
The type of interconnect, distance required to  travel in the device, and number of switch 
matrices to traverse factor into the total delay. Most timing issues are addressed by 
examining the block delays and determining the impact of using fewer levels or faster paths. If interconnect delays seem too long , increase implementation effort levels or 
iterations to improve performance along with making sure that the required timing is in the constraints file.
Nets with critical timing or that are heavily loaded can often be improved by replicating 
the source of the net. The dual 5-input LU T configuration of the slice simplifies the 
replication of logic in the same slice, which minimizes any additional loads on the inputs to the source function. Replicating logic in multip le slices gives the software more flexibility 
to place the sources independently.
Floorplanning is the process of specifying us er-placement constraint s. Floorplanning can 
be done either before or after automatic plac e and route, but automatic place and route is 
always recommended first before specif ying user floorplanning. The Xilinx 
implementation tool provides a graphical view  of placement. It helps the designer choose 
between RTL coding and synthesis and implemen tation, with extensive design exploration 
and analysis features. 
Devices Using Stacked Silicon Interconnect (SSI) Technology
As noted in the DS180 , 7 Series FPGAs Overview , some of the Virtex-7 devices use stacked 
silicon interconnect (SSI) technology. These de vices provide a unique additional type of 
interconnect resource called a super long line  or SLL. These special routing resources can 
be treated like other interconnect resources as they are abundant (more than 10,000) and 
fast (about 1 ns). The SLL provides a connection between super logic regions (SLRs), as shown in Figure 6-3 . Combining multiple SLRs effectively increases the height of the 
ASMBL™ architecture columns and increases the overall capacity of the device. The 
software can be allowed to take  best advantage of this conf iguration, or users can apply 
floorplanning to control placement within and between SLRs. Note that carry logic 
cascading is limited to within an SLR and do es not continue through the SLL connections. 
The same is true of other types of cascading including block RAM, DSP , and DCI. Boundaries are visible in floorplanning tools and reported in timing reports. The number 
of SLRs per Virtex-7 device is listed in the 7 Series FPGAs Overview .
Send Feedback

--- Page 74 ---
74 www.xilinx.com 7 Series FPGAs CLB User Guide
UG474 (v1.7) November 17, 2014Chapter 6: Advanced Topics
Designs targeting devices using SSI technology only require one STARTUPE2 
instantiation. One source for GSR and GTS si gnals propagates across the SLR boundaries 
to all elements of the device.
Optimization for devices using SSI technology can start with the same techniques as for 
any standard device, including using proper design techniques, timing constraints or 
options to automatically find the best implem entation. Floorplanning for these devices can 
use the same graphical tools.
For more information on devices usin g SSI technology, see the following:
DS180 , 7 Series FPGAs Overview
 Stacked Silicon Interconnect Technology page 
www.xilinx.com/technology/roadm ap/stacked-silic on-interconnect
WP380 , Xilinx Stacked Silicon Interconnect Technology Delivers Breakthrough FPGA 
Capacity, Bandwidth, and Power EfficiencyX-Ref Target - Figure 6- 3
Figure 6-3: Stacked Silicon Interconnect TechnologySuper Logic
Region (SLR)
Super Logic
Region (SLR)Super Long
Line (SLL)
UG474_c6_03_090211
Send Feedback

