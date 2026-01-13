/**
 * Analysis Store - Zustand state management for sharing analysis results
 */

import { create } from 'zustand';
import type { AnalysisResult } from '@/types/api';

interface AnalysisState {
    // Analysis data
    analysisResult: AnalysisResult | null;
    isLoading: boolean;
    error: string | null;

    // Actions
    setAnalysisResult: (result: AnalysisResult | null) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
    clearResults: () => void;
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
    // Initial state
    analysisResult: null,
    isLoading: false,
    error: null,

    // Actions
    setAnalysisResult: (result) => set({ analysisResult: result, error: null }),
    setLoading: (loading) => set({ isLoading: loading }),
    setError: (error) => set({ error, isLoading: false }),
    clearResults: () => set({ analysisResult: null, error: null, isLoading: false }),
}));
