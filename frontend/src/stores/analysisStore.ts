import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { AnalysisResult, Project } from '@/types/api';

interface AnalysisState {
    // Analysis data
    analysisResult: AnalysisResult | null;
    isLoading: boolean;
    error: string | null;

    // Project History
    projects: Project[];

    // Notifications
    notification: { message: string, type: 'success' | 'error' | 'info' } | null;

    // Actions
    setAnalysisResult: (result: AnalysisResult | null) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
    clearResults: () => void;

    // Project Management
    saveCurrentAnalysis: (name: string, description?: string) => void;
    deleteProject: (id: string) => void;
    loadProject: (id: string) => void;
    renameProject: (id: string, newName: string) => void;

    // Notification Actions
    showNotification: (message: string, type?: 'success' | 'error' | 'info') => void;
    hideNotification: () => void;
}

export const useAnalysisStore = create<AnalysisState>()(
    persist(
        (set, get) => ({
            // Initial state
            analysisResult: null,
            isLoading: false,
            error: null,
            projects: [],
            notification: null,

            // Actions
            setAnalysisResult: (result) => set({ analysisResult: result, error: null }),
            setLoading: (loading) => set({ isLoading: loading }),
            setError: (error) => set({ error, isLoading: false }),
            clearResults: () => set({ analysisResult: null, error: null, isLoading: false }),

            // Project Management
            saveCurrentAnalysis: (name, description) => {
                const { analysisResult, projects } = get();
                if (!analysisResult) return;

                const newProject: Project = {
                    id: crypto.randomUUID(),
                    name,
                    description,
                    timestamp: Date.now(),
                    result: analysisResult
                };

                set({ projects: [newProject, ...projects] });
                get().showNotification(`Project saved: ${name}`, 'success');
            },

            deleteProject: (id) => {
                const { projects, showNotification } = get();
                const project = projects.find(p => p.id === id);
                set({ projects: projects.filter(p => p.id !== id) });
                showNotification(`Deleted project: ${project?.name || 'Unknown'}`, 'info');
            },

            loadProject: (id) => {
                const { projects, showNotification } = get();
                const project = projects.find(p => p.id === id);
                if (project) {
                    set({ analysisResult: project.result });
                    showNotification(`Loaded project: ${project.name}`, 'info');
                }
            },

            renameProject: (id, newName) => {
                const { projects, showNotification } = get();
                const updatedProjects = projects.map(p =>
                    p.id === id ? { ...p, name: newName } : p
                );
                set({ projects: updatedProjects });
                showNotification('Project renamed successfully!', 'success');
            },

            // Notification Management
            showNotification: (message, type = 'success') => {
                set({ notification: { message, type } });
                // Auto-hide after 3 seconds
                setTimeout(() => {
                    get().hideNotification();
                }, 3000);
            },

            hideNotification: () => set({ notification: null }),
        }),
        {
            name: 'uhi-analysis-storage', // name of the item in the storage (must be unique)
            storage: createJSONStorage(() => localStorage),
            partialize: (state) => ({ projects: state.projects }), // Only persist the projects list
        }
    )
);
