"""
    Smart Money Laundering System - Interactive Animations Page
Showcases how the blockchain illegal activity detection system works with 2D and 3D visualizations
"""

from nicegui import ui
import plotly.graph_objects as go
import numpy as np
from app import ui as app_ui


def create_animations_page():
    """Create the animations demonstration page"""
    
    # Ensure global styles are added for theme consistency
    app_ui.add_global_styles()
    
    # Enhanced page styling with dynamic theme support
    ui.add_head_html("""
        <style>
            .animations-page {
                position: relative;
                overflow-x: hidden;
            }
            
            .dark .animations-page {
                background: #050505;
            }
            
            /* Step Card Styling - Unified with ui.py */
            .step-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(34, 197, 94, 0.2);
                border-radius: 16px;
                padding: 20px;
                transition: all 0.3s ease;
            }
            
            .dark .step-card {
                background: rgba(15, 23, 42, 0.6);
                border-color: rgba(34, 197, 94, 0.3);
            }
            
            .step-card:hover {
                transform: translateY(-5px);
                border-color: rgba(34, 197, 94, 0.6);
                box-shadow: 0 10px 30px rgba(34, 197, 94, 0.1);
            }

            .section-title {
                background: linear-gradient(90deg, #22c55e, #0ea5e9, #a855f7);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-family: 'Space Grotesk', sans-serif;
                font-weight: 900;
                letter-spacing: -1px;
            }
            
            .step-number {
                width: 40px;
                height: 40px;
                background: #22c55e;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: #fff;
                box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
                animation: numberPulse 2s infinite;
            }
            
            @keyframes numberPulse {
                0%, 100% { box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3); transform: scale(1); }
                50% { box-shadow: 0 8px 25px rgba(34, 197, 94, 0.5); transform: scale(1.05); }
            }
            
            .flow-animation {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .flow-animation:hover {
                transform: scale(1.2) rotate(5deg);
                filter: drop-shadow(0 0 15px currentColor);
            }

            /* Theme-aware text for pipeline stages */
            .pipeline-text {
                font-weight: 700;
                font-size: 15px;
                color: #1e293b;
            }
            .dark .pipeline-text {
                color: #f1f5f9;
            }
        </style>
    """)
    
    # Main container with animated background
    with ui.element('div').classes('animations-page w-full min-h-screen landing-bg p-8 animations-page-active'):
        # Force dark mode on this page
        ui.run_javascript("document.documentElement.classList.add('dark'); if (document.body) document.body.classList.add('dark');")
        
        # Header with back button
        with ui.row().classes('w-full items-center justify-between mb-12 animate-fade-in'):
            with ui.row().classes('items-center gap-6'):
                ui.button('← Back to Home', on_click=lambda: ui.navigate.to('/')).props('flat').classes(
                    'dark:text-white text-gray-900 hover:bg-green-500/10 px-6 py-3 rounded-xl text-lg font-bold transition-all duration-300 border-2 border-green-500/30'
                )
                
                with ui.column().classes('gap-1'):
                    ui.label('Smart Money Laundering System Core').classes('text-5xl font-extrabold section-title')
                    ui.label('Cyber Forensic Visualizations & AI Neural Simulations').classes('text-xl dark:text-gray-400 text-gray-600 font-medium')
            
            ui.icon('hub', size='4rem').classes('text-green-500 animate-pulse').style(
                'filter: drop-shadow(0 0 30px rgba(34, 197, 94, 0.6));'
            )
        
        # Section 1: 2D Animation
        with ui.card().classes('glass-card w-full mb-12 p-10 scroll-reveal'):
            ui.label('📡 Neural Data Flow: Transaction Analysis').classes('text-4xl font-bold dark:text-white text-gray-900 mb-8')
            
            create_2d_animation()
        
        # Section 2: 3D Animation
        with ui.card().classes('glass-card w-full mb-12 p-10 scroll-reveal'):
            ui.label('⛓️ 3D Core: Decentralized Forensic Ledger').classes('text-4xl font-bold dark:text-white text-gray-900 mb-8')

            
            create_3d_animation()
        
        # Section 3: VTAC Pipeline Animation
        with ui.card().classes('glass-card w-full mb-12 p-10 scroll-reveal'):
            ui.label('🧭 VTAC 3D Pipeline: Detection → Identification').classes('text-4xl font-bold dark:text-white text-gray-900 mb-8')
            
            create_vtac_pipeline_animation()
        
        # Section 4: VTAC Advisory Graph
        with ui.card().classes('glass-card w-full mb-12 p-10 scroll-reveal'):
            ui.label('🕸️ VTAC Advisory Graph: Illegal Transaction Tracking').classes('text-4xl font-bold dark:text-white text-gray-900 mb-8')
            
            create_vtac_advisory_graph_animation()
        
        # Section 5: Mobile Bitcoin Transfer Animation
        with ui.card().classes('glass-card w-full mb-12 p-10 scroll-reveal'):
            ui.label('📱 P2P Bitcoin Transfer Visualization').classes('text-4xl font-bold dark:text-white text-gray-900 mb-8')
            
            create_mobile_bitcoin_animation()
        
        # Section 6: Attack Detection Animation
        with ui.card().classes('glass-card w-full mb-12 p-10 scroll-reveal'):
            ui.label('🚨 Real-Time Attack Detection & Admin Alert').classes('text-4xl font-bold dark:text-white text-gray-900 mb-8')
            
            create_attack_detection_animation()
        
        # Section 7: Process Flow Steps
        with ui.card().classes('glass-card w-full mb-12 p-10 scroll-reveal'):
            ui.label('⚡ How Smart Money Laundering Works').classes('text-4xl font-bold dark:text-white text-gray-900 mb-8')
            
            create_process_flow()



def create_2d_animation():
    """Create 2D animation showing transaction flow through the system"""
    
    # Container for 2D animation
    with ui.column().classes('w-full gap-8'):
        
        # Description
        ui.label('Watch how transactions flow through our AI-powered illegal activity detection system').classes(
            'text-xl dark:text-gray-300 text-gray-600 mb-4'
        )
        
        # Animation stages container
        with ui.row().classes('w-full justify-around items-center flex-wrap gap-6 mb-8'):
            
            # Stage 1: Transaction Initiated
            with ui.column().classes('items-center gap-3 step-card'):
                with ui.element('div').classes('step-number'):
                    ui.label('1')
                ui.icon('payments', size='3rem').classes('text-blue-400 flow-animation')
                ui.label('Transaction').classes('text-lg font-bold dark:text-white text-gray-900')
                ui.label('Initiated').classes('text-sm dark:text-gray-400 text-gray-500')
            
            # Connection arrow
            ui.icon('arrow_forward', size='2rem').classes('text-green-400 flow-animation')
            
            # Stage 2: AI Analysis
            with ui.column().classes('items-center gap-3 step-card'):
                with ui.element('div').classes('step-number'):
                    ui.label('2')
                ui.icon('psychology', size='3rem').classes('text-purple-400 flow-animation')
                ui.label('AI Analysis').classes('text-lg font-bold dark:text-white text-gray-900')
                ui.label('Real-time Scan').classes('text-sm dark:text-gray-400 text-gray-500')
            
            # Connection arrow
            ui.icon('arrow_forward', size='2rem').classes('text-green-400 flow-animation')
            
            # Stage 3: Risk Assessment
            with ui.column().classes('items-center gap-3 step-card'):
                with ui.element('div').classes('step-number'):
                    ui.label('3')
                ui.icon('verified_user', size='3rem').classes('text-yellow-400 flow-animation')
                ui.label('Risk Score').classes('text-lg font-bold dark:text-white text-gray-900')
                ui.label('Calculated').classes('text-sm dark:text-gray-400 text-gray-500')
            
            # Connection arrow
            ui.icon('arrow_forward', size='2rem').classes('text-green-400 flow-animation')
            
            # Stage 4: Blockchain Storage
            with ui.column().classes('items-center gap-3 step-card'):
                with ui.element('div').classes('step-number'):
                    ui.label('4')
                ui.icon('link', size='3rem').classes('text-cyan-400 flow-animation')
                ui.label('Blockchain').classes('text-lg font-bold dark:text-white text-gray-900')
                ui.label('Immutable Record').classes('text-sm dark:text-gray-400 text-gray-500')
            
            # Connection arrow
            ui.icon('arrow_forward', size='2rem').classes('text-green-400 flow-animation')
            
            # Stage 5: Decision
            with ui.column().classes('items-center gap-3 step-card'):
                with ui.element('div').classes('step-number'):
                    ui.label('5')
                ui.icon('check_circle', size='3rem').classes('text-green-400 flow-animation')
                ui.label('Approved').classes('text-lg font-bold dark:text-white text-gray-900')
                ui.label('or Flagged').classes('text-sm dark:text-gray-400 text-gray-500')
        
        # Interactive Plotly 2D Flow Chart
        create_interactive_2d_chart()


def create_interactive_2d_chart():
    """Create an interactive 2D Sankey diagram showing data flow"""
    
    # Get theme-aware colors
    is_dark = ui.dark_mode().value
    chart_colors = app_ui.get_chart_colors(is_dark)
    
    # Sankey diagram showing transaction flow
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=30,
            line=dict(color='#1e293b', width=2),
            label=[
                'Incoming Transactions',
                'AI Analysis',
                'Risk Assessment',
                'Low Risk',
                'High Risk',
                'Blockchain Storage',
                'Approved',
                'Flagged for Review'
            ],
            color=[
                '#3b82f6',  # Blue - Incoming
                '#8b5cf6',  # Purple - AI
                '#f59e0b',  # Orange - Risk Assessment
                '#22c55e',  # Green - Low Risk
                '#ef4444',  # Red - High Risk
                '#06b6d4',  # Cyan - Blockchain
                '#22c55e',  # Green - Approved
                '#ef4444'   # Red - Flagged
            ],
            customdata=[
                'All transactions enter here',
                'Machine learning analysis',
                'Risk score calculation',
                'Safe transactions',
                'Suspicious activity',
                'Immutable ledger',
                'Transaction completed',
                'Requires manual review'
            ],
            hovertemplate='%{label}<br>%{customdata}<extra></extra>'
        ),
        link=dict(
            source=[0, 1, 2, 2, 3, 4, 5, 5],
            target=[1, 2, 3, 4, 5, 5, 6, 7],
            value=[1000, 1000, 950, 50, 950, 50, 950, 50],
            color=[
                'rgba(59, 130, 246, 0.3)',
                'rgba(139, 92, 246, 0.3)',
                'rgba(34, 197, 94, 0.3)',
                'rgba(239, 68, 68, 0.3)',
                'rgba(34, 197, 94, 0.3)',
                'rgba(239, 68, 68, 0.3)',
                'rgba(34, 197, 94, 0.3)',
                'rgba(239, 68, 68, 0.3)'
            ],
            customdata=[
                '1000 transactions/sec',
                'Real-time processing',
                '95% pass initial check',
                '5% flagged as suspicious',
                'Low risk → Blockchain',
                'High risk → Blockchain',
                '95% approved automatically',
                '5% require review'
            ],
            hovertemplate='%{customdata}<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title={
            'text': 'Transaction Flow Analysis',
            'font': {'size': 24, 'color': chart_colors['text']},
            'x': 0.5,
            'xanchor': 'center'
        },
        font=dict(size=14, color=chart_colors['text']),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        height=600,
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    ui.plotly(fig).classes('w-full')


def create_interactive_3d_chart():
    """Create an interactive 3D blockchain visualization with blocks and chains"""
    
    # Get theme-aware colors
    is_dark = ui.dark_mode().value
    chart_colors = app_ui.get_chart_colors(is_dark)
    
    # Generate blockchain data - chain of blocks
    num_blocks = 20
    
    # Blocks positioned in a chain (linear arrangement)
    x_blocks = np.arange(num_blocks) * 4  # Spacing between blocks
    y_blocks = np.zeros(num_blocks)
    z_blocks = np.zeros(num_blocks)
    
    # Add some variation for visual interest
    y_blocks = np.sin(np.arange(num_blocks) * 0.3) * 2
    z_blocks = np.cos(np.arange(num_blocks) * 0.3) * 2
    
    # Block sizes (represent transaction volume)
    block_sizes = np.random.randint(15, 35, num_blocks)
    
    # Block colors - green for valid, orange for recent
    block_colors = ['#22c55e'] * (num_blocks - 3) + ['#f59e0b', '#f59e0b', '#3b82f6']
    
    # Create the 3D figure
    fig = go.Figure()
    
    # Add blockchain blocks as cubes (represented as scatter with large markers)
    fig.add_trace(go.Scatter3d(
        x=x_blocks, y=y_blocks, z=z_blocks,
        mode='markers+text',
        marker=dict(
            size=block_sizes,
            color=block_colors,
            symbol='square',
            opacity=0.9,
            line=dict(width=2, color='#ffffff')
        ),
        text=[f'Block #{i}' for i in range(num_blocks)],
        textposition='top center',
        textfont=dict(size=10, color=chart_colors['text']),
        hovertext=[f'Block #{i}<br>Hash: {hex(hash(i*54321) % 0xFFFFFFFF)[2:].upper()}<br>Transactions: {np.random.randint(100, 2000)}<br>Size: {np.random.randint(500, 1200)} KB<br>Timestamp: 2024-01-{15+i:02d}' 
                   for i in range(num_blocks)],
        hoverinfo='text',
        name='Blocks'
    ))
    
    # Add chain links between blocks
    for i in range(num_blocks - 1):
        fig.add_trace(go.Scatter3d(
            x=[x_blocks[i], x_blocks[i+1]],
            y=[y_blocks[i], y_blocks[i+1]],
            z=[z_blocks[i], z_blocks[i+1]],
            mode='lines',
            line=dict(
                color='#22c55e',
                width=8
            ),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Add hash arrows (small markers along the chain)
    for i in range(num_blocks - 1):
        mid_x = (x_blocks[i] + x_blocks[i+1]) / 2
        mid_y = (y_blocks[i] + y_blocks[i+1]) / 2
        mid_z = (z_blocks[i] + z_blocks[i+1]) / 2
        fig.add_trace(go.Scatter3d(
            x=[mid_x], y=[mid_y], z=[mid_z],
            mode='markers',
            marker=dict(
                size=6,
                color='#06b6d4',
                symbol='diamond'
            ),
            hovertext=f'Hash Link<br>Previous: {hex(hash(i*54321) % 0xFFFFFFFF)[2:].upper()[:8]}<br>Next: {hex(hash((i+1)*54321) % 0xFFFFFFFF)[2:].upper()[:8]}',
            hoverinfo='text',
            showlegend=False
        ))
    
    # Add mining nodes around the chain
    num_miners = 8
    for i in range(num_miners):
        angle = 2 * np.pi * i / num_miners
        radius = 15
        mx = x_blocks[num_blocks//2] + radius * np.cos(angle)
        my = radius * np.sin(angle)
        mz = 8 * np.sin(angle * 2)
        
        fig.add_trace(go.Scatter3d(
            x=[mx], y=[my], z=[mz],
            mode='markers',
            marker=dict(
                size=12,
                color='#8b5cf6',
                symbol='diamond',
                line=dict(width=2, color='#ffffff')
            ),
            hovertext=f'Miner Node {i+1}<br>Hashrate: {np.random.randint(50, 200)} TH/s<br>Status: Mining<br>Blocks Found: {np.random.randint(10, 100)}',
            hoverinfo='text',
            showlegend=False,
            name=f'Miner {i+1}'
        ))
        
        # Connection to nearest block
        nearest_block = num_blocks - 1  # Connect to latest block
        fig.add_trace(go.Scatter3d(
            x=[mx, x_blocks[nearest_block]],
            y=[my, y_blocks[nearest_block]],
            z=[mz, z_blocks[nearest_block]],
            mode='lines',
            line=dict(
                color='rgba(139, 92, 246, 0.3)',
                width=2,
                dash='dot'
            ),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Add pending transactions pool
    num_pending = 15
    pending_x = np.random.uniform(x_blocks[-1] + 5, x_blocks[-1] + 15, num_pending)
    pending_y = np.random.uniform(-8, 8, num_pending)
    pending_z = np.random.uniform(-8, 8, num_pending)
    
    fig.add_trace(go.Scatter3d(
        x=pending_x, y=pending_y, z=pending_z,
        mode='markers',
        marker=dict(
            size=5,
            color='#fbbf24',
            opacity=0.7
        ),
        hovertext=[f'Pending Tx<br>Amount: {np.random.uniform(0.01, 5):.4f} BTC<br>Fee: {np.random.uniform(0.0001, 0.001):.6f} BTC' for _ in range(num_pending)],
        hoverinfo='text',
        name='Pending Transactions'
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': '3D Blockchain Visualization',
            'font': {'size': 24, 'color': chart_colors['text']},
            'x': 0.5,
            'xanchor': 'center'
        },
        scene=dict(
            xaxis=dict(
                title='Chain Position',
                backgroundcolor='rgba(0, 0, 0, 0)',
                gridcolor=chart_colors['grid'],
                showbackground=True,
                tickfont=dict(color=chart_colors['text'])
            ),
            yaxis=dict(
                title='Network Spread',
                backgroundcolor='rgba(0, 0, 0, 0)',
                gridcolor=chart_colors['grid'],
                showbackground=True,
                tickfont=dict(color=chart_colors['text'])
            ),
            zaxis=dict(
                title='Depth',
                backgroundcolor='rgba(0, 0, 0, 0)',
                gridcolor=chart_colors['grid'],
                showbackground=True,
                tickfont=dict(color=chart_colors['text'])
            ),
            camera=dict(
                eye=dict(x=1.8, y=1.2, z=0.8)
            )
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        height=700,
        margin=dict(l=0, r=0, t=80, b=0),
        font=dict(color=chart_colors['text']),
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(0,0,0,0.3)',
            font=dict(color=chart_colors['text'])
        )
    )
    
    ui.plotly(fig).classes('w-full')



def create_3d_animation():
    """Create 3D animation showing blockchain network"""
    
    with ui.column().classes('w-full gap-8'):
        
        # Description
        ui.label('Explore the 3D blockchain network with interactive nodes and connections').classes(
            'text-xl dark:text-gray-300 text-gray-600 mb-4'
        )
        
        # Create interactive 3D blockchain visualization
        create_interactive_3d_chart()
        
        # Blockchain nodes explanation
        with ui.row().classes('w-full justify-around flex-wrap gap-6 mt-8'):
            with ui.card().classes('step-card flex-1 min-w-[250px]'):
                with ui.row().classes('items-center gap-4 mb-4'):
                    ui.icon('account_balance', size='2.5rem').classes('text-cyan-400')
                    ui.label('Blockchain Nodes').classes('text-xl font-bold dark:text-white text-gray-900')
                ui.label('Each node represents a validated transaction block with cryptographic hash').classes(
                    'dark:text-gray-300 text-gray-600'
                )
            
            with ui.card().classes('step-card flex-1 min-w-[250px]'):
                with ui.row().classes('items-center gap-4 mb-4'):
                    ui.icon('security', size='2.5rem').classes('text-green-400')
                    ui.label('Immutable Chain').classes('text-xl font-bold dark:text-white text-gray-900')
                ui.label('Blocks are cryptographically linked, making tampering virtually impossible').classes(
                    'dark:text-gray-300 text-gray-600'
                )
            
            with ui.card().classes('step-card flex-1 min-w-[250px]'):
                with ui.row().classes('items-center gap-4 mb-4'):
                    ui.icon('speed', size='2.5rem').classes('text-purple-400')
                    ui.label('Fast Consensus').classes('text-xl font-bold dark:text-white text-gray-900')
                ui.label('Distributed validation ensures transaction integrity in milliseconds').classes(
                    'dark:text-gray-300 text-gray-600'
                )
        
        # 3D Process Simulation Section
        ui.separator().classes('my-12')
        
        with ui.row().classes('items-center gap-4 mb-6'):
            ui.icon('precision_manufacturing', size='2.5rem').classes('text-green-400').style(
                'filter: drop-shadow(0 0 20px rgba(34, 197, 94, 0.8));'
            )
            ui.label('Live 3D Process Simulation').classes('text-3xl font-bold dark:text-white text-gray-900')
        
        ui.label('Watch transactions flow through the system in real-time 3D animation').classes(
            'text-xl dark:text-gray-300 text-gray-600 mb-6'
        )
        
        # Create the 3D simulation
        create_3d_process_simulation()


def create_3d_process_simulation():
    """Create a highly detailed 3D 'Neural Forensic Core' simulation with Three.js"""
    
    with ui.column().classes('w-full gap-8'):
        
        # Load Three.js and OrbitControls
        ui.add_head_html('''
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        ''')
        
        # Simulation container
        ui.html("""<div id="simulation-wrapper" style="width: 100%; height: 850px; position: relative; border-radius: 24px; overflow: hidden; background: #020617; box-shadow: 0 0 50px rgba(34, 197, 94, 0.2);" class="animations-page-active">
    <canvas id="threejs-canvas" style="width: 100%; height: 100%; display: block;"></canvas>
    
    <!-- Title Banner -->
    <div style="position: absolute; top: 30px; left: 50%; transform: translateX(-50%); background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(20px); padding: 15px 40px; border-radius: 12px; border: 2px solid rgba(34, 197, 94, 0.5); text-align: center; z-index: 10; box-shadow: 0 0 30px rgba(34, 197, 94, 0.3);">
        <div style="color: #22c55e; font-size: 22px; font-weight: 900; letter-spacing: 2px; font-family: 'Space Grotesk', sans-serif;">NEURAL FORENSIC CORE</div>
        <div style="color: #94a3b8; font-size: 12px; margin-top: 5px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Real-time Multidimensional Illegal Activity Analysis</div>
    </div>
    
    <!-- Stats Panel -->
    <div style="position: absolute; top: 30px; right: 30px; background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(20px); padding: 25px; border-radius: 16px; color: #f1f5f9; font-family: 'Inter', sans-serif; min-width: 260px; border: 1px solid rgba(34, 197, 94, 0.3); z-index: 10;">
        <div style="font-weight: 800; margin-bottom: 20px; font-size: 14px; color: #22c55e; border-bottom: 2px solid rgba(34, 197, 94, 0.3); padding-bottom: 10px; display: flex; align-items: center; gap: 10px;">
            <div style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%; animation: pulse-glow 2s infinite;"></div>
            CORE ANALYTICS
        </div>
        <div style="margin: 12px 0; display: flex; justify-content: space-between; font-size: 14px;">
            <span style="color: #94a3b8;">Neural Paths:</span>
            <span id="stat-active" style="color: #0ea5e9; font-weight: 800;">64</span>
        </div>
        <div style="margin: 12px 0; display: flex; justify-content: space-between; font-size: 14px;">
            <span style="color: #94a3b8;">Validated:</span>
            <span id="stat-processed" style="color: #22c55e; font-weight: 800;">0</span>
        </div>
        <div style="margin: 12px 0; display: flex; justify-content: space-between; font-size: 14px;">
            <span style="color: #94a3b8;">Illegal Alerts:</span>
            <span id="stat-fraud" style="color: #ef4444; font-weight: 800;">0</span>
        </div>
        <div style="margin: 12px 0; display: flex; justify-content: space-between; font-size: 14px;">
            <span style="color: #94a3b8;">Core Stability:</span>
            <span id="stat-rate" style="color: #a855f7; font-weight: 800;">99.2%</span>
        </div>
    </div>
    
    <!-- Stage Progress -->
    <div style="position: absolute; bottom: 30px; right: 30px; background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(20px); padding: 20px; border-radius: 16px; color: #f1f5f9; min-width: 240px; border: 1px solid rgba(139, 92, 246, 0.3); z-index: 10;">
        <div style="font-weight: 800; margin-bottom: 15px; font-size: 14px; color: #a855f7;">AI PROCESSING PIPELINE</div>
        <div id="stage-indicators" style="display: flex; flex-direction: column; gap: 8px;">
            <div id="stage-1" style="display: flex; align-items: center; gap: 10px; font-size: 12px; padding: 6px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px; border-left: 3px solid #3b82f6;"><span>01</span> INPUT INGESTION</div>
            <div id="stage-2" style="display: flex; align-items: center; gap: 10px; font-size: 12px; padding: 6px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px; border-left: 3px solid #06b6d4;"><span>02</span> NEURAL FILTERING</div>
            <div id="stage-3" style="display: flex; align-items: center; gap: 10px; font-size: 12px; padding: 6px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px; border-left: 3px solid #8b5cf6;"><span>03</span> PATTERN MATCHING</div>
            <div id="stage-4" style="display: flex; align-items: center; gap: 10px; font-size: 12px; padding: 6px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px; border-left: 3px solid #22c55e;"><span>04</span> LEDGER COMMIT</div>
        </div>
    </div>
    
    <style>
        @keyframes pulse-glow {
            0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
            100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
        }
    </style>
</div>
""", ).classes('w-full')
        
        # Three.js simulation script - Highly Detailed Neural Core
        ui.run_javascript('''
(function() {
    "use strict";
    
    function initSimulation() {
        const canvas = document.getElementById("threejs-canvas");
        const wrapper = document.getElementById("simulation-wrapper");
        if (!canvas || !wrapper) return;
        
        const width = wrapper.clientWidth;
        const height = wrapper.clientHeight || 850;
        
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x020617);
        scene.fog = new THREE.FogExp2(0x020617, 0.01);
        
        const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 2000);
        camera.position.set(60, 40, 80);
        
        const renderer = new THREE.WebGLRenderer({ 
            canvas: canvas, 
            antialias: true, 
            alpha: true 
        });
        renderer.setSize(width, height);
        renderer.setPixelRatio(window.devicePixelRatio);
        
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.autoRotate = true;
        controls.autoRotateSpeed = 0.5;
        
        // --- Lights ---
        scene.add(new THREE.AmbientLight(0xffffff, 0.2));
        const mainLight = new THREE.PointLight(0x22c55e, 2, 200);
        mainLight.position.set(0, 50, 0);
        scene.add(mainLight);
        
        // --- Neural Core ---
        const coreGroup = new THREE.Group();
        scene.add(coreGroup);
        
        // Inner Glow Sphere
        const coreGlowGeo = new THREE.SphereGeometry(8, 64, 64);
        const coreGlowMat = new THREE.MeshPhongMaterial({
            color: 0x22c55e,
            emissive: 0x22c55e,
            emissiveIntensity: 2,
            transparent: true,
            opacity: 0.1,
        });
        const coreGlow = new THREE.Mesh(coreGlowGeo, coreGlowMat);
        coreGroup.add(coreGlow);
        
        // Wireframe Core
        const coreWireGeo = new THREE.IcosahedronGeometry(10, 2);
        const coreWireMat = new THREE.MeshBasicMaterial({
            color: 0x22c55e,
            wireframe: true,
            transparent: true,
            opacity: 0.2
        });
        const coreWire = new THREE.Mesh(coreWireGeo, coreWireMat);
        coreGroup.add(coreWire);
        
        // Orbital Rings (Temporal & Spatial Layers)
        const ringGroup = new THREE.Group();
        coreGroup.add(ringGroup);
        
        const createRing = (radius, color, rotationX, speed) => {
            const ringGeo = new THREE.TorusGeometry(radius, 0.05, 16, 100);
            const ringMat = new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0.4 });
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.rotation.x = rotationX;
            ringGroup.add(ring);
            return { mesh: ring, speed: speed };
        };
        
        const rings = [
            createRing(18, 0x0ea5e9, Math.PI/2.2, 0.01),
            createRing(24, 0x8b5cf6, -Math.PI/2.5, -0.008),
            createRing(30, 0x22c55e, Math.PI/3, 0.005)
        ];
        
        // --- Neural Pathways (Curved Lines) ---
        const paths = [];
        const createPath = (start, end, midOffset) => {
            const mid = new THREE.Vector3().lerpVectors(start, end, 0.5);
            mid.add(midOffset);
            const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
            const points = curve.getPoints(50);
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const material = new THREE.LineBasicMaterial({ color: 0x334155, transparent: true, opacity: 0.1 });
            const line = new THREE.Line(geometry, material);
            scene.add(line);
            return curve;
        };
        
        // Generate many paths from outer space to core
        for(let i=0; i<40; i++) {
            const angle = (i / 40) * Math.PI * 2;
            const start = new THREE.Vector3(Math.cos(angle)*100, (Math.random()-0.5)*100, Math.sin(angle)*100);
            const end = new THREE.Vector3(0, 0, 0);
            const offset = new THREE.Vector3((Math.random()-0.5)*50, (Math.random()-0.5)*50, (Math.random()-0.5)*50);
            paths.push(createPath(start, end, offset));
        }
        
        // --- Transactions ---
        const txParticles = [];
        const txGeo = new THREE.SphereGeometry(0.8, 16, 16);
        
        const createTransaction = () => {
            const isFraud = Math.random() < 0.15;
            const color = isFraud ? 0xef4444 : 0x22c55e;
            const mat = new THREE.MeshPhongMaterial({ color: color, emissive: color, emissiveIntensity: 2 });
            const mesh = new THREE.Mesh(txGeo, mat);
            scene.add(mesh);
            
            return {
                mesh: mesh,
                path: paths[Math.floor(Math.random() * paths.length)],
                progress: 0,
                speed: 0.003 + Math.random() * 0.005,
                isFraud: isFraud
            };
        };
        
        for(let i=0; i<30; i++) txParticles.push(createTransaction());
        
        // --- Stats ---
        let processed = 0;
        let fraud = 0;
        
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            
            const time = performance.now() * 0.001;
            
            // Core pulsations
            coreWire.rotation.y += 0.01;
            coreWire.rotation.x += 0.005;
            coreGlow.scale.setScalar(1 + Math.sin(time*2)*0.05);
            
            // Rings rotation
            rings.forEach(r => {
                r.mesh.rotation.z += r.speed;
            });
            
            // Update transactions
            txParticles.forEach((tx, index) => {
                tx.progress += tx.speed;
                
                if (tx.progress >= 1) {
                    tx.progress = 0;
                    processed++;
                    if (tx.isFraud) {
                        fraud++;
                        // Core "Shock" effect for fraud
                        coreGlow.material.emissiveIntensity = 5;
                        coreGlow.material.color.setHex(0xef4444);
                        setTimeout(() => {
                            coreGlow.material.emissiveIntensity = 2;
                            coreGlow.material.color.setHex(0x22c55e);
                        }, 100);
                    }
                    
                    // Reset to new path
                    tx.path = paths[Math.floor(Math.random() * paths.length)];
                    tx.isFraud = Math.random() < 0.15;
                    const color = tx.isFraud ? 0xef4444 : 0x22c55e;
                    tx.mesh.material.color.setHex(color);
                    tx.mesh.material.emissive.setHex(color);
                }
                
                const pos = tx.path.getPoint(tx.progress);
                tx.mesh.position.copy(pos);
                
                // Trail/Glow effect scaling
                const scale = (1 - tx.progress) * 1.5;
                tx.mesh.scale.setScalar(scale);
            });
            
            // UI Update
            document.getElementById("stat-processed").textContent = processed;
            document.getElementById("stat-fraud").textContent = fraud;
            if(processed > 0) {
                const stability = (1 - (fraud/processed)).toFixed(1);
                document.getElementById("stat-rate").textContent = (stability * 100).toFixed(1) + "%";
            }
            
            renderer.render(scene, camera);
        }
        
        animate();
        
        window.addEventListener("resize", () => {
            const w = wrapper.clientWidth;
            const h = wrapper.clientHeight || 850;
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
        });
    }
    
    // Delayed init to ensure THREE is ready
    setTimeout(initSimulation, 1000);
  })();
        ''')


def create_vtac_pipeline_animation():
    """Create a 3D VTAC pipeline animation (Detection → De-anonymization → Identification) per the research paper"""
    
    with ui.column().classes('w-full gap-8'):
        # Clear explanation of what this animation shows
        with ui.card().classes('step-card mb-6'):
            ui.label('VTAC Framework: 3-Phase Money Laundering Detection').classes('text-2xl font-bold dark:text-white text-gray-900 mb-4')
            ui.label('This animation shows how transactions flow through the VTAC pipeline from the research paper:').classes(
                'text-lg dark:text-gray-300 text-gray-600 mb-4'
            )
            
        # Phase explanation cards in a clearer layout
        with ui.row().classes('w-full gap-4 flex-wrap mb-6'):
            with ui.card().classes('flex-1 min-w-[280px] p-5 border-l-4 border-blue-500 bg-blue-500/5'):
                with ui.row().classes('items-center gap-3 mb-3'):
                    ui.html('<div style="width:32px;height:32px;background:#3b82f6;border-radius:8px;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;">1</div>')
                    ui.label('DETECTION PHASE').classes('font-bold text-blue-400 text-lg')
                ui.label('Machine Learning Classification').classes('font-semibold dark:text-white text-gray-800 mb-2')
                ui.html('''
                    <ul class="text-sm dark:text-gray-400 text-gray-600 list-disc ml-4 space-y-1">
                        <li><b>Models:</b> RandomForest, AdaBoost, XGBoost</li>
                        <li><b>Input:</b> 166 features from Elliptic dataset</li>
                        <li><b>Output:</b> LEGAL (green) or ILLEGAL (red) classification</li>
                    </ul>
                ''')
                
            with ui.card().classes('flex-1 min-w-[280px] p-5 border-l-4 border-purple-500 bg-purple-500/5'):
                with ui.row().classes('items-center gap-3 mb-3'):
                    ui.html('<div style="width:32px;height:32px;background:#8b5cf6;border-radius:8px;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;">2</div>')
                    ui.label('DE-ANONYMIZATION').classes('font-bold text-purple-400 text-lg')
                ui.label('Map to Real Bitcoin Addresses').classes('font-semibold dark:text-white text-gray-800 mb-2')
                ui.html('''
                    <ul class="text-sm dark:text-gray-400 text-gray-600 list-disc ml-4 space-y-1">
                        <li><b>Purpose:</b> Link anonymous Elliptic IDs to real hashes</li>
                        <li><b>Method:</b> Result.csv mapping file</li>
                        <li><b>Result:</b> Real Bitcoin transaction hash for on-chain lookup</li>
                    </ul>
                ''')
                
            with ui.card().classes('flex-1 min-w-[280px] p-5 border-l-4 border-green-500 bg-green-500/5'):
                with ui.row().classes('items-center gap-3 mb-3'):
                    ui.html('<div style="width:32px;height:32px;background:#22c55e;border-radius:8px;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;">3</div>')
                    ui.label('IDENTIFICATION (ADVISORY)').classes('font-bold text-green-400 text-lg')
                ui.label('Trace Money Flow & Beneficiaries').classes('font-semibold dark:text-white text-gray-800 mb-2')
                ui.html('''
                    <ul class="text-sm dark:text-gray-400 text-gray-600 list-disc ml-4 space-y-1">
                        <li><b>Value Score:</b> Transaction amount analysis</li>
                        <li><b>Frequency:</b> Transaction rate patterns</li>
                        <li><b>Time Window:</b> First-out to last-in interval</li>
                        <li><b>Weight Factor:</b> Combined risk assessment</li>
                    </ul>
                ''')
        
        ui.add_head_html('''
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        ''')
        
        # Live status panel with clearer labels
        ui.label('Live Transaction Processing Status').classes('text-lg font-bold dark:text-white text-gray-800 mb-2')
        with ui.row().classes('w-full justify-around flex-wrap gap-4 mb-6'):
            with ui.card().classes('step-card flex-1 min-w-[150px] text-center'):
                ui.label('Current Phase').classes('text-sm dark:text-gray-400 text-gray-500 mb-2')
                ui.html('<div id="vtac-phase" class="text-xl font-bold text-blue-400">DETECTION</div>')
            with ui.card().classes('step-card flex-1 min-w-[150px] text-center'):
                ui.label('Transaction ID').classes('text-sm dark:text-gray-400 text-gray-500 mb-2')
                ui.html('<div id="vtac-tx" class="text-lg font-bold text-cyan-400">TX-0001</div>')
            with ui.card().classes('step-card flex-1 min-w-[150px] text-center'):
                ui.label('ML Classification').classes('text-sm dark:text-gray-400 text-gray-500 mb-2')
                ui.html('<div id="vtac-prediction" class="text-xl font-bold text-gray-500">---</div>')
            with ui.card().classes('step-card flex-1 min-w-[150px] text-center'):
                ui.label('VTAC Risk Score').classes('text-sm dark:text-gray-400 text-gray-500 mb-2')
                ui.html('<div id="vtac-score" class="text-xl font-bold text-gray-500">0.00</div>')
        
        ui.html("""<div id="vtac-pipeline-wrapper" style="width: 100%; height: 650px; position: relative; border-radius: 24px; overflow: hidden; background: #0a0f1a; box-shadow: 0 0 50px rgba(14, 165, 233, 0.25);" class="animations-page-active">
    <canvas id="vtac-pipeline-canvas" style="width: 100%; height: 100%; display: block;"></canvas>
    
    <!-- Legend -->
    <div style="position: absolute; top: 20px; left: 20px; background: rgba(15, 23, 42, 0.9); padding: 15px; border-radius: 12px; border: 1px solid rgba(14, 165, 233, 0.4); color: #e2e8f0; font-size: 12px; z-index: 10;">
        <div style="font-weight: 700; margin-bottom: 10px; color: #0ea5e9;">VTAC PIPELINE LEGEND</div>
        <div style="display: flex; align-items: center; gap: 8px; margin: 6px 0;"><div style="width: 12px; height: 12px; background: #3b82f6; border-radius: 2px;"></div> Detection (ML)</div>
        <div style="display: flex; align-items: center; gap: 8px; margin: 6px 0;"><div style="width: 12px; height: 12px; background: #8b5cf6; border-radius: 2px;"></div> De-anonymization</div>
        <div style="display: flex; align-items: center; gap: 8px; margin: 6px 0;"><div style="width: 12px; height: 12px; background: #22c55e; border-radius: 2px;"></div> Identification</div>
        <div style="display: flex; align-items: center; gap: 8px; margin: 6px 0;"><div style="width: 12px; height: 12px; background: #22c55e; border-radius: 50%;"></div> Legal Transaction</div>
        <div style="display: flex; align-items: center; gap: 8px; margin: 6px 0;"><div style="width: 12px; height: 12px; background: #ef4444; border-radius: 50%;"></div> Illegal Transaction</div>
    </div>
</div>
""").classes('w-full')
        
        ui.run_javascript('''
(function() {
    "use strict";
    function initVtacPipeline() {
        const canvas = document.getElementById("vtac-pipeline-canvas");
        const wrapper = document.getElementById("vtac-pipeline-wrapper");
        if (!canvas || !wrapper || typeof THREE === 'undefined') {
            setTimeout(initVtacPipeline, 500);
            return;
        }
        const width = wrapper.clientWidth;
        const height = wrapper.clientHeight || 650;
        
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0f1a);
        
        const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
        camera.position.set(0, 10, 35);
        
        const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.maxDistance = 60;
        controls.minDistance = 15;
        
        scene.add(new THREE.AmbientLight(0xffffff, 0.3));
        const keyLight = new THREE.DirectionalLight(0xffffff, 0.8);
        keyLight.position.set(10, 20, 10);
        keyLight.castShadow = true;
        scene.add(keyLight);
        
        // Grid
        const gridHelper = new THREE.GridHelper(60, 30, 0x1e3a5f, 0x0f172a);
        gridHelper.position.y = -6;
        scene.add(gridHelper);
        
        // Create stage boxes with detailed content
        function createStageBox(x, color, title, subtitle, details) {
            const group = new THREE.Group();
            
            // Main box
            const boxGeo = new THREE.BoxGeometry(8, 5, 3);
            const boxMat = new THREE.MeshPhongMaterial({ 
                color: color, 
                transparent: true, 
                opacity: 0.85,
                shininess: 100
            });
            const box = new THREE.Mesh(boxGeo, boxMat);
            box.castShadow = true;
            box.receiveShadow = true;
            group.add(box);
            
            // Glow
            const glowGeo = new THREE.BoxGeometry(8.5, 5.5, 3.5);
            const glowMat = new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0.1 });
            const glow = new THREE.Mesh(glowGeo, glowMat);
            group.add(glow);
            
            // Title label
            const titleCanvas = document.createElement('canvas');
            const titleCtx = titleCanvas.getContext('2d');
            titleCanvas.width = 512;
            titleCanvas.height = 256;
            titleCtx.fillStyle = '#ffffff';
            titleCtx.font = 'bold 36px Arial';
            titleCtx.textAlign = 'center';
            titleCtx.fillText(title, 256, 80);
            titleCtx.font = '22px Arial';
            titleCtx.fillStyle = '#94a3b8';
            titleCtx.fillText(subtitle, 256, 130);
            titleCtx.font = '18px Arial';
            titleCtx.fillStyle = '#64748b';
            const detailLines = details.split('\\n');
            detailLines.forEach((line, i) => {
                titleCtx.fillText(line, 256, 170 + i * 25);
            });
            
            const titleTexture = new THREE.CanvasTexture(titleCanvas);
            const titleSprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: titleTexture, transparent: true }));
            titleSprite.scale.set(10, 5, 1);
            titleSprite.position.set(0, -5, 0);
            group.add(titleSprite);
            
            group.position.set(x, 0, 0);
            return group;
        }
        
        // VTAC Pipeline Stages
        const stage1 = createStageBox(-16, 0x3b82f6, 'PHASE 1', 'DETECTION', 'RandomForest\\nAdaBoost\\nXGBoost');
        const stage2 = createStageBox(0, 0x8b5cf6, 'PHASE 2', 'DE-ANONYMIZE', 'txId → Bitcoin Hash\\nResult.csv Mapping');
        const stage3 = createStageBox(16, 0x22c55e, 'PHASE 3', 'IDENTIFICATION', 'Value Score\\nFrequency\\nTime Window\\nWeight Factor');
        
        scene.add(stage1);
        scene.add(stage2);
        scene.add(stage3);
        
        // Connection arrows (tubes)
        function createArrow(startX, endX, color) {
            const curve = new THREE.CatmullRomCurve3([
                new THREE.Vector3(startX, 0, 2),
                new THREE.Vector3((startX + endX) / 2, 2, 3),
                new THREE.Vector3(endX, 0, 2)
            ]);
            const tubeGeo = new THREE.TubeGeometry(curve, 20, 0.15, 8, false);
            const tubeMat = new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0.6 });
            const tube = new THREE.Mesh(tubeGeo, tubeMat);
            scene.add(tube);
            return curve;
        }
        
        const arrow1 = createArrow(-12, -4, 0x38bdf8);
        const arrow2 = createArrow(4, 12, 0x38bdf8);
        
        // Transaction particles
        const transactions = [];
        let txCount = 0;
        
        function createTransaction() {
            const isIllegal = Math.random() < 0.3; // 30% illegal per Elliptic dataset ratio
            const color = isIllegal ? 0xef4444 : 0x22c55e;
            
            const group = new THREE.Group();
            
            // Core
            const coreGeo = new THREE.IcosahedronGeometry(0.5, 1);
            const coreMat = new THREE.MeshPhongMaterial({ 
                color: color,
                emissive: color,
                emissiveIntensity: 0.5
            });
            const core = new THREE.Mesh(coreGeo, coreMat);
            group.add(core);
            
            // Glow
            const glowGeo = new THREE.SphereGeometry(0.8, 16, 16);
            const glowMat = new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0.3 });
            const glow = new THREE.Mesh(glowGeo, glowMat);
            group.add(glow);
            
            group.position.set(-24, 0, 2);
            group.userData = {
                isIllegal: isIllegal,
                progress: 0,
                phase: 0,
                id: ++txCount,
                score: isIllegal ? (0.7 + Math.random() * 0.25) : (Math.random() * 0.4)
            };
            
            scene.add(group);
            transactions.push(group);
            
            updateUI('DETECTION', 'TX-' + String(txCount).padStart(4, '0'), '---', '0.00', 'text-gray-500', 'text-gray-500');
        }
        
        function updateUI(phase, tx, prediction, score, predColor, scoreColor) {
            const phaseEl = document.getElementById('vtac-phase');
            const txEl = document.getElementById('vtac-tx');
            const predEl = document.getElementById('vtac-prediction');
            const scoreEl = document.getElementById('vtac-score');
            
            if (phaseEl) {
                phaseEl.textContent = phase;
                phaseEl.className = 'text-xl font-bold ' + (phase === 'DETECTION' ? 'text-blue-400' : phase === 'DE-ANONYMIZE' ? 'text-purple-400' : 'text-green-400');
            }
            if (txEl) txEl.textContent = tx;
            if (predEl) {
                predEl.textContent = prediction;
                predEl.className = 'text-xl font-bold ' + predColor;
            }
            if (scoreEl) {
                scoreEl.textContent = score;
                scoreEl.className = 'text-xl font-bold ' + scoreColor;
            }
        }
        
        // Spawn first transaction
        setTimeout(createTransaction, 1000);
        
        // Spawn new transactions periodically
        setInterval(() => {
            if (transactions.length < 3) {
                createTransaction();
            }
        }, 4000);
        
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            
            const time = performance.now() * 0.001;
            
            // Animate stages
            [stage1, stage2, stage3].forEach((stage, i) => {
                stage.position.y = Math.sin(time * 0.5 + i) * 0.3;
            });
            
            // Process transactions
            transactions.forEach((tx, index) => {
                tx.userData.progress += 0.004;
                const p = tx.userData.progress;
                
                // Rotate core
                tx.children[0].rotation.x += 0.02;
                tx.children[0].rotation.y += 0.03;
                
                // Phase 0: Moving to Detection
                if (p < 0.25) {
                    tx.position.x = -24 + p * 48;  // -24 to -12
                    tx.position.y = Math.sin(p * Math.PI * 4) * 1;
                    tx.position.z = 2;
                    
                    if (tx.userData.phase !== 0) {
                        tx.userData.phase = 0;
                        updateUI('DETECTION', 'TX-' + String(tx.userData.id).padStart(4, '0'), 'ANALYZING...', '---', 'text-yellow-400', 'text-gray-500');
                    }
                }
                // Phase 1: At Detection, being analyzed
                else if (p < 0.35) {
                    tx.position.set(-16, Math.sin(time * 5) * 0.5, 4);
                    
                    if (tx.userData.phase !== 1) {
                        tx.userData.phase = 1;
                        const pred = tx.userData.isIllegal ? 'ILLEGAL' : 'LEGAL';
                        const predColor = tx.userData.isIllegal ? 'text-red-500' : 'text-green-400';
                        updateUI('DETECTION', 'TX-' + String(tx.userData.id).padStart(4, '0'), pred, tx.userData.score.toFixed(2), predColor, tx.userData.isIllegal ? 'text-red-500' : 'text-green-400');
                    }
                }
                // Phase 2: Moving to De-anonymization
                else if (p < 0.5) {
                    const localP = (p - 0.35) / 0.15;
                    const point = arrow1.getPoint(localP);
                    tx.position.copy(point);
                    
                    if (tx.userData.phase !== 2) {
                        tx.userData.phase = 2;
                        updateUI('DE-ANONYMIZE', 'TX-' + String(tx.userData.id).padStart(4, '0'), tx.userData.isIllegal ? 'ILLEGAL' : 'LEGAL', tx.userData.score.toFixed(2), tx.userData.isIllegal ? 'text-red-500' : 'text-green-400', tx.userData.isIllegal ? 'text-red-500' : 'text-green-400');
                    }
                }
                // Phase 3: At De-anonymization
                else if (p < 0.6) {
                    tx.position.set(0, Math.sin(time * 5) * 0.5, 4);
                    
                    if (tx.userData.phase !== 3) {
                        tx.userData.phase = 3;
                    }
                }
                // Phase 4: Moving to Identification
                else if (p < 0.75) {
                    const localP = (p - 0.6) / 0.15;
                    const point = arrow2.getPoint(localP);
                    tx.position.copy(point);
                    
                    if (tx.userData.phase !== 4) {
                        tx.userData.phase = 4;
                        updateUI('IDENTIFICATION', 'TX-' + String(tx.userData.id).padStart(4, '0'), tx.userData.isIllegal ? 'ILLEGAL' : 'LEGAL', tx.userData.score.toFixed(2), tx.userData.isIllegal ? 'text-red-500' : 'text-green-400', tx.userData.isIllegal ? 'text-red-500' : 'text-green-400');
                    }
                }
                // Phase 5: At Identification, advisory computed
                else if (p < 0.9) {
                    tx.position.set(16, Math.sin(time * 5) * 0.5, 4);
                    
                    if (tx.userData.phase !== 5) {
                        tx.userData.phase = 5;
                    }
                }
                // Phase 6: Exiting
                else {
                    tx.position.x = 16 + (p - 0.9) * 80;
                    tx.children[1].material.opacity = 0.3 * (1 - (p - 0.9) / 0.1);
                    
                    if (p >= 1) {
                        scene.remove(tx);
                        transactions.splice(index, 1);
                    }
                }
            });
            
            renderer.render(scene, camera);
        }
        animate();
        
        window.addEventListener('resize', () => {
            const w = wrapper.clientWidth;
            const h = wrapper.clientHeight || 650;
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
        });
    }
    setTimeout(initVtacPipeline, 800);
})();
        ''')


def create_vtac_advisory_graph_animation():
    """Create a 3D advisory graph animation showing money laundering layering detection"""
    
    with ui.column().classes('w-full gap-8'):
        # Clear explanation header
        with ui.card().classes('step-card mb-6'):
            ui.label('What This Animation Shows').classes('text-2xl font-bold dark:text-white text-gray-900 mb-3')
            ui.label('This visualization demonstrates how the VTAC system tracks illegal fund flows through a Bitcoin transaction network:').classes(
                'text-lg dark:text-gray-300 text-gray-600 mb-4'
            )
        
        # Explanation of the visualization elements
        with ui.row().classes('w-full gap-4 flex-wrap mb-6'):
            with ui.card().classes('flex-1 min-w-[200px] p-4 bg-gray-500/5'):
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.html('<div style="width:16px;height:16px;background:#22c55e;border-radius:50%;"></div>')
                    ui.label('Green Nodes').classes('font-bold text-green-400')
                ui.label('Normal Bitcoin wallet addresses - legitimate transactions').classes('text-sm dark:text-gray-400 text-gray-600')
                
            with ui.card().classes('flex-1 min-w-[200px] p-4 bg-red-500/5'):
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.html('<div style="width:16px;height:16px;background:#ef4444;border-radius:50%;"></div>')
                    ui.label('Red Nodes & Path').classes('font-bold text-red-400')
                ui.label('ILLEGAL: Detected layering chain - funds moving through intermediaries to obscure origin').classes('text-sm dark:text-gray-400 text-gray-600')
                
            with ui.card().classes('flex-1 min-w-[200px] p-4 bg-orange-500/5'):
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.html('<div style="width:16px;height:16px;background:#f97316;border-radius:50%;"></div>')
                    ui.label('Orange Particle').classes('font-bold text-orange-400')
                ui.label('Illicit funds being traced through the layering chain in real-time').classes('text-sm dark:text-gray-400 text-gray-600')
                
            with ui.card().classes('flex-1 min-w-[200px] p-4 bg-cyan-500/5'):
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.html('<div style="width:20px;height:8px;background:#0ea5e9;border-radius:4px;"></div>')
                    ui.label('Blue Ring').classes('font-bold text-cyan-400')
                ui.label('Time Window analysis - tracking transaction timing patterns').classes('text-sm dark:text-gray-400 text-gray-600')
        
        # Live tracking panel
        ui.label('Real-Time Layering Detection').classes('text-lg font-bold dark:text-white text-gray-800 mb-2')
        with ui.row().classes('w-full justify-around flex-wrap gap-4 mb-6'):
            with ui.card().classes('step-card flex-1 min-w-[120px] text-center'):
                ui.label('Tracking Status').classes('text-sm dark:text-gray-400 text-gray-500 mb-1')
                ui.html('<div id="advisory-status" class="text-lg font-bold text-orange-400">TRACING...</div>')
            with ui.card().classes('step-card flex-1 min-w-[120px] text-center'):
                ui.label('Hop Count').classes('text-sm dark:text-gray-400 text-gray-500 mb-1')
                ui.html('<div id="advisory-hop" class="text-lg font-bold text-red-400">1 / 5</div>')
            with ui.card().classes('step-card flex-1 min-w-[120px] text-center'):
                ui.label('Value Score').classes('text-sm dark:text-gray-400 text-gray-500 mb-1')
                ui.html('<div id="advisory-value" class="text-lg font-bold text-purple-400">0.85</div>')
            with ui.card().classes('step-card flex-1 min-w-[120px] text-center'):
                ui.label('Risk Level').classes('text-sm dark:text-gray-400 text-gray-500 mb-1')
                ui.html('<div id="advisory-risk" class="text-lg font-bold text-red-500">HIGH</div>')
        
        ui.add_head_html('''
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        ''')
        
        ui.html("""<div id="vtac-graph-wrapper" style="width: 100%; height: 650px; position: relative; border-radius: 24px; overflow: hidden; background: #0a0f1c; box-shadow: 0 0 60px rgba(239, 68, 68, 0.2);" class="animations-page-active">
    <canvas id="vtac-graph-canvas" style="width: 100%; height: 100%; display: block;"></canvas>
    
    <!-- Title overlay -->
    <div style="position: absolute; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(15, 23, 42, 0.9); padding: 12px 24px; border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.5); text-align: center; z-index: 10;">
        <div style="color: #ef4444; font-size: 16px; font-weight: 800; letter-spacing: 1px;">MONEY LAUNDERING LAYERING CHAIN</div>
        <div style="color: #94a3b8; font-size: 11px; margin-top: 4px;">Tracing illicit funds through intermediary wallets</div>
    </div>
    
    <!-- Legend -->
    <div style="position: absolute; bottom: 20px; left: 20px; background: rgba(15, 23, 42, 0.9); padding: 14px 18px; border-radius: 12px; border: 1px solid rgba(34, 197, 94, 0.4); color: #e2e8f0; font-size: 11px; z-index: 10;">
        <div style="font-weight: 700; margin-bottom: 8px; color: #94a3b8;">CHAIN STRUCTURE</div>
        <div style="display:flex;align-items:center;gap:8px;margin:5px 0;"><div style="width:10px;height:10px;background:#ef4444;border-radius:50%;"></div> Source (Criminal Wallet)</div>
        <div style="display:flex;align-items:center;gap:8px;margin:5px 0;"><div style="width:8px;height:8px;background:#ef4444;border-radius:50%;opacity:0.7;"></div> Intermediary Wallets</div>
        <div style="display:flex;align-items:center;gap:8px;margin:5px 0;"><div style="width:10px;height:10px;background:#ef4444;border-radius:50%;"></div> Destination (Beneficiary)</div>
        <div style="display:flex;align-items:center;gap:8px;margin:5px 0;"><div style="width:10px;height:10px;background:#f97316;border-radius:50%;"></div> Traced Funds (Moving)</div>
    </div>
    
    <!-- Current transaction info -->
    <div style="position: absolute; top: 20px; right: 20px; background: rgba(15, 23, 42, 0.9); padding: 14px 18px; border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.4); color: #e2e8f0; font-size: 11px; z-index: 10; min-width: 180px;">
        <div style="color: #ef4444; font-weight: 700; margin-bottom: 8px;">CURRENT HOP</div>
        <div id="graph-from" style="margin:4px 0;"><span style="color:#94a3b8;">From:</span> <span style="color:#ef4444;font-weight:600;">WALLET_A</span></div>
        <div id="graph-to" style="margin:4px 0;"><span style="color:#94a3b8;">To:</span> <span style="color:#ef4444;font-weight:600;">WALLET_B</span></div>
        <div id="graph-amount" style="margin:4px 0;"><span style="color:#94a3b8;">Amount:</span> <span style="color:#f97316;font-weight:600;">2.45 BTC</span></div>
    </div>
</div>
""").classes('w-full')
        
        ui.run_javascript('''
(function() {
    "use strict";
    function initVtacGraph() {
        const canvas = document.getElementById("vtac-graph-canvas");
        const wrapper = document.getElementById("vtac-graph-wrapper");
        if (!canvas || !wrapper || typeof THREE === 'undefined') {
            setTimeout(initVtacGraph, 500);
            return;
        }
        const width = wrapper.clientWidth;
        const height = wrapper.clientHeight || 650;
        
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0f1c);
        
        const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 1000);
        camera.position.set(0, 8, 25);
        
        const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.autoRotate = true;
        controls.autoRotateSpeed = 0.2;
        
        scene.add(new THREE.AmbientLight(0xffffff, 0.4));
        const light = new THREE.PointLight(0xef4444, 1.5, 80);
        light.position.set(0, 15, 10);
        scene.add(light);
        
        // Create the layering chain - a clear path from source to destination
        const chainLabels = ['SOURCE', 'HOP 1', 'HOP 2', 'HOP 3', 'DESTINATION'];
        const chainPositions = [
            new THREE.Vector3(-12, 0, 0),
            new THREE.Vector3(-6, 2, 3),
            new THREE.Vector3(0, -1, -2),
            new THREE.Vector3(6, 1, 2),
            new THREE.Vector3(12, 0, 0)
        ];
        
        const chainNodes = [];
        const chainNodeGeo = new THREE.SphereGeometry(0.6, 32, 32);
        
        chainPositions.forEach((pos, i) => {
            // Node
            const isEndpoint = i === 0 || i === chainPositions.length - 1;
            const nodeMat = new THREE.MeshPhongMaterial({ 
                color: 0xef4444, 
                emissive: 0xef4444,
                emissiveIntensity: isEndpoint ? 0.5 : 0.2,
                transparent: true,
                opacity: isEndpoint ? 1 : 0.8
            });
            const node = new THREE.Mesh(chainNodeGeo, nodeMat);
            node.position.copy(pos);
            node.scale.setScalar(isEndpoint ? 1.3 : 1);
            scene.add(node);
            chainNodes.push(node);
            
            // Glow
            const glowGeo = new THREE.SphereGeometry(isEndpoint ? 1.2 : 0.9, 16, 16);
            const glowMat = new THREE.MeshBasicMaterial({ color: 0xef4444, transparent: true, opacity: 0.15 });
            const glow = new THREE.Mesh(glowGeo, glowMat);
            glow.position.copy(pos);
            scene.add(glow);
            
            // Label
            const labelCanvas = document.createElement('canvas');
            const ctx = labelCanvas.getContext('2d');
            labelCanvas.width = 256;
            labelCanvas.height = 64;
            ctx.fillStyle = isEndpoint ? '#ef4444' : '#f87171';
            ctx.font = 'bold 20px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(chainLabels[i], 128, 40);
            const texture = new THREE.CanvasTexture(labelCanvas);
            const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true }));
            sprite.scale.set(4, 1, 1);
            sprite.position.set(pos.x, pos.y - 1.8, pos.z);
            scene.add(sprite);
        });
        
        // Draw the layering chain connections (thick red lines)
        const pathMat = new THREE.LineBasicMaterial({ color: 0xef4444, transparent: true, opacity: 0.9, linewidth: 2 });
        for (let i = 0; i < chainNodes.length - 1; i++) {
            const curve = new THREE.CatmullRomCurve3([
                chainNodes[i].position.clone(),
                new THREE.Vector3(
                    (chainNodes[i].position.x + chainNodes[i+1].position.x) / 2,
                    (chainNodes[i].position.y + chainNodes[i+1].position.y) / 2 + 1,
                    (chainNodes[i].position.z + chainNodes[i+1].position.z) / 2
                ),
                chainNodes[i+1].position.clone()
            ]);
            const points = curve.getPoints(30);
            const geo = new THREE.BufferGeometry().setFromPoints(points);
            scene.add(new THREE.Line(geo, pathMat));
        }
        
        // Add background legitimate nodes (green, scattered)
        const legitimateNodes = [];
        const legitGeo = new THREE.SphereGeometry(0.25, 16, 16);
        for (let i = 0; i < 20; i++) {
            const legitMat = new THREE.MeshBasicMaterial({ color: 0x22c55e, transparent: true, opacity: 0.4 });
            const node = new THREE.Mesh(legitGeo, legitMat);
            node.position.set(
                (Math.random() - 0.5) * 28,
                (Math.random() - 0.5) * 10,
                (Math.random() - 0.5) * 14 - 5
            );
            scene.add(node);
            legitimateNodes.push(node);
        }
        
        // Connect some legitimate nodes with faint lines
        const legitEdgeMat = new THREE.LineBasicMaterial({ color: 0x334155, transparent: true, opacity: 0.15 });
        for (let i = 0; i < legitimateNodes.length; i++) {
            for (let j = i + 1; j < legitimateNodes.length; j++) {
                if (Math.random() > 0.85) {
                    const points = [legitimateNodes[i].position, legitimateNodes[j].position];
                    const geo = new THREE.BufferGeometry().setFromPoints(points);
                    scene.add(new THREE.Line(geo, legitEdgeMat));
                }
            }
        }
        
        // Moving funds particle
        const fundsGeo = new THREE.SphereGeometry(0.5, 24, 24);
        const fundsMat = new THREE.MeshPhongMaterial({ 
            color: 0xf97316, 
            emissive: 0xf97316, 
            emissiveIntensity: 0.8
        });
        const fundsParticle = new THREE.Mesh(fundsGeo, fundsMat);
        scene.add(fundsParticle);
        
        // Funds glow
        const fundsGlowGeo = new THREE.SphereGeometry(0.9, 16, 16);
        const fundsGlowMat = new THREE.MeshBasicMaterial({ color: 0xf97316, transparent: true, opacity: 0.3 });
        const fundsGlow = new THREE.Mesh(fundsGlowGeo, fundsGlowMat);
        scene.add(fundsGlow);
        
        // Time window ring
        const ringGeo = new THREE.TorusGeometry(10, 0.06, 16, 100);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0x0ea5e9, transparent: true, opacity: 0.25 });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = Math.PI / 2;
        ring.position.y = -3;
        scene.add(ring);
        
        // Grid
        const gridHelper = new THREE.GridHelper(30, 30, 0x1e3a5f, 0x0f172a);
        gridHelper.position.y = -5;
        scene.add(gridHelper);
        
        let t = 0;
        const walletNames = ['WALLET_A', 'WALLET_B', 'WALLET_C', 'WALLET_D', 'WALLET_E'];
        const amounts = ['2.45', '2.40', '2.35', '2.30', '2.25'];
        
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            const time = performance.now() * 0.001;
            
            t += 0.003;
            if (t > 1) t = 0;
            
            // Calculate current segment and position
            const totalSegments = chainNodes.length - 1;
            const segment = Math.floor(t * totalSegments);
            const localT = (t * totalSegments) - segment;
            
            const startNode = chainNodes[segment];
            const endNode = chainNodes[Math.min(segment + 1, chainNodes.length - 1)];
            
            // Smooth curved path
            const midPoint = new THREE.Vector3().lerpVectors(startNode.position, endNode.position, 0.5);
            midPoint.y += 1;
            
            const curveT = localT;
            const p0 = startNode.position;
            const p1 = midPoint;
            const p2 = endNode.position;
            
            // Quadratic bezier
            const invT = 1 - curveT;
            fundsParticle.position.x = invT * invT * p0.x + 2 * invT * curveT * p1.x + curveT * curveT * p2.x;
            fundsParticle.position.y = invT * invT * p0.y + 2 * invT * curveT * p1.y + curveT * curveT * p2.y;
            fundsParticle.position.z = invT * invT * p0.z + 2 * invT * curveT * p1.z + curveT * curveT * p2.z;
            
            fundsGlow.position.copy(fundsParticle.position);
            fundsGlow.scale.setScalar(1 + Math.sin(time * 5) * 0.2);
            
            // Update UI
            const currentHop = segment + 1;
            const hopEl = document.getElementById('advisory-hop');
            const statusEl = document.getElementById('advisory-status');
            const fromEl = document.getElementById('graph-from');
            const toEl = document.getElementById('graph-to');
            const amountEl = document.getElementById('graph-amount');
            
            if (hopEl) hopEl.textContent = currentHop + ' / ' + totalSegments;
            if (statusEl) statusEl.textContent = currentHop >= totalSegments ? 'TRACED!' : 'TRACING...';
            if (fromEl) fromEl.innerHTML = '<span style="color:#94a3b8;">From:</span> <span style="color:#ef4444;font-weight:600;">' + walletNames[segment] + '</span>';
            if (toEl) toEl.innerHTML = '<span style="color:#94a3b8;">To:</span> <span style="color:#ef4444;font-weight:600;">' + walletNames[Math.min(segment + 1, walletNames.length - 1)] + '</span>';
            if (amountEl) amountEl.innerHTML = '<span style="color:#94a3b8;">Amount:</span> <span style="color:#f97316;font-weight:600;">' + amounts[segment] + ' BTC</span>';
            
            // Animate chain nodes
            chainNodes.forEach((node, i) => {
                node.position.y = chainPositions[i].y + Math.sin(time + i) * 0.15;
            });
            
            // Ring rotation
            ring.rotation.z += 0.002;
            
            // Pulsing path
            pathMat.opacity = 0.6 + Math.sin(time * 2) * 0.3;
            
            renderer.render(scene, camera);
        }
        animate();
        
        window.addEventListener('resize', () => {
            const w = wrapper.clientWidth;
            const h = wrapper.clientHeight || 650;
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
        });
    }
    setTimeout(initVtacGraph, 900);
})();
        ''')



def create_mobile_bitcoin_animation():
    """Create a 3D animation showing two mobile phones sending Bitcoin to each other"""
    
    with ui.column().classes('w-full gap-8'):
        
        # Description
        ui.label('Watch a real-time visualization of peer-to-peer Bitcoin transfer between two mobile devices').classes(
            'text-xl dark:text-gray-300 text-gray-600 mb-4'
        )
        
        # Mobile Bitcoin Transfer Animation Container
        ui.html("""<div id="mobile-btc-wrapper" style="width: 100%; height: 700px; position: relative; border-radius: 24px; overflow: hidden; background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); box-shadow: 0 0 60px rgba(247, 147, 26, 0.3);" class="animations-page-active">
    <canvas id="mobile-btc-canvas" style="width: 100%; height: 100%; display: block;"></canvas>
    
    <!-- Title Banner -->
    <div style="position: absolute; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(20px); padding: 12px 30px; border-radius: 12px; border: 2px solid rgba(247, 147, 26, 0.5); text-align: center; z-index: 10; box-shadow: 0 0 30px rgba(247, 147, 26, 0.3);">
        <div style="color: #f7931a; font-size: 20px; font-weight: 900; letter-spacing: 2px; font-family: 'Space Grotesk', sans-serif;">BITCOIN P2P TRANSFER</div>
        <div style="color: #94a3b8; font-size: 11px; margin-top: 4px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Real-time Blockchain Transaction Visualization</div>
    </div>
    
    <!-- Transaction Info Panel -->
    <div style="position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(20px); padding: 15px 25px; border-radius: 12px; color: #f1f5f9; font-family: 'Inter', sans-serif; border: 1px solid rgba(247, 147, 26, 0.3); z-index: 10; display: flex; gap: 30px; align-items: center;">
        <div style="text-align: center;">
            <div style="color: #94a3b8; font-size: 11px; text-transform: uppercase;">Sender</div>
            <div id="btc-sender" style="color: #22c55e; font-weight: 800; font-size: 14px;">Device A</div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div id="btc-amount" style="color: #f7931a; font-weight: 900; font-size: 18px;">0.0000 BTC</div>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f7931a" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
        </div>
        <div style="text-align: center;">
            <div style="color: #94a3b8; font-size: 11px; text-transform: uppercase;">Receiver</div>
            <div id="btc-receiver" style="color: #3b82f6; font-weight: 800; font-size: 14px;">Device B</div>
        </div>
    </div>
    
    <!-- Stats Panel -->
    <div style="position: absolute; top: 20px; right: 20px; background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(20px); padding: 15px; border-radius: 12px; color: #f1f5f9; font-family: 'Inter', sans-serif; min-width: 180px; border: 1px solid rgba(247, 147, 26, 0.3); z-index: 10;">
        <div style="font-weight: 800; margin-bottom: 12px; font-size: 12px; color: #f7931a; border-bottom: 1px solid rgba(247, 147, 26, 0.3); padding-bottom: 8px;">TRANSACTION STATS</div>
        <div style="margin: 8px 0; display: flex; justify-content: space-between; font-size: 12px;">
            <span style="color: #94a3b8;">Transfers:</span>
            <span id="btc-transfers" style="color: #22c55e; font-weight: 700;">0</span>
        </div>
        <div style="margin: 8px 0; display: flex; justify-content: space-between; font-size: 12px;">
            <span style="color: #94a3b8;">Total BTC:</span>
            <span id="btc-total" style="color: #f7931a; font-weight: 700;">0.0000</span>
        </div>
        <div style="margin: 8px 0; display: flex; justify-content: space-between; font-size: 12px;">
            <span style="color: #94a3b8;">Confirmations:</span>
            <span id="btc-confirmations" style="color: #8b5cf6; font-weight: 700;">0</span>
        </div>
    </div>
</div>
""").classes('w-full')
        
        # Three.js Mobile Bitcoin Animation Script
        ui.run_javascript('''
(function() {
    "use strict";
    
    function initMobileBtcAnimation() {
        const canvas = document.getElementById("mobile-btc-canvas");
        const wrapper = document.getElementById("mobile-btc-wrapper");
        if (!canvas || !wrapper || typeof THREE === 'undefined') {
            setTimeout(initMobileBtcAnimation, 500);
            return;
        }
        
        const width = wrapper.clientWidth;
        const height = wrapper.clientHeight || 700;
        
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0f172a);
        
        const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
        camera.position.set(0, 5, 25);
        
        const renderer = new THREE.WebGLRenderer({ 
            canvas: canvas, 
            antialias: true, 
            alpha: true 
        });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxDistance = 50;
        controls.minDistance = 10;
        
        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        scene.add(ambientLight);
        
        const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
        mainLight.position.set(10, 20, 10);
        mainLight.castShadow = true;
        scene.add(mainLight);
        
        const btcLight = new THREE.PointLight(0xf7931a, 2, 30);
        btcLight.position.set(0, 5, 5);
        scene.add(btcLight);
        
        // Create Mobile Phone Function
        function createPhone(color, posX) {
            const phoneGroup = new THREE.Group();
            
            // Phone body
            const bodyGeo = new THREE.BoxGeometry(3, 6, 0.3);
            const bodyMat = new THREE.MeshPhongMaterial({ 
                color: color,
                shininess: 100,
                specular: 0x444444
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            body.receiveShadow = true;
            phoneGroup.add(body);
            
            // Screen
            const screenGeo = new THREE.BoxGeometry(2.6, 5.2, 0.05);
            const screenMat = new THREE.MeshPhongMaterial({ 
                color: 0x1a1a2e,
                emissive: 0x0a0a14,
                emissiveIntensity: 0.3,
                shininess: 150
            });
            const screen = new THREE.Mesh(screenGeo, screenMat);
            screen.position.z = 0.18;
            phoneGroup.add(screen);
            
            // Screen glow border
            const glowGeo = new THREE.BoxGeometry(2.7, 5.3, 0.02);
            const glowMat = new THREE.MeshBasicMaterial({ 
                color: color === 0x22c55e ? 0x22c55e : 0x3b82f6,
                transparent: true,
                opacity: 0.5
            });
            const glow = new THREE.Mesh(glowGeo, glowMat);
            glow.position.z = 0.16;
            phoneGroup.add(glow);
            
            // Camera notch
            const notchGeo = new THREE.CylinderGeometry(0.15, 0.15, 0.1, 16);
            const notchMat = new THREE.MeshPhongMaterial({ color: 0x111111 });
            const notch = new THREE.Mesh(notchGeo, notchMat);
            notch.rotation.x = Math.PI / 2;
            notch.position.set(0, 2.3, 0.2);
            phoneGroup.add(notch);
            
            // Home button indicator
            const homeBtnGeo = new THREE.BoxGeometry(0.8, 0.15, 0.02);
            const homeBtnMat = new THREE.MeshBasicMaterial({ 
                color: 0x333333
            });
            const homeBtn = new THREE.Mesh(homeBtnGeo, homeBtnMat);
            homeBtn.position.set(0, -2.5, 0.2);
            phoneGroup.add(homeBtn);
            
            phoneGroup.position.x = posX;
            return phoneGroup;
        }
        
        // Create Bitcoin symbol
        function createBitcoinCoin() {
            const coinGroup = new THREE.Group();
            
            // Main coin
            const coinGeo = new THREE.CylinderGeometry(0.8, 0.8, 0.15, 32);
            const coinMat = new THREE.MeshPhongMaterial({ 
                color: 0xf7931a,
                emissive: 0xf7931a,
                emissiveIntensity: 0.3,
                shininess: 200,
                specular: 0xffaa00
            });
            const coin = new THREE.Mesh(coinGeo, coinMat);
            coin.rotation.x = Math.PI / 2;
            coinGroup.add(coin);
            
            // Bitcoin B symbol (simplified as torus knot for visual effect)
            const symbolGeo = new THREE.TorusGeometry(0.3, 0.08, 8, 24);
            const symbolMat = new THREE.MeshBasicMaterial({ 
                color: 0xffffff,
                transparent: true,
                opacity: 0.9
            });
            const symbol = new THREE.Mesh(symbolGeo, symbolMat);
            symbol.position.z = 0.1;
            coinGroup.add(symbol);
            
            // Glow effect
            const glowGeo = new THREE.SphereGeometry(1.2, 16, 16);
            const glowMat = new THREE.MeshBasicMaterial({ 
                color: 0xf7931a,
                transparent: true,
                opacity: 0.15
            });
            const glow = new THREE.Mesh(glowGeo, glowMat);
            coinGroup.add(glow);
            
            return coinGroup;
        }
        
        // Create phones
        const phoneA = createPhone(0x1e293b, -8);
        const phoneB = createPhone(0x1e293b, 8);
        scene.add(phoneA);
        scene.add(phoneB);
        
        // Add phone labels
        function createLabel(text, color) {
            const canvas2d = document.createElement('canvas');
            const ctx = canvas2d.getContext('2d');
            canvas2d.width = 256;
            canvas2d.height = 64;
            ctx.fillStyle = color;
            ctx.font = 'bold 32px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(text, 128, 45);
            
            const texture = new THREE.CanvasTexture(canvas2d);
            const spriteMat = new THREE.SpriteMaterial({ map: texture, transparent: true });
            const sprite = new THREE.Sprite(spriteMat);
            sprite.scale.set(4, 1, 1);
            return sprite;
        }
        
        const labelA = createLabel('SENDER', '#22c55e');
        labelA.position.set(-8, -5, 0);
        scene.add(labelA);
        
        const labelB = createLabel('RECEIVER', '#3b82f6');
        labelB.position.set(8, -5, 0);
        scene.add(labelB);
        
        // Transaction particles
        const particles = [];
        const particleGeo = new THREE.SphereGeometry(0.1, 8, 8);
        const particleMat = new THREE.MeshBasicMaterial({ color: 0xf7931a });
        
        // Bitcoin coins in transit
        const btcCoins = [];
        let direction = 1; // 1 = A to B, -1 = B to A
        let transfers = 0;
        let totalBtc = 0;
        let confirmations = 0;
        
        function createTransaction() {
            const coin = createBitcoinCoin();
            const startX = direction === 1 ? -8 : 8;
            const endX = direction === 1 ? 8 : -8;
            
            coin.position.set(startX, 0, 2);
            coin.userData = {
                startX: startX,
                endX: endX,
                progress: 0,
                speed: 0.008 + Math.random() * 0.004,
                amount: (Math.random() * 0.5 + 0.01).toFixed(4),
                yOffset: (Math.random() - 0.5) * 2,
                rotationSpeed: 0.05 + Math.random() * 0.05
            };
            
            scene.add(coin);
            btcCoins.push(coin);
            
            // Update UI
            document.getElementById("btc-amount").textContent = coin.userData.amount + " BTC";
            document.getElementById("btc-sender").textContent = direction === 1 ? "Device A" : "Device B";
            document.getElementById("btc-receiver").textContent = direction === 1 ? "Device B" : "Device A";
            
            // Create trail particles
            for (let i = 0; i < 5; i++) {
                setTimeout(() => {
                    const particle = new THREE.Mesh(particleGeo, particleMat.clone());
                    particle.position.copy(coin.position);
                    particle.userData = { life: 1, coin: coin };
                    scene.add(particle);
                    particles.push(particle);
                }, i * 50);
            }
        }
        
        // Initial transaction
        setTimeout(createTransaction, 1000);
        
        // Create new transaction periodically
        setInterval(() => {
            if (btcCoins.length < 3) {
                createTransaction();
            }
        }, 2500);
        
        // Add blockchain network visualization in background
        const networkNodes = [];
        for (let i = 0; i < 20; i++) {
            const nodeGeo = new THREE.SphereGeometry(0.15, 8, 8);
            const nodeMat = new THREE.MeshBasicMaterial({ 
                color: 0x22c55e,
                transparent: true,
                opacity: 0.3
            });
            const node = new THREE.Mesh(nodeGeo, nodeMat);
            node.position.set(
                (Math.random() - 0.5) * 30,
                (Math.random() - 0.5) * 15,
                -10 + Math.random() * -10
            );
            scene.add(node);
            networkNodes.push(node);
        }
        
        // Connect nodes with lines
        const lineMat = new THREE.LineBasicMaterial({ color: 0x22c55e, transparent: true, opacity: 0.1 });
        for (let i = 0; i < networkNodes.length; i++) {
            for (let j = i + 1; j < networkNodes.length; j++) {
                if (Math.random() > 0.7) {
                    const points = [networkNodes[i].position, networkNodes[j].position];
                    const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
                    const line = new THREE.Line(lineGeo, lineMat);
                    scene.add(line);
                }
            }
        }
        
        // Ground plane with grid
        const gridHelper = new THREE.GridHelper(40, 40, 0x1e3a5f, 0x0f172a);
        gridHelper.position.y = -6;
        scene.add(gridHelper);
        
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            
            const time = performance.now() * 0.001;
            
            // Animate phones (gentle floating)
            phoneA.position.y = Math.sin(time * 0.5) * 0.3;
            phoneA.rotation.y = Math.sin(time * 0.3) * 0.1;
            phoneB.position.y = Math.sin(time * 0.5 + Math.PI) * 0.3;
            phoneB.rotation.y = Math.sin(time * 0.3 + Math.PI) * 0.1;
            
            // Animate Bitcoin coins
            btcCoins.forEach((coin, index) => {
                coin.userData.progress += coin.userData.speed;
                
                const progress = coin.userData.progress;
                const startX = coin.userData.startX;
                const endX = coin.userData.endX;
                
                // Bezier-like curve path
                const t = progress;
                const heightCurve = Math.sin(t * Math.PI) * 4;
                
                coin.position.x = startX + (endX - startX) * t;
                coin.position.y = heightCurve + coin.userData.yOffset;
                coin.position.z = 2 + Math.sin(t * Math.PI * 2) * 0.5;
                
                // Rotate coin
                coin.rotation.y += coin.userData.rotationSpeed;
                coin.rotation.z = Math.sin(time * 3) * 0.2;
                
                // Scale pulsing
                const scale = 1 + Math.sin(time * 5) * 0.1;
                coin.scale.setScalar(scale);
                
                // Transaction complete
                if (progress >= 1) {
                    scene.remove(coin);
                    btcCoins.splice(index, 1);
                    
                    transfers++;
                    totalBtc += parseFloat(coin.userData.amount);
                    confirmations += Math.floor(Math.random() * 3) + 1;
                    
                    // Update stats
                    document.getElementById("btc-transfers").textContent = transfers;
                    document.getElementById("btc-total").textContent = totalBtc.toFixed(4);
                    document.getElementById("btc-confirmations").textContent = confirmations;
                    
                    // Switch direction
                    direction *= -1;
                    
                    // Flash effect on receiving phone
                    const targetPhone = direction === -1 ? phoneB : phoneA;
                    const originalColor = targetPhone.children[2].material.opacity;
                    targetPhone.children[2].material.opacity = 1;
                    setTimeout(() => {
                        targetPhone.children[2].material.opacity = originalColor;
                    }, 200);
                }
            });
            
            // Animate particles (trails)
            particles.forEach((particle, index) => {
                particle.userData.life -= 0.02;
                particle.material.opacity = particle.userData.life;
                particle.scale.setScalar(particle.userData.life);
                
                if (particle.userData.life <= 0) {
                    scene.remove(particle);
                    particles.splice(index, 1);
                }
            });
            
            // Animate background network nodes
            networkNodes.forEach((node, i) => {
                node.material.opacity = 0.2 + Math.sin(time + i) * 0.1;
            });
            
            // Animate BTC light
            btcLight.intensity = 1.5 + Math.sin(time * 2) * 0.5;
            
            renderer.render(scene, camera);
        }
        
        animate();
        
        window.addEventListener("resize", () => {
            const w = wrapper.clientWidth;
            const h = wrapper.clientHeight || 700;
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
        });
    }
    
    // Delayed init to ensure THREE is ready
    setTimeout(initMobileBtcAnimation, 1500);
})();
        ''')
        
        # Feature cards explaining the animation
        with ui.row().classes('w-full justify-around flex-wrap gap-6 mt-8'):
            with ui.card().classes('step-card flex-1 min-w-[250px]'):
                with ui.row().classes('items-center gap-4 mb-4'):
                    ui.icon('phone_android', size='2.5rem').classes('text-green-400')
                    ui.label('P2P Transfer').classes('text-xl font-bold dark:text-white text-gray-900')
                ui.label('Direct device-to-device Bitcoin transactions without intermediaries').classes(
                    'dark:text-gray-300 text-gray-600'
                )
            
            with ui.card().classes('step-card flex-1 min-w-[250px]'):
                with ui.row().classes('items-center gap-4 mb-4'):
                    ui.icon('currency_bitcoin', size='2.5rem').classes('text-orange-400')
                    ui.label('Bitcoin Network').classes('text-xl font-bold dark:text-white text-gray-900')
                ui.label('Transactions are broadcast to the decentralized Bitcoin network for validation').classes(
                    'dark:text-gray-300 text-gray-600'
                )
            
            with ui.card().classes('step-card flex-1 min-w-[250px]'):
                with ui.row().classes('items-center gap-4 mb-4'):
                    ui.icon('verified', size='2.5rem').classes('text-blue-400')
                    ui.label('Confirmations').classes('text-xl font-bold dark:text-white text-gray-900')
                ui.label('Multiple network confirmations ensure transaction finality and security').classes(
                    'dark:text-gray-300 text-gray-600'
                )


def create_attack_detection_animation():
    """Create 3D animation showing attack detection and admin alert - per VTAC paper"""
    
    with ui.column().classes('w-full gap-6'):
        ui.label('Visualization of VTAC real-time attack detection: Transaction processing → Attack detected → Instant admin alert').classes(
            'text-xl dark:text-gray-300 text-gray-600 mb-4'
        )
        
        # Status panel that updates during the animation
        with ui.row().classes('w-full justify-around flex-wrap gap-4 mb-6'):
            with ui.card().classes('step-card flex-1 min-w-[180px] text-center'):
                ui.label('Transaction Status').classes('text-sm dark:text-gray-400 text-gray-500 mb-2')
                ui.html('<div id="attack-tx-status" class="text-xl font-bold text-blue-400">PROCESSING</div>')
            
            with ui.card().classes('step-card flex-1 min-w-[180px] text-center'):
                ui.label('VTAC Risk Score').classes('text-sm dark:text-gray-400 text-gray-500 mb-2')
                ui.html('<div id="attack-risk-score" class="text-xl font-bold text-green-400">0.00</div>')
            
            with ui.card().classes('step-card flex-1 min-w-[180px] text-center'):
                ui.label('Attack Type').classes('text-sm dark:text-gray-400 text-gray-500 mb-2')
                ui.html('<div id="attack-type" class="text-xl font-bold text-gray-500">NONE</div>')
            
            with ui.card().classes('step-card flex-1 min-w-[180px] text-center'):
                ui.label('Admin Alert').classes('text-sm dark:text-gray-400 text-gray-500 mb-2')
                ui.html('<div id="attack-admin-alert" class="text-xl font-bold text-gray-500">STANDBY</div>')
        
        # 3D Canvas
        with ui.element('div').classes('w-full').style('position: relative;') as wrapper:
            wrapper.props('id="attack-detection-wrapper"')
            ui.html('<canvas id="attack-detection-canvas" style="width: 100%; height: 700px; border-radius: 16px;"></canvas>')
        
        # Inject the Three.js attack detection scene
        ui.run_javascript('''
(function() {
    function initAttackDetectionAnimation() {
        const wrapper = document.getElementById("attack-detection-wrapper");
        const canvas = document.getElementById("attack-detection-canvas");
        if (!wrapper || !canvas || typeof THREE === "undefined") {
            setTimeout(initAttackDetectionAnimation, 300);
            return;
        }
        
        const width = wrapper.clientWidth;
        const height = wrapper.clientHeight || 700;
        
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x050510);
        
        const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 1000);
        camera.position.set(0, 8, 25);
        camera.lookAt(0, 0, 0);
        
        const renderer = new THREE.WebGLRenderer({ 
            canvas: canvas, 
            antialias: true, 
            alpha: true 
        });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxDistance = 50;
        controls.minDistance = 10;
        
        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
        scene.add(ambientLight);
        
        const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
        mainLight.position.set(10, 20, 10);
        mainLight.castShadow = true;
        scene.add(mainLight);
        
        // Alert light (starts off, activates on attack)
        const alertLight = new THREE.PointLight(0xff0000, 0, 50);
        alertLight.position.set(0, 10, 0);
        scene.add(alertLight);
        
        // Grid
        const gridHelper = new THREE.GridHelper(50, 50, 0x1e3a5f, 0x0f172a);
        gridHelper.position.y = -5;
        scene.add(gridHelper);
        
        // Create Server/Node meshes
        function createServer(x, z, color, label) {
            const group = new THREE.Group();
            
            // Server box
            const boxGeo = new THREE.BoxGeometry(2.5, 3, 1.5);
            const boxMat = new THREE.MeshPhongMaterial({ 
                color: color,
                emissive: color,
                emissiveIntensity: 0.1,
                shininess: 100
            });
            const box = new THREE.Mesh(boxGeo, boxMat);
            box.castShadow = true;
            group.add(box);
            
            // Server LED lights
            for (let i = 0; i < 4; i++) {
                const ledGeo = new THREE.SphereGeometry(0.08, 8, 8);
                const ledMat = new THREE.MeshBasicMaterial({ color: 0x22c55e });
                const led = new THREE.Mesh(ledGeo, ledMat);
                led.position.set(-0.8 + i * 0.5, 1, 0.8);
                led.userData.baseColor = 0x22c55e;
                group.add(led);
            }
            
            // Label
            const canvas2d = document.createElement("canvas");
            const ctx = canvas2d.getContext("2d");
            canvas2d.width = 256;
            canvas2d.height = 64;
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 24px Arial";
            ctx.textAlign = "center";
            ctx.fillText(label, 128, 45);
            
            const texture = new THREE.CanvasTexture(canvas2d);
            const spriteMat = new THREE.SpriteMaterial({ map: texture, transparent: true });
            const sprite = new THREE.Sprite(spriteMat);
            sprite.scale.set(4, 1, 1);
            sprite.position.y = 2.5;
            group.add(sprite);
            
            group.position.set(x, 0, z);
            return group;
        }
        
        // Create Admin Panel
        function createAdminPanel() {
            const group = new THREE.Group();
            
            // Monitor stand
            const standGeo = new THREE.CylinderGeometry(0.3, 0.5, 1, 16);
            const standMat = new THREE.MeshPhongMaterial({ color: 0x333333 });
            const stand = new THREE.Mesh(standGeo, standMat);
            stand.position.y = -1;
            group.add(stand);
            
            // Monitor frame
            const frameGeo = new THREE.BoxGeometry(5, 3.5, 0.3);
            const frameMat = new THREE.MeshPhongMaterial({ color: 0x1a1a2e });
            const frame = new THREE.Mesh(frameGeo, frameMat);
            group.add(frame);
            
            // Screen
            const screenGeo = new THREE.BoxGeometry(4.5, 3, 0.05);
            const screenMat = new THREE.MeshBasicMaterial({ 
                color: 0x0a192f,
                transparent: true,
                opacity: 0.9
            });
            const screen = new THREE.Mesh(screenGeo, screenMat);
            screen.position.z = 0.18;
            group.add(screen);
            
            // Screen content (dashboard elements)
            const dashGeo = new THREE.PlaneGeometry(4, 2.5);
            const dashCanvas = document.createElement("canvas");
            const dashCtx = dashCanvas.getContext("2d");
            dashCanvas.width = 400;
            dashCanvas.height = 250;
            
            function drawDashboard(alertActive) {
                dashCtx.fillStyle = "#0a192f";
                dashCtx.fillRect(0, 0, 400, 250);
                
                // Header
                dashCtx.fillStyle = alertActive ? "#ef4444" : "#22c55e";
                dashCtx.font = "bold 18px Arial";
                dashCtx.fillText("VTAC ADMIN DASHBOARD", 20, 30);
                
                // Status indicators
                dashCtx.fillStyle = "#94a3b8";
                dashCtx.font = "12px Arial";
                dashCtx.fillText("System Status:", 20, 60);
                dashCtx.fillStyle = alertActive ? "#ef4444" : "#22c55e";
                dashCtx.fillText(alertActive ? "ALERT ACTIVE" : "MONITORING", 120, 60);
                
                // Transaction count
                dashCtx.fillStyle = "#94a3b8";
                dashCtx.fillText("Transactions:", 20, 85);
                dashCtx.fillStyle = "#60a5fa";
                dashCtx.fillText("1,247", 120, 85);
                
                // Risk level
                dashCtx.fillStyle = "#94a3b8";
                dashCtx.fillText("Risk Level:", 20, 110);
                dashCtx.fillStyle = alertActive ? "#ef4444" : "#22c55e";
                dashCtx.fillText(alertActive ? "CRITICAL" : "LOW", 120, 110);
                
                // Alert box
                if (alertActive) {
                    dashCtx.strokeStyle = "#ef4444";
                    dashCtx.lineWidth = 2;
                    dashCtx.strokeRect(15, 130, 370, 100);
                    
                    dashCtx.fillStyle = "#ef4444";
                    dashCtx.font = "bold 16px Arial";
                    dashCtx.fillText("⚠ ATTACK DETECTED", 20, 155);
                    
                    dashCtx.fillStyle = "#f87171";
                    dashCtx.font = "12px Arial";
                    dashCtx.fillText("Type: Money Laundering Pattern", 20, 180);
                    dashCtx.fillText("VTAC Score: 0.92 (CRITICAL)", 20, 200);
                    dashCtx.fillText("Action: Transaction BLOCKED", 20, 220);
                }
            }
            
            drawDashboard(false);
            
            const dashTexture = new THREE.CanvasTexture(dashCanvas);
            const dashMat = new THREE.MeshBasicMaterial({ map: dashTexture, transparent: true });
            const dash = new THREE.Mesh(dashGeo, dashMat);
            dash.position.z = 0.2;
            dash.userData.canvas = dashCanvas;
            dash.userData.ctx = dashCtx;
            dash.userData.texture = dashTexture;
            dash.userData.drawDashboard = drawDashboard;
            group.add(dash);
            
            // Admin label
            const labelCanvas = document.createElement("canvas");
            const labelCtx = labelCanvas.getContext("2d");
            labelCanvas.width = 256;
            labelCanvas.height = 64;
            labelCtx.fillStyle = "#a855f7";
            labelCtx.font = "bold 24px Arial";
            labelCtx.textAlign = "center";
            labelCtx.fillText("ADMIN CONSOLE", 128, 45);
            
            const labelTexture = new THREE.CanvasTexture(labelCanvas);
            const labelSprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: labelTexture, transparent: true }));
            labelSprite.scale.set(4, 1, 1);
            labelSprite.position.y = 2.5;
            group.add(labelSprite);
            
            return group;
        }
        
        // Create transaction packet
        function createTransactionPacket(isMalicious) {
            const group = new THREE.Group();
            
            const color = isMalicious ? 0xef4444 : 0x22c55e;
            
            // Outer glow
            const glowGeo = new THREE.SphereGeometry(0.8, 16, 16);
            const glowMat = new THREE.MeshBasicMaterial({ 
                color: color,
                transparent: true,
                opacity: 0.2
            });
            const glow = new THREE.Mesh(glowGeo, glowMat);
            group.add(glow);
            
            // Core
            const coreGeo = new THREE.IcosahedronGeometry(0.4, 1);
            const coreMat = new THREE.MeshPhongMaterial({ 
                color: color,
                emissive: color,
                emissiveIntensity: 0.5,
                shininess: 150
            });
            const core = new THREE.Mesh(coreGeo, coreMat);
            group.add(core);
            
            group.userData.isMalicious = isMalicious;
            return group;
        }
        
        // Create alert beacon
        function createAlertBeacon() {
            const group = new THREE.Group();
            
            // Base
            const baseGeo = new THREE.CylinderGeometry(0.5, 0.7, 0.5, 16);
            const baseMat = new THREE.MeshPhongMaterial({ color: 0x333333 });
            const base = new THREE.Mesh(baseGeo, baseMat);
            group.add(base);
            
            // Light dome
            const domeGeo = new THREE.SphereGeometry(0.6, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2);
            const domeMat = new THREE.MeshBasicMaterial({ 
                color: 0xff0000,
                transparent: true,
                opacity: 0.3
            });
            const dome = new THREE.Mesh(domeGeo, domeMat);
            dome.position.y = 0.3;
            group.add(dome);
            
            // Inner light
            const innerGeo = new THREE.SphereGeometry(0.3, 16, 16);
            const innerMat = new THREE.MeshBasicMaterial({ 
                color: 0xff0000,
                transparent: true,
                opacity: 0.8
            });
            const inner = new THREE.Mesh(innerGeo, innerMat);
            inner.position.y = 0.4;
            group.add(inner);
            
            group.userData.dome = dome;
            group.userData.inner = inner;
            group.visible = false;
            return group;
        }
        
        // Build scene
        const senderServer = createServer(-12, 0, 0x3b82f6, "SENDER");
        const vtacServer = createServer(0, 0, 0x22c55e, "VTAC SYSTEM");
        const receiverServer = createServer(12, 0, 0x06b6d4, "RECEIVER");
        const adminPanel = createAdminPanel();
        adminPanel.position.set(0, 2, 10);
        adminPanel.rotation.x = -0.2;
        
        const alertBeacon = createAlertBeacon();
        alertBeacon.position.set(0, 5, 0);
        
        scene.add(senderServer);
        scene.add(vtacServer);
        scene.add(receiverServer);
        scene.add(adminPanel);
        scene.add(alertBeacon);
        
        // Connection lines
        const lineMat = new THREE.LineBasicMaterial({ color: 0x22c55e, transparent: true, opacity: 0.3 });
        
        const points1 = [new THREE.Vector3(-12, 0, 0), new THREE.Vector3(0, 0, 0)];
        const line1 = new THREE.Line(new THREE.BufferGeometry().setFromPoints(points1), lineMat);
        scene.add(line1);
        
        const points2 = [new THREE.Vector3(0, 0, 0), new THREE.Vector3(12, 0, 0)];
        const line2 = new THREE.Line(new THREE.BufferGeometry().setFromPoints(points2), lineMat);
        scene.add(line2);
        
        const points3 = [new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 2, 10)];
        const line3 = new THREE.Line(new THREE.BufferGeometry().setFromPoints(points3), new THREE.LineBasicMaterial({ color: 0xa855f7, transparent: true, opacity: 0.3 }));
        scene.add(line3);
        
        // Animation state
        let phase = "normal"; // normal, attack, alert
        let phaseTime = 0;
        let transactions = [];
        let attackActive = false;
        let attackTriggered = false;
        let transactionCount = 0;
        
        const dashboard = adminPanel.children.find(c => c.userData.drawDashboard);
        
        function updateStatusUI(status, score, attackType, alertStatus, scoreColor) {
            const statusEl = document.getElementById("attack-tx-status");
            const scoreEl = document.getElementById("attack-risk-score");
            const typeEl = document.getElementById("attack-type");
            const alertEl = document.getElementById("attack-admin-alert");
            
            if (statusEl) {
                statusEl.textContent = status;
                statusEl.className = "text-xl font-bold " + (status === "BLOCKED" ? "text-red-500" : status === "APPROVED" ? "text-green-400" : "text-blue-400");
            }
            if (scoreEl) {
                scoreEl.textContent = score;
                scoreEl.className = "text-xl font-bold " + (scoreColor || "text-green-400");
            }
            if (typeEl) {
                typeEl.textContent = attackType;
                typeEl.className = "text-xl font-bold " + (attackType !== "NONE" ? "text-red-500" : "text-gray-500");
            }
            if (alertEl) {
                alertEl.textContent = alertStatus;
                alertEl.className = "text-xl font-bold " + (alertStatus === "ACTIVE" ? "text-red-500 animate-pulse" : "text-gray-500");
            }
        }
        
        function spawnTransaction(isMalicious) {
            const tx = createTransactionPacket(isMalicious);
            tx.position.set(-12, 1, 0);
            tx.userData.progress = 0;
            tx.userData.phase = "toVtac"; // toVtac, analyzing, toReceiver, blocked
            tx.userData.speed = 0.005 + Math.random() * 0.003;
            tx.userData.analyzed = false;
            scene.add(tx);
            transactions.push(tx);
            transactionCount++;
        }
        
        // Start normal transactions
        spawnTransaction(false);
        let spawnInterval = setInterval(() => {
            if (transactions.length < 3 && !attackActive) {
                spawnTransaction(false);
            }
        }, 2000);
        
        // Trigger attack after 8 seconds
        setTimeout(() => {
            if (!attackTriggered) {
                attackTriggered = true;
                phase = "attack";
                spawnTransaction(true);
            }
        }, 8000);
        
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            
            const time = performance.now() * 0.001;
            phaseTime += 0.016;
            
            // Animate servers
            senderServer.position.y = Math.sin(time * 0.5) * 0.1;
            vtacServer.position.y = Math.sin(time * 0.5 + 1) * 0.1;
            receiverServer.position.y = Math.sin(time * 0.5 + 2) * 0.1;
            
            // Animate server LEDs
            [senderServer, vtacServer, receiverServer].forEach((server, si) => {
                server.children.forEach((child, i) => {
                    if (child.userData.baseColor !== undefined) {
                        child.material.color.setHex(
                            Math.sin(time * 5 + i + si) > 0.5 ? 0x22c55e : 0x0a3a0a
                        );
                    }
                });
            });
            
            // Process transactions
            transactions.forEach((tx, index) => {
                tx.children[1].rotation.x += 0.02;
                tx.children[1].rotation.y += 0.03;
                
                // Pulse glow
                const pulseScale = 1 + Math.sin(time * 4) * 0.2;
                tx.children[0].scale.setScalar(pulseScale);
                
                if (tx.userData.phase === "toVtac") {
                    tx.userData.progress += tx.userData.speed;
                    tx.position.x = -12 + tx.userData.progress * 12;
                    tx.position.y = 1 + Math.sin(tx.userData.progress * Math.PI) * 2;
                    
                    updateStatusUI("PROCESSING", "0.15", "NONE", "STANDBY", "text-green-400");
                    
                    if (tx.userData.progress >= 1) {
                        tx.userData.phase = "analyzing";
                        tx.userData.progress = 0;
                        tx.position.set(0, 1, 0);
                    }
                }
                else if (tx.userData.phase === "analyzing") {
                    tx.userData.progress += 0.015;
                    
                    // Orbit around VTAC
                    const orbitRadius = 2;
                    tx.position.x = Math.cos(tx.userData.progress * Math.PI * 4) * orbitRadius;
                    tx.position.z = Math.sin(tx.userData.progress * Math.PI * 4) * orbitRadius;
                    tx.position.y = 1 + Math.sin(tx.userData.progress * Math.PI * 2) * 0.5;
                    
                    // Scanning effect on VTAC
                    vtacServer.children[0].material.emissiveIntensity = 0.3 + Math.sin(time * 10) * 0.2;
                    
                    const analysisScore = tx.userData.isMalicious ? 
                        (0.15 + tx.userData.progress * 0.77).toFixed(2) : 
                        (0.15 + tx.userData.progress * 0.1).toFixed(2);
                    const scoreColor = tx.userData.isMalicious && tx.userData.progress > 0.5 ? "text-red-500" : "text-yellow-400";
                    updateStatusUI("ANALYZING", analysisScore, tx.userData.isMalicious ? "SCANNING..." : "NONE", "STANDBY", scoreColor);
                    
                    if (tx.userData.progress >= 1) {
                        tx.userData.analyzed = true;
                        
                        if (tx.userData.isMalicious) {
                            tx.userData.phase = "blocked";
                            tx.userData.progress = 0;
                            attackActive = true;
                            phase = "alert";
                            
                            // Trigger alert
                            alertBeacon.visible = true;
                            alertLight.intensity = 3;
                            
                            // Update admin dashboard
                            if (dashboard) {
                                dashboard.userData.drawDashboard(true);
                                dashboard.userData.texture.needsUpdate = true;
                            }
                            
                            updateStatusUI("BLOCKED", "0.92", "LAYERING ATTACK", "ACTIVE", "text-red-500");
                        } else {
                            tx.userData.phase = "toReceiver";
                            tx.userData.progress = 0;
                        }
                    }
                }
                else if (tx.userData.phase === "toReceiver") {
                    tx.userData.progress += tx.userData.speed;
                    tx.position.x = tx.userData.progress * 12;
                    tx.position.y = 1 + Math.sin(tx.userData.progress * Math.PI) * 2;
                    tx.position.z = 0;
                    
                    updateStatusUI("APPROVED", "0.25", "NONE", "STANDBY", "text-green-400");
                    
                    if (tx.userData.progress >= 1) {
                        scene.remove(tx);
                        transactions.splice(index, 1);
                    }
                }
                else if (tx.userData.phase === "blocked") {
                    tx.userData.progress += 0.02;
                    
                    // Shake and fade
                    tx.position.x = (Math.random() - 0.5) * 0.5;
                    tx.position.z = (Math.random() - 0.5) * 0.5;
                    tx.children[0].material.opacity = 1 - tx.userData.progress;
                    tx.children[1].material.opacity = 1 - tx.userData.progress;
                    
                    // Pulse red
                    tx.children[1].material.emissiveIntensity = 0.5 + Math.sin(time * 20) * 0.5;
                    
                    if (tx.userData.progress >= 1) {
                        scene.remove(tx);
                        transactions.splice(index, 1);
                        
                        // Reset after 5 seconds
                        setTimeout(() => {
                            attackActive = false;
                            attackTriggered = false;
                            phase = "normal";
                            alertBeacon.visible = false;
                            alertLight.intensity = 0;
                            
                            if (dashboard) {
                                dashboard.userData.drawDashboard(false);
                                dashboard.userData.texture.needsUpdate = true;
                            }
                            
                            updateStatusUI("PROCESSING", "0.00", "NONE", "STANDBY", "text-green-400");
                            
                            // Schedule next attack
                            setTimeout(() => {
                                if (!attackTriggered) {
                                    attackTriggered = true;
                                    spawnTransaction(true);
                                }
                            }, 10000);
                        }, 5000);
                    }
                }
            });
            
            // Animate alert beacon
            if (alertBeacon.visible) {
                const dome = alertBeacon.userData.dome;
                const inner = alertBeacon.userData.inner;
                
                dome.material.opacity = 0.3 + Math.sin(time * 8) * 0.2;
                inner.material.opacity = 0.5 + Math.sin(time * 8) * 0.5;
                alertBeacon.rotation.y += 0.05;
                
                alertLight.intensity = 2 + Math.sin(time * 8) * 1;
            }
            
            renderer.render(scene, camera);
        }
        
        animate();
        
        window.addEventListener("resize", () => {
            const w = wrapper.clientWidth;
            const h = wrapper.clientHeight || 700;
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
        });
    }
    
    setTimeout(initAttackDetectionAnimation, 1500);
})();
        ''')
        
        # Feature explanation cards
        with ui.row().classes('w-full justify-around flex-wrap gap-6 mt-8'):
            with ui.card().classes('step-card flex-1 min-w-[250px]'):
                with ui.row().classes('items-center gap-4 mb-4'):
                    ui.icon('security', size='2.5rem').classes('text-red-400')
                    ui.label('Attack Detection').classes('text-xl font-bold dark:text-white text-gray-900')
                ui.label('VTAC system analyzes transaction patterns in real-time using ML models to detect layering, structuring, and other money laundering techniques').classes(
                    'dark:text-gray-300 text-gray-600'
                )
            
            with ui.card().classes('step-card flex-1 min-w-[250px]'):
                with ui.row().classes('items-center gap-4 mb-4'):
                    ui.icon('speed', size='2.5rem').classes('text-yellow-400')
                    ui.label('Instant Response').classes('text-xl font-bold dark:text-white text-gray-900')
                ui.label('Sub-50ms detection time ensures malicious transactions are blocked before completion, preventing fund movement through the network').classes(
                    'dark:text-gray-300 text-gray-600'
                )
            
            with ui.card().classes('step-card flex-1 min-w-[250px]'):
                with ui.row().classes('items-center gap-4 mb-4'):
                    ui.icon('notifications_active', size='2.5rem').classes('text-purple-400')
                    ui.label('Admin Alerts').classes('text-xl font-bold dark:text-white text-gray-900')
                ui.label('Administrators receive instant visual and system alerts with full transaction details, VTAC risk scores, and recommended actions').classes(
                    'dark:text-gray-300 text-gray-600'
                )


def create_process_flow():
    """Create detailed process flow explanation"""
    
    with ui.column().classes('w-full gap-6'):
        
        # Step 1
        with ui.card().classes('step-card'):
            with ui.row().classes('items-start gap-6'):
                with ui.element('div').classes('step-number'):
                    ui.label('1')
                with ui.column().classes('gap-3 flex-1'):
                    ui.label('Transaction Initiation').classes('text-2xl font-bold dark:text-white text-gray-900')
                    ui.label('A user initiates a financial transaction through the system. Transaction details including amount, sender, receiver, location, and timestamp are captured.').classes('text-lg dark:text-gray-300 text-gray-600')
                    with ui.row().classes('gap-4 mt-2 flex-wrap'):
                        ui.badge('Amount', color='blue').classes('px-3 py-1 text-sm')
                        ui.badge('Location', color='cyan').classes('px-3 py-1 text-sm')
                        ui.badge('Timestamp', color='purple').classes('px-3 py-1 text-sm')
        
        # Step 2
        with ui.card().classes('step-card'):
            with ui.row().classes('items-start gap-6'):
                with ui.element('div').classes('step-number'):
                    ui.label('2')
                with ui.column().classes('gap-3 flex-1'):
                    ui.label('AI-Powered Illegal Activity Detection').classes('text-2xl font-bold dark:text-white text-gray-900')
                    ui.label('Our machine learning model analyzes 100+ features in real-time using advanced neural networks. The AI engine has been trained on millions of transactions with 99.2% accuracy.').classes('text-lg dark:text-gray-300 text-gray-600')
                    with ui.row().classes('gap-4 mt-2 flex-wrap'):
                        ui.badge('Neural Network', color='purple').classes('px-3 py-1 text-sm')
                        ui.badge('99.2% Accuracy', color='green').classes('px-3 py-1 text-sm')
                        ui.badge('Real-time', color='orange').classes('px-3 py-1 text-sm')
        
        # Step 3
        with ui.card().classes('step-card'):
            with ui.row().classes('items-start gap-6'):
                with ui.element('div').classes('step-number'):
                    ui.label('3')
                with ui.column().classes('gap-3 flex-1'):
                    ui.label('Risk Score Calculation').classes('text-2xl font-bold dark:text-white text-gray-900')
                    ui.label('The AI model generates a risk score from 0-100. Transactions above threshold (>80) are flagged as suspicious. Multiple illegal activity patterns are detected including unusual amounts, velocity, and location anomalies.').classes('text-lg dark:text-gray-300 text-gray-600')
                    with ui.row().classes('gap-4 mt-2 flex-wrap'):
                        ui.badge('Risk Score', color='yellow').classes('px-3 py-1 text-sm')
                        ui.badge('Pattern Detection', color='red').classes('px-3 py-1 text-sm')
                        ui.badge('Threshold: 80', color='orange').classes('px-3 py-1 text-sm')
        
        # Step 4
        with ui.card().classes('step-card'):
            with ui.row().classes('items-start gap-6'):
                with ui.element('div').classes('step-number'):
                    ui.label('4')
                with ui.column().classes('gap-3 flex-1'):
                    ui.label('Blockchain Validation & Storage').classes('text-2xl font-bold dark:text-white text-gray-900')
                    ui.label('Transaction is added to the blockchain with cryptographic hash, creating an immutable audit trail. Multiple validator nodes verify the block through consensus mechanism ensuring data integrity.').classes('text-lg dark:text-gray-300 text-gray-600')
                    with ui.row().classes('gap-4 mt-2 flex-wrap'):
                        ui.badge('Cryptographic Hash', color='cyan').classes('px-3 py-1 text-sm')
                        ui.badge('Immutable', color='green').classes('px-3 py-1 text-sm')
                        ui.badge('Distributed Consensus', color='blue').classes('px-3 py-1 text-sm')
        
        # Step 5
        with ui.card().classes('step-card'):
            with ui.row().classes('items-start gap-6'):
                with ui.element('div').classes('step-number'):
                    ui.label('5')
                with ui.column().classes('gap-3 flex-1'):
                    ui.label('Decision & Alert Generation').classes('text-2xl font-bold dark:text-white text-gray-900')
                    ui.label('Based on risk score, transactions are either approved automatically or flagged for review. High-risk transactions trigger real-time alerts to analysts with detailed forensic information.').classes('text-lg dark:text-gray-300 text-gray-600')
                    with ui.row().classes('gap-4 mt-2 flex-wrap'):
                        ui.badge('Auto-Approve', color='green').classes('px-3 py-1 text-sm')
                        ui.badge('Manual Review', color='red').classes('px-3 py-1 text-sm')
                        ui.badge('Real-time Alerts', color='orange').classes('px-3 py-1 text-sm')
        
        # Summary Statistics
        with ui.row().classes('w-full justify-around flex-wrap gap-6 mt-12'):
            with ui.card().classes('step-card text-center flex-1 min-w-[200px]'):
                ui.icon('speed', size='3rem').classes('text-green-400 mb-4')
                ui.label('< 50ms').classes('text-4xl font-extrabold text-green-400 mb-2')
                ui.label('Average Detection Time').classes('text-lg dark:text-gray-300 text-gray-600')
            
            with ui.card().classes('step-card text-center flex-1 min-w-[200px]'):
                ui.icon('verified', size='3rem').classes('text-blue-400 mb-4')
                ui.label('99.2%').classes('text-4xl font-extrabold text-blue-400 mb-2')
                ui.label('Detection Accuracy').classes('text-lg dark:text-gray-300 text-gray-600')
            
            with ui.card().classes('step-card text-center flex-1 min-w-[200px]'):
                ui.icon('security', size='3rem').classes('text-purple-400 mb-4')
                ui.label('100%').classes('text-4xl font-extrabold text-purple-400 mb-2')
                ui.label('Data Integrity').classes('text-lg dark:text-gray-300 text-gray-600')
            
            with ui.card().classes('step-card text-center flex-1 min-w-[200px]'):
                ui.icon('savings', size='3rem').classes('text-cyan-400 mb-4')
                ui.label('$10M+').classes('text-4xl font-extrabold text-cyan-400 mb-2')
                ui.label('Illegal Transactions Prevented').classes('text-lg dark:text-gray-300 text-gray-600')
