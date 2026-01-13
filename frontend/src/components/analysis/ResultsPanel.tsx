/**
 * Results Panel Component
 * Displays analysis results including LST stats, UHI metrics, and recommendations
 */

import React from 'react';
import {
    Thermometer,
    Flame,
    Leaf,
    Building2,
    Droplets,
    AlertTriangle,
    CheckCircle,
    Info,
    TrendingUp,
    Clock
} from 'lucide-react';
import { clsx } from 'clsx';
import type { AnalysisResult } from '@/types/api';

interface ResultsPanelProps {
    result: AnalysisResult | null;
    isLoading?: boolean;
    error?: string | null;
    className?: string;
}

// Metric Card component
const MetricCard: React.FC<{
    icon: React.ReactNode;
    label: string;
    value: string | number | null | undefined;
    unit?: string;
    color?: 'blue' | 'red' | 'green' | 'orange' | 'purple';
}> = ({ icon, label, value, unit, color = 'blue' }) => {
    const colorClasses = {
        blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
        red: 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400',
        green: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400',
        orange: 'bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400',
        purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400',
    };

    return (
        <div className={clsx('rounded-lg p-3', colorClasses[color])}>
            <div className="flex items-center gap-2 mb-1">
                {icon}
                <span className="text-xs font-medium opacity-80">{label}</span>
            </div>
            <div className="text-lg font-bold">
                {value != null ? value : '--'}{unit && <span className="text-sm font-normal ml-1">{unit}</span>}
            </div>
        </div>
    );
};

// Severity Badge component
const SeverityBadge: React.FC<{ severity: string }> = ({ severity }) => {
    const severityConfig: Record<string, { color: string; icon: React.ReactNode }> = {
        minimal: { color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400', icon: <CheckCircle className="w-4 h-4" /> },
        mild: { color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400', icon: <Info className="w-4 h-4" /> },
        moderate: { color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400', icon: <AlertTriangle className="w-4 h-4" /> },
        severe: { color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400', icon: <Flame className="w-4 h-4" /> },
        critical: { color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400', icon: <Flame className="w-4 h-4" /> },
    };

    const config = severityConfig[severity.toLowerCase()] || severityConfig.mild;

    return (
        <span className={clsx('inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium', config.color)}>
            {config.icon}
            {severity.charAt(0).toUpperCase() + severity.slice(1)}
        </span>
    );
};

// Priority Badge for recommendations
const PriorityBadge: React.FC<{ priority: string }> = ({ priority }) => {
    const priorityColors: Record<string, string> = {
        CRITICAL: 'bg-red-500 text-white',
        HIGH: 'bg-orange-500 text-white',
        MEDIUM: 'bg-yellow-500 text-black',
        LOW: 'bg-blue-500 text-white',
    };

    return (
        <span className={clsx('px-2 py-0.5 rounded text-xs font-bold', priorityColors[priority] || 'bg-gray-500 text-white')}>
            {priority}
        </span>
    );
};

// Land Cover Bar Chart
const LandCoverChart: React.FC<{ percentages: Record<string, number> }> = ({ percentages }) => {
    const colors: Record<string, string> = {
        'Water': 'bg-blue-500',
        'Urban/Built-up': 'bg-red-400',
        'Vegetation': 'bg-green-500',
        'Bare Soil': 'bg-amber-600',
    };

    // Filter out "No Data" and sort by percentage
    const entries = Object.entries(percentages)
        .filter(([name]) => name !== 'No Data')
        .sort((a, b) => b[1] - a[1]);

    return (
        <div className="space-y-2">
            {entries.map(([name, value]) => (
                <div key={name}>
                    <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-600 dark:text-slate-400">{name}</span>
                        <span className="font-medium text-slate-700 dark:text-slate-300">{value.toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                        <div
                            className={clsx('h-full rounded-full transition-all', colors[name] || 'bg-slate-400')}
                            style={{ width: `${value}%` }}
                        />
                    </div>
                </div>
            ))}
        </div>
    );
};

export const ResultsPanel: React.FC<ResultsPanelProps> = ({
    result,
    isLoading,
    error,
    className
}) => {
    // Loading state
    if (isLoading) {
        return (
            <div className={clsx('card p-4 flex flex-col items-center justify-center min-h-[200px]', className)}>
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mb-4"></div>
                <p className="text-slate-600 dark:text-slate-400 font-medium">Processing imagery...</p>
                <p className="text-sm text-slate-500 dark:text-slate-500 mt-1">This may take a few minutes</p>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className={clsx('card p-4', className)}>
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                        <div>
                            <h4 className="font-medium text-red-800 dark:text-red-300">Analysis Failed</h4>
                            <p className="text-sm text-red-600 dark:text-red-400 mt-1">{error}</p>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Empty state
    if (!result) {
        return (
            <div className={clsx('card p-4', className)}>
                <h3 className="font-medium mb-3 text-slate-800 dark:text-slate-100">Results</h3>
                <div className="text-center py-8 text-slate-500 text-sm">
                    <Thermometer className="w-10 h-10 mx-auto mb-3 opacity-30" />
                    Upload band files and run analysis to view results
                </div>
            </div>
        );
    }

    // Results display
    const { lst, uhi, land_cover, insights, ndvi } = result;

    return (
        <div className={clsx('space-y-4 overflow-y-auto', className)}>
            {/* Execution Time */}
            <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                <Clock className="w-3.5 h-3.5" />
                Analysis completed in {result.execution_time_seconds.toFixed(2)}s
            </div>

            {/* UHI Intensity Card */}
            <div className="card p-4">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium text-slate-800 dark:text-slate-100">UHI Intensity</h3>
                    <SeverityBadge severity={insights.severity} />
                </div>
                <div className="text-4xl font-bold text-slate-900 dark:text-white mb-2">
                    {uhi.uhi_intensity !== null ? `${uhi.uhi_intensity.toFixed(1)}°C` : '--'}
                </div>
                <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
                    <div>
                        <span className="text-slate-500 dark:text-slate-400">Urban Mean</span>
                        <div className="font-semibold text-red-600 dark:text-red-400">
                            {uhi.urban_mean_temp?.toFixed(1) ?? '--'}°C
                        </div>
                    </div>
                    <div>
                        <span className="text-slate-500 dark:text-slate-400">Rural Mean</span>
                        <div className="font-semibold text-green-600 dark:text-green-400">
                            {uhi.rural_mean_temp?.toFixed(1) ?? '--'}°C
                        </div>
                    </div>
                </div>
            </div>

            {/* LST Statistics */}
            <div className="card p-4">
                <h3 className="font-medium mb-3 text-slate-800 dark:text-slate-100">Temperature Statistics</h3>
                <div className="grid grid-cols-2 gap-3">
                    <MetricCard
                        icon={<Thermometer className="w-4 h-4" />}
                        label="Maximum"
                        value={lst.statistics.max?.toFixed(1)}
                        unit="°C"
                        color="red"
                    />
                    <MetricCard
                        icon={<Thermometer className="w-4 h-4" />}
                        label="Minimum"
                        value={lst.statistics.min?.toFixed(1)}
                        unit="°C"
                        color="blue"
                    />
                    <MetricCard
                        icon={<TrendingUp className="w-4 h-4" />}
                        label="Mean"
                        value={lst.statistics.mean?.toFixed(1)}
                        unit="°C"
                        color="orange"
                    />
                    <MetricCard
                        icon={<Flame className="w-4 h-4" />}
                        label="Hotspots"
                        value={uhi.hotspot_count.toLocaleString()}
                        color="red"
                    />
                </div>
            </div>

            {/* Land Cover */}
            <div className="card p-4">
                <h3 className="font-medium mb-3 text-slate-800 dark:text-slate-100">Land Cover</h3>
                <LandCoverChart percentages={land_cover.class_percentages} />
            </div>

            {/* NDVI Summary */}
            <div className="card p-4">
                <h3 className="font-medium mb-3 text-slate-800 dark:text-slate-100">Vegetation (NDVI)</h3>
                <div className="grid grid-cols-3 gap-2">
                    <MetricCard
                        icon={<Leaf className="w-4 h-4" />}
                        label="Mean NDVI"
                        value={ndvi.statistics.mean?.toFixed(2)}
                        color="green"
                    />
                    <MetricCard
                        icon={<Building2 className="w-4 h-4" />}
                        label="Urban/Bare"
                        value={ndvi.classification_percentages.urban_bare_soil?.toFixed(0)}
                        unit="%"
                        color="orange"
                    />
                    <MetricCard
                        icon={<Droplets className="w-4 h-4" />}
                        label="Water"
                        value={ndvi.classification_percentages.water?.toFixed(0)}
                        unit="%"
                        color="blue"
                    />
                </div>
            </div>

            {/* Recommendations */}
            <div className="card p-4">
                <h3 className="font-medium mb-3 text-slate-800 dark:text-slate-100">
                    Recommendations ({insights.recommendation_count})
                </h3>
                <div className="space-y-3">
                    {insights.recommendations.slice(0, 5).map((rec, index) => (
                        <div
                            key={index}
                            className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700"
                        >
                            <div className="flex items-start gap-2 mb-2">
                                <span className="text-slate-400 font-medium text-sm">{index + 1}.</span>
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <PriorityBadge priority={rec.priority} />
                                        <span className="text-xs text-slate-500 dark:text-slate-400">{rec.category}</span>
                                    </div>
                                    <h4 className="font-medium text-slate-800 dark:text-slate-200 text-sm">
                                        {rec.title}
                                    </h4>
                                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">
                                        {rec.description}
                                    </p>
                                    <div className="flex gap-3 mt-2 text-xs text-slate-500">
                                        <span>⏱ {rec.timeframe}</span>
                                        <span>📊 Impact: {rec.estimated_impact}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Explanation */}
            <div className="card p-4">
                <h3 className="font-medium mb-3 text-slate-800 dark:text-slate-100">Analysis Summary</h3>
                <div className="prose prose-sm dark:prose-invert max-w-none text-slate-600 dark:text-slate-400">
                    <div
                        className="whitespace-pre-wrap text-sm leading-relaxed"
                        dangerouslySetInnerHTML={{
                            __html: insights.explanation
                                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                .replace(/## (.*?)\n/g, '<h4 class="font-semibold text-slate-800 dark:text-slate-200 mt-4 mb-2">$1</h4>')
                                .replace(/### (.*?)\n/g, '<h5 class="font-medium text-slate-700 dark:text-slate-300 mt-3 mb-1">$1</h5>')
                        }}
                    />
                </div>
            </div>
        </div>
    );
};

export default ResultsPanel;
