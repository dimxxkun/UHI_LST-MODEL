import React, { useEffect, useState } from 'react';
import { ImageOverlay, useMap } from 'react-leaflet';
import * as GeoTIFF from 'geotiff';
import type { LatLngBoundsExpression } from 'leaflet';
import proj4 from 'proj4';

interface CompositeTiffLayerProps {
    redBand: File | null;
    greenBand: File | null;
    blueBand: File | null;
    opacity?: number;
}

export const CompositeTiffLayer: React.FC<CompositeTiffLayerProps> = ({
    redBand,
    greenBand,
    blueBand,
    opacity = 1.0
}) => {
    const map = useMap();
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [bounds, setBounds] = useState<LatLngBoundsExpression | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!redBand || !greenBand || !blueBand) {
            setImageUrl(null);
            setBounds(null);
            return;
        }

        const processComposite = async () => {
            setLoading(true);
            setError(null);

            try {
                // Read all three bands
                const loadBand = async (file: File) => {
                    const buffer = await file.arrayBuffer();
                    const tiff = await GeoTIFF.fromArrayBuffer(buffer);
                    const image = await tiff.getImage();
                    return { tiff, image };
                };

                const [rData, gData, bData] = await Promise.all([
                    loadBand(redBand),
                    loadBand(greenBand),
                    loadBand(blueBand)
                ]);

                // Use dimension from first band (assume they match or we'll scale)
                const width = rData.image.getWidth();
                const height = rData.image.getHeight();

                // Downsample for performance (max 1024x1024)
                const maxDim = 1024;
                let targetWidth = width;
                let targetHeight = height;
                if (width > maxDim || height > maxDim) {
                    const scale = Math.max(width / maxDim, height / maxDim);
                    targetWidth = Math.floor(width / scale);
                    targetHeight = Math.floor(height / scale);
                }

                const readRaster = async (image: GeoTIFF.GeoTIFFImage) => {
                    const rasters = await image.readRasters({
                        window: [0, 0, width, height],
                        width: targetWidth,
                        height: targetHeight,
                        samples: [0]
                    });
                    return rasters[0] as Float32Array;
                };

                const [rArray, gArray, bArray] = await Promise.all([
                    readRaster(rData.image),
                    readRaster(gData.image),
                    readRaster(bData.image)
                ]);

                // Create canvas for RGB
                const canvas = document.createElement('canvas');
                canvas.width = targetWidth;
                canvas.height = targetHeight;
                const ctx = canvas.getContext('2d')!;
                const imageData = ctx.createImageData(targetWidth, targetHeight);
                const pixels = imageData.data;

                // Function to stretch values (0-65535 to 0-255 with 2% clip)
                const getStats = (data: Float32Array) => {
                    let min = Infinity, max = -Infinity;
                    // Sampling for speed
                    const step = Math.max(1, Math.floor(data.length / 5000));
                    for (let i = 0; i < data.length; i += step) {
                        const v = data[i];
                        // Ignore -9999, 0, and NaN for stats
                        if (v !== -9999 && v !== 0 && !isNaN(v)) {
                            if (v < min) min = v;
                            if (v > max) max = v;
                        }
                    }
                    return { min, max };
                };

                const rStats = getStats(rArray);
                const gStats = getStats(gArray);
                const bStats = getStats(bArray);

                // Combine bands
                for (let i = 0; i < rArray.length; i++) {
                    const idx = i * 4;
                    const r = rArray[i];
                    const g = gArray[i];
                    const b = bArray[i];

                    if (r === -9999 || r === 0 || isNaN(r)) {
                        pixels[idx + 3] = 0; // Transparent
                        continue;
                    }

                    // Simple linear stretch with enhancement
                    const stretch = (val: number, min: number, max: number) => {
                        const norm = (val - min) / (max - min);
                        // Apply gamma correction (0.8) to brighten midtones
                        return Math.min(255, Math.pow(Math.max(0, norm), 0.8) * 255);
                    };

                    pixels[idx] = stretch(r, rStats.min, rStats.max);
                    pixels[idx + 1] = stretch(g, gStats.min, gStats.max);
                    pixels[idx + 2] = stretch(b, bStats.min, bStats.max);
                    pixels[idx + 3] = 255; // Solid
                }

                ctx.putImageData(imageData, 0, 0);
                setImageUrl(canvas.toDataURL());

                // Set bounds (from red band)
                const bbox = rData.image.getBoundingBox();
                const geoKeys = rData.image.getGeoKeys();
                let sourceProj = 'EPSG:4326';
                if (geoKeys?.ProjectedCSTypeGeoKey) {
                    sourceProj = `EPSG:${geoKeys.ProjectedCSTypeGeoKey}`;
                }

                let sw: [number, number], ne: [number, number];
                if (sourceProj !== 'EPSG:4326' && Math.abs(bbox[0]) > 180) {
                    const swT = proj4(sourceProj, 'EPSG:4326', [bbox[0], bbox[1]]);
                    const neT = proj4(sourceProj, 'EPSG:4326', [bbox[2], bbox[3]]);
                    sw = [swT[1], swT[0]];
                    ne = [neT[1], neT[0]];
                } else {
                    sw = [bbox[1], bbox[0]];
                    ne = [bbox[3], bbox[2]];
                }

                setBounds([sw, ne]);
                map.fitBounds([sw, ne]);
                setLoading(false);

            } catch (err) {
                console.error("Composite processing error:", err);
                setError(err instanceof Error ? err.message : 'RGB Processing Failed');
                setLoading(false);
            }
        };

        processComposite();
    }, [redBand, greenBand, blueBand]);

    if (loading) return (
        <div className="absolute bottom-4 left-4 z-[1000] bg-indigo-600/90 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
            <span className="text-sm font-medium">Generating True Color Composite...</span>
        </div>
    );

    if (error) return (
        <div className="absolute bottom-4 left-4 z-[1000] bg-red-600/90 text-white px-4 py-2 rounded-lg shadow-lg">
            <p className="text-xs font-bold">RGB Error: {error}</p>
        </div>
    );

    if (!imageUrl || !bounds) return null;

    return <ImageOverlay url={imageUrl} bounds={bounds} opacity={opacity} />;
};
