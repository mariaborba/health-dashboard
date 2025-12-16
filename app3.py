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
                    st.markdown(f"📄 **{doc}**")
                    st.caption("15/12/2025")
                    st.button("Visualizar", key=f"doc_{i}")




def tela_profissional():
    # --- LÓGICA DE NAVEGAÇÃO INTERNA ---
    if 'paciente_selecionado' not in st.session_state:
        st.session_state['paciente_selecionado'] = None

    # Se tiver paciente selecionado, renderiza o Prontuário e PARA aqui (return)
    if st.session_state['paciente_selecionado'] is not None:
        render_prontuario_paciente(st.session_state['paciente_selecionado'])
        return

    # --- SE NÃO, MOSTRA O DASHBOARD GERAL ---
    st.markdown("### Painel do Profissional de Saúde")
    
    # KPIs SUPERIORES (Mantidos)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="card-metric-orange"><div class="metric-title">Ocupação</div><div class="metric-value">85%</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card-metric-green"><div class="metric-title">Hoje</div><div class="metric-value">12 Pacientes</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="card-metric-orange"><div class="metric-title">Cancelados</div><div class="metric-value">1</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card-metric-green"><div class="metric-title">Tempo Médio de Atendimento</div><div class="metric-value">18 min</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # --- AGENDA INTERATIVA ---
    c_head, c_nav = st.columns([1, 2])
    with c_head: st.subheader("Agenda Diária")

    # Navegação de Dias (Mantida)
    if 'dia_medico_sel' not in st.session_state: st.session_state['dia_medico_sel'] = 15
    nums_dias = [15, 16, 17, 18, 19, 20]
    cols_dias = st.columns(6)
    for i, col in enumerate(cols_dias):
        with col:
            tipo = "primary" if nums_dias[i] in [15, 16, 17] else "secondary"
            if st.button(f"{nums_dias[i]}", key=f"med_d_{i}", type=tipo):
                st.session_state['dia_medico_sel'] = nums_dias[i]

    # LISTA DE PACIENTES (AGORA CLICÁVEL)
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
            
            # BOTÃO DE AÇÃO: VER PRONTUÁRIO
            with c_btn:
                if status != "livre":
                    # Ao clicar aqui, mudamos o estado 'paciente_selecionado' e damos rerun
                    if st.button("📋 Prontuário", key=f"btn_pront_{dia_sel}_{idx}"):
                        st.session_state['paciente_selecionado'] = paciente
                        st.rerun()

    st.markdown("---")
    # (Restante dos gráficos mantidos...)
    c1, c2 = st.columns([2, 1])
    with c1: 
        st.markdown("#### Desempenho")
        st.plotly_chart(plot_gauge(78, "Resolução"), use_container_width=True)
    with c2:
        st.markdown("#### Alertas")
        st.error("🚨 2 Risco Alto")
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

# --- NAVEGAÇÃO LATERAL ---
with st.sidebar:
    st.image("imagens/DM.jpg", width=60)
    st.markdown("## DM Health")
    st.markdown("Selecione o Perfil:")
    
    opcao = st.radio(
        "Navegação",
        [
            "Paciente",
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