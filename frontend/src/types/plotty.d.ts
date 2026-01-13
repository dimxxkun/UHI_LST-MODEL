declare module 'plotty' {
    export interface PlotOptions {
        canvas: HTMLCanvasElement | null;
        data: Float32Array | Float64Array | Uint8Array | number[];
        width: number;
        height: number;
        domain: [number, number];
        colorScale?: string;
        clampLow?: boolean;
        clampHigh?: boolean;
        noDataValue?: number;
    }

    export class plot {
        constructor(options: PlotOptions);
        render(): void;
        setDomain(domain: [number, number]): void;
        setData(data: Float32Array | Float64Array | Uint8Array | number[], width: number, height: number): void;
    }
}
