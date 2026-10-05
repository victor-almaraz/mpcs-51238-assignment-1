# COVER
kicker: Autumn · Hole, glass and stop
strap: A magazine of black-and-white photography
headline: The geometry of light
subhead: Five decks to punch, focus and expose
names: Ibn al-Haytham, Barbaro, Talbot, Petzval and Rayleigh · Airy, Adams, Weston, Cunningham and Van Dyke · Chevalier, Petzval, Taylor, Rudolph and Brandt

# EDITORS
title: From the editors

Before there is any silver, any developer or any print, there is a hole in a box and the light that comes through it. Everything a photograph will ever be is decided in the few centimetres between the front of the camera and the film: how big the picture is, how much of the world it takes in, how bright it is, which parts are sharp and which are not. That is optics, and it is the oldest part of photography by eight hundred years.

This issue is about the arithmetic of those few centimetres. A scholar in Cairo who watched candles through a hole in a wall and saw that light runs in straight lines. A Venetian who put a spectacle lens in the hole, and then covered most of it to make the picture sharper. A mathematician in Vienna who computed a lens with the help of a squad of gunners and made portraits twenty times quicker. A peer of the realm who worked out how big a pinhole should be. A group of Californians who named themselves after the smallest stop on their lenses. And the lens makers of Paris, Vienna, York and Jena who, one fault at a time, taught glass to draw a straight line to the corner of the frame.

Our argument is that the photographers who mattered knew this arithmetic, whether or not they ever wrote it down. Every formula in these pages has a worked example in real numbers, with millimetres a reader can measure on their own camera, and every one of them was once a rule of thumb that someone had to discover.

Five of them are here to be run. Wherever an article discusses a deck, a button beside the text puts it on the coding form. The decks find the best pinhole for a camera of any length, follow a lens through its focusing and draw its rays, set out every stop against every shutter speed, chart the depth of field of a lens across its stops, and trace rays through a single lens to show where they go wrong. The line printer draws with a full stop for paper and an asterisk for ink, which is exactly what a ray diagram needs. The comment cards at the top of each deck say what its data cards hold; change them, and the optics change with them.

Printed in black alone on coated paper, the diagrams from line blocks and the plates through a screen of 150 lines to the inch.

# CONTENTS
- 01 | The dark chamber | The camera obscura from Ibn al-Haytham to Kepler, the best pinhole by Petzval’s rule and Rayleigh’s, and the lens equation that puts glass in the hole.
- 02 | Stopping down | The f-number and its steps of the square root of two, exposure values and the inverse square, depth of field and the hyperfocal distance, and why Group f/64 could use f/64.
- 03 | Answering the aberrations | Seidel’s five faults, spherical aberration traced ray by ray, Chevalier’s landscape lens, Petzval’s portrait lens, the Cooke triplet and the Tessar, and the angle of view.
- 05 | Five decks to punch | The catalogue: every deck in the issue, ready for the coding form.

# ARTICLE 01
kicker: The camera obscura and the pinhole, 1000–1891
title: The dark chamber
standfirst: Make a small hole in the wall of a dark room and the street appears upside down on the opposite wall. It took eight centuries to explain why, and to work out how small the hole should be.
pullquote: A camera with only a pin-hole.

## Candles and a window

In the early eleventh century the scholar Ibn al-Haytham, known in Latin Europe as Alhazen, set several candles in a row before an opening into a dark recess. On the white wall inside, each candle made its own spot of light, directly opposite it on a straight line through the opening; shield one candle and only its spot went out. The lights did not mingle in the air. That experiment, in his *Book of Optics*, is the principle of every camera. Each point of the scene sends its light through the hole along a straight line, and so lands at one place on the wall, above for what is below and left for what is right. In a treatise on the shape of the eclipse he noted that a partly eclipsed sun shows as a crescent on the wall only when the hole is very small.

The Frisian-born physician and mathematician Gemma Frisius watched the solar eclipse of 24 January 1544 this way at Louvain, and his illustration of the next year, in *De radio astronomico et geometrico*, is the earliest known picture of a camera obscura. The name, the dark chamber, is usually credited to Johannes Kepler, in 1604.

The geometry is that of similar triangles. If the hole is a distance `f` from the wall, a subject of height `h` at distance `u` makes an image of height

= h' = h × f/u

A tree 10 metres tall and 20 metres away, through a box 100 mm deep, makes an image 10,000 × 100/20,000 = 50 mm tall, upside down. That depth is the pinhole camera’s focal length.

## How small a hole

A hole focuses nothing. Every point of the scene throws a patch of light about the size of the hole, so a hole of 1 mm draws every point as a disc 1 mm across. Make the hole smaller and the patch shrinks, but only so far, because light through a small opening spreads by diffraction, and the smaller the opening the more it spreads: through a hole of 0.1 mm in the same box, green light spreads into a disc about 2.44 × 0.00055 × 100/0.1 = 1.3 mm across. Between the two lies a best hole.

Joseph Petzval, of whom more in our third feature, was the first to publish a rule for it, in 1857. For a box of depth `f` and light of wavelength `λ`, his best diameter was

= d = sqrt(2fλ)

Lord Rayleigh came back to the question in 1891, in “On pin-hole photography” in the *Philosophical Magazine*, and was the first to treat it by the wave theory of light. His conclusion, in *Nature* the same year, was that the hole “may advantageously be enlarged beyond that given by Petzval’s rule”: he suggested a radius of `sqrt(fλ)`, that is, a diameter of

= d = 2 × sqrt(fλ)

Take the 100 mm box and green light of 550 nanometres, 0.00055 mm. Then `fλ` = 0.055 mm², its square root is 0.2345 mm, and Rayleigh’s hole is 0.469 mm across; Petzval’s is 0.332 mm. A box four times as long needs a hole only twice as wide.

The price is light. The f-number of the pinhole, depth over diameter, is 100/0.469 = 213, and a lens at f/16 lets in (213/16)² = 177 times as much, seven and a half stops more. Where the rule of thumb of our next feature gives 1/100 second at f/16, the pinhole needs 177/100 = 1.8 seconds, and in practice more, because film loses speed in dim light.

*The best pinhole* does the sums for eight boxes from 25 to 500 mm deep: both rules, the f-number, the stops beyond f/16 and the exposure. The 25 mm box takes a hole of 0.235 mm at f/107 and four-tenths of a second, the 500 mm box a hole of 1.049 mm at f/477 and nearly nine seconds.

[deck: the-best-pinhole | The best pinhole]

The first known description of pinhole photography is in David Brewster’s *The Stereoscope* of 1856: “a camera without lenses, and with only a pin-hole”. In 1890 George Davison won a medal at the Photographic Society’s exhibition with *An Old Farmstead*, taken through a pinhole, its softness the point; Alfred Stieglitz printed it in *Camera Work* in 1907 as *The Onion Field*.

## Glass in the hole

A lens is a hole that can be large without blurring, because it bends every ray from one point of the subject back to one point of the image. In 1568 the Venetian Daniele Barbaro, in *La pratica della perspettiva*, described a camera with a lens from an old man’s spectacles, and advised covering the lens until only a little of the middle was left open, because the picture was then sharper: the first diaphragm. William Henry Fox Talbot’s small cameras of 1835, known as mousetraps, had lenses, and with one of them in August of that year he made the oldest surviving negative, a window at Lacock Abbey.

For a simple lens of focal length `f`, a subject at distance `u` in front comes to focus at distance `v` behind, by the thin-lens equation:

= 1/f = 1/u + 1/v

and the image is inverted and magnified by

= m = v/u

Focus a 50 mm lens on a person 3 metres away: `1/v` = 1/50 - 1/3,000 = 59/3,000, so `v` = 50.85 mm. The lens moves forward 0.85 mm, and the magnification is 50.85/3,000 = 0.0169, one fifty-ninth: a person 1.75 m tall is 29.7 mm high on the film and fits the long side of a 24 × 36 frame. At 2 metres, at 44.9 mm, they do not. At `u` = 2f = 100 mm, `v` is 100 mm too, the image is life size, and the light that formed a small image is spread over a large one: the exposure has to grow by `(1 + m)²`, four times, two stops.

*The thin lens* sets out those figures at eight distances, from 40 mm (inside the focal length, where there is no real image) to 10 metres. Then it draws the three textbook rays for a subject 150 mm away: one parallel to the axis and bent through the focal point behind; one straight through the centre; one through the focal point in front, leaving parallel. All three meet 75 mm behind the lens at the tip of an image half the size.

[deck: the-thin-lens | The thin lens]

## Plates

*Gemma Frisius*, observing the solar eclipse of 24 January 1544 in a camera obscura. Illustration from *De radio astronomico et geometrico liber*, Antwerp and Louvain, 1545.

*William Henry Fox Talbot*, *Windows from Inside South Gallery, Lacock Abbey* (the latticed window), August 1835. Paper negative made in a camera obscura, 3.5 × 2.9 cm. National Science and Media Museum, Bradford, Science Museum Group.

*George Davison*, *The Onion Field*, 1890, printed 1907. Photogravure from *Camera Work*, no. 8, April 1907, 15.4 × 20.4 cm. Art Gallery of New South Wales, Sydney.

# ARTICLE 02
kicker: Aperture, exposure and depth, 1835–1932
title: Stopping down
standfirst: Every lens has a ring of numbers that goes up by the square root of two. Turn it one way and the picture is brighter; the other way and more of it is sharp, until the light itself begins to blur.
pullquote: US 256, or f/64.

## The number on the ring

The brightness of the image a lens makes depends on two lengths: the diameter `D` of its opening, which sets how much light it gathers, and its focal length `f`, which sets how large an image it spreads that light across. Their ratio is the f-number:

= N = f/D

A 50 mm lens with an opening 25 mm across is at f/2; close the diaphragm to 6.25 mm and it is at f/8. The light gathered grows with the area of the opening, and the area of the image with the square of the focal length, so the brightness of the image goes as `1/N²`. Any lens at f/8 gives the same exposure as any other lens at f/8, whatever its focal length, and that is the whole use of the number.

To halve the light, halve the area, which means dividing the diameter by the square root of two, 1.414. So the stops go up by that factor, each one letting in half the light of the one before: 1, 1.4, 2, 2.8, 4, 5.6, 8, 11, 16, 22, 32, 45, 64. Every second stop is a power of two. The others are rounded: f/11 is really 11.31, f/22 is 22.63 and f/45 is 45.25.

The notation took time to settle. In the 1880s the Photographic Society of Great Britain adopted the Uniform System, in which US 16 was f/16 but the numbers followed the exposure, not the diameter: f/11 was US 8, f/8 was US 4, f/32 was US 64. The rule is `US = N²/16`, and Kodak was still marking its cameras that way in the 1920s.

## Exposure by number

What reaches the film is the brightness of the image times the time the shutter is open, `t`. Both are folded into a single figure, the exposure value:

= EV = log2(N²/t)

At f/16 and 1/125 second, `N²/t` = 256 × 125 = 32,000, and log2 of 32,000 is 14.97, so EV 15. At f/8 and 1/500, `N²/t` = 64 × 500 = 32,000 again: two stops wider, two steps of the shutter shorter, the same exposure. That is the old rule of thumb, sunny sixteen: in bright sun, f/16 at one over the film speed.

*Sunny sixteen* turns the rule into exposure values for any film speed and light. As it stands, for ASA 100 in bright sun, it works out EV 14.64, calls it 15, prints every stop from f/1.4 to f/32 against every speed from one second to 1/1000, and lists the six settings that give the rule’s exposure.

[deck: sunny-sixteen | Sunny sixteen]

A lamp or a flash, unlike the sun, is near, and its light falls off with the square of the distance:

= E = I/r²

Twice the distance is a quarter of the light, two stops. Flash guns are rated by a guide number, `GN = N × r`, the stop times the distance. With a guide number of 32 in metres, a subject 4 metres away needs f/8; at 8 metres, f/4, two stops wider for twice the distance.

## How much is sharp

A lens focused at one distance brings only that distance to a point. Nearer and farther points come to a focus in front of or behind the film and draw small discs instead. If the discs are small enough they pass for points, and the limit is the circle of confusion, `c`, commonly taken as 0.03 mm for the 24 × 36 frame, about a fourteen-hundredth of its diagonal. A smaller stop makes narrower cones of light, so smaller discs, and a deeper zone that passes for sharp.

The key distance is the hyperfocal distance:

= H = f²/(Nc) + f

For a 50 mm lens at f/8, `H` = 2,500/(8 × 0.03) + 50 = 10,467 mm. Focus at 10.5 metres and everything from half that, 5.2 metres, to the horizon is sharp. Focused at a distance `s`, the near and far limits are

= near = s(H - f)/(H + s - 2f)

= far = s(H - f)/(H - s)

At f/8 and 3 metres that is 3,000 × 10,417/13,367 = 2.34 m to 3,000 × 10,417/7,467 = 4.19 m. Stop down to f/16 and the zone opens to 1.92 to 6.92 metres; at f/32, `H` is 2.65 metres, less than `s`, and the far limit is infinity.

*Depth of field* prints all of this across twelve stops, with the exact power of the square root of two beside each marked one, and charts the zone of sharpness on a scale from half a metre to infinity, widening like a funnel as the lens closes.

[deck: depth-of-field | Depth of field]

## The limit of the small stop

Stopping down cannot go on for ever. George Biddell Airy showed in 1835, in “On the Diffraction of an Object-glass with Circular Aperture”, that even a perfect lens draws a point as a bright disc ringed with fainter circles. Its radius to the first dark ring is `1.22λN`, so its diameter is

= d = 2.44 × λ × N

For green light at f/8 it is 2.44 × 0.00055 × 8 = 0.011 mm, a third of `c`. At f/22 it is 0.0295 mm, as large as `c`, and at f/64 it is 0.086 mm, nearly three times as large. That is why the stops on a lens for the 35 mm camera stop at f/16 or f/22. A negative 8 by 10 inches, printed by contact, can bear a circle of confusion of about 0.2 mm, and there f/64 is safe.

The Californians knew it. On 15 November 1932 an exhibition opened at the M. H. de Young Memorial Museum in San Francisco by Ansel Adams, Imogen Cunningham, John Paul Edwards, Sonya Noskowiak, Henry Swift, Willard Van Dyke and Edward Weston, who called themselves Group f/64. Van Dyke later recalled suggesting “US 256”, the same stop in the Uniform System; Adams thought it would confuse the public. The small stop meant great depth of field and sharp detail from front to back on large negatives. With a 300 mm lens at f/64 and `c` = 0.2 mm, `H` is 7.3 metres. In August 1930 Weston had set a pepper inside a tin funnel and photographed it with his 8 × 10 camera and a Zeiss lens of 21 cm. His daybook records “an exposure of six minutes”.

## Plates

*Imogen Cunningham*, *Magnolia Blossom*, 1925. Gelatin silver print, 26 × 33.2 cm. The Art Institute of Chicago.

*Edward Weston*, *Artichoke, Halved*, 1930, printed 1953–54. Gelatin silver print, 19 × 23.5 cm. The Art Institute of Chicago.

*Ansel Adams*, *Rose and Driftwood, San Francisco, California*, about 1932. Gelatin silver print, 18.3 × 22.7 cm. The Art Institute of Chicago.

# ARTICLE 03
kicker: Aberration and design, 1839–1961
title: Answering the aberrations
standfirst: A single lens draws a picture, but not a good one. The history of the photographic lens is a list of its faults and the glasses, one after another, that were put in their way.
pullquote: “It saw differently.”

## Five faults

The thin-lens equation is true only for rays close to the axis. A real lens with spherical surfaces departs from it in ways that the Munich mathematician Ludwig von Seidel set out in 1856 as five aberrations: spherical aberration, coma, astigmatism, curvature of field and distortion. Glass adds a sixth fault, chromatic aberration, because it bends blue light more than red.

Spherical aberration is the simplest to see. The rays that pass near the rim of a lens are bent too much, and cross the axis short of the focus of the rays near the centre. Take a lens with one face flat and the other curved with a radius `R` of 50 mm, in glass of index `n` = 1.5. Its focal length is

= f = R/(n - 1)

that is, 100 mm. Open it to 12.5 mm either side of the axis, f/4. *Spherical aberration* traces ten rays through it by the law of refraction, `sin i = n sin r`, at each face. With the curved face to the light the rim rays cross 1.84 mm short of the focus of the central rays; turn the lens round, flat face first, and they fall 7.24 mm short, 3.9 times worse. The deck finds the smallest spot each way, 0.12 mm across and then 0.47 mm, and draws the beam from the side, narrowing to its waist and opening again. The fault grows as the square of the aperture: close to 6.25 mm, two stops, and it falls to a quarter.

[deck: spherical-aberration | Spherical aberration]

Colour is answered by pairing glasses. A typical crown glass has an Abbe number, a measure of how little it spreads the colours, of about 64, and a single lens of crown focuses blue and red apart by about `f/V`: for a 100 mm lens, 100/64 = 1.6 mm. A weaker negative lens of flint glass, which spreads colour more, cemented to a positive lens of crown, can bring two colours to one focus. Chester Moor Hall had made such doublets in the 1730s, and John Dollond was granted a patent for them in 1758.

## Landscape and portrait

The first photographic lens was the achromatic landscape lens that Charles Chevalier made for the camera Alphonse Giroux sold with Daguerre’s process in 1839, a cemented doublet with a stop in front of it at about f/16. It drew a fair landscape, but slowly; a portrait sitter had to hold still for minutes.

In 1840 Joseph Petzval, professor of mathematics in Vienna, computed something faster. Archduke Louis lent him eight gunners and three corporals of the artillery to do the arithmetic, and the lens, two doublets with a stop between them, was made by Peter Wilhelm Friedrich Voigtländer. It worked at f/3.6, and its gain over Chevalier’s lens is the ratio of the squares:

= (16/3.6)² = 19.8

about twenty times the light, so that an exposure of ten minutes became one of thirty seconds. Voigtländer built it into an all-metal camera in 1841. The price was the field. Petzval’s lens was sharp in the middle and soft at the edges, where the image lies on a curved surface rather than the flat plate, and its useful field was only about 30 degrees.

## Three glasses, then four

The cure for that curve came from Petzval’s own mathematics: the curvature of the field depends on a sum over the powers and indices of the elements, and can be brought to zero if positive and negative elements balance. In 1893 Harold Dennis Taylor, chief engineer of T. Cooke & Sons of York, patented the Cooke triplet: a negative element of flint between two positive elements of crown, spaced apart in air, so that the lens converged the light but drew on a flat field. With three elements it could correct all five of Seidel’s faults for one colour. Cooke was reluctant to make it, and the design was licensed to Taylor, Taylor and Hobson of Leicester.

In 1902 Paul Rudolph at Carl Zeiss in Jena arrived by another road at the Tessar, four elements in three groups, the rear pair cemented. It began at f/6.3 and reached f/4.5 by 1907, and millions have been made since.

## Wide and long

The focal length and the size of the frame together fix how much of the world a lens sees. Across the diagonal `d` of the frame, the angle of view is

= A = 2 × arctan(d/2f)

The 24 × 36 frame has a diagonal of `sqrt(24² + 36²)` = 43.27 mm. A 50 mm lens sees 2 × arctan(0.433) = 46.8 degrees, and a lens whose focal length is close to the diagonal of its frame is called normal. A 28 mm lens sees 75.4 degrees, a 135 mm lens 18.2. *The thin lens* prints the figure for whatever lens and frame are on its first data card.

Bill Brandt found a wider view in a second-hand shop near Covent Garden: an old wooden Kodak made to photograph the scenes of crimes. In his words, “Like nineteenth-century cameras it had no shutter, and the wide-angle lens, with an aperture as minute as a pinhole, was focused on infinity.” Its tiny stop made its depth of field almost endless, and its wide lens stretched whatever came near it. “My new camera saw more and it saw differently,” he wrote. His *Perspective of Nudes* followed in 1961.

## Plates

*Voigtländer & Sohn*, daguerreotype camera with a Petzval portrait lens, Vienna, 1841. Brass and glass, 35.5 × 17 × 31 cm. National Science and Media Museum, Bradford, Science Museum Group.

*Ilse Bing*, *My Shadow on the Roof with Leica (and Mart Stam), Hellerhof Settlement, Frankfurt-am-Main*, 1930. Gelatin silver print, 19 × 28.2 cm. The Metropolitan Museum of Art, New York.

*Bill Brandt*, *East Sussex Coast*, 1957. Gelatin silver print, from *Perspective of Nudes*, 33.5 × 28.8 cm. The Art Institute of Chicago.

# CATALOGUE
title: Five decks to punch
standfirst: Every deck in this issue, in the order the articles discuss them. Each one runs as it stands, and its comment cards say what its data cards hold. The printer draws with two marks, a full stop for paper and an asterisk for ink, which is all a ray diagram needs.
- the-best-pinhole | The best pinhole | Petzval’s rule and Rayleigh’s for the best pinhole in a camera of any length, with its f-number, the stops it lies beyond sunny sixteen, and the exposure it needs.
- the-thin-lens | The thin lens | The lens equation worked for eight subject distances: image distance, focusing movement, magnification, image size and the exposure factor, the angle of view, and a ray diagram of the three principal rays.
- sunny-sixteen | Sunny sixteen | The sunny sixteen rule turned into an exposure value for any film speed and light, a table of every stop against every shutter speed, and the settings that give the same exposure.
- depth-of-field | Depth of field | Hyperfocal distance, near and far limits and the Airy disc for one lens across twelve stops, with a chart of the zone of sharpness on a scale of distance.
- spherical-aberration | Spherical aberration | Ten rays traced through a plano-convex lens both ways round, where each crosses the axis, the smallest spot, and the beam drawn narrowing to its waist.
