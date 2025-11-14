
=== 第 1 页 ===
Measuring various types
of low-frequency noise in
DC/DC switching converters
Varun John
Validation Engineer
Texas Instruments

=== 第 2 页 ===
Power-supply noise levels are critical in applications
like phase-locked loops (PLLs), voltage-controlled
oscillators (VCOs), analog-to-digital converters
(ADCs) and amplifiers.
In telecommunication networks, the upconversion Flicker noise originates as a result of the modulation
of low-frequency noise injected from the power of the conductance of a channel. Equation 1
supplies of local oscillators and amplifiers to the expresses the conductance ( ) of a semiconductor
intermediate frequency (IF) level during mixing with as a product of the carrier concentration and
σ
the radio frequency (RF) signal results in sideband mobility:
formation on both sides of the IF, leading to higher σ=q(nµ + pµ ) (1)
e h
phase noise. Phase noise adds to root-mean-
where q is the charge of an electron; n and p are the
square (RMS) phase error during the detection
concentrations of electrons and holes, respectively;
of digitally modulated signals, thereby limiting
and µ and µ are the electron and hole mobility in
the performance of the network [1]. This white e h
the material, respectively.
paper explains sources of low-frequency noise
in bipolar junction transistors (BJTs), metal-oxide Two models in literature try to explain modulation:
semiconductor field-effect transistors (MOSFETs) A number fluctuation model developed by
σ
and resistors, and how this noise propagates to McWhorter in 1957 [2] and a mobility fluctuation
the output voltage of a DC/DC converter. I’ll also model developed by Hooge in 1969 [3].
show you a setup for measuring the low-frequency The McWhorter model states that flicker noise is
noise spectrum of the output voltage of a DC/DC a surface phenomenon that originates from the
converter and use that setup to compare a low- variation of carrier concentrations caused by charge
frequency noise-optimized DC/DC converter’s noise trapping in surface states. Figure 1 shows the
spectrum with a standard DC/DC converter. energy-band diagram of an N-channel metal-oxide
semiconductor (NMOS) in inversion.
Types of low-frequency noise
The different types of noise in integrated circuits Metal SiO2 p-Si
(ICs) include flicker noise, thermal noise, shot noise,
SiO2 Bulk Traps
popcorn noise and generation-recombination noise.
Flicker noise and thermal noise dominate the low-
frequency output voltage noise spectrum of a DC/
EF
DC converter.
Interface
Traps
Flicker noise
Flicker noise, also known as 1/f noise, has been
observed in all electronic devices under biasing, for
Figure 1. Energy band diagram of an NMOS in inversion.
frequencies from 10-6Hz to a few hundreds of hertz.
Measuring low-frequency noise in DC/DC switching converters 2 January 2018

=== 第 3 页 ===
Due to the imperfect interface between the silicon Shot noise
(Si) and silicon dioxide (SiO ), there exist traps
2 Shot noise is a fluctuation in current caused by the
or intermediate energy states in the bandgap of
discrete structure of charges composing it. Current
the Si-SiO interface. Defects in SiO also lead to
2 2 flowing across a potential barrier is not uniform,
bulk SiO traps. When applied to MOSFETs, the
2 but comprises individual carriers arriving at random
McWhorter theory states that the traps cause the
times. The noise spectral density of shot noise
trapping and release of carriers from the channel,
given by Equation 3 is independent of temperature
thus causing a shift in the threshold voltage (V)
t but proportional to the current flowing through the
and a fluctuation in carrier concentration [4] [5] [6].
junction:
The time constants for these transitions depend
on the trap’s distance from the surface. Traps that l2=2qIΔf
sh (3)
are much farther away have a smaller probability of
where I is the junction current.
trapping carriers.
Shot noise is modeled as a current source
In Hooge’s mobility fluctuation model, flicker noise
connected in parallel to the small-signal junction
in semiconductor devices arises mainly from two
resistance. It is generally a low-noise contributor
carrier-scattering mechanisms: scattering in the
due to the low current in the reference system of a
semiconductor lattice and scattering from impurities.
DC/DC converter.
This model is more suitable to explain flicker noise in
Other sources of low-frequency noise in
BJTs, whereas the McWhorter model better explains
semiconductors include popcorn noise, also known
flicker noise in MOSFETs.
as burst noise, or random-telegraph-signal (RTS)
Thermal noise and generation-recombination noise. The RMS
values of these noise sources are lower when
Random charge carrier motion caused by thermal
compared to flicker and thermal noises for well-
excitation in a resistive medium results in voltage
fluctuations known as thermal noise. Thermal noise,
establish
l
e2d
+
fa
l
b2rication technologies.
thd 1/fb
also known as Johnson noise, is broadband white
BJT and MOSFET noise models
noise. Equation 2 gives the spectral density of
l2
Figure 2s hshows equivalent BJT and MOSFET
thermal noise across a resistor of resistance (R):
device models with noise sources included. In BJTs,
V th 2=4kT R×Δf (2) the basel s 2 h la b y+erl 1 2 h / a fb s a certain resistance (r b ) that adds
thermal noise. This can be modeled as a voltage
where k is the Boltzman constant, T is the absolute
temperature, ∆f is the frequency bandwidth and 4kT source v 2 in series with r b .
thr
b
is equal to 1.61 × 10-20 VC at room temperature. The base current in a BJT is the result of carrier
injection from emitter to base and the recombination
Thermal noise is often modeled as a voltage source r
b
of these carriers in the base. These two processes
in series with the resistor. A 50Ω resistor at room
are independent random events and thus have shot
temperature has an associated noise voltage source
noise associated with them. The base current also
of about 1nV/√Hz, but this value increases with
has flicker noise from scattering mechanisms in the
resistance.
base.
Measuring low-frequency noise in DC/DC switching converters 3 January 2018

=== 第 4 页 ===
l2 +l2
thd 1/fb
l2
sh
You can combine these two noise sources, TPS63710) to a standard DC/DC buck converter
represented by a current source l 2 +l2 in (the TPS54622) that doesn’t have any special noise-
shb 1/fb
parallel with the base-emitter junction. The collector filtering schemes.
current is made up of carriers diffu
v
s2ing through the
Since the TPS63710 is an inverting DC/DC
thrb
base-emitter junction and accelerated by the field
converter that gives a negative output voltage for a
across the collector-base junction. The diffusion
r positive input voltage, the TPS54622 is configured
b
current is a random process and is a source of shot
as an inverting buck-boost converter. Interchanging
noise in the collector current. This is modeled as
the V and GND pins configures a buck converter
OUT
a current source in parallel to the collector-emitter
as an inverting buck-boost. Changing the FB
terminals.
resistor accordingly achieves the right output
For MOSFETs, in addition to flicker noise, the voltage. Reference [8] gives a detailed description
resistance between drain and source causes on configuring a buck converter as a buck-boost.
thermal noise generated in the channel. You can
Figure 3 shows the low-noise reference system of
combine the thermal and flicker noise together as
the TPS63710. External feedback resistors R and
1
a current source l2 +l2 in parallel to the drain-
thd 1/fb R and internal bandgap voltage (V ) set the value
2 BG
source terminals.
of the reference voltage (V ). The voltage at V is
REF REF
l2 C D negative and lower than the output voltage by the
sh
gain factor of the error amplifier. A resistor-capacitor
v2
B r b thrb l2 +l2 (RC) filter made up of an internal 100K resistor and
shb 1/fb
l2 l2 +l2 an external capacitor on the CAP pin filters the
sh G thd 1/fb
l s 2 hb +l 1 2 /fb v2 noise from the V REF pin. The voltage on the CAP pin
thrb
is the low-noise reference of the error amplifier. The
output voltage Vout is reduced internally to 0.9*V
r E S OUT
b before serving as the negative input of the error
Figure 2. Equivalent BJT and MOSFET noise models.
amplifier. The low gain (1/0.9) configuration of the
error amplifier ensures that the noise from the error
Low-frequency output voltage noise
amplifier is not gained up.
in DC/DC converters
Error
The low-frequency noise in the output voltage of Amplifier
DC/DC converters comes from the supply of the
- V REF CAP
reference system and the internal transistors and V BG + SW L
100k Ω
resistors used in the reference system. This paper R 1 C CAP
C
OUT
compares the low-frequency output noise spectral
FB Noise
density of a DC/DC converter with a specially Filter
designed low-noise reference system (the R 2 V OUT
Figure 3. TPS63710 low-noise reference system.
Measuring low-frequency noise in DC/DC switching converters 4 January 2018

=== 第 5 页 ===
R=1k Ω
2
Spectrum
-3V Analyzer
C=200 µF
3
R=10 Ω 50 Ω
1
-
C=0.3 µF
5
OPA842
C=0.3 F
2 FFT Signal
Battery DC/DC + Analyzer
FFT
C 1 =2.2 mF R 3 =50 Ω +3V C 4 =200 µF
50 Ω
Figure 4. Noise measurement setup.
Measurement setup for low- decade below the lowest measurable frequency. For
frequency noise example, a 0.3F capacitor with a 50Ω termination
sets the corner frequency to 10mHz, with the lowest
Figure 4 shows a setup for measuring the output
possible measurable frequency 100mHz.
voltage-noise spectrum of a DC/DC converter.
You can measure the noise spectrum either with a Setting the OPA842 low-noise operational amplifier
heterodyne spectrum analyzer or a signal analyzer in a noninverting configuration with a gain of 100
using the fast Fourier transform (FFT) function. amplifies the output voltage noise of the DC/DC
I used a HP35670 FFT signal analyzer for the converter over the noise floor of the signal analyzer.
measurements shown in this paper because of the The HP35670 signal analyzer’s noise floor was
limitation of the spectrum analyzer to measure very measured at around 300nV/√Hz.
low frequencies. It is important to not use large resistors at the
I recommend supplying the DC/DC converter and inverting input of the op amp to avoid high thermal
the operational amplifier (op amp) used in the setup noise injection. Another high-pass filter at the output
with a battery at the input of the DC/DC converter of the op amp made up of C and the 50 Ω internal
5
to eliminate noise from the input power supply. termination of the analyzers filters any DC offset at
Due to the limitations of the battery to supply high the op amp’s output.
currents to the DC/DC converter, you could also Figure 5 shows the noise spectral density of the
use a low-noise bench power supply instead if the output voltages of the TPS63710 and TPS54622.
DC/DC converter under test has a high enough Both devices were supplied from a 6.5V battery
power-supply rejection ratio (PSRR) in the frequency source and V was set to –1.8V using the FB
OUT
band being measured. Most spectrum and signal divider resistors. A 10µF capacitor on the CAP pin
analyzers only allow zero or very low DC voltage of the TPS63710 performed noise filtering. You
levels at their input. This necessitates the use of can see that thermal noise dominates the noise
a DC blocker or high-pass filter at the DC/DC spectrum of both devices from 1kHz upward. At
converter output. lower frequencies, the influence of flicker noise
Choose the capacitance C so that the corner starts increasing, dominating the total noise
2
frequency of the C -R high-pass filter is at least one spectrum at very low frequencies.
2 3
Measuring low-frequency noise in DC/DC switching converters 5 January 2018

=== 第 6 页 ===
References
1) Matt Loy. “Understanding and Enhancing
Sensitivity in Receivers for Wireless
Applications.” Texas Instruments Technical
Brief (SWRA30), May 1999.
2) Alan L. McWhorter. “1/f noise and germanium
surface properties.” Semiconductor Surface
Physics, University of Pennsylvania Press
(Philadelphia, Pennsylvania), 1957: 207-228.
3) F.N. Hooge. “1/f noise sources.” IEEE
Transactions on Electron Devices 41, No. 11
(November 1994): 1926-1935.
Figure 5. Noise spectral density of the output voltage of TI’s
4) G. Reimbold. “Modified 1/f trapping noise theory
TPS54622 and TPS63710.
and experiments in MOS transistors biased from
Conclusion weak to strong inversion – influence of interface
states.” IEEE Transactions on Electron Devices 31,
Low-frequency noise from power supplies can limit
No. 9 (September 1984): 1190-1198.
the performance of noise-sensitive applications like
telecommunications networks. Flicker and thermal 5) Kent H. Lundberg. “Noise Sources in Bulk
noise dominates the noise in the output voltage CMOS,” 2002.
spectrum of DC/DC converters. The low-noise
6) Alicia Konczakowska and Bogdan M.Wilamowski.
reference system of the TPS63710, in combination
“Noise in Semiconductor Devices,” 2010.
with an external capacitor on the CAP pin, helps
7) Yannis Tsividis. “Operation and Modeling of
provide a negative output voltage with lower flicker
the MOS Transistor.” McGraw-Hill (New York,
and thermal noise levels.
New York), 1987.
8) Tahar Allag and Chris Glaser. “Using the
TPS6215x in An Inverting Buck-Boost Topology.”
Texas Instruments Application Report (SL
VA469C), November 2011 – Revised June 2013.
Important Notice: The products and services of Texas Instruments Incorporated and its subsidiaries described herein are sold subject to TI’s standard terms
and conditions of sale. Customers are advised to obtain the most current and complete information about TI products and services before placing orders. TI
assumes no liability for applications assistance, customer’s applications or product designs, software performance, or infringement of patents. The
publication of information regarding any other company’s products or services does not constitute TI’s approval, warranty or endorsement thereof.
The platform bar is a trademark of Texas Instruments.
All other trademarks are the property of their respective owners.
© 2018 Texas Instruments Incorporated SLYY134

=== 第 7 页 ===
IMPORTANT NOTICE FORTIDESIGNINFORMATIONANDRESOURCES
TexasInstrumentsIncorporated(‘TI”)technical,applicationorotherdesignadvice,servicesorinformation,including,butnotlimitedto,
referencedesignsandmaterialsrelatingtoevaluationmodules,(collectively,“TIResources”)areintendedtoassistdesignerswhoare
developingapplicationsthatincorporateTIproducts;bydownloading,accessingorusinganyparticularTIResourceinanyway,you
(individuallyor,ifyouareactingonbehalfofacompany,yourcompany)agreetouseitsolelyforthispurposeandsubjecttothetermsof
thisNotice.
TI’sprovisionofTIResourcesdoesnotexpandorotherwisealterTI’sapplicablepublishedwarrantiesorwarrantydisclaimersforTI
products,andnoadditionalobligationsorliabilitiesarisefromTIprovidingsuchTIResources.TIreservestherighttomakecorrections,
enhancements,improvementsandotherchangestoitsTIResources.
Youunderstandandagreethatyouremainresponsibleforusingyourindependentanalysis,evaluationandjudgmentindesigningyour
applicationsandthatyouhavefullandexclusiveresponsibilitytoassurethesafetyofyourapplicationsandcomplianceofyourapplications
(andofallTIproductsusedinorforyourapplications)withallapplicableregulations,lawsandotherapplicablerequirements.You
representthat,withrespecttoyourapplications,youhaveallthenecessaryexpertisetocreateandimplementsafeguardsthat(1)
anticipatedangerousconsequencesoffailures,(2)monitorfailuresandtheirconsequences,and(3)lessenthelikelihoodoffailuresthat
mightcauseharmandtakeappropriateactions.YouagreethatpriortousingordistributinganyapplicationsthatincludeTIproducts,you
willthoroughlytestsuchapplicationsandthefunctionalityofsuchTIproductsasusedinsuchapplications.TIhasnotconductedany
testingotherthanthatspecificallydescribedinthepublisheddocumentationforaparticularTIResource.
Youareauthorizedtouse,copyandmodifyanyindividualTIResourceonlyinconnectionwiththedevelopmentofapplicationsthatinclude
theTIproduct(s)identifiedinsuchTIResource.NOOTHERLICENSE,EXPRESSORIMPLIED,BYESTOPPELOROTHERWISETO
ANYOTHERTIINTELLECTUALPROPERTYRIGHT,ANDNOLICENSETOANYTECHNOLOGYORINTELLECTUALPROPERTY
RIGHTOFTIORANYTHIRDPARTYISGRANTEDHEREIN,includingbutnotlimitedtoanypatentright,copyright,maskworkright,or
otherintellectualpropertyrightrelatingtoanycombination,machine,orprocessinwhichTIproductsorservicesareused.Information
regardingorreferencingthird-partyproductsorservicesdoesnotconstitutealicensetousesuchproductsorservices,orawarrantyor
endorsementthereof.UseofTIResourcesmayrequirealicensefromathirdpartyunderthepatentsorotherintellectualpropertyofthe
thirdparty,oralicensefromTIunderthepatentsorotherintellectualpropertyofTI.
TIRESOURCESAREPROVIDED“ASIS”ANDWITHALLFAULTS.TIDISCLAIMSALLOTHERWARRANTIESOR
REPRESENTATIONS,EXPRESSORIMPLIED,REGARDINGTIRESOURCESORUSETHEREOF,INCLUDINGBUTNOTLIMITEDTO
ACCURACYORCOMPLETENESS,TITLE,ANYEPIDEMICFAILUREWARRANTYANDANYIMPLIEDWARRANTIESOF
MERCHANTABILITY,FITNESSFORAPARTICULARPURPOSE,ANDNON-INFRINGEMENTOFANYTHIRDPARTYINTELLECTUAL
PROPERTYRIGHTS.
TISHALLNOTBELIABLEFORANDSHALLNOTDEFENDORINDEMNIFYYOUAGAINSTANYCLAIM,INCLUDINGBUTNOT
LIMITEDTOANYINFRINGEMENTCLAIMTHATRELATESTOORISBASEDONANYCOMBINATIONOFPRODUCTSEVENIF
DESCRIBEDINTIRESOURCESOROTHERWISE.INNOEVENTSHALLTIBELIABLEFORANYACTUAL,DIRECT,SPECIAL,
COLLATERAL,INDIRECT,PUNITIVE,INCIDENTAL,CONSEQUENTIALOREXEMPLARYDAMAGESINCONNECTIONWITHOR
ARISINGOUTOFTIRESOURCESORUSETHEREOF,ANDREGARDLESSOFWHETHERTIHASBEENADVISEDOFTHE
POSSIBILITYOFSUCHDAMAGES.
YouagreetofullyindemnifyTIanditsrepresentativesagainstanydamages,costs,losses,and/orliabilitiesarisingoutofyournon-
compliancewiththetermsandprovisionsofthisNotice.
ThisNoticeappliestoTIResources.Additionaltermsapplytotheuseandpurchaseofcertaintypesofmaterials,TIproductsandservices.
Theseinclude;withoutlimitation,TI’sstandardtermsforsemiconductorproductshttp://www.ti.com/sc/docs/stdterms.htm),evaluation
modules,andsamples(http://www.ti.com/sc/docs/sampterms.htm).
MailingAddress:TexasInstruments,PostOfficeBox655303,Dallas,Texas75265
Copyright©2018,TexasInstrumentsIncorporated
