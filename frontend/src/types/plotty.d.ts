declare module 'plotty' {
    export class plot {
        constructor(options: any);
        render(): void;
        setDomain(domain: [number, number]): void;
        setData(data: any, width: number, height: number): void;
    }
}
