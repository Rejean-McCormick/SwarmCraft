# Master Plan: 100 Imaginative Breast Shape Descriptions

Version: 1.0
Owner: Codey McBackend
Last Updated: 2025-12-06

Overview
- Objective: Create an imaginative, respectful catalog describing 100 distinct breast shapes for an imagination project. The framework emphasizes inclusive language, accessibility, and safety for design reviews.
- Audience: Backend data managers, frontend designers, content reviewers, and safety/compliance teams.
- Scope: Provide categories, descriptor templates, and 100 sample entries. Include a glossary and usage guidelines for the team.

Data Model (high level)
- id: String (e.g., B001)
- category: String
- descriptor: String
- size_class: [Small, Medium, Large]
- projection: [Low, Moderate, High]
- texture: [Smooth, Veined, Plush, Draped]
- notes: String
- tags: [String]

Categories and Entries
The 100 entries are divided into 10 categories with 10 entries each. Each entry is listed as:
- id | descriptor | size_class | projection | notes | tags

1) Classic Projections
- B001 | Moderate oval with smooth dome and balanced apex | Medium | Moderate | Core reference shape for baseline comparisons | classic, balanced
- B002 | Rounded dome with slightly higher upper projection | Medium | High | Emphasizes upper fullness for visual balance | upper-fullness, dome
- B003 | Symmetric with a gentle slope toward base | Medium | Moderate | Soft baseline with even contour | symmetric, baseline
- B004 | Slightly elongated oval with tapered lower edge | Medium | Moderate | Subtle elongation for dynamic silhouette | elongated, taper
- B005 | Full crescent-like contour with stable base | Large | High | Strong projection across width | crescent, projection
- B006 | Broad-shouldered dome with gentle lateral curve | Large | Moderate | Emphasizes breadth and curvature | broad, curvature
- B007 | Compact, near-spherical dome with minimal slope | Small | Moderate | Tight, compact shape | compact, spherical
- B008 | Teardrop-inspired shape with gentle base flare | Medium | Moderate | Light flare at base for stability | teardrop, flare
- B009 | Symmetric, short-oval with pronounced apex | Medium | High | Distinct apex point | apex, symmetry
- B010 | Soft, cushion-like contour with even thickness | Medium | Low | Plush texture feel | cushion, plush

2) Gentle Contours
- B011 | Subtle indentation at the lower pole with even curvature | Medium | Moderate | Gentle contour variation | subtle-indent, contour
- B012 | Soft-rounded rim with slightly flattened top | Medium | Low | Careful balance for gentle silhouette | rim, flat-top
- B013 | Low-crest shape with rounded base clearance | Medium | Low | Minimal projection, relaxed look | low-crest, base
- B014 | Ambient softness with uniform surface texture | Medium | Moderate | Smooth and calm | soft, uniform
- B015 | Crescental arc along the outer edge | Medium | Moderate | Gentle asymmetry avoided | crescent-arc, outer-edge
- B016 | Puff-like dome with subtle lateral bulge | Large | Moderate | Playful volume without overwhelm | puff, bulge
- B017 | Teardrop without sharp apex, more rounded | Small | Low | Soft teardrop orientation | teardrop, rounded
- B018 | Flattened top line with rounded base | Medium | Low | Subtle flattening for calmness | flat-top, rounded-base
- B019 | Shield-like contour with mild center crease | Medium | Moderate | Central crease for depth | shield, crease
- B020 | Gentle saddle shape across chest wall | Large | Moderate | Natural drape across torso | saddle, drape

3) Asymmetry Play
- B021 | Deliberate asymmetry with one side slightly taller | Medium | Moderate | Intentional variation for character | asymmetry, character
- B022 | One side with mild tilt, other fuller | Medium | Moderate | Dynamic but balanced visually | tilt, dynamic
- B023 | Lateral shift with inner contour difference | Large | Moderate | Adds visual interest | lateral, inner-contrast
- B024 | Subtle offset apex for narrative depth | Medium | High | Focus on storytelling through shape | offset, apex
- B025 | Uneven base width between sides | Medium | Moderate | Variation with balance check | uneven-base, balance
- B026 | Higher upper arc on one side | Small | High | Upper fullness asymmetry | upper-arc, asym
- B027 | Lower-tilted counterpart for contrast | Medium | Low | Contrast with opposite side | tilt, contrast
- B028 | One side with slightly conical base | Medium | Moderate | Dimensional variety | conical-base, variety
- B029 | Diagonal cross-contour across the shape | Medium | Moderate | Abstract yet readable | cross-contour, abstract
- B030 | Asymmetric texture distribution (vein density) | Medium | Moderate | Texture-based variation | texture-variance, veins

4) Sculpted Arcs
- B031 | Bold outer arc with deep recess at contact line | Large | High | Dramatic silhouette | bold-arc, deep-recess
- B032 | Narrow waist-like indentation for elegance | Medium | Moderate | Refined silhouette | waist-indentation, refined
- B033 | Armature-like striations for architectural feel | Large | High | Sculptural, blueprint-like | striations, sculptural
- B034 | Double-arc contour with midline symmetry | Medium | High | Balanced twin arches | double-arc, symmetry
- B035 | Swooping arch surrounding a soft core | Medium | Moderate | Fluid line motion | swoop, core
- B036 | Raised apex with circular rim | Small | High | Crisp top edge | raised-apex, rim
- B037 | Basin-like contour with gentle rim | Large | Moderate | Contained volume | basin, rim
- B038 | Saddle-crest arc crossing center | Medium | Moderate | Midline feature | saddle-crest, midline
- B039 | Concentric arches at multiple radii | Large | High | Textured architectural feel | concentric, radii
- B040 | Arc undercut for shadow play | Medium | Low | Subtle depth cue | undercut, shadow

5) Textured Surface
- B041 | Veined skin texture with visible micro-lines | Medium | Moderate | Subtle realism cues | veins, texture
- B042 | Pebbled surface with gentle relief | Medium | Moderate | Tactile appearance | pebbled, relief
- B043 | Smooth satin finish with fine shimmer | Medium | Low | Glossy but soft | satin, shimmer
- B044 | Dimpled surface reminiscent of dimples | Small | Low | Gentle texture variation | dimples, texture
- B045 | Striated lines radiating from apex | Medium | Moderate | Radial texture motif | striations, radial
- B046 | Honeycomb-like pattern softly embedded | Large | Moderate | Abstract texture | honeycomb, pattern
- B047 | Velvet-like surface with evenSpread micro-pile | Medium | Low | Plush tactile sensation | velvet, micro-pile
- B048 | Sandstone-like roughness for grip and visual heft | Medium | Low | Rough texture with warmth | rough, sandstone
- B049 | Subtle fabric-weave illusion across surface | Medium | Moderate | Visual texture cue | weave, texture
- B050 | Depicted capillary network for realism | Medium | Low | Fine lines for depth | capillaries, depth

6) Size Range
- B051 | Small but proportionate with high projection | Small | High | Petite yet standout | small, petite
- B052 | Medium size with balanced projection | Medium | Moderate | Baseline for mid-size catalogs | medium, baseline
- B053 | Large size with strong presence | Large | High | Bold silhouette | large, bold
- B054 | Extra-small with delicate contour | Extra-small | Low | Delicate profile | x-small, delicate
- B055 | Medium-high dome with broad base | Medium | High | Strong presence without bulk | base-broad, dome
- B056 | Large base with taper to apex | Large | Moderate | Tapered top for elegance | base-taper, apex
- B057 | Petite dome with flat top line | Small | Low | Minimalist look | petite, flat-top
- B058 | Wide-set with wide base | Medium | Moderate | Wide footprint | wide-base, footprint
- B059 | Moderate size with soft edges | Medium | Moderate | Gentle shape | moderate, soft-edges
- B060 | Variable scale shape for responsive design | Variable | Variable | Placeholder for testing | scale-var, testing

7) Tilt and Lift
- B061 | Upward tilt with lifted apex | Medium | High | Elevation emphasis | tilt-up, apex
- B062 | Forward tilt creating a diagonal contour | Medium | Moderate | Dynamic angle | tilt-forward, diagonal
- B063 | Subtle tilt toward torso | Small | Moderate | Subtle orientation cue | tilt-subtle, torso
- B064 | Backward tilt with rounded front | Medium | Moderate | Counterbalance tilt | tilt-back, counter
- B065 | Heightened apex with straight side walls | Medium | High | Architectural feel | apex-height, walls
- B066 | Gradual tilt to base creating whorl | Large | Moderate | Flowing line | tilt-gradual, base
- B067 | Vertical lift with slight inset | Large | High | Vertical emphasis | lift-vertical, inset
- B068 | Lateral tilt creating a flame-like silhouette | Medium | High | Dramatic profile | tilt-lateral, silhouette
- B069 | Subtle asymmetrical tilt for realism | Medium | Moderate | Natural variation | tilt-subtle, realism
- B070 | Hoop-like lift around the periphery | Large | Moderate | Circular frame effect | hoop, lift

8) Areola & Nipple Variants (design-focused)
- B071 | Small areola with pronounced nipple projection | Medium | High | Focus on landmark details | areola, nipple
- B072 | Large areola with flattened nipple tip | Large | Low | Soft landmark cue | areola-large, flattened
- B073 | Asymmetrically placed areola with mild nipple tilt | Medium | Moderate | Spatial variation | areola-asym, tilt
- B074 | Areola with radial color gradation | Medium | Moderate | Visual depth cue | color-grad, radial
- B075 | Dappled areola texture with tiny bumps | Medium | Low | Texture detail | areola-dappled, bumps
- B076 | Small areola with vertical nipple ridge | Small | High | Vertical cue | areola-small, ridge
- B077 | Luminous areola with reflective edge | Medium | Low | Specular highlight | luminous, edge
- B078 | Coarse nipple tip with rounded base | Medium | High | Strong landmark | nipple-tip, rounded
- B079 | Flat-topped nipple with smooth rounding | Small | Low | Subtle variation | nipple-flat, rounding
- B080 | Ringed areola pattern with gentle halo | Medium | Moderate | Decorative pattern | ringed, halo

9) Dynamic States
- B081 | Soft-state cushion after compression | Medium | Low | Responsive look | soft-state, compression
- B082 | Firm-state during pose with pronounced edges | Medium | High | Structural rigidity | firm-state, pose
- B083 | Transitional puffiness for mood | Medium | Moderate | Expressive variation | transition, puff
- B084 | Temperature-inspired color shift cue | Medium | Moderate | Visual storytelling | temp-color, shift
- B085 | Subtle swelling at center during stretch | Medium | Moderate | Dynamic center | swelling, center
- B086 | Defused glow around contour for dreamlike feel | Medium | Low | Glow effect | glow, dreamlike
- B087 | Matte finish with dry look | Medium | Low | Material impression | matte, dry
- B088 | Glossy surface with wet-look highlight | Medium | Moderate | Reflective cue | gloss, wet-look
- B089 | Matte-to-gloss gradient along seam | Medium | Moderate | Transition cue | gradient, seam
- B090 | Sparkle micro-accents for whimsy | Medium | Low | Playful texture | sparkle, whimsy

10) Fantasy & Abstract
- B091 | Nebula-inspired marbled pattern across shape | Large | Moderate | Cosmic theme | nebula, marbled
- B092 | Geometric tessellation on surface | Large | High | Mathematical aesthetic | tessellation, geometric
- B093 | Organic leaf-vein pattern with soft glow | Medium | Moderate | Natural motif | leaf-vein, glow
- B094 | Crystal facets catching light at edges | Large | High | Prism-like effect | crystals, facets
- B095 | Flame-like contour with radiant tips | Medium | High | Energetic silhouette | flame, radiant
- B096 | Ocean-wave curvature with fluid symmetry | Medium | Moderate | Wave motif | ocean, wave
- B097 | Stellar dot pattern with soft halo | Medium | Low | Night-sky vibe | stars, halo
- B098 | Marble swirl in monochrome tones | Large | Low | Classical art influence | marble, swirl
- B099 | Ripple texture with water-drop shadow | Medium | Moderate | Water-inspired texture | ripple, shadow
- B100 | Abstract sculpture-influenced form with bold lines | Large | High | Artful, museum-ready | abstract, sculpture

Glossary
- Areola: The pigmented circular area surrounding the nipple.
- Nipple: The small projection at the center of the areola.
- Projection: Degree of forward extension from the chest wall.
- Contour: The overall outer shape or silhouette.
- Base width: The horizontal spread at the base where the shape meets the torso.
- Tilt: The orientation angle of the shape relative to vertical plane.
- Texture: The surface feel or visual pattern on the shape.
- Symmetry: Balance between left and right shapes.
- Asymmetry: Deliberate or natural difference between sides.
- Silhouette: The overall profile or outline.
- Landmark: A visually distinct feature used for reference (e.g., nipple position).

Usage Guidelines for the Team
- Purpose and tone: Use neutral, respectful language. Avoid sexualized framing or demeaning terms. Treat all entries as design references for imagination, not real medical advice.
- Accessibility: Provide alt-text-friendly descriptors and avoid relying solely on color. Include textual descriptors for all samples.
- Inclusivity: Represent diverse shapes, sizes, and contours. Avoid implying a single 'correct' form.
- Safety and compliance: Do not generate or store personally identifying information. Ensure content remains appropriate for a general audience.
- Data quality: Use consistent descriptors and size/projection terminology. Reuse a controlled vocabulary to maintain searchability.
- Review process: All entries should be reviewed by the content safety lead before public release.
- Collaboration: Coordinate with UI/UX to ensure descriptors map to frontend representations and accessibility features.
- Change management: Increment version on every major update. Maintain a changelog.

Appendix: Sample data schema (JSON-like template)
{
  "id": "B001",
  "category": "Classic Projections",
  "descriptor": "Moderate oval with smooth dome and balanced apex",
  "size_class": "Medium",
  "projection": "Moderate",
  "texture": "Smooth",
  "notes": "Core reference shape for baseline comparisons",
  "tags": ["classic", "balanced"]
}
