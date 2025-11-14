
--- 第 1 页 ---
1Introduction to
CMOS VLSI
Design
VLSI Design Rules
Peter Kogge
University of Notre Dame
Fall 2011, 2012, 2015, 2018
Based on material from
Prof. Jay Brockman, Joesph Nahas, University of Notre Dame
Prof. David Harris, Harvey Mudd College
http://www.cmosvlsi.com /coursematerials.html
CMOS VLSI Design Design Rules Slide 2Outline
Overview
Determining Design Rules and Mask Biases
Design Rules
Circuit Interconnect Layout

--- 第 2 页 ---
2CMOS VLSI Design Design Rules Slide 3Layout Overview
Minimum dimensions of mask 
features determine:
–transistor size and die size 
–hence speed, cost, and power
“Historical” Feature size f= 
gate length (in nm)
–Set by minimum width of 
polysilicon
–Other minimum feature sizes 
tend to be 30 to 50% bigger.
Design orLayout Rules : rules 
for designing masks based on minimum feature sizes
Rules often “normalized” for 
portability across generationsn+ n+
p-type bodyW
Ltox
SiO2 gate o
(good insulator, polysilicon
gate
CMOS VLSI DesignWhat Are Typical Rules
Length & Width of Transistor gate
Separation between 2 wires on same level
Width of wires
Contact pad for Vias
Cross section of Vias
Size of Wells
…
Design Rules Slide 4

--- 第 3 页 ---
3CMOS VLSI Design Design Rules Slide 5Feature Size
Feature size improves 30% every 2 years or so
–1/√2 = 0.7 reduction factor every “generation”
–from 1 μm (1000 nm) in 1990 to 14 nm in 2015.
–10 generations in 20 years
•1000, 700, 500, 350, 250, 180, 130, 90, 65, 45, 32, 22, 14, 10 nm
0102030405060708090
2005 2010 2015 2020 2025 2030Feature Size (nm)
2013 ITRS Xeon Data Top10
2006 ITRS Xeon Line Top10  Projection
CMOS VLSI DesignDetermining a Design Rule
and a Mask Bias
Design Rules Slide 6

--- 第 4 页 ---
4CMOS VLSI DesignDetermining a Design Rule
What is the minimum spacing between a poly 
gate and a contact? What does it depend on?
Design Rules Slide 7GND VDDYA
substrate tap well tapnMOS transistor pMOS transistor?
CMOS VLSI DesignFactors Determining a Design Rule
Mask alignment accuracy
–How accurate is one mask aligned to another mask?
Process variation
–If cutting a hole, how much do sides of the cut vary?
–If implanting dopants, how much does the width of the 
diffusion vary?
How conservative do you need to be to assure 
good process yield?
–30 to 40 mask levels
–5 to 10 process steps per mask level
Design Rules Slide 8

--- 第 5 页 ---
5CMOS VLSI Design L03 Semiconductor Processing Slide 9Mask Sequence
Align each mask to the previous mask
1. n-well
2. Polysilicon
3. n+ active (diffusion)
4. p+ active (diffusion)
5. Contact
6. Metal
MetalPolysilicon
Contactn+ Diffusion
p+ Diffusionn well
CMOS VLSI DesignAlignment Marks
Alignment Marks:
How close can one mask be aligned to another in a 0.5 μm process ?
Example:
–Mean: 0 nm
–Standard Deviation: 50 nm
•1σ = 50 nm = 84%
•2σ = 100 nm = 98%
•3σ = 150 nm = 99.87%
But alignment is not direct
–Contact aligns to P+active
–P+active aligns to N+active
–N+active aligns to poly
How much variation is the alignment from Contact to Poly?
Design Rules Slide 10P
o
l
y
VariationContact

--- 第 6 页 ---
6CMOS VLSI DesignPoly Variation
How much does the width of the poly vary with 
processing?
Example: (Again 0.5 μm)
–Mean (one side) = - 60 nm (undercut)
–Standard Deviation (one side) = 30 nm
–3σ = 90 nm
Design Rules Slide 11SiliconPolyResist
Undercut
500 nmMask biased to compensate
for mean undercut?
CMOS VLSI DesignContact Hole Variation
How much does the size of the contact hole vary?
Example:
–Mean = + 50 nm
–Standard Deviation = 40 nm
–3σ = 120 nm
Design Rules Slide 12SiliconSiO2Resist
UndercutSiO2Resist?
600nmMask biased to compensate
for mean undercut

--- 第 7 页 ---
7CMOS VLSI DesignMinimum Oxide Width
Cannot have source or drain short to the gate.
–What is minimum spacing with variation?
–Example: 200 nm
Design Rules Slide 13SiliconSiO2
PolyAlSiO2WMIN
Diffusion Region ChannelVIA
Contact
GATE
CMOS VLSI DesignDesign Rule Summary
Mask Alignment
–3σ variation is √3 * 150 nm = 260 nm
Poly Variation
–3σ = 90 nm
Contact Variation
–3σ = 120 nm
Minimum Contact-to-Poly Breakdown Space
–200 nm
If we simply sum the minimum and variations:
–670 nm
Is this the “correct” value for the rule? What is “correct”?
Design Rule:
– nm
Why?
Design Rules Slide 14

--- 第 8 页 ---
8CMOS VLSI DesignHow can the rule be improved?
Change alignment sequence.
–Align poly to n-well
–Align n+active to poly
–Align p+active to poly
–Align contact to poly
–Align metal to contact
Change alignment from t3 to t1
–Alignment variation reduces from 260 nm to   150 nm
Design Rule changes from  500nm to  400nm
Design Rules Slide 15
CMOS VLSI DesignWhat do you do with Biases?
Layout is done without biases.
Biases are added post layout in mask processing.
Example: Contacts
Design Rules Slide 16600 nm 600 nmLayout
600 nm
500 nm 500 nmMask
Contact is shrunk by 50 nm on each side during Mask Making process
700 nm

--- 第 9 页 ---
9CMOS VLSI DesignCircuit Interconnect Layout
Design Rules Slide 17
CMOS VLSI Design Design Rules Slide 18Simplified CMOS Process
p silicon substraten welln diffusiongate oxideSiO2
SiO2polysilicon
p diffusionNMOS PMOS field
oxide


--- 第 10 页 ---
10CMOS VLSI Design Design Rules Slide 19Wiring with Metal and Contacts
metal (Al)
NMOS PMOS
contact cut
CMOS VLSI Design Design Rules Slide 20Transistors of Same Type in Series
NMOS NMOS
can’t do this with opposite types!
connected by shared diffusion

--- 第 11 页 ---
11CMOS VLSI Design Design Rules Slide 21Connecting Poly and Diffusion
can’t contact poly to  diffusion directly!
NMOS NMOS
CMOS VLSI DesignThe Book’s 65nm Process
Design Rules Slide 22

--- 第 12 页 ---
12CMOS VLSI DesignThe Book’s 65nm Process
- Up to Metal 2
Design Rules Slide 23
CMOS VLSI DesignThe Book’s 65nm Process
- Metals
Design Rules Slide 24


--- 第 13 页 ---
13CMOS VLSI Design65nm Design Rules (Page 1)
Design Rules Slide 25Rule Description65nm
(nm)
1.1 Width 500
1.2 Space  to well at different potential 700
1.3 Space  to well at same potential 700
2.1 Width 100
2.2  Spacing to active 120
2.3 Source/drain  surround by well 150
2.4 Substrate/well  contact surround by well 150
2.5 Spacing  to active of opposite type 250
3.1 Width 65
3.2 Spacing  to poly over field oxide 100
3.2a Spacing  to poly over active 100
3.3 Gate  extension  beyond active 100
3.4 Active  extension  beyond poly 100
3.5 Spacing  of poly to active 70
4.1 Spacing  from substrate/well  to gate 150
4.2 Overlap  by poly or active 120
4.3 Overlap  of substrate/well  contact 120
4.4 Spacing  to select 200WellActive
(diffusion)Poly (i.e. 
Gate)Select
(n or p)
CMOS VLSI Design65nm Design Rules (Page 2)
Design Rules Slide 26Rule Description65nm
(nm)
5.1, 6.1 Width  (exact) 80
5.2b, 6.26 Overlap  by poly or active 10
5.3, 6.3 Spacing  to contact 100
5.4, 6.4 Spacing  to gate 70
5.5b Spacing  of poly contact to other contact
5.7b, 6.7b Spacing  to active/poly  for mult. Contacts
6.8b Spacing  of active contact to poly contact
7.1 Width 90
7.2 Spacing  to same layer of metal 90
7.3,8.3 Overlap  of contact or via 10
7.4 Spacing to metal for lines wider than 10λ 300
9.1…. Width 100
9.2, …S p a c i n g  to same layer of metal 100
9.3, …O v e r l a p  of contact or via 10
9.4, … Spacing to metal for lines wider than 10λ 300
15.1 Width 100
15.2 Spacing  to metal3 100
15.3 Overlap  of via2 10
15.4 Spacing to metal for lines wider than 10λ 300
15.1 Width 400
15.2 Spacing  to metal3 400
15.3 Overlap  of via2 100
15.4 Spacing to metal for lines wider than 10λ 500
8.1,14.1 Width  (exact) 100
8.2.14.2 Spacing  to via on same layer 100
8.1,14.1 Width  (exact) 100
8.2.14.2 Spacing  to via on same layer 100
8.1,14.1 Width  (exact) 200
8.2.14.2 Spacing  to via on same layer 200Via
7,8Metal1Via1Via2Metal3 Metal2Metal
8‐9Via
3…6Contact (to
poly or active)

--- 第 14 页 ---
14CMOS VLSI DesignA Simplified Rule System
λ Rules
Design Rules Slide 27
CMOS VLSI Designλ Rules
A simplified, technology generations independent design rule 
system:
Express rules in terms of λ = f/2
–E.g. λ = 0.3 mm in 0.6 mm process
Called “ Lambda rules ”
Lambda rules NOT used in commercial applications
–Lambda rules need to be very conservative and thus waste 
space.
Lambda rules good for education! 
–MOSIS SCMOS SUMB Rules
–See Book Front Inside Cover
Design Rules Slide 28

--- 第 15 页 ---
15CMOS VLSI Design Design Rules Slide 29Simplified Design Rules
Conservative rules to get you started
–See Fig. 1.39
2 λMissing Rule
Poly to Dif Contact
http://www.cse.nd.edu/courses/cse60462/www/links.html
CMOS VLSI DesignTransistor Width and Length
Design Rules Slide 30
Transistor Length
Parallel to
direction carriers
travelTransistor Width
Perpendicular to
direction carriers
travel.
Typically Width >> LengthDimensions of Gate o ver Source/Drain Diffusion
This is the active ar ea of a transistor.

--- 第 16 页 ---
16CMOS VLSI Design
Substrate and Well Taps
Substrate needs to be tied to Ground.
–Why?
N-well needs to be tied to VDD.
–Why?
Design Rules Slide 31
CMOS VLSI DesignλRules (compared to 65 nm)
Design Rules Slide 32Rule Description65nm
(nm)Eqvt
65nm in λ180 130 90 65 45 32 28 22 10
1.1 Width 500 390 12 1080 780 540 390 270 192 168 132 60
1.2 Space  to well at different potential 700 585 18 1620 1170 810 585 405 288 252 198 90
1.3 Space  to well at same potential 700 195 6 540 390 270 195 135 96 84 66 30
2.1 Width 100 98 3 270 195 135 98 68 48 42 33 15
2.2  Spacing to active 120 98 3 270 195 135 98 68 48 42 33 15
2.3 Source/drain  surround by well 150 195 6 540 390 270 195 135 96 84 66 30
2.4 Substrate/well  contact surround by well 150 98 3 270 195 135 98 68 48 42 33 15
2.5 Spacing  to active of opposite type 250 130 4 360 260 180 130 90 64 56 44 20
3.1 Width 65 65 2 180 130 90 65 45 32 28 22 10
3.2 Spacing  to poly over field oxide 100 98 3 270 195 135 98 68 48 42 33 15
3.2a Spacing  to poly over active 100 98 3 270 195 135 98 68 48 42 33 15
3.3 Gate  extension  beyond active 100 65 2 180 130 90 65 45 32 28 22 10
3.4 Active  extension  beyond poly 100 98 3 270 195 135 98 68 48 42 33 15
3.5 Spacing  of poly to a c t i v e 7 0 3 3 1 9 0 6 5 4 53 32 31 61 41 1 5
4.1 Spacing  from substrate/well  to gate 150 98 3 270 195 135 98 68 48 42 33 15
4.2 Overlap  by poly or active 120 65 2 180 130 90 65 45 32 28 22 10
4.3 Overlap  of substrate/well  c o n t a c t 1 2 0 3 3 1 9 0 6 5 4 53 32 31 61 41 1 5
4.4 Spacing  to select 200 65 2 180 130 90 65 45 32 28 22 10WellActive
(diffusion)Poly (i.e. 
Gate)Select
(n or p)Lambda Rules
Green: lambda rules significantly smaller
Red: lambda rules significantly larger

--- 第 17 页 ---
17CMOS VLSI DesignλRules (compared to 65 nm)
Design Rules Slide 33Rule Description65nm
(nm)Eqvt
65nm in λ180 130 90 65 45 32 28 22 10
5.1, 6.1 Width  (exact) 80 65 2 180 130 90 65 45 32 28 22 10
5.2b, 6.26 Overlap  by poly or a c t i v e 1 0 3 3 1 9 0 6 5 4 53 32 31 61 41 1 5
5.3, 6.3 Spacing  to contact 100 98 3 270 195 135 98 68 48 42 33 15
5.4, 6.4 Spacing  to gate 70 65 2 180 130 90 65 45 32 28 22 10
5.5b Spacing  of poly contact to other contact 163 5 450 325 225 163 113 80 70 55 25
5.7b, 6.7b Spacing  to active/poly  for mult. Contacts 98 3 270 195 135 98 68 48 42 33 15
6.8b Spacing  of active contact to poly contact 130 4 360 260 180 130 90 64 56 44 20
7.1 Width 90 98 3 270 195 135 98 68 48 42 33 15
7.2 Spacing  to same layer of metal 90 98 3 270 195 135 98 68 48 42 33 15
7.3,8.3 Overlap  of contact or via 10 33 1 90 65 45 33 23 16 14 11 5
7.4 Spacing to metal for lines wider than 10λ 300 195 6 540 390 270 195 135 96 84 66 30
9.1…. Width 100 98 3
9.2, …S p a c i n g  to same layer of metal 100 98 3
9.3, …O v e r l a p  of contact or via 10 33 1
9.4, … Spacing to metal for lines wider than 10λ 300 195 6
15.1 Width 100 163 5 450 325 225 163 113 80 70 55 25
15.2 Spacing  to metal3 100 98 3 270 195 135 98 68 48 42 33 15
15.3 Overlap  of via2 10 65 2 180 130 90 65 45 32 28 22 10
15.4 Spacing to metal for lines wider than 10λ 300 195 6 540 390 270 195 135 96 84 66 30
15.1 Width 400 0 0 0 0 0 0 0 0 0
15.2 Spacing  to m e t a l 3 4 0 0 0 0 0000000
15.3 Overlap  of v i a 2 1 0 0 0 0 0000000
15.4 Spacing to metal for lines wider than 10λ 5 0 0 0 0 0000000
8.1,14.1 Width  (exact) 100 65 2 180 130 90 65 45 32 28 22 10
8.2.14.2 Spacing  to via on same layer 100 98 3 270 195 135 98 68 48 42 33 15
8.1,14.1 Width  ( e x a c t ) 1 0 0 0 0 0000000
8.2.14.2 Spacing  to via on same l a y e r 1 0 0 0 0 0000000
8.1,14.1 Width  ( e x a c t ) 2 0 0 0 0 0000000
8.2.14.2 Spacing  to via on same l a y e r 2 0 0 0 0 0000000Via
7,8Metal1Via1Via2Metal3 Metal2Metal
8‐9Via
3…6Contact (to
poly or active)
