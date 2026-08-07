# Complete Guide to Creative Coding, HTML5 Canvas, and Procedural Animations

This document serves as the core reference guide for generating breathtaking, high-fidelity, self-contained HTML5 Canvas animations, SVG vector graphics, and procedural visual systems. It covers layout, responsiveness, skeletal walk cycles, mathematical gait animation, parallax background scrolling, and resource management.

---

## 1. Core Principles of Procedural Art & Canvas setup

To create a visually stunning animation that is responsive and runs at a stable 60 FPS, the boilerplate must be clean, hide all scrollbars, and dynamically adjust to the window viewport size without distorting coordinates.

### 1.1 Responsive High-DPI Canvas Boilerplate
Use a logical target resolution (e.g., 1920x1080) for coordinates, then scale the rendering context using `ctx.scale(scale, scale)` dynamically based on the window aspect ratio. This ensures layout integrity across all devices.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>High-Fidelity Procedural Scene</title>
    <style>
        * { box-sizing: border-box; }
        body, html {
            margin: 0; padding: 0;
            width: 100%; height: 100%;
            overflow: hidden;
            background-color: #050d1a;
        }
        canvas {
            display: block;
            width: 100vw; height: 100vh;
        }
    </style>
</head>
<body>
    <canvas id="stage"></canvas>
    <script>
        const canvas = document.getElementById('stage');
        const ctx = canvas.getContext('2d');

        // Coordinate scaling
        const targetWidth = 1920;
        const targetHeight = 1080;
        let scale = 1;

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            
            // Uniform scale factor
            scale = canvas.height / targetHeight;
            if (canvas.width / scale < targetWidth) {
                scale = canvas.width / targetWidth;
            }
            scale = Math.max(scale, 0.4); // Prevent division by zero
        }
        
        window.addEventListener('resize', resize);
        resize();
    </script>
</body>
</html>
```

---

## 2. Procedural Skeletal Walks and Gait Articulation

To draw a realistic walking creature (e.g., a dog, a cat, or a person) using pure canvas vectors, **NEVER** use static shapes or a single simple circle. You must draw a multi-segment skeletal structure using translations, rotations, and local coordinate spaces.

### 2.1 The Mathematics of a Walk Cycle
A standard walk cycle is modeled using out-of-phase sine waves. For a quadruped (four-legged animal):
1. **Walk Cycle Frequency**: The cycle phase is driven by a time variable `walkCycle = time * frequency`.
2. **Body & Head Bobbing**: The torso bobs up and down twice per cycle (`Math.sin(walkCycle * 2) * bobAmplitude`). The head bobs slightly out-of-phase with the body.
3. **Leg Phases**:
   - **Left Front (LF)** leg swing angle: `Math.sin(walkCycle)`
   - **Right Front (RF)** leg swing angle: `Math.sin(walkCycle + Math.PI)` (180 degrees out of phase with LF)
   - **Left Hind (LH)** leg swing angle: `Math.sin(walkCycle + Math.PI * 0.5)` (90 degrees out of phase with Front)
   - **Right Hind (RH)** leg swing angle: `Math.sin(walkCycle + Math.PI * 1.5)` (180 degrees out of phase with LH)
4. **Tail Wagging**: The tail wags side-to-side or rotates gently driven by a fast sine wave (`Math.sin(walkCycle * 2.5) * wagRange`).

### 2.2 Articulated Leg Bending (Thigh, Knee, and Paw)
Do not draw legs as simple straight lines. A realistic leg consists of an upper segment, a lower segment, and a foot. Use `ctx.save()`, `ctx.translate()`, `ctx.rotate()`, and `ctx.restore()` to render joints.

```javascript
function drawLeg(ctx, hipX, hipY, swingAngle, upperLength, lowerLength, colors, isFrontLayer) {
    ctx.save();
    ctx.translate(hipX, hipY);
    ctx.rotate(swingAngle); // Rotate at hip joint

    // 1. Draw Thigh (Upper Leg)
    ctx.fillStyle = isFrontLayer ? colors.primaryGrad : colors.darkShadowGrad;
    ctx.beginPath();
    ctx.ellipse(0, upperLength * 0.4, upperLength * 0.3, upperLength * 0.5, 0.1, 0, Math.PI * 2);
    ctx.fill();

    // 2. Translate to Knee Joint and BEND (articulate knee out of phase)
    ctx.translate(0, upperLength * 0.8);
    const kneeBend = -swingAngle * 0.6; // Articulate knee bending back when leg swings forward
    ctx.rotate(kneeBend);
    
    ctx.beginPath();
    ctx.ellipse(0, lowerLength * 0.4, lowerLength * 0.25, lowerLength * 0.5, -0.1, 0, Math.PI * 2);
    ctx.fill();

    // 3. Translate to Foot / Paw
    ctx.translate(0, lowerLength * 0.8);
    ctx.fillStyle = colors.pawAccent;
    ctx.beginPath();
    ctx.ellipse(2, 2, lowerLength * 0.35, lowerLength * 0.2, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
}
```

---

## 3. High-Fidelity Character Graphics (Golden Retriever Example)

Draw visual subjects using overlapping bezier shapes, fluffy textures, and rich linear/radial gradients. Avoid flat, single-color shapes.

```javascript
function drawGoldenRetriever(ctx, x, y, time, colors) {
    ctx.save();
    ctx.translate(x, y);

    const walkCycle = time * 2.5;
    const bodyBob = Math.sin(walkCycle * 2) * 5;
    const headBob = Math.cos(walkCycle * 2) * 6;
    const tailWag = Math.sin(walkCycle * 2.5) * 0.35;

    const angleLF = Math.sin(walkCycle) * 0.45;
    const angleRF = Math.sin(walkCycle + Math.PI) * 0.45;
    const angleLH = Math.sin(walkCycle + Math.PI * 0.5) * 0.4;
    const angleRH = Math.sin(walkCycle + Math.PI * 1.5) * 0.4;

    // Leg scale dimensions
    const upperLeg = 45;
    const lowerLeg = 40;

    // --- Layer 1: Back Legs (Drawn first so body covers hips) ---
    drawLeg(ctx, -45, 10, angleLH, upperLeg, lowerLeg, colors, false);
    drawLeg(ctx, 35, 12, angleLF, upperLeg, lowerLeg, colors, false);

    // --- Layer 2: Tail (Wagging) ---
    ctx.save();
    ctx.translate(-55, -25 + bodyBob);
    ctx.rotate(-0.4 + tailWag);
    ctx.fillStyle = colors.bodyGrad;
    ctx.beginPath();
    ctx.ellipse(-25, -8, 30, 10, -0.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // --- Layer 3: Main Torso / Chest ---
    ctx.save();
    ctx.translate(0, bodyBob);
    ctx.fillStyle = colors.bodyGrad;
    
    // Smooth fluffy torso
    ctx.beginPath();
    ctx.ellipse(0, -10, 68, 38, 0.05, 0, Math.PI * 2);
    ctx.fill();
    
    // Chest fluff highlight
    ctx.fillStyle = colors.undercoatGrad;
    ctx.beginPath();
    ctx.ellipse(45, -15, 25, 25, 0.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // --- Layer 4: Front Legs ---
    drawLeg(ctx, -40, 10, angleRH, upperLeg, lowerLeg, colors, true);
    drawLeg(ctx, 40, 12, angleRF, upperLeg, lowerLeg, colors, true);

    // --- Layer 5: Neck & Head (Bobbing) ---
    ctx.save();
    ctx.translate(50, -32 + headBob);

    // Neck
    ctx.fillStyle = colors.bodyGrad;
    ctx.beginPath();
    ctx.ellipse(8, -10, 18, 30, -0.4, 0, Math.PI * 2);
    ctx.fill();

    // Head
    ctx.beginPath();
    ctx.ellipse(22, -30, 24, 20, 0, 0, Math.PI * 2);
    ctx.fill();

    // Snout / Muzzle
    ctx.beginPath();
    ctx.ellipse(38, -26, 18, 11, 0.08, 0, Math.PI * 2);
    ctx.fill();

    // Nose
    ctx.fillStyle = '#1e1a19';
    ctx.beginPath();
    ctx.ellipse(54, -28, 5, 5, 0, 0, Math.PI * 2);
    ctx.fill();

    // Eye (Polished, happy reflection)
    ctx.fillStyle = '#1e1a19';
    ctx.beginPath();
    ctx.arc(26, -34, 3.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(27.5, -35.5, 1, 0, Math.PI * 2);
    ctx.fill();

    // Ear (Dynamic sway responding to head bob)
    ctx.save();
    ctx.translate(12, -38);
    ctx.rotate(0.1 + Math.sin(walkCycle * 2) * 0.08);
    ctx.fillStyle = colors.earGrad;
    ctx.beginPath();
    ctx.ellipse(2, 18, 12, 24, 0.1, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    ctx.restore(); // Neck & Head

    ctx.restore();
}
```

---

## 4. Flawless Parallax Layer Management

To create a deep, multi-layered environment, arrange scenery layers back-to-front and render them with scroll offsets scaled by their distance (depth factor).

### 4.1 Speed and Depth Ratios
Scenery objects must move across the viewport in infinite loops based on a global `offset = time * speed`:

| Layer | Type | Parallax Speed Factor | Visual Description |
|---|---|---|---|
| 0 | Sky & Sun | 0.00 | Static sunset or sunrise color gradient. |
| 1 | Clouds | 0.05 - 0.10 | Layered shapes drifting slowly in the high sky. |
| 2 | Distant Buildings | 0.15 | Dark silhouettes of clock towers and gables. |
| 3 | Midground Buildings | 0.30 | Detailed brick patterns and window grids. |
| 4 | Midground Trees | 0.45 | Soft, overlapping foliage clusters. |
| 5 | Lawns & Pathway | 0.80 | Curved lawns, textured pathways, road markings. |
| 6 | Subject (Creature) | 0.80 | Fixed X position, walking in place. |
| 7 | Foreground Trees | 1.10 | Trees near the viewport edge scrolling fast to add framing depth. |

### 4.2 Parallax Loop Calculation
For repeating elements (buildings, trees, clouds), use the modulo operator to loop the $x$-coordinate within target bounds, adding overlap to ensure no visible pop-in.

```javascript
function drawInfiniteLayer(ctx, elements, offset, speedFactor, drawCallback) {
    const loopBoundary = targetWidth + 400; // Allow buffer for clean pop-in
    elements.forEach(item => {
        // Calculate looping coordinate
        let itemX = (item.x - offset * speedFactor) % loopBoundary;
        if (itemX < -item.width) {
            itemX += loopBoundary; // Wrap around to far right
        }
        drawCallback(ctx, itemX, item.y, item);
    });
}
```

---

## 5. Performance, Memory, and requestAnimationFrame Rules

catastrophic performance issues occur when resources are instantiated inside the rendering loop. Follow these instructions strictly:

### 5.1 No Allocations in the Render Loop
* **NEVER** write `new Image()`, `new Path2D()`, `document.createElement('canvas')`, or `ctx.createLinearGradient` inside the `requestAnimationFrame` body. 
* All gradients, geometry constants, cloud speeds, and background structures must be defined **once** during an initialization phase (`setup()`).
* Reuse arrays and objects instead of creating new instances.

### 5.2 Correct Setup-and-Loop Pattern
```javascript
// 1. Declare resource containers in global scope
const colors = {};
const buildings = [];
const trees = [];

function setup() {
    // 2. Initialize resources ONCE
    colors.bodyGrad = ctx.createLinearGradient(-60, -40, 60, 20);
    colors.bodyGrad.addColorStop(0, '#f6c365');
    colors.bodyGrad.addColorStop(1, '#c67a13');
    
    // Generate background coordinate structures
    for (let i = 0; i < 15; i++) {
        buildings.push({
            x: i * 250,
            y: 0,
            width: 200 + Math.random() * 100,
            height: 300 + Math.random() * 200,
            type: Math.random() > 0.5 ? 'hall' : 'tower'
        });
    }
}

let time = 0;
function animate() {
    // 3. Simple update and draw calls ONLY
    time += 0.05;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    ctx.save();
    ctx.scale(scale, scale); // Apply scaling
    
    // Draw background layers...
    drawParallaxBuildings(ctx, buildings, time * 100);
    drawGoldenRetriever(ctx, targetWidth * 0.4, targetHeight * 0.8, time, colors);
    
    ctx.restore();
    
    requestAnimationFrame(animate); // Keep loop going at 60 FPS
}

// Start sequence
setup();
animate();
```
