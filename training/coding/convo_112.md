# الرمز التعريفي للمحادثة: Convo_112

User:
How do I create a 3D rotating cube with realistic lighting and shadows using three.js that responds to mouse movement on a web page?

---

Bot
Here's a complete solution for a 3D rotating cube with realistic lighting and shadows that responds to mouse movement:

```html
<!DOCTYPE html>
<html>
<head>
    <title>3D Rotating Cube</title>
    <style>
        body { margin: 0; overflow: hidden; }
        canvas { display: block; }
    </style>
</head>
<body>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x101010);
        
        // Camera
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 5;
        
        // Renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFShadowMap;
        document.body.appendChild(renderer.domElement);
        
        // Create cube with material that supports shadows
        const geometry = new THREE.BoxGeometry(1, 1, 1);
        const material = new THREE.MeshPhongMaterial({ 
            color: 0x00aaff,
            shininess: 100,
            specular: 0xffffff
        });
        
        const cube = new THREE.Mesh(geometry, material);
        cube.castShadow = true;
        scene.add(cube);
        
        // Add ground plane for shadows
        const planeGeometry = new THREE.PlaneGeometry(10, 10);
        const planeMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x222222,
            side: THREE.DoubleSide
        });
        const plane = new THREE.Mesh(planeGeometry, planeMaterial);
        plane.rotation.x = Math.PI / 2;
        plane.position.y = -1.5;
        plane.receiveShadow = true;
        scene.add(plane);
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(3, 5, 2);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 1024;
        directionalLight.shadow.mapSize.height = 1024;
        scene.add(directionalLight);
        
        // Mouse movement
        let mouseX = 0;
        let mouseY = 0;
        
        function onMouseMove(event) {
            mouseX = (event.clientX / window.innerWidth) * 2 - 1;
            mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
        }
        
        window.addEventListener('mousemove', onMouseMove);
        
        // Handle window resize
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
        
        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            
            // Rotate cube based on mouse position
            cube.rotation.x += mouseY * 0.01;
            cube.rotation.y += mouseX * 0.01;
            
            renderer.render(scene, camera);
        }
        
        animate();
    </script>
</body>
</html>
```

Key features:
- Realistic Phong shading with specular highlights
- Directional light casting shadows with proper shadow mapping
- Ground plane that receives shadows
- Mouse movement controls rotation along both axes
- Responsive design that handles window resizing
- Smooth animation using requestAnimationFrame

The cube will rotate in response to mouse position - move your cursor left/right to rotate around the Y-axis, up/down to rotate around the X-axis. The lighting and shadows will update in real-time as you move the mouse.

To customize:
- Change colors by modifying the material color values
- Adjust rotation speed by changing the multiplier in the rotation calculations
- Modify light intensity by changing the second parameter in DirectionalLight constructor
- Change shadow quality by adjusting mapSize values

The scene includes proper shadow casting and receiving, ambient lighting for overall illumination, and directional light that creates realistic shading effects. The cube material uses Phong shading which provides better lighting response than basic Lambert shading.

---

User:
Whoa, that's a lot of code. I'm still kinda confused about the shadow part—does it work on all browsers?

---

Bot
### Understanding Shadows in Three.js

I get it—the code can feel overwhelming at first, especially with shadows added on top. Let's break down the shadow implementation step by step, focusing on what's directly needed for your rotating cube. I'll explain how it works practically, then address browser compatibility.

#### Key Components for Shadows
Shadows in Three.js rely on a technique called **shadow mapping**, where the scene is rendered from the light's point of view to create a "map" of what's in shadow. Here's the breakdown from the code:

1. **Enable Shadow Mapping on the Renderer**:  
   ```javascript
   renderer.shadowMap.enabled = true;
   renderer.shadowMap.type = THREE.PCFShadowMap;
   ```  
   This tells Three.js to calculate shadows. `PCFShadowMap` is a high-quality option that softens shadow edges for realism (compared to basic hard shadows).

2. **Set Up the Light to Cast Shadows**:  
   ```javascript
   const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
   directionalLight.castShadow = true;
   directionalLight.shadow.mapSize.width = 1024;
   directionalLight.shadow.mapSize.height = 1024;
   ```  
   Only directional lights can cast shadows here (point lights or spotlights work too). The `mapSize` controls shadow resolution—higher numbers (like 2048) make shadows sharper but slower to render. Start with 1024 for balance on most devices.

3. **Make Objects Cast or Receive Shadows**:  
   - On the cube: `cube.castShadow = true;` (the cube will block light, creating shadows).  
   - On the plane: `plane.receiveShadow = true;` (the plane shows where shadows fall).  
   Without these, objects ignore shadows.

4. **Why a Ground Plane?**  
   It provides a surface for shadows to appear. Without it, shadows would "fall" into nothingness, making the effect harder to see.

In your animation loop, shadows update automatically as the cube rotates— no extra code needed.

#### Browser Compatibility
Yes, shadows work on most modern browsers, but let's be specific:
- **Supported Browsers**: Chrome (version 51+), Firefox (version 51+), Safari (version 10+), Edge (version 79+), and newer versions of mobile browsers like iOS Safari. These support WebGL (the underlying tech for Three.js graphics and shadows).
- **Exceptions**: Internet Explorer (even IE11) doesn't fully support WebGL shadows due to older rendering engines. Very old browsers (e.g., pre-2015 versions) might not work at all. If WebGL is disabled in browser settings, it won't render.
- **Testing Tip**: Open the page in your browser and check developer tools (F12) for errors. If you see WebGL-related warnings, try updating your browser or enabling hardware acceleration in settings.

Does this clarify how shadows are set up and why they might not work everywhere? If you're testing on a specific browser, let me know for more tailored advice.

Next steps: Try running the code in a compatible browser (like Chrome or Firefox) and observe the shadows as you move the mouse. Experiment by commenting out `renderer.shadowMap.enabled = true;` to see the difference—no shadows without it. What part still feels unclear? We can tweak the code from there.

---

User:
Wait, so if IE doesn't work, what about on my phone? Does it lag a lot?

---

Bot
### Mobile Compatibility for Your 3D Cube

You're right to ask about mobile—it's a common concern since phones dominate web usage. Let's break this down step by step, focusing on how the code performs on smartphones and why you might see lag. I'll also address the key issue with mouse controls not working on touch devices.

#### Does It Work on Phones?
Yes, the cube with shadows should work on most modern smartphones, but with caveats:
- **Supported Devices**: iPhones (iOS Safari, versions 10+), Android phones (Chrome, Firefox, or Samsung Internet, versions 51+), and other mobile browsers that support WebGL. WebGL is the core technology powering Three.js graphics and shadows on mobile.
- **Exceptions**: Very old phones (e.g., iPhone 6 or older Android devices from 2015-2017) might struggle or not render at all due to limited hardware. If a phone's browser has WebGL disabled (rare but possible in settings), it won't work.
- **Testing Tip**: Try opening the page on your phone's browser. If it loads but looks blank, check for browser errors in developer tools (usually accessible via a menu or by tapping the URL bar and typing "debug" or similar). A quick online WebGL test (like get.webgl.org) can confirm if your device supports it.

#### Performance and Lag Concerns
Mobile devices often have less powerful GPUs (graphics processors) than desktops, so lag is a real risk, especially with complex features like shadows. Here's why and how to mitigate it:
- **Why Lag Happens**: Shadows involve extra calculations (rendering the scene from the light's view to create the shadow map). On mobile, this can drop frame rates below 60 FPS, causing stuttering or choppy rotation. The 1024x1024 shadow map size in the code is decent for desktops but can be too high for phones.
- **Expected Performance**: On a mid-range phone (e.g., iPhone 11 or Samsung Galaxy A50), you might see smooth performance at 60 FPS without shadows. With shadows enabled, it could drop to 30-45 FPS, feeling laggy. High-end phones (e.g., iPhone 15 or Pixel 8) handle it better. Battery drain and heat are also concerns during prolonged use.
- **Optimizations to Reduce Lag**:
  - Lower shadow quality: Change `directionalLight.shadow.mapSize.width = 512;` and `directionalLight.shadow.mapSize.height = 512;` (half the resolution) for faster rendering on mobile.
  - Disable shadows on mobile: Add a check like `if (!/Mobi|Android/i.test(navigator.userAgent)) { renderer.shadowMap.enabled = true; ... }` to enable shadows only on desktops (detects mobile via user agent).
  - Reduce antialiasing if needed: Change `{ antialias: true }` to `false` for smoother performance on weaker devices.
  - Test and profile: Use browser dev tools to monitor FPS (under Performance tab) while moving the mouse (or simulating touch).

If lag persists, it's often due to hardware limits rather than the code—Three.js is optimized, but mobile GPUs prioritize power efficiency over speed.

#### Key Fix: Mouse Events Don't Work on Touch Phones
The biggest issue is that the code uses `window.addEventListener('mousemove', onMouseMove);`, which only responds to mouse movement on desktops. Phones use touch gestures, so the cube won't rotate at all.
- **Solution**: Add touch event support. Update the code to handle both mouse and touch. Replace the mouse event section with this:
  ```javascript
  let mouseX = 0;
  let mouseY = 0;
  
  function onPointerMove(event) {
      // Normalize to -1 to 1 range
      mouseX = (event.clientX / window.innerWidth) * 2 - 1;
      mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
  }
  
  // For mouse (desktop)
  window.addEventListener('mousemove', onPointerMove);
  
  // For touch (mobile) - use touchmove event
  window.addEventListener('touchmove', (event) => {
      // Prevent scrolling while dragging
      event.preventDefault();
      // Get the first touch point
      const touch = event.touches[0];
      // Simulate mouse event
      onPointerMove({ clientX: touch.clientX, clientY: touch.clientY });
  });
  ```
  This makes the cube respond to finger dragging on phones, just like mouse movement on desktop. The rotation logic (`cube.rotation.x += mouseY * 0.01; cube.rotation.y += mouseX * 0.01;`) stays the same.

Paste this into your existing code, replacing the original mouse event section. Now the cube should rotate smoothly on both desktop and mobile.

Does this address your concerns about mobile lag and controls? Have you tested it on your phone yet? If it still lags, share your device model, and we can fine-tune the shadow settings further.

**Next Steps**: 
1. Update the code with the touch event fix above.
2. Lower the shadow map size to 512x512 and test on your phone.
3. If needed, disable shadows on mobile using the user agent check.
4. Experiment: Change the rotation multiplier (e.g., 0.01 to 0.005) for slower, smoother movement on mobile. What did you observe when running it? Let's iterate from there.

---

