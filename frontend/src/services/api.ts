/**
 * API Service for UHI-LST Analysis Backend
 */

import axios, { AxiosError } from 'axios';
import type { AnalysisResult, AnalysisError } from '@/types/api';
import type { BandFiles } from '@/components/analysis/UploadPanel';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with defaults
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 600000, // 10 minutes for large file processing
});

/**
 * Check API health status
 */
export const checkHealth = async (): Promise<{ status: string }> => {
    const response = await api.get('/api/health');
    return response.data;
};

/**
 * Run UHI-LST analysis on uploaded band files
 */
export const analyzeImagery = async (
    bandFiles: BandFiles,
    mlCoefficient: number = 3.342e-4,
    alCoefficient: number = 0.1,
    onProgress?: (progress: number) => void
): Promise<AnalysisResult> => {
    // Validate all required bands are present
    const requiredBands: (keyof BandFiles)[] = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10'];
    const missingBands = requiredBands.filter(band => !bandFiles[band]);

    if (missingBands.length > 0) {
        throw new Error(`Missing required bands: ${missingBands.join(', ')}`);
    }

    // Create FormData with all band files
    const formData = new FormData();
    formData.append('band_2', bandFiles.B2!);
    formData.append('band_3', bandFiles.B3!);
    formData.append('band_4', bandFiles.B4!);
    formData.append('band_5', bandFiles.B5!);
    formData.append('band_6', bandFiles.B6!);
    formData.append('band_7', bandFiles.B7!);
    formData.append('band_10', bandFiles.B10!);

    try {
        const response = await api.post<AnalysisResult>('/api/analyze', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            params: {
                ml_coefficient: mlCoefficient,
                al_coefficient: alCoefficient,
            },
            onUploadProgress: (progressEvent) => {
                if (progressEvent.total && onProgress) {
                    const progress = Math.round((progressEvent.loaded * 50) / progressEvent.total);
                    onProgress(progress); // Upload is 0-50%
                }
            },
        });

        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            const axiosError = error as AxiosError<AnalysisError>;
            if (axiosError.response?.data) {
                const errorData = axiosError.response.data;
                throw new Error(errorData.message || errorData.error || 'Analysis failed');
            }
            throw new Error(axiosError.message || 'Network error occurred');
        }
        throw error;
    }
};

/**
 * Get map legends for visualization
 */
export const getLegend = async () => {
    const response = await api.get('/api/legend');
    return response.data;
};

/**
 * Format file size for display
 */
export const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Calculate total size of band files
 */
export const getTotalFileSize = (bandFiles: BandFiles): number => {
    return Object.values(bandFiles).reduce((total, file) => {
        return total + (file?.size || 0);
    }, 0);
};

export default api;
