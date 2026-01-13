/**
 * API Types for UHI-LST Analysis
 */

export interface AnalysisResult {
    job_id: string;
    status: string;
    execution_time_seconds: number;
    step_times: Record<string, number>;

    metadata: {
        width: number;
        height: number;
        crs: string;
        bounds: {
            left: number;
            bottom: number;
            right: number;
            top: number;
        };
    };

    lst: {
        statistics: {
            min: number | null;
            max: number | null;
            mean: number | null;
            std: number | null;
            median: number | null;
            valid_pixels: number;
            total_pixels: number;
            unit: string;
        };
        unit: string;
    };

    ndvi: {
        statistics: {
            min: number | null;
            max: number | null;
            mean: number | null;
            std: number | null;
            valid_pixels: number;
            total_pixels: number;
        };
        classification_percentages: {
            water: number;
            urban_bare_soil: number;
            sparse_vegetation: number;
            dense_vegetation: number;
        };
    };

    land_cover: {
        class_counts: Record<string, number>;
        class_percentages: Record<string, number>;
        total_valid_pixels: number;
        total_pixels: number;
        nodata_pixels: number;
    };

    uhi: {
        uhi_intensity: number | null;
        uhi_category: string;
        uhi_category_value: number;
        urban_mean_temp: number | null;
        rural_mean_temp: number | null;
        hotspot_count: number;
        hotspot_cluster_count: number;
        hotspot_threshold_temp: number | null;
        affected_area_km2: number;
        affected_area_ha: number;
        affected_pixels: number;
        pixel_resolution_m: number;
        unit: string;
    };

    insights: {
        explanation: string;
        recommendations: Recommendation[];
        recommendation_count: number;
        severity: string;
        severity_value: number;
        summary_metrics: Record<string, number | string | null>;
    };

    heatmap: {
        points: HeatmapPoint[];
        point_count: number;
        statistics: {
            count: number;
            min_temp: number;
            max_temp: number;
            mean_temp: number;
            std_temp: number;
            min_lat: number;
            max_lat: number;
            min_lon: number;
            max_lon: number;
        };
        config: {
            max_points: number;
            sample_step: number;
        };
    };
}

export interface HeatmapPoint {
    lat: number;
    lon: number;
    temp: number;
}

export interface Recommendation {
    title: string;
    description: string;
    priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    priority_value: number;
    category: string;
    timeframe: string;
    estimated_impact: string;
}

export interface AnalysisError {
    error: string;
    message: string;
    job_id?: string;
    hint?: string;
}
