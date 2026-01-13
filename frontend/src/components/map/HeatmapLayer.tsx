/**
 * Heatmap Layer Component for Leaflet
 * Renders temperature data as a heatmap overlay
 */

import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Import leaflet.heat
import 'leaflet.heat';

// Extend Leaflet types for heat layer
declare module 'leaflet' {
    function heatLayer(
        latlngs: Array<[number, number, number?]>,
        options?: HeatLayerOptions
    ): HeatLayer;

    interface HeatLayerOptions {
        minOpacity?: number;
        maxZoom?: number;
        max?: number;
        radius?: number;
        blur?: number;
        gradient?: Record<number, string>;
    }

    interface HeatLayer extends L.Layer {
        setLatLngs(latlngs: Array<[number, number, number?]>): this;
        addLatLng(latlng: [number, number, number?]): this;
        setOptions(options: HeatLayerOptions): this;
    }
}

export interface HeatmapPoint {
    lat: number;
    lon: number;
    temp: number;
}

interface HeatmapLayerProps {
    points: HeatmapPoint[];
    minTemp?: number;
    maxTemp?: number;
    radius?: number;
    blur?: number;
    maxZoom?: number;
    opacity?: number;
}

// Temperature-based color gradient (cold to hot)
const TEMP_GRADIENT: Record<number, string> = {
    0.0: '#313695',  // Deep blue (cold)
    0.1: '#4575b4',
    0.2: '#74add1',
    0.3: '#abd9e9',
    0.4: '#e0f3f8',
    0.5: '#ffffbf',  // Yellow (neutral)
    0.6: '#fee090',
    0.7: '#fdae61',
    0.8: '#f46d43',
    0.9: '#d73027',
    1.0: '#a50026',  // Deep red (hot)
};

export const HeatmapLayer: React.FC<HeatmapLayerProps> = ({
    points,
    minTemp,
    maxTemp,
    radius = 25,
    blur = 15,
    maxZoom = 18,
    opacity = 0.6,
}) => {
    const map = useMap();

    useEffect(() => {
        if (!points || points.length === 0) {
            return;
        }

        // Calculate min/max if not provided
        const temps = points.map(p => p.temp);
        const actualMin = minTemp ?? Math.min(...temps);
        const actualMax = maxTemp ?? Math.max(...temps);
        const tempRange = actualMax - actualMin;

        // Normalize temperatures to 0-1 intensity
        const heatData: Array<[number, number, number]> = points.map(point => {
            const intensity = tempRange > 0
                ? (point.temp - actualMin) / tempRange
                : 0.5;
            return [point.lat, point.lon, intensity];
        });

        // Create heat layer
        const heatLayer = L.heatLayer(heatData, {
            radius,
            blur,
            maxZoom,
            minOpacity: opacity,
            max: 1.0,
            gradient: TEMP_GRADIENT,
        });

        heatLayer.addTo(map);

        // Fit bounds to heatmap data
        if (heatData.length > 0) {
            const lats = heatData.map(d => d[0]);
            const lons = heatData.map(d => d[1]);
            const bounds = L.latLngBounds(
                [Math.min(...lats), Math.min(...lons)],
                [Math.max(...lats), Math.max(...lons)]
            );
            map.fitBounds(bounds, { padding: [20, 20] });
        }

        // Cleanup on unmount or when points change
        return () => {
            map.removeLayer(heatLayer);
        };
    }, [points, minTemp, maxTemp, radius, blur, maxZoom, opacity, map]);

    return null; // This component doesn't render anything directly
};

export default HeatmapLayer;
