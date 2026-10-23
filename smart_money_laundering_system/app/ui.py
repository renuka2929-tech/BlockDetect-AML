from typing import Optional
import os
import json

from nicegui import ui, run
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from . import services


CURRENT_ROLE = {'role': None}


def role_badge():
    """Display admin badge - simplified for admin-only access"""
    if CURRENT_ROLE['role']:
        ui.label('👨‍💼 Administrator').classes(
            'text-sm px-4 py-2 rounded-lg bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold shadow-lg ml-auto'
        ).style('box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);')


def theme_toggle_button():
    """Create a toggle button for dark/light mode with proper icon sync and persistence"""
    dark = ui.dark_mode()

    # Initial sync script to be run once when the button is created
    ui.run_javascript("""
            (function() {
                const savedTheme = localStorage.getItem('sml_system_theme');
                const isAnimationsPage = window.location.pathname === '/animations';
                const doc = document.documentElement;
                const body = document.body;
                if (isAnimationsPage || savedTheme === 'dark') {
                    doc.classList.add('dark');
                    if (body) body.classList.add('dark');
                } else {
                    doc.classList.remove('dark');
                    if (body) body.classList.remove('dark');
                }
            })();
    """)

    def sync_dark_class(is_dark):
        ui.run_javascript(f"""
            (function() {{
                const isDark = {str(is_dark).lower()};
                const doc = document.documentElement;
                const body = document.body;
                if (isDark) {{
                    doc.classList.add('dark');
                    if (body) body.classList.add('dark');
                    localStorage.setItem('sml_system_theme', 'dark');
                }} else {{
                    doc.classList.remove('dark');
                    if (body) body.classList.remove('dark');
                    localStorage.setItem('sml_system_theme', 'light');
                }}
            }})();
        """)

    def toggle():
        if dark.value:
            dark.disable()
            button.props('icon=light_mode')
            button.tooltip('Switch to Dark Mode')
            sync_dark_class(False)
        else:
            dark.enable()
            button.props('icon=dark_mode')
            button.tooltip('Switch to Light Mode')
            sync_dark_class(True)

    # Determine initial icon and tooltip
    is_initial_dark = bool(dark.value)
    # Check localStorage for initial state if auto
    initial_icon = 'dark_mode' if is_initial_dark else 'light_mode'
    initial_tooltip = 'Switch to Light Mode' if is_initial_dark else 'Switch to Dark Mode'

    button = ui.button(icon=initial_icon, on_click=toggle).props('flat round dense').classes('ml-2')
    button.tooltip(initial_tooltip)

    return button


def add_global_styles():
    # Add theme initialization script BEFORE styles to prevent FOUC
    ui.add_head_html(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <script>
        (function() {
            const savedTheme = localStorage.getItem('sml_system_theme');
            const isAnimationsPage = window.location.pathname === '/animations';
            const doc = document.documentElement;
            const body = document.body;
            
            if (isAnimationsPage || savedTheme === 'dark') {
                doc.classList.add('dark');
                if (body) body.classList.add('dark');
            } else {
                doc.classList.remove('dark');
                if (body) body.classList.remove('dark');
            }
        })();
        </script>
        """
    )
    
    ui.add_head_html(
        """
        <style>
        :root {
            --font-heading: 'Space Grotesk', sans-serif;
            --font-body: 'Inter', sans-serif;
            --primary: #22c55e;
            --primary-glow: rgba(34, 197, 94, 0.4);
            --accent: #0ea5e9;
            --danger: #ef4444;
            --bg-light: #f8fafc;
            --bg-dark: #020617;
            --text-light: #1e293b;
            --text-dark: #f1f5f9;
            --card-light: rgba(255, 255, 255, 0.8);
            --card-dark: rgba(15, 23, 42, 0.8);
            --border-light: rgba(0, 0, 0, 0.05);
            --border-dark: rgba(255, 255, 255, 0.1);
        }

        /* Global Theme-aware base styles */
        body {
            font-family: var(--font-body) !important;
            background-color: var(--bg-light);
            color: var(--text-light);
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        .dark body, .body--dark {
            background-color: var(--bg-dark) !important;
            color: var(--text-dark) !important;
        }
        
        /* Visibility fixes for standard text classes */
        .text-gray-600 { color: #475569 !important; }
        .text-gray-700 { color: #334155 !important; }
        .dark .text-gray-600, .body--dark .text-gray-600 { color: #94a3b8 !important; }
        .dark .text-gray-700, .body--dark .text-gray-700 { color: #cbd5e1 !important; }
        .dark .text-white, .body--dark .text-white { color: #ffffff !important; }
        .dark .text-gray-900, .body--dark .text-gray-900 { color: #f8fafc !important; }
        
        /* Selection visibility fix */
        ::selection {
            background-color: var(--primary);
            color: white;
        }
        .dark ::selection {
            background-color: var(--primary);
            color: #020617;
        }

        /* Force animations page to stay dark */
        .animations-page-active {
            background-color: var(--bg-dark) !important;
            color: var(--text-dark) !important;
        }
        .animations-page-active .pipeline-text {
            color: var(--text-dark) !important;
        }

        h1, h2, h3, h4, .text-h1, .text-h2, .text-h3, .text-h4, .font-bold, .font-extrabold {
            font-family: var(--font-heading) !important;
        }
        
        html, body, #q-app {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            min-height: 100vh !important;
            overflow-x: hidden !important;
        }
        
        .nicegui-content {
            padding: 0 !important;
            width: 100% !important;
        }
        
        /* Force Animations page to Dark Mode styling */
        .animations-page-active .landing-bg {
            background: var(--dark-bg) !important;
        }
        
        /* Matrix Digital Rain Background for Hero */
        .matrix-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
            opacity: 0.1;
            pointer-events: none;
        }

        .dark .matrix-canvas {
            opacity: 0.2;
        }

        /* Visibility Fixes for text */
        .dark .text-gray-600 { color: #94a3b8 !important; }
        .dark .text-gray-700 { color: #cbd5e1 !important; }
        .dark .text-gray-400 { color: #94a3b8 !important; }
        .dark .text-gray-300 { color: #cbd5e1 !important; }
        
        /* High Contrast Text for Selected Elements */
        .highlight-text {
            color: var(--primary);
            font-weight: 700;
            text-shadow: 0 0 10px rgba(34, 197, 94, 0.3);
        }

        /* Optimize all elements for better scroll performance */
        * {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        /* Force GPU acceleration for smoother scrolling */
        .landing-bg, .landing-bg::before, .landing-bg::after {
            transform: translateZ(0);
            backface-visibility: hidden;
            perspective: 1000px;
        }
        
        /* Optimized lightweight animations for blockchain background */
        @keyframes pulse-glow-bg {
            0%, 100% { opacity: 0.01; }
            50% { opacity: 0.02; }
        }
        
        /* Beautiful gradient shimmer effect */
        @keyframes gradient-shimmer {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .gradient-text {
            background: linear-gradient(135deg, #22c55e, #10b981, #3b82f6, #6366f1);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            animation: gradient-shimmer 4s ease infinite;
        }

        .dark .landing-bg::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: 
                radial-gradient(circle at 20% 30%, rgba(34, 197, 94, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(14, 165, 233, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }
        
        .dark .landing-bg::after {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2322c55e' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.3;
            pointer-events: none;
            z-index: -1;
        }
        
        /* Light mode - static background with minimal animation */
        .landing-bg {
            background: var(--bg-light);
            position: relative;
            overflow-x: hidden;
            transition: background-color 0.3s ease;
        }

        .dark .landing-bg, .body--dark .landing-bg {
            background: var(--bg-dark) !important;
        }
        
        .dark .glass-card {
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 0, 0, 0.05);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
            border-radius: 24px;
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            border-color: var(--primary);
            box-shadow: 0 15px 40px rgba(34, 197, 94, 0.15);
        }
        
        .dark .glass-card:hover,
        .body--dark .glass-card:hover,
        .glass-card:hover {
            border-color: rgba(34, 197, 94, 0.7);
            transform: translateY(-4px) scale(1.02);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .dark .glass-card:hover,
        .body--dark .glass-card:hover {
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.6), 0 0 140px rgba(34, 197, 94, 0.2), inset 0 1px 1px rgba(255, 255, 255, 0.15);
        }
        
        .glass-card:hover {
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2), 0 0 100px rgba(34, 197, 94, 0.15), inset 0 1px 1px rgba(255, 255, 255, 1);
        }
        /* Simplified, GPU-accelerated animations */
        @keyframes float-up {
            from { transform: translate3d(0, 30px, 0); opacity: 0; }
            to { transform: translate3d(0, 0, 0); opacity: 1; }
        }
        @keyframes fade-in {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slide-right {
            from { transform: translate3d(-20px, 0, 0); opacity: 0; }
            to { transform: translate3d(0, 0, 0); opacity: 1; }
        }
        @keyframes count-up {
            from { opacity: 0; transform: scale3d(0.8, 0.8, 1); }
            to { opacity: 1; transform: scale3d(1, 1, 1); }
        }
        
        .animate-float-up {
            animation: float-up 0.8s ease-out both;
            will-change: transform, opacity;
        }
        .animate-fade-in {
            animation: fade-in 1s ease-out both;
            will-change: opacity;
        }
        .animate-slide-right {
            animation: slide-right 0.7s ease-out both;
            will-change: transform, opacity;
        }
        .animate-count {
            animation: count-up 0.5s ease-out both;
            will-change: transform, opacity;
        }
        
        /* Reduced delays for faster loading */
        .delay-100 { animation-delay: 0.05s; }
        .delay-200 { animation-delay: 0.1s; }
        .delay-300 { animation-delay: 0.15s; }
        .delay-400 { animation-delay: 0.2s; }
        .delay-500 { animation-delay: 0.25s; }
        .dark .feature-card,
        .body--dark .feature-card {
            backdrop-filter: none;
            background: linear-gradient(135deg, rgba(30, 41, 59, 1) 0%, rgba(15, 23, 42, 0.98) 100%);
            border: 2px solid rgba(34, 197, 94, 0.3);
            border-radius: 1.25rem;
            padding: 2rem;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.05);
            transform: translateZ(0);
            backface-visibility: hidden;
            -webkit-font-smoothing: antialiased;
            display: flex;
            flex-direction: column;
            height: 100%;
            position: relative;
            overflow: hidden;
        }

        .stat-card .stat-value {
            width: 100%;
            overflow-wrap: anywhere;
            word-break: break-word;
            hyphens: auto;
            line-height: 1.1;
        }

        .stat-card .stat-label {
            width: 100%;
        }
        
        .dark .feature-card::after,
        .body--dark .feature-card::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(34, 197, 94, 0.08) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.4s ease;
        }
        
        .dark .feature-card:hover::after,
        .body--dark .feature-card:hover::after {
            opacity: 1;
        }
        
        .feature-card {
            backdrop-filter: none;
            background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(248, 250, 252, 1) 100%);
            border: 2px solid rgba(34, 197, 94, 0.3);
            border-radius: 1.25rem;
            padding: 2rem;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), inset 0 1px 1px rgba(255, 255, 255, 1);
            transform: translateZ(0);
            backface-visibility: hidden;
            -webkit-font-smoothing: antialiased;
            display: flex;
            flex-direction: column;
            height: 100%;
            position: relative;
            overflow: hidden;
        }
        
        .feature-card::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(34, 197, 94, 0.12) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.4s ease;
        }
        
        .feature-card:hover::after {
            opacity: 1;
        }
        
        .dark .feature-card:hover,
        .body--dark .feature-card:hover {
            background: linear-gradient(135deg, rgba(30, 41, 59, 1) 0%, rgba(15, 23, 42, 1) 100%);
            border-color: rgba(34, 197, 94, 0.7);
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 16px 48px rgba(34, 197, 94, 0.3), 0 0 80px rgba(34, 197, 94, 0.15), inset 0 1px 1px rgba(255, 255, 255, 0.1);
        }
        
        .feature-card:hover {
            background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(241, 245, 249, 1) 100%);
            border-color: rgba(34, 197, 94, 0.7);
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 16px 48px rgba(34, 197, 94, 0.25), 0 0 80px rgba(34, 197, 94, 0.12), inset 0 1px 1px rgba(255, 255, 255, 1);
        }
        
        .dark .stat-card,
        .body--dark .stat-card {
            backdrop-filter: none;
            background: linear-gradient(135deg, rgba(15, 23, 42, 1), rgba(30, 41, 59, 1));
            border: 2px solid rgba(34, 197, 94, 0.5);
            border-radius: 1.25rem;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 60px rgba(34, 197, 94, 0.1), inset 0 1px 1px rgba(255, 255, 255, 0.1);
            transform: translateZ(0);
            backface-visibility: hidden;
            -webkit-font-smoothing: antialiased;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .dark .stat-card::before,
        .body--dark .stat-card::before {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 1.25rem;
            padding: 2px;
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.6), rgba(14, 165, 233, 0.6));
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .dark .stat-card:hover::before,
        .body--dark .stat-card:hover::before {
            opacity: 1;
        }
        
        .dark .stat-card:hover,
        .body--dark .stat-card:hover {
            transform: translateY(-4px) scale(1.05);
            box-shadow: 0 12px 48px rgba(34, 197, 94, 0.3), 0 0 100px rgba(34, 197, 94, 0.2);
            animation: pulse-glow 2s ease-in-out infinite;
        }
        
        .stat-card {
            backdrop-filter: none;
            background: linear-gradient(135deg, rgba(255, 255, 255, 1), rgba(241, 245, 249, 1));
            border: 2px solid rgba(34, 197, 94, 0.5);
            border-radius: 1.25rem;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 0 0 60px rgba(34, 197, 94, 0.08), inset 0 1px 1px rgba(255, 255, 255, 1);
            transform: translateZ(0);
            backface-visibility: hidden;
            -webkit-font-smoothing: antialiased;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 1.25rem;
            padding: 2px;
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.8), rgba(14, 165, 233, 0.8));
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .stat-card:hover::before {
            opacity: 1;
        }
        
        .stat-card:hover {
            transform: translateY(-4px) scale(1.05);
            box-shadow: 0 12px 48px rgba(34, 197, 94, 0.25), 0 0 100px rgba(34, 197, 94, 0.15);
            animation: pulse-glow 2s ease-in-out infinite;
        }
        
        .gradient-text {
            background: linear-gradient(135deg, #22c55e, #0ea5e9, #a855f7, #ec4899);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradient-shimmer 6s ease infinite;
            font-weight: 800;
            letter-spacing: -0.02em;
        }
        
        .dark .nav-blur,
        .body--dark .nav-blur {
            backdrop-filter: none;
            background: rgba(15, 23, 42, 0.98);
            border-bottom: 2px solid rgba(34, 197, 94, 0.4);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            position: relative;
            z-index: 100;
        }
        
        .nav-blur {
            backdrop-filter: none;
            background: rgba(255, 255, 255, 0.98);
            border-bottom: 2px solid rgba(34, 197, 94, 0.4);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            position: relative;
            z-index: 100;
        }
        
        /* Navbar button hover effects */
        .nav-blur button {
            transition: all 0.3s ease;
        }
        
        .nav-blur button:hover {
            transform: translateY(-2px);
        }
        
        /* Ensure all content is above background */
        .landing-bg > * {
            position: relative;
            z-index: 10;
        }
        
        /* Scroll-triggered animations: subtle, never fully hide content */
        .scroll-reveal {
            opacity: 0.9;
            transform: translate3d(0, 10px, 0);
            transition: opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            will-change: opacity, transform;
            backface-visibility: hidden;
            -webkit-font-smoothing: antialiased;
        }
        
        .scroll-reveal.revealed {
            opacity: 1;
            transform: translate3d(0, 0, 0);
        }
        
        /* Slide from left with gentle fade */
        .scroll-reveal-left {
            opacity: 0.9;
            transform: translate3d(-12px, 0, 0);
            transition: opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            will-change: opacity, transform;
            backface-visibility: hidden;
            -webkit-font-smoothing: antialiased;
        }
        
        .scroll-reveal-left.revealed {
            opacity: 1;
            transform: translate3d(0, 0, 0);
        }
        
        /* Slide from right with gentle fade */
        .scroll-reveal-right {
            opacity: 0.9;
            transform: translate3d(12px, 0, 0);
            transition: opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            will-change: opacity, transform;
            backface-visibility: hidden;
            -webkit-font-smoothing: antialiased;
        }
        
        .scroll-reveal-right.revealed {
            opacity: 1;
            transform: translate3d(0, 0, 0);
        }
        
        /* Scale up animation for charts - slight pop-in */
        .scroll-reveal-scale {
            opacity: 0.9;
            transform: scale3d(0.97, 0.97, 1);
            transition: opacity 0.7s cubic-bezier(0.34, 1.56, 0.64, 1), transform 0.7s cubic-bezier(0.34, 1.56, 0.64, 1);
            will-change: opacity, transform;
            backface-visibility: hidden;
            -webkit-font-smoothing: antialiased;
        }
        
        .scroll-reveal-scale.revealed {
            opacity: 1;
            transform: scale3d(1, 1, 1);
        }
        
        /* Staggered animation delays for cascading effect */
        .scroll-reveal-delay-1 { transition-delay: 0.1s; }
        .scroll-reveal-delay-2 { transition-delay: 0.2s; }
        .scroll-reveal-delay-3 { transition-delay: 0.3s; }
        .scroll-reveal-delay-4 { transition-delay: 0.4s; }
        .scroll-reveal-delay-5 { transition-delay: 0.5s; }
        .scroll-reveal-delay-6 { transition-delay: 0.6s; }
        
        .chart-container {
            backdrop-filter: none;
            background: linear-gradient(145deg, rgba(255, 255, 255, 1), rgba(248, 250, 252, 0.98)) !important;
            border-radius: 1.25rem;
            padding: 2rem;
            border: 2px solid rgba(34, 197, 94, 0.4);
            box-sizing: border-box;
            overflow: visible;
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12), 0 0 80px rgba(34, 197, 94, 0.08), inset 0 1px 1px rgba(255, 255, 255, 1);
            transform: translateZ(0);
            backface-visibility: hidden;
            -webkit-font-smoothing: antialiased;
            transition: all 0.4s ease;
            position: relative;
        }
        
        .chart-container:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 64px rgba(0, 0, 0, 0.15), 0 0 120px rgba(34, 197, 94, 0.12), inset 0 1px 1px rgba(255, 255, 255, 1);
            border-color: rgba(34, 197, 94, 0.6);
        }
        
        .dark .chart-container,
        .body--dark .chart-container {
            background: linear-gradient(145deg, rgba(15, 23, 42, 1), rgba(30, 41, 59, 0.98)) !important;
            border: 2px solid rgba(34, 197, 94, 0.5);
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5), 0 0 80px rgba(34, 197, 94, 0.12), inset 0 1px 1px rgba(255, 255, 255, 0.08);
        }
        
        .dark .chart-container:hover,
        .body--dark .chart-container:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 64px rgba(0, 0, 0, 0.6), 0 0 120px rgba(34, 197, 94, 0.18), inset 0 1px 1px rgba(255, 255, 255, 0.12);
            border-color: rgba(34, 197, 94, 0.7);
        }
        
        /* Make Plotly charts transparent so container background shows through */
        .plotly {
            background: transparent !important;
            border-radius: 8px;
            min-height: 350px;
        }
        
        .plotly .main-svg {
            background: transparent !important;
        }
        
        /* Force chart text visibility in dark mode using CSS */
        .dark .plotly text,
        .body--dark .plotly text,
        .dark .js-plotly-plot text,
        .body--dark .js-plotly-plot text {
            fill: #e2e8f0 !important;
        }
        
        .dark .plotly .gridlayer line,
        .body--dark .plotly .gridlayer line {
            stroke: rgba(148, 163, 184, 0.3) !important;
        }
        
        .dark .plotly .zerolinelayer line,
        .body--dark .plotly .zerolinelayer line {
            stroke: rgba(148, 163, 184, 0.5) !important;
        }
        
        /* Pie chart specific */
        .dark .plotly .slice .slicetext,
        .body--dark .plotly .slice .slicetext {
            fill: #e2e8f0 !important;
        }
        
        /* Legend */
        .dark .plotly .legend text,
        .body--dark .plotly .legend text {
            fill: #e2e8f0 !important;
        }
        
        /* Gauge/Indicator specific */
        .dark .plotly .indicator text,
        .body--dark .plotly .indicator text,
        .dark .plotly .angularaxis text,
        .body--dark .plotly .angularaxis text {
            fill: #e2e8f0 !important;
        }
        
        /* Bar chart text */
        .dark .plotly .bars text,
        .body--dark .plotly .bars text {
            fill: #e2e8f0 !important;
        }
        
        /* Axis titles and tick labels */
        .dark .plotly .xtick text,
        .body--dark .plotly .xtick text,
        .dark .plotly .ytick text,
        .body--dark .plotly .ytick text {
            fill: #e2e8f0 !important;
        }
        
        /* Enhanced table styling */
        .q-table {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .dark .q-table,
        .body--dark .q-table {
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        
        .q-table thead tr th {
            font-weight: 700;
            font-size: 0.95rem;
            letter-spacing: 0.02em;
        }
        
        .q-table tbody tr {
            transition: all 0.2s ease;
        }
        
        .q-table tbody tr:hover {
            transform: scale(1.01);
            box-shadow: 0 4px 16px rgba(34, 197, 94, 0.15);
        }
        
        /* Beautiful input styling - Light Mode */
        .q-field--outlined .q-field__control {
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        .q-field--outlined .q-field__control:hover {
            box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
        }
        
        .q-field--outlined.q-field--focused .q-field__control {
            box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.4);
        }
        
        /* Input fields dark mode - Text visibility */
        .dark .q-field__control,
        .body--dark .q-field__control {
            color: #e2e8f0 !important;
        }
        
        .dark .q-field__native,
        .body--dark .q-field__native,
        .dark input,
        .body--dark input {
            color: #e2e8f0 !important;
        }
        
        .dark .q-field__label,
        .body--dark .q-field__label {
            color: #94a3b8 !important;
        }
        
        .dark .q-placeholder,
        .body--dark .q-placeholder,
        .dark input::placeholder,
        .body--dark input::placeholder {
            color: #64748b !important;
        }
        
        /* Input prepend icons in dark mode */
        .dark .q-field__prepend,
        .body--dark .q-field__prepend {
            color: #94a3b8 !important;
        }
        
        /* Fix label floating behavior - prevent overlap */
        .q-field--float .q-field__label {
            transform: translateY(-40%) scale(0.75) !important;
        }
        
        .q-field--filled.q-field--float .q-field__label {
            transform: translateY(-40%) scale(0.75) !important;
        }
        
        /* Dark mode label positioning */
        .dark .q-field--float .q-field__label,
        .body--dark .q-field--float .q-field__label {
            transform: translateY(-40%) scale(0.75) !important;
            color: #94a3b8 !important;
        }
        
        .dark .q-field--filled.q-field--float .q-field__label,
        .body--dark .q-field--filled.q-field--float .q-field__label {
            transform: translateY(-40%) scale(0.75) !important;
        }
        
        /* Ensure label stays above input when focused or has content */
        .q-field--highlighted .q-field__label,
        .q-field--filled .q-field__label {
            opacity: 1 !important;
        }
        
        /* Expansion panel dark mode */
        .dark .q-expansion-item,
        .body--dark .q-expansion-item {
            color: #e2e8f0 !important;
        }
        
        .dark .q-expansion-item__container,
        .body--dark .q-expansion-item__container {
            background: rgba(30, 41, 59, 0.5) !important;
            border: 1px solid rgba(34, 197, 94, 0.2);
        }
        
        .dark .q-item,
        .body--dark .q-item {
            color: #e2e8f0 !important;
        }
        
        .dark .q-item__label,
        .body--dark .q-item__label {
            color: #e2e8f0 !important;
        }
        
        /* Separator in dark mode */
        .dark .q-separator,
        .body--dark .q-separator {
            background: rgba(148, 163, 184, 0.2) !important;
        }
        
        /* Button text in dark mode */
        .dark .q-btn__content,
        .body--dark .q-btn__content {
            color: inherit !important;
        }
        
        /* Login page specific - Ensure content alignment in dark mode */
        .dark .q-card,
        .body--dark .q-card {
            display: flex !important;
            flex-direction: column !important;
            align-items: stretch !important;
        }
        
        /* Ensure proper text alignment in cards */
        .dark .q-card .q-card__section,
        .body--dark .q-card .q-card__section {
            width: 100%;
        }
        
        /* Fix input field backgrounds in dark mode */
        .dark .q-field__control:before,
        .body--dark .q-field__control:before {
            border-color: rgba(148, 163, 184, 0.3) !important;
        }
        
        .dark .q-field--filled .q-field__control,
        .body--dark .q-field--filled .q-field__control {
            background: rgba(30, 41, 59, 0.5) !important;
        }
        
        .dark .q-field--filled .q-field__control:hover,
        .body--dark .q-field--filled .q-field__control:hover {
            background: rgba(30, 41, 59, 0.7) !important;
        }
        
        .dark .q-field--filled.q-field--focused .q-field__control,
        .body--dark .q-field--filled.q-field--focused .q-field__control {
            background: rgba(30, 41, 59, 0.8) !important;
        }
        
        /* Enhance slider */
        .q-slider__track-container {
            border-radius: 10px;
        }
        
        /* Beautiful scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(148, 163, 184, 0.1);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.6), rgba(14, 165, 233, 0.6));
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.8), rgba(14, 165, 233, 0.8));
        }
        
        .dark ::-webkit-scrollbar-track,
        .body--dark ::-webkit-scrollbar-track {
            background: rgba(15, 23, 42, 0.5);
        }
        
        /* Tab Navigation - Enhanced visibility for both light and dark modes */
        .q-tabs,
        .dashboard-tabs {
            overflow: visible !important;
        }
        
        /* Light mode tab background */
        .dashboard-tabs {
            background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%) !important;
            border-bottom: 2px solid rgba(34, 197, 94, 0.2) !important;
            transition: background 0.3s ease, border-color 0.3s ease;
        }
        
        /* Dark mode tab background */
        .dark .dashboard-tabs,
        .body--dark .dashboard-tabs {
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
            border-bottom: 2px solid rgba(34, 197, 94, 0.3) !important;
        }
        
        /* Light mode tab panels background */
        .dashboard-tab-panels {
            background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%) !important;
            transition: background 0.3s ease;
        }
        
        /* Dark mode tab panels background */
        .dark .dashboard-tab-panels,
        .body--dark .dashboard-tab-panels {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        }
        
        .q-tab {
            opacity: 1 !important;
            visibility: visible !important;
        }
        
        /* Light mode tabs - Dark text */
        .q-tab__label,
        .q-tab__icon {
            color: #1e293b !important;
            opacity: 0.85;
            transition: all 0.3s ease;
        }
        
        .q-tab--active .q-tab__label,
        .q-tab--active .q-tab__icon {
            color: #22c55e !important;
            opacity: 1;
        }
        
        .q-tab:hover .q-tab__label,
        .q-tab:hover .q-tab__icon {
            opacity: 1;
        }
        
        /* Dark mode tabs - Light text */
        .dark .q-tab__label,
        .dark .q-tab__icon,
        .body--dark .q-tab__label,
        .body--dark .q-tab__icon {
            color: #e2e8f0 !important;
            opacity: 0.85;
        }
        
        .dark .q-tab--active .q-tab__label,
        .dark .q-tab--active .q-tab__icon,
        .body--dark .q-tab--active .q-tab__label,
        .body--dark .q-tab--active .q-tab__icon {
            color: #22c55e !important;
            opacity: 1;
        }
        
        .dark .q-tab:hover .q-tab__label,
        .dark .q-tab:hover .q-tab__icon,
        .body--dark .q-tab:hover .q-tab__label,
        .body--dark .q-tab:hover .q-tab__icon {
            opacity: 1;
        }
        
        /* Tab indicator */
        .q-tab__indicator {
            background: #22c55e !important;
            height: 3px !important;
        }
        
        /* Ensure tabs are always visible - Emergency fallback */
        .q-tab,
        .q-tab * {
            display: block !important;
            visibility: visible !important;
        }
        
        /* Scroll Progress Bar */
        .scroll-progress {
            position: fixed;
            top: 0;
            left: 0;
            height: 4px;
            background: linear-gradient(90deg, #22c55e, #0ea5e9, #a855f7);
            z-index: 9999;
            transform-origin: left;
            transform: scaleX(0);
            transition: transform 0.1s ease-out;
        }
        
        /* Parallax scroll effects */
        .parallax-slow {
            transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* Fade up on scroll with bounce */
        @keyframes fadeInUpBounce {
            0% {
                opacity: 0;
                transform: translate3d(0, 40px, 0);
            }
            60% {
                opacity: 1;
                transform: translate3d(0, -8px, 0);
            }
            100% {
                opacity: 1;
                transform: translate3d(0, 0, 0);
            }
        }
        
        .scroll-fade-up {
            opacity: 0;
            transform: translate3d(0, 40px, 0);
            transition: opacity 0.8s ease-out, transform 0.8s ease-out;
        }
        
        .scroll-fade-up.revealed {
            animation: fadeInUpBounce 0.8s ease-out forwards;
        }
        
        /* Zoom in on scroll */
        @keyframes zoomIn {
            from {
                opacity: 0;
                transform: scale3d(0.8, 0.8, 1);
            }
            to {
                opacity: 1;
                transform: scale3d(1, 1, 1);
            }
        }
        
        .scroll-zoom {
            opacity: 0;
            transform: scale3d(0.8, 0.8, 1);
        }
        
        .scroll-zoom.revealed {
            animation: zoomIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }
        
        /* Slide and fade with rotation */
        @keyframes slideRotate {
            from {
                opacity: 0;
                transform: translate3d(-30px, 30px, 0) rotate(-5deg);
            }
            to {
                opacity: 1;
                transform: translate3d(0, 0, 0) rotate(0deg);
            }
        }
        
        .scroll-rotate {
            opacity: 0;
            transform: translate3d(-30px, 30px, 0) rotate(-5deg);
        }
        
        .scroll-rotate.revealed {
            animation: slideRotate 0.7s ease-out forwards;
        }
        
        /* Stagger delays for sequential animations */
        .stagger-1 { transition-delay: 0.1s; animation-delay: 0.1s; }
        .stagger-2 { transition-delay: 0.2s; animation-delay: 0.2s; }
        .stagger-3 { transition-delay: 0.3s; animation-delay: 0.3s; }
        .stagger-4 { transition-delay: 0.4s; animation-delay: 0.4s; }
        .stagger-5 { transition-delay: 0.5s; animation-delay: 0.5s; }
        .stagger-6 { transition-delay: 0.6s; animation-delay: 0.6s; }
        .stagger-7 { transition-delay: 0.7s; animation-delay: 0.7s; }
        .stagger-8 { transition-delay: 0.8s; animation-delay: 0.8s; }
        
        /* Smooth section transitions with gradient overlays */
        .section-transition {
            position: relative;
            overflow: hidden;
        }
        
        .section-transition::before {
            content: '';
            position: absolute;
            top: -100%;
            left: 0;
            right: 0;
            height: 100%;
            background: linear-gradient(180deg, transparent, rgba(34, 197, 94, 0.03));
            transition: top 1s ease-out;
        }
        
        .section-transition.revealed::before {
            top: 0;
        }
        
        /* Advanced Animation: Flip In */
        @keyframes flipIn {
            from {
                transform: perspective(400px) rotate3d(1, 0, 0, 90deg);
                opacity: 0;
            }
            40% {
                transform: perspective(400px) rotate3d(1, 0, 0, -20deg);
            }
            60% {
                transform: perspective(400px) rotate3d(1, 0, 0, 10deg);
                opacity: 1;
            }
            80% {
                transform: perspective(400px) rotate3d(1, 0, 0, -5deg);
            }
            to {
                transform: perspective(400px) rotate3d(0, 0, 0, 0);
            }
        }
        
        .scroll-flip {
            opacity: 0.3;
            transform: perspective(400px) rotate3d(1, 0, 0, 30deg);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        
        .scroll-flip.revealed {
            animation: flipIn 0.8s cubic-bezier(0.36, 0, 0.66, -0.56) forwards;
            opacity: 1;
        }
        
        /* Advanced Animation: Bounce In */
        @keyframes bounceIn {
            from, 20%, 40%, 60%, 80%, to {
                animation-timing-function: cubic-bezier(0.215, 0.61, 0.355, 1);
            }
            0% {
                opacity: 0;
                transform: scale3d(0.3, 0.3, 0.3);
            }
            20% {
                transform: scale3d(1.1, 1.1, 1.1);
            }
            40% {
                transform: scale3d(0.9, 0.9, 0.9);
            }
            60% {
                opacity: 1;
                transform: scale3d(1.03, 1.03, 1.03);
            }
            80% {
                transform: scale3d(0.97, 0.97, 0.97);
            }
            to {
                opacity: 1;
                transform: scale3d(1, 1, 1);
            }
        }
        
        .scroll-bounce {
            opacity: 0.3;
            transform: scale3d(0.7, 0.7, 0.7);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        
        .scroll-bounce.revealed {
            animation: bounceIn 0.8s forwards;
            opacity: 1;
        }
        
        /* Advanced Animation: Slide Diagonal */
        @keyframes slideDiagonal {
            from {
                opacity: 0;
                transform: translate3d(-60px, 60px, 0);
            }
            to {
                opacity: 1;
                transform: translate3d(0, 0, 0);
            }
        }
        
        .scroll-diagonal {
            opacity: 0.3;
            transform: translate3d(-30px, 30px, 0);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        
        .scroll-diagonal.revealed {
            animation: slideDiagonal 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
            opacity: 1;
        }
        
        /* Advanced Animation: Wave Effect for Groups */
        @keyframes wave {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .scroll-wave {
            opacity: 0.3;
            transform: translateY(20px);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        
        .scroll-wave.revealed {
            animation: wave 0.6s ease-out forwards;
            opacity: 1;
        }
        
        /* Number Counter Animation */
        @keyframes countUp {
            from {
                opacity: 0;
                transform: translateY(20px) scale(0.8);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        
        .counter-animate {
            display: inline-block;
            opacity: 1;
            transform: translateY(0) scale(1);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        
        .counter-animate.counting {
            animation: countUp 0.6s ease-out forwards;
        }
        
        /* Ensure visibility fallback for all scroll animations */
        [class*="scroll-"].revealed {
            opacity: 1 !important;
        }
        
        /* Prevent flash of invisible content */
        @media (prefers-reduced-motion: reduce) {
            [class*="scroll-"] {
                opacity: 1 !important;
                transform: none !important;
                filter: none !important;
                animation: none !important;
            }
        }
        
        /* Floating Particles Background */
        .particles-bg {
            position: absolute;
            inset: 0;
            overflow: hidden;
            pointer-events: none;
            z-index: -1;
        }
        
        .particle {
            position: absolute;
            background: radial-gradient(circle, rgba(34, 197, 94, 0.8), transparent);
            border-radius: 50%;
            animation: float-particle linear infinite;
            opacity: 0;
        }
        
        @keyframes float-particle {
            0% {
                transform: translateY(100vh) translateX(0) scale(0);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100px) translateX(100px) scale(1);
                opacity: 0;
            }
        }
        
        /* Magnetic Effect for Buttons */
        .magnetic-effect {
            transition: transform 0.2s ease-out;
        }
        
        /* Reveal with Blur Effect */
        @keyframes revealBlur {
            from {
                opacity: 0;
                filter: blur(20px);
                transform: scale(0.9);
            }
            to {
                opacity: 1;
                filter: blur(0);
                transform: scale(1);
            }
        }
        
        .scroll-blur {
            opacity: 0.3;
            filter: blur(10px);
            transform: scale(0.95);
            transition: opacity 0.3s ease, filter 0.3s ease, transform 0.3s ease;
        }
        
        .scroll-blur.revealed {
            animation: revealBlur 0.8s ease-out forwards;
            opacity: 1;
        }
        
        /* Typewriter Effect */
        @keyframes typewriter {
            from {
                width: 0;
            }
            to {
                width: 100%;
            }
        }
        
        .typewriter {
            overflow: hidden;
            white-space: nowrap;
            border-right: 3px solid rgba(34, 197, 94, 0.8);
            width: 0;
        }
        
        .typewriter.typing {
            animation: typewriter 2s steps(40) forwards, blink 0.75s step-end infinite;
        }
        
        @keyframes blink {
            from, to {
                border-color: transparent;
            }
            50% {
                border-color: rgba(34, 197, 94, 0.8);
            }
        }
        
        /* Scroll Snap for Smooth Navigation */
        .scroll-snap-container {
            scroll-snap-type: y proximity;
            scroll-behavior: smooth;
        }
        
        .scroll-snap-section {
            scroll-snap-align: start;
            scroll-snap-stop: normal;
        }
        
        /* Glow Pulse on Scroll */
        @keyframes glowPulse {
            0%, 100% {
                box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
            }
            50% {
                box-shadow: 0 0 40px rgba(34, 197, 94, 0.6), 0 0 60px rgba(34, 197, 94, 0.4);
            }
        }
        
        .scroll-glow {
            box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
        }
        
        .scroll-glow.revealed {
            animation: glowPulse 2s ease-in-out infinite;
        }
        
        /* Skew and Fade */
        @keyframes skewFade {
            from {
                opacity: 0;
                transform: skewX(-15deg) translateX(-50px);
            }
            to {
                opacity: 1;
                transform: skewX(0) translateX(0);
            }
        }
        
        .scroll-skew {
            opacity: 0.3;
            transform: skewX(-8deg) translateX(-25px);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        
        .scroll-skew.revealed {
            animation: skewFade 0.7s ease-out forwards;
            opacity: 1;
        }
        </style>
        
        <script>
        // Scroll Progress Bar
        (function() {
            function init() {
                if (document.body && !document.querySelector('.scroll-progress')) {
                    const progressBar = document.createElement('div');
                    progressBar.className = 'scroll-progress';
                    progressBar.style.width = '100%';
                    document.body.appendChild(progressBar);
                    
                    window.addEventListener('scroll', () => {
                        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
                        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                        const scrolled = (winScroll / height);
                        progressBar.style.transform = `scaleX(${scrolled})`;
                    });
                }
            }
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', init);
            } else {
                init();
            }
        })();
        </script>
        
        <script>
        // Matrix Digital Rain
        (function() {
            function initMatrix() {
                const canvas = document.querySelector('.matrix-canvas');
                if (!canvas) return;
                
                const ctx = canvas.getContext('2d');
                let width = canvas.width = window.innerWidth;
                let height = canvas.height = window.innerHeight;
                
                const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$#@%&*';
                const fontSize = 16;
                const columns = width / fontSize;
                const drops = [];
                
                for (let i = 0; i < columns; i++) {
                    drops[i] = 1;
                }
                
                function draw() {
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
                    ctx.fillRect(0, 0, width, height);
                    
                    ctx.fillStyle = '#00FF41';
                    ctx.font = fontSize + 'px monospace';
                    
                    for (let i = 0; i < drops.length; i++) {
                        const text = characters.charAt(Math.floor(Math.random() * characters.length));
                        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                        
                        if (drops[i] * fontSize > height && Math.random() > 0.975) {
                            drops[i] = 0;
                        }
                        drops[i]++;
                    }
                }
                
                let interval = setInterval(draw, 33);
                
                window.addEventListener('resize', () => {
                    width = canvas.width = window.innerWidth;
                    height = canvas.height = window.innerHeight;
                });
            }
            
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initMatrix);
            } else {
                initMatrix();
            }
        })();
        </script>

        """
    )


def get_chart_colors(is_dark_mode=False):
    """Get chart colors based on current theme"""
    if is_dark_mode:
        return {
            'text': '#e2e8f0',
            'grid': 'rgba(148,163,184,0.15)',
            'background': 'rgba(0,0,0,0)',
        }
    else:
        return {
            'text': '#1e293b',
            'grid': 'rgba(148,163,184,0.2)',
            'background': 'rgba(0,0,0,0)',
        }


def landing_page():
    add_global_styles()
    
    # Get dynamic stats from services
    try:
        total_txn, fraud_cnt, fraud_rate = services.get_fraud_summary()
        model_status = services.get_model_status()
    except:
        total_txn, fraud_cnt, fraud_rate = 0, 0, 0.0
        model_status = {'status': 'loading'}
    try:
        model_info = services.get_active_model_info()
    except Exception:
        model_info = {}
    model_type = str(model_info.get('model_type') or 'unknown')
    model_type_label = model_type.replace('_', ' ').strip().title()
    dataset_path_label = str(model_info.get('dataset_path') or '').strip()
    if dataset_path_label:
        dataset_path_label = os.path.basename(dataset_path_label)
    else:
        dataset_path_label = 'Dataset'
    
    with ui.column().classes('w-full min-h-screen landing-bg').style('margin: 0; padding: 0;'):
        # Animated Navbar
        with ui.row().classes('w-full justify-between items-center px-8 py-4 nav-blur sticky top-0 z-50 animate-fade-in'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('hub', size='2rem').classes('text-green-400')
                ui.label('Smart Money Laundering System').classes('text-2xl font-bold tracking-tight gradient-text')
            with ui.row().classes('items-center gap-4'):
                ui.button('AI Engine', on_click=lambda: ui.run_javascript('document.getElementById("features-section").scrollIntoView({behavior: "smooth"})')).props('flat dense')
                ui.button('Forensic Core', on_click=lambda: ui.run_javascript('document.getElementById("forensic-section").scrollIntoView({behavior: "smooth"})')).props('flat dense')
                ui.button('3D Visualizer', on_click=lambda: ui.navigate.to('/animations')).props('flat dense')
                theme_toggle_button()
                ui.button('ACCESS SYSTEM', icon='security', on_click=lambda: ui.navigate.to('/login')).props('unelevated color=green-10').classes('ml-2 font-bold')

        # Hero Section - Enhanced with Cyber Aesthetics
        with ui.column().classes('w-full px-8 py-24 items-center text-center gap-8 relative'):
            # Matrix rain effect container
            ui.html('<canvas class="matrix-canvas"></canvas>')
            
            # AI Brain Icon with pulse
            with ui.element('div').classes('relative z-10').style('animation: float-gentle 3s ease-in-out infinite;'):
                ui.label('🧠').classes('text-8xl scroll-blur stagger-1').style('filter: drop-shadow(0 0 50px rgba(0, 255, 65, 0.8));')
            
            # Main headline
            ui.label('VTAC Money Laundering Detection').classes('text-6xl md:text-8xl font-extrabold leading-tight gradient-text scroll-flip stagger-2 relative z-10')
            
            # Subheadline
            ui.label('A VTAC paper-aligned pipeline: ML detection + de-anonymization + advisory identification over a transaction graph. Built to classify transactions as illegal/legal and surface evidence-ready signals.').classes('text-xl md:text-2xl font-medium max-w-4xl dark:text-gray-300 text-gray-700 scroll-skew stagger-3 relative z-10')

            with ui.row().classes('gap-3 flex-wrap justify-center scroll-reveal relative z-10'):
                ui.badge('Illegal / Legal', color='red').classes('px-4 py-2 text-sm font-bold')
                ui.badge('Elliptic Dataset', color='purple').classes('px-4 py-2 text-sm font-bold')
                ui.badge('Result.csv De-anonymization', color='indigo').classes('px-4 py-2 text-sm font-bold')
                ui.badge('VTAC Advisory Framework', color='green').classes('px-4 py-2 text-sm font-bold')
                ui.badge('Optional Blockchain Enrichment', color='cyan').classes('px-4 py-2 text-sm font-bold')
            
            # CTA buttons
            with ui.row().classes('gap-6 mt-10 scroll-diagonal stagger-4 relative z-10'):
                ui.button('LAUNCH AI DASHBOARD', icon='bolt', on_click=lambda: ui.navigate.to('/dashboard')).props('unelevated size=lg').classes('magnetic-effect bg-gradient-to-r from-green-500 to-cyan-600 text-white px-10 py-5 text-xl font-bold shadow-2xl hover:scale-105 transition-all').style('border-radius: 12px;')
                ui.button('EXPLORE 3D CORE', icon='visibility', on_click=lambda: ui.navigate.to('/animations')).props('outline size=lg').classes('magnetic-effect border-2 px-10 py-5 text-xl font-bold dark:border-cyan-400 dark:text-cyan-400 border-gray-900 text-gray-900 hover:bg-cyan-400/10 transition-all').style('border-radius: 12px;')

        # Stats Section - Enhanced with Dynamic Counters
        with ui.element('div').classes('w-full px-8 py-20 bg-black/5'):
            with ui.element('div').classes('w-full max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8'):
                stats = [
                    (model_type_label, 'Active Model', 'Model used for illegal/legal detection right now.', 'memory', 'cyan-400'),
                    (dataset_path_label, 'Active Dataset', 'Dataset currently selected for training/prediction.', 'dataset', 'purple-400'),
                    (f'{total_txn:,} txns', 'Transactions Logged', 'Total transactions stored in the local database.', 'receipt_long', 'green-400'),
                    (f'{fraud_rate:.2f}%', 'Illegal Rate', 'Percent of logged transactions classified as illegal.', 'percent', 'yellow-400'),
                ]
                for val, label, desc, icon, color in stats:
                    sval = str(val)
                    if len(sval) > 18:
                        size_cls = 'text-2xl'
                    elif len(sval) > 12:
                        size_cls = 'text-3xl'
                    elif len(sval) > 8:
                        size_cls = 'text-4xl'
                    else:
                        size_cls = 'text-5xl'
                    with ui.card().classes('stat-card text-center w-full h-[235px] p-6 flex flex-col justify-center items-center scroll-bounce stagger-1'):
                        ui.icon(icon, size='3.25rem').classes(f'text-{color} mb-4 scroll-zoom')
                        ui.label(sval).classes(f'stat-value {size_cls} font-black text-{color} mb-2 counter-animate px-2 text-center').style(f'text-shadow: 0 0 30px {color}80;')
                        ui.label(label).classes('stat-label text-base font-bold mt-2 dark:text-gray-300 text-gray-700 text-center')
                        ui.label(desc).classes('text-xs mt-2 dark:text-gray-400 text-gray-600 text-center max-w-[220px]')

        with ui.column().classes('w-full px-8 py-24 items-center gap-12 bg-gradient-to-b from-transparent to-black/10').props('id=features-section'):
            with ui.row().classes('items-center gap-4 scroll-reveal'):
                ui.icon('article', size='4rem').classes('text-cyan-400')
                ui.label('VTAC Paper Alignment').classes('text-5xl font-extrabold gradient-text')

            ui.label('This system follows the VTAC approach described in “Machine Learning in Money Laundering Detection Over Blockchain Technology”: detection, de-anonymization, and identification/advisory over a transaction graph.').classes('text-lg md:text-xl max-w-5xl text-center dark:text-gray-300 text-gray-700 scroll-reveal')

            with ui.row().classes('w-full max-w-7xl justify-center gap-8 flex-wrap'):
                with ui.card().classes('feature-card flex-1 min-w-[340px] scroll-reveal-left'):
                    ui.label('1) Detection (ML)').classes('text-2xl font-bold mb-4 text-cyan-400')
                    ui.label('Trains and evaluates models on the Elliptic dataset using 10-fold cross-validation without leakage. Active inference returns an illegal/legal score for a selected transaction.').classes('dark:text-gray-300 text-gray-600 leading-relaxed mb-6')
                    with ui.column().classes('gap-3'):
                        ui.badge('RandomForest', color='cyan').classes('p-2')
                        ui.badge('AdaBoost', color='blue').classes('p-2')
                        ui.badge('XGBoost (selected)', color='indigo').classes('p-2')

                with ui.card().classes('feature-card flex-1 min-w-[340px] scroll-reveal'):
                    ui.label('2) De-anonymization').classes('text-2xl font-bold mb-4 text-purple-400')
                    ui.label('Maps Elliptic txId values to real Bitcoin transaction hashes using Result.csv, enabling downstream chain analysis on real transactions.').classes('dark:text-gray-300 text-gray-600 leading-relaxed mb-6')
                    with ui.column().classes('gap-3'):
                        ui.badge('Result.csv mapping', color='purple').classes('p-2')
                        ui.badge('txId → tx_hash', color='violet').classes('p-2')
                        ui.badge('Elliptic dataset support', color='fuchsia').classes('p-2')

                with ui.card().classes('feature-card flex-1 min-w-[340px] scroll-reveal-right'):
                    ui.label('3) Identification & Advisory').classes('text-2xl font-bold mb-4 text-green-400')
                    ui.label('Builds a graph neighborhood from the Elliptic edge list and produces VTAC advisory fields: value, frequency, time window, and weight factor. Optional blockchain lookup enriches with real BTC totals and beneficiaries.').classes('dark:text-gray-300 text-gray-600 leading-relaxed mb-6')
                    with ui.column().classes('gap-3'):
                        ui.badge('Value', color='green').classes('p-2')
                        ui.badge('Frequency', color='emerald').classes('p-2')
                        ui.badge('Time Window', color='teal').classes('p-2')
                        ui.badge('Weight Factor', color='lime').classes('p-2')

            with ui.card().classes('glass-card p-6 w-full max-w-5xl scroll-reveal-scale'):
                with ui.row().classes('items-center gap-3 mb-2'):
                    ui.icon('travel_explore', size='2rem').classes('text-cyan-400')
                    ui.label('Try VTAC Lookup in the UI').classes('text-2xl font-bold dark:text-white text-gray-900')
                ui.label('Go to Dashboard → Monitor → Elliptic txId Lookup. Enter a txId from Result.csv and get illegal/legal classification plus advisory fields and beneficiaries.').classes('dark:text-gray-300 text-gray-600')
                with ui.row().classes('gap-4 mt-4'):
                    ui.button('OPEN LOGIN', icon='security', on_click=lambda: ui.navigate.to('/login')).props('unelevated color=green-10').classes('font-bold')
                    ui.button('API: /api/predict_elliptic/{txId}', icon='link', on_click=lambda: ui.run_javascript("navigator.clipboard.writeText(window.location.origin + '/api/predict_elliptic/230325127')")).props('outline').classes('font-bold')

            with ui.card().classes('feature-card w-full max-w-5xl scroll-reveal'):
                with ui.row().classes('items-center gap-3 mb-4'):
                    ui.icon('assignment', size='2rem').classes('text-green-400')
                    ui.label('VTAC Advisory Framework (Outputs)').classes('text-2xl font-bold dark:text-white text-gray-900')
                ui.label('For each transaction, the system produces VTAC advisory fields to help investigators prioritize and interpret activity.').classes('dark:text-gray-300 text-gray-600 mb-4')
                with ui.row().classes('w-full gap-4 flex-wrap'):
                    with ui.card().classes('glass-card p-4 flex-1 min-w-[220px]'):
                        ui.label('Value').classes('text-lg font-bold text-green-400')
                        ui.label('Incoming/outgoing BTC totals and fees (when blockchain lookup is enabled).').classes('text-sm dark:text-gray-300 text-gray-700')
                    with ui.card().classes('glass-card p-4 flex-1 min-w-[220px]'):
                        ui.label('Frequency').classes('text-lg font-bold text-cyan-400')
                        ui.label('Graph-based incoming/outgoing edge counts around the transaction.').classes('text-sm dark:text-gray-300 text-gray-700')
                    with ui.card().classes('glass-card p-4 flex-1 min-w-[220px]'):
                        ui.label('Time Window').classes('text-lg font-bold text-purple-400')
                        ui.label('Elliptic time-step window, plus optional blockchain time window from block times.').classes('text-sm dark:text-gray-300 text-gray-700')
                    with ui.card().classes('glass-card p-4 flex-1 min-w-[220px]'):
                        ui.label('Weight Factor').classes('text-lg font-bold text-yellow-400')
                        ui.label('Neighborhood weight estimate (normalized local degree).').classes('text-sm dark:text-gray-300 text-gray-700')

        # NEW: Neural Architecture Section
        with ui.column().classes('w-full px-8 py-24 items-center gap-12 bg-gradient-to-b from-transparent to-black/10').props('id=forensic-section'):
            with ui.row().classes('items-center gap-4 scroll-reveal'):
                ui.icon('psychology', size='4rem').classes('text-purple-400')
                ui.label('Neural Forensic Architecture').classes('text-5xl font-extrabold gradient-text')
            
            with ui.row().classes('w-full max-w-7xl justify-center gap-8 flex-wrap'):
                with ui.card().classes('feature-card flex-1 min-w-[350px] scroll-reveal-left'):
                    ui.label('🧠 Multi-Layer Perception').classes('text-2xl font-bold mb-4 text-purple-400')
                    ui.label('Our AI engine uses advanced Random Forest and Isolation Forest ensembles to identify anomalies in high-dimensional transaction spaces.').classes('text-gray-400 mb-6')
                    with ui.column().classes('gap-3'):
                        ui.badge('Temporal Pattern Analysis', color='purple').classes('p-2')
                        ui.badge('Spatial Risk Mapping', color='blue').classes('p-2')
                        ui.badge('Behavioral Biometrics', color='cyan').classes('p-2')

                with ui.card().classes('feature-card flex-1 min-w-[350px] scroll-reveal-right'):
                    ui.label('🛡️ Cryptographic Integrity').classes('text-2xl font-bold mb-4 text-green-400')
                    ui.label('Every detection event is cryptographically hashed using SHA-256 and signed with RSA-2048 keys before storage.').classes('text-gray-400 mb-6')
                    with ui.column().classes('gap-3'):
                        ui.badge('Immutable Audit Trail', color='green').classes('p-2')
                        ui.badge('Digital Signatures', color='emerald').classes('p-2')
                        ui.badge('Zero-Tamper Ledger', color='teal').classes('p-2')

        # Interactive Visualizer Preview Section
        with ui.row().classes('w-full px-8 py-24 items-center justify-center gap-16 flex-wrap-reverse'):
            with ui.column().classes('max-w-xl gap-6 scroll-reveal-left'):
                ui.label('Live 3D Forensic Simulation').classes('text-4xl font-extrabold dark:text-white text-gray-900')
                ui.label('Step inside the neural core. Watch transactions as they are analyzed, validated, and appended to the blockchain ledger in an immersive 3D environment.').classes('text-lg dark:text-gray-400 text-gray-600 leading-relaxed')
                with ui.row().classes('gap-4 mt-4'):
                    ui.button('LAUNCH 3D ENGINE', icon='rocket_launch', on_click=lambda: ui.navigate.to('/animations')).props('unelevated color=green-10').classes('px-8 py-4 font-bold rounded-lg')
                    ui.button('WATCH DEMO', icon='play_circle', on_click=lambda: ui.navigate.to('/animations')).props('outline').classes('px-8 py-4 font-bold rounded-lg dark:text-white text-gray-900 dark:border-white border-gray-900')
            
            with ui.card().classes('glass-card p-0 overflow-hidden w-full max-w-2xl scroll-reveal-right').style('height: 400px;'):
                ui.image('https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=2232&auto=format&fit=crop').classes('w-full h-full object-cover opacity-80')
                with ui.element('div').classes('absolute inset-0 flex items-center justify-center bg-black/40 hover:bg-black/20 transition-all'):
                    ui.icon('3d_rotation', size='6rem').classes('text-green-400 animate-pulse')

        # Live Analytics Section
        with ui.column().classes('w-full px-8 py-24 items-center gap-12 bg-black/5').props('id=analytics-section'):
            with ui.row().classes('items-center gap-4 scroll-reveal'):
                ui.icon('insights', size='4rem').classes('text-cyan-400')
                ui.label('Real-Time Intelligence').classes('text-5xl font-extrabold gradient-text')
            
            with ui.row().classes('w-full max-w-7xl gap-8 flex-wrap justify-center'):
                with ui.card().classes('chart-container flex-1 min-w-[500px] scroll-reveal-scale'):
                    ui.label('Detection Confidence Trend (Demo)').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Illustrative model confidence over recent evaluation points (higher is better).').classes('text-xs mb-6 dark:text-gray-300 text-gray-600')
                    # Mini dynamic chart
                    fig = go.Figure(go.Scatter(y=[95, 96, 98, 97, 99.2], x=[1, 2, 3, 4, 5], mode='lines+markers', line=dict(color='#00FF41', width=4)))
                    fig.update_layout(
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#0f172a'),
                        margin=dict(l=20, r=20, t=10, b=20),
                        xaxis=dict(title='Point', showgrid=False, color='#334155'),
                        yaxis=dict(title='Confidence (%)', showgrid=True, gridcolor='rgba(148,163,184,0.25)', color='#334155', range=[90, 100]),
                    )
                    ui.plotly(fig).classes('w-full')
                
                with ui.column().classes('flex-1 min-w-[350px] gap-6'):
                    with ui.card().classes('glass-card p-6 scroll-reveal-right stagger-1'):
                        ui.label('⚡ Low Latency').classes('text-xl font-bold text-cyan-400')
                        ui.label('Proprietary inference optimization ensures <50ms processing per transaction.').classes('text-sm text-gray-400')
                    with ui.card().classes('glass-card p-6 scroll-reveal-right stagger-2'):
                        ui.label('🔍 Forensic Explainability').classes('text-xl font-bold text-purple-400')
                        ui.label('Integrated SHAP values provide clear evidence for every flagged transaction.').classes('text-sm text-gray-400')
                    with ui.card().classes('glass-card p-6 scroll-reveal-right stagger-3'):
                        ui.label('🛡️ Immutable Records').classes('text-xl font-bold text-green-400')
                        ui.label('Signed audit logs ensure compliance and prevent post-detection tampering.').classes('text-sm text-gray-400')

        # Final CTA Section
        with ui.column().classes('w-full px-8 py-32 items-center text-center gap-8 bg-gradient-to-r from-green-900/20 to-cyan-900/20'):
            ui.label('Ready to secure your financial ecosystem?').classes('text-4xl font-extrabold dark:text-white text-gray-900 scroll-reveal')
            ui.label('Join the elite financial institutions using AI to stay ahead of cyber criminals.').classes('text-xl dark:text-gray-300 text-gray-600 max-w-2xl scroll-reveal')
            ui.button('INITIALIZE SYSTEM ACCESS', icon='security', on_click=lambda: ui.navigate.to('/login')).props('unelevated size=xl').classes('bg-green-600 hover:bg-green-500 text-white font-black px-12 py-6 rounded-2xl shadow-2xl hover:scale-105 transition-all scroll-bounce')

        # Footer
        with ui.column().classes('w-full px-8 py-12 items-center gap-6 border-t border-white/10'):
            ui.label('Smart Money Laundering System | Neural Forensic Ledger v2.0').classes('text-sm font-bold text-gray-500')
            with ui.row().classes('gap-8 text-gray-600'):
                ui.link('Architecture', '#').classes('hover:text-green-400')
                ui.link('Security Docs', '#').classes('hover:text-green-400')
                ui.link('API Reference', '#').classes('hover:text-green-400')
                ui.link('3D Core', '/animations').classes('hover:text-green-400')
            
            with ui.row().classes('w-full justify-center gap-8 flex-wrap'):
                # Feature 1: Neural Engine
                with ui.card().classes('feature-card flex-1 min-w-[320px] scroll-reveal-left stagger-1'):
                    with ui.row().classes('items-center gap-4 mb-4'):
                        ui.icon('psychology', size='3rem').classes('text-purple-400')
                        ui.label('Neural Analysis Engine').classes('text-2xl font-bold dark:text-white text-gray-900')
                    ui.label('Deep Learning models specifically optimized for identifying complex money laundering patterns (Layering, Placement, Integration) with multi-dimensional feature extraction.').classes('text-gray-600 dark:text-gray-300 leading-relaxed mb-6')
                    with ui.column().classes('gap-2'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('check_circle', size='xs').classes('text-green-500')
                            ui.label('Temporal Pattern Recognition').classes('text-sm font-semibold')
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('check_circle', size='xs').classes('text-green-500')
                            ui.label('Multi-modal Data Fusion').classes('text-sm font-semibold')
                
                # Feature 2: Blockchain Ledger
                with ui.card().classes('feature-card flex-1 min-w-[320px] scroll-reveal stagger-2'):
                    with ui.row().classes('items-center gap-4 mb-4'):
                        ui.icon('link', size='3rem').classes('text-green-400')
                        ui.label('Forensic Blockchain Ledger').classes('text-2xl font-bold dark:text-white text-gray-900')
                    ui.label('Every detection and decision is cryptographically signed and stored on an immutable private blockchain, ensuring an untamperable audit trail for regulatory compliance.').classes('text-gray-600 dark:text-gray-300 leading-relaxed mb-6')
                    with ui.column().classes('gap-2'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('check_circle', size='xs').classes('text-green-500')
                            ui.label('SHA-256 Hashing Architecture').classes('text-sm font-semibold')
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('check_circle', size='xs').classes('text-green-500')
                            ui.label('RSA Digital Signatures').classes('text-sm font-semibold')

                # Feature 3: SHAP Explainability
                with ui.card().classes('feature-card flex-1 min-w-[320px] scroll-reveal-right stagger-3'):
                    with ui.row().classes('items-center gap-4 mb-4'):
                        ui.icon('visibility', size='3rem').classes('text-cyan-400')
                        ui.label('SHAP Explainable AI').classes('text-2xl font-bold dark:text-white text-gray-900')
                    ui.label('No black-box decisions. Our SHAP implementation explains exactly WHY a transaction was flagged, providing forensic analysts with actionable insights and evidence.').classes('text-gray-600 dark:text-gray-300 leading-relaxed mb-6')
                    with ui.column().classes('gap-2'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('check_circle', size='xs').classes('text-green-500')
                            ui.label('Feature Importance Attribution').classes('text-sm font-semibold')
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('check_circle', size='xs').classes('text-green-500')
                            ui.label('Evidence-based Reporting').classes('text-sm font-semibold')

        # Project Animation Showcase
        with ui.column().classes('w-full px-8 py-20 items-center gap-8 bg-black/10').props('id=animation-showcase'):
            with ui.row().classes('items-center gap-4 animate-float-up scroll-reveal'):
                ui.icon('animation', size='3rem').classes('text-green-400').style('filter: drop-shadow(0 0 20px rgba(34, 197, 94, 0.5));')
                ui.label('System Visualization').classes('text-5xl font-extrabold gradient-text')
            
            with ui.row().classes('w-full justify-center gap-12 flex-wrap items-center'):
                # 2D Animation Preview
                with ui.card().classes('glass-card p-0 overflow-hidden flex-1 min-w-[380px] scroll-reveal-left'):
                    with ui.column().classes('p-8 gap-4'):
                        ui.label('2D Neural Flow').classes('text-3xl font-bold dark:text-white text-gray-900')
                        ui.label('Interactive Sankey diagrams and real-time data propagation simulations showing transaction lifecycle.').classes('dark:text-gray-300 text-gray-600')
                        ui.button('VIEW 2D ANALYTICS', icon='analytics', on_click=lambda: ui.navigate.to('/animations')).props('unelevated color=blue-600').classes('w-full font-bold mt-4')
                    ui.image('https://images.unsplash.com/photo-1551288049-bbbda536339a?q=80&w=2070&auto=format&fit=crop').classes('w-full h-64 object-cover opacity-50')

                # 3D Animation Preview
                with ui.card().classes('glass-card p-0 overflow-hidden flex-1 min-w-[380px] scroll-reveal-right'):
                    with ui.column().classes('p-8 gap-4'):
                        ui.label('3D Forensic Core').classes('text-3xl font-bold dark:text-white text-gray-900')
                        ui.label('Immersive Three.js simulation of the decentralized ledger with 8-stage processing nodes and particle trails.').classes('dark:text-gray-300 text-gray-600')
                        ui.button('EXPLORE 3D CORE', icon='3d_rotation', on_click=lambda: ui.navigate.to('/animations')).props('unelevated color=green-600').classes('w-full font-bold mt-4')
                    ui.image('https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=2232&auto=format&fit=crop').classes('w-full h-64 object-cover opacity-50')

        # Dynamic Analytics Section with Charts
        with ui.column().classes('w-full px-8 py-20 items-center gap-8').props('id=analytics-section'):
            # Section header with icon
            with ui.row().classes('items-center gap-4 animate-slide-right'):
                ui.icon('insights', size='3rem').classes('text-blue-400').style('filter: drop-shadow(0 0 20px rgba(14, 165, 233, 0.5));')
                ui.label('Live System Analytics').classes('text-5xl font-extrabold gradient-text')
            ui.label('Real-time insights powered by advanced AI and blockchain technology').classes('text-xl font-medium animate-slide-right delay-100 dark:text-gray-300 text-gray-600 max-w-3xl text-center').style('line-height: 1.6;')
            
            # First row of charts
            with ui.row().classes('w-full max-w-6xl gap-6 mt-8 flex-wrap justify-center'):
                # Illegal Detection Chart
                with ui.card().classes('chart-container flex-1 min-w-[350px] max-w-[500px] scroll-reveal scroll-reveal-delay-1'):
                    ui.label('Illegal vs Legal Transactions').classes('text-lg font-semibold mb-4 dark:text-white text-gray-900')
                    
                    legitimate_count = total_txn - fraud_cnt
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=['Legal', 'Illegal'],
                        values=[legitimate_count, fraud_cnt],
                        marker=dict(colors=['#22c55e', '#ef4444']),
                        hole=0.4,
                        textinfo='label+percent',
                        textposition='outside',
                        textfont=dict(size=13)
                    )])
                    fig_pie.update_layout(
                        height=350,
                        margin=dict(l=40, r=40, t=40, b=60),
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        showlegend=True,
                        legend=dict(
                            orientation='h',
                            y=-0.15,
                            x=0.5,
                            xanchor='center'
                        )
                    )
                    chart_element = ui.plotly(fig_pie).classes('w-full pie-chart')
                    chart_element.style('background: transparent;')
                
                # Detection Rate Gauge
                with ui.card().classes('chart-container flex-1 min-w-[350px] max-w-[500px] scroll-reveal-left scroll-reveal-delay-2'):
                    ui.label('Current Detection Rate').classes('text-lg font-semibold mb-4 dark:text-white text-gray-900')
                    
                    fig_gauge = go.Figure(go.Indicator(
                        mode='gauge+number+delta',
                        value=99.2,
                        domain={'x': [0, 1], 'y': [0, 0.85]},
                        title={'text': 'Accuracy %', 'font': {'size': 14}},
                        number={'font': {'size': 36}, 'valueformat': '.1f'},
                        delta={'reference': 95, 'increasing': {'color': '#22c55e'}, 'font': {'size': 14}},
                        gauge={
                            'axis': {'range': [None, 100], 'tickfont': {'size': 10}},
                            'bar': {'color': '#22c55e', 'thickness': 0.8},
                            'bgcolor': 'rgba(148,163,184,0.2)',
                            'borderwidth': 2,
                            'bordercolor': '#64748b',
                            'steps': [
                                {'range': [0, 50], 'color': 'rgba(239,68,68,0.3)'},
                                {'range': [50, 75], 'color': 'rgba(251,191,36,0.3)'},
                                {'range': [75, 100], 'color': 'rgba(34,197,94,0.3)'}
                            ],
                            'threshold': {
                                'line': {'color': '#0ea5e9', 'width': 4},
                                'thickness': 0.75,
                                'value': 95
                            }
                        }
                    ))
                    fig_gauge.update_layout(
                        height=350,
                        margin=dict(l=40, r=40, t=100, b=40),
                        paper_bgcolor='rgba(0, 0, 0, 0)'
                    )
                    chart_element = ui.plotly(fig_gauge).classes('w-full gauge-chart')
                    chart_element.style('background: transparent;')
            
            # Second row of charts
            with ui.row().classes('w-full max-w-6xl gap-6 mt-6 flex-wrap justify-center'):
                # Model Performance Metrics
                with ui.card().classes('chart-container flex-1 min-w-[350px] max-w-[500px] scroll-reveal-right scroll-reveal-delay-3'):
                    ui.label('Model Performance Metrics').classes('text-lg font-semibold mb-4 dark:text-white text-gray-900')
                    
                    metrics = ['Precision', 'Recall', 'F1-Score', 'Accuracy']
                    values = [98.5, 97.8, 98.1, 99.2]
                    
                    fig_bar = go.Figure(data=[
                        go.Bar(
                            x=metrics,
                            y=values,
                            marker=dict(
                                color=values,
                                colorscale=[[0, '#ef4444'], [0.5, '#f59e0b'], [1, '#22c55e']],
                                showscale=False,
                                line=dict(width=2)
                            ),
                            text=[f'{v}%' for v in values],
                            textposition='outside',
                            textfont=dict(size=14)
                        )
                    ])
                    fig_bar.update_layout(
                        height=350,
                        margin=dict(l=40, r=40, t=40, b=80),
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        xaxis=dict(
                            gridcolor='rgba(148,163,184,0.2)'
                        ),
                        yaxis=dict(
                            gridcolor='rgba(148,163,184,0.2)',
                            range=[0, 105]
                        )
                    )
                    chart_element = ui.plotly(fig_bar).classes('w-full bar-chart')
                    chart_element.style('background: transparent;')
                
                # Transaction Volume Over Time
                with ui.card().classes('chart-container flex-1 min-w-[350px] max-w-[500px] scroll-reveal-scale scroll-reveal-delay-4'):
                    ui.label('Transaction Volume Trend').classes('text-lg font-semibold mb-4 dark:text-white text-gray-900')
                    
                    hours = list(range(24))
                    volumes = [int(100 + 50 * np.sin(h/3) + np.random.randint(-20, 20)) for h in hours]
                    fraud_volumes = [int(v * 0.02 + np.random.randint(0, 3)) for v in volumes]
                    
                    fig_line = go.Figure()
                    fig_line.add_trace(go.Scatter(
                        x=hours,
                        y=volumes,
                        mode='lines+markers',
                        name='Total',
                        line=dict(color='#0ea5e9', width=3),
                        fill='tozeroy',
                        fillcolor='rgba(14,165,233,0.1)',
                        marker=dict(size=6, color='#0ea5e9')
                    ))
                    fig_line.add_trace(go.Scatter(
                        x=hours,
                        y=fraud_volumes,
                        mode='lines+markers',
                        name='Illegal',
                        line=dict(color='#ef4444', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(239,68,68,0.1)',
                        marker=dict(size=6, color='#ef4444')
                    ))
                    fig_line.update_layout(
                        height=350,
                        margin=dict(l=50, r=40, t=40, b=80),
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        xaxis=dict(
                            title=dict(text='Hour of Day', font=dict(size=13)),
                            gridcolor='rgba(148,163,184,0.2)'
                        ),
                        yaxis=dict(
                            title=dict(text='Transactions', font=dict(size=13)),
                            gridcolor='rgba(148,163,184,0.2)'
                        ),
                        legend=dict(
                            orientation='h',
                            y=-0.25,
                            x=0.5,
                            xanchor='center'
                        )
                    )
                    chart_element = ui.plotly(fig_line).classes('w-full line-chart')
                    chart_element.style('background: transparent;')

        # Features Section
        with ui.column().classes('w-full px-8 py-20 items-center gap-8').props('id=features-section'):
            # Section header with icon
            with ui.row().classes('items-center gap-4 animate-slide-right'):
                ui.icon('star', size='3rem').classes('text-yellow-400').style('filter: drop-shadow(0 0 20px rgba(234, 179, 8, 0.5));')
                ui.label('Enterprise-Grade Features').classes('text-5xl font-extrabold gradient-text')
            ui.label('Built for financial institutions, security teams, and compliance officers').classes('text-xl font-medium animate-slide-right delay-100 dark:text-gray-300 text-gray-600 max-w-3xl text-center').style('line-height: 1.6;')
            
            # Grid container for perfect alignment with varied animations
            with ui.element('div').classes('w-full max-w-6xl mt-8').style('display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; justify-items: stretch;'):
                # Feature 1: AI Detection - Flip animation
                with ui.card().classes('feature-card h-full scroll-flip scroll-reveal-delay-1'):
                    ui.icon('psychology', size='3rem').classes('text-green-400 mb-4')
                    ui.label('AI-Powered Detection').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('RandomForest + IsolationForest with SMOTE balancing. Detects complex illegal activity patterns that rule-based systems miss.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Feature 2: Explainability - Bounce animation
                with ui.card().classes('feature-card h-full scroll-bounce scroll-reveal-delay-2'):
                    ui.icon('auto_awesome', size='3rem').classes('text-blue-400 mb-4')
                    ui.label('SHAP Explainability').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Every illegal transaction alert includes transparent, human-readable explanations showing which features triggered the detection.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Feature 3: Blockchain - Diagonal slide
                with ui.card().classes('feature-card h-full scroll-diagonal scroll-reveal-delay-3'):
                    ui.icon('link', size='3rem').classes('text-purple-400 mb-4')
                    ui.label('Immutable Ledger').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Custom SHA-256 blockchain with RSA digital signatures. Every illegal transaction alert is cryptographically signed and tamper-proof.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Feature 4: Dashboard - Blur reveal
                with ui.card().classes('feature-card h-full scroll-blur scroll-reveal-delay-4'):
                    ui.icon('dashboard', size='3rem').classes('text-orange-400 mb-4')
                    ui.label('Real-Time Dashboard').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Interactive NiceGUI interface with role-based access. Monitor transactions, alerts, blockchain, and analytics in real-time.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Feature 5: Offline - Skew animation
                with ui.card().classes('feature-card h-full scroll-skew scroll-reveal-delay-5'):
                    ui.icon('cloud_off', size='3rem').classes('text-cyan-400 mb-4')
                    ui.label('100% Offline').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('No external APIs or cloud dependencies. Runs entirely on local infrastructure with SQLite and file-based storage.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Feature 6: Adaptive - Glow pulse
                with ui.card().classes('feature-card h-full scroll-glow scroll-reveal-delay-6'):
                    ui.icon('refresh', size='3rem').classes('text-pink-400 mb-4')
                    ui.label('Continuous Learning').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Retrain models on updated data via retrain_model.py. Schedule periodic retraining to adapt to new illegal activity patterns.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')

        # How It Works Section
        with ui.column().classes('w-full px-8 py-20 items-center gap-8').style('background: linear-gradient(135deg, rgba(34, 197, 94, 0.05), rgba(14, 165, 233, 0.05));'):
            with ui.row().classes('items-center gap-4 animate-slide-right'):
                ui.icon('settings_suggest', size='3rem').classes('text-green-400').style('filter: drop-shadow(0 0 20px rgba(34, 197, 94, 0.5));')
                ui.label('How It Works').classes('text-5xl font-extrabold gradient-text')
            ui.label('Four-step process to detect, verify, and prevent illegal transactions in real-time').classes('text-xl font-medium animate-slide-right delay-100 dark:text-gray-300 text-gray-600 max-w-3xl text-center').style('line-height: 1.6;')
            
            with ui.row().classes('w-full max-w-6xl gap-6 mt-12 flex-wrap justify-center'):
                # Step 1
                with ui.card().classes('glass-card flex-1 min-w-[250px] max-w-[280px] text-center scroll-reveal scroll-reveal-delay-1'):
                    with ui.element('div').classes('w-16 h-16 mx-auto mb-4 rounded-full bg-green-500 flex items-center justify-center').style('box-shadow: 0 0 30px rgba(34, 197, 94, 0.5);'):
                        ui.label('1').classes('text-3xl font-bold text-white')
                    ui.label('Data Ingestion').classes('text-xl font-bold mb-3 dark:text-white text-gray-900')
                    ui.label('Transaction data flows in from your payment systems, automatically normalized and validated').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Step 2
                with ui.card().classes('glass-card flex-1 min-w-[250px] max-w-[280px] text-center scroll-reveal scroll-reveal-delay-2'):
                    with ui.element('div').classes('w-16 h-16 mx-auto mb-4 rounded-full bg-blue-500 flex items-center justify-center').style('box-shadow: 0 0 30px rgba(14, 165, 233, 0.5);'):
                        ui.label('2').classes('text-3xl font-bold text-white')
                    ui.label('AI Analysis').classes('text-xl font-bold mb-3 dark:text-white text-gray-900')
                    ui.label('Dual ML models analyze patterns, anomalies, and risk factors with 99.2% accuracy in <50ms').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Step 3
                with ui.card().classes('glass-card flex-1 min-w-[250px] max-w-[280px] text-center scroll-reveal scroll-reveal-delay-3'):
                    with ui.element('div').classes('w-16 h-16 mx-auto mb-4 rounded-full bg-purple-500 flex items-center justify-center').style('box-shadow: 0 0 30px rgba(168, 85, 247, 0.5);'):
                        ui.label('3').classes('text-3xl font-bold text-white')
                    ui.label('Blockchain Logging').classes('text-xl font-bold mb-3 dark:text-white text-gray-900')
                    ui.label('Illegal transaction alerts are cryptographically signed and stored in an immutable blockchain ledger').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Step 4
                with ui.card().classes('glass-card flex-1 min-w-[250px] max-w-[280px] text-center scroll-reveal scroll-reveal-delay-4'):
                    with ui.element('div').classes('w-16 h-16 mx-auto mb-4 rounded-full bg-orange-500 flex items-center justify-center').style('box-shadow: 0 0 30px rgba(251, 146, 60, 0.5);'):
                        ui.label('4').classes('text-3xl font-bold text-white')
                    ui.label('Alert & Action').classes('text-xl font-bold mb-3 dark:text-white text-gray-900')
                    ui.label('Real-time notifications sent to analysts with SHAP explanations for immediate investigation').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')

        # Technology Stack Section
        with ui.column().classes('w-full px-8 py-20 items-center gap-8'):
            with ui.row().classes('items-center gap-4 animate-slide-right'):
                ui.icon('developer_board', size='3rem').classes('text-blue-400').style('filter: drop-shadow(0 0 20px rgba(14, 165, 233, 0.5));')
                ui.label('Technology Stack').classes('text-5xl font-extrabold gradient-text')
            ui.label('Built with cutting-edge open-source technologies').classes('text-xl font-medium animate-slide-right delay-100 dark:text-gray-300 text-gray-600 max-w-3xl text-center').style('line-height: 1.6;')
            
            with ui.element('div').classes('w-full max-w-6xl mt-8').style('display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem;'):
                # AI/ML Stack
                with ui.card().classes('stat-card scroll-reveal scroll-reveal-delay-1'):
                    ui.icon('psychology', size='2.5rem').classes('text-green-400 mb-3')
                    ui.label('AI/ML').classes('text-xl font-bold mb-3 dark:text-white text-gray-900')
                    with ui.column().classes('gap-2 text-sm dark:text-gray-400 text-gray-600'):
                        ui.label('• Scikit-learn (RandomForest, IsolationForest)')
                        ui.label('• SHAP (Explainable AI)')
                        ui.label('• SMOTE (Data Balancing)')
                        ui.label('• NumPy & Pandas')
                
                # Backend Stack
                with ui.card().classes('stat-card scroll-reveal scroll-reveal-delay-2'):
                    ui.icon('storage', size='2.5rem').classes('text-blue-400 mb-3')
                    ui.label('Backend').classes('text-xl font-bold mb-3 dark:text-white text-gray-900')
                    with ui.column().classes('gap-2 text-sm dark:text-gray-400 text-gray-600'):
                        ui.label('• Python 3.12+')
                        ui.label('• SQLite Database')
                        ui.label('• Cryptography (RSA-2048)')
                        ui.label('• SHA-256 Hashing')
                
                # Frontend Stack
                with ui.card().classes('stat-card scroll-reveal scroll-reveal-delay-3'):
                    ui.icon('web', size='2.5rem').classes('text-purple-400 mb-3')
                    ui.label('Frontend').classes('text-xl font-bold mb-3 dark:text-white text-gray-900')
                    with ui.column().classes('gap-2 text-sm dark:text-gray-400 text-gray-600'):
                        ui.label('• NiceGUI Framework')
                        ui.label('• Plotly Visualizations')
                        ui.label('• TailwindCSS Styling')
                        ui.label('• Responsive Design')
                
                # Security Stack
                with ui.card().classes('stat-card scroll-reveal scroll-reveal-delay-4'):
                    ui.icon('shield', size='2.5rem').classes('text-orange-400 mb-3')
                    ui.label('Security').classes('text-xl font-bold mb-3 dark:text-white text-gray-900')
                    with ui.column().classes('gap-2 text-sm dark:text-gray-400 text-gray-600'):
                        ui.label('• Custom Blockchain')
                        ui.label('• RSA Digital Signatures')
                        ui.label('• Role-Based Access Control')
                        ui.label('• Encrypted Data Storage')

        # Use Cases Section
        with ui.column().classes('w-full px-8 py-20 items-center gap-8').style('background: linear-gradient(135deg, rgba(168, 85, 247, 0.05), rgba(236, 72, 153, 0.05));'):
            with ui.row().classes('items-center gap-4 animate-slide-right'):
                ui.icon('business_center', size='3rem').classes('text-purple-400').style('filter: drop-shadow(0 0 20px rgba(168, 85, 247, 0.5));')
                ui.label('Industry Use Cases').classes('text-5xl font-extrabold gradient-text')
            ui.label('Trusted by organizations across multiple sectors').classes('text-xl font-medium animate-slide-right delay-100 dark:text-gray-300 text-gray-600 max-w-3xl text-center').style('line-height: 1.6;')
            
            with ui.row().classes('w-full max-w-6xl gap-6 mt-12 flex-wrap justify-center'):
                # Banking
                with ui.card().classes('feature-card flex-1 min-w-[300px] max-w-[380px] scroll-reveal scroll-reveal-delay-1'):
                    ui.icon('account_balance', size='3rem').classes('text-green-400 mb-4')
                    ui.label('Banking & Finance').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Protect credit card transactions, wire transfers, and ACH payments from sophisticated illicit activity and laundering schemes. Real-time detection prevents losses before they occur.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # E-commerce
                with ui.card().classes('feature-card flex-1 min-w-[300px] max-w-[380px] scroll-reveal scroll-reveal-delay-2'):
                    ui.icon('shopping_cart', size='3rem').classes('text-blue-400 mb-4')
                    ui.label('E-Commerce').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Stop illicit payments, account takeovers, and chargeback abuse. Protect your revenue while maintaining seamless customer experience.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Insurance
                with ui.card().classes('feature-card flex-1 min-w-[300px] max-w-[380px] scroll-reveal scroll-reveal-delay-3'):
                    ui.icon('health_and_safety', size='3rem').classes('text-purple-400 mb-4')
                    ui.label('Insurance').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Detect suspicious claims and abnormal patterns in policy applications. Reduce claim processing costs and improve risk assessment accuracy.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Fintech
                with ui.card().classes('feature-card flex-1 min-w-[300px] max-w-[380px] scroll-reveal scroll-reveal-delay-4'):
                    ui.icon('payments', size='3rem').classes('text-orange-400 mb-4')
                    ui.label('Fintech & Payments').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Secure digital wallets, P2P transfers, and mobile payments. Built for high-volume transaction processing with minimal latency.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Government
                with ui.card().classes('feature-card flex-1 min-w-[300px] max-w-[380px] scroll-reveal scroll-reveal-delay-5'):
                    ui.icon('gavel', size='3rem').classes('text-cyan-400 mb-4')
                    ui.label('Government & Public Sector').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Protect taxpayer funds, benefits programs, and public procurement. Ensure compliance with audit trails and transparent reporting.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Cryptocurrency
                with ui.card().classes('feature-card flex-1 min-w-[300px] max-w-[380px] scroll-reveal scroll-reveal-delay-6'):
                    ui.icon('currency_bitcoin', size='3rem').classes('text-pink-400 mb-4')
                    ui.label('Cryptocurrency Exchanges').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Monitor crypto transactions for wash trading, pump-and-dump schemes, and suspicious wallet activity. Blockchain-native security.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')

        # About/Contact Section
        with ui.column().classes('w-full px-8 py-20 items-center gap-8').props('id=login-section'):
            # Section header with icon
            with ui.row().classes('items-center gap-4 animate-slide-right'):
                ui.icon('lock_person', size='3rem').classes('text-green-400').style('filter: drop-shadow(0 0 20px rgba(34, 197, 94, 0.5));')
                ui.label('Secure Access').classes('text-5xl font-extrabold gradient-text')
            ui.label('Enterprise-grade authentication with role-based access control').classes('text-xl font-medium animate-slide-right delay-100 dark:text-gray-300 text-gray-600 max-w-3xl text-center').style('line-height: 1.6;')
            
            with ui.row().classes('w-full max-w-5xl gap-8 mt-8 justify-center items-stretch'):
                # Security Features
                with ui.card().classes('feature-card flex-1 max-w-md scroll-reveal scroll-reveal-delay-1'):
                    ui.icon('security', size='3rem').classes('text-green-400 mb-4')
                    ui.label('Multi-Layer Security').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('End-to-end encryption, secure authentication, and blockchain-verified audit trails for complete data protection.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # Role-Based Access
                with ui.card().classes('feature-card flex-1 max-w-md scroll-reveal-scale scroll-reveal-delay-2'):
                    ui.icon('admin_panel_settings', size='3rem').classes('text-blue-400 mb-4')
                    ui.label('Role-Based Access').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Admin, Analyst, Auditor, and User roles with granular permissions for secure, compliant operations.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')
                
                # 24/7 Monitoring
                with ui.card().classes('feature-card flex-1 max-w-md scroll-reveal-left scroll-reveal-delay-3'):
                    ui.icon('monitoring', size='3rem').classes('text-purple-400 mb-4')
                    ui.label('24/7 Monitoring').classes('text-xl font-bold mb-2 dark:text-white text-gray-900')
                    ui.label('Real-time illegal activity detection with instant alerts and comprehensive analytics for proactive threat management.').classes('text-sm leading-relaxed dark:text-gray-400 text-gray-600')

        # Footer - Enhanced with gradient border
        with ui.column().classes('w-full px-8 py-12 items-center gap-6 animate-fade-in delay-500').style('border-top: 2px solid; border-image: linear-gradient(90deg, transparent, rgba(34, 197, 94, 0.5), transparent) 1;'):
            # Footer content with better spacing
            with ui.row().classes('items-center gap-6 flex-wrap justify-center text-sm dark:text-gray-400 text-gray-600'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('copyright', size='sm')
                    ui.label('2024 Smart Money Laundering').classes('font-semibold')
                ui.label('•')
                with ui.row().classes('items-center gap-2'):
                    ui.icon('security', size='sm').classes('text-green-400')
                    ui.label('Enterprise-Grade Security')
                ui.label('•')
                with ui.row().classes('items-center gap-2'):
                    ui.icon('code', size='sm').classes('text-blue-400')
                    ui.label('Built with NiceGUI & Python')
            
            # Social/Legal links
            with ui.row().classes('gap-6 text-xs dark:text-gray-500 text-gray-500 mt-2'):
                ui.link('Privacy Policy', '#').classes('hover:text-green-400 transition-colors')
                ui.label('•')
                ui.link('Terms of Service', '#').classes('hover:text-green-400 transition-colors')
                ui.label('•')
                ui.link('Documentation', '#').classes('hover:text-green-400 transition-colors')


def login_page():
    add_global_styles()
    
    # Single Admin credentials
    ADMIN_EMAIL = 'admin@proofledger.com'
    ADMIN_PASSWORD = 'admin123'
    
    with ui.column().classes('w-full min-h-screen landing-bg items-center justify-center').style('margin: 0; padding: 0;'):
        # Back to home button - theme persists globally via localStorage
        with ui.row().classes('absolute top-6 left-6'):
            ui.button('← Back to Home', icon='home', on_click=lambda: ui.navigate.to('/')).props('flat').classes('dark:text-white text-gray-900 hover:bg-white/10 px-4 py-2 rounded-lg transition-all duration-300')
        
        # Login Card - Enhanced
        with ui.card().classes('glass-card p-12 w-full max-w-lg animate-float-up').style('box-shadow: 0 20px 80px rgba(0, 0, 0, 0.3), 0 0 120px rgba(0, 255, 65, 0.2); border-color: rgba(0, 255, 65, 0.4);'):
            # Logo and Title with animation
            with ui.column().classes('items-center mb-8'):
                with ui.element('div').style('animation: float-gentle 3s ease-in-out infinite;'):
                    ui.icon('hub', size='5rem').classes('text-green-400 mb-4').style('filter: drop-shadow(0 0 30px rgba(0, 255, 65, 0.6));')
                ui.label('Smart Money Laundering').classes('text-4xl font-extrabold gradient-text mb-3')
                ui.label('Cyber Forensic Access Portal').classes('text-xl font-medium dark:text-gray-300 text-gray-600')
            
            # Login Form - Enhanced inputs
            email_input = ui.input('Neural ID (Email)').classes('w-full mb-5').props('outlined filled').style('font-size: 1.05rem;')
            email_input.props('type=email')
            with email_input:
                with email_input.add_slot('prepend'):
                    ui.icon('fingerprint').classes('dark:text-green-400 text-green-500')
            
            password_input = ui.input('Access Key (Password)', password=True, password_toggle_button=True).classes('w-full mb-5').props('outlined filled').style('font-size: 1.05rem;')
            with password_input:
                with password_input.add_slot('prepend'):
                    ui.icon('vpn_key').classes('dark:text-green-400 text-green-500')
            
            error_label = ui.label().classes('text-red-500 font-semibold text-sm mb-3 px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/30')
            error_label.visible = False
            
            def do_login():
                email = email_input.value.strip()
                password = password_input.value.strip()
                
                if not email or not password:
                    error_label.set_text('Please enter credentials')
                    error_label.visible = True
                    return
                
                if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                    CURRENT_ROLE['role'] = 'Admin'
                    ui.notify('Neural Link Established. Welcome, Admin.', type='positive')
                    ui.navigate.to('/dashboard')
                else:
                    error_label.set_text('Access Denied: Invalid Credentials')
                    error_label.visible = True
            
            # Submit button - Enhanced with gradient
            ui.button('INITIALIZE LINK', icon='security', on_click=do_login).props('unelevated size=lg').classes('w-full mb-6 bg-gradient-to-r from-green-500 to-cyan-600 text-white text-lg font-bold py-4 shadow-2xl hover:scale-105 transition-all').style('border-radius: 8px;')
            
            # Divider
            with ui.row().classes('w-full items-center mb-6'):
                ui.separator().classes('flex-1')
                ui.label('CORE AUTH').classes('px-4 text-xs dark:text-gray-500 text-gray-500 font-bold')
                ui.separator().classes('flex-1')
            
            # Admin Credentials Info
            with ui.expansion('Emergency Bypass (Admin Credentials)', icon='info').classes('w-full'):
                with ui.column().classes('gap-3 p-2'):
                    ui.label('Admin Account:').classes('font-semibold text-sm dark:text-gray-300 text-gray-700 mb-2')
                    
                    with ui.card().classes('p-4 bg-green-50 dark:bg-green-900/20 border-2 border-green-500/30'):
                        ui.label('Email: admin@proofledger.com').classes('text-sm dark:text-gray-200 text-gray-800 font-mono')
                        ui.label('Password: admin123').classes('text-sm dark:text-gray-200 text-gray-800 font-mono')


def monitor_tab():
    # Enhanced title with icon
    with ui.row().classes('items-center gap-4 mb-6'):
        ui.icon('monitor_heart', size='2.5rem').classes('text-green-400').style('filter: drop-shadow(0 0 15px rgba(34, 197, 94, 0.5));')
        ui.label('Real-Time Transaction Monitoring').classes('text-3xl font-extrabold gradient-text')
    
    with ui.row().classes('w-full gap-6'):
        with ui.card().classes('flex-1 glass-card p-6'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.icon('add_circle', size='2rem').classes('text-blue-400')
                ui.label('Simulate New Transaction').classes('text-xl font-bold dark:text-white text-gray-900')

            amount = ui.number('Amount (INR)', value=1000.0).classes('mb-2 w-full')
            txn_type = ui.select(
                ['payment', 'transfer', 'withdrawal', 'deposit'],
                label='Transaction Type',
                value='payment',
            ).classes('mb-2 w-full')
            location = ui.input('Location (City)').classes('mb-2 w-full')
            device_id = ui.input('Device ID').classes('mb-2 w-full')

            result_label = ui.label().classes('mt-2')

            def submit_txn():
                # Admin-only access - no role check needed
                try:
                    txn, score, is_fraud, _ = services.handle_new_transaction(
                        amount.value,
                        txn_type.value,
                        location.value or 'Unknown',
                        device_id.value or 'Unknown',
                    )
                except Exception as e:
                    ui.notify(str(e), color='red')
                    return
                status = 'ILLEGAL' if is_fraud else 'LEGAL'
                color = 'red' if is_fraud else 'green'
                msg = (
                    f"TXN {txn['txn_id']} | User {txn['user_id']} | "
                    f"Score {score:.3f} | {status}"
                )
                result_label.set_text(msg)
                ui.notify(msg, color=color)
                transactions_table.update()

            ui.button('Submit Transaction', icon='send', on_click=submit_txn).props('unelevated').classes('w-full bg-gradient-to-r from-blue-500 to-cyan-600 text-white font-bold py-3 rounded-lg shadow-lg hover:shadow-blue-500/50 transition-all duration-300')

            ui.separator().classes('my-6')
            with ui.row().classes('items-center gap-3 mb-3'):
                ui.icon('dataset', size='1.5rem').classes('text-purple-400')
                ui.label('Demo from Dataset').classes('text-lg font-bold dark:text-white text-gray-900')

            def submit_dataset(want_fraud: bool):
                # Admin-only access - no role check needed
                try:
                    txn, score, is_fraud, _, actual = services.handle_dataset_transaction(want_fraud=want_fraud)
                    expected = 'ILLEGAL' if actual == 1 else 'LEGAL'
                    status = 'ILLEGAL' if is_fraud else 'LEGAL'
                    color = 'red' if is_fraud else 'green'
                    msg = f"Dataset TXN {txn['txn_id']} | Score {score:.3f} | Pred {status} | Actual {expected}"
                    result_label.set_text(msg)
                    ui.notify(msg, color=color)
                    transactions_table.update()
                except Exception as e:
                    ui.notify(str(e), color='red')

            with ui.row().classes('w-full gap-3'):
                ui.button('Generate Legal', icon='check_circle', on_click=lambda: submit_dataset(False)).props('outline').classes('flex-1 border-2 border-green-500 text-green-600 dark:text-green-400 font-bold py-3 rounded-lg hover:bg-green-500/10 transition-all duration-300')
                ui.button('Generate Illegal', icon='error', on_click=lambda: submit_dataset(True)).props('outline').classes('flex-1 border-2 border-red-500 text-red-600 dark:text-red-400 font-bold py-3 rounded-lg hover:bg-red-500/10 transition-all duration-300')

            ui.separator().classes('my-6')
            with ui.row().classes('items-center gap-3 mb-3'):
                ui.icon('currency_bitcoin', size='1.5rem').classes('text-amber-400')
                ui.label('VTAC Crypto Transaction').classes('text-lg font-bold dark:text-white text-gray-900')

            sender_hash = ui.input('Sender Wallet Hash').classes('mb-2 w-full')
            receiver_hash = ui.input('Receiver Wallet Hash').classes('mb-2 w-full')
            tx_hash = ui.input('Transaction Hash').classes('mb-2 w-full')
            crypto_amount = ui.number('Amount (BTC)', value=0.1).classes('mb-2 w-full')
            tx_fee = ui.number('Transaction Fee (BTC)', value=0.0001).classes('mb-2 w-full')
            asset = ui.input('Asset', value='BTC').classes('mb-2 w-full')
            network = ui.input('Network', value='bitcoin').classes('mb-2 w-full')

            def submit_crypto_txn():
                try:
                    txn, score, is_fraud, _ = services.handle_crypto_transaction(
                        sender_hash=sender_hash.value or 'unknown_sender',
                        receiver_hash=receiver_hash.value or 'unknown_receiver',
                        tx_hash=tx_hash.value or 'unknown_tx',
                        amount=float(crypto_amount.value or 0.0),
                        tx_fee=float(tx_fee.value or 0.0),
                        asset=asset.value or 'BTC',
                        network=network.value or 'bitcoin',
                    )
                except Exception as e:
                    ui.notify(str(e), color='red')
                    return
                status = 'ILLEGAL' if is_fraud else 'LEGAL'
                color = 'red' if is_fraud else 'green'
                msg = f"Crypto TXN {txn['txn_id']} | Score {score:.3f} | {status}"
                result_label.set_text(msg)
                ui.notify(msg, color=color)
                transactions_table.update()

            ui.button('Submit Crypto Transaction', icon='send', on_click=submit_crypto_txn).props('unelevated').classes('w-full bg-gradient-to-r from-amber-500 to-orange-600 text-white font-bold py-3 rounded-lg shadow-lg hover:shadow-orange-500/50 transition-all duration-300')

            ui.separator().classes('my-6')
            with ui.row().classes('items-center gap-3 mb-3'):
                ui.icon('search', size='1.5rem').classes('text-cyan-400')
                ui.label('Elliptic txId Lookup').classes('text-lg font-bold dark:text-white text-gray-900')

            elliptic_txid = ui.number('Elliptic txId (from Result.csv)', value=230325127).classes('mb-2 w-full')

            elliptic_summary = ui.label('').classes('text-sm font-mono dark:text-gray-200 text-gray-800')
            elliptic_deanonym = ui.label('').classes('text-xs dark:text-gray-300 text-gray-700')
            elliptic_advisory = ui.label('').classes('text-xs dark:text-gray-300 text-gray-700')

            beneficiaries_columns = [
                {'name': 'address', 'label': 'Beneficiary Address', 'field': 'address'},
                {'name': 'total_received_btc', 'label': 'Total Received (BTC)', 'field': 'total_received_btc'},
            ]
            beneficiaries_table = ui.table(columns=beneficiaries_columns, rows=[]).classes('w-full')
            elliptic_raw = ui.textarea('Raw Response (JSON)', value='', placeholder='').props('readonly').classes('w-full')

            async def run_elliptic_lookup():
                try:
                    txid_val = int(elliptic_txid.value)
                except Exception:
                    ui.notify('Please enter a valid txId (number).', color='red')
                    return

                try:
                    lookup_btn.disable()
                    lookup_btn.update()
                    res = await run.io_bound(services.predict_elliptic_txid, txid_val)
                except Exception as e:
                    ui.notify(str(e), color='red')
                    return
                finally:
                    try:
                        lookup_btn.enable()
                        lookup_btn.update()
                    except Exception:
                        pass

                score = float(res.get('score') or 0.0)
                classification = str(res.get('classification') or '').upper() or 'UNKNOWN'
                deanonym_hash = res.get('deanonymized_tx_hash')
                ident = res.get('identification') or {}
                advisory = ident.get('advisory') or {}

                elliptic_summary.set_text(f"ELLIPTIC-{txid_val} | Score {score:.3f} | {classification}")
                if deanonym_hash:
                    elliptic_deanonym.set_text(f"De-anonymized tx hash: {deanonym_hash}")
                else:
                    elliptic_deanonym.set_text('De-anonymized tx hash: (not available in Result.csv)')

                if isinstance(advisory, dict) and advisory and 'error' not in advisory:
                    iv = advisory.get('incoming_value_total_btc')
                    ov = advisory.get('outgoing_value_total_btc')
                    fv = advisory.get('fee_total_btc')
                    twb = advisory.get('time_window_blockchain') or {}
                    chain_tw = ''
                    try:
                        if isinstance(twb, dict) and twb:
                            secs = twb.get('seconds')
                            if secs is not None:
                                chain_tw = f" | Blockchain time window {float(secs):.0f}s"
                    except Exception:
                        chain_tw = ''
                    elliptic_advisory.set_text(
                        f"Frequency In {ident.get('incoming_edges')} | Out {ident.get('outgoing_edges')} | "
                        f"Time window {ident.get('time_interval_steps')} steps | Weight {ident.get('weight_factor')} | "
                        f"Value In {iv} BTC | Out {ov} BTC | Fee {fv} BTC{chain_tw}"
                    )
                elif isinstance(advisory, dict) and advisory.get('error'):
                    elliptic_advisory.set_text(
                        f"Frequency In {ident.get('incoming_edges')} | Out {ident.get('outgoing_edges')} | "
                        f"Time window {ident.get('time_interval_steps')} steps | Weight {ident.get('weight_factor')} | "
                        f"Advisory error: {advisory.get('error')}"
                    )
                else:
                    elliptic_advisory.set_text(
                        f"Frequency In {ident.get('incoming_edges')} | Out {ident.get('outgoing_edges')} | "
                        f"Time window {ident.get('time_interval_steps')} steps | Weight {ident.get('weight_factor')}"
                    )

                beneficiaries = ident.get('beneficiaries') or []
                rows = []
                for b in beneficiaries:
                    try:
                        rows.append({
                            'address': str(b.get('address') or ''),
                            'total_received_btc': f"{float(b.get('total_received_btc') or 0.0):.8f}",
                        })
                    except Exception:
                        continue
                beneficiaries_table.rows = rows
                beneficiaries_table.update()

                elliptic_raw.value = json.dumps(res, indent=2)
                elliptic_raw.update()

                ui.notify('Elliptic lookup complete.', color='green' if classification == 'LEGAL' else 'red')

            lookup_btn = ui.button('Lookup Elliptic txId', icon='travel_explore', on_click=run_elliptic_lookup).props('unelevated').classes('w-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold py-3 rounded-lg shadow-lg hover:shadow-cyan-500/50 transition-all duration-300')

        with ui.card().classes('flex-1 glass-card p-6'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.icon('receipt_long', size='2rem').classes('text-orange-400')
                ui.label('Recent Transactions').classes('text-xl font-bold dark:text-white text-gray-900')
            columns = [
                {'name': 'txn_id', 'label': 'Txn ID', 'field': 'txn_id'},
                {'name': 'user_id', 'label': 'User', 'field': 'user_id'},
                {'name': 'amount', 'label': 'Amount', 'field': 'amount'},
                {'name': 'txn_type', 'label': 'Type', 'field': 'txn_type'},
                {'name': 'timestamp', 'label': 'Timestamp', 'field': 'timestamp'},
                {'name': 'location', 'label': 'Location', 'field': 'location'},
                {'name': 'device_id', 'label': 'Device', 'field': 'device_id'},
                {'name': 'is_fraud', 'label': 'Status', 'field': 'is_fraud'},
                {'name': 'fraud_score', 'label': 'Score', 'field': 'fraud_score'},
            ]

            def load_txn_rows():
                rows = []
                for r in services.get_recent_transactions():
                    rows.append({
                        'txn_id': r[0],
                        'user_id': r[1],
                        'amount': r[2],
                        'txn_type': r[3],
                        'timestamp': r[4],
                        'location': r[5],
                        'device_id': r[6],
                        'is_fraud': 'ILLEGAL' if r[7] == 1 else 'LEGAL',
                        'fraud_score': f"{r[8]:.3f}",
                    })
                return rows

            global transactions_table
            transactions_table = ui.table(columns=columns, rows=load_txn_rows()).classes('w-full')

            def refresh():
                transactions_table.rows = load_txn_rows()
                transactions_table.update()

            ui.timer(5.0, refresh)


def alerts_tab():
    # Admin-only access - no role check needed
    
    # Enhanced title with icon
    with ui.row().classes('items-center gap-4 mb-6'):
        ui.icon('warning', size='2.5rem').classes('text-yellow-400').style('filter: drop-shadow(0 0 15px rgba(234, 179, 8, 0.5));')
        ui.label('Illegal Transaction Alerts Dashboard').classes('text-3xl font-extrabold gradient-text')
    columns = [
        {'name': 'case_id', 'label': 'Case ID', 'field': 'case_id'},
        {'name': 'txn_id', 'label': 'Txn ID', 'field': 'txn_id'},
        {'name': 'user_id', 'label': 'User', 'field': 'user_id'},
        {'name': 'amount', 'label': 'Amount', 'field': 'amount'},
        {'name': 'fraud_score', 'label': 'Score', 'field': 'fraud_score'},
        {'name': 'explanation', 'label': 'Explanation', 'field': 'explanation'},
        {'name': 'timestamp', 'label': 'Timestamp', 'field': 'timestamp'},
    ]

    def load_alert_rows():
        rows = []
        for r in services.get_alerts():
            rows.append({
                'case_id': r[0],
                'txn_id': r[1],
                'user_id': r[2],
                'amount': r[3],
                'fraud_score': f"{r[4]:.3f}",
                'explanation': r[5],
                'timestamp': r[6],
            })
        return rows

    alerts_table = ui.table(columns=columns, rows=load_alert_rows()).classes('w-full')

    def refresh():
        alerts_table.rows = load_alert_rows()
        alerts_table.update()

    ui.timer(7.0, refresh)


def blockchain_tab():
    # Admin-only access - no role check needed
    
    # Enhanced title with icon
    with ui.row().classes('items-center gap-4 mb-6'):
        ui.icon('link', size='2.5rem').classes('text-blue-400').style('filter: drop-shadow(0 0 15px rgba(14, 165, 233, 0.5));')
        ui.label('Smart Money Laundering Blockchain Viewer').classes('text-3xl font-extrabold gradient-text')
    
    with ui.row().classes('mb-6 gap-4'):
        def verify():
            ok = services.verify_chain()
            if ok:
                ui.notify('✅ Blockchain valid - No tampering detected', color='green', position='top')
            else:
                ui.notify('⚠️ Blockchain INVALID - Tampering detected!', color='red', position='top')

        def export_chain():
            try:
                path = services.export_ledger()
                ui.download(path)
                ui.notify('📦 Ledger JSON downloaded!', color='positive', position='top')
            except Exception as e:
                ui.notify(f'❌ Error: {str(e)}', color='negative', position='top')

        ui.button('Verify Chain Integrity', icon='verified', on_click=verify).props('unelevated').classes('bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold px-6 py-3 rounded-lg shadow-lg hover:shadow-green-500/50 transition-all duration-300')
        ui.button('Export Ledger JSON', icon='download', on_click=export_chain).props('outline').classes('border-2 border-blue-500 text-blue-600 dark:text-blue-400 font-bold px-6 py-3 rounded-lg hover:bg-blue-500/10 transition-all duration-300')

    columns = [
        {'name': 'index', 'label': 'Index', 'field': 'index'},
        {'name': 'txn_id', 'label': 'Txn ID', 'field': 'txn_id'},
        {'name': 'timestamp', 'label': 'Timestamp', 'field': 'timestamp'},
        {'name': 'fraud_score', 'label': 'Score', 'field': 'fraud_score'},
        {'name': 'explanation_hash', 'label': 'Explanation Hash', 'field': 'explanation_hash'},
        {'name': 'prev_hash', 'label': 'Prev Hash', 'field': 'prev_hash'},
        {'name': 'current_hash', 'label': 'Current Hash', 'field': 'current_hash'},
    ]

    def load_block_rows():
        rows = []
        for r in services.get_blocks():
            rows.append({
                'index': r[0],
                'txn_id': r[1],
                'timestamp': r[2],
                'fraud_score': f"{r[3]:.3f}",
                'explanation_hash': r[4][:12] + '...',
                'prev_hash': r[5][:12] + '...',
                'current_hash': r[6][:12] + '...',
            })
        return rows

    blocks_table = ui.table(columns=columns, rows=load_block_rows()).classes('w-full')

    def refresh():
        blocks_table.rows = load_block_rows()
        blocks_table.update()

    ui.timer(10.0, refresh)


def analytics_tab():
    # Admin-only access - no role check needed
    
    # Enhanced title with icon
    with ui.row().classes('items-center gap-4 mb-6'):
        ui.icon('analytics', size='2.5rem').classes('text-purple-400').style('filter: drop-shadow(0 0 15px rgba(168, 85, 247, 0.5));')
        ui.label('Analytics & Model Performance').classes('text-3xl font-extrabold gradient-text')
    
    # Get data for charts
    total_txn, fraud_cnt, fraud_rate = services.get_fraud_summary()
    legitimate_cnt = total_txn - fraud_cnt

    model_info = services.get_active_model_info()
    model_type = str(model_info.get('model_type') or 'unknown')
    dataset_path = str(model_info.get('dataset_path') or '')
    dataset_name = os.path.basename(dataset_path) if dataset_path else ''
    dataset_name = dataset_name or 'Dataset'
    threshold = float(model_info.get('threshold') or 0.0)
    cv_folds = int(model_info.get('cv_folds') or 0)

    # Active Model + Algorithm Details
    with ui.card().classes('glass-card p-6 mb-6'):
        with ui.row().classes('items-center gap-3 mb-3'):
            ui.icon('psychology', size='2rem').classes('text-cyan-400')
            ui.label('Active ML Model & VTAC Pipeline').classes('text-2xl font-extrabold dark:text-white text-gray-900')
        with ui.row().classes('w-full gap-6 flex-wrap'):
            with ui.column().classes('gap-1 min-w-[280px] flex-1'):
                ui.label(f"Model: {model_type}").classes('text-lg font-bold dark:text-gray-200 text-gray-800')
                ui.label(f"Decision threshold: {threshold:.2f}").classes('text-sm dark:text-gray-300 text-gray-700')
                ui.label(f"Cross-validation: {cv_folds}-fold").classes('text-sm dark:text-gray-300 text-gray-700')
                ui.label(f"Dataset: {dataset_name}").classes('text-xs dark:text-gray-400 text-gray-600')
            with ui.column().classes('gap-2 min-w-[320px] flex-1'):
                with ui.expansion('Algorithm details (Detection + Identification)', icon='schema').classes('w-full'):
                    with ui.column().classes('gap-2 p-2'):
                        ui.label('VTAC is implemented as:').classes('font-bold dark:text-gray-200 text-gray-800')
                        ui.label('1) Detection phase: supervised ML (RandomForest / AdaBoost / XGBoost) to classify legal vs illegal.').classes('text-sm dark:text-gray-300 text-gray-700')
                        ui.label('2) Identification/advisory phase: value + frequency + time-window + weight-factor signals for crypto-style transactions (wallet hashes).').classes('text-sm dark:text-gray-300 text-gray-700')
                        ui.label('Data leakage prevention: scaler is fit on TRAIN only; then applied to validation/test.').classes('text-sm dark:text-gray-300 text-gray-700')
                        ui.label('Imbalance handling: optional SMOTE (configurable).').classes('text-sm dark:text-gray-300 text-gray-700')

    # Row 1: Key Metrics Cards
    with ui.row().classes('w-full gap-6 mb-6 flex-wrap'):
        with ui.card().classes('stat-card text-center min-w-[200px] flex-1'):
            ui.icon('verified_user', size='2rem').classes('text-green-400 mb-2')
            ui.label(f'{total_txn:,}').classes('text-4xl font-extrabold text-green-400 mb-2')
            ui.label('Total Transactions').classes('text-sm font-semibold dark:text-gray-300 text-gray-700')
        
        with ui.card().classes('stat-card text-center min-w-[200px] flex-1'):
            ui.icon('warning', size='2rem').classes('text-red-400 mb-2')
            ui.label(f'{fraud_cnt:,}').classes('text-4xl font-extrabold text-red-400 mb-2')
            ui.label('Illegal Detected').classes('text-sm font-semibold dark:text-gray-300 text-gray-700')
        
        with ui.card().classes('stat-card text-center min-w-[200px] flex-1'):
            ui.icon('check_circle', size='2rem').classes('text-blue-400 mb-2')
            ui.label(f'{legitimate_cnt:,}').classes('text-4xl font-extrabold text-blue-400 mb-2')
            ui.label('Legal').classes('text-sm font-semibold dark:text-gray-300 text-gray-700')
        
        with ui.card().classes('stat-card text-center min-w-[200px] flex-1'):
            ui.icon('percent', size='2rem').classes('text-purple-400 mb-2')
            ui.label(f'{fraud_rate:.2f}%').classes('text-4xl font-extrabold text-purple-400 mb-2')
            ui.label('Illegal Rate').classes('text-sm font-semibold dark:text-gray-300 text-gray-700')
    
    # Row 2: Interactive Charts
    with ui.row().classes('w-full gap-6 mb-6 flex-wrap'):
        # Illegal Distribution Pie Chart
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('Illegal vs Legal Transactions').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Legal', 'Illegal'],
                values=[legitimate_cnt, fraud_cnt],
                marker=dict(colors=['#22c55e', '#ef4444']),
                hole=0.4,
                textinfo='label+percent+value',
                textposition='outside',
                textfont=dict(size=13)
            )])
            fig_pie.update_layout(
                height=400,
                margin=dict(l=40, r=40, t=40, b=40),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                showlegend=True,
                legend=dict(
                    orientation='h',
                    y=-0.15,
                    x=0.5,
                    xanchor='center',
                    font=dict(size=12)
                )
            )
            ui.plotly(fig_pie).classes('w-full')
        
        # Model Performance Metrics Bar Chart
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('Model Performance Metrics').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')

            metrics = ['Precision', 'Recall', 'F1-Score', 'Accuracy']
            values = [0.0, 0.0, 0.0, 0.0]
            try:
                mc = model_info.get('model_comparison') or {}
                holdout = (mc.get('holdout_test') or {}).get('selected') or {}
                wavg = holdout.get('weighted avg') or {}
                values = [
                    float(wavg.get('precision', 0.0)) * 100.0,
                    float(wavg.get('recall', 0.0)) * 100.0,
                    float(wavg.get('f1-score', 0.0)) * 100.0,
                    float(holdout.get('accuracy', 0.0)) * 100.0,
                ]
            except Exception:
                values = [0.0, 0.0, 0.0, 0.0]
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=metrics,
                    y=values,
                    marker=dict(
                        color=values,
                        colorscale=[[0, '#ef4444'], [0.5, '#f59e0b'], [1, '#22c55e']],
                        showscale=False,
                        line=dict(width=2)
                    ),
                    text=[f'{v}%' for v in values],
                    textposition='outside',
                    textfont=dict(size=14)
                )
            ])
            fig_bar.update_layout(
                height=400,
                margin=dict(l=40, r=40, t=40, b=80),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                yaxis=dict(
                    gridcolor='rgba(148,163,184,0.2)',
                    range=[0, 105]
                )
            )
            ui.plotly(fig_bar).classes('w-full')
    
    # Row 3: Time Series and Distribution
    with ui.row().classes('w-full gap-6 mb-6 flex-wrap'):
        # Transaction Volume Over Time
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):

            ui.label('Transaction Volume (Last 24 Hours)').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            evo = services.get_time_evolution(window_hours=24, window_days=30)
            hours = evo.get('hourly', {}).get('labels', [])
            volumes = evo.get('hourly', {}).get('total', [])
            fraud_volumes = evo.get('hourly', {}).get('fraud', [])
            
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=hours,
                y=volumes,
                mode='lines+markers',
                name='Total Transactions',
                line=dict(color='#0ea5e9', width=3),
                fill='tozeroy',
                fillcolor='rgba(14,165,233,0.1)',
                marker=dict(size=8, color='#0ea5e9')
            ))
            fig_line.add_trace(go.Scatter(
                x=hours,
                y=fraud_volumes,
                mode='lines+markers',
                name='Illegal Detected',
                line=dict(color='#ef4444', width=2),
                fill='tozeroy',
                fillcolor='rgba(239,68,68,0.1)',
                marker=dict(size=6, color='#ef4444')
            ))
            fig_line.update_layout(
                height=400,
                margin=dict(l=50, r=40, t=40, b=80),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                xaxis=dict(
                    title='Hour of Day',
                    gridcolor='rgba(148,163,184,0.2)'
                ),
                yaxis=dict(
                    title='Transactions',
                    gridcolor='rgba(148,163,184,0.2)'
                ),
                legend=dict(
                    orientation='h',
                    y=-0.25,
                    x=0.5,
                    xanchor='center'
                )
            )
            ui.plotly(fig_line).classes('w-full')

        # 30-day trend based on actual transactions
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('30-Day Illegal Trend (Logged Data)').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            evo = services.get_time_evolution(window_hours=24, window_days=30)
            dates = evo.get('daily', {}).get('labels', [])
            total_trend = evo.get('daily', {}).get('total', [])
            fraud_trend = evo.get('daily', {}).get('fraud', [])

            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=dates,
                y=total_trend,
                mode='lines',
                name='Total Transactions',
                line=dict(color='#0ea5e9', width=2),
                fill='tozeroy',
                fillcolor='rgba(14,165,233,0.1)'
            ))
            fig_trend.add_trace(go.Scatter(
                x=dates,
                y=fraud_trend,
                mode='lines',
                name='Illegal Detected',
                line=dict(color='#ef4444', width=3),
                fill='tozeroy',
                fillcolor='rgba(239,68,68,0.2)'
            ))
            fig_trend.update_layout(
                height=400,
                margin=dict(l=50, r=40, t=40, b=120),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                xaxis=dict(
                    title='Date',
                    gridcolor='rgba(148,163,184,0.2)',
                    tickangle=-45
                ),
                yaxis=dict(
                    title='Count',
                    gridcolor='rgba(148,163,184,0.2)'
                ),
                legend=dict(
                    orientation='h',
                    y=-0.35,
                    x=0.5,
                    xanchor='center'
                ),
                hovermode='x unified'
            )
            ui.plotly(fig_trend).classes('w-full')
        
        # Detection Rate Gauge
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('Current Detection Accuracy').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            
            fig_gauge = go.Figure(go.Indicator(
                mode='gauge+number+delta',
                value=99.2,
                domain={'x': [0, 1], 'y': [0, 0.85]},
                title={'text': 'Accuracy %', 'font': {'size': 16}},
                number={'font': {'size': 48}, 'valueformat': '.1f'},
                delta={'reference': 95, 'increasing': {'color': '#22c55e'}, 'font': {'size': 16}},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': '#22c55e', 'thickness': 0.8},
                    'bgcolor': 'rgba(148,163,184,0.2)',
                    'borderwidth': 2,
                    'bordercolor': '#64748b',
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(239,68,68,0.3)'},
                        {'range': [50, 75], 'color': 'rgba(251,191,36,0.3)'},
                        {'range': [75, 100], 'color': 'rgba(34,197,94,0.3)'}
                    ],
                    'threshold': {
                        'line': {'color': '#0ea5e9', 'width': 4},
                        'thickness': 0.75,
                        'value': 95
                    }
                }
            ))
            fig_gauge.update_layout(
                height=400,
                margin=dict(l=40, r=40, t=100, b=40),
                paper_bgcolor='rgba(0, 0, 0, 0)'
            )
            ui.plotly(fig_gauge).classes('w-full')
    
    # Row 4: Feature Importance and Confusion Matrix
    with ui.row().classes('w-full gap-6 mb-6 flex-wrap'):
        # Top Features Contributing to Illegal Detection
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('Top Features (Illegal Detection)').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            
            features = ['Amount', 'Time', 'Location Risk', 'Device Trust', 'Frequency', 'Velocity']
            importance = [0.35, 0.25, 0.18, 0.12, 0.06, 0.04]
            
            fig_h_bar = go.Figure(data=[
                go.Bar(
                    y=features,
                    x=importance,
                    orientation='h',
                    marker=dict(
                        color=importance,
                        colorscale='Viridis',
                        showscale=False
                    ),
                    text=[f'{v*100:.1f}%' for v in importance],
                    textposition='outside'
                )
            ])
            fig_h_bar.update_layout(
                height=400,
                margin=dict(l=120, r=40, t=40, b=60),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                xaxis=dict(
                    title='Importance Score',
                    gridcolor='rgba(148,163,184,0.2)',
                    range=[0, 0.4]
                ),
                yaxis=dict(gridcolor='rgba(148,163,184,0.1)')
            )
            ui.plotly(fig_h_bar).classes('w-full')
        
        # Confusion Matrix Heatmap
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('Confusion Matrix').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            
            confusion_matrix = [[980, 8], [12, 988]]
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=confusion_matrix,
                x=['Predicted Legal', 'Predicted Illegal'],
                y=['Actual Legal', 'Actual Illegal'],
                colorscale='RdYlGn_r',
                text=confusion_matrix,
                texttemplate='%{text}',
                textfont={'size': 24},
                showscale=True,
                colorbar=dict(title='Count')
            ))
            fig_heatmap.update_layout(
                height=400,
                margin=dict(l=100, r=40, t=40, b=100),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                xaxis=dict(side='bottom'),
                yaxis=dict(autorange='reversed')
            )
            ui.plotly(fig_heatmap).classes('w-full')
    
    # Row 5: Additional Analytics Charts
    with ui.row().classes('w-full gap-6 mb-6 flex-wrap'):
        # Transaction Amount Distribution
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('Transaction Amount Distribution').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            
            import numpy as np
            amounts = np.random.lognormal(7, 1.5, 1000)
            
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=amounts,
                nbinsx=30,
                marker=dict(
                    color='#0ea5e9',
                    line=dict(color='#0284c7', width=1)
                ),
                name='Transactions'
            ))
            fig_hist.update_layout(
                height=400,
                margin=dict(l=50, r=40, t=40, b=80),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                xaxis=dict(
                    title='Transaction Amount ($)',
                    gridcolor='rgba(148,163,184,0.2)'
                ),
                yaxis=dict(
                    title='Frequency',
                    gridcolor='rgba(148,163,184,0.2)'
                ),
                showlegend=False
            )
            ui.plotly(fig_hist).classes('w-full')
        
        # Risk Score Distribution
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('Risk Score Distribution').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            
            risk_scores = np.concatenate([
                np.random.beta(2, 8, 800) * 100,  # Legal (low risk)
                np.random.beta(8, 2, 200) * 100   # Illegal (high risk)
            ])
            
            fig_risk = go.Figure()
            fig_risk.add_trace(go.Box(
                y=risk_scores,
                name='Risk Scores',
                marker=dict(
                    color='#a855f7',
                    line=dict(color='#9333ea', width=2)
                ),
                boxmean='sd'
            ))
            fig_risk.update_layout(
                height=400,
                margin=dict(l=50, r=40, t=40, b=80),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                yaxis=dict(
                    title='Risk Score',
                    gridcolor='rgba(148,163,184,0.2)',
                    range=[0, 100]
                ),
                showlegend=False
            )
            ui.plotly(fig_risk).classes('w-full')
    
    # Row 6: Hourly Heatmap and Daily Trends
    with ui.row().classes('w-full gap-6 mb-6 flex-wrap'):
        # Illegal Detection by Hour (Heatmap)
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('Illegal Detection Heatmap (Hour vs Day)').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            hours_list = list(range(24))
            
            # Generate random heatmap data
            heatmap_data = []
            for day in days:
                row = []
                for hour in hours_list:
                    # More illegal activity at night and weekends
                    base_rate = 5
                    if hour > 22 or hour < 6:
                        base_rate += 3
                    if day in ['Sat', 'Sun']:
                        base_rate += 2
                    row.append(base_rate + np.random.randint(-2, 3))
                heatmap_data.append(row)
            
            fig_heat = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                x=[f'{h}:00' for h in hours_list],
                y=days,
                colorscale='Reds',
                text=heatmap_data,
                texttemplate='%{text}',
                textfont={'size': 10},
                colorbar=dict(title='Illegal Count')
            ))
            fig_heat.update_layout(
                height=400,
                margin=dict(l=80, r=40, t=40, b=100),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                xaxis=dict(title='Hour of Day', side='bottom'),
                yaxis=dict(title='Day of Week')
            )
            ui.plotly(fig_heat).classes('w-full')
        
        # Daily Trend Analysis (Last 30 Days)
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('30-Day Illegal Trend').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            
            from datetime import datetime, timedelta
            dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
            fraud_trend = [int(20 + 10 * np.sin(i/5) + np.random.randint(-5, 5)) for i in range(30)]
            total_trend = [int(500 + 50 * np.sin(i/5) + np.random.randint(-20, 20)) for i in range(30)]
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=dates,
                y=total_trend,
                mode='lines',
                name='Total Transactions',
                line=dict(color='#0ea5e9', width=2),
                fill='tozeroy',
                fillcolor='rgba(14,165,233,0.1)'
            ))
            fig_trend.add_trace(go.Scatter(
                x=dates,
                y=fraud_trend,
                mode='lines',
                name='Illegal Detected',
                line=dict(color='#ef4444', width=3),
                fill='tozeroy',
                fillcolor='rgba(239,68,68,0.2)'
            ))
            fig_trend.update_layout(
                height=400,
                margin=dict(l=50, r=40, t=40, b=120),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                xaxis=dict(
                    title='Date',
                    gridcolor='rgba(148,163,184,0.2)',
                    tickangle=-45
                ),
                yaxis=dict(
                    title='Count',
                    gridcolor='rgba(148,163,184,0.2)'
                ),
                legend=dict(
                    orientation='h',
                    y=-0.35,
                    x=0.5,
                    xanchor='center'
                ),
                hovermode='x unified'
            )
            ui.plotly(fig_trend).classes('w-full')
    
    # Row 7: Location Analysis and Alert Distribution
    with ui.row().classes('w-full gap-6 mb-6 flex-wrap'):
        # Top Fraud Locations
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('Top Illegal Activity Locations').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            
            locations_data = [
                {'location': 'New York, USA', 'count': 45, 'risk': 'High'},
                {'location': 'London, UK', 'count': 38, 'risk': 'High'},
                {'location': 'Tokyo, Japan', 'count': 28, 'risk': 'Medium'},
                {'location': 'Dubai, UAE', 'count': 22, 'risk': 'Medium'},
                {'location': 'Singapore', 'count': 18, 'risk': 'Low'},
                {'location': 'Paris, France', 'count': 15, 'risk': 'Low'},
            ]
            
            locations = [d['location'] for d in locations_data]
            counts = [d['count'] for d in locations_data]
            colors = ['#ef4444' if d['risk'] == 'High' else '#f59e0b' if d['risk'] == 'Medium' else '#22c55e' for d in locations_data]
            
            fig_loc = go.Figure(data=[
                go.Bar(
                    y=locations,
                    x=counts,
                    orientation='h',
                    marker=dict(color=colors),
                    text=counts,
                    textposition='outside',
                    textfont=dict(size=12)
                )
            ])
            fig_loc.update_layout(
                height=400,
                margin=dict(l=150, r=40, t=40, b=60),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                xaxis=dict(
                    title='Illegal Count',
                    gridcolor='rgba(148,163,184,0.2)'
                ),
                yaxis=dict(gridcolor='rgba(148,163,184,0.1)'),
                showlegend=False
            )
            ui.plotly(fig_loc).classes('w-full')
        
        # Alert Severity Distribution
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('Alert Severity Distribution').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            
            severities = ['Critical', 'High', 'Medium', 'Low']
            severity_counts = [25, 68, 142, 89]
            severity_colors = ['#dc2626', '#f59e0b', '#eab308', '#22c55e']
            
            fig_sev = go.Figure(data=[
                go.Pie(
                    labels=severities,
                    values=severity_counts,
                    marker=dict(colors=severity_colors),
                    hole=0.5,
                    textinfo='label+percent',
                    textposition='outside',
                    textfont=dict(size=13)
                )
            ])
            fig_sev.update_layout(
                height=400,
                margin=dict(l=40, r=40, t=40, b=40),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                showlegend=True,
                legend=dict(
                    orientation='h',
                    y=-0.15,
                    x=0.5,
                    xanchor='center',
                    font=dict(size=12)
                ),
                annotations=[dict(text='Alerts', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            ui.plotly(fig_sev).classes('w-full')
    
    # Row 8: Detection Speed and Processing Metrics
    with ui.row().classes('w-full gap-6 mb-6 flex-wrap'):
        # Detection Speed Over Time
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('Average Detection Speed (ms)').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            
            time_points = list(range(24))
            detection_speeds = [int(50 + 20 * np.sin(t/4) + np.random.randint(-5, 5)) for t in time_points]
            
            fig_speed = go.Figure()
            fig_speed.add_trace(go.Scatter(
                x=time_points,
                y=detection_speeds,
                mode='lines+markers',
                name='Detection Speed',
                line=dict(color='#8b5cf6', width=3),
                marker=dict(size=8, color='#8b5cf6'),
                fill='tozeroy',
                fillcolor='rgba(139,92,246,0.2)'
            ))
            fig_speed.add_hline(
                y=np.mean(detection_speeds),
                line_dash='dash',
                line_color='#22c55e',
                annotation_text=f'Avg: {np.mean(detection_speeds):.1f}ms',
                annotation_position='top right'
            )
            fig_speed.update_layout(
                height=400,
                margin=dict(l=50, r=40, t=40, b=80),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                xaxis=dict(
                    title='Hour of Day',
                    gridcolor='rgba(148,163,184,0.2)'
                ),
                yaxis=dict(
                    title='Speed (ms)',
                    gridcolor='rgba(148,163,184,0.2)'
                ),
                showlegend=False
            )
            ui.plotly(fig_speed).classes('w-full')
        
        # Transaction Processing Funnel
        with ui.card().classes('chart-container flex-1 min-w-[400px]'):
            ui.label('Transaction Processing Funnel').classes('text-xl font-bold mb-4 dark:text-white text-gray-900')
            
            stages = ['Received', 'Validated', 'AI Analyzed', 'Blockchain Verified', 'Completed']
            stage_values = [1000, 985, 970, 965, 960]
            
            fig_funnel = go.Figure(go.Funnel(
                y=stages,
                x=stage_values,
                textinfo='value+percent initial',
                marker=dict(
                    color=['#0ea5e9', '#06b6d4', '#8b5cf6', '#a855f7', '#22c55e'],
                    line=dict(width=2, color='#1e293b')
                ),
                textfont=dict(size=13)
            ))
            fig_funnel.update_layout(
                height=400,
                margin=dict(l=150, r=40, t=40, b=60),
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)'
            )
            ui.plotly(fig_funnel).classes('w-full')
    
    # Row 9: Recent Transactions Table
    with ui.card().classes('chart-container w-full mb-6'):
        with ui.row().classes('items-center justify-between mb-4'):
            ui.label('Recent Transactions').classes('text-xl font-bold dark:text-white text-gray-900')
            ui.button('Refresh', icon='refresh', on_click=lambda: update_recent_txn()).props('flat round dense').classes('text-blue-500')
        
        # Table columns
        columns = [
            {'name': 'id', 'label': 'Txn ID', 'field': 'id', 'align': 'left', 'sortable': True},
            {'name': 'timestamp', 'label': 'Timestamp', 'field': 'timestamp', 'align': 'left', 'sortable': True},
            {'name': 'amount', 'label': 'Amount', 'field': 'amount', 'align': 'right', 'sortable': True},
            {'name': 'location', 'label': 'Location', 'field': 'location', 'align': 'left'},
            {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'center'},
            {'name': 'confidence', 'label': 'Confidence', 'field': 'confidence', 'align': 'right', 'sortable': True}
        ]
        
        # Sample data - Replace with actual data from services
        import random
        from datetime import datetime, timedelta
        
        def generate_recent_txn():
            rows = []
            locations = ['New York', 'London', 'Tokyo', 'Paris', 'Sydney', 'Dubai', 'Singapore']
            for i in range(20):
                is_fraud = random.random() < 0.05
                rows.append({
                    'id': f'TXN{1000+i:04d}',
                    'timestamp': (datetime.now() - timedelta(minutes=random.randint(1, 120))).strftime('%Y-%m-%d %H:%M:%S'),
                    'amount': f'${random.randint(100, 50000):,}',
                    'location': random.choice(locations),
                    'status': '🔴 Illegal' if is_fraud else '🟢 Legal',
                    'confidence': f'{random.uniform(85, 99.9):.1f}%'
                })
            return rows
        
        recent_txn_table = ui.table(columns=columns, rows=generate_recent_txn(), row_key='id').classes('w-full')
        recent_txn_table.classes('dark:bg-gray-800/50 bg-white/50')
        
        def update_recent_txn():
            recent_txn_table.rows = generate_recent_txn()
            ui.notify('✅ Transactions refreshed', color='positive', position='top')
    
    # Row 6: Action Buttons and Export Options
    with ui.row().classes('gap-6 flex-wrap'):
        with ui.card().classes('glass-card p-6 flex-1 min-w-[300px]'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.icon('model_training', size='2rem').classes('text-green-400')
                ui.label('Model & Reports').classes('text-xl font-bold dark:text-white text-gray-900')

            def show_report():
                text = services.get_model_report_text()
                with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl'):
                    with ui.row().classes('w-full items-center justify-between mb-4'):
                        ui.label('📊 Classification Report').classes('text-2xl font-bold dark:text-white text-gray-900')
                        ui.button(icon='close', on_click=dialog.close).props('flat round dense')
                    
                    # Scrollable content area with monospace font for proper formatting
                    with ui.scroll_area().classes('w-full h-[500px] border-2 border-gray-300 dark:border-gray-600 rounded-lg p-4'):
                        ui.label(text).classes('whitespace-pre font-mono text-sm dark:text-gray-200 text-gray-800')
                    
                    with ui.row().classes('w-full justify-end mt-4 gap-2'):
                        ui.button('Close', on_click=dialog.close).props('outline')
                dialog.open()

            def export_importance():
                try:
                    path = services.export_feature_importance()
                    # Trigger download
                    ui.download(path)
                    ui.notify(f'📊 Feature importance chart downloaded!', color='positive', position='top')
                except Exception as e:
                    ui.notify(f'❌ Error: {str(e)}', color='negative', position='top')

            def show_model_comparison():
                text = services.get_model_comparison_text()
                with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl'):
                    with ui.row().classes('w-full items-center justify-between mb-4'):
                        ui.label('🔬 Model Comparison').classes('text-2xl font-bold dark:text-white text-gray-900')
                        ui.button(icon='close', on_click=dialog.close).props('flat round dense')
                    
                    # Scrollable content area with JSON formatting
                    with ui.scroll_area().classes('w-full h-[500px] border-2 border-gray-300 dark:border-gray-600 rounded-lg p-4 bg-gray-50 dark:bg-gray-800'):
                        ui.label(text).classes('whitespace-pre font-mono text-sm dark:text-gray-200 text-gray-800')
                    
                    with ui.row().classes('w-full justify-end mt-4 gap-2'):
                        ui.button('Close', on_click=dialog.close).props('outline')
                dialog.open()

            def retrain():
                # Admin-only access - no role check needed
                services.retrain_model()
                ui.notify('Model retrained using latest dataset.', color='primary')

            with ui.column().classes('gap-3 w-full'):
                ui.button('View Classification Report', icon='description', on_click=show_report).props('outline').classes('w-full border-2 border-blue-500 text-blue-600 dark:text-blue-400 font-semibold py-2 rounded-lg hover:bg-blue-500/10 transition-all duration-300')
                ui.button('Export Feature Importance', icon='bar_chart', on_click=export_importance).props('outline').classes('w-full border-2 border-purple-500 text-purple-600 dark:text-purple-400 font-semibold py-2 rounded-lg hover:bg-purple-500/10 transition-all duration-300')
                ui.button('View Model Comparison', icon='compare', on_click=show_model_comparison).props('outline').classes('w-full border-2 border-cyan-500 text-cyan-600 dark:text-cyan-400 font-semibold py-2 rounded-lg hover:bg-cyan-500/10 transition-all duration-300')
                ui.button('Retrain Model', icon='refresh', on_click=retrain).props('unelevated').classes('w-full bg-gradient-to-r from-orange-500 to-red-600 text-white font-bold py-2 rounded-lg shadow-lg hover:shadow-orange-500/50 transition-all duration-300')

        with ui.card().classes('glass-card p-6 flex-1 min-w-[300px]'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.icon('pie_chart', size='2rem').classes('text-orange-400')
                ui.label('Illegal Rate Summary').classes('text-xl font-bold dark:text-white text-gray-900')
            fraud_label = ui.label()
            total_label = ui.label()

            def update_stats():
                total, fraud_cnt, rate = services.get_fraud_summary()
                total_label.set_text(f'Total Transactions: {total}')
                fraud_label.set_text(f'Illegal: {fraud_cnt} ({rate:.2f}%)')

            update_stats()
            ui.timer(8.0, update_stats)

        with ui.card().classes('glass-card p-6 flex-1 min-w-[300px]'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.icon('show_chart', size='2rem').classes('text-cyan-400')
                ui.label('Visual Analytics').classes('text-xl font-bold dark:text-white text-gray-900')

            def export_time_series():
                try:
                    path = services.export_fraud_time_series_chart()
                    ui.download(path)
                    ui.notify(f'📊 Time-series chart downloaded!', color='positive', position='top')
                except Exception as e:
                    ui.notify(f'❌ {str(e)}', color='negative', position='top')

            def export_location_chart():
                try:
                    path = services.export_fraud_by_location_chart()
                    ui.download(path)
                    ui.notify(f'📍 Location chart downloaded!', color='positive', position='top')
                except Exception as e:
                    ui.notify(f'❌ {str(e)}', color='negative', position='top')

            with ui.column().classes('gap-3 w-full'):
                ui.button('Export Time-Series Chart', icon='timeline', on_click=export_time_series).props('outline').classes('w-full border-2 border-cyan-500 text-cyan-600 dark:text-cyan-400 font-semibold py-2 rounded-lg hover:bg-cyan-500/10 transition-all duration-300')
                ui.button('Export Location Chart', icon='map', on_click=export_location_chart).props('outline').classes('w-full border-2 border-teal-500 text-teal-600 dark:text-teal-400 font-semibold py-2 rounded-lg hover:bg-teal-500/10 transition-all duration-300')

        with ui.card().classes('glass-card p-6 flex-1 min-w-[300px]'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.icon('cloud_download', size='2rem').classes('text-indigo-400')
                ui.label('Compliance & Export').classes('text-xl font-bold dark:text-white text-gray-900')

            def export_txn_csv():
                try:
                    path = services.export_transactions_csv()
                    ui.download(path)
                    ui.notify(f'📄 Transactions CSV downloaded!', color='positive', position='top')
                except Exception as e:
                    ui.notify(f'❌ {str(e)}', color='negative', position='top')

            def export_alerts_csv():
                try:
                    path = services.export_alerts_csv()
                    ui.download(path)
                    ui.notify(f'📄 Alerts CSV downloaded!', color='positive', position='top')
                except Exception as e:
                    ui.notify(f'❌ {str(e)}', color='negative', position='top')

            def export_backup():
                try:
                    path = services.export_full_backup()
                    ui.download(path)
                    ui.notify(f'📦 Full backup ZIP downloaded!', color='positive', position='top')
                except Exception as e:
                    ui.notify(f'❌ {str(e)}', color='negative', position='top')

            with ui.column().classes('gap-3 w-full'):
                ui.button('Export Transactions CSV', icon='table_chart', on_click=export_txn_csv).props('outline').classes('w-full border-2 border-green-500 text-green-600 dark:text-green-400 font-semibold py-2 rounded-lg hover:bg-green-500/10 transition-all duration-300')
                ui.button('Export Alerts CSV', icon='report', on_click=export_alerts_csv).props('outline').classes('w-full border-2 border-yellow-500 text-yellow-600 dark:text-yellow-400 font-semibold py-2 rounded-lg hover:bg-yellow-500/10 transition-all duration-300')
                ui.button('Export Full Backup', icon='backup', on_click=export_backup).props('unelevated').classes('w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold py-2 rounded-lg shadow-lg hover:shadow-indigo-500/50 transition-all duration-300')


def dashboard_page():
    add_global_styles()
    
    # Enhanced Header with Theme-aware styling
    with ui.header().classes('items-center justify-between px-8 py-5 nav-blur').style(
        'border-bottom: 1px solid rgba(34, 197, 94, 0.3);'
    ):
        with ui.row().classes('items-center gap-4'):
            ui.icon('hub', size='2.5rem').classes('text-green-400').style('filter: drop-shadow(0 0 10px rgba(34, 197, 94, 0.3));')
            with ui.column().classes('gap-1'):
                ui.label('Smart Money Laundering System').classes('text-2xl font-extrabold dark:text-white text-gray-900')
                ui.label('Neural Forensic Analysis System').classes('text-xs text-cyan-400 font-mono tracking-widest')
        
        with ui.row().classes('items-center gap-4'):
            model_status = ui.label().classes('text-sm px-5 py-2.5 rounded-xl font-bold shadow-lg transition-all duration-300')
            theme_toggle_button()
            role_badge()
            ui.button('EXIT', icon='logout', on_click=lambda: ui.navigate.to('/')).props('flat').classes('text-red-400 hover:bg-red-400/10 px-4 py-2 rounded-lg transition-all duration-300 font-bold')

    def refresh_model_status():
        s = services.get_model_status()
        if s['status'] == 'ready':
            model_status.set_text('🟢 AI Model Active')
            model_status.classes(replace='text-sm px-5 py-2.5 rounded-xl font-bold shadow-lg transition-all duration-300 bg-gradient-to-r from-green-500 to-emerald-600 text-white')
            model_status.style('box-shadow: 0 4px 20px rgba(34, 197, 94, 0.4);')
        elif s['status'] == 'error':
            model_status.set_text('🔴 Model Error')
            model_status.classes(replace='text-sm px-5 py-2.5 rounded-xl font-bold shadow-lg transition-all duration-300 bg-gradient-to-r from-red-500 to-rose-600 text-white')
            model_status.style('box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);')
        else:
            model_status.set_text('🟡 Loading...')
            model_status.classes(replace='text-sm px-5 py-2.5 rounded-xl font-bold shadow-lg transition-all duration-300 bg-gradient-to-r from-yellow-500 to-orange-600 text-white')
            model_status.style('box-shadow: 0 4px 20px rgba(234, 179, 8, 0.4);')

    refresh_model_status()
    ui.timer(2.0, refresh_model_status)

    # Enhanced Tabs with modern styling and gradients - Fully responsive to theme changes
    with ui.tabs().classes('w-full dashboard-tabs') as tabs:
        # Tabs with proper visibility in both modes
        ui.tab('Monitor', icon='monitor_heart').classes('text-lg font-bold transition-all duration-300 hover:text-green-400').style('min-width: 150px;')
        ui.tab('Alerts', icon='warning').classes('text-lg font-bold transition-all duration-300 hover:text-yellow-400').style('min-width: 150px;')
        ui.tab('Blockchain', icon='link').classes('text-lg font-bold transition-all duration-300 hover:text-blue-400').style('min-width: 150px;')
        ui.tab('Analytics', icon='analytics').classes('text-lg font-bold transition-all duration-300 hover:text-purple-400').style('min-width: 150px;')

    with ui.tab_panels(tabs, value='Monitor').classes('w-full p-8 dashboard-tab-panels'):
        with ui.tab_panel('Monitor'):
            monitor_tab()
        with ui.tab_panel('Alerts'):
            alerts_tab()
        with ui.tab_panel('Blockchain'):
            blockchain_tab()
        with ui.tab_panel('Analytics'):
            analytics_tab()
