import React, { useEffect, useState } from 'react';
import { ImageOverlay, useMap } from 'react-leaflet';
import * as GeoTIFF from 'geotiff';
import * as plotty from 'plotty';
import type { LatLngBoundsExpression } from 'leaflet';

interface TiffLayerProps {
    file: File | null;
    opacity?: number;
}

export const TiffLayer: React.FC<TiffLayerProps> = ({ file, opacity = 0.7 }) => {
    const map = useMap();
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [bounds, setBounds] = useState<LatLngBoundsExpression | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!file) {
            setImageUrl(null);
            setBounds(null);
            setError(null);
            return;
        }

        const processTiff = async () => {
            setLoading(true);
            setError(null);

            try {
                // Check file size
                const fileSizeMB = file.size / (1024 * 1024);
                console.log(`TIFF size: ${fileSizeMB.toFixed(2)} MB`);

                if (fileSizeMB > 500) {
                    throw new Error(`File too large (${fileSizeMB.toFixed(0)}MB). Max: 500MB`);
                }

                const arrayBuffer = await file.arrayBuffer();
                const tiff = await GeoTIFF.fromArrayBuffer(arrayBuffer);
                const image = await tiff.getImage();

                // Get dimensions
                const width = image.getWidth();
                const height = image.getHeight();
                console.log(`TIFF: ${width}x${height} pixels`);

                // Auto-downsample if needed (max 2048x2048)
                const maxDim = 2048;
                let targetWidth = width;
                let targetHeight = height;

                if (width > maxDim || height > maxDim) {
                    const scale = Math.max(width / maxDim, height / maxDim);
                    targetWidth = Math.floor(width / scale);
                    targetHeight = Math.floor(height / scale);
                    console.log(`Downsampling to ${targetWidth}x${targetHeight}`);
                }

                // Read with downsampling
                let rasters;
                if (targetWidth < width || targetHeight < height) {
                    rasters = await image.readRasters({
                        window: [0, 0, width, height],
                        width: targetWidth,
                        height: targetHeight,
                        samples: [0]
                    });
                } else {
                    rasters = await image.readRasters({ samples: [0] });
                }

                const data = rasters[0] as unknown as Float32Array;

                if (!data || data.length === 0) {
                    throw new Error('Failed to read TIFF data');
                }

                // Create canvas
                const canvas = document.createElement('canvas');
                canvas.width = targetWidth;
                canvas.height = targetHeight;

                // Calculate domain (ignore nodata)
                let min = Infinity;
                let max = -Infinity;
                let validCount = 0;

                for (let i = 0; i < data.length; i++) {
                    if (!isNaN(data[i]) && isFinite(data[i]) && data[i] !== -9999 && data[i] !== 0) {
                        if (data[i] < min) min = data[i];
                        if (data[i] > max) max = data[i];
                        validCount++;
                    }
                }

                if (validCount === 0 || min === Infinity || max === -Infinity) {
                    throw new Error('No valid data values found');
                }

                console.log(`Range: ${min.toFixed(2)} - ${max.toFixed(2)} (${validCount} valid)`);

                // Create a temporary canvas for Plotty (WebGL)
                const tempCanvas = document.createElement('canvas');
                tempCanvas.width = targetWidth;
                tempCanvas.height = targetHeight;

                const plot = new plotty.plot({
                    canvas: tempCanvas,
                    data: data,
                    width: targetWidth,
                    height: targetHeight,
                    domain: [min, max],
                    colorScale: 'greys',
                    clampLow: false,
                    clampHigh: false,
                });

                plot.render();

                // Create a second canvas to apply alpha masking (2D)
                // We can't use '2d' and 'webgl' on the same canvas
                const finalCanvas = document.createElement('canvas');
                finalCanvas.width = targetWidth;
                finalCanvas.height = targetHeight;
                const ctx = finalCanvas.getContext('2d')!;

                // Draw the WebGL result onto the 2D canvas
                ctx.drawImage(tempCanvas, 0, 0);

                // Apply transparency to NoData pixels using the 2D context
                const imageData = ctx.getImageData(0, 0, targetWidth, targetHeight);
                const pixels = imageData.data;

                for (let i = 0; i < data.length; i++) {
                    // Set alpha to 0 for NoData values (-9999, 0, or NaN/Infinite)
                    if (data[i] === -9999 || data[i] === 0 || !isFinite(data[i])) {
                        const pixelIndex = i * 4;
                        pixels[pixelIndex + 3] = 0; // Set alpha channel to transparent
                    }
                }

                ctx.putImageData(imageData, 0, 0);
                setImageUrl(finalCanvas.toDataURL());

                // Get bounds and projection info
                const bbox = image.getBoundingBox();
                if (!bbox) {
                    throw new Error('TIFF has no geographic bounds');
                }

                // Get projection (GeoKeys or WKT)
                const geoKeys = image.getGeoKeys();
                let sourceProj = 'EPSG:4326'; // Default to WGS84

                // Try to determine source projection
                if (geoKeys) {
                    // Check for EPSG code
                    if (geoKeys.ProjectedCSTypeGeoKey) {
                        sourceProj = `EPSG:${geoKeys.ProjectedCSTypeGeoKey}`;
                    } else if (geoKeys.GeographicTypeGeoKey) {
                        sourceProj = `EPSG:${geoKeys.GeographicTypeGeoKey}`;
                    }
                }

                console.log(`Source projection: ${sourceProj}`);

                // Transform coordinates if not already WGS84
                let southWest: [number, number];
                let northEast: [number, number];

                if (sourceProj !== 'EPSG:4326' && Math.abs(bbox[0]) > 180) {
                    // Import proj4 dynamically
                    const proj4 = (await import('proj4')).default;

                    try {
                        // Transform corner coordinates
                        const swTransformed = proj4(sourceProj, 'EPSG:4326', [bbox[0], bbox[1]]);
                        const neTransformed = proj4(sourceProj, 'EPSG:4326', [bbox[2], bbox[3]]);

                        southWest = [swTransformed[1], swTransformed[0]];
                        northEast = [neTransformed[1], neTransformed[0]];

                        console.log(`Transformed from ${sourceProj} to WGS84`);
                        console.log(`SW: [${southWest}], NE: [${northEast}]`);
                    } catch (projError) {
                        console.error('Projection transformation failed:', projError);
                        throw new Error(`Cannot transform from ${sourceProj} to WGS84. TIFF may need reprojection.`);
                    }
                } else {
                    // Already in geographic coordinates
                    southWest = [bbox[1], bbox[0]];
                    northEast = [bbox[3], bbox[2]];
                }

                // Validate coordinates
                if (Math.abs(southWest[0]) > 90 || Math.abs(southWest[1]) > 180) {
                    throw new Error('Invalid coordinates after transformation. TIFF projection may not be recognized.');
                }

                setBounds([southWest, northEast]);
                map.fitBounds([southWest, northEast]);

                setLoading(false);
            } catch (err) {
                console.error("Error processing TIFF:", err);
                setError(err instanceof Error ? err.message : 'Failed to process TIFF');
                setImageUrl(null);
                setBounds(null);
                setLoading(false);
            }
        };

        processTiff();
    }, [file, map]);

    if (error) {
        return (
            <div className="absolute bottom-4 left-4 z-[1000] bg-red-500/90 text-white px-4 py-3 rounded-lg shadow-lg max-w-md">
                <p className="font-semibold mb-1">TIFF Processing Error</p>
                <p className="text-sm mb-2">{error}</p>
                <p className="text-xs opacity-90">Tip: Use files &lt;50MB or Cloud Optimized GeoTIFFs</p>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="absolute bottom-4 left-4 z-[1000] bg-blue-500/90 text-white px-4 py-2 rounded-lg shadow-lg">
                <p className="text-sm font-medium">Processing TIFF...</p>
                <p className="text-xs opacity-90">Large files may take a moment</p>
            </div>
        );
    }

    if (!imageUrl || !bounds) return null;

    return <ImageOverlay url={imageUrl} bounds={bounds} opacity={opacity} />;
};
