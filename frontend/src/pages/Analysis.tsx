import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadPanel } from '@/components/analysis/UploadPanel';
import type { BandFiles } from '@/components/analysis/UploadPanel';
import { MapViewer } from '@/components/map/MapViewer';
import { TiffLayer } from '@/components/map/TiffLayer';
import { HeatmapLayer } from '@/components/map/HeatmapLayer';
import { CompositeTiffLayer } from '@/components/map/CompositeTiffLayer';
import { analyzeImagery } from '@/services/api';
import { useAnalysisStore } from '@/stores/analysisStore';
import { CheckCircle, ArrowRight, Clock, Eye, Thermometer } from 'lucide-react';

export const AnalysisPage = () => {
    const navigate = useNavigate();
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [bandFiles, setBandFiles] = useState<BandFiles>({
        B10: null, B7: null, B6: null, B5: null, B4: null, B3: null, B2: null
    });

    // Use global store for analysis state
    const { analysisResult, isLoading, error, setAnalysisResult, setLoading, setError } = useAnalysisStore();
    const [uploadProgress, setUploadProgress] = useState(0);
    const [mapViewMode, setMapViewMode] = useState<'thermal' | 'truecolor'>('thermal');
    const [opacity, setOpacity] = useState(0.8);

    const handleFileSelect = (file: File) => {
        setSelectedFile(file);
    };

    const handleBandFilesSelect = (bands: BandFiles) => {
        setBandFiles(bands);
        if (Object.values(bands).some(file => file !== null)) {
            setSelectedFile(null);
        }
    };

    const handleRunAnalysis = async () => {
        setLoading(true);
        setError(null);
        setUploadProgress(0);
        setAnalysisResult(null);

        try {
            const missingBands = Object.entries(bandFiles)
                .filter(([, file]) => !file)
                .map(([key]) => key);

            if (missingBands.length > 0) {
                throw new Error(`Please upload all required bands. Missing: ${missingBands.join(', ')}`);
            }

            const result = await analyzeImagery(
                bandFiles,
                undefined,
                undefined,
                (progress) => setUploadProgress(progress)
            );

            setAnalysisResult(result);
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred during analysis';
            console.error('Analysis failed:', err);
            setError(errorMessage);
        } finally {
            setLoading(false);
            setUploadProgress(0);
        }
    };

    const previewFile = selectedFile || bandFiles.B10;
    const isReady = Object.values(bandFiles).every(file => file !== null);

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] sm:h-[calc(100vh-7rem)] gap-4">
            {/* Header */}
            <div className="flex-none flex items-center justify-between">
                <div>
                    <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white mb-1 sm:mb-2">Analysis Workspace</h1>
                    <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400">Upload Landsat imagery to generate LST and UHI maps.</p>
                </div>
                {/* View Dashboard button when analysis is complete */}
                {analysisResult && (
                    <button
                        onClick={() => navigate('/')}
                        className="btn-primary flex items-center gap-2 text-sm"
                    >
                        View Results on Dashboard
                        <ArrowRight className="w-4 h-4" />
                    </button>
                )}
            </div>

            {/* Main content */}
            <div className="flex-1 flex flex-col lg:flex-row gap-4 min-h-0 overflow-hidden">
                {/* Left Panel: Upload & Config */}
                <div className="w-full lg:w-80 flex-none flex flex-col gap-4">
                    <UploadPanel
                        onFileSelect={handleFileSelect}
                        onBandFilesSelect={handleBandFilesSelect}
                        selectedFile={selectedFile}
                    />

                    {/* Run Analysis Button */}
                    <button
                        onClick={handleRunAnalysis}
                        disabled={!isReady || isLoading}
                        className={`btn-primary w-full text-sm sm:text-base py-3 flex items-center justify-center gap-2 ${(!isReady || isLoading) ? 'opacity-70 cursor-not-allowed' : ''}`}
                    >
                        {isLoading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                <span>{uploadProgress > 0 && uploadProgress < 50 ? `Uploading ${uploadProgress}%` : 'Analyzing...'}</span>
                            </>
                        ) : (
                            'Run Analysis'
                        )}
                    </button>

                    {/* Processing Status - Shows while loading */}
                    {isLoading && (
                        <div className="card p-4 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 animate-pulse">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 border-3 border-blue-300 border-t-blue-600 rounded-full animate-spin"></div>
                                <div>
                                    <p className="font-medium text-blue-800 dark:text-blue-300">Analysis in Progress</p>
                                    <p className="text-sm text-blue-600 dark:text-blue-400">
                                        {uploadProgress > 0 && uploadProgress < 50
                                            ? 'Uploading band files...'
                                            : 'Processing imagery - this may take a few minutes...'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Compact Results Summary */}
                    {analysisResult && (
                        <div className="card p-3 sm:p-4 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                            <div className="flex items-center gap-2 text-green-700 dark:text-green-400 mb-2">
                                <CheckCircle className="w-5 h-5" />
                                <span className="font-medium">Analysis Complete</span>
                            </div>
                            <div className="text-sm text-green-600 dark:text-green-400 space-y-1">
                                <div className="flex items-center gap-1">
                                    <Clock className="w-3.5 h-3.5" />
                                    <span>Completed in {analysisResult.execution_time_seconds.toFixed(1)}s</span>
                                </div>
                                <p className="text-xs mt-2 text-slate-600 dark:text-slate-400">
                                    View detailed results on the Dashboard
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Error Display */}
                    {error && (
                        <div className="card p-3 sm:p-4 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
                            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                        </div>
                    )}
                </div>

                {/* Right Panel: Map */}
                <div className="flex-1 card p-0 overflow-hidden relative border-0 shadow-md min-h-[300px] sm:min-h-[400px] lg:min-h-0">
                    {/* Map Controls (Toggle + Opacity) */}
                    <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-3 items-end">
                        {/* View Mode Toggle */}
                        <div className="flex bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
                            <button
                                onClick={() => {
                                    setMapViewMode('thermal');
                                    setOpacity(0.8);
                                }}
                                className={`px-3 py-2 flex items-center gap-2 text-xs font-medium transition-colors ${mapViewMode === 'thermal'
                                        ? 'bg-indigo-600 text-white'
                                        : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
                                    }`}
                            >
                                <Thermometer className="w-3.5 h-3.5" />
                                Thermal
                            </button>
                            <button
                                onClick={() => {
                                    setMapViewMode('truecolor');
                                    setOpacity(1.0);
                                }}
                                disabled={!bandFiles.B4 || !bandFiles.B3 || !bandFiles.B2}
                                title={(!bandFiles.B4 || !bandFiles.B3 || !bandFiles.B2) ? "Upload Bands 4, 3, and 2 to enable True Color" : ""}
                                className={`px-3 py-2 flex items-center gap-2 text-xs font-medium transition-colors ${mapViewMode === 'truecolor'
                                        ? 'bg-indigo-600 text-white'
                                        : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed'
                                    }`}
                            >
                                <Eye className="w-3.5 h-3.5" />
                                True Color
                            </button>
                        </div>

                        {/* Opacity Slider */}
                        {(previewFile || (bandFiles.B4 && bandFiles.B3 && bandFiles.B2)) && (
                            <div className="bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm p-3 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 w-48">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-[10px] uppercase tracking-wider font-bold text-slate-500 dark:text-slate-400">Opacity</span>
                                    <span className="text-[10px] font-mono text-indigo-600 dark:text-indigo-400">{Math.round(opacity * 100)}%</span>
                                </div>
                                <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.01"
                                    value={opacity}
                                    onChange={(e) => setOpacity(parseFloat(e.target.value))}
                                    className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                                />
                            </div>
                        )}
                    </div>

                    <MapViewer>
                        {mapViewMode === 'thermal' ? (
                            previewFile && <TiffLayer file={previewFile} opacity={opacity} />
                        ) : (
                            bandFiles.B4 && bandFiles.B3 && bandFiles.B2 && (
                                <CompositeTiffLayer
                                    redBand={bandFiles.B4}
                                    greenBand={bandFiles.B3}
                                    blueBand={bandFiles.B2}
                                    opacity={opacity}
                                />
                            )
                        )}

                        {analysisResult?.heatmap && (
                            <HeatmapLayer points={analysisResult.heatmap.points} />
                        )}
                    </MapViewer>
                </div>
            </div>
        </div>
    );
};
