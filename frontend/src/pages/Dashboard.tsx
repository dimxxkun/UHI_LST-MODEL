

export const Dashboard = () => {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Dashboard</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="card">
                        <h3 className="text-lg font-medium text-slate-800 dark:text-slate-100 mb-2">Stat {i}</h3>
                        <p className="text-3xl font-bold text-primary-600">1,234</p>
                        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">+12% from last month</p>
                    </div>
                ))}
            </div>

            <div className="card h-96 flex items-center justify-center">
                <p className="text-slate-400">Chart Placeholder</p>
            </div>
        </div>
    );
};
