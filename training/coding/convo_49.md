# الرمز التعريفي للمحادثة: Convo_49

User:
How do I properly implement a custom shader material in three.js that combines both vertex and fragment shaders to create a realistic water surface effect with dynamic reflections and refractions while maintaining optimal performance for mobile browsers?

---

Bot
To create a realistic water shader in three.js with dynamic reflections and refractions while maintaining mobile performance, start with a basic vertex-fragment shader setup.

For the vertex shader, you'll want to animate the water surface using sine waves or noise functions. Keep it simple - avoid expensive calculations that will bog down mobile devices. Use `gl_Position` to transform vertices and add displacement based on time and position.

In the fragment shader, implement a basic Fresnel effect for reflections and use environment mapping for dynamic reflections. For refractions, you can either use a pre-rendered cube map or a screen-space approach that's more performant on mobile.

Key performance tips:
- Use lower resolution environment maps
- Limit the number of light calculations
- Consider using `gl_FragColor` with simple blending rather than complex lighting models
- Implement level-of-detail techniques where the water surface uses fewer waves or less detailed displacement on mobile

Use three.js's built-in `ShaderMaterial` and pass in your custom shader strings. For reflections, you can either:
1. Use a separate reflection camera setup (more accurate but expensive)
2. Use screen-space reflections with a lower resolution texture
3. Implement a simple environment mapping approach that works well across devices

The key is to find the right balance between visual quality and performance - start with a basic implementation and optimize based on actual device behavior rather than assumptions.

---

User:
That Fresnel effect stuff sounds tricky—how do I even calculate that in the shader without it killing the framerate on my phone?

---

Bot
### Understanding the Fresnel Effect in Shaders

The Fresnel effect simulates how light reflects more intensely off a surface when viewed at grazing angles (like looking across water), blending reflections and refractions realistically. It's not inherently performance-heavy—it's just a few dot products and multiplications—so it won't kill your framerate on mobile if implemented simply. The key is to avoid overcomplicating it with unnecessary lighting or multiple samples.

#### Quick Breakdown of the Calculation
You calculate Fresnel based on the angle between the view direction (from camera to surface) and the surface normal. At perpendicular angles, refraction dominates; at shallow angles, reflection takes over.

1. **Compute the view direction**: In the fragment shader, subtract the vertex position from the camera position (use `cameraPosition` uniform in three.js).
2. **Normalize vectors**: Ensure both the view direction and normal are unit vectors.
3. **Dot product for angle**: Use `dot(normal, viewDir)` to get the cosine of the angle (theta). Fresnel intensity is often approximated as `pow(1.0 - dot(normal, viewDir), exponent)`, where the exponent (e.g., 2-5) controls the sharpness—lower for smoother transitions.
4. **Blend reflections and refractions**: Multiply your reflection color by the Fresnel value and refraction color by (1.0 - Fresnel value), then add them.

This is efficient: it adds maybe 5-10 operations per pixel, negligible on most mobile GPUs.

#### Simple Fragment Shader Example
Here's a stripped-down GLSL snippet for your water shader. Assume you're using three.js's `ShaderMaterial` with uniforms for reflection/refract textures. I'll focus only on the Fresnel part—integrate it into your existing fragment shader.

```glsl
uniform vec3 cameraPosition;  // Passed from three.js
varying vec3 vNormal;         // From vertex shader
varying vec3 vPosition;       // World position from vertex shader

void main() {
    // Normalize view direction
    vec3 viewDir = normalize(cameraPosition - vPosition);
    
    // Fresnel approximation (simple and fast)
    float fresnel = pow(1.0 - max(0.0, dot(vNormal, viewDir)), 2.0);  // Exponent of 2 for mobile performance
    
    // Example: Blend reflection (from env map) and refraction (from below surface)
    vec3 reflectionColor = textureCube(reflectionMap, reflect(-viewDir, vNormal)).rgb;
    vec3 refractionColor = texture2D(refractMap, screenUV).rgb;  // Screen-space refraction for simplicity
    
    // Blend based on Fresnel
    vec3 finalColor = mix(refractionColor, reflectionColor, fresnel);
    
    gl_FragColor = vec4(finalColor, 1.0);
}
```

- **Why this works on mobile**: No loops, no heavy math—just vector ops that GPUs handle in parallel. If your normals are pre-computed (e.g., flat for water), it's even faster.
- **Common pitfall**: If your normals aren't normalized, the dot product will give weird results. Pass them from the vertex shader and normalize in frag if needed.
- **Optimization tip**: For very low-end mobile, hardcode the exponent to 1.0 for a linear blend, sacrificing some realism for speed.

Does this clarify how to plug it in without performance hits? Have you tried a basic version yet, or need help with the full vertex/fragment integration? As a next step, add this to a simple plane geometry in three.js and test on your phone—tweak the exponent based on visuals. Let me know what you observe!

---

