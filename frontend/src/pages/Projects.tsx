import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalysisStore } from '@/stores/analysisStore';
import {
    Folder,
    Calendar,
    Thermometer,
    Zap,
    Trash2,
    ExternalLink,
    Search,
    Clock,
    Layers
} from 'lucide-react';

export const ProjectsPage = () => {
    const navigate = useNavigate();
    const { projects, deleteProject, loadProject, renameProject } = useAnalysisStore();
    const [searchTerm, setSearchTerm] = useState('');
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editName, setEditName] = useState('');

    const filteredProjects = projects.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.description?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleOpenProject = (id: string) => {
        loadProject(id);
        navigate('/'); // Navigate to Dashboard
    };

    const handleStartRename = (id: string, currentName: string) => {
        setEditingId(id);
        setEditName(currentName);
    };

    const handleSaveRename = (id: string) => {
        if (editName.trim()) {
            renameProject(id, editName.trim());
        }
        setEditingId(null);
    };

    const formatDate = (timestamp: number) => {
        return new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(timestamp));
    };

    return (
        <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-900">
            {/* Header */}
            <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-6 py-4 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <Folder className="w-5 h-5 text-indigo-500" />
                            Analysis History
                        </h1>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                            Manage and review your saved Land Surface Temperature analyses.
                        </p>
                    </div>

                    <div className="relative max-w-xs w-full">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Search projects..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-slate-100 dark:bg-slate-700 border-transparent focus:bg-white dark:focus:bg-slate-600 focus:ring-2 focus:ring-indigo-500 rounded-lg text-sm transition-all"
                        />
                    </div>
                </div>
            </header>

            {/* Content Area */}
            <main className="flex-1 overflow-y-auto p-6">
                {projects.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center opacity-70">
                        <div className="w-16 h-16 bg-slate-200 dark:bg-slate-800 rounded-full flex items-center justify-center mb-4">
                            <Folder className="w-8 h-8 text-slate-400" />
                        </div>
                        <h3 className="text-lg font-medium text-slate-900 dark:text-white">No saved projects</h3>
                        <p className="text-sm text-slate-500 max-w-xs mt-2">
                            Run a new analysis in the workspace and save your results to see them here.
                        </p>
                        <button
                            onClick={() => navigate('/analysis')}
                            className="mt-6 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors"
                        >
                            Go to Analysis Workspace
                        </button>
                    </div>
                ) : filteredProjects.length === 0 ? (
                    <div className="py-12 text-center opacity-50">
                        <p className="text-slate-500">No projects match your search.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filteredProjects.map((project) => (
                            <div
                                key={project.id}
                                className="group relative bg-white dark:bg-slate-800 rounded-xl shadow-sm hover:shadow-md border border-slate-200 dark:border-slate-700 transition-all overflow-hidden"
                            >
                                {/* Card Header */}
                                <div className="p-5 border-b border-slate-50 dark:border-slate-700/50">
                                    <div className="flex justify-between items-start mb-2">
                                        {editingId === project.id ? (
                                            <input
                                                autoFocus
                                                value={editName}
                                                onChange={(e) => setEditName(e.target.value)}
                                                onBlur={() => handleSaveRename(project.id)}
                                                onKeyDown={(e) => e.key === 'Enter' && handleSaveRename(project.id)}
                                                className="bg-slate-100 dark:bg-slate-700 border-indigo-500 rounded px-2 py-0.5 text-sm font-bold w-full"
                                            />
                                        ) : (
                                            <h3
                                                className="font-bold text-slate-900 dark:text-white truncate pr-6 cursor-pointer hover:text-indigo-600 dark:hover:text-indigo-400"
                                                onClick={() => handleStartRename(project.id, project.name)}
                                                title="Click to rename"
                                            >
                                                {project.name}
                                            </h3>
                                        )}
                                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button
                                                onClick={() => handleOpenProject(project.id)}
                                                className="p-1.5 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-md"
                                                title="Open in Dashboard"
                                            >
                                                <ExternalLink className="w-4 h-4" />
                                            </button>
                                            <button
                                                onClick={() => deleteProject(project.id)}
                                                className="p-1.5 hover:bg-red-50 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400 rounded-md"
                                                title="Delete Project"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400">
                                        <Calendar className="w-3 h-3" />
                                        {formatDate(project.timestamp)}
                                    </div>
                                </div>

                                {/* Card Body: Key Stats */}
                                <div className="p-5 bg-slate-50/50 dark:bg-slate-900/20">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="flex flex-col">
                                            <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400 dark:text-slate-500 mb-1">Mean Temp</span>
                                            <div className="flex items-center gap-1.5">
                                                <div className="w-7 h-7 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center">
                                                    <Thermometer className="w-3.5 h-3.5 text-orange-600 dark:text-orange-400" />
                                                </div>
                                                <span className="text-sm font-bold text-slate-700 dark:text-slate-300">
                                                    {project.result.lst.statistics.mean?.toFixed(1) || '--'}°C
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex flex-col">
                                            <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400 dark:text-slate-500 mb-1">UHI Intensity</span>
                                            <div className="flex items-center gap-1.5">
                                                <div className="w-7 h-7 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
                                                    <Zap className="w-3.5 h-3.5 text-red-600 dark:text-red-400" />
                                                </div>
                                                <span className="text-sm font-bold text-slate-700 dark:text-slate-300">
                                                    +{project.result.uhi.uhi_intensity?.toFixed(2) || '0'}°C
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Quick Metadata Footer */}
                                <div className="px-5 py-3 bg-white dark:bg-slate-800 border-t border-slate-50 dark:border-slate-700/50 flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="flex items-center gap-1 text-[10px] text-slate-500">
                                            <Layers className="w-3 h-3" />
                                            {project.result.metadata.crs.split(':').pop()}
                                        </div>
                                        <div className="flex items-center gap-1 text-[10px] text-slate-500">
                                            <Clock className="w-3 h-3" />
                                            {project.result.execution_time_seconds.toFixed(1)}s
                                        </div>
                                    </div>

                                    <div className={`text-[10px] font-bold uppercase py-0.5 px-2 rounded-full ${project.result.uhi.uhi_category_value >= 3
                                        ? 'bg-red-100 text-red-700'
                                        : 'bg-green-100 text-green-700'
                                        }`}>
                                        {project.result.uhi.uhi_category}
                                    </div>
                                </div>

                                {/* Hover Action Overlay (Mobile-friendly) */}
                                <button
                                    onClick={() => handleOpenProject(project.id)}
                                    className="absolute inset-0 z-0 sm:hidden"
                                />
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
};
