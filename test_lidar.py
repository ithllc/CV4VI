#!/usr/bin/env python3
"""
Simple LiDAR processing script for generating depth maps from NYC LAS files
Based on the POCworkplan.md requirements
"""

import os
import numpy as np
import cv2
from PIL import Image
import laspy
import streamlit as st
import requests
from io import BytesIO

def create_sample_depth_map():
    """Create a sample depth map for testing when no LiDAR data is available"""
    H, W = 224, 224
    
    # Create a more realistic depth pattern
    depth_array = np.zeros((H, W), dtype=np.float32)
    
    # Simulate a path with obstacles
    # Ground plane (far)
    depth_array[:, :] = 10.0
    
    # Path/sidewalk (closer)
    depth_array[H//3:2*H//3, W//4:3*W//4] = 2.0
    
    # Obstacles (closest)
    # Left obstacle (building/wall)
    depth_array[50:150, 20:60] = 0.5
    
    # Right obstacle (tree/pole)
    depth_array[80:180, 160:200] = 1.0
    
    # Add some noise for realism
    noise = np.random.normal(0, 0.1, (H, W))
    depth_array += noise
    
    return depth_array

def load_las_file(las_path):
    """Load a LAS file and extract point cloud data"""
    try:
        las = laspy.read(las_path)
        
        # Extract coordinates
        x = las.x
        y = las.y  
        z = las.z
        
        # Stack into points array
        points = np.vstack((x, y, z)).transpose()
        
        st.info(f"Loaded {len(points)} points from {las_path}")
        st.write(f"X range: {x.min():.2f} to {x.max():.2f}")
        st.write(f"Y range: {y.min():.2f} to {y.max():.2f}")
        st.write(f"Z range: {z.min():.2f} to {z.max():.2f}")
        
        return points, las
        
    except Exception as e:
        st.error(f"Error loading LAS file: {e}")
        return None, None

def points_to_depth_map(points, H=224, W=224, view_type="forward"):
    """Convert 3D points to a 2D depth map"""
    if points is None or len(points) == 0:
        return create_sample_depth_map()
    
    x = points[:, 0]
    y = points[:, 1] 
    z = points[:, 2]
    
    if view_type == "forward":
        # Forward-facing view: Y is horizontal, Z is vertical, X is depth
        # Filter points in front of the sensor
        forward_mask = x > x.min() + (x.max() - x.min()) * 0.1  # Keep front 90%
        points_filtered = points[forward_mask]
        
        if len(points_filtered) == 0:
            return create_sample_depth_map()
            
        x_f = points_filtered[:, 0]
        y_f = points_filtered[:, 1]
        z_f = points_filtered[:, 2]
        
        # Map Y to horizontal image coordinates
        y_img = ((y_f - y_f.min()) / (y_f.max() - y_f.min()) * (W - 1)).astype(int)
        # Map Z to vertical image coordinates (flip for image coordinates)
        z_img = ((z_f.max() - z_f) / (z_f.max() - z_f.min()) * (H - 1)).astype(int)
        
        # Use X as depth
        depth_values = x_f
        
    else:  # top-down view
        # Map X,Y to image coordinates, use Z as depth
        x_img = ((x - x.min()) / (x.max() - x.min()) * (W - 1)).astype(int)
        y_img = ((y - y.min()) / (y.max() - y.min()) * (H - 1)).astype(int)
        depth_values = z
        z_img = y_img
        y_img = x_img
    
    # Create depth map
    depth_map = np.zeros((H, W), dtype=np.float32)
    
    # Fill depth map (use max depth per pixel to avoid occlusion issues)
    for yi, xi, depth in zip(z_img, y_img, depth_values):
        if 0 <= yi < H and 0 <= xi < W:
            depth_map[yi, xi] = max(depth_map[yi, xi], depth)
    
    # Handle empty pixels by interpolation
    mask = depth_map == 0
    if np.any(~mask):
        from scipy.ndimage import binary_dilation
        # Simple interpolation: use nearest non-zero value
        depth_map[mask] = np.mean(depth_map[~mask])
    
    return depth_map

def create_colored_depth_map(depth_array):
    """Convert depth array to colored visualization"""
    # Normalize depth values
    normalized = cv2.normalize(depth_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    # Apply colormap
    colored = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
    
    # Convert BGR to RGB for PIL
    colored_rgb = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
    
    return Image.fromarray(colored_rgb)

def download_sample_las():
    """Download a small sample LAS file for testing"""
    # This is a placeholder function - in practice you'd download from the NYC FTP
    st.warning("Sample LAS download not implemented. Using simulated data.")
    return None

def test_lidar_processing():
    """Test LiDAR processing functionality"""
    st.title("🗂️ LiDAR Processing Test")
    
    st.subheader("LiDAR Data Sources")
    st.write("""
    **Recommended Dataset:** NYC 2017 Topobathymetric Classified Point Cloud (LAS 1.4)
    - **FTP Location:** ftp://ftp.gis.ny.gov/elevation/LIDAR/NYC_2021/
    - **Format:** LAS 1.4 (compatible with laspy 2.5.4)
    - **Coverage:** All of NYC + 100m buffer
    - **Resolution:** 10.75+ points/m²
    - **Classifications:** Ground, Water, Buildings, etc.
    """)
    
    # File upload option
    uploaded_las = st.file_uploader("Upload a LAS file for testing:", type=['las', 'laz'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Point Cloud")
        
        if uploaded_las is not None:
            # Save uploaded file temporarily
            temp_path = f"/tmp/{uploaded_las.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_las.read())
            
            points, las_data = load_las_file(temp_path)
            
            if points is not None:
                st.success(f"Loaded {len(points)} points")
                
                # Show classification info if available
                if hasattr(las_data, 'classification'):
                    unique_classes = np.unique(las_data.classification)
                    st.write(f"Classifications found: {unique_classes}")
        else:
            st.info("No LAS file uploaded. Using simulated data.")
            points = None
    
    with col2:
        st.subheader("Generated Depth Map")
        
        view_type = st.selectbox("View Type:", ["forward", "top-down"])
        
        if st.button("Generate Depth Map"):
            with st.spinner("Processing point cloud..."):
                depth_array = points_to_depth_map(points, view_type=view_type)
                
                # Create colored visualization
                depth_image = create_colored_depth_map(depth_array)
                
                st.image(depth_image, caption=f"{view_type} depth map")
                
                # Save for use with Moondream
                depth_image.save("/tmp/depth_map_color.png")
                st.success("Depth map saved as /tmp/depth_map_color.png")
                
                # Show some statistics
                st.write(f"Depth range: {depth_array.min():.2f} to {depth_array.max():.2f}")
                st.write(f"Mean depth: {depth_array.mean():.2f}")

def main():
    """Main function for LiDAR testing"""
    st.set_page_config(
        page_title="LiDAR Processing Test", 
        page_icon="🗂️",
        layout="wide"
    )
    
    test_lidar_processing()
    
    # Information sidebar
    st.sidebar.title("NYC LiDAR Info")
    st.sidebar.write("""
    **2017 Dataset Features:**
    - Topographic + Bathymetric
    - LAS 1.4 format
    - Pre-classified points
    - High resolution (10+ pts/m²)
    - Coordinate system: NY State Plane
    - Includes geolocation data
    
    **Edge Device Strategy:**
    - Download specific tiles only
    - Focus on camera intersection areas
    - Use classification filters
    - Preprocess to depth maps
    """)
    
    st.sidebar.title("Next Steps")
    st.sidebar.write("""
    1. ✅ Test basic LAS file loading
    2. ✅ Generate depth maps
    3. 🔄 Integrate with Moondream2
    4. 🔄 Add NYC webcam locations
    5. 🔄 Implement geolocation logic
    """)

if __name__ == "__main__":
    main()
