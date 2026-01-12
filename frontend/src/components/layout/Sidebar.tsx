import React from 'react';
import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    Map as MapIcon,
    FolderOpen,
    Settings,
    X
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface SidebarProps {
    isOpen: boolean;
    toggleSidebar: () => void;
}

const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
    { icon: FolderOpen, label: 'Projects', path: '/projects' },
    { icon: MapIcon, label: 'Analysis', path: '/analysis' },
    { icon: Settings, label: 'Settings', path: '/settings' },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, toggleSidebar }) => {
    return (
        <>
            {/* Mobile Overlay */}
            <div
                className={clsx(
                    "fixed inset-0 bg-black/50 z-20 transition-opacity lg:hidden",
                    isOpen ? "opacity-100" : "opacity-0 pointer-events-none"
                )}
                onClick={toggleSidebar}
            />

            {/* Sidebar Container */}
            <aside
                className={clsx(
                    "fixed top-0 left-0 bottom-0 z-30 w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static",
                    isOpen ? "translate-x-0" : "-translate-x-full"
                )}
            >
                <div className="flex flex-col h-full">
                    {/* Logo Area */}
                    <div className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800">
                        <MapIcon className="w-8 h-8 text-primary-600 mr-3" />
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-primary-400">
                            UHI-LST
                        </span>
                        <button
                            onClick={toggleSidebar}
                            className="ml-auto lg:hidden text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    </div>

                    {/* Navigation Links */}
                    <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                className={({ isActive }) => twMerge(
                                    "flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                                    isActive
                                        ? "bg-primary-50 text-primary-700 dark:bg-primary-900/10 dark:text-primary-400"
                                        : "text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                                )}
                                onClick={() => window.innerWidth < 1024 && toggleSidebar()}
                            >
                                <item.icon className="w-5 h-5 mr-3 shrink-0" />
                                {item.label}
                            </NavLink>
                        ))}
                    </nav>

                    {/* User Profile / Footer */}
                    <div className="p-4 border-t border-slate-200 dark:border-slate-800">
                        <div className="flex items-center">
                            <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold">
                                U
                            </div>
                            <div className="ml-3">
                                <p className="text-sm font-medium text-slate-700 dark:text-slate-200">User</p>
                                <p className="text-xs text-slate-500 dark:text-slate-400">Analyst</p>
                            </div>
                        </div>
                    </div>
                </div>
            </aside>
        </>
    );
};
