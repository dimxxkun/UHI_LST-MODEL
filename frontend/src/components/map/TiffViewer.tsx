import React, { useEffect, useRef, useState } from 'react';
import * as GeoTIFF from 'geotiff';
import * as plotty from 'plotty';

interface TiffViewerProps {
    file: File | null;
    className?: string;
}

export const TiffViewer: React.FC<TiffViewerProps> = ({ file, className = "" }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!file || !canvasRef.current) return;

        const renderTiff = async () => {
            setLoading(true);
            setError(null);
            try {
                const arrayBuffer = await file.arrayBuffer();
                const tiff = await GeoTIFF.fromArrayBuffer(arrayBuffer);
                const image = await tiff.getImage();
                const rasters = await image.readRasters();
                const width = image.getWidth();
                const height = image.getHeight();

                // Use the first band for visualization
                const data = rasters[0] as unknown as Float32Array; // Geometric data often float32

                const plot = new plotty.plot({
                    canvas: canvasRef.current,
                    data: data,
                    width: width,
                    height: height,
                    domain: [0, 65535], // Adjust based on data type (e.g. Landsat DN) or calculate min/max
                    colorScale: 'viridis',
                    clampLow: true,
                    clampHigh: true,
                });

                // Auto calculate domain for better contrast if possible
                // Simple min/max scan
                let min = Infinity;
                let max = -Infinity;
                for (let i = 0; i < data.length; i++) {
                    // plotting usually ignores NaNs, but for min/max we check
                    if (!isNaN(data[i])) {
                        if (data[i] < min) min = data[i];
                        if (data[i] > max) max = data[i];
                    }
                }

                if (min !== Infinity && max !== -Infinity) {
                    plot.setDomain([min, max]);
                }

                plot.render();
            } catch (err) {
                console.error("Error rendering TIFF:", err);
                setError("Failed to render TIFF image.");
            } finally {
                setLoading(false);
            }
        };

        renderTiff();
    }, [file]);

    if (!file) {
        return (
            <div className={`flex items-center justify-center bg-slate-100 dark:bg-slate-800 rounded-lg border-2 border-dashed border-slate-300 dark:border-slate-700 ${className}`}>
                <p className="text-slate-500 text-sm">No TIFF file selected</p>
            </div>
        );
    }

    return (
        <div className={`relative overflow-hidden rounded-lg bg-black ${className}`}>
            {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50 text-white z-10">
                    Loading...
                </div>
            )}
            {error && (
                <div className="absolute inset-0 flex items-center justify-center bg-red-900/50 text-red-200 z-10 p-4 text-center">
                    {error}
                </div>
            )}
            <canvas
                ref={canvasRef}
                className="w-full h-full object-contain"
            />
        </div>
    );
};
