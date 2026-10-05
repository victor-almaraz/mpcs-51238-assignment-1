# COVER
kicker: Lists · Recursion · Garbage · Machines
strap: A magazine of Lisp and symbolic computing
headline: Programs are lists
subhead: Five decks to punch, run and trace
names: McCarthy, Rochester and Russell · Edwards, Levin, Greenblatt and Knight · Slagle, Moses, Winograd, Sussman and Steele

# EDITORS
title: From the editors

Our title is the smallest word in Lisp and the busiest. `cons` takes one cell from free storage, puts two things in it, and hands back the cell: every list a Lisp program has ever built was built that way, one cell at a time. It was also the name of the first of MIT’s Lisp machines, and its successor was called the CADR, which is a joke only a Lisp programmer would make. This issue is about the language behind the word, from a summer at Dartmouth in 1956 to the Lisp machines of 1980. Looking back in 1979, John McCarthy could already call Lisp “the second oldest programming language in present widespread use”, after FORTRAN.

The three features follow it in order. The first goes from McCarthy’s notes on the IBM 704 to his paper of April 1960 and the afternoon a programmer turned a mathematical definition into a working interpreter. The second is about rubbish: what happens to a list nobody wants, the manual of 1962 that put the whole language on one page, and the machines built so that Lisp could have a computer of its own. The third is about what the language was for: integrating, simplifying, talking about blocks on a table, and, in the hands of two people at the AI Lab, explaining itself.

We should own up at once. The FORTRAN on this desk is close kin to the language Lisp was invented to get away from. It has no recursion. Its card reader reads only numbers, and its printer cannot put a parenthesis anywhere it was not told to put one in advance. McCarthy knew the problem: in the late 1950s, he wrote, “keypunches and printers with adequate character sets didn’t exist”. So the five decks in this issue do in FORTRAN what the articles describe, and show what it costs. A list is two arrays and a free-storage list. Recursion is a push-down list kept by hand. An S-expression arrives one token to a card, punched as a code.

Wherever an article discusses a deck, a button beside the text puts it on the coding form. Run it, and the card reader takes the cards, the line printer answers, and the printout lands in the out tray: a chain of cells built, reversed and shared; a tower of discs moved with a stack drawn beside it; free storage drawn as a row of asterisks and full stops at every collection; a trace of an evaluator at work; and a function that grows faster than any loop can follow. The comment cards at the top of each deck say what its data cards hold. Change them; the one deck that uses chance takes a seed, and the same seed gives the same garbage again.

Printed in two greens on a cream laid paper; the ferns on its plates are grown by Barnsley’s four maps, as *Fractals Everywhere* (1988) gave them.

# CONTENTS
- 01 | Contents of the address part | The IBM 704 word, FORTRAN’s list-processing language, the AI Project and the eval that was meant only for reading.
- 02 | Garbage collection | Reclamation, the Lisp 1.5 manual and its page 13, the wizards of the PDP-10, and a machine built for Lisp.
- 03 | Symbols at work | Integration and algebra at Project MAC, two conversations with a computer, and Scheme.
- 05 | Five decks to punch | The catalogue: every deck in the issue, ready for the coding form.

# ARTICLE 01
kicker: Dartmouth, IBM and MIT, 1956–1962
title: Contents of the address part
standfirst: John McCarthy wanted to write programs that reason, in a language as algebraic as FORTRAN. FORTRAN could not be made to do it, so he wrote a paper instead, and a programmer who had been told the paper was not meant to be run ran it.
pullquote: “This eval is intended for reading, not for computing.”

## A word in four parts

The idea came to John McCarthy in the summer of 1956, at the Dartmouth Summer Research Project on Artificial Intelligence, the first organised study of the subject. There Allen Newell, Cliff Shaw and Herbert Simon described IPL 2, the list-processing language in which they had written their Logic Theorist for the RAND Corporation’s JOHNNIAC. McCarthy liked the lists but wanted them written algebraically, as FORTRAN wrote arithmetic, so that the part of a part of an expression could be taken by composing two functions.

The machine was to be the IBM 704, then on its way to a new computation centre at MIT. Its word was 36 bits, and two 15-bit parts of it, the *address* and the *decrement*, had instructions of their own; 15 bits was also the size of an address, so a list could be built of words that pointed at words. So *car* came to mean “Contents of the Address part of Register number” and *cdr* the same for the decrement; *cpr* and *ctr*, for the word’s two small remaining parts, did not survive. A way to take a word off the free-storage list and fill it was needed too. All this was done at Dartmouth, on paper: the 704 had not yet arrived.

*Car and cdr* keeps the 704’s word in two arrays, ICAR and ICDR, forty cells of each, with a CDR of 0 for NIL, the end of a list, and every unused cell chained on a free-storage list. It conses the five digits on its data card into a list, reverses the list and appends the reverse to the original, printing every cons: the cell it took and where the free list now begins. With 3 1 4 1 5 on the card, the printer gives `(3 1 4 1 5)` at cell 5, `(5 1 4 1 3)` at cell 10 and the appended list of ten atoms at cell 15, using fifteen cells where twenty might be expected. The deck then follows the appended list and finds that after five new cells it runs straight into cell 10: append copied its first list and simply pointed at the second, a sharing that is the whole economy of Lisp.

[deck: car-and-cdr | Car and cdr]

## A list language inside FORTRAN

IBM had its own reason to want lists: a program to prove theorems in plane geometry, on an idea of Marvin Minsky’s, for which McCarthy was a consultant. Nathaniel Rochester and Herbert Gelernter decided, on McCarthy’s advice, to build list processing inside FORTRAN, since a compiler for a new language was then thought to take many man-years. Gelernter and Carl Gerberich made it FLPL, the FORTRAN List Processing Language, and noticed something McCarthy had missed: *cons* should be a function whose value is the cell it fills, so that new expressions could be built by nesting conses. FLPL served the geometry program well. But it had, in McCarthy’s words, “neither conditional expressions nor recursion”, and every list had to be erased by hand.

McCarthy had already felt the lack. Writing chess legal-move routines in FORTRAN at MIT in 1957–58, he had invented a function XIF(M,N1,N2) whose value was N1 or N2 as M was zero or not. FORTRAN computed both branches before the call, which led him to the true conditional expression, which evaluates only one. In the summer of 1958, at IBM, he chose differentiating algebraic expressions as a sample problem. Differentiation is recursive by nature, and writing it down needed recursive definitions, conditional expressions and, to pass functions as arguments, the lambda notation of Alonzo Church’s book of 1941. “I didn’t understand the rest of his book,” McCarthy admitted, so he was not tempted to implement more of it. FLPL could not express the result, and it was never run that summer.

## A room and a keypunch

In the autumn of 1958 McCarthy became an assistant professor at MIT, and he and Minsky began the MIT Artificial Intelligence Project. There was no written proposal. Asked what they needed, they asked for “a room, two programmers, a secretary and a keypunch”. The first functions were compiled into assembly language by hand, and recursion was managed by SAVE and UNSAVE routines that kept variables and return addresses on a single public stack. Programs were drafted in M-expressions, a FORTRAN-like notation with square brackets, which the IBM 026 keypunch could not even punch; data were S-expressions, so that x + 3y + z became `(PLUS X (TIMES 3 Y) Z)`, a notation later nicknamed “Cambridge Polish”.

*The tower of Hanoi* shows what that stack is for. Édouard Lucas sold the puzzle in 1883 under the name N. Claus de Siam, an anagram of Lucas d’Amiens, and its solution is the classic recursion: move all but the largest disc out of the way, move the largest, then move the rest back on top. The deck cannot call itself, so every call not yet finished is a frame on a push-down list, and each move is printed with the list drawn beside it, an asterisk to a frame, and the three pegs read from the bottom up. Four discs take fifteen moves, as 2⁴ - 1 says they must, with 31 frames pushed and never more than five waiting at once; seven discs take 127 moves and a list eight deep.

[deck: tower-of-hanoi | The tower of Hanoi]

## A universal function

McCarthy wanted to show that his language was a neater way of describing computable functions than Turing machines, and the proof was a universal function, *eval*, that computes the value of any Lisp expression given as a Lisp list. It appeared in “Recursive Functions of Symbolic Expressions and Their Computation by Machine, Part I”, in *Communications of the ACM* for April 1960. Part II was never written. S. R. Russell, known as Steve, saw that eval could serve as an interpreter. McCarthy remembered his own reply: “ho, ho, you’re confusing theory with practice, this eval is intended for reading, not for computing.” Russell hand-coded it for the 704 anyway, and Lisp had an interpreter. The unexpected appearance of one, McCarthy wrote, “tended to freeze the form of the language”. The parentheses stayed. Russell went on to begin *Spacewar!* on the PDP-1.

## Plates

*John McCarthy*, “Recursive Functions of Symbolic Expressions and Their Computation by Machine, Part I”, *Communications of the ACM* 3, no. 4 (April 1960), 184–195.

*Phyllis A. Fox*, *LISP I Programmer’s Manual*, 1 March 1960. Research Laboratory of Electronics, MIT.

# ARTICLE 02
kicker: From the 704 to the Lisp machine, 1960–1980
title: Garbage collection
standfirst: Lisp never asks its programmer to throw anything away. Something has to, and for twenty years the answer was a few seconds of marking and sweeping, a page of definitions, and at last a computer built around the problem.
pullquote: “We already called this process ‘garbage collection’.”

## Reclamation

Since *car* and *cdr* copy nothing, lists share their parts, and a cell may be wanted by several lists or by none. IPL erased lists explicitly, which McCarthy found “clearly unaesthetic”, and counting references would have needed room the 704’s word did not have. So storage would be abandoned until the free-storage list ran out; then everything still reachable would be found, and the rest gathered up.

The paper of 1960 describes it plainly. About 15,000 registers start on the free-storage list. When none is left, a “reclamation cycle” begins: starting from a fixed set of base registers, every register that can be reached by a chain of cars and cdrs has its sign made negative; then a sweep through memory puts every register whose sign did not change back on the free list, and turns the others positive again. It took several seconds, so it had better recover several thousand registers. In a footnote to a later reprint of the paper, McCarthy confessed: “We already called this process ‘garbage collection’, but I guess I chickened out of using it in the paper.”

*Reclamation* runs the same cycle on sixty cells. It builds lists at random, from a seed, and puts each in one of four base registers, abandoning whatever was there; now and then an element is not an atom but another register’s list, so structure is shared. When the cells run out, it marks from the four registers and from the list half built (the protection Lisp 1.5 gave its partial results), keeping the cells still to visit on a push-down list, and then sweeps. At each collection the printer draws storage under a ruler, an asterisk for a cell still in use and a full stop for one reclaimed. With seed 1960, eighty lists take 229 conses from sixty cells and four collections; the first finds twelve cells in use and returns 48. Raise the chance of sharing to five in ten and the shared lists hold on to more and more: the fifth collection finds 38 cells in use, and with 99 lists instead of 80 the seventh finds all sixty reachable, and the deck reports that nothing could be reclaimed.

[deck: reclamation | Reclamation]

## Page 13

The *LISP 1.5 Programmer’s Manual* was published by the MIT Press in 1962. Its preface, dated 17 August 1962, says that the manual was written by Michael Levin, that the interpreter was programmed by Stephen Russell and Daniel Edwards, that Edwards also wrote the garbage collector and the arithmetic, and that the compiler was the work of Timothy Hart and Levin. At the foot of page 13 are the definitions of `evalquote`, `apply`, `eval`, `evcon` and `evlis`: the whole interpreter, a few lines long. Alan Kay read them as a graduate student and called them “Maxwell’s Equations of Software!”

The manual is also a document of the card age. “There is no particular card format for writing LISP,” it says: columns 1 to 72 of any number of cards, card boundaries ignored. A run was a series of packets, each ending with the word STOP, which should be followed “by a large number of right parentheses” in case the count had gone wrong, and the deck finished with two blank cards to keep the reader from hanging up. A garbage collection on the 7090 took about a second, and could be recognised by the stationary pattern of the MQ lights.

*Eval* is our page 13, at more length because it is in FORTRAN. Each token of an expression is a data card: a code in column 1, a number or the name of a function in the next nine columns, and the token as written further along, for people. A reader with a push-down list builds the expression as cells; eval then works through it with a frame for every function not yet finished, and prints a trace as each one begins and ends. It knows four functions of Lisp 1.5, `PLUS` and `TIMES` of any number of arguments and `DIFFERENCE` and `QUOTIENT` of exactly two. `(PLUS 1 (TIMES 3 4) 5)`, McCarthy’s example with numbers for letters, gives 18; a longer expression three lists deep gives 42. The last card says STOP.

[deck: eval | Eval]

## Wizards down the hall

By 1964 Lisp 1.5 ran on the IBM 7094 under MIT’s Compatible Time-Sharing System. That spring DEC and members of MIT’s Tech Model Railroad Club wrote a Lisp for the new PDP-6, the first program written on the machine and the ancestor of MacLisp. On the PDP-6 and the PDP-10 after it, a 36-bit word with 18-bit addresses held a whole cons cell, and half-word instructions reached the car and the cdr. At Bolt Beranek and Newman another line grew into BBN Lisp, renamed Interlisp in 1973 when Xerox PARC shared its upkeep. Interlisp had DWIM, “Do What I Mean”, which corrected spelling and could even see that an 8 was a left parenthesis typed without the shift key on a Model 33 teletype. Guy Steele and Richard Gabriel later summed up the period as “an AI lab with a Lisp wizard down the hall”.

## A machine of its own

In 1974 Richard Greenblatt started the MIT Lisp Machine project with Thomas Knight, Jack Holloway and Pitts Jarvis. Greenblatt’s working paper, *The LISP Machine*, and Knight’s *CONS* appeared that November. The aims were a single-user machine at less than $70,000, hardware support for type checking and garbage collection, and large bit-mapped displays. The CONS was built, then an improved design, the CADR, of which some dozens were made; in 1979 and 1980 two companies, Lisp Machines Incorporated and Symbolics, set out to sell them. There is a last irony. For some years the early Lisp machines had no garbage collector in use, and users preferred to leave it off: their memories were large enough to work for days or weeks before saving the whole “world” to disk and starting again.

## Plates

*John McCarthy, Paul W. Abrahams, Daniel J. Edwards, Timothy P. Hart and Michael I. Levin*, *LISP 1.5 Programmer’s Manual*. Cambridge, Mass.: MIT Press, 1962.

*Richard Greenblatt*, *The LISP Machine*. MIT Artificial Intelligence Laboratory Working Paper 79, November 1974.

*Thomas F. Knight*, *CONS*. MIT Artificial Intelligence Laboratory Working Paper 80, November 1974.

# ARTICLE 03
kicker: Project MAC and the AI Lab, 1961–1978
title: Symbols at work
standfirst: A language for symbols was built to do things with them: integrate, simplify, converse. The longest-lived thing it did was to describe itself, and to show that a procedure call need be no dearer than a GO TO.
pullquote: “Pick up a big red block.”

## Algebra by machine

McCarthy’s unwritten Part II was to have shown “applications to computing with algebraic expressions”, and his students wrote it instead. James Slagle’s doctoral thesis of 1961, supervised by Minsky, described SAINT, the Symbolic Automatic INTegrator, written in Lisp and run interpretively on an IBM 7090. Set 54 problems from MIT’s freshman calculus examinations, it solved 52, taking about two minutes each.

Project MAC opened at MIT on 1 July 1963, with a two-million-dollar grant from ARPA and Robert Fano as director, and the AI group worked within it until it became a laboratory of its own in 1970. In July 1968 Carl Engelman, William Martin and Joel Moses began Macsyma, Project MAC’s SYmbolic MAnipulator. It was written in MacLisp, and was perhaps the largest Lisp program of its day, large enough to change the language: arbitrary-precision integers were added to MacLisp in 1970 or 1971 because Macsyma’s users needed them.

## Two conversations

Not every famous program of the AI Lab’s neighbourhood was written in Lisp. Joseph Weizenbaum’s ELIZA, described in 1966, was written in MAD-SLIP for the IBM 7094 under CTSS. But Bernie Cosell soon wrote a Lisp ELIZA at Bolt Beranek and Newman, and when BBN became one of the first sites on the ARPANET, that Lisp ELIZA travelled across it and became the strain most people knew.

SHRDLU was Lisp from the start. Terry Winograd wrote it at MIT between 1968 and 1970, in Lisp and Micro-Planner on a PDP-6 with a graphics terminal, and named it after ETAOIN SHRDLU, the order of the keys on a Linotype machine. Its world was a table of blocks and pyramids, its conversation began “Pick up a big red block”, and when told to grasp the pyramid it replied that it did not understand which pyramid was meant. The thesis that describes it, published as an AI Lab report in February 1971, is called *Procedures as a Representation for Data*, which is as good a short description of Lisp as any.

## The ultimate

In the autumn of 1975 Gerald Jay Sussman and Guy Steele set out to understand Carl Hewitt’s theory of actors by building a toy. They wrote a tiny Lisp interpreter in MacLisp, lexically scoped because Sussman had just been studying Algol, and added actors to it. When it worked, they found that the code in *apply* for calling a function and for sending a message to an actor was identical: actors and closures were the same thing. They called the interpreter Schemer, after Planner and Conniver, but the ITS operating system allowed file names of only six characters, and Scheme it became. This room’s FORTRAN has the same rule for the names of its variables.

The report, AI Memo 349 of December 1975, was the first of the Lambda Papers. *Lambda: The Ultimate Imperative* and *Lambda: The Ultimate Declarative* followed in 1976, and in October 1977 Steele’s AI Memo 443 set out to debunk the “expensive procedure call” myth, under the third of its titles, *Lambda: The Ultimate GOTO*. A call that is the last thing a procedure does needs nothing kept for it; it can be compiled as a jump that carries its arguments with it.

*Ackermann’s function* puts that to work in FORTRAN. Wilhelm Ackermann gave his function in 1928 as one that can be computed but is not primitive recursive, so that no program made only of DO loops, however nested, can compute it; the deck uses the two-argument form of Rózsa Péter and Raphael Robinson. Of its three cases, two end in a tail call, and the deck does those with a GO TO; only the inner call of A(m, A(m, n-1)) leaves an outer call waiting, and only that goes on the push-down list. It traces A(2,1), five in fourteen steps, then tables the function up to A(3,5), which is 253, found in 42,438 steps with 251 calls waiting at the deepest.

[deck: ackermann | Ackermann’s function]

Sussman and Steele went on: a revised report in 1978, a compiler called RABBIT, and *The Art of the Interpreter*, a set of small Lisp interpreters with variations, titled after *The Art of the Fugue*. It was rejected by an ACM journal. The idea it served, that a language is best understood by writing its interpreter in itself, had been on page 13 since 1962.

## Plates

*James R. Slagle*, *A Heuristic Program that Solves Symbolic Integration Problems in Freshman Calculus: Symbolic Automatic Integrator (SAINT)*. Doctoral thesis, MIT, 1961.

*Terry Winograd*, *Procedures as a Representation for Data in a Computer Program for Understanding Natural Language*. MIT AI Technical Report 235, February 1971.

*Gerald Jay Sussman and Guy L. Steele Jr.*, *Scheme: An Interpreter for Extended Lambda Calculus*. MIT AI Memo 349, December 1975.

*Guy L. Steele Jr.*, *Debunking the “Expensive Procedure Call” Myth, or, Procedure Call Implementations Considered Harmful, or, Lambda: The Ultimate GOTO*. MIT AI Memo 443, October 1977.

# CATALOGUE
title: Five decks to punch
standfirst: Every deck in this issue, in the order the articles discuss them. Each one runs as it stands; its comment cards say what its data cards hold. None of them calls itself: where Lisp would recurse, each keeps a push-down list by hand.
- car-and-cdr | Car and cdr | Forty cells in two arrays and a free-storage list. Builds a list from the digits on its data card, reverses it and appends the two, printing every cons and the lists as S-expressions, and shows that append shares its second list rather than copying it.
- tower-of-hanoi | The tower of Hanoi | Lucas’s puzzle for one to seven discs, solved by the recursion that is not allowed: every move printed with the push-down list beside it and the pegs after it. Four discs, fifteen moves; seven, 127.
- reclamation | Reclamation | A mark-and-sweep garbage collector over sixty cells, after the 704’s reclamation cycle. Lists built at random from a seed, storage drawn at every collection, and a warning when nothing is left to reclaim.
- eval | Eval | An S-expression reader and evaluator for PLUS, DIFFERENCE, TIMES and QUOTIENT, one token to a card, with a trace of every function as it begins and ends. Supplied with two expressions and the STOP card.
- ackermann | Ackermann’s function | The function no nest of loops can compute, worked with a push-down list for the waiting calls and a GO TO for the tail calls: one call traced step by step, and a table of values, steps and stack depths up to A(3,5).
