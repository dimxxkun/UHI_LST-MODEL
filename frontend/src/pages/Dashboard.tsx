/**
 * Dashboard Page - Displays analysis results with full statistics
 */

import { useNavigate } from 'react-router-dom';
import { useAnalysisStore } from '@/stores/analysisStore';
import {
    Thermometer,
    Flame,
    Building2,
    Leaf,
    Droplets,
    AlertTriangle,
    CheckCircle,
    Info,
    Clock,
    ArrowRight,
    TrendingUp,
    MapPin
} from 'lucide-react';
import { clsx } from 'clsx';

// Stat Card Component
const StatCard: React.FC<{
    icon: React.ReactNode;
    label: string;
    value: string | number;
    unit?: string;
    color?: 'blue' | 'red' | 'green' | 'orange' | 'purple';
    subtext?: string;
}> = ({ icon, label, value, unit, color = 'blue', subtext }) => {
    const colorClasses = {
        blue: 'text-blue-600 dark:text-blue-400 bg-blue-500/10',
        red: 'text-red-600 dark:text-red-400 bg-red-500/10',
        green: 'text-green-600 dark:text-green-400 bg-green-500/10',
        orange: 'text-orange-600 dark:text-orange-400 bg-orange-500/10',
        purple: 'text-purple-600 dark:text-purple-400 bg-purple-500/10',
    };

    return (
        <div className="card p-4 sm:p-6">
            <div className="flex items-center gap-3 mb-3">
                <div className={clsx('p-2.5 rounded-lg', colorClasses[color])}>
                    {icon}
                </div>
                <span className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</span>
            </div>
            <div className="text-3xl sm:text-4xl font-bold text-slate-900 dark:text-white">
                {value}
                {unit && <span className="text-lg sm:text-xl font-normal text-slate-500 ml-1">{unit}</span>}
            </div>
            {subtext && (
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">{subtext}</p>
            )}
        </div>
    );
};

// Severity Badge
const SeverityBadge: React.FC<{ severity: string }> = ({ severity }) => {
    const config: Record<string, { color: string; icon: React.ReactNode }> = {
        minimal: { color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400', icon: <CheckCircle className="w-4 h-4" /> },
        mild: { color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400', icon: <Info className="w-4 h-4" /> },
        moderate: { color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400', icon: <AlertTriangle className="w-4 h-4" /> },
        severe: { color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400', icon: <Flame className="w-4 h-4" /> },
        critical: { color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400', icon: <Flame className="w-4 h-4" /> },
    };

    const { color, icon } = config[severity.toLowerCase()] || config.mild;

    return (
        <span className={clsx('inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium', color)}>
            {icon}
            {severity.charAt(0).toUpperCase() + severity.slice(1)} UHI
        </span>
    );
};

// Land Cover Chart
const LandCoverChart: React.FC<{ percentages: Record<string, number> }> = ({ percentages }) => {
    const colors: Record<string, { bg: string; text: string }> = {
        'Water': { bg: 'bg-blue-500', text: 'text-blue-600' },
        'Urban/Built-up': { bg: 'bg-red-400', text: 'text-red-600' },
        'Vegetation': { bg: 'bg-green-500', text: 'text-green-600' },
        'Bare Soil': { bg: 'bg-amber-600', text: 'text-amber-600' },
    };

    const entries = Object.entries(percentages)
        .filter(([name]) => name !== 'No Data')
        .sort((a, b) => b[1] - a[1]);

    return (
        <div className="space-y-4">
            {entries.map(([name, value]) => (
                <div key={name}>
                    <div className="flex justify-between text-sm mb-2">
                        <span className={clsx('font-medium', colors[name]?.text || 'text-slate-600')}>{name}</span>
                        <span className="font-bold text-slate-700 dark:text-slate-300">{value.toFixed(1)}%</span>
                    </div>
                    <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                        <div
                            className={clsx('h-full rounded-full transition-all duration-500', colors[name]?.bg || 'bg-slate-400')}
                            style={{ width: `${value}%` }}
                        />
                    </div>
                </div>
            ))}
        </div>
    );
};

// Priority Badge
const PriorityBadge: React.FC<{ priority: string }> = ({ priority }) => {
    const colors: Record<string, string> = {
        CRITICAL: 'bg-red-500 text-white',
        HIGH: 'bg-orange-500 text-white',
        MEDIUM: 'bg-yellow-500 text-black',
        LOW: 'bg-blue-500 text-white',
    };

    return (
        <span className={clsx('px-2 py-0.5 rounded text-xs font-bold', colors[priority] || 'bg-gray-500 text-white')}>
            {priority}
        </span>
    );
};

export const Dashboard = () => {
    const navigate = useNavigate();
    const { analysisResult } = useAnalysisStore();

    // Empty state - no analysis yet
    if (!analysisResult) {
        return (
            <div className="space-y-6">
                <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">Dashboard</h1>

                <div className="card p-8 sm:p-12 flex flex-col items-center justify-center text-center">
                    <div className="w-20 h-20 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-6">
                        <Thermometer className="w-10 h-10 text-slate-400" />
                    </div>
                    <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-2">
                        No Analysis Results Yet
                    </h2>
                    <p className="text-slate-500 dark:text-slate-400 mb-6 max-w-md">
                        Upload Landsat band files and run an analysis to see UHI and LST results here.
                    </p>
                    <button
                        onClick={() => navigate('/analysis')}
                        className="btn-primary flex items-center gap-2"
                    >
                        Go to Analysis
                        <ArrowRight className="w-4 h-4" />
                    </button>
                </div>
            </div>
        );
    }

    const { lst, uhi, land_cover, insights, ndvi } = analysisResult;

    return (
        <div className="space-y-6 pb-8">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">Analysis Results</h1>
                    <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mt-1">
                        <Clock className="w-4 h-4" />
                        <span>Completed in {analysisResult.execution_time_seconds.toFixed(2)}s</span>
                    </div>
                </div>
                <SeverityBadge severity={insights.severity} />
            </div>

            {/* Key Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
                <StatCard
                    icon={<Flame className="w-5 h-5" />}
                    label="UHI Intensity"
                    value={uhi.uhi_intensity?.toFixed(1) ?? '--'}
                    unit="°C"
                    color="red"
                    subtext={`Urban-Rural temperature difference`}
                />
                <StatCard
                    icon={<Thermometer className="w-5 h-5" />}
                    label="Mean LST"
                    value={lst.statistics.mean?.toFixed(1) ?? '--'}
                    unit="°C"
                    color="orange"
                    subtext={`Range: ${lst.statistics.min?.toFixed(0)}° - ${lst.statistics.max?.toFixed(0)}°`}
                />
                <StatCard
                    icon={<MapPin className="w-5 h-5" />}
                    label="Hotspots"
                    value={uhi.hotspot_count.toLocaleString()}
                    color="red"
                    subtext={`${uhi.affected_area_km2.toFixed(1)} km² affected`}
                />
                <StatCard
                    icon={<Leaf className="w-5 h-5" />}
                    label="Mean NDVI"
                    value={ndvi.statistics.mean?.toFixed(2) ?? '--'}
                    color="green"
                    subtext="Vegetation health index"
                />
            </div>

            {/* Two Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left Column */}
                <div className="space-y-6">
                    {/* Land Cover */}
                    <div className="card p-4 sm:p-6">
                        <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">
                            Land Cover Distribution
                        </h2>
                        <LandCoverChart percentages={land_cover.class_percentages} />
                    </div>

                    {/* Temperature Summary */}
                    <div className="card p-4 sm:p-6">
                        <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">
                            Temperature Summary
                        </h2>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                                <div className="flex items-center gap-2 text-red-600 dark:text-red-400 mb-1">
                                    <TrendingUp className="w-4 h-4" />
                                    <span className="text-xs font-medium">Urban Mean</span>
                                </div>
                                <div className="text-2xl font-bold text-red-700 dark:text-red-300">
                                    {uhi.urban_mean_temp?.toFixed(1) ?? '--'}°C
                                </div>
                            </div>
                            <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                <div className="flex items-center gap-2 text-green-600 dark:text-green-400 mb-1">
                                    <Leaf className="w-4 h-4" />
                                    <span className="text-xs font-medium">Rural Mean</span>
                                </div>
                                <div className="text-2xl font-bold text-green-700 dark:text-green-300">
                                    {uhi.rural_mean_temp?.toFixed(1) ?? '--'}°C
                                </div>
                            </div>
                        </div>

                        {/* Vegetation Stats */}
                        <div className="grid grid-cols-3 gap-3 mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                            <div className="text-center">
                                <div className="flex items-center justify-center gap-1 text-blue-600 dark:text-blue-400 mb-1">
                                    <Droplets className="w-4 h-4" />
                                </div>
                                <div className="text-lg font-bold text-slate-700 dark:text-slate-300">
                                    {ndvi.classification_percentages.water?.toFixed(0) ?? 0}%
                                </div>
                                <div className="text-xs text-slate-500">Water</div>
                            </div>
                            <div className="text-center">
                                <div className="flex items-center justify-center gap-1 text-orange-600 dark:text-orange-400 mb-1">
                                    <Building2 className="w-4 h-4" />
                                </div>
                                <div className="text-lg font-bold text-slate-700 dark:text-slate-300">
                                    {ndvi.classification_percentages.urban_bare_soil?.toFixed(0) ?? 0}%
                                </div>
                                <div className="text-xs text-slate-500">Urban/Bare</div>
                            </div>
                            <div className="text-center">
                                <div className="flex items-center justify-center gap-1 text-green-600 dark:text-green-400 mb-1">
                                    <Leaf className="w-4 h-4" />
                                </div>
                                <div className="text-lg font-bold text-slate-700 dark:text-slate-300">
                                    {ndvi.classification_percentages.dense_vegetation?.toFixed(0) ?? 0}%
                                </div>
                                <div className="text-xs text-slate-500">Dense Veg.</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Column - Recommendations */}
                <div className="card p-4 sm:p-6">
                    <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">
                        Recommendations ({insights.recommendation_count})
                    </h2>
                    <div className="space-y-4 max-h-[500px] overflow-y-auto scrollbar-hidden">
                        {insights.recommendations.map((rec, index) => (
                            <div
                                key={index}
                                className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700"
                            >
                                <div className="flex items-start gap-3">
                                    <span className="text-2xl font-bold text-slate-300 dark:text-slate-600">
                                        {index + 1}
                                    </span>
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2">
                                            <PriorityBadge priority={rec.priority} />
                                            <span className="text-xs text-slate-500">{rec.category}</span>
                                        </div>
                                        <h4 className="font-medium text-slate-800 dark:text-slate-200 mb-1">
                                            {rec.title}
                                        </h4>
                                        <p className="text-sm text-slate-600 dark:text-slate-400">
                                            {rec.description}
                                        </p>
                                        <div className="flex gap-4 mt-3 text-xs text-slate-500">
                                            <span>⏱ {rec.timeframe}</span>
                                            <span>📊 Impact: {rec.estimated_impact}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Analysis Explanation */}
            <div className="card p-4 sm:p-6">
                <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">
                    Analysis Summary
                </h2>
                <div
                    className="prose prose-sm dark:prose-invert max-w-none text-slate-600 dark:text-slate-400"
                    dangerouslySetInnerHTML={{
                        __html: insights.explanation
                            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                            .replace(/## (.*?)\n/g, '<h4 class="font-semibold text-slate-800 dark:text-slate-200 mt-4 mb-2">$1</h4>')
                            .replace(/### (.*?)\n/g, '<h5 class="font-medium text-slate-700 dark:text-slate-300 mt-3 mb-1">$1</h5>')
                    }}
                />
            </div>
        </div>
    );
};
