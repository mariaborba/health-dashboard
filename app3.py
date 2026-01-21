import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL E CSS ---
st.set_page_config(page_title="DM Health - Analytics", page_icon="✚", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    
    /* --- CARDS DO TOPO --- */
    .card-wrapper {
        text-decoration: none; /* Remove sublinhado do link */
        color: inherit; /* Mantém a cor do texto */
        display: block;
    }
    
    .card-metric-orange {
        background-color: #FFF3E0;
        border-radius: 12px; padding: 15px; height: 140px;
        border: 1px solid #FFE0B2; margin-bottom: 10px;
    }
    .card-metric-green {
        background-color: #F1F8F9;
        border-radius: 12px; padding: 15px; height: 140px;
        border: 1px solid #E0F2F1; margin-bottom: 10px;
        transition: transform 0.1s; /* Efeito visual ao passar o mouse */
    }
    .card-metric-green:hover {
        transform: scale(1.02); /* Leve zoom ao passar o mouse no card linkado */
        border-color: #009688;
        cursor: pointer;
    }
    
    /* Textos dos Cards */
    .metric-title { font-size: 15px; font-weight: 600; color: #444; margin-bottom: 5px; }
    .metric-value { font-size: 14px; color: #666; margin-bottom: 25px; }
    .metric-footer { font-size: 11px; color: #999; margin-top: auto; }

    /* --- AGENDA / CALENDÁRIO --- */
    .month-selector {
        font-size: 20px; font-weight: bold; color: #00796B; text-align: center; margin-bottom: 15px;
    }

    /* Botões dos Dias (Redondos) */
    div[data-testid="stColumn"] > button {
        border-radius: 50%; height: 55px; width: 55px;
        border: none; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* DIA SEM CONSULTA (Verde Claro / Padrão) - Secondary */
    div[data-testid="stColumn"] > button[kind="secondary"] {
        background-color: #E0F2F1 !important; /* Verde bem clarinho */
        color: #00695C !important;
        border: 1px solid #B2DFDB !important;
    }

    /* DIA COM CONSULTA (Verde Escuro / Destaque) - Primary */
    div[data-testid="stColumn"] > button[kind="primary"] {
        background-color: #00796B !important; /* Verde Escuro */
        color: white !important;
        border: 2px solid #004D40 !important;
    }

    /* Botão focado/clicado */
    div[data-testid="stColumn"] > button:focus {
        box-shadow: 0 0 0 3px rgba(0, 150, 136, 0.4);
    }
    
    .agenda-header { font-size: 16px; font-weight: bold; color: #333; }

    /* Estilo para a Timeline do Prontuário */
    .timeline-item {
        border-left: 2px solid #0078D7;
        padding-left: 20px;
        margin-bottom: 20px;
        position: relative;
    }
    .timeline-dot {
        width: 12px; height: 12px; background: #0078D7; border-radius: 50%;
        position: absolute; left: -7px; top: 0;
    }
    .patient-header {
        background-color: #F8F9FA; border-radius: 10px; padding: 20px; border: 1px solid #E9ECEF;
}

</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES DE GRÁFICOS ---

def plot_gauge(valor, titulo):
    # Lógica de Cor Dinâmica (Escala Semáforo)
    if valor >= 80:
        cor = "#00C853" # Verde Forte
    elif valor >= 50:
        cor = "#FFAB00" # Laranja/Amarelo
    else:
        cor = "#D50000" # Vermelho
        
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=valor,
        title={'text': titulo, 'font': {'size': 14, 'color': '#555'}},
        number={'suffix': "%", 'font': {'color': '#333'}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#ddd"},
            'bar': {'color': cor}, 
            'bgcolor': "#f0f0f0",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 50], 'color': '#ffebee'},   # Fundo vermelho claro
                {'range': [50, 80], 'color': '#fff8e1'},  # Fundo amarelo claro
                {'range': [80, 100], 'color': '#e8f5e9'}  # Fundo verde claro
            ]
        }
    ))
    fig.update_layout(height=160, margin=dict(l=20,r=20,t=30,b=20), paper_bgcolor='rgba(0,0,0,0)')
    return fig

def plot_trend(dados, titulo):
    # Tendência sempre verde/azul profissional
    cor = "#00897B"
    fig = px.area(x=range(len(dados)), y=dados, title=titulo)
    fig.update_traces(line_color=cor, fillcolor="rgba(0, 137, 123, 0.1)")
    fig.update_layout(
        title_font_size=14,
        title_font_color="#555",
        height=160, 
        margin=dict(l=0,r=0,t=30,b=0), 
        xaxis_visible=False, 
        yaxis_visible=False, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# --- TELAS POR PERFIL ---

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO INICIAL E CSS ---
st.set_page_config(page_title="DM Health - Analytics", page_icon="✚", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    
    /* CARDS DO TOPO */
    .card-metric-orange {
        background-color: #FFF3E0; border-radius: 12px; padding: 15px; height: 140px;
        border: 1px solid #FFE0B2; margin-bottom: 10px;
    }
    .card-metric-green {
        background-color: #F1F8F9; border-radius: 12px; padding: 15px; height: 140px;
        border: 1px solid #E0F2F1; margin-bottom: 10px;
    }
    .metric-title { font-size: 15px; font-weight: 600; color: #444; margin-bottom: 5px; font-family: 'Segoe UI', sans-serif; }
    .metric-value { font-size: 14px; color: #666; margin-bottom: 25px; }
    .metric-footer { font-size: 11px; color: #999; margin-top: auto; }

    /* AGENDA / CALENDÁRIO */
    .month-selector { font-size: 20px; font-weight: bold; color: #00796B; text-align: center; margin-bottom: 15px; }

    /* Botões dos Dias */
    div[data-testid="stColumn"] > button {
        border-radius: 50%; height: 55px; width: 55px;
        border: none; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* CORES DOS DIAS DA AGENDA */
    div[data-testid="stColumn"] > button[kind="secondary"] {
        background-color: #E0F2F1 !important; color: #00695C !important; border: 1px solid #B2DFDB !important;
    }
    div[data-testid="stColumn"] > button[kind="primary"] {
        background-color: #00796B !important; color: white !important; border: 2px solid #004D40 !important;
    }
    div[data-testid="stColumn"] > button:focus { box-shadow: 0 0 0 3px rgba(0, 150, 136, 0.4); }
    
    .agenda-header { font-size: 16px; font-weight: bold; color: #333; }
    
    /* BOTÃO DE NAVEGAÇÃO (SETAS) */
    .nav-btn { font-size: 20px; font-weight: bold; cursor: pointer; color: #555; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES DE GRÁFICOS ---
def plot_gauge(valor, titulo):
    if valor >= 80: cor = "#00C853"
    elif valor >= 50: cor = "#FFAB00"
    else: cor = "#D50000"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=valor,
        title={'text': titulo, 'font': {'size': 14, 'color': '#555'}},
        number={'suffix': "%", 'font': {'color': '#333'}},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': cor}, 'bgcolor': "#f0f0f0"}
    ))
    fig.update_layout(height=160, margin=dict(l=20,r=20,t=30,b=20), paper_bgcolor='rgba(0,0,0,0)')
    return fig

def plot_trend(dados, titulo):
    fig = px.area(x=range(len(dados)), y=dados, title=titulo)
    fig.update_traces(line_color="#00897B", fillcolor="rgba(0, 137, 123, 0.1)")
    fig.update_layout(height=160, margin=dict(l=0,r=0,t=30,b=0), xaxis_visible=False, yaxis_visible=False, paper_bgcolor='rgba(0,0,0,0)')
    return fig

# --- LÓGICA DE DADOS (SIMULAÇÃO) ---
def get_consultas_mock():
    # Simulando consultas em datas específicas
    return {
        "2025-12-18": [{"hora": "14:00", "medico": "Dra. Ana Silva", "tipo": "Teleconsulta"}],
        "2025-12-22": [{"hora": "09:00", "medico": "Dr. Carlos (Endócrino)", "tipo": "Presencial"}],
        "2025-12-25": [], # Natal
    }

def get_proxima_consulta_real(agenda):
    # Encontra a próxima consulta a partir de HOJE
    hoje = datetime.now().date()
    datas_ordenadas = sorted(agenda.keys())
    
    for data_str in datas_ordenadas:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        if data_obj >= hoje and len(agenda[data_str]) > 0:
            consulta = agenda[data_str][0]
            # Formata para exibir bonitinho
            dia_formatado = data_obj.strftime("%d/%m")
            return f"{dia_formatado} - {consulta['hora']}", f"{consulta['medico']}"
            
    return "Nenhuma futura", "Agende agora"

def get_medicacoes():
    return pd.DataFrame({
        "Medicamento": ["Losartana", "Metformina", "Vitamina D"],
        "Dosagem": ["50mg", "850mg", "2000UI"],
        "Frequência": ["1x Manhã", "2x ao dia", "1x dia"],
        "Próxima dose": ["08:00 (Amanhã)", "20:00 (Hoje)", "08:00 (Amanhã)"]
    })

# --- TELA DO PACIENTE ---
def tela_paciente():
    st.markdown("### Painel do Paciente")
    
    # 1. INICIALIZAÇÃO DE ESTADO (PERSISTÊNCIA)
    if 'meds_open' not in st.session_state: st.session_state.meds_open = False
    if 'data_referencia' not in st.session_state: st.session_state.data_referencia = datetime.now()
    if 'dia_selecionado_dt' not in st.session_state: st.session_state.dia_selecionado_dt = datetime.now().date()

    # Dados
    agenda_db = get_consultas_mock()
    prox_data, prox_detalhe = get_proxima_consulta_real(agenda_db)
    data_atual_str = datetime.now().strftime("%d/%m/%Y %H:%M")

    # --- PARTE 1: CARDS DO TOPO ---
    c1, c2, c3, c4, c5 = st.columns(5)

    # Card 1: Próxima Consulta (Dinâmico e Persistente)
    with c1:
        st.markdown(f"""
        <div class="card-metric-orange">
            <div class="metric-title">Próxima consulta</div>
            <div class="metric-title" style="float:right; color:#ddd">●</div>
            <div class="metric-value" style="font-weight:bold; color:#E65100">{prox_data}</div>
            <div class="metric-footer">{prox_detalhe}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<a href="#agenda-anchor" class="card-wrapper"><div class="card-metric-green"><div class="metric-title">Consultas 🔗</div><div class="metric-value">2 Agendadas</div><div class="metric-footer">Clique para ver</div></div></a>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""<div class="card-metric-green"><div class="metric-title">CID atual</div><div class="metric-value">Z00.0 (Geral)</div><div class="metric-footer">Ref: {data_atual_str}</div></div>""", unsafe_allow_html=True)

    # Card 4: Medicações (Clicável via botão interno)
    with c4:
        # Visual do Card
        st.markdown(f"""<div class="card-metric-green" style="margin-bottom:0px"><div class="metric-title">Medicações</div><div class="metric-value">3 Ativos</div><div class="metric-footer">Clique abaixo 👇</div></div>""", unsafe_allow_html=True)
        # Botão Lógico para abrir
        if st.button("💊 Ver Lista", key="btn_abrir_meds", use_container_width=True):
            st.session_state.meds_open = not st.session_state.meds_open
        
    with c5:
        st.markdown(f"""<div class="card-metric-green"><div class="metric-title">Monitoramento</div><div class="metric-value">Ativo</div><div class="metric-footer">Ref: {data_atual_str}</div></div>""", unsafe_allow_html=True)

    # --- ÁREA EXPANSÍVEL DE MEDICAÇÕES ---
    if st.session_state.meds_open:
        with st.container(border=True):
            st.subheader("💊 Minhas Medicações")
            st.dataframe(get_medicacoes(), use_container_width=True, hide_index=True)
            if st.button("Fechar Lista"):
                st.session_state.meds_open = False
                st.rerun()

    st.markdown("---")

    # --- PARTE 2: GRÁFICOS ---
    # (Mantido simplificado para focar na agenda)
    col_g1, col_g2 = st.columns([1, 3])
    with col_g1: st.plotly_chart(plot_gauge(92, "Adesão"), use_container_width=True)
    with col_g2: st.plotly_chart(plot_trend([120, 118, 122, 121, 135, 128], "Pressão Arterial (7d)"), use_container_width=True)

    st.markdown("<div id='agenda-anchor'></div>", unsafe_allow_html=True)
    st.markdown("---")

    # --- PARTE 3: AGENDA COM NAVEGAÇÃO ENTRE SEMANAS ---
    st.subheader("Agenda")

    # Lógica de Navegação de Datas
    # Calculamos o início da semana (Segunda-feira) baseado na data de referência
    start_of_week = st.session_state.data_referencia - timedelta(days=st.session_state.data_referencia.weekday())
    
    # 1. Cabeçalho de Navegação (Setas e Mês)
    col_prev, col_mes, col_next = st.columns([1, 6, 1])
    
    with col_prev:
        if st.button("◀", key="prev_week"):
            st.session_state.data_referencia -= timedelta(days=7)
            st.rerun()
            
    with col_mes:
        mes_atual_str = start_of_week.strftime("%B %Y").capitalize() # Ex: Dezembro 2025
        st.markdown(f"<div class='month-selector'>{mes_atual_str}</div>", unsafe_allow_html=True)
        
    with col_next:
        if st.button("▶", key="next_week"):
            st.session_state.data_referencia += timedelta(days=7)
            st.rerun()

    # 2. Renderização dos Dias da Semana (Dinâmico)
    cols_dias = st.columns(7)
    dias_semana_nome = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
    
    # Verifica quais dias dessa semana visualizada têm consulta no "Banco de Dados"
    dias_da_semana_atual = []
    for i in range(7):
        dias_da_semana_atual.append(start_of_week + timedelta(days=i))
    
    for i, col in enumerate(cols_dias):
        data_loop = dias_da_semana_atual[i]
        dia_num = data_loop.day
        data_str_loop = data_loop.strftime("%Y-%m-%d")
        
        # Tem consulta nesse dia?
        tem_consulta = data_str_loop in agenda_db and len(agenda_db[data_str_loop]) > 0
        tipo_btn = "primary" if tem_consulta else "secondary"
        
        with col:
            st.caption(dias_semana_nome[i])
            # Botão do Dia
            if st.button(f"{dia_num}", key=f"d_{data_str_loop}", type=tipo_btn):
                st.session_state.dia_selecionado_dt = data_loop
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Lista de Detalhes do Dia Selecionado
    dia_sel_str = st.session_state.dia_selecionado_dt.strftime("%Y-%m-%d")
    dia_sel_fmt = st.session_state.dia_selecionado_dt.strftime("%d/%m/%Y")
    
    with st.container(border=True):
        topo_c1, topo_c2 = st.columns([4, 1])
        with topo_c1:
            st.markdown(f'<p class="agenda-header">Consultas do Dia {dia_sel_fmt}</p>', unsafe_allow_html=True)
        with topo_c2:
            st.button("+ Agendar", key="btn_add_agenda", use_container_width=True)
            
        st.divider()
        
        if dia_sel_str in agenda_db and len(agenda_db[dia_sel_str]) > 0:
            for consulta in agenda_db[dia_sel_str]:
                st.markdown(f"""
                <div style="background-color: #E0F2F1; padding: 15px; border-radius: 8px; border-left: 5px solid #00796B; margin-bottom: 10px;">
                    <strong>{consulta['hora']}</strong> - {consulta['medico']}
                    <br><span style="font-size: 12px; color: #666;">{consulta['tipo']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; color: #999; padding: 30px;">
                Nenhuma consulta para este dia.<br>
                <small>Use as setas acima para navegar entre as semanas.</small>
            </div>
            """, unsafe_allow_html=True)


def render_prontuario_paciente(nome_paciente):
    # Botão de Voltar no Topo
    if st.button("← Voltar para Agenda", type="secondary"):
        st.session_state['paciente_selecionado'] = None
        st.rerun()

    # --- CABEÇALHO DO PACIENTE ---
    with st.container(border=True):
        c_avatar, c_info, c_risk = st.columns([1, 4, 2])
        
        with c_avatar:
            st.markdown(f"""
            <div style='background-color:#E3F2FD; width:80px; height:80px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:30px; color:#1565C0; font-weight:bold;'>
                {nome_paciente[0]}
            </div>
            """, unsafe_allow_html=True)
            
        with c_info:
            st.markdown(f"### {nome_paciente}")
            st.markdown("**34 anos** • Feminino • 📞 (11) 99999-8888")
            st.caption("Convênio: Unimed (Plano Especial) • Matrícula: 88374-2")
            
        with c_risk:
            st.markdown("#### Risco Clínico")
            # Exemplo de Tag de Risco
            risco = "Alto" if "João" in nome_paciente else "Moderado"
            cor_risco = "#D32F2F" if risco == "Alto" else "#FBC02D"
            st.markdown(f"""
            <div style='background-color:{cor_risco}; color:white; padding:5px 15px; border-radius:20px; text-align:center; font-weight:bold;'>
                {risco}
            </div>
            """, unsafe_allow_html=True)
            st.caption("Última estratificação: 10/11/2025")

    st.markdown("---")

    # --- ABAS DE INFORMAÇÃO ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Clínica", "💊 Medicamentos", "📅 Histórico", "📂 Exames"])

    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            with st.container(border=True):
                st.markdown("#### Últimos Sinais Vitais")
                st.metric("Pressão Arterial", "130/85 mmHg", "↑ Leve")
                st.metric("Glicemia", "98 mg/dL", "Normal")
                st.metric("IMC", "24.5", "Adequado")
                st.metric("Peso", "72 kg", "-1.2kg")
        
        with c2:
            with st.container(border=True):
                st.markdown("#### Curva de Evolução (Pressão Arterial)")
                st.plotly_chart(plot_trend([120, 118, 122, 135, 130, 128], ""), use_container_width=True)

    with tab2:
        st.subheader("Prescrições Ativas")
        # Tabela interativa de remédios
        df_meds = pd.DataFrame({
            "Medicamento": ["Losartana", "Metformina", "AAS Infantil"],
            "Dosagem": ["50mg", "850mg", "100mg"],
            "Posologia": ["1x pela manhã", "2x ao dia (Almoço/Jantar)", "1x após almoço"],
            "Status": ["Uso Contínuo", "Uso Contínuo", "Suspender em 7 dias"],
            "Adesão Detectada": ["95%", "80%", "100%"]
        })
        
        # Edição direta na tabela (Simulando ajuste médico)
        st.data_editor(
            df_meds, 
            column_config={
                "Adesão Detectada": st.column_config.ProgressColumn("Adesão", format="%s", min_value=0, max_value=100),
            },
            use_container_width=True, num_rows="dynamic"
        )
        st.button("+ Nova Prescrição", type="primary")

    with tab3:
        st.subheader("Linha do Tempo")
        
        # Simulação de Timeline
        eventos = [
            {"data": "10/12/2025", "tipo": "Consulta", "desc": "Retorno Cardiologia - Queixa de palpitação."},
            {"data": "05/11/2025", "tipo": "Exame", "desc": "Ecocardiograma realizado (Normal)."},
            {"data": "20/08/2025", "tipo": "Pronto-Socorro", "desc": "Entrada por crise hipertensiva."},
        ]
        
        for ev in eventos:
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <strong>{ev['data']} - {ev['tipo']}</strong><br>
                <span style="color:#555">{ev['desc']}</span>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.info("Visualizador de DICOM/PDF integrado")
        col_docs = st.columns(3)
        docs = ["Hemograma Completo.pdf", "Ecocardiograma.pdf", "Receita Digital.pdf"]
        for i, doc in enumerate(docs):
            with col_docs[i]:
                with st.container(border=True):
                    st.markdown(f"**{doc}**")
                    st.caption("15/12/2025")
                    st.button("Visualizar", key=f"doc_{i}")


def tela_profissional():
    # --- LÓGICA DE NAVEGAÇÃO INTERNA (PRONTUÁRIO) ---
    if 'paciente_selecionado' not in st.session_state:
        st.session_state['paciente_selecionado'] = None

    # Se tiver paciente selecionado, renderiza o Prontuário e PARA a execução aqui
    if st.session_state['paciente_selecionado'] is not None:
        render_prontuario_paciente(st.session_state['paciente_selecionado'])
        return

    # --- SE NÃO, MOSTRA O DASHBOARD GERAL ---
    st.markdown("### Painel do Profissional de Saúde")
    
    # 1. KPIs SUPERIORES (Mantidos - Visão Rápida)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="card-metric-orange"><div class="metric-title">Ocupação</div><div class="metric-value">85%</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card-metric-green"><div class="metric-title">Hoje</div><div class="metric-value">12 Pacientes</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="card-metric-orange"><div class="metric-title">Cancelados</div><div class="metric-value">1</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card-metric-green"><div class="metric-title">Tempo Médio</div><div class="metric-value">18 min</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # --- 2. CRIAÇÃO DAS ABAS ---
    # Aqui separamos o operacional (Agenda) do estratégico (Vigilância)
    tab_agenda, tab_vigilancia = st.tabs(["📅 Agenda Diária", "🩺 Vigilância Ativa"])
    
    # --- ABA 1: AGENDA (Seu código original ajustado) ---
    with tab_agenda:
        c_head, c_nav = st.columns([1, 2])
        with c_head: st.subheader("Agenda Diária")

        # Navegação de Dias
        if 'dia_medico_sel' not in st.session_state: st.session_state['dia_medico_sel'] = 15
        nums_dias = [15, 16, 17, 18, 19, 20]
        cols_dias = st.columns(6)
        for i, col in enumerate(cols_dias):
            with col:
                tipo = "primary" if nums_dias[i] in [15, 16, 17] else "secondary"
                if st.button(f"{nums_dias[i]}", key=f"med_d_{i}", type=tipo):
                    st.session_state['dia_medico_sel'] = nums_dias[i]

        # Lista de Pacientes
        dia_sel = st.session_state['dia_medico_sel']
        st.markdown(f"**Visualizando: {dia_sel} de Dezembro**")

        # Dados Mockados
        agenda_dados = {
            15: [("08:00", "João Silva", "Retorno", "confirmado"), 
                 ("09:00", "Maria Souza", "Primeira vez", "confirmado"), 
                 ("10:00", "-- Intervalo --", "", "livre")],
            16: [("08:00", "Carlos Ferreira", "Retorno", "atencao")]
        }
        consultas = agenda_dados.get(dia_sel, [("08:00", "-- Livre --", "", "livre")])

        with st.container(border=True):
            for idx, (hora, paciente, tipo, status) in enumerate(consultas):
                c_hora, c_card, c_btn = st.columns([1, 5, 2])
                
                with c_hora:
                    st.markdown(f"<div style='margin-top:15px; font-weight:bold;'>{hora}</div>", unsafe_allow_html=True)
                
                with c_card:
                    if status == "livre":
                        st.markdown(f"<div style='background:#f9f9f9; padding:10px; border-radius:8px; color:#aaa;'>Disponível</div>", unsafe_allow_html=True)
                    else:
                        cor_borda = "#FB8C00" if status == "atencao" else "#009688"
                        st.markdown(f"""
                        <div style='background:#F1F8F9; padding:10px; border-radius:8px; border-left: 5px solid {cor_borda};'>
                            <b>{paciente}</b> <span style='font-size:12px; color:#666'> - {tipo}</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Botão de Prontuário
                with c_btn:
                    if status != "livre":
                        if st.button("📋 Prontuário", key=f"btn_pront_{dia_sel}_{idx}"):
                            st.session_state['paciente_selecionado'] = paciente
                            st.rerun()

        st.markdown("---")
        
        # Gráficos de Rodapé (Desempenho e Alertas da Agenda)
        c_perf1, c_perf2 = st.columns([2, 1])
        with c_perf1: 
            st.markdown("#### Desempenho")
            st.plotly_chart(plot_gauge(78, "Resolução"), use_container_width=True)
        with c_perf2:
            st.markdown("#### Alertas do Dia")
            st.error("🚨 2 Pacientes com Risco Alto na agenda de hoje")

    # --- ABA 2: VIGILÂNCIA ATIVA (Novo Dashboard Tier 2/3) ---
    with tab_vigilancia:
        # Chama a função que criamos anteriormente
        # Certifique-se de ter copiado a função 'aba_vigilancia_ativa()' no seu código
        aba_vigilancia_ativa()

def tela_gestor_unidade():
    st.markdown("### Gestor de Unidade (UBS Central)")
    
    with st.container(border=True):
        cols = st.columns(5)
        cols[0].metric("Ocupação Unidade", "92%", "Alta")
        cols[1].metric("Absenteísmo", "12%", "Meta <15%")
        cols[2].metric("Espera Média", "18 min", "Recepção")
        cols[3].metric("NPS Pacientes", "75", "Qualidade")
        cols[4].metric("NPS Equipe", "82", "Clima")

    c1, c2 = st.columns([1, 1])
    with c1:
        with st.container(border=True):
            st.markdown("#### Agenda Consolidada")
            fig = px.pie(names=['Realizadas', 'Canceladas', 'Remarcadas', 'Ociosas'], values=[70, 10, 5, 15], hole=0.5)
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
            
    with c2:
        with st.container(border=True):
            st.markdown("#### Eficácia Monitoramento")
            st.plotly_chart(plot_gauge(78, "Adesão Geral"), use_container_width=True)
            st.metric("Alertas Tratados", "98%", "Em < 24h")

def tela_gestor_operacional():
    st.markdown("### Gestor Operacional (Multicêntrico)")
    
    with st.container(border=True):
        st.markdown("#### Visão Saúde Populacional")
        c1, c2, c3 = st.columns(3)
        c1.metric("Hospitalizações", "1.2%", "-0.3%")
        c2.metric("Reinternações", "5%", "Estável")
        c3.metric("Prevalência Crônicos", "32%", "Hipertensão/Diabetes")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### Comparativo de Produtividade")
            unidades = ['Centro', 'Sul', 'Norte']
            produtividade = [1200, 950, 1050]
            fig = px.bar(x=unidades, y=produtividade, title="Consultas/Mês")
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        with st.container(border=True):
            st.markdown("#### Eficiência Operacional Global")
            st.metric("Tempo Médio Chat", "4.5 min", "Meta < 5")
            st.metric("Teleconsultas Totais", "1.250", "+15%")

def tela_gestor_ti():
    st.markdown("### Gestor de TI e Infraestrutura")
    
    k1, k2, k3 = st.columns(3)
    k1.metric("System Uptime", "99.98%", "Operacional")
    k2.metric("Incidentes Segurança", "0", "Últimos 30 dias")
    k3.metric("SLA Suporte", "96%", "Resolução < 4h")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### Vulnerabilidades")
            fig = go.Figure(data=[
                go.Bar(name='Identificadas', x=['Jan', 'Fev', 'Mar'], y=[10, 5, 2]),
                go.Bar(name='Corrigidas', x=['Jan', 'Fev', 'Mar'], y=[10, 5, 2], marker_color='green')
            ])
            fig.update_layout(barmode='group', height=250)
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        with st.container(border=True):
            st.markdown("#### Disponibilidade da Plataforma")
            st.plotly_chart(plot_trend([99.9, 99.8, 99.95, 100, 99.99], "Latência (ms)"), use_container_width=True)

def tela_gestor_pleno():
    st.markdown("### Gestor Pleno (Executivo)")
    
    with st.container(border=True):
        cols = st.columns(4)
        cols[0].metric("ROI do Projeto", "18.5%", "Positivo")
        cols[1].metric("Custo por Consulta", "R$ 42,00", "-5%")
        cols[2].metric("Receita Unidade", "R$ 1.2M", "Média")
        cols[3].metric("NPS Global", "78", "Excelente")

    c1, c2 = st.columns([2, 1])
    with c1:
        with st.container(border=True):
            st.markdown("#### Impacto Monitoramento Remoto")
            fig = px.bar(x=["Sem Monit.", "Com Monit."], y=[1500, 1200], title="Custo Médio Paciente Crônico (R$)")
            fig.update_traces(marker_color=['#D32F2F', '#388E3C'])
            st.plotly_chart(fig, use_container_width=True)
            
    with c2:
        with st.container(border=True):
            st.markdown("#### Satisfação Consolidada")
            st.metric("Pacientes", "4.8/5")
            st.metric("Profissionais", "4.5/5")
            st.metric("Suporte TI", "4.9/5")


def tela_assistente():
    st.markdown("### Painel do Assistente")
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Fila de Espera", "12 min", "Média Atual")
    k2.metric("Ociosidade Agenda", "10%", "2 horários")
    k3.metric("Confirmados", "92%", "Agenda de Amanhã")
    k4.metric("Msgs Pendentes", "15", "Chat")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### Eficiência Operacional")
            fig = go.Figure(go.Bar(
                x=[85, 90, 60], y=['Respostas Notif.', 'Confirmação', 'Triagem'],
                orientation='h', marker_color='#0288D1'
            ))
            fig.update_layout(title="Taxa de Execução (%)", height=200, margin=dict(l=0,r=0,t=30,b=0))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        with st.container(border=True):
            st.markdown("#### Feedback e Volume")
            st.metric("Interações Totais", "145", "Hoje")
            st.metric("Telemedicina", "30%", "Das consultas")

def tela_paciente_gestante():
    st.markdown("### 🤰 Painel da Gestante (Pré-Natal)")
    
    # INICIALIZAÇÃO DE ESTADO
    if 'meds_gest_open' not in st.session_state: st.session_state.meds_gest_open = False
    if 'data_ref_gest' not in st.session_state: st.session_state.data_ref_gest = datetime.now()
    if 'dia_sel_gest' not in st.session_state: st.session_state.dia_sel_gest = datetime.now().date()

    # DADOS MOCKADOS ESPECÍFICOS DE GESTANTE
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    
    # --- PARTE 1: CARDS DO TOPO (MATERNO-FETAL) ---
    c1, c2, c3, c4, c5 = st.columns(5)

    # Card 1: Idade Gestacional (O mais importante)
    with c1:
        st.markdown(f"""
        <div class="card-metric-orange">
            <div class="metric-title">Idade Gestacional</div>
            <div class="metric-value" style="color:#E65100">28 Semanas</div>
            <div class="metric-footer">+ 3 dias | 3º Trimestre</div>
        </div>""", unsafe_allow_html=True)

    # Card 2: Próximo Pré-Natal
    with c2:
        st.markdown(f"""
        <div class="card-metric-green">
            <div class="metric-title">Próximo Pré-Natal</div>
            <div class="metric-value">18/12 - 14h</div>
            <div class="metric-footer">Dr. Carlos (Obstetra)</div>
        </div>""", unsafe_allow_html=True)

    # Card 3: DPP (Data Provável do Parto)
    with c3:
        st.markdown(f"""
        <div class="card-metric-green">
            <div class="metric-title">Data do Parto (DPP)</div>
            <div class="metric-value">15/03/2026</div>
            <div class="metric-footer">Restam 12 semanas</div>
        </div>""", unsafe_allow_html=True)

    # Card 4: Movimentação Fetal (Tier 2 - Monitoramento Clínico)
    with c4:
        st.markdown(f"""
        <div class="card-metric-green">
            <div class="metric-title">Movimentos Hoje</div>
            <div class="metric-value">12 Chutes 👣</div>
            <div class="metric-footer">Meta diária atingida</div>
        </div>""", unsafe_allow_html=True)
        
    # Card 5: Suplementação (Tier 3 - Hábitos)
    with c5:
        st.markdown(f"""
        <div class="card-metric-green">
            <div class="metric-title">Suplementação</div>
            <div class="metric-value">Pendente 💊</div>
            <div class="metric-footer">Ácido Fólico (Manhã)</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # --- PARTE 2: JORNADA TIER 2 & 3 (Gráficos Específicos) ---
    # Aqui chamamos a função que criamos anteriormente para Peso e Bem-Estar
    aba_jornada_gestante() 

    st.markdown("<br>", unsafe_allow_html=True)

    # --- PARTE 3: AGENDA DE PRÉ-NATAL ---
    st.subheader("Agenda Pré-Natal")
    
    # Navegação de Semanas
    start_of_week = st.session_state.data_ref_gest - timedelta(days=st.session_state.data_ref_gest.weekday())
    
    col_prev, col_mes, col_next = st.columns([1, 6, 1])
    with col_prev:
        if st.button("◀", key="prev_wk_g"):
            st.session_state.data_ref_gest -= timedelta(days=7)
            st.rerun()
    with col_mes:
        st.markdown(f"<div class='month-selector'>{start_of_week.strftime('%B %Y').capitalize()}</div>", unsafe_allow_html=True)
    with col_next:
        if st.button("▶", key="next_wk_g"):
            st.session_state.data_ref_gest += timedelta(days=7)
            st.rerun()

    # Dias da Semana
    cols_dias = st.columns(7)
    dias_semana_nome = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
    
    # Mock de Consultas de Gestante (Ex: dia 18 tem consulta)
    dias_consulta_gestante = [18, 25] 
    
    for i, col in enumerate(cols_dias):
        data_loop = start_of_week + timedelta(days=i)
        dia_num = data_loop.day
        
        # Lógica visual: Verde Escuro se tiver consulta
        tipo_btn = "primary" if dia_num in dias_consulta_gestante else "secondary"
        
        with col:
            st.caption(dias_semana_nome[i])
            if st.button(f"{dia_num}", key=f"g_d_{dia_num}", type=tipo_btn):
                st.session_state.dia_sel_gest = data_loop
                st.rerun()

    # Detalhe do Dia
    dia_fmt = st.session_state.dia_sel_gest.strftime("%d/%m/%Y")
    dia_int = st.session_state.dia_sel_gest.day
    
    with st.container(border=True):
        st.markdown(f'<p class="agenda-header">Compromissos do Dia {dia_fmt}</p>', unsafe_allow_html=True)
        st.divider()
        
        if dia_int == 18:
            st.markdown("""
            <div style="background-color: #E3F2FD; padding: 15px; border-radius: 8px; border-left: 5px solid #2196F3;">
                <strong>14:00</strong> - Consulta Pré-Natal Mensal
                <br><span style="font-size: 12px; color: #666;">Dr. Carlos (Obstetra) - Trazer últimos exames</span>
            </div>
            """, unsafe_allow_html=True)
        elif dia_int == 25:
             st.markdown("""
            <div style="background-color: #F3E5F5; padding: 15px; border-radius: 8px; border-left: 5px solid #9C27B0;">
                <strong>09:00</strong> - Ultrassom Morfológico
                <br><span style="font-size: 12px; color: #666;">Laboratório Imagem - Chegar 15min antes</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; color:#999; padding:20px;'>Dia livre. Aproveite para descansar!</div>", unsafe_allow_html=True)

# --- PÁGINA: BI-DIFY ---
def tela_bi_dify():
    st.markdown("### 📊 Business Intelligence - Integração Dify")
    st.caption("Governança: Núcleo de IA DM Health | Responsável: Duda (Data & BI)")

    # Simulação de seleção de contexto (Baseado nos Endpoints 1 e 2)
    with st.sidebar:
        st.divider()
        st.markdown("#### Filtros de Instância")
        # Endpoint 1: GET /api/instancia/instancias
        instancia = st.selectbox("Instância", ["DM Health Global", "Clínica Parceira A"])
        # Endpoint 2: GET /api/instancia/unidades-instancia
        unidade = st.selectbox("Unidade", ["UBS Central", "Unidade Sul"])

    # --- CAMADA 1: ESTRUTURA E PESSOAL (Endpoints 4, 5, 6, 7) ---
    st.markdown("#### 👥 Composição e Capacidade")
    c1, c2, c3, c4 = st.columns(4)
    
    # KPIs derivados dos endpoints de listagem de profissionais, pacientes e secretárias
    with c1: st.metric("Pacientes Ativos", "1,240", "+12%") # Endpoint 5
    with c2: st.metric("Profissionais", "45", "Ativos")    # Endpoint 4
    with c3: st.metric("Secretarias", "12", "Online")     # Endpoint 6
    with c4: st.metric("Personas", "8", "Definidas")      # Endpoint 7

    st.markdown("---")

    # --- CAMADA 2: SAÚDE E ENGAJAMENTO (Endpoints 8, 9, 10) ---
    col_quest, col_score = st.columns([1, 1])

    with col_quest:
        with st.container(border=True):
            st.markdown("#### 📝 Engajamento em Questionários")
            # Endpoint 8 e 9: Base para métrica de adesão
            adesao_data = {"Enviados": 500, "Respondidos": 380}
            fig_adesao = px.bar(
                x=list(adesao_data.keys()), 
                y=list(adesao_data.values()),
                color=list(adesao_data.keys()),
                color_discrete_map={"Enviados": "#B2DFDB", "Respondidos": "#00796B"}
            )
            fig_adesao.update_layout(height=250, showlegend=False, xaxis_title="")
            st.plotly_chart(fig_adesao, use_container_width=True)
            st.caption("Base: Questionários de Pacientes e Pesquisa (Research)")

    with col_score:
        with st.container(border=True):
            st.markdown("#### 📈 Evolução de Scores (EcoMind)")
            # Endpoint 10: GET /api/Quizz/by-paciente (Agregado)
            # Representa a tradução do método científico em lógica de IA [cite: 81]
            scores_agregados = [7.2, 7.5, 7.1, 7.8, 8.2, 8.0]
            st.plotly_chart(plot_trend(scores_agregados, "Média de Bem-estar Global"), use_container_width=True)
            st.markdown("<small>⚠️ Exibição de dados agregados para proteção de subjetividades[cite: 171, 172].</small>", unsafe_allow_html=True)

    # --- REGRA DE OURO (Visual) ---
    st.warning("Se um indicador não puder ser explicado, defendido e auditado, ele não pode ser implementado[cite: 52, 129].")
    st.markdown("### 📊 BI-DIFY: Inteligência e Governança")
    
    # --- CABEÇALHO DE GOVERNANÇA ---
    # Todo BI deve ser explicável, defendido e auditado [cite: 52, 129]
    with st.expander("🛡️ Parâmetros de Governança (Responsible AI by Design)"):
        st.write(f"**Validação Metodológica:** Rodrigo [cite: 44]")
        st.write(f"**Qualidade e Rastreabilidade:** Nathy [cite: 28]")
        st.write(f"**Operacionalização Técnica:** Duda [cite: 40]")

    # --- CAMADA 1: INFRAESTRUTURA E PESSOAS (Endpoints 1, 2, 4, 5, 6, 7) ---
    st.markdown("#### 🏥 Gestão de Instâncias e Personas")
    
    # KPIs derivados dos Endpoints de listagem
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        st.metric("Pacientes (EP 5)", "1.240", "Base Direct") # Endpoint 5 [cite: 65]
    with c2: 
        st.metric("Profissionais (EP 4)", "45", "Ativos")     # Endpoint 4 [cite: 79]
    with c3: 
        st.metric("Personas (EP 7)", "8", "Tipologias")      # Endpoint 7 [cite: 83]
    with c4: 
        st.metric("Secretarias (EP 6)", "12", "Suporte")      # Endpoint 6 [cite: 73]

    st.markdown("---")

    # --- CAMADA 2: MÉTODO E ENGAJAMENTO EMA (Endpoints 8, 9) ---
    # A Nathy garante a correta aplicação da metodologia [cite: 25, 27]
    col_metodo, col_adesao = st.columns([1, 1])
    
    with col_metodo:
        with st.container(border=True):
            st.markdown("#### 🔬 Configuração Metodológica")
            # Endpoint 8: Questionários disponíveis
            st.write("**Questionários Ativos (EP 8):** 5")
            st.write("**Foco:** Saúde Mental e Bem-Estar (EcoMind) [cite: 65]")
            st.caption("Garantia de não indução de decisão automática[cite: 39, 93].")

    with col_adesao:
        with st.container(border=True):
            st.markdown("#### 📈 Adesão ao Monitoramento")
            # Dados agregados para evitar vigilância de subjetividades [cite: 171, 172]
            fig_adesao = px.line(y=[65, 72, 68, 85], x=["Sem 1", "Sem 2", "Sem 3", "Sem 4"], 
                                 title="Taxa de Resposta EMA (%)")
            fig_adesao.update_traces(line_color="#00796B")
            st.plotly_chart(fig_adesao, use_container_width=True)

    # --- CAMADA 3: INSIGHTS CIENTÍFICOS (Endpoint 10) ---
    # O Rodrigo define o método científico e limites [cite: 16, 18]
    st.markdown("#### 🧠 Score de Bem-Estar Longitudinal (Quizz EP 10)")
    with st.container(border=True):
        # O BI deve preservar a comparabilidade longitudinal [cite: 83]
        scores_mock = [7.2, 7.5, 7.1, 7.8, 8.2, 8.0]
        st.plotly_chart(plot_trend(scores_mock, "Evolução de Score Agregado - Instância"), use_container_width=True)
        st.info("⚠️ Decisões clínicas e assistenciais permanecem 100% humanas[cite: 156, 159].")

    # --- FOOTER DE CONFORMIDADE ---
    st.divider()
    if st.button("📄 Gerar Log de Auditoria"):
        st.success("Log de rastreabilidade gerado para Due Diligence[cite: 117].")
# Adicione "BI-DIFY" à lista de navegação no sidebar e ao roteamento
def get_dados_peso_gestacional():
    # Simula curva de peso para Tier 2 (Monitoramento Clínico) e Tier 3 (Nutrição)
    semanas = list(range(0, 42))
    # Peso inicial 60kg
    peso_ideal_min = [60 + (0.3 * s) if s > 12 else 60 for s in semanas]
    peso_ideal_max = [60 + (0.5 * s) if s > 12 else 60 + 2 for s in semanas]
    peso_real = [60 + (0.4 * s) + np.random.uniform(-0.5, 0.5) if s > 12 else 60 + np.random.uniform(-0.2, 0.2) for s in semanas[:28]] # Até semana 28
    
    return pd.DataFrame({
        "Semana": semanas,
        "Mínimo Ideal": peso_ideal_min,
        "Máximo Ideal": peso_ideal_max,
        "Peso Real": peso_real + [None] * (42 - 28)
    })

def get_dados_bem_estar():
    # Simula Diário de Bem-Estar (EMA - Tier 3)
    datas = [datetime.now().date() - timedelta(days=i) for i in range(30)]
    humores = np.random.choice(["Bem", "Cansaço", "Enjoo", "Dor", "Ansiedade"], 30, p=[0.5, 0.2, 0.15, 0.1, 0.05])
    return pd.DataFrame({"Data": datas, "Sintoma": humores})

def get_dados_radar_estilo_vida():
    # Métricas TIER 3 (Hábitos)
    return pd.DataFrame({
        "Categoria": ["Suplementação", "Ativ. Física", "Qualidade Nutricional", "Consultas", "Exames"],
        "Valor": [85, 40, 70, 100, 95] # Exemplo: Baixa atividade física
    })

def get_dados_pa_sintomas():
    # Correlação PA (Tier 2) x Sintomas (Tier 3)
    datas = pd.date_range(end=datetime.now(), periods=14)
    sistolica = [110, 112, 115, 118, 120, 135, 142, 138, 130, 125, 122, 120, 118, 115]
    diastolica = [70, 72, 75, 78, 80, 85, 92, 88, 85, 80, 78, 75, 72, 70]
    
    df = pd.DataFrame({"Data": datas, "Sistólica": sistolica, "Diastólica": diastolica})
    
    # Adiciona sintomas nos dias de pico
    df['Sintoma'] = None
    df.loc[6, 'Sintoma'] = "Cefaleia Intensa" # Dia do pico 142/92
    df.loc[5, 'Sintoma'] = "Visão Turva"
    return df

# --- 1. ABA DA GESTANTE: "Jornada & Bem-Estar" ---
def aba_jornada_gestante():
    st.subheader("🤰 Minha Jornada e Bem-Estar")
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        with st.container(border=True):
            st.markdown("#### Curva de Ganho de Peso")
            df_peso = get_dados_peso_gestacional()
            
            fig = go.Figure()
            # Faixa Ideal (Área Sombreada)
            fig.add_trace(go.Scatter(
                x=df_peso['Semana'], y=df_peso['Máximo Ideal'], mode='lines', line=dict(width=0),
                showlegend=False, hoverinfo='skip'
            ))
            fig.add_trace(go.Scatter(
                x=df_peso['Semana'], y=df_peso['Mínimo Ideal'], mode='lines', line=dict(width=0),
                fill='tonexty', fillcolor='rgba(0, 200, 83, 0.1)', name='Faixa Ideal'
            ))
            # Linha Real
            fig.add_trace(go.Scatter(
                x=df_peso['Semana'], y=df_peso['Peso Real'], mode='lines+markers',
                line=dict(color='#2979FF', width=3), name='Meu Peso'
            ))
            
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20),
                              xaxis_title="Semana Gestacional", yaxis_title="Peso (kg)")
            st.plotly_chart(fig, use_container_width=True)
            st.info("**Dica Nutricional:** Seu ganho está dentro do esperado! Mantenha o consumo de proteínas.")

    with c2:
        with st.container(border=True):
            st.markdown("#### Contador de Movimentos")
            st.markdown("Sentiu o bebê mexer hoje?")
            
            col_k1, col_k2 = st.columns(2)
            with col_k1:
                if st.button("👣 Chutar", type="primary", use_container_width=True):
                    st.toast("Movimento registrado! 👶")
            
            with col_k2:
                st.metric("Hoje", "12", "+3 vs ontem")
            
            st.progress(0.8, text="Meta diária (10 movimentos)")
            
    st.markdown("---")
    
    st.markdown("#### Diário de Sintomas")
    df_sintomas = get_dados_bem_estar()
    
    # Mapa de Calor Simplificado (Scatter Plot estilo Calendar)
    fig_cal = px.scatter(df_sintomas, x="Data", y=[1]*len(df_sintomas), 
                         color="Sintoma", size=[20]*len(df_sintomas),
                         color_discrete_map={"Bem":"#66BB6A", "Cansaço":"#FFEE58", "Enjoo":"#FFA726", "Dor":"#EF5350", "Ansiedade":"#AB47BC"})
    
    fig_cal.update_layout(height=150, yaxis_visible=False, xaxis_title="", showlegend=True, margin=dict(t=10,b=10))
    st.plotly_chart(fig_cal, use_container_width=True)

# --- 2. ABA DO PROFISSIONAL: "Vigilância Ativa" ---
# --- GERADOR DE DADOS DINÂMICO ---
def get_dados_radar_estilo_vida(paciente_nome):
    # Simulando perfis diferentes para testar o filtro
    perfis = {
        "Ana Silva": [85, 30, 70, 100, 95],   # Sedentária
        "Maria Souza": [95, 90, 95, 100, 100], # Atleta/Exemplar
        "Joana Lima": [40, 20, 30, 60, 50],    # Risco Alto (Baixa adesão)
        "Carla Dias": [70, 60, 80, 90, 80]     # Média
    }
    
    # Pega os dados ou usa um padrão se não encontrar
    valores = perfis.get(paciente_nome, [80, 50, 70, 90, 85])
    
    return pd.DataFrame({
        "Categoria": ["Suplementação", "Ativ. Física", "Qualidade Nutricional", "Consultas", "Exames"],
        "Valor": valores
    })

def get_dados_pa_sintomas_dinamico(paciente_nome):
    # Pequena variação nos dados para parecer real quando troca o paciente
    np.random.seed(len(paciente_nome)) # Seed baseada no nome para ser consistente
    base_sist = np.random.randint(110, 140)
    base_diast = np.random.randint(70, 90)
    
    datas = pd.date_range(end=datetime.now(), periods=14)
    sistolica = [base_sist + np.random.randint(-5, 10) for _ in range(14)]
    diastolica = [base_diast + np.random.randint(-3, 5) for _ in range(14)]
    
    df = pd.DataFrame({"Data": datas, "Sistólica": sistolica, "Diastólica": diastolica})
    df['Sintoma'] = None
    
    # Adiciona sintoma aleatório em um dia
    if "Joana" in paciente_nome: # Paciente de risco
        df.loc[12, 'Sintoma'] = "Cefaleia"
        df.loc[13, 'Sintoma'] = "Visão Turva"
        
    return df

# --- ABA VIGILÂNCIA ATIVA COM FILTRO ---
def aba_vigilancia_ativa():
    st.subheader("🩺 Vigilância Ativa & Estilo de Vida")
    
    # 1. ÁREA DE FILTRO (NOVO)
    c_filtro, c_resumo = st.columns([1, 3])
    with c_filtro:
        lista_pacientes = ["Ana Silva", "Maria Souza", "Joana Lima", "Carla Dias"]
        paciente_sel = st.selectbox("Selecione a Paciente:", lista_pacientes)
        
    with c_resumo:
        # Mostra um resumo rápido do perfil selecionado
        if paciente_sel == "Joana Lima":
            st.warning(f"⚠️ **Perfil de Risco:** {paciente_sel} apresenta baixa adesão e sintomas recentes.")
        elif paciente_sel == "Maria Souza":
            st.success(f"✅ **Perfil Estável:** {paciente_sel} está seguindo todas as recomendações.")
        else:
            st.info(f"ℹ️ Visualizando dados de monitoramento de **{paciente_sel}**.")

    st.markdown("---")
    
    c_radar, c_pa = st.columns([1, 2])
    
    # 2. RADAR ATUALIZADO PELO FILTRO
    with c_radar:
        with st.container(border=True):
            st.markdown(f"#### 🎯 Radar de Hábitos: {paciente_sel.split()[0]}")
            
            # Busca dados específicos da paciente selecionada
            df_radar = get_dados_radar_estilo_vida(paciente_sel)
            
            fig = go.Figure(go.Scatterpolar(
                r=df_radar['Valor'], theta=df_radar['Categoria'], fill='toself',
                line_color='#0091EA', name=paciente_sel
            ))
            
            # Adiciona linha de meta (Ideal) para comparação
            fig.add_trace(go.Scatterpolar(
                r=[80, 80, 80, 100, 100], theta=df_radar['Categoria'], 
                line_color='rgba(0,0,0,0.3)', line_dash='dot', name='Meta Clínica', hoverinfo='skip'
            ))

            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), 
                              height=350, margin=dict(t=30, b=30, l=40, r=40), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Feedback Automático Baseado no Dado
            val_fisica = df_radar[df_radar['Categoria']=='Ativ. Física']['Valor'].values[0]
            val_suple = df_radar[df_radar['Categoria']=='Suplementação']['Valor'].values[0]
            
            if val_fisica < 50:
                st.caption("🔴 **Sedentarismo:** Prescrever caminhada leve 3x/semana.")
            if val_suple < 60:
                st.caption("🟠 **Suplementação:** Verificar adesão ao Ferro/Ácido Fólico.")

    # 3. GRÁFICO PA x SINTOMAS (DINÂMICO)
    with c_pa:
        with st.container(border=True):
            st.markdown(f"#### 🩸 Monitoramento PA (14 dias)")
            
            df_pa = get_dados_pa_sintomas_dinamico(paciente_sel)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_pa['Data'], y=df_pa['Sistólica'], name='Sistólica', line=dict(color='#EF5350')))
            fig.add_trace(go.Scatter(x=df_pa['Data'], y=df_pa['Diastólica'], name='Diastólica', line=dict(color='#42A5F5')))
            
            # Sintomas
            sintomas = df_pa.dropna(subset=['Sintoma'])
            if not sintomas.empty:
                fig.add_trace(go.Scatter(
                    x=sintomas['Data'], y=sintomas['Sistólica'], mode='markers', 
                    marker=dict(size=12, color='black', symbol='x'),
                    name='Sintoma', text=sintomas['Sintoma']
                ))

            fig.add_hline(y=140, line_dash="dash", line_color="red", annotation_text="Limite Risco")
            fig.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    
    # Score Geral (Rodapé)
    c_score1, c_score2 = st.columns([3, 1])
    with c_score1:
        st.markdown("#### Score de Engajamento do Paciente")
        # Score calculado (média dos valores do radar)
        score_medio = int(df_radar['Valor'].mean())
        st.progress(score_medio/100, text=f"{score_medio}/100 - Baseado em adesão e hábitos")
    with c_score2:
        st.metric("Risco Calculado", "Baixo" if score_medio > 70 else "Alto", delta_color="inverse")
# --- 3. ABA DO GESTOR: "Qualidade & Desfechos" ---
def aba_qualidade_desfechos():
    st.subheader("Qualidade, Desfechos e Sustentabilidade")
    
    # Big Number de Alerta (Tier 3 - Sinais de Alerta)
    st.error("**Early Warning:** 12 Pacientes relataram sangramento ou cefaleia nas últimas 24h.")
    
    c_sankey, c_scatter = st.columns(2)
    
    with c_sankey:
        with st.container(border=True):
            st.markdown("#### Funil de Desfechos Obstétricos")
            # Sankey Diagram Simples
            fig = go.Figure(data=[go.Sankey(
                node = dict(
                  pad = 15, thickness = 20, line = dict(color = "black", width = 0.5),
                  label = ["Total Gestantes", "Baixo Risco", "Alto Risco", "Parto Vaginal", "Cesárea"],
                  color = ["blue", "green", "red", "green", "orange"]
                ),
                link = dict(
                  source = [0, 0, 1, 1, 2, 2], # Indices origem
                  target = [1, 2, 3, 4, 3, 4], # Indices destino
                  value  = [800, 200, 600, 200, 50, 150] # Quantidades
              ))])
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

    with c_scatter:
        with st.container(border=True):
            st.markdown("#### Matriz Experiência vs. Tecnologia")
            # Scatter Plot
            df_ux = pd.DataFrame({
                "Unidade": ["UBS Centro", "UBS Norte", "UBS Sul", "UBS Leste"],
                "Facilidade Uso App (0-10)": [8.5, 4.2, 7.0, 6.5],
                "Satisfação Pré-Natal (0-10)": [9.0, 5.0, 8.8, 6.0],
                "Volume": [40, 30, 50, 25]
            })
            fig = px.scatter(df_ux, x="Facilidade Uso App (0-10)", y="Satisfação Pré-Natal (0-10)",
                             size="Volume", color="Unidade", text="Unidade")
            fig.add_hline(y=7, line_dash="dot", annotation_text="Meta Satisfação")
            fig.add_vline(x=7, line_dash="dot", annotation_text="Meta UX")
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
            
    # Sustentabilidade
    with st.container(border=True):
        st.markdown("#### Sustentabilidade e Eficiência")
        c1, c2, c3 = st.columns(3)
        c1.metric("Custo Médio / Paciente", "R$ 450", "-10% vs Não-monit.")
        c2.metric("Intercorrências Evitadas", "15", "Economia R$ 45k")
        c3.metric("Tempo Médio Suporte", "12h", "Manutenção App")

# --- NAVEGAÇÃO LATERAL ---
with st.sidebar:
    st.image("imagens/DM.jpg", width=60)
    st.markdown("## DM Health")
    st.markdown("Selecione o Perfil:")
    
    opcao = st.radio(
        "Navegação",
        [
            "Paciente",
            "Paciente Gestante",
            "Profissional de Saúde",
            "Assistente",
            "Gestor de Unidade",
            "Gestor Operacional",
            "Gestor de TI",
            "Gestor Pleno"
        ],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("v1.1 - Corporate View")

# --- ROTEAMENTO ---
if opcao == "Paciente":
    tela_paciente()
elif opcao == "Paciente Gestante":
    tela_paciente_gestante()
elif opcao == "Profissional de Saúde":
    tela_profissional()
elif opcao == "Assistente":
    tela_assistente()
elif opcao == "Gestor de Unidade":
    tela_gestor_unidade()
elif opcao == "Gestor Operacional":
    tela_gestor_operacional()
elif opcao == "Gestor de TI":
    tela_gestor_ti()
elif opcao == "Gestor Pleno":
    tela_gestor_pleno()