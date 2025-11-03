
=== 第 1 页 ===
CHAPTER I
BACKGROUND AND
OBJECTIVES
1.1 INTRODUCTION
An operational amplifier is a high-gain direct-coupled amplifier that is
normally used in feedback connections. If the amplifier characteristics are
satisfactory, the transfer function of the amplifier with feedback can often
be controlled primarily by the stable and well-known values of passive
feedback elements.
The term operational amplifier evolved from original applications in
analog computation where these circuits were used to perform various
mathematical operations such as summation and integration. Because of
the performance and economic advantages of available units, present
applications extend far beyond the original ones, and modern operational
amplifiers are used as general purpose analog data-processing elements.
High-quality operational amplifiers' were available in the early 1950s.
These amplifiers were generally committed to use with analog computers
and were not used with the flexibility of modern units. The range of opera­
tional-amplifier usage began to expand toward the present spectrum of
applications in the early 1960s as various manufacturers developed modu­
lar, solid-state circuits. These amplifiers were smaller, much more rugged,
less expensive, and had less demanding power-supply requirements than
their predecessors. A variety of these discrete-component circuits are cur­
rently available, and their performance characteristics are spectacular when
compared with older units.
A quantum jump in usage occurred in the late 1960s, as monolithic
integrated-circuit amplifiers with respectable performance characteristics
evolved. While certain performance characteristics of these units still do
not compare with those of the better discrete-component circuits, the inte­
grated types have an undeniable cost advantage, with several designs
available at prices of approximately $0.50. This availability frequently
justifies the replacement of two- or three-transistor circuits with operational
1 An excellent description of the technology of this era is available in G. A. Korn and
T. M. Korn, Electronic Analog Computers, 2nd Ed., McGraw-Hill, New York, 1956.

=== 第 2 页 ===
2 Background and Objectives
amplifiers on economic grounds alone, independent of associated perform­
ance advantages. As processing and designs improve, the integrated circuit
will invade more areas once considered exclusively the domain of the
discrete design, and it is probable that the days of the discrete-component
circuit, except for specials with limited production requirements, are
numbered.
There are several reasons for pursuing a detailed study of operational
amplifiers. We must discuss both the theoretical and the practical aspects
of these versatile devices rather than simply listing a representative sample
of their applications. Since virtually all operational-amplifier connections
involve some form of feedback, a thorough understanding of this process
is central to the intelligent application of the devices. While partially under­
stood rules of thumb may suffice for routine requirements, this design
method fails as performance objectives approach the maximum possible
use from the amplifier in question.
Similarly, an appreciation of the internal structure and function of opera­
tional amplifiers is imperative for the serious user, since such information
is necessary to determine various limitations and to indicate how a unit
may be modified (via, for example, appropriate connections to its com­
pensation terminals) or connected for optimum performance in a given
application. The modern analog circuit designer thus needs to understand
the internal function of an operational amplifier (even though he may
never design one) for much the same reason that his counterpart of 10 years
ago required a knowledge of semiconductor physics. Furthermore, this
is an area where good design practice has evolved to a remarkable degree,
and many of the circuit techniques that are described in following chapters
can be applied to other types of electronic circuit and system design.
1.2 THE CLOSED-LOOP GAIN OF AN OPERATIONAL
AMPLIFIER
As mentioned in the introduction, most operational-amplifier connec­
tions involve feedback. Therefore the user is normally interested in deter­
mining the closed-loop gain or closed-loop transferfunctionof the amplifier,
which results when feedback is included. As we shall see, this quantity can
be made primarily dependent on the characteristics of the feedback ele­
ments in many cases of interest.
A prerequisite for the material presented in the remainder of this book
is the ability to determine the gain of the amplifier-feedback network com­
bination in simple connections. The techniques used to evaluate closed-loop
gain are outlined in this section.

=== 第 3 页 ===
The Closed-Loop Gain of an Operational Amplifier 3
Vb
Figure 1.1 Symbol for an operational amplifier.
1.2.1 Closed-Loop Gain Calculation
The symbol used to designate an operational amplifier is shown in Fig.
1.1. The amplifier shown has a differential input and a single output. The
input terminals marked - and + are called the inverting and the non-
invertinginput terminals respectively. The implied linear-region relationship
among input and output variables2 is
V, = a(V, - Vb) (1.1)
The quantity a in this equation is the open-loop gain or open-loop transfer
function of the amplifier. (Note that a gain of a is assumed, even if it is not
explicitly indicated inside the amplifier symbol.) The dynamics normally
associated with this transfer function are frequently emphasized by writ­
ing a(s).
It is also necessary to provide operating power to the operational ampli­
fier via power-supply terminals. Many operational amplifiers use balanced
(equal positive and negative) supply voltages. The various signals are
usually referenced to the common ground connection of these power sup­
2 The notation used to designate system variables consists of a symbol and a subscript.
This combination serves not only as a label, but also to identify the nature of the quantity
as follows:
Total instantaneous variables:
lower-case symbols with upper-case subscripts.
Quiescent or operating-point variables:
upper-case symbols with upper-case subscripts.
Incremental instantaneous variables:
lower-case symbols with lower-case subscripts.
Complex amplitudes or Laplace transforms of incremental variables:
upper-case symbols with lower-case subscripts.
Using this notation we would write v = V, + vi, indicating that the instantaneous value of
1
vi consists of a quiescent plus an incremental component. The transform of vi is Vi. The
notation Vi(s) is often used to reinforce the fact that Vi is a function of the complex vari­
able s.

=== 第 4 页 ===
4 Background and Objectives
plies. The power connections are normally not included in diagrams in­
tended only to indicate relationships among signal variables, since elimi­
nating these connections simplifies the diagram.
Although operational amplifiers are used in a myriad of configurations,
many applications are variations of either the inverting connection (Fig.
1.2a) or the noninverting connection (Fig. 1.2b). These connections com­
bine the amplifier with impedances that provide feedback.
The closed-loop transfer function is calculated as follows for the invert­
ing connection. Because of the reference polarity chosen for the inter­
mediate variable V.,
V, = -a V, (1.2)
z
2
z,
+ \ a Vo 0
K.
Vl
(a)
V
0
Vi
-I
(b)
Figure 1.2 Operational-amplifier connections. (a) Inverting. (b) Noninverting.

=== 第 5 页 ===
The Closed-Loop Gain of an Operational Amplifier 5
where it has been assumed that the output voltage of the amplifier is not
modified by the loading of the Z -Z network. If the input impedance of the
1 2
amplifier itself is high enough so that the Z -Z network is not loaded
1 2
significantly, the voltage V, is
Z2 Z1
V, = 2 Vi + V" (1.3)
(Z1 + Z2) (Z1 + Z2)
Combining Eqns. 1.2 and 1.3 yields
( aZs aZ1
V, = - V, V (1.4)
0
(Z1 + Z2) (Z1 + Z2)
or, solving for the closed-loop gain,
Vo -aZ /(Z + Z )
2 1 2
Vi 1 + [aZ /(Z + Z )]
1 1 2
The condition that is necessary to have the closed-loop gain depend
primarily on the characteristics of the Zi-Z network rather than on the
2
performance of the amplifier itself is easily determined from Eqn. 1.5. At
la(jo)Z
any frequency w where the inequality (jw)/[Z (jo) + Z (jO)] >> 1
1 1 2
is satisfied, Eqn. 1.5 reduces to
V 0(jw) Z2(jo)
Vi(jco) Z1(jo)
The closed-loop gain calculation for the noninverting connection is simi­
lar. If we assume negligible loading at the amplifier input and output,
V, = a(V- V,) = aVi - aZ) V 0 (1.7)
(Z1 + Z2)
or
V a
0 V, a (1.8)
- 1 + [aZ 1 /(Z 1 + Z 2 )]
This expression reduces to
V(jo) Zi(jW) + Z (jO)
2
Vi(jco) Z1(jo)
when ja(jo)Z1(jo)/[Z(jo) + Z (jw)]| >> 1.
1 2
The quantity
L aZi (1.10)
Z + Z
1 2

=== 第 6 页 ===
6 Background and Objectives
is the loop transmission for either of the connections of Fig. 1.2. The loop
transmission is of fundamental importance in any feedback system because
it influences virtually all closed-loop parameters of the system. For ex­
ample, the preceding discussion shows that if the magnitude of loop trans­
mission is large, the closed-loop gain of either the inverting or the non-
inverting amplifier connection becomes virtually independent of a. This
relationship is valuable, since the passive feedback components that deter­
mine closed-loop gain for large loop-transmission magnitude are normally
considerably more stable with time and environmental changes than is the
open-loop gain a.
The loop transmission can be determined by setting the inputs of a feed­
back system to zero and breaking the signal path at any point inside the
feedback loop.' The loop transmission is the ratio of the signal returned by
the loop to a test applied at the point where the loop is opened. Figure 1.3
indicates one way to determine the loop transmission for the connections
of Fig. 1.2. Note that the topology shown is common to both the inverting
and the noninverting connection when input points are grounded.
It is important to emphasize the difference between the loop transmission,
which is dependent on properties of both the feedback elements and the
operational amplifier, and the open-loop gain of the operational amplifier
itself.
1.2.2 The Ideal Closed-Loop Gain
Detailed gain calculations similar to those of the last section are always
possible for operational-amplifier connections. However, operational ampli­
fiers are frequently used in feedback connections where loop characteristics
are such that the closed-loop gain is determined primarily by the feedback
elements. Therefore, approximations that indicate the idealclosed-loop gain
or the gain that results with perfect amplifier characteristics simplify the
analysis or design of many practical connections.
It is possible to calculate the ideal closed-loop gain assuming only two
conditions (in addition to the implied condition that the amplifier-feedback
network combination is stable4) are satisfied.
1. A negligibly small differential voltage applied between the two input
terminals of the amplifier is sufficient to produce any desired output
voltage.
3There are practical difficulties, such as insuring that the various elements in the loop
remain in their linear operating regions and that loading is maintained. These difficulties
complicate the determination of the loop transmission in physical systems. Therefore, the
technique described here should be considered a conceptual experiment. Methods that are
useful for actual hardware are introduced in later sections.
4Stability is discussed in detail in Chapter 4.

=== 第 7 页 ===
The Closed-Loop Gain of an Operational Amplifier 7
Z Z
2
Input set to zero
if inverting connection
*:_ Input set to zero if
Test generator noninverting connection
Figure 1.3 Loop transmission for connections of Fig. 1.2. Loop transmission is
Vr/Vt = -a Z/(Z + Z ).
1 1 2
2. The current required at either amplifier terminal is negligibly small.
The use of these assumptions to calculate the ideal closed-loop gain is
first illustrated for the inverting amplifier connection (Fig. 1.2a). Since the
noninverting amplifier input terminal is grounded in this connection, condi­
tion 1 implies that
V,, 0 (1.11)
Kirchhoff's current law combined with condition 2 shows that
I. + Ib ~ 0 (1.12)
With Eqn. 1.11 satisfied, the currents I, and I are readily determined in
terms of the input and output voltages.
Vai
(1.13)
Z
1
Va
b (1.14)
Z2
Combining Eqns. 1.12, 1.13, and 1.14 and solving for the ratio of V, to Vi
yields the ideal closed-loop gain
V.V - Z2 (1.15)
Vi Z1
The technique used to determine the ideal closed-loop gain is called the
virtual-groundmethod when applied to the inverting connection, since in
this case the inverting input terminal of the operational amplifier is as­
sumed to be at ground potential.

=== 第 8 页 ===
8 Background and Objectives
The noninverting amplifier (Fig. 1.2b) provides a second example of
ideal-gain determination. Condition 2 insures that the voltage V,, is not
influenced by current at the inverting input. Thus,
Z
1
V1 ~ V (1.16)
0
Zi + Z
2
Since condition 1 requires equality between Ve, and Vi, the ideal closed-
loop gain is
Vo = ZZ1 + ZZ2(1.17)
0
Vi Z1
The conditions can be used to determine ideal values for characteristics
other than gain. Consider, for example, the input impedance of the two
amplifier connections shown in Fig. 1.2. In Fig. 1.2a, the inverting input
terminal and, consequently, the right-hand end of impedance Z , is at
1
ground potential if the amplifier characteristics are ideal. Thus the input
impedance seen by the driving source is simply Z . The input source is
1
connected directly to the noninverting input of the operational amplifier
in the topology of Fig. 1.2b. If the amplifier satisfies condition 2 and has
negligible input current required at this terminal, the impedance loading
the signal source will be very high. The noninverting connection is often used
as a buffer amplifier for this reason.
The two conditions used to determine the ideal closed-loop gain are
deceptively simple in that a complex combination of amplifier characteris­
tics are required to insure satisfaction of these conditions. Consider the
first condition. High open-loop voltage gain at anticipated operating fre­
quencies is necessary but not sufficient to guarantee this condition. Note
that gain at the frequency of interest is necessary, while the high open-loop
gain specified by the manufacturer is normally measured at d-c. This speci­
fication is somewhat misleading, since the gain may start to decrease at a
frequency on the order of one hertz or less.
In addition to high open-loop gain, the amplifier must have low voltage
offset5 referred to the input to satisfy the first condition. This quantity,
defined as the voltage that must be applied between the amplifier input
terminals to make the output voltage zero, usually arises because of mis­
matches between various amplifier components.
Surprisingly, the incremental input impedance of an operational ampli­
fier often has relatively little effect on its input current, since the voltage
that appears across this impedance is very low if condition 1 is satisfied.
I Offset and other problems with d-c amplifiers are discussed in Chapter 7.

=== 第 9 页 ===
The Closed-Loop Gain of an Operational Amplifier 9
A more important contribution to input current often results from the bias
current that must be supplied to the amplifier input transistors.
Many of the design techniques that are used in an attempt to combine the
two conditions necessary to approach the ideal gain are described in sub­
sequent sections.
The reason that the satisfaction of the two conditions introduced earlier
guarantees that the actual closed-loop gain of the amplifier approaches the
ideal value is because of the negative feedback associated with operational-
amplifier connections. Assume, for example, that the actual voltage out of
the inverting-amplifier connection shown in Fig. 1.2a is more positive than
the value predicted by the ideal-gain relationship for a particular input
signal level. In this case, the voltage V will be positive, and this positive
0
voltage applied to the inverting input terminal of the amplifier drives the
output voltage negative until equilibrium is reached. This reasoning shows
that it is actually the negative feedback that forces the voltage between
the two input terminals to be very small.
Alternatively, consider the situation that results if positive feedback is
used by interchanging the connections to the two input terminals of the
zi
1
+1 /~
Vi,?
-p1
Iz2
0
Vi
2
S
0
ZiN
iN
V 1 N
Figure 1.4 Summing amplifier.

=== 第 10 页 ===
10 Background and Objectives
amplifier. In this case, the voltage V is again zero when V and Vi are
0
related by the ideal closed-loop gain expression. However, the resulting
equilibrium is unstable, and a small perturbation from the ideal output
voltage results in this voltage being driven further from the ideal value
until the amplifier saturates. The ideal gain is not achieved in this case in
spite of perfect amplifier characteristics because the connection is unstable.
As we shall see, negative feedback connections can also be unstable. The
ideal gain of these unstable systems is meaningless because they oscillate,
producing an output signal that is often nearly independent of the input
signal.
1.2.3 Examples
The technique introduced in the last section can be used to determine the
ideal closed-loop transfer function of any operational-amplifier connec­
tion. The summing amplifier shown in Fig. 1.4 illustrates the use of this
technique for a connection slightly more complex than the two basic
amplifiers discussed earlier.
Since the inverting input terminal of the amplifier is a virtual ground, the
currents can be determined as
Vnl
1I1 =
Z
1
1i2 =Vi 2
2
liN ~ VN
Z N
i
=V 0
if = (1.18)
Zf
These currents must sum to zero in the absence of significant current at the
inverting input terminal of the amplifier. Thus
Iil + I + --- + IiN + If -9
2
Combining Eqns. 1.18 and 1.19 shows that
Zf Zf Zf
V 0 - - V n 2 - -V-i ViN (1.20)
Zul Z2 ZiN

=== 第 11 页 ===
The Closed-Loop Gain of an Operational Amplifier 11I
We see that this amplifier, which is an extension of the basic inverting-
amplifier connection, provides an output that is the weighted sum of several
input voltages.
Summation is one of the "operations" that operational amplifiers per­
form in analog computation. A subsequent development (Section 12.3) will
show that if the operations of gain, summation, and integration are com­
bined, an electrical network that satisfies any linear, ordinary differential
equation can be constructed. This technique is the basis for analog com­
putation.
Integrators required for analog computation or for any other application
can be constructed by using an operational amplifier in the inverting con­
nection (Fig. 1.2a) and making impedance Z a capacitor C and impedance
2
Z a resistor R. In this case, Eqn. 1.15 shows that the ideal closrd-loop
1
transfer function is
1.1
VJ(s) Z (s) 1
2
Vi(s) Z1(s) RCs
so that the connection functions as an inverting integrator.
It is also possible to construct noninverting integrators using an opera­
tional amplifier connected as shown in Fig. 1.5. This topology precedes a
noninverting amplifier with a low-pass filter. The ideal transfer function
from the noninverting input of the amplifier to its output is (see Eqn. 1.17)
_
V (s) RCs + 1 (1.22)
0
Va(S) RCs
Since the conditions for an ideal operational amplifier preclude input cur-
R,
0 +
C, V rV 0
C
Figure 1.5 Noninverting integrator.

=== 第 12 页 ===
12 Background and Objectives
VD
rD
R
VV
0
Figure 1.6 Log circuit.
rent, the transfer function from Vi to V, can be calculated with no loading,
and in this case
V.(s) 1 1.23)
Vi(s) R Cis + 1
1
Combining Eqns. 1.22 and 1.23 shows that the ideal closed-loop gain is
1
V(s) = 1 FRCs + 11 (1.24)
0
Vi(s) R C s + I RCs _
1 1
If the two time constants in Eqn. 1.24 are made equal, noninverting inte­
gration results.
The comparison between the two integrator connections hints at the
possibility of realizing most functions via either an inverting or a non-
inverting connection. Practical considerations often recommend one ap­
proach in preference to the other. For example, the noninverting integrator
requires more external components than does the inverting version. This
difference is important because the high-quality capacitors required for
accurate integration are often larger and more expensive than the opera­
tional amplifier that is used.
The examples considered up to now have involved only linear elements,
at least if it is assumed that the operational amplifier remains in its linear
operating region. Operational amplifiers are also frequently used in inten­
tionally nonlinear connections. One possibility is the circuit shown in Fig.
1.6.6 It is assumed that the diode current-voltage relationship is
iD = IS(eqvD/kT - 1) (1.25)
6 Note that the notation for the variables used in this case combines lower-case variables
with upper-case subscripts, indicating the total instantaneous signals necessary to describe
the anticipated nonlinear relationships.

=== 第 13 页 ===
Overview 13
where Is is a constant dependent on diode construction, q is the charge
of an electron, k is Boltzmann's constant, and T is the absolute temperature.
If the voltage at the inverting input of the amplifier is negligibly small,
the diode voltage is equal to the output voltage. If the input current is
negligibly small, the diode current and the current iR sum to zero. Thus,
if these two conditions are satisfied,
- R = Is(evolkT - 1) (1.26)
R
Consider operation with a positive input voltage. The maximum negative
value of the diode current is limited to -Is. If vI/R > Is, the current
through the reverse-biased diode cannot balance the current IR.Accordingly,
the amplifier output voltage is driven negative until the amplifier saturates.
In this case, the feedback loop cannot keep the voltage at the inverting
amplifier input near ground because of the limited current that the diode
can conduct in the reverse direction. The problem is clearly not with the
amplifier, since no solution exists to Eqn. 1.26 for sufficiently positive
values of vr.
This problem does not exist with negative values for vi. If the magnitude
of iR is considerably larger than Is (typical values for Is are less than 10-1
A), Eqn. 1.26 reduces to
- R~ Isero~kT (1.27)
R
or
kT - Vr
vo 1- In (1.28)
q \R1s
Thus the circuit provides an output voltage proportional to the log of the
magnitude of the input voltage for negative inputs.
1.3 OVERVIEW
The operational amplifier is a powerful, multifaceted analog data-proc­
essing element, and the optimum exploitation of this versatile building
block requires a background in several different areas. The primary objec­
tive of this book is to help the reader apply operational amplifiers to his
own problems. While the use of a "handbook" approach that basically
tabulates a number of configurations that others have found useful is
attractive because of its simplicity, this approach has definite limitations.
Superior results are invariably obtained when the designer tailors the circuit

=== 第 14 页 ===
14 Background and Objectives
he uses to his own specific, detailed requirements, and to the particular
operational amplifier he chooses.
A balanced presentation that combines practical circuit and system design
concepts with applicable theory is essential background for the type of
creative approach that results in optimum operational-amplifier systems.
The following chapters provide the necessary concepts. A second advan­
tage of this presentation is that many of the techniques are readily applied
to a wide spectrum of circuit and system design problems, and the material
is structured to encourage this type of transfer.
Feedback is central to virtually all operational-amplifier applications,
and a thorough understanding of this important topic is necessary in any
challenging design situation. Chapters 2 through 6 are devoted to feedback
concepts, with emphasis placed on examples drawn from operational-
amplifier connections. However, the presentation in these chapters is kept
general enough to allow its application to a wide variety of feedback sys­
tems. Topics covered include modeling, a detailed study of the advantages
and limitations of feedback, determination of responses, stability, and com­
pensation techniques intended to improve stability. Simple methods for the
analysis of certain types of nonlinear systems are also included. This in-
depth approach is included at least in part because I am convinced that a
detailed understanding of feedback is the single most important pre­
requisite to successful electronic circuit and system design.
Several interesting and widely applicable circuit-design techniques are
used to realize operational amplifiers. The design of operational-amplifier
circuits is complicated by the requirement of obtaining gain at zero fre­
quency with low drift and input current. Chapter 7 discusses the design
of the necessary d-c amplifiers. The implications of topology on the dy­
namics of operational-amplifier circuits are discussed in Chapter 8. The
design of the high-gain stages used in most modern operational amplifiers
and the factors which influence output-stage performance are also included.
Chapter 9 illustrates how circuit design techniques and feedback-system
concepts are combined in an illustrative operational-amplifier circuit.
The factors influencing the design of the modern integrated-circuit opera­
tional amplifiers that have dramatically increased amplifier usage are dis­
cussed in Chapter 10. Several examples of representative present-day de­
signs are included.
A variety of operational-amplifier applications are sprinkled throughout
the first 10 chapters to illustrate important concepts. Chapters 11 and 12
focus on further applications, with major emphasis given to clarifying im­
portant techniques and topologies rather than concentrating on minor
details that are highly dependent on the specifics of a given application and
the amplifier used.

=== 第 15 页 ===
Problems 15
Chapter 13 is devoted to the problem of compensating operational ampli­
fiers for optimum dynamic performance in a variety of applications. Dis­
cussion of this material is deferred until the final chapter because only then
is the feedback, circuit, and application background necessary to fully
appreciate the subtleties of compensating modern operational amplifiers
available. Compensation is probably the single most important aspect of
effectively applying operational amplifiers, and often represents the differ­
ence between inadequate and superlative performance. Several examples
of the way in which compensation influences the performance of a repre­
sentative integrated-circuit operational amplifier are used to reinforce the
theoretical discussion included in this chapter.
PROBLEMS
P1.1
Design a circuit using a single operational amplifier that provides an
ideal input-output relationship
V, = -Vn 1 - 2V, 2 - 3Vi 3
Keep the values of all resistors used between 10 and 100 kU.
Determine the loop transmission (assuming no loading) for your design.
P1.2
Note that it is possible to provide an ideal input-output relationship
V, = V 1 + 2Vi + 3Vi 3
by following the design for Problem 1.1 with a unity-gain inverter. Find a
more efficient design that produces this relationship using only a single
operational amplifier.
P1.3
An operational amplifier is connected to provide an inverting gain with
an ideal value of 10. At low frequencies, the open-loop gain of the ampli­
fier is frequency independent and equal to ao. Assuming that the only source
of error is the finite value of open-loop gain, how large should ao be so that
the actual closed-loop gain of the amplifier differs from its ideal value by
less than 0.1 %?
P1.4
Design a single-amplifier connection that provides the ideal input-output
relationship
Vo = -100f (vil + v ) dt
2

=== 第 16 页 ===
16 Background and Objectives
Vi
10 k&2
(a)
10 k92
10 kW
Vi 2 + 10 k2 ++
Vg, 10 k2
(b)
Figure 1.7 Differential-amplifier connections.
Keep the values of all resistors you use between 10 and 100 k2.
P1.5
Design a single-amplifier connection that provides the ideal input-output
relationship
V,= +100f (vnl + vi) dt
2
using only resistor values between 10 and 100 kU. Determine the loop trans­
mission of your configuration, assuming negligible loading.
P1.6
Determine the ideal input-output relationships for the two connections
shown in Fig. 1.7.

=== 第 17 页 ===
Problems 17
1 M 2 1 M2V
-
Vi - 2 pF 1pF 1 pF
0.5 MS2
Figure 1.8 Two-pole system.
P1.7
Determine the ideal input-output transfer function for the operational-
amplifier connection shown in Fig. 1.8. Estimate the value of open-loop
gain required such that the actual closed-loop gain of the circuit approaches
its ideal value at an input frequency of 0.01 radian per second. You may
neglect loading.
P1.8
Assume that the operational-amplifier connection shown in Fig. 1.9
satisfies the two conditions stated in Section 1.2.2. Use these conditions to
determine the output resistance of the connection (i.e., the resistance seen
by the load).
V + >7
vi
R
Figure 1.9 Circuit with controlled output resistance.

=== 第 18 页 ===
18 Background and Objectives
ic
10 kn B
VvoOB'
Figure 1.10 Log circuit.
P1.9
Determine the ideal input-output transfer relationship for the circuit
shown in Fig. 1.10. Assume that transistor terminal variables are related as
ic = 10-"e40VBE
where ic is expressed in amperes and VBE is expressed in volts.
P1.10
Plot the ideal input-output characteristics for the two circuits shown
in Fig. 1.11. In part a, assume that the diode variables are related by
iD = 10-13 e40 V, where iD is expressed in amperes and VD is expressed
in volts. In part b, assume that iD = 0, VD < 0, and VD = 0, iD > 0.
P1.11
We have concentrated on operational-amplifier connections involving
negative feedback. However, several useful connections, such as that
shown in Fig. 1.12, use positive feedback around an amplifier. Assume that
the linear-region open-loop gain of the amplifier is very high, but that its
output voltage is limited to ±10 volts because of saturation of the ampli­
fier output stage. Approximate and plot the output signal for the circuit
shown in Fig. 1.12 using these assumptions.
P1.12
Design an operational-amplifier circuit that provides an ideal input-
output relationship of the form
vo = KevI/K2
where K and K are constants dependent on parameter values used in
1 2
your design.

=== 第 19 页 ===
EiD
vi
VD
o
0 v
0
1 k
(a)
1 Mn
1 ME2
kn
VD +
1 k2
-5 V
(b)
Figure 1.11 Nonlinear circuits.
0 vo
vI = 10 sin t
10 k2
10 kE2
Figure 1.12 Schmitt trigger.
19

=== 第 20 页 ===
.2

=== 第 21 页 ===
MIT OpenCourseWare
http://ocw.mit.edu
RES.6-010 Electronic Feedback Systems
Spring 2013
For information about citing these materials or our Terms of Use, visit: http://ocw.mit.edu/terms.
