"""
DocuMind AI — Custom CSS (Premium Dark Glassmorphism Theme)
"""

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e0e0ff !important; font-weight: 600;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown label {
        color: #a0a0c0 !important;
    }

    /* Glass Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; padding: 20px; margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1);
    }

    /* Hero */
    .hero-header { text-align: center; padding: 40px 20px 20px; margin-bottom: 10px; }
    .hero-title {
        font-size: 3rem; font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin-bottom: 8px;
        animation: fadeInDown 0.8s ease-out;
    }
    .hero-subtitle {
        font-size: 1.1rem; color: #8888aa; font-weight: 300;
        animation: fadeInUp 0.8s ease-out;
    }

    /* Source Badges */
    .source-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; color: #a5b4fc; margin: 2px 4px;
    }
    .source-badge-web { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.2); color: #6ee7b7; }
    .source-badge-text { background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.2); color: #fbbf24; }

    /* Stats */
    .stats-container { display: flex; justify-content: center; gap: 24px; padding: 16px 0; margin-bottom: 10px; }
    .stat-item {
        text-align: center; background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 12px 24px; min-width: 120px;
    }
    .stat-value {
        font-size: 1.6rem; font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stat-label { font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

    /* Agent Thoughts */
    .thought-step {
        background: rgba(99, 102, 241, 0.05); border-left: 3px solid #667eea;
        border-radius: 0 8px 8px 0; padding: 10px 14px; margin: 6px 0; font-size: 0.88rem; color: #c4b5fd;
    }
    .thought-label { font-weight: 600; color: #a78bfa; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.5px; }

    /* Animations */
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    .pulse-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #22c55e; animation: pulse 1.5s infinite; margin-right: 6px; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        padding: 8px 20px !important; font-weight: 500 !important; transition: all 0.3s ease !important;
    }
    .stButton > button:hover { box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important; transform: translateY(-1px) !important; }

    /* Inputs */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important; color: #e0e0ff !important;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important; box-shadow: 0 0 0 1px #667eea !important;
    }

    /* Welcome */
    .welcome-card {
        text-align: center; padding: 60px 40px; background: rgba(255,255,255,0.02);
        border: 1px dashed rgba(255,255,255,0.1); border-radius: 20px; margin: 20px auto; max-width: 600px;
    }
    .welcome-icon { font-size: 3rem; margin-bottom: 16px; }
    .welcome-text { color: #6b7280; font-size: 1rem; line-height: 1.6; }

    /* Feature Tags */
    .feature-tags { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-top: 20px; }
    .feature-tag {
        background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 8px; padding: 6px 14px; font-size: 0.78rem; color: #a5b4fc;
    }
</style>
"""
